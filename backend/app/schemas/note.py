"""笔记相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    note_type: str = Field(default="note", description="note/highlight/question")
    text: str = Field(..., description="笔记内容")
    highlight_range: Optional[dict] = Field(None, description="划线范围")


class NoteResponse(BaseModel):
    id: int
    content_id: int
    user_id: int
    note_type: str
    text: str
    highlight_range: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    total: int
    items: list[NoteResponse]
