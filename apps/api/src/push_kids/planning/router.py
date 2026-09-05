from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from push_kids.planning.schemas import FeedbackRequest, FeedbackResult
from push_kids.planning.service import PlanningService
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["planning"])


@router.get("/children/{child_id}/todos")
def daily_todos(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    day: Annotated[date | None, Query()] = None,
):
    return {
        "day": (day or date.today()).isoformat(),
        "groups": PlanningService.daily_todos(db, family, child_id, day),
    }


@router.post("/reviews/{review_id}/feedback", response_model=FeedbackResult)
def feedback(
    review_id: str,
    body: FeedbackRequest,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ] = None,
):
    return PlanningService.feedback(db, family, review_id, body.action, idempotency_key)


@router.get("/children/{child_id}/practice-materials")
def practice_materials(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    review_ids: str | None = None,
):
    selected = [item for item in (review_ids or "").split(",") if item]
    return PlanningService.practice_materials(db, family, child_id, review_ids=selected)
