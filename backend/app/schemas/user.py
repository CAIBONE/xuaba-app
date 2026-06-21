"""用户相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    nickname: str = Field(default="", max_length=100)
    avatar: str = Field(default="")


class UserCreate(UserBase):
    openid: str = Field(..., max_length=64)


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    profile_json: Optional[dict] = None


class UserResponse(UserBase):
    id: int
    openid: str
    profile_json: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户学习档案"""
    learning_speed: Optional[float] = None
    preferred_style: Optional[str] = None
    weak_areas: list[str] = []
    available_time_pattern: Optional[dict] = None


class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录 code")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
