"""学习项目模型"""
from datetime import datetime, date
from sqlalchemy import BigInteger, String, Text, Date, Integer, Numeric, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Project(Base):
    """学习项目表（学习科目表）"""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    subject: Mapped[str] = mapped_column(String(100), comment="科目名称")
    goal_description: Mapped[str] = mapped_column(Text, default="", comment="学习目标")
    goal_type: Mapped[str] = mapped_column(String(50), default="skill", comment="exam/skill/interest")
    deadline: Mapped[date] = mapped_column(Date, nullable=True, comment="截止日期")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="active/completed/paused")

    # 知识图谱元信息
    tree_version: Mapped[int] = mapped_column(Integer, default=0, comment="知识图谱版本")
    tree_total_nodes: Mapped[int] = mapped_column(Integer, default=0, comment="节点总数")
    tree_total_hours: Mapped[float] = mapped_column(Numeric(5, 1), default=0, comment="预计总学时")

    # 学习目标策略
    plan_strategy: Mapped[dict] = mapped_column(JSON, default=dict, comment="学习策略配置")

    # 目标梳理（2-track 系统）
    baseline_level: Mapped[str] = mapped_column(Text, default="", comment="用户当前水平描述")
    benchmark_source: Mapped[str] = mapped_column(Text, default="", comment="考试标准来源")
    target_score: Mapped[str] = mapped_column(String(50), default="", comment="目标分数")
    learning_why: Mapped[str] = mapped_column(Text, default="", comment="学习动机")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Project(id={self.id}, subject={self.subject})>"
