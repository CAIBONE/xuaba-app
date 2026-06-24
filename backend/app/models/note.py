"""学习笔记模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Note(Base):
    """学习笔记表"""
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    content_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contents.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)

    note_type: Mapped[str] = mapped_column(String(20), default="note", comment="note/highlight/question")
    text: Mapped[str] = mapped_column(Text, comment="笔记内容")
    highlight_range: Mapped[dict] = mapped_column(JSON, nullable=True, comment="划线范围 {start, end}")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, content_id={self.content_id})>"
