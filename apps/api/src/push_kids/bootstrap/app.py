from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager, suppress
from typing import TextIO

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from push_kids.activities.router import router as activities_router
from push_kids.agent_processing.providers import build_provider
from push_kids.agent_processing.worker import AnalysisWorker
from push_kids.children.router import router as children_router
from push_kids.data_management.router import router as data_management_router
from push_kids.data_management.worker import DataDeletionWorker
from push_kids.families.rate_limit import InvitePreviewRateLimiter
from push_kids.families.router import router as families_router
from push_kids.learning.router import router as learning_router
from push_kids.media.preview_limit import MediaPreviewLimiter
from push_kids.media.store import build_media_store
from push_kids.notifications.router import router as notifications_router
from push_kids.notifications.scheduler import NotificationScheduler
from push_kids.notifications.service import build_channel
from push_kids.planning.router import router as planning_router
from push_kids.platform.config import Settings, get_settings
from push_kids.platform.database import Database
from push_kids.platform.errors import AppError
from push_kids.reporting.router import router as reporting_router
from push_kids.travel.router import router as travel_router

logger = logging.getLogger("push_kids")
_CLOUD_HANDLER_MARKER = "_push_kids_cloud_handler"


def configure_cloud_logging(stream: TextIO | None = None) -> None:
    """Route application INFO events to cloud stderr without changing root logging."""
    application_logger = logging.getLogger("push_kids")
    application_logger.setLevel(logging.INFO)
    has_cloud_handler = any(
        getattr(item, _CLOUD_HANDLER_MARKER, False) for item in application_logger.handlers
    )
    if has_cloud_handler:
        return
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    setattr(handler, _CLOUD_HANDLER_MARKER, True)
    application_logger.addHandler(handler)
    application_logger.propagate = False


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()
    if config.is_cloud:
        configure_cloud_logging()
    config.validate_cloud_runtime()
    database = Database(config)
    provider = build_provider(config)
    media_store = build_media_store(config)
    worker = AnalysisWorker(database, provider, media_store, config.worker_poll_seconds)
    deletion_worker = DataDeletionWorker(database, media_store, config.worker_poll_seconds)
    notification_channel = build_channel(config)
    notification_scheduler = NotificationScheduler(
        database, notification_channel, config.notification_tick_seconds
    )

    def worker_done(task: asyncio.Task) -> None:
        if not task.cancelled():
            error = task.exception()
            if error is not None:
                logger.warning("worker_task_exited error_type=%s", type(error).__name__)

    def scheduler_done(task: asyncio.Task) -> None:
        if not task.cancelled():
            error = task.exception()
            if error is not None:
                logger.warning("notification_scheduler_exited error_type=%s", type(error).__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if config.is_cloud:
            database.verify_cloud_schema()
        else:
            config.media_root.mkdir(parents=True, exist_ok=True)
            database.create_schema()
        task = asyncio.create_task(worker.run()) if config.run_worker else None
        deletion_task = asyncio.create_task(deletion_worker.run()) if config.run_worker else None
        app.state.worker_task = task
        app.state.deletion_worker_task = deletion_task
        for running_task in (task, deletion_task):
            if running_task:
                running_task.add_done_callback(worker_done)
        # Reminders are only scheduled where a channel exists, so an unconfigured deployment does
        # not spend database work producing rows that could never be sent.
        scheduler_task = (
            asyncio.create_task(notification_scheduler.run())
            if config.run_notification_scheduler and notification_channel.available
            else None
        )
        app.state.notification_scheduler_task = scheduler_task
        if scheduler_task:
            scheduler_task.add_done_callback(scheduler_done)
        try:
            yield
        finally:
            try:
                if scheduler_task:
                    notification_scheduler.stop()
                    with suppress(asyncio.CancelledError, Exception):
                        await scheduler_task
                if task:
                    worker.stop()
                    # The completion callback consumes and safely reports task failure.
                    with suppress(asyncio.CancelledError, Exception):
                        await task
                if deletion_task:
                    deletion_worker.stop()
                    with suppress(asyncio.CancelledError, Exception):
                        await deletion_task
            finally:
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
    app.state.media_preview_limiter = MediaPreviewLimiter()
    app.state.worker = worker
    app.state.worker_task = None
    app.state.deletion_worker = deletion_worker
    app.state.deletion_worker_task = None
    app.state.invite_preview_limiter = InvitePreviewRateLimiter()
    app.state.notification_channel = notification_channel
    app.state.notification_scheduler = notification_scheduler
    app.state.notification_scheduler_task = None
    if config.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origin_list,
            allow_methods=["GET", "POST", "PATCH", "DELETE"],
            allow_headers=["Content-Type", "X-Family-ID", "X-Debug-Actor", "Idempotency-Key"],
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
    def health_ready():
        database.check_ready()
        if config.is_cloud:
            database.verify_cloud_schema()
        task = app.state.worker_task
        deletion_task = app.state.deletion_worker_task
        if config.run_worker and (
            task is None
            or task.done()
            or not worker.is_ready
            or deletion_task is None
            or deletion_task.done()
            or not deletion_worker.is_ready
        ):
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "worker_unavailable",
                        "message": "分析任务执行器暂不可用",
                    }
                },
            )
        return {"status": "ready"}

    api_prefix = "/api/v1"
    app.include_router(children_router, prefix=api_prefix)
    app.include_router(data_management_router, prefix=api_prefix)
    app.include_router(families_router, prefix=api_prefix)
    app.include_router(learning_router, prefix=api_prefix)
    app.include_router(planning_router, prefix=api_prefix)
    app.include_router(activities_router, prefix=api_prefix)
    app.include_router(travel_router, prefix=api_prefix)
    app.include_router(reporting_router, prefix=api_prefix)
    app.include_router(notifications_router, prefix=api_prefix)
    return app
