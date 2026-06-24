"""管理后台 API"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.node import Node
from app.models.content import Content
from app.models.quiz import Quiz
from app.config import settings

router = APIRouter()


async def verify_admin_key(x_admin_key: str = Header(...)):
    """验证管理员密钥"""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin_key)
):
    """获取仪表板统计数据"""
    # 用户统计
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar()

    # 项目统计
    project_count_result = await db.execute(select(func.count(Project.id)))
    project_count = project_count_result.scalar()

    # 知识点统计
    node_count_result = await db.execute(select(func.count(Node.id)))
    node_count = node_count_result.scalar()

    # 教材统计
    content_count_result = await db.execute(select(func.count(Content.id)))
    content_count = content_count_result.scalar()

    # 测验统计
    quiz_count_result = await db.execute(select(func.count(Quiz.id)))
    quiz_count = quiz_count_result.scalar()

    return {
        "user_count": user_count,
        "project_count": project_count,
        "node_count": node_count,
        "content_count": content_count,
        "quiz_count": quiz_count
    }


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin_key)
):
    """获取用户列表"""
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return [
        {
            "id": u.id,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "project_count": 0  # TODO: 计算用户项目数
        }
        for u in users
    ]


@router.get("/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin_key)
):
    """获取项目列表"""
    result = await db.execute(
        select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "subject": p.subject,
            "goal_description": p.goal_description,
            "goal_type": p.goal_type,
            "deadline": p.deadline.isoformat() if p.deadline else None,
            "status": p.status,
            "tree_total_nodes": p.tree_total_nodes,
            "tree_total_hours": float(p.tree_total_hours) if p.tree_total_hours else 0,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in projects
    ]


@router.get("/system")
async def get_system_info(
    _: None = Depends(verify_admin_key)
):
    """获取系统信息"""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "debug_mode": settings.DEBUG
    }
