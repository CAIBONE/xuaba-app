"""目标梳理服务 - 2-track 系统"""
import json
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm

GOAL_REFINER_PROMPT = """你是一个专业的学习顾问。你的任务是帮助用户梳理和明确学习目标。

## 工作方式

你需要通过对话了解：
1. 用户想学什么
2. 为什么要学（动机）
3. 当前水平如何
4. 期望达到什么程度
5. 有多少时间

根据目标类型，采用不同的策略：

### 考试型目标（有明确标准）
- 确认考试科目、目标分数、考试时间
- 了解当前水平（可以是分数、等级、或描述性如"零基础"、"有一些基础"）
- 询问每周可投入的学习时间

### 技能型目标（无明确标准）
- 确认想学到什么程度（能做什么）
- 了解当前基础
- 定义 2-3 个可验证的里程碑

## 输出格式

你必须严格输出 JSON，不要输出任何其他内容：

```json
{
  "goal_type": "exam" 或 "skill",
  "refined_goal": "梳理后的明确目标描述",
  "baseline_level": "用户当前水平描述",
  "target": {
    "score": "目标分数（如果是考试型）",
    "date": "目标日期",
    "milestones": ["里程碑1", "里程碑2"]
  },
  "weekly_hours": 10,
  "follow_up_questions": ["还有什么需要了解的？"],
  "ready": false
}
```

当 ready=true 时，表示目标已经足够明确，可以开始生成知识图谱。
当 ready=false 时，follow_up_questions 包含需要继续追问的问题。
"""


def parse_refiner_response(text: str) -> dict:
    """解析目标梳理响应"""
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

    raise ValueError(f"无法解析目标梳理响应: {text[:200]}...")


async def refine_goal(
    raw_goal: str,
    conversation_history: list[dict] = None,
) -> dict:
    """
    梳理学习目标

    Args:
        raw_goal: 用户原始目标描述
        conversation_history: 之前的对话历史

    Returns:
        梳理后的目标信息
    """
    llm = get_llm(temperature=0.5)

    messages = [SystemMessage(content=GOAL_REFINER_PROMPT)]

    # 添加对话历史
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(SystemMessage(content=f"（之前的分析结果：{msg['content']}）"))

    # 添加当前用户输入
    messages.append(HumanMessage(content=f"我的学习目标是：{raw_goal}"))

    max_retries = 5
    retry_delay = 180

    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            result = parse_refiner_response(response.content)
            return result
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise
            else:
                raise
