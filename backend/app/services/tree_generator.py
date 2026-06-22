"""知识图谱生成服务"""
import json
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm
from app.config import settings

SYSTEM_PROMPT = """你是一个专业的学习规划师。你的任务是根据用户的学习目标，生成一棵以知识点为核心的知识图谱。

## 核心原则

1. **知识点导向**：每个节点都是一个具体的、可学习的知识点（concept），不是章节或模块
2. **递进关系**：知识点之间要有明确的先后依赖关系，体现从基础到进阶的学习路径
3. **网状结构**：知识点之间可以有多对多的依赖关系，形成知识网络
4. **粒度适中**：每个知识点应该能在 15-60 分钟内学会，太大要拆分，太小要合并
5. **实用性**：知识点要覆盖该领域必须掌握的核心概念和技能

## 输出格式要求

你必须严格输出 JSON，不要输出任何其他内容。JSON 结构如下：

```json
{
  "knowledge_points": [
    {
      "title": "知识点标题（简洁明确）",
      "node_key": "kp-001",
      "estimated_minutes": 30,
      "description": "一句话描述这个知识点是什么",
      "prerequisites": [],
      "level": 0
    },
    {
      "title": "另一个知识点",
      "node_key": "kp-002",
      "estimated_minutes": 45,
      "description": "一句话描述",
      "prerequisites": ["kp-001"],
      "level": 1
    },
    {
      "title": "进阶知识点",
      "node_key": "kp-003",
      "estimated_minutes": 40,
      "description": "一句话描述",
      "prerequisites": ["kp-001", "kp-002"],
      "level": 2
    }
  ]
}
```

## 字段说明

- `title`: 知识点名称，要具体明确（如"需求法则与供给法则"，而不是"第二章 市场原理"）
- `node_key`: 唯一标识，格式 `kp-XXX`（XXX 为三位数字）
- `estimated_minutes`: 预计学习分钟数（15-60 分钟）
- `description`: 一句话说明这个知识点的核心内容
- `prerequisites`: 前置知识点的 node_key 列表（必须掌握这些才能学当前知识点）
- `level`: 层级深度（0=最基础，数字越大越进阶）

## 生成规则

1. 知识点总数控制在 30-80 个
2. 必须有清晰的起点（level=0 的基础知识点，没有前置依赖）
3. 每个知识点的 prerequisites 必须是已经定义过的 node_key
4. 知识点要覆盖该学科的核心概念，由浅入深、循序渐进
5. 如果用户有截止日期，总学时不应超过可用时间（按每天 1-2 小时估算）
6. 只输出 JSON，不要输出任何解释文字

## 示例结构

```
level 0: 基础概念 A, 基础概念 B (无前置)
  ↓
level 1: 进阶概念 C (依赖 A), 进阶概念 D (依赖 A, B)
  ↓
level 2: 综合应用 E (依赖 C, D), 高级概念 F (依赖 D)
  ↓
level 3: 实战技巧 G (依赖 E, F)
```

"""


def build_user_prompt(subject: str, goal: str, goal_type: str, deadline: Optional[str] = None) -> str:
    """构建用户提示词"""
    prompt = f"""请为以下学习目标生成知识图谱：

- 科目：{subject}
- 学习目标：{goal}
- 目标类型：{goal_type}
"""
    if deadline:
        prompt += f"- 截止日期：{deadline}\n"

    prompt += "\n请生成知识点级别的知识图谱，体现知识点之间的递进和依赖关系。"
    return prompt


def parse_tree_response(text: str) -> dict:
    """从 LLM 响应中解析 JSON 树结构"""
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 ```json ... ``` 代码块
    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试找到第一个 { 和最后一个 }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从 LLM 响应中解析 JSON: {text[:200]}...")


def flatten_tree(tree: dict) -> list[dict]:
    """将知识图谱扁平化为节点列表（用于批量插入数据库）"""
    nodes = []

    for kp in tree.get("knowledge_points", []):
        nodes.append({
            "node_key": kp["node_key"],
            "title": kp["title"],
            "description": kp.get("description", ""),
            "parent_id": None,  # 知识点图谱没有父子关系
            "level": kp.get("level", 0),
            "estimated_minutes": kp.get("estimated_minutes", 30),
            "prerequisites": kp.get("prerequisites", []),
        })

    return nodes


async def generate_knowledge_tree(
    subject: str,
    goal: str,
    goal_type: str = "skill",
    deadline: Optional[str] = None,
) -> dict:
    """
    调用 LLM 生成知识树（带重试机制）

    Returns:
        解析后的树结构 dict，包含 knowledge_points 列表
    """
    llm = get_llm(temperature=0.5)  # 较低温度保证结构稳定

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=build_user_prompt(subject, goal, goal_type, deadline)),
    ]

    max_retries = 5
    retry_delay = 180  # 3 分钟

    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            tree = parse_tree_response(response.content)

            # 验证基本结构
            if "knowledge_points" not in tree:
                raise ValueError("生成的知识图谱缺少 knowledge_points 字段")

            return tree

        except Exception as e:
            error_msg = str(e)
            # 检查是否是 429 限流错误
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"遇到限流 (429)，等待 {retry_delay} 秒后重试... (第 {attempt + 1}/{max_retries} 次)")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"达到最大重试次数 ({max_retries})，仍然遇到限流: {error_msg}")
            else:
                # 非限流错误，直接抛出
                raise
