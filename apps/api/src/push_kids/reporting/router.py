from datetime import date
from typing import Annotated, Literal
from urllib.parse import unquote

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session

from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db
from push_kids.reporting.service import ReportingService

router = APIRouter(tags=["reporting"])


@router.get("/children/{child_id}/dashboard")
def dashboard(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    day: date | None = None,
):
    return ReportingService.dashboard(db, family, child_id, day)


@router.get("/children/{child_id}/daily-summary")
def daily_summary(
    child_id: str,
    day: date,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ReportingService.daily_summary(db, family, child_id, day)


@router.get("/children/{child_id}/history")
def history(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    view: Literal["confirmed", "pending", "all"] | None = None,
    history_query: Annotated[str, Header(alias="X-History-Query", max_length=1200)] = "",
    subject_id: str | None = None,
    source: Literal["photo", "text"] | None = None,
    start: Annotated[date | None, Query(alias="from")] = None,
    end: Annotated[date | None, Query(alias="to")] = None,
    cancelled: bool = False,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    response.headers["Cache-Control"] = "no-store"
    q = unquote(history_query, errors="strict").strip()
    if len(q) > 100:
        raise ValueError("搜索内容最多 100 字")
    if view is not None:
        if cancelled and view != "all":
            raise ValueError("已取消筛选仅适用于全部记录")
        return ReportingService.history_page(
            db,
            family,
            child_id,
            view=view,
            q=q.strip(),
            subject_id=subject_id,
            source=source,
            start=start,
            end=end,
            cancelled=cancelled,
            cursor=cursor,
            limit=limit,
        )
    return {"items": ReportingService.history(db, family, child_id)}


@router.get("/children/{child_id}/history/{submission_id}")
def history_detail(
    child_id: str,
    submission_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ReportingService.history_detail(db, family, child_id, submission_id)


@router.get("/children/{child_id}/history/{submission_id}/reviews")
def history_reviews(
    child_id: str,
    submission_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    review_id: str | None = None,
    before: str | None = None,
):
    return ReportingService.history_reviews(db, family, child_id, submission_id, review_id, before)


@router.get("/children/{child_id}/calendar")
def calendar(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
):
    return ReportingService.calendar(db, family, child_id, month)


@router.get("/children/{child_id}/report")
def report(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(default=7),
):
    if days not in {7, 30, 100}:
        raise ValueError("报表范围只支持 7、30 或 100 天")
    return ReportingService.report(db, family, child_id, days)
