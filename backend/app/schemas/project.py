"""学习项目相关 Schema"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    subject: str = Field(..., max_length=100, description="科目名称")
    goal_description: str = Field(default="", description="学习目标")
    goal_type: str = Field(default="skill", description="exam/skill/interest")
    deadline: Optional[date] = None


class ProjectCreate(ProjectBase):
    baseline_level: Optional[str] = None
    benchmark_source: Optional[str] = None
    target_score: Optional[str] = None
    learning_why: Optional[str] = None


class ProjectUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=100)
    goal_description: Optional[str] = None
    goal_type: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[str] = None
    plan_strategy: Optional[dict] = None
    baseline_level: Optional[str] = None
    benchmark_source: Optional[str] = None
    target_score: Optional[str] = None
    learning_why: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    tree_version: int
    tree_total_nodes: int
    tree_total_hours: float
    plan_strategy: dict
    baseline_level: str
    benchmark_source: str
    target_score: str
    learning_why: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    items: list[ProjectResponse]
