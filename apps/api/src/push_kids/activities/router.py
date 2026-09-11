from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session

from push_kids.activities.schemas import (
    ActivityRecordCreate,
    ActivityRecordView,
    ActivityScheduleCreate,
    ActivityScheduleList,
    ActivityScheduleUpdate,
    ActivityScheduleView,
    CalendarEventPatch,
    CalendarEventView,
    CalendarEventWrite,
)
from push_kids.activities.service import ActivitiesService
from push_kids.activities.weekly_slots import has_weekly_time_slots_capability
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["activities"])


@router.post("/activity-schedules", response_model=ActivityScheduleView, status_code=201)
def create_schedule(
    body: ActivityScheduleCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    item = ActivitiesService.create_schedule(db, family, body, client_supports_slots=supports_slots)
    return ActivitiesService.view(db, item, client_supports_slots=supports_slots)


@router.get(
    "/children/{child_id}/activity-schedules",
    response_model=ActivityScheduleList,
)
def list_schedules(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    items = ActivitiesService.list_schedules(db, family, child_id)
    return {
        "items": [
            ActivitiesService.view(db, item, client_supports_slots=supports_slots) for item in items
        ]
    }


@router.patch("/activity-schedules/{schedule_id}", response_model=ActivityScheduleView)
def update_schedule(
    schedule_id: str,
    body: ActivityScheduleUpdate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    item = ActivitiesService.update_schedule(
        db,
        family,
        schedule_id,
        body,
        client_supports_slots=supports_slots,
    )
    return ActivitiesService.view(db, item, client_supports_slots=supports_slots)


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
    items = ActivitiesService.events_for_day(db, family, child_id, day, include_travel=True)
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
    response: Response,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    page = ActivitiesService.record_page(db, family, child_id, cursor=cursor, limit=limit)
    response.headers["X-Result-Limit"] = str(limit)
    if page["next_cursor"]:
        response.headers["X-Next-Cursor"] = page["next_cursor"]
    return page["items"]


@router.get("/children/{child_id}/activity-suggestions")
def suggestions(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    day: date | None = None,
):
    return {"items": ActivitiesService.suggestions(db, family, child_id, day)}
