"""对话历史模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Conversation(Base):
    """对话历史表"""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), nullable=True, index=True)

    session_key: Mapped[str] = mapped_column(String(100), index=True, comment="会话标识")
    messages: Mapped[list] = mapped_column(JSON, default=list, comment="对话消息列表")
    message_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_key={self.session_key})>"
