"""测验生成服务"""
import json
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm
from app.config import settings

QUIZ_SYSTEM_PROMPT = """你是一个专业的出题老师。你的任务是根据知识点生成测验题目。

## 输出格式要求

你必须严格输出 JSON，不要输出任何其他内容。JSON 结构如下：

```json
{
  "questions": [
    {
      "type": "choice",
      "content": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "A",
      "explanation": "解析",
      "difficulty": "normal"
    },
    {
      "type": "short_answer",
      "content": "简答题题目",
      "answer": "参考答案",
      "explanation": "评分要点",
      "difficulty": "normal"
    }
  ]
}
```

## 规则

1. 题目数量：根据要求生成指定数量的题目
2. 题型分布：
   - 选择题（choice）：60-70%
   - 简答题（short_answer）：30-40%
3. 难度分布：
   - easy: 20%
   - normal: 60%
   - hard: 20%
4. 选择题必须有 4 个选项（A/B/C/D）和正确答案
5. 题目要覆盖知识点的核心内容
6. 每题都有清晰的解析或评分要点
7. 只输出 JSON，不要输出任何解释文字

"""


def build_quiz_prompt(node_title: str, node_description: str, question_count: int, quiz_type: str) -> str:
    """构建测验生成提示词"""
    return f"""请为以下知识点生成测验题目：

- 知识点标题：{node_title}
- 知识点描述：{node_description}
- 题目数量：{question_count} 道
- 测验类型：{quiz_type}

请生成 {question_count} 道题目，包含选择题和简答题，难度分布合理。"""


def parse_quiz_response(text: str) -> dict:
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


async def generate_quiz(
    node_title: str,
    node_description: str,
    question_count: int = 5,
    quiz_type: str = "post_test",
) -> dict:
    """
    调用 LLM 生成测验题目（带重试机制）

    Args:
        node_title: 知识点标题
        node_description: 知识点描述
        question_count: 题目数量
        quiz_type: 测验类型

    Returns:
        包含 questions 列表的 dict
    """
    llm = get_llm(temperature=0.7)

    messages = [
        SystemMessage(content=QUIZ_SYSTEM_PROMPT),
        HumanMessage(content=build_quiz_prompt(node_title, node_description, question_count, quiz_type)),
    ]

    max_retries = 5
    retry_delay = 180  # 3 分钟

    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            quiz = parse_quiz_response(response.content)

            # 验证基本结构
            if "questions" not in quiz:
                raise ValueError("生成的测验缺少 questions 字段")

            return quiz

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
