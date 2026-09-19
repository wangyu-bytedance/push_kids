from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from push_kids.planning.schemas import (
    BatchFeedbackRequest,
    BatchFeedbackResult,
    FeedbackRequest,
    FeedbackResult,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db
from push_kids.platform.time import local_date

router = APIRouter(tags=["planning"])


@router.get("/children/{child_id}/todos")
def daily_todos(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    day: Annotated[date | None, Query()] = None,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
):
    page = PlanningService.daily_todo_page(db, family, child_id, day, cursor=cursor, limit=limit)
    return {
        "day": (day or local_date()).isoformat(),
        "groups": page["groups"],
        "total_count": page["total_count"],
        "required_count": page["required_count"],
        "estimated_minutes": page["estimated_minutes"],
        "returned_count": page["returned_count"],
        "remaining_count": page["remaining_count"],
        "next_cursor": page["next_cursor"],
    }


@router.get("/children/{child_id}/upcoming-reviews")
def upcoming_reviews(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    after: Annotated[date | None, Query(alias="after")] = None,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
):
    page = PlanningService.upcoming_review_page(
        db,
        family,
        child_id,
        after,
        cursor=cursor,
        limit=limit,
    )
    return page or {
        "day": None,
        "groups": [],
        "total_count": 0,
        "estimated_minutes": 0,
        "returned_count": 0,
        "remaining_count": 0,
        "next_cursor": None,
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


@router.post("/review-feedback-batches", response_model=BatchFeedbackResult)
def feedback_batch(
    body: BatchFeedbackRequest,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ],
):
    return PlanningService.feedback_batch(
        db,
        family,
        body.child_id,
        [item.model_dump() for item in body.items],
        idempotency_key,
    )


@router.get("/children/{child_id}/practice-materials")
def practice_materials(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    review_ids: str | None = None,
):
    selected = [item for item in (review_ids or "").split(",") if item]
    return PlanningService.practice_materials(db, family, child_id, review_ids=selected)
