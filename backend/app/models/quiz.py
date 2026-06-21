"""测验模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Numeric, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Quiz(Base):
    """测验表"""
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("nodes.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    quiz_type: Mapped[str] = mapped_column(String(50), comment="pre_test/post_test/review/practice")

    # 题目内容
    questions: Mapped[list] = mapped_column(JSON, default=list, comment="题目列表")

    # 测验结果
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    answers_json: Mapped[dict] = mapped_column(JSON, default=dict, comment="用户答案详情")

    # 掌握度变化
    mastery_before: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    mastery_after: Mapped[float] = mapped_column(Numeric(3, 2), default=0)

    # 时间
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Quiz(id={self.id}, node_id={self.node_id}, score={self.score})>"
