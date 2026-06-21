"""报表 API"""
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.node import Node
from app.models.mastery_history import MasteryHistory
from app.models.study_log import StudyLog
from app.models.quiz import Quiz
from app.schemas.report import (
    ProgressReport, MasteryReport, MasteryPoint,
    HeatmapReport, HeatmapDay,
    ForgettingReport, ForgettingPoint,
    WeakNodesReport, WeakNode
)
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/progress/{project_id}", response_model=ProgressReport)
async def get_progress_report(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """学习进度报表"""
    # 验证项目
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 统计节点
    nodes_result = await db.execute(
        select(Node).where(Node.project_id == project_id)
    )
    nodes = nodes_result.scalars().all()

    total_nodes = len(nodes)
    completed_nodes = sum(1 for n in nodes if n.status == "completed")
    in_progress_nodes = sum(1 for n in nodes if n.status == "in_progress")
    pending_nodes = sum(1 for n in nodes if n.status == "pending")

    # 计算学时
    total_hours_planned = sum(n.estimated_minutes for n in nodes) / 60.0
    # TODO: 从 study_logs 计算实际学时
    total_hours_spent = 0.0

    completion_rate = completed_nodes / total_nodes if total_nodes > 0 else 0

    return ProgressReport(
        project_id=project_id,
        subject=project.subject,
        total_nodes=total_nodes,
        completed_nodes=completed_nodes,
        in_progress_nodes=in_progress_nodes,
        pending_nodes=pending_nodes,
        completion_rate=round(completion_rate, 2),
        total_hours_planned=round(total_hours_planned, 1),
        total_hours_spent=round(total_hours_spent, 1),
    )


@router.get("/mastery/{project_id}/{node_id}", response_model=MasteryReport)
async def get_mastery_report(
    project_id: int,
    node_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """知识点掌握度变化报表"""
    # 验证节点
    result = await db.execute(
        select(Node).where(Node.id == node_id, Node.project_id == project_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 获取掌握度历史
    history_result = await db.execute(
        select(MasteryHistory)
        .where(MasteryHistory.user_id == user.id, MasteryHistory.node_id == node_id)
        .order_by(MasteryHistory.assessed_at)
    )
    history_records = history_result.scalars().all()

    points = [
        MasteryPoint(
            date=h.assessed_at.date(),
            mastery_level=float(h.mastery_level),
            node_id=node_id,
            node_title=node.title
        )
        for h in history_records
    ]

    # 判断趋势
    if len(points) >= 2:
        trend = "improving" if points[-1].mastery_level > points[-2].mastery_level else "stable"
    else:
        trend = "stable"

    return MasteryReport(
        project_id=project_id,
        node_id=node_id,
        node_title=node.title,
        current_mastery=float(node.mastery_level),
        history=points,
        trend=trend
    )


@router.get("/heatmap", response_model=HeatmapReport)
async def get_heatmap_report(
    days: int = 365,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """打卡热力图报表"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # 获取学习日志
    result = await db.execute(
        select(StudyLog)
        .where(StudyLog.user_id == user.id, StudyLog.study_date >= start_date)
        .order_by(StudyLog.study_date)
    )
    logs = result.scalars().all()

    # 转换为热力图数据
    log_map = {log.study_date: log for log in logs}
    heatmap_days = []
    total_minutes = 0
    active_days = 0

    current = start_date
    while current <= end_date:
        log = log_map.get(current)
        if log:
            minutes = log.minutes_spent
            total_minutes += minutes
            active_days += 1
            # 计算活跃度等级
            level = min(4, minutes // 30) if minutes > 0 else 0
        else:
            minutes = 0
            level = 0

        heatmap_days.append(HeatmapDay(date=current, minutes_spent=minutes, level=level))
        current += timedelta(days=1)

    return HeatmapReport(
        user_id=user.id,
        start_date=start_date,
        end_date=end_date,
        total_days=days,
        active_days=active_days,
        total_minutes=total_minutes,
        days=heatmap_days
    )


@router.get("/forgetting/{project_id}", response_model=ForgettingReport)
async def get_forgetting_report(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """遗忘曲线报表"""
    # 获取项目下所有已学习的节点
    result = await db.execute(
        select(Node).where(Node.project_id == project_id, Node.status == "completed")
    )
    nodes = result.scalars().all()

    points = []
    for node in nodes:
        # 获取最近评估时间
        history_result = await db.execute(
            select(MasteryHistory)
            .where(MasteryHistory.user_id == user.id, MasteryHistory.node_id == node.id)
            .order_by(MasteryHistory.assessed_at.desc())
            .limit(1)
        )
        last_history = history_result.scalar_one_or_none()

        if last_history:
            days_since = (date.today() - last_history.assessed_at.date()).days
            # 艾宾浩斯遗忘曲线简化模型
            retention = 0.9 if days_since <= 1 else 0.7 if days_since <= 3 else 0.5 if days_since <= 7 else 0.3
            predicted_mastery = float(node.mastery_level) * retention

            points.append(ForgettingPoint(
                node_id=node.id,
                node_title=node.title,
                last_review_date=last_history.assessed_at.date(),
                days_since_review=days_since,
                current_mastery=float(node.mastery_level),
                predicted_mastery=round(predicted_mastery, 2),
                needs_review=predicted_mastery < 0.5
            ))

    return ForgettingReport(
        user_id=user.id,
        project_id=project_id,
        points=points,
        total_nodes_to_review=sum(1 for p in points if p.needs_review)
    )


@router.get("/weak-nodes/{project_id}", response_model=WeakNodesReport)
async def get_weak_nodes(
    project_id: int,
    threshold: float = 0.6,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """欠掌握知识点报表"""
    # 获取掌握度低于阈值的节点
    result = await db.execute(
        select(Node).where(
            Node.project_id == project_id,
            Node.mastery_level < threshold,
            Node.status.in_(["in_progress", "completed"])
        )
    )
    weak_nodes_list = result.scalars().all()

    weak_nodes = []
    for node in weak_nodes_list:
        # 获取测验统计
        quiz_result = await db.execute(
            select(func.count(Quiz.id), func.avg(Quiz.score))
            .where(Quiz.user_id == user.id, Quiz.node_id == node.id)
        )
        quiz_count, avg_score = quiz_result.one()

        # 获取最近评估时间
        history_result = await db.execute(
            select(MasteryHistory)
            .where(MasteryHistory.user_id == user.id, MasteryHistory.node_id == node.id)
            .order_by(MasteryHistory.assessed_at.desc())
            .limit(1)
        )
        last_assessed = history_result.scalar_one_or_none()

        weak_nodes.append(WeakNode(
            node_id=node.id,
            node_title=node.title,
            mastery_level=float(node.mastery_level),
            last_assessed=last_assessed.assessed_at if last_assessed else datetime.utcnow(),
            quiz_count=quiz_count or 0,
            avg_score=round(float(avg_score or 0), 2)
        ))

    return WeakNodesReport(
        user_id=user.id,
        project_id=project_id,
        threshold=threshold,
        weak_nodes=weak_nodes,
        total_count=len(weak_nodes)
    )
