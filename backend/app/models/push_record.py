"""推送记录模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PushRecord(Base):
    """推送记录表"""
    __tablename__ = "push_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    content_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contents.id"), index=True)

    channel: Mapped[str] = mapped_column(String(20), default="in_app", comment="wechat/in_app")
    status: Mapped[str] = mapped_column(String(20), default="sent", comment="sent/delivered/read/completed")

    pushed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user_rating: Mapped[int] = mapped_column(Integer, nullable=True, comment="1-5 评分")
    feedback: Mapped[str] = mapped_column(Text, default="", comment="文字反馈")

    def __repr__(self):
        return f"<PushRecord(id={self.id}, content_id={self.content_id}, status={self.status})>"
