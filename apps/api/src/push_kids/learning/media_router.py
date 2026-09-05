"""Authenticated read access to original submission media; no public local mounts."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from push_kids.learning.history import LearningHistory
from push_kids.media.store import LocalMediaStore, WeChatCloudMediaStore
from push_kids.platform.context import RequestContext, family_id, request_context
from push_kids.platform.dependencies import get_db
from push_kids.platform.errors import GoneError

router = APIRouter(tags=["learning"])


@router.get("/submissions/{submission_id}/media/{media_id}/preview")
def preview(
    submission_id: str,
    media_id: str,
    child_id: str,
    request: Request,
    response: Response,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(request_context)],
):
    media = LearningHistory.media(db, family, child_id, submission_id, media_id)
    assert media.path is not None
    request.app.state.media_preview_limiter.check(context.member_id or family)
    response.headers["Cache-Control"] = "no-store"
    store = request.app.state.media_store
    if isinstance(store, WeChatCloudMediaStore):
        return {"url": store.preview_url(media.path), "expires_in": 60}
    with store.materialize(media.path) as path:
        if not path.is_file():
            raise GoneError("原图已删除或不可用")
    return {
        "download_path": (
            f"/submissions/{submission_id}/media/{media_id}/content?child_id={child_id}"
        )
    }


@router.get("/submissions/{submission_id}/media/{media_id}/content")
def content(
    submission_id: str,
    media_id: str,
    child_id: str,
    request: Request,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    media = LearningHistory.media(db, family, child_id, submission_id, media_id)
    assert media.path is not None
    store = request.app.state.media_store
    if not isinstance(store, LocalMediaStore):
        raise GoneError("请重新获取照片预览")
    with store.materialize(media.path) as path:
        if not path.is_file() or path.stat().st_size > store.max_bytes:
            raise GoneError("原图已删除或不可用")
        data = path.read_bytes()
    return Response(
        content=data,
        media_type=media.content_type,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
