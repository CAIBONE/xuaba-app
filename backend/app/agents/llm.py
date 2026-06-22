"""LLM 客户端配置"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.config import settings


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> BaseChatModel:
    """获取 LLM 实例"""
    # DashScope OpenAI 兼容模式
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    return ChatOpenAI(
        model=model or settings.LLM_MODEL,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        api_key=settings.LLM_API_KEY,
        base_url=base_url,
    )


# 默认 LLM 实例
llm = get_llm()

# 用于审计的 LLM（可能需要更严格的温度）
audit_llm = get_llm(temperature=0.3)
