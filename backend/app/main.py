from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routes import materials, tags, ai, graph, review, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时：清理资源（如有需要）

app = FastAPI(title="学习收集工具", lifespan=lifespan)

# CORS 中间件（开发阶段允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(materials.router)
app.include_router(tags.router)
app.include_router(ai.router)
app.include_router(graph.router)
app.include_router(review.router)
app.include_router(export.router)


@app.get("/api/health")
async def health():
    """健康检查接口"""
    return {"status": "ok"}
