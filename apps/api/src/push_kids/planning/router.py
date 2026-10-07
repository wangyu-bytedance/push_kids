from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session

from push_kids.planning.schemas import (
    BatchFeedbackRequest,
    BatchFeedbackResult,
    FeedbackRequest,
    FeedbackResult,
    ScheduleReviewRequest,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db
from push_kids.platform.time import local_date

router = APIRouter(tags=["planning"])


@router.get("/children/{child_id}/review-inventory/subjects")
def review_subjects(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    return PlanningService.inventory_subjects(db, family, child_id, cursor=cursor, limit=limit)


@router.get("/children/{child_id}/review-inventory")
def review_inventory(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    view: Literal["time", "subject", "count"] = "time",
    offset: Annotated[int, Query(ge=1, le=2)] = 1,
    subject_id: Annotated[str | None, Query(max_length=36)] = None,
    review_count: Annotated[int | None, Query(ge=0, le=2147483647)] = None,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    return PlanningService.inventory_page(
        db,
        family,
        child_id,
        view=view,
        offset=offset,
        subject_id=subject_id,
        review_count=review_count,
        cursor=cursor,
        limit=limit,
    )


@router.post("/children/{child_id}/reviews/{review_id}/schedule")
def schedule_review(
    child_id: str,
    review_id: str,
    body: ScheduleReviewRequest,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ],
):
    return PlanningService.schedule_review(
        db,
        family,
        child_id,
        review_id,
        action=body.action,
        base_day=body.base_day,
        expected_version=body.expected_version,
        idempotency_key=idempotency_key,
    )


@router.delete("/children/{child_id}/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(
    child_id: str,
    knowledge_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    PlanningService.delete_knowledge(db, family, child_id, knowledge_id)
    return Response(status_code=204)


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
