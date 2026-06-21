"""学习日志模型"""
from datetime import datetime, date
from sqlalchemy import BigInteger, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class StudyLog(Base):
    """学习日志表（用于打卡热力图）"""
    __tablename__ = "study_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "study_date", name="uq_user_study_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), index=True)

    study_date: Mapped[date] = mapped_column(Date, comment="学习日期")
    minutes_spent: Mapped[int] = mapped_column(Integer, default=0, comment="学习时长（分钟）")
    nodes_completed: Mapped[int] = mapped_column(Integer, default=0, comment="完成节点数")
    quizzes_taken: Mapped[int] = mapped_column(Integer, default=0, comment="完成测验数")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StudyLog(id={self.id}, user_id={self.user_id}, date={self.study_date})>"
