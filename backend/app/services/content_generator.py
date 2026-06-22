"""教材内容生成服务"""
import json
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm
from app.config import settings

LESSON_SYSTEM_PROMPT = """你是一个专业的教材编写者。你的任务是根据知识点的标题、描述和前置知识，生成一份清晰易懂的教材内容。

## 输出格式要求

你必须严格输出 JSON，不要输出任何其他内容。JSON 结构如下：

```json
{
  "title": "教材标题",
  "sections": [
    {
      "heading": "章节标题",
      "content": "章节内容（支持简单的 Markdown 格式）",
      "key_points": ["要点1", "要点2"]
    }
  ],
  "summary": "总结",
  "key_terms": [
    {"term": "术语", "definition": "定义"}
  ]
}
```

## 规则

1. 内容要准确、专业、易懂
2. 每个章节包含标题、内容和要点
3. 使用简单清晰的中文表达
4. 包含 3-5 个章节
5. 总结部分概括核心内容
6. 列出 5-10 个关键术语及其定义
7. 内容字数控制在 1500-3000 字
8. 只输出 JSON，不要输出任何解释文字

"""

EXERCISE_SYSTEM_PROMPT = """你是一个专业的出题老师。你的任务是根据知识点生成练习题。

## 输出格式要求

你必须严格输出 JSON，不要输出任何其他内容。JSON 结构如下：

```json
{
  "title": "练习题标题",
  "exercises": [
    {
      "type": "choice",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "A",
      "explanation": "解析"
    },
    {
      "type": "short_answer",
      "question": "简答题题目",
      "answer": "参考答案",
      "key_points": ["要点1", "要点2"]
    }
  ]
}
```

## 规则

1. 生成 5-8 道题目
2. 题型包括：选择题（choice）、简答题（short_answer）
3. 选择题必须有 4 个选项和正确答案
4. 题目难度适中，覆盖核心知识点
5. 每题都有解析或要点
6. 只输出 JSON，不要输出任何解释文字

"""


def build_content_prompt(node_title: str, node_description: str, prerequisites: list = None) -> str:
    """构建教材生成提示词"""
    prompt = f"""请为以下知识点生成教材内容：

- 知识点标题：{node_title}
- 知识点描述：{node_description}
"""
    if prerequisites:
        prompt += f"- 前置知识：{', '.join(prerequisites)}\n"

    prompt += "\n请生成一份清晰、专业、易懂的教材。"
    return prompt


def build_exercise_prompt(node_title: str, node_description: str) -> str:
    """构建练习题生成提示词"""
    return f"""请为以下知识点生成练习题：

- 知识点标题：{node_title}
- 知识点描述：{node_description}

请生成 5-8 道题目，包括选择题和简答题。"""


def parse_content_response(text: str) -> dict:
    """从 LLM 响应中解析 JSON"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从 LLM 响应中解析 JSON: {text[:200]}...")


async def generate_content(
    node_title: str,
    node_description: str,
    content_type: str = "lesson",
    prerequisites: list = None,
) -> dict:
    """
    调用 LLM 生成教材内容（带重试机制）

    Args:
        node_title: 知识点标题
        node_description: 知识点描述
        content_type: 内容类型（lesson/exercise）
        prerequisites: 前置知识列表

    Returns:
        解析后的内容 dict
    """
    llm = get_llm(temperature=0.7)

    if content_type == "exercise":
        system_prompt = EXERCISE_SYSTEM_PROMPT
        user_prompt = build_exercise_prompt(node_title, node_description)
    else:
        system_prompt = LESSON_SYSTEM_PROMPT
        user_prompt = build_content_prompt(node_title, node_description, prerequisites)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    max_retries = 5
    retry_delay = 180  # 3 分钟

    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            content = parse_content_response(response.content)
            return content

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"遇到限流 (429)，等待 {retry_delay} 秒后重试... (第 {attempt + 1}/{max_retries} 次)")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"达到最大重试次数 ({max_retries})，仍然遇到限流: {error_msg}")
            else:
                raise
