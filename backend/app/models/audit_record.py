"""审计记录模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditRecord(Base):
    """审计记录表"""
    __tablename__ = "audit_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, index=True)
    node_id: Mapped[int] = mapped_column(BigInteger, nullable=True, index=True)

    # 审计对象
    artifact_type: Mapped[str] = mapped_column(String(50), comment="knowledge_tree/content/quiz")
    artifact_id: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="对应的内容/题目 ID")

    # 审计结果
    verdict: Mapped[str] = mapped_column(String(30), comment="passed/passed_with_notes/not_passed")
    checks_json: Mapped[dict] = mapped_column(JSON, default=dict, comment="检查项详情")
    failed_hard_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_soft_count: Mapped[int] = mapped_column(Integer, default=0)

    # 重试信息
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    final_verdict: Mapped[str] = mapped_column(String(30), default="", comment="最终裁决")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditRecord(id={self.id}, artifact_type={self.artifact_type}, verdict={self.verdict})>"
