"""报表相关 Schema"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ProgressReport(BaseModel):
    """学习进度报表"""
    project_id: int
    subject: str
    total_nodes: int
    completed_nodes: int
    in_progress_nodes: int
    pending_nodes: int
    completion_rate: float = Field(ge=0, le=1)
    total_hours_planned: float
    total_hours_spent: float
    estimated_completion_date: Optional[date] = None


class MasteryPoint(BaseModel):
    """掌握度数据点"""
    date: date
    mastery_level: float
    node_id: int
    node_title: str


class MasteryReport(BaseModel):
    """掌握度变化报表"""
    project_id: int
    node_id: int
    node_title: str
    current_mastery: float
    history: list[MasteryPoint]
    trend: str = Field(description="improving/stable/declining")


class HeatmapDay(BaseModel):
    """热力图单日数据"""
    date: date
    minutes_spent: int
    level: int = Field(ge=0, le=4, description="活跃度等级 0-4")


class HeatmapReport(BaseModel):
    """打卡热力图报表"""
    user_id: int
    start_date: date
    end_date: date
    total_days: int
    active_days: int
    total_minutes: int
    days: list[HeatmapDay]


class ForgettingPoint(BaseModel):
    """遗忘曲线数据点"""
    node_id: int
    node_title: str
    last_review_date: date
    days_since_review: int
    current_mastery: float
    predicted_mastery: float = Field(description="根据遗忘曲线预测")
    needs_review: bool


class ForgettingReport(BaseModel):
    """遗忘曲线报表"""
    user_id: int
    project_id: int
    points: list[ForgettingPoint]
    total_nodes_to_review: int


class WeakNode(BaseModel):
    """薄弱知识点"""
    node_id: int
    node_title: str
    mastery_level: float
    last_assessed: datetime
    quiz_count: int
    avg_score: float


class WeakNodesReport(BaseModel):
    """欠掌握知识点报表"""
    user_id: int
    project_id: int
    threshold: float = Field(description="掌握度阈值")
    weak_nodes: list[WeakNode]
    total_count: int
