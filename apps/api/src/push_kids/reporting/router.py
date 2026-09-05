from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
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
):
    return {"items": ReportingService.history(db, family, child_id)}


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
