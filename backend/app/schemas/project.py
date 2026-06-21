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
    pass


class ProjectUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=100)
    goal_description: Optional[str] = None
    goal_type: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[str] = None
    plan_strategy: Optional[dict] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    tree_version: int
    tree_total_nodes: int
    tree_total_hours: float
    plan_strategy: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    items: list[ProjectResponse]
