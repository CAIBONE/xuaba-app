"""用户模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment="微信 openid")
    nickname: Mapped[str] = mapped_column(String(100), default="", comment="昵称")
    avatar: Mapped[str] = mapped_column(String(500), default="", comment="头像 URL")
    profile_json: Mapped[dict] = mapped_column(JSON, default=dict, comment="学习偏好、速度、薄弱点等")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"
