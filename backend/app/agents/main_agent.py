"""Main Agent - 学习逻辑主 Agent"""
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from app.agents.llm import llm
from app.agents.tools.knowledge_tree import generate_knowledge_tree
from app.agents.tools.content_gen import generate_content
from app.agents.tools.quiz_gen import generate_quiz
from app.agents.tools.audit import audit_tool


# Main Agent 系统提示
MAIN_AGENT_SYSTEM = """你是学吧，一位智能学习助手。你的职责是帮助用户高效学习。

你可以：
1. 根据学习目标生成知识图谱
2. 根据知识节点生成学习教材
3. 根据教材内容生成测验题目
4. 追踪学习进度和掌握度

工作流程：
1. 用户设定学习目标 → 生成知识图谱 → 审计
2. 根据知识图谱生成学习计划
3. 按计划逐个节点生成教材 → 审计 → 推送
4. 每个节点学习后生成测验 → 审计 → 测验
5. 根据测验结果更新掌握度
6. 生成学习报表

重要原则：
- 所有生成物必须经过审计
- 审计不通过需要修复后重新审计
- 最多重试 3 次，超过则提交用户裁决
- 内容密度按 250-300 字/分钟设计
"""


# 创建 Main Agent
tools = [generate_knowledge_tree, generate_content, generate_quiz, audit_tool]

main_agent = create_react_agent(
    llm,
    tools,
    prompt=MAIN_AGENT_SYSTEM
)


async def run_main_agent(
    user_message: str,
    thread_id: Optional[str] = None
) -> dict:
    """
    运行 Main Agent

    Args:
        user_message: 用户消息
        thread_id: 会话 ID（用于保持上下文）

    Returns:
        Agent 响应
    """
    config = {"configurable": {"thread_id": thread_id or "default"}}

    result = await main_agent.ainvoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=config
    )

    # 提取最终响应
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        return {
            "response": last_message.content if hasattr(last_message, "content") else str(last_message),
            "messages": messages
        }

    return {"response": "", "messages": []}


# 便捷方法
async def generate_knowledge_tree_with_audit(
    subject: str,
    goal: str,
    goal_type: str = "skill"
) -> dict:
    """生成知识图谱并审计"""
    # 生成
    tree_result = generate_knowledge_tree.invoke({
        "subject": subject,
        "goal": goal,
        "goal_type": goal_type
    })

    # 审计
    audit_result = audit_tool.invoke({
        "audit_type": "knowledge_tree",
        "artifact": tree_result,
        "context": {"subject": subject, "goal": goal}
    })

    return {
        "tree": tree_result,
        "audit": audit_result,
        "passed": audit_result.get("verdict") in ["passed", "passed_with_notes"]
    }


async def generate_content_with_audit(
    node_title: str,
    node_description: str = "",
    content_type: str = "lesson",
    difficulty: str = "normal",
    estimated_minutes: int = 30
) -> dict:
    """生成教材并审计"""
    # 生成
    content_result = generate_content.invoke({
        "node_title": node_title,
        "node_description": node_description,
        "content_type": content_type,
        "difficulty": difficulty,
        "estimated_minutes": estimated_minutes
    })

    # 审计
    audit_result = audit_tool.invoke({
        "audit_type": "content",
        "artifact": content_result,
        "context": {"node_title": node_title}
    })

    return {
        "content": content_result,
        "audit": audit_result,
        "passed": audit_result.get("verdict") in ["passed", "passed_with_notes"]
    }


async def generate_quiz_with_audit(
    node_title: str,
    node_content: str,
    quiz_type: str = "post_test",
    question_count: int = 5
) -> dict:
    """生成测验并审计"""
    # 生成
    quiz_result = generate_quiz.invoke({
        "node_title": node_title,
        "node_content": node_content,
        "quiz_type": quiz_type,
        "question_count": question_count
    })

    # 审计
    audit_result = audit_tool.invoke({
        "audit_type": "quiz",
        "artifact": quiz_result,
        "context": {"node_title": node_title}
    })

    return {
        "quiz": quiz_result,
        "audit": audit_result,
        "passed": audit_result.get("verdict") in ["passed", "passed_with_notes"]
    }
