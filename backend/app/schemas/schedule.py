"""学习计划相关 Schema"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ScheduleBase(BaseModel):
    planned_start: date
    planned_end: date


class ScheduleCreate(ScheduleBase):
    project_id: int
    node_id: int


class ScheduleUpdate(BaseModel):
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    adjust_reason: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    id: int
    project_id: int
    node_id: int
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: str
    progress_percent: int
    adjusted_at: Optional[datetime] = None
    adjust_reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    total: int
    items: list[ScheduleResponse]


class GeneratePlanRequest(BaseModel):
    """生成学习计划请求"""
    project_id: int
    daily_minutes: int = Field(default=30, ge=10, le=240, description="每日学习时长（分钟）")
    start_date: date = Field(default_factory=date.today, description="开始日期")
    intensity: str = Field(default="normal", description="low/normal/high")


class PlanStrategy(BaseModel):
    """学习策略"""
    daily_minutes: int = 30
    review_interval: str = "1-3-7-15"  # 艾宾浩斯复习间隔
    intensity: str = "normal"
    start_date: date
