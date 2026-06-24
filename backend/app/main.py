"""学吧 API - FastAPI 入口"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db, close_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    yield
    # 关闭时
    await close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="学吧 - AI 智能学习助手 API",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# Web 测试界面
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/test.html")

@app.get("/admin")
async def admin_dashboard():
    return FileResponse("static/admin/index.html")


# 注册 API 路由
from app.api import auth, projects, nodes, contents, quizzes, reports, notes, chat, admin, schedules

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["知识节点"])
app.include_router(contents.router, prefix="/api/contents", tags=["教材"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["测验"])
app.include_router(reports.router, prefix="/api/reports", tags=["报表"])
app.include_router(notes.router, prefix="/api", tags=["笔记"])
app.include_router(chat.router, prefix="/api", tags=["对话"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["学习计划"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
