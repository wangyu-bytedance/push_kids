from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from push_kids.activities.schemas import (
    ActivityRecordCreate,
    ActivityRecordView,
    ActivityScheduleCreate,
    ActivityScheduleUpdate,
    CalendarEventPatch,
    CalendarEventView,
    CalendarEventWrite,
)
from push_kids.activities.service import ActivitiesService
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["activities"])


def schedule_view(item):
    return {
        "id": item.id,
        "child_id": item.child_id,
        "subject_id": item.subject_id,
        "weekdays": [int(value) for value in (item.weekdays or "").split(",") if value],
        "start_time": item.start_time,
        "end_time": item.end_time,
        "target_per_week": item.target_per_week,
        "note": item.note,
        "active": item.active,
    }


@router.post("/activity-schedules", status_code=201)
def create_schedule(
    body: ActivityScheduleCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    item = ActivitiesService.create_schedule(db, family, body)
    return schedule_view(item)


@router.get("/children/{child_id}/activity-schedules")
def list_schedules(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    items = ActivitiesService.list_schedules(db, family, child_id)
    return {"items": [schedule_view(item) for item in items]}


@router.patch("/activity-schedules/{schedule_id}")
def update_schedule(
    schedule_id: str,
    body: ActivityScheduleUpdate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return schedule_view(ActivitiesService.update_schedule(db, family, schedule_id, body))


@router.delete("/activity-schedules/{schedule_id}", status_code=204)
def remove_schedule(
    schedule_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    ActivitiesService.remove_schedule(db, family, schedule_id)


@router.post("/calendar-events", response_model=CalendarEventView, status_code=201)
def create_event(
    body: CalendarEventWrite,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ] = None,
):
    return ActivitiesService.create_event(db, family, body, idempotency_key)


@router.patch("/calendar-events/{event_id}", response_model=CalendarEventView)
def update_event(
    event_id: str,
    body: CalendarEventPatch,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ActivitiesService.update_event(db, family, event_id, body)


@router.delete("/calendar-events/{event_id}", status_code=204)
def delete_event(
    event_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    ActivitiesService.delete_event(db, family, event_id)


@router.get("/children/{child_id}/schedule")
def schedule_for_day(
    child_id: str,
    day: date,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    items = ActivitiesService.events_for_day(db, family, child_id, day)
    return {"day": day.isoformat(), "items": items}


@router.post("/activity-records", response_model=ActivityRecordView, status_code=201)
def create_record(
    body: ActivityRecordCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ActivitiesService.create_record(db, family, body)


@router.get("/children/{child_id}/activity-records", response_model=list[ActivityRecordView])
def list_records(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ActivitiesService.list_records(db, family, child_id)


@router.get("/children/{child_id}/activity-suggestions")
def suggestions(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    day: date | None = None,
):
    return {"items": ActivitiesService.suggestions(db, family, child_id, day)}
