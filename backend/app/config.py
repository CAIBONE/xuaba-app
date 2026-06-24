"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置，从环境变量读取"""

    # 应用
    APP_NAME: str = "学吧"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://xueba:xueba@localhost:5432/xueba"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM 配置
    LLM_PROVIDER: str = "openai"  # openai / dashscope / local
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7

    # Audit Agent 配置
    AUDIT_AGENT_URL: str = "http://localhost:8001"
    AUDIT_TIMEOUT: int = 600  # 审计超时（秒）

    # 微信小程序
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24 * 7  # 7 天

    # 管理后台
    ADMIN_API_KEY: str = "change-this-admin-key"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
