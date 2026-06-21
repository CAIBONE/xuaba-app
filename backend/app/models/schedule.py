"""学习计划表"""
from datetime import datetime, date
from sqlalchemy import BigInteger, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Schedule(Base):
    """学习计划表（按节点排程）"""
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), index=True)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("nodes.id"), index=True)

    # 计划时间
    planned_start: Mapped[date] = mapped_column(Date, comment="计划开始日期")
    planned_end: Mapped[date] = mapped_column(Date, comment="计划结束日期")

    # 实际时间
    actual_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 状态
    status: Mapped[str] = mapped_column(String(20), default="planned", comment="planned/in_progress/completed/delayed/skipped")
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, comment="进度百分比")

    # 调整记录
    adjusted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    adjust_reason: Mapped[str] = mapped_column(Text, default="", comment="调整原因")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Schedule(id={self.id}, node_id={self.node_id}, status={self.status})>"
