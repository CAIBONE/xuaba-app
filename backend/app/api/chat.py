"""对话 API - 有记忆的 LLM Agent"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.node import Node
from app.models.conversation import Conversation
from app.agents.llm import get_llm
from app.api.auth import get_current_user

router = APIRouter()


def build_system_prompt(project_subject: str, knowledge_points: list[dict], user_profile: dict) -> str:
    """构建系统提示词，包含项目知识和用户画像"""
    kp_text = "\n".join([f"- {kp['title']}: {kp.get('description', '')}" for kp in knowledge_points[:20]])

    # 用户画像
    profile_text = ""
    if user_profile:
        strengths = user_profile.get("strengths", [])
        weaknesses = user_profile.get("weaknesses", [])
        learning_style = user_profile.get("learning_style", "")
        expertise = user_profile.get("expertise", [])

        if strengths:
            profile_text += f"\n强项: {', '.join(strengths)}"
        if weaknesses:
            profile_text += f"\n弱项: {', '.join(weaknesses)}"
        if expertise:
            profile_text += f"\n专长: {', '.join(expertise)}"
        if learning_style:
            profile_text += f"\n学习风格: {learning_style}"

    return f"""你是一个专业的学习助手，正在帮助学生学习「{project_subject}」。

学生画像：{profile_text if profile_text else '暂无详细信息'}

可访问的知识点：
{kp_text}

回答规则：
1. 基于上述知识点回答问题
2. 根据学生的强项和弱项调整回答深度（强项可深入，弱项需详细解释）
3. 如果问题超出知识点范围，诚实说明
4. 回答要简洁、准确、易懂
5. 可以举例说明，但不要超出知识点范围
6. 如果学生提问模糊，主动引导他们明确问题
7. 记住学生的特点，在后续对话中持续关注他们的薄弱环节
"""


@router.post("/chat/{project_id}")
async def chat(
    project_id: int,
    message: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """与 LLM 对话（有记忆）"""
    # 验证项目存在
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取项目知识点
    nodes_result = await db.execute(
        select(Node).where(Node.project_id == project_id).order_by(Node.level, Node.node_key)
    )
    nodes = nodes_result.scalars().all()
    knowledge_points = [{"title": n.title, "description": n.description} for n in nodes]

    # 获取或创建会话
    session_key = f"user_{user.id}_project_{project_id}"
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.project_id == project_id,
            Conversation.session_key == session_key
        )
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            user_id=user.id,
            project_id=project_id,
            session_key=session_key,
            messages=[],
            message_count=0
        )
        db.add(conversation)
        await db.flush()

    # 构建消息列表（包含历史）
    messages = [SystemMessage(content=build_system_prompt(project.subject, knowledge_points, user.profile_json))]

    # 添加历史消息（最近 10 轮）
    history = conversation.messages[-20:] if conversation.messages else []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # 添加当前用户消息
    messages.append(HumanMessage(content=message))

    # 调用 LLM
    llm = get_llm(temperature=0.7)
    response = await llm.ainvoke(messages)
    reply = response.content

    # 更新会话历史
    conversation.messages.append({"role": "user", "content": message})
    conversation.messages.append({"role": "assistant", "content": reply})
    conversation.message_count += 2
    await db.flush()

    return {
        "reply": reply,
        "message_count": conversation.message_count
    }


@router.get("/chat/{project_id}/history")
async def get_chat_history(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取对话历史"""
    session_key = f"user_{user.id}_project_{project_id}"
    result = await db.execute(
        select(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.project_id == project_id,
            Conversation.session_key == session_key
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        return {"messages": [], "message_count": 0}

    return {
        "messages": conversation.messages,
        "message_count": conversation.message_count
    }
