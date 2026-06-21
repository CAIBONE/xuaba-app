"""教材模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Content(Base):
    """教材表"""
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("nodes.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)

    content_type: Mapped[str] = mapped_column(String(50), comment="lesson/summary/exercise/example")
    title: Mapped[str] = mapped_column(String(200), comment="教材标题")
    content_json: Mapped[dict] = mapped_column(JSON, default=dict, comment="完整内容")
    word_count: Mapped[int] = mapped_column(Integer, default=0, comment="字数")
    difficulty_level: Mapped[str] = mapped_column(String(20), default="normal", comment="easy/normal/hard")

    # 审计状态
    audit_status: Mapped[str] = mapped_column(String(30), default="pending", comment="pending/passed/not_passed")
    audit_retry_count: Mapped[int] = mapped_column(Integer, default=0)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="发布（推送）时间")

    def __repr__(self):
        return f"<Content(id={self.id}, title={self.title})>"
