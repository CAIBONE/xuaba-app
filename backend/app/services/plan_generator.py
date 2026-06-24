"""每日学习计划生成服务"""
import json
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node import Node
from app.models.project import Project


async def generate_daily_plan(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    daily_study_minutes: int = 60
) -> dict:
    """
    生成每日学习计划

    Args:
        project_id: 项目 ID
        user_id: 用户 ID
        db: 数据库会话
        daily_study_minutes: 每日学习时间（分钟）

    Returns:
        每日学习计划
    """
    # 获取项目信息
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("项目不存在")

    # 获取所有节点
    result = await db.execute(
        select(Node)
        .where(Node.project_id == project_id)
        .order_by(Node.level, Node.node_key)
    )
    all_nodes = result.scalars().all()

    if not all_nodes:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "project_id": project_id,
            "nodes": [],
            "total_minutes": 0,
            "message": "暂无知识点，请先生成知识图谱"
        }

    # 分类节点
    pending_nodes = [n for n in all_nodes if n.status == "pending"]
    in_progress_nodes = [n for n in all_nodes if n.status == "in_progress"]
    completed_nodes = [n for n in all_nodes if n.status == "completed"]

    # 生成今日计划
    today_plan = []
    total_minutes = 0

    # 1. 优先安排正在学习的节点
    for node in in_progress_nodes:
        if total_minutes + node.estimated_minutes <= daily_study_minutes:
            today_plan.append({
                "node_id": node.id,
                "title": node.title,
                "estimated_minutes": node.estimated_minutes,
                "status": "in_progress",
                "priority": "high"
            })
            total_minutes += node.estimated_minutes

    # 2. 安排新的节点（按层级和依赖关系排序）
    for node in pending_nodes:
        if total_minutes >= daily_study_minutes:
            break

        # 检查前置知识是否已完成
        prerequisites_met = True
        if node.prerequisites:
            prereq_ids = [int(pid) for pid in node.prerequisites if pid]
            completed_ids = [n.id for n in completed_nodes]
            prerequisites_met = all(pid in completed_ids for pid in prereq_ids)

        if prerequisites_met:
            today_plan.append({
                "node_id": node.id,
                "title": node.title,
                "estimated_minutes": node.estimated_minutes,
                "status": "pending",
                "priority": "normal"
            })
            total_minutes += node.estimated_minutes

    # 3. 安排复习节点（基于遗忘曲线）
    # 简单实现：找出已完成但掌握度低于 0.7 的节点
    review_nodes = [n for n in completed_nodes if float(n.mastery_level) < 0.7]
    for node in review_nodes[:2]:  # 最多安排 2 个复习节点
        if total_minutes + 15 <= daily_study_minutes:  # 复习节点固定 15 分钟
            today_plan.append({
                "node_id": node.id,
                "title": f"[复习] {node.title}",
                "estimated_minutes": 15,
                "status": "review",
                "priority": "medium"
            })
            total_minutes += 15

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "project_id": project_id,
        "subject": project.subject,
        "nodes": today_plan,
        "total_minutes": total_minutes,
        "total_nodes": len(today_plan),
        "progress": {
            "pending": len([n for n in today_plan if n["status"] == "pending"]),
            "in_progress": len([n for n in today_plan if n["status"] == "in_progress"]),
            "review": len([n for n in today_plan if n["status"] == "review"])
        }
    }
