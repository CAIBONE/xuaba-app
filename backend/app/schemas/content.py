"""教材相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    content_type: str = Field(..., description="lesson/summary/exercise/example")
    title: str = Field(..., max_length=200)
    content_json: dict = Field(default_factory=dict)
    word_count: int = Field(default=0, ge=0)
    difficulty_level: str = Field(default="normal", description="easy/normal/hard")


class ContentCreate(ContentBase):
    node_id: int
    user_id: int


class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content_json: Optional[dict] = None
    audit_status: Optional[str] = None


class ContentResponse(ContentBase):
    id: int
    node_id: int
    user_id: int
    audit_status: str
    audit_retry_count: int
    generated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    total: int
    items: list[ContentResponse]


class GenerateContentRequest(BaseModel):
    """生成教材请求"""
    node_id: int
    content_type: str = Field(default="lesson", description="lesson/summary/exercise/example")
    difficulty: str = Field(default="normal", description="easy/normal/hard")


class PushContentRequest(BaseModel):
    """推送教材请求"""
    channel: str = Field(default="in_app", description="wechat/in_app")
