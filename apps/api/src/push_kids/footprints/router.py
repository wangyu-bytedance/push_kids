"""Transport-only footprint API. All owner/expiry checks live in services."""

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Header, Query, Request, Response, UploadFile
from sqlalchemy.orm import Session

from push_kids.footprints import access
from push_kids.footprints.imports import FootprintImports
from push_kids.footprints.media_service import FootprintMedia
from push_kids.footprints.reads import FootprintReads
from push_kids.footprints.schemas import (
    Claim,
    Confirm,
    ImportCreate,
    ManualCreate,
    PhotoPatch,
    PreferencePatch,
    VisitOrder,
)
from push_kids.footprints.service import FootprintsService, view
from push_kids.platform.context import RequestContext, manager_context, request_context
from push_kids.platform.dependencies import get_db

router = APIRouter(prefix="/footprints", tags=["footprints"])
Context = Annotated[RequestContext, Depends(request_context)]
DB = Annotated[Session, Depends(get_db)]
ChildId = Annotated[str, Query(min_length=1, max_length=36)]
PageSize = Annotated[int, Query(ge=1, le=50)]
Cursor = Annotated[str | None, Query(max_length=1500)]
Manager = Annotated[RequestContext, Depends(manager_context)]


@router.get("/cleanup")
def failed_cleanup(child_id: ChildId, context: Manager, db: DB):
    return FootprintsService.failed_cleanup(db, context.family_id, child_id)


@router.post("/photos/{photo_id}/cleanup-retry")
def retry_cleanup(
    photo_id: str, child_id: ChildId, context: Manager, db: DB, version: Annotated[int, Query(ge=0)]
):
    return FootprintsService.retry_cleanup(db, context.family_id, child_id, photo_id, version)


@router.patch("/visits/{visit_id}/order")
def order_visit(visit_id: str, body: VisitOrder, child_id: ChildId, context: Context, db: DB):
    return FootprintsService.order_visit(db, context.family_id, child_id, visit_id, body)


@router.get("/preferences")
def preferences(context: Context, db: DB):
    return FootprintsService.preferences(db, context.family_id, context.member_id)


@router.patch("/preferences")
def set_preferences(body: PreferencePatch, context: Context, db: DB):
    return FootprintsService.set_preferences(db, context.family_id, context.member_id, body)


@router.post("/imports", status_code=201)
def create_import(
    body: ImportCreate,
    context: Context,
    db: DB,
    key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=100)],
):
    return FootprintImports.create(db, context.family_id, context.member_id, body, key)


@router.post("/manual", status_code=201)
def manual(
    body: ManualCreate,
    context: Context,
    db: DB,
    key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=100)],
):
    return FootprintImports.manual(db, context.family_id, context.member_id, body, key)


@router.get("/imports/{import_id}")
def get_import(import_id: str, child_id: ChildId, context: Context, db: DB):
    return FootprintImports.get(db, context.family_id, child_id, import_id)


@router.post("/imports/{import_id}/confirm")
def confirm(import_id: str, body: Confirm, child_id: ChildId, context: Context, db: DB):
    return FootprintsService.confirm(db, context.family_id, child_id, import_id, body)


@router.get("/drafts")
def drafts(
    child_id: ChildId, context: Context, db: DB, cursor: Cursor = None, limit: PageSize = 20
):
    return FootprintReads.drafts(db, context.family_id, child_id, cursor, limit)


@router.get("/photos/{photo_id}")
def get_photo(photo_id: str, child_id: ChildId, context: Context, db: DB):
    return view(access.photo(db, context.family_id, child_id, photo_id))


@router.patch("/photos/{photo_id}")
def patch_photo(photo_id: str, body: PhotoPatch, child_id: ChildId, context: Context, db: DB):
    return FootprintsService.patch(db, context.family_id, child_id, photo_id, body)


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: str, child_id: ChildId, context: Context, db: DB, version: Annotated[int, Query(ge=0)]
):
    FootprintsService.delete_photo(db, context.family_id, child_id, photo_id, version)
    return Response(status_code=204)


@router.post("/photos/{photo_id}/retry")
def retry(
    photo_id: str, child_id: ChildId, context: Context, db: DB, version: Annotated[int, Query(ge=0)]
):
    return FootprintsService.retry(db, context.family_id, child_id, photo_id, version)


@router.post("/photos/{photo_id}/upload-ticket")
def ticket(photo_id: str, child_id: ChildId, context: Context, db: DB):
    return FootprintImports.ticket(db, context.family_id, child_id, photo_id, context.member_id)


@router.post("/photos/{photo_id}/claim")
def claim(
    photo_id: str, body: Claim, child_id: ChildId, request: Request, context: Context, db: DB
):
    return FootprintImports.claim(
        db, context.family_id, child_id, photo_id, context, request.app.state.media_store, body
    )


@router.post("/photos/{photo_id}/upload")
async def upload(
    photo_id: str,
    child_id: ChildId,
    request: Request,
    context: Context,
    db: DB,
    file: Annotated[UploadFile, File()],
):
    return await FootprintImports.upload(
        db,
        context.family_id,
        child_id,
        photo_id,
        context.member_id,
        request.app.state.media_store,
        file,
    )


@router.get("/photos/{photo_id}/preview")
def preview(
    photo_id: str,
    child_id: ChildId,
    request: Request,
    response: Response,
    context: Context,
    db: DB,
    size: Literal["display", "thumbnail"] = "display",
):
    response.headers["Cache-Control"] = "no-store"
    return FootprintMedia.preview(
        db,
        context.family_id,
        child_id,
        photo_id,
        size,
        request.app.state.media_store,
        request.app.state.media_preview_limiter,
        context.member_id or context.family_id,
    )


@router.get("/photos/{photo_id}/content")
def content(
    photo_id: str,
    child_id: ChildId,
    request: Request,
    context: Context,
    db: DB,
    size: Literal["display", "thumbnail"] = "display",
):
    data = FootprintMedia.content(
        db, context.family_id, child_id, photo_id, size, request.app.state.media_store
    )
    return Response(
        content=data,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/visits")
def visits(
    child_id: ChildId,
    context: Context,
    db: DB,
    start: date | None = None,
    end: date | None = None,
    cursor: Cursor = None,
    limit: PageSize = 20,
    place: Annotated[str | None, Query(max_length=64)] = None,
):
    return FootprintReads.visits(db, context.family_id, child_id, start, end, cursor, limit, place)


@router.get("/visits/{visit_id}/photos")
def visit_photos(
    visit_id: str,
    child_id: ChildId,
    context: Context,
    db: DB,
    cursor: Cursor = None,
    limit: PageSize = 20,
):
    return FootprintReads.photos(db, context.family_id, child_id, visit_id, cursor, limit)


@router.get("/summary")
def summary(
    child_id: ChildId, context: Context, db: DB, start: date | None = None, end: date | None = None
):
    return FootprintReads.summary(db, context.family_id, child_id, start, end)


@router.get("/map")
def map_points(
    child_id: ChildId,
    context: Context,
    db: DB,
    start: date | None = None,
    end: date | None = None,
    mode: Literal["auto", "china", "world"] = "auto",
    west: Annotated[float | None, Query(ge=-180, le=180)] = None,
    south: Annotated[float | None, Query(ge=-90, le=90)] = None,
    east: Annotated[float | None, Query(ge=-180, le=180)] = None,
    north: Annotated[float | None, Query(ge=-90, le=90)] = None,
):
    values = (west, south, east, north)
    if any(v is not None for v in values) and not all(v is not None for v in values):
        raise ValueError("请提供完整地图范围")
    return FootprintReads.map_points(
        db, context.family_id, child_id, start, end, values if west is not None else None, mode
    )


@router.get("/playback")
def playback(
    child_id: ChildId,
    context: Context,
    db: DB,
    cursor: Cursor = None,
    start: date | None = None,
    end: date | None = None,
    revision: int | None = None,
):
    return FootprintReads.playback(db, context.family_id, child_id, start, end, cursor, revision)


@router.get("/places/search")
def search_places(
    request: Request,
    context: Context,
    keyword: Annotated[str, Query(min_length=1, max_length=120)],
    region: Annotated[str, Query(min_length=1, max_length=80)],
):
    return FootprintsService.search_places(
        request.app.state.footprint_places,
        request.app.state.media_preview_limiter,
        context.member_id or context.family_id,
        keyword,
        region,
    )
