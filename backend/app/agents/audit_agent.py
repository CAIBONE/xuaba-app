"""Audit Agent 服务 - 独立审计服务"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

from app.config import settings
from app.agents.tools.audit import audit_tool


# Audit Agent 系统提示
AUDIT_AGENT_SYSTEM = """你是学习质量审计专家，你的职责是独立审查学习内容的质量。

你审查的对象包括：
1. 知识图谱 - 结构完整性、依赖合理性、时间合理性
2. 学习教材 - 字数达标、结构完整、知识准确
3. 测验题目 - 答案正确、题目清晰、难度分布合理

审查原则：
- 独立判断，不受生成过程影响
- 只看生成物本身和审计标准
- 硬指标（hard）必须通过
- 软指标（soft）可带标记通过

输出格式：
- verdict: passed / passed_with_notes / not_passed
- checks: 每个检查项的结果
- failed_hard: 硬指标失败数
- failed_soft: 软指标失败数
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    yield


# 创建 Audit Agent 服务
audit_app = FastAPI(
    title="学吧审计服务",
    version="0.1.0",
    description="Audit Agent - 独立审计知识图谱、教材、测验的质量",
    lifespan=lifespan,
)


class AuditRequest(BaseModel):
    """审计请求"""
    audit_type: Literal["knowledge_tree", "content", "quiz"] = Field(..., description="审计类型")
    artifact: dict = Field(..., description="待审计的生成物")
    context: dict = Field(default_factory=dict, description="上下文信息")


class AuditCheck(BaseModel):
    """审计检查项"""
    name: str
    severity: str
    passed: bool
    details: str = ""
    fix_action: str = ""


class AuditResponse(BaseModel):
    """审计响应"""
    verdict: str = Field(..., description="passed/passed_with_notes/not_passed")
    checks: list[AuditCheck] = []
    failed_hard: int = 0
    failed_soft: int = 0
    summary: str = ""


@audit_app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "audit-agent"}


@audit_app.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest):
    """
    审计接口

    接收生成物，返回审计结果。
    Main Agent 通过 HTTP 调用此接口。
    """
    try:
        result = audit_tool.invoke({
            "audit_type": request.audit_type,
            "artifact": request.artifact,
            "context": request.context
        })

        return AuditResponse(
            verdict=result.get("verdict", "not_passed"),
            checks=[AuditCheck(**c) for c in result.get("checks", [])],
            failed_hard=result.get("failed_hard", 0),
            failed_soft=result.get("failed_soft", 0),
            summary=result.get("summary", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 单独运行 Audit Agent 服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.agents.audit_agent:audit_app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
    )
