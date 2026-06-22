"""知识节点模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Numeric, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Node(Base):
    """知识节点表"""
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), index=True)
    node_key: Mapped[str] = mapped_column(String(100), comment="节点标识（如 kp-001）")
    title: Mapped[str] = mapped_column(String(200), comment="节点标题")
    description: Mapped[str] = mapped_column(Text, default="", comment="知识点描述")
    parent_id: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="父节点 ID")
    level: Mapped[int] = mapped_column(Integer, default=0, comment="层级深度")
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30, comment="预计学习时间（分钟）")
    prerequisites: Mapped[list] = mapped_column(JSON, default=list, comment="前置节点 ID 列表")

    # 学习状态
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="pending/in_progress/completed")
    mastery_level: Mapped[float] = mapped_column(Numeric(3, 2), default=0, comment="掌握度 0.00~1.00")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Node(id={self.id}, title={self.title})>"
