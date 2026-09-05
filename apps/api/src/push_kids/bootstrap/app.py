from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from push_kids.activities.router import router as activities_router
from push_kids.agent_processing.providers import build_provider
from push_kids.agent_processing.worker import AnalysisWorker
from push_kids.children.router import router as children_router
from push_kids.learning.router import router as learning_router
from push_kids.media.store import build_media_store
from push_kids.planning.router import router as planning_router
from push_kids.platform.config import Settings, get_settings
from push_kids.platform.database import Database
from push_kids.platform.errors import AppError
from push_kids.reporting.router import router as reporting_router

logger = logging.getLogger("push_kids")


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()
    config.validate_cloud_runtime()
    database = Database(config)
    provider = build_provider(config)
    media_store = build_media_store(config)
    worker = AnalysisWorker(database, provider, media_store, config.worker_poll_seconds)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if config.is_cloud:
            database.verify_cloud_schema()
        else:
            config.media_root.mkdir(parents=True, exist_ok=True)
            database.create_schema()
        task = asyncio.create_task(worker.run()) if config.run_worker else None
        yield
        if task:
            worker.stop()
            await task
        database.engine.dispose()

    app = FastAPI(
        title="Push Kids API",
        version="0.1.0",
        description="家长确认驱动的小学生学习记录、复习计划与活动跟进 API",
        lifespan=lifespan,
        docs_url=None if config.is_cloud else "/docs",
        redoc_url=None if config.is_cloud else "/redoc",
        openapi_url=None if config.is_cloud else "/openapi.json",
    )
    app.state.settings = config
    app.state.database = database
    app.state.analysis_provider = provider
    app.state.media_store = media_store
    app.state.worker = worker
    if config.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origin_list,
            allow_methods=["GET", "POST", "PATCH", "DELETE"],
            allow_headers=["Content-Type", "X-Family-ID"],
        )

    @app.middleware("http")
    async def enforce_cloud_request_limit(request: Request, call_next):
        if config.is_cloud:
            content_length = request.headers.get("content-length")
            if content_length and content_length.isdigit() and int(content_length) > 100 * 1024:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "request_too_large",
                            "message": "云托管接口请求体不能超过 100KB，图片请直传对象存储",
                        }
                    },
                )
        return await call_next(request)

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "invalid_input", "message": str(exc)}},
        )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "ai_provider": config.ai_provider}

    @app.get("/health/live", tags=["system"])
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["system"])
    def health_ready() -> dict[str, str]:
        database.check_ready()
        if config.is_cloud:
            database.verify_cloud_schema()
        return {"status": "ready"}

    api_prefix = "/api/v1"
    app.include_router(children_router, prefix=api_prefix)
    app.include_router(learning_router, prefix=api_prefix)
    app.include_router(planning_router, prefix=api_prefix)
    app.include_router(activities_router, prefix=api_prefix)
    app.include_router(reporting_router, prefix=api_prefix)
    return app
