"""掌握度历史记录模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MasteryHistory(Base):
    """掌握度历史记录表"""
    __tablename__ = "mastery_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("nodes.id"), index=True)

    mastery_level: Mapped[float] = mapped_column(Numeric(3, 2), comment="掌握度 0.00~1.00")
    assessment_type: Mapped[str] = mapped_column(String(30), comment="quiz/review/self_report")
    assessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MasteryHistory(id={self.id}, node_id={self.node_id}, mastery={self.mastery_level})>"
