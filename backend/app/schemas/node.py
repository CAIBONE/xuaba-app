"""知识节点相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NodeBase(BaseModel):
    node_key: str = Field(..., max_length=100, description="节点标识")
    title: str = Field(..., max_length=200, description="节点标题")
    parent_id: Optional[int] = None
    level: int = Field(default=0, ge=0)
    estimated_minutes: int = Field(default=30, gt=0)
    prerequisites: list[int] = []


class NodeCreate(NodeBase):
    project_id: int


class NodeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = None
    mastery_level: Optional[float] = Field(None, ge=0, le=1)


class NodeResponse(NodeBase):
    id: int
    project_id: int
    status: str
    mastery_level: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NodeListResponse(BaseModel):
    """节点列表响应"""
    total: int
    items: list[NodeResponse]


class KnowledgeTreeResponse(BaseModel):
    """知识图谱响应"""
    project_id: int
    nodes: list[NodeResponse]
    total_nodes: int
    total_hours: float
