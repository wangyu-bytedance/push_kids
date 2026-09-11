from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from hashlib import sha256

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.activities.capacity import ensure_timed_item_capacity
from push_kids.activities.conflicts import attach_conflicts
from push_kids.activities.schemas import (
    ActivityRecordCreate,
    ActivityScheduleCreate,
    ActivityScheduleUpdate,
    CalendarEventPatch,
    CalendarEventWrite,
)
from push_kids.activities.weekly_slots import WeeklySlotValue, slots_from_legacy, uniform_range
from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    ActivityRecord,
    ActivitySchedule,
    ActivityScheduleSlot,
    CalendarEvent,
    CalendarEventRequest,
    Child,
    Subject,
)
from push_kids.platform.errors import ClientUpgradeRequiredError, ConflictError, NotFoundError
from push_kids.platform.pagination import decode_cursor, encode_cursor
from push_kids.platform.time import SHANGHAI, local_date, utcnow
from push_kids.travel.service import TravelService


@dataclass(frozen=True)
class ScheduledOccurrence:
    """One concrete instance of a schedule on one day, expanded in Asia/Shanghai.

    `occurrence_id` is the identity of the *source* row, not of the instance: combined with the
    local day it lets a reminder for a moved event be refreshed rather than duplicated.
    """

    family_id: str
    child_id: str
    child_name: str
    occurrence_id: str
    name: str
    local_day: date
    start_at: datetime
    start_time_text: str
    kind: str
    # None when the source row has no trustworthy end time; a reminder then omits the duration.
    duration_minutes: int | None = None


class ActivitiesService:
    @staticmethod
    def purge_data(db: Session, family_id: str, child_id: str | None) -> None:
        event_query = select(CalendarEvent.id).where(CalendarEvent.family_id == family_id)
        activity_scope = [ActivityRecord.family_id == family_id]
        schedule_scope = [ActivitySchedule.family_id == family_id]
        if child_id is not None:
            event_query = event_query.where(CalendarEvent.child_id == child_id)
            activity_scope.append(ActivityRecord.child_id == child_id)
            schedule_scope.append(ActivitySchedule.child_id == child_id)
        schedule_ids = list(db.scalars(select(ActivitySchedule.id).where(*schedule_scope)))
        event_ids = list(db.scalars(event_query))
        db.execute(
            delete(CalendarEventRequest).where(
                CalendarEventRequest.family_id == family_id,
                CalendarEventRequest.event_id.in_(event_ids),
            )
        )
        db.execute(delete(CalendarEvent).where(CalendarEvent.id.in_(event_ids)))
        db.execute(delete(ActivityRecord).where(*activity_scope))
        db.execute(
            delete(ActivityScheduleSlot).where(
                ActivityScheduleSlot.family_id == family_id,
                ActivityScheduleSlot.schedule_id.in_(schedule_ids),
            )
        )
        db.execute(delete(ActivitySchedule).where(*schedule_scope))

    @staticmethod
    def _slot_values(db: Session, schedule_id: str) -> tuple[WeeklySlotValue, ...]:
        rows = db.scalars(
            select(ActivityScheduleSlot)
            .where(ActivityScheduleSlot.schedule_id == schedule_id)
            .order_by(ActivityScheduleSlot.weekday)
        )
        values = []
        for row in rows:
            if row.weekday is None or row.start_time is None or row.end_time is None:
                raise RuntimeError("activity schedule slot is incomplete")
            values.append(WeeklySlotValue(row.weekday, row.start_time, row.end_time))
        return tuple(values)

    @staticmethod
    def _ensure_client_supports_slots(
        slots: tuple[WeeklySlotValue, ...], client_supports_slots: bool
    ) -> None:
        if slots and uniform_range(slots) is None and not client_supports_slots:
            raise ClientUpgradeRequiredError("请重新打开或更新小程序后查看不同日期时间")

    @classmethod
    def view(
        cls,
        db: Session,
        item: ActivitySchedule,
        *,
        client_supports_slots: bool,
    ) -> dict:
        slots = cls._slot_values(db, str(item.id))
        cls._ensure_client_supports_slots(slots, client_supports_slots)
        common = uniform_range(slots)
        return {
            "id": item.id,
            "child_id": item.child_id,
            "subject_id": item.subject_id,
            "weekdays": [slot.weekday for slot in slots],
            "start_time": common[0] if common else None,
            "end_time": common[1] if common else None,
            "time_slots": [
                {
                    "weekday": slot.weekday,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                }
                for slot in slots
            ],
            "target_per_week": item.target_per_week,
            "note": item.note,
            "active": item.active,
        }

    @staticmethod
    def _replace_slots(
        db: Session, schedule: ActivitySchedule, slots: tuple[WeeklySlotValue, ...]
    ) -> None:
        db.execute(
            delete(ActivityScheduleSlot).where(
                ActivityScheduleSlot.schedule_id == schedule.id,
                ActivityScheduleSlot.family_id == schedule.family_id,
            )
        )
        for slot in slots:
            db.add(
                ActivityScheduleSlot(
                    family_id=schedule.family_id,
                    child_id=schedule.child_id,
                    schedule_id=schedule.id,
                    weekday=slot.weekday,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                )
            )
        common = uniform_range(slots)
        schedule.weekdays = ",".join(str(slot.weekday) for slot in slots)
        mirror = common or ((slots[0].start_time, slots[0].end_time) if slots else None)
        schedule.start_time = mirror[0] if mirror else None
        schedule.end_time = mirror[1] if mirror else None

    @staticmethod
    def _activity_subject(db: Session, family_id: str, child_id: str, subject_id: str) -> Subject:
        subject = db.scalar(
            select(Subject).where(
                Subject.id == subject_id,
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.kind == "activity",
                Subject.active.is_(True),
            )
        )
        if subject is None:
            raise NotFoundError("没有找到这个活动科目")
        return subject

    @classmethod
    def create_schedule(
        cls,
        db: Session,
        family_id: str,
        data: ActivityScheduleCreate,
        *,
        client_supports_slots: bool = False,
    ) -> ActivitySchedule:
        slots = data.slot_values()
        cls._ensure_client_supports_slots(slots, client_supports_slots)
        ChildrenService.require_active_child(db, family_id, data.child_id)
        cls._activity_subject(db, family_id, data.child_id, data.subject_id)
        existing = db.scalar(
            select(ActivitySchedule).where(
                ActivitySchedule.family_id == family_id,
                ActivitySchedule.child_id == data.child_id,
                ActivitySchedule.subject_id == data.subject_id,
                ActivitySchedule.active.is_(True),
            )
        )
        if existing is not None:
            existing.time_text = data.time_text
            existing.target_per_week = data.target_per_week
            existing.note = data.note
            cls._replace_slots(db, existing, slots)
            db.commit()
            return existing
        ensure_timed_item_capacity(db, family_id, data.child_id)
        schedule = ActivitySchedule(
            family_id=family_id,
            child_id=data.child_id,
            subject_id=data.subject_id,
            weekdays="",
            time_text=data.time_text,
            start_time=None,
            end_time=None,
            target_per_week=data.target_per_week,
            note=data.note,
        )
        db.add(schedule)
        db.flush()
        cls._replace_slots(db, schedule, slots)
        db.commit()
        return schedule

    @classmethod
    def list_schedules(cls, db: Session, family_id: str, child_id: str) -> list[ActivitySchedule]:
        ChildrenService.get_child(db, family_id, child_id)
        return list(
            db.scalars(
                select(ActivitySchedule)
                .where(
                    ActivitySchedule.family_id == family_id,
                    ActivitySchedule.child_id == child_id,
                    ActivitySchedule.active.is_(True),
                )
                .order_by(ActivitySchedule.created_at)
            )
        )

    @classmethod
    def update_schedule(
        cls,
        db: Session,
        family_id: str,
        schedule_id: str,
        data: ActivityScheduleUpdate,
        *,
        client_supports_slots: bool = False,
    ) -> ActivitySchedule:
        schedule = db.scalar(
            select(ActivitySchedule).where(
                ActivitySchedule.id == schedule_id, ActivitySchedule.family_id == family_id
            )
        )
        if schedule is None:
            raise NotFoundError("没有找到这个活动提醒")
        ChildrenService.require_active_child(db, family_id, schedule.child_id)
        current_slots = cls._slot_values(db, schedule_id)
        cls._ensure_client_supports_slots(current_slots, client_supports_slots)
        slot_values = data.slot_values()
        legacy_fields = {"weekdays", "start_time", "end_time"}
        if slot_values is None and legacy_fields & data.model_fields_set:
            current_common = uniform_range(current_slots)
            weekdays = (
                data.weekdays
                if "weekdays" in data.model_fields_set
                else [slot.weekday for slot in current_slots]
            )
            start = (
                data.start_time
                if "start_time" in data.model_fields_set
                else (current_common[0] if current_common else None)
            )
            end = (
                data.end_time
                if "end_time" in data.model_fields_set
                else (current_common[1] if current_common else None)
            )
            slot_values = slots_from_legacy(weekdays or [], start, end)
        if slot_values is not None:
            cls._ensure_client_supports_slots(slot_values, client_supports_slots)
        values = data.model_dump(
            exclude_unset=True,
            exclude={"child_id", "subject_id", "weekdays", "start_time", "end_time", "time_slots"},
        )
        for key, value in values.items():
            setattr(schedule, key, value)
        if slot_values is not None:
            cls._replace_slots(db, schedule, slot_values)
        db.commit()
        return schedule

    @staticmethod
    def remove_schedule(db: Session, family_id: str, schedule_id: str) -> None:
        schedule = db.scalar(
            select(ActivitySchedule).where(
                ActivitySchedule.id == schedule_id,
                ActivitySchedule.family_id == family_id,
            )
        )
        if schedule is None:
            raise NotFoundError("没有找到这个活动提醒")
        ChildrenService.require_active_child(db, family_id, schedule.child_id)
        schedule.active = False
        subject = db.scalar(
            select(Subject).where(
                Subject.id == schedule.subject_id,
                Subject.family_id == family_id,
                Subject.child_id == schedule.child_id,
            )
        )
        if subject is not None:
            subject.active = False
        db.commit()

    @classmethod
    def create_event(
        cls,
        db: Session,
        family_id: str,
        data: CalendarEventWrite,
        idempotency_key: str | None = None,
    ) -> CalendarEvent:
        ChildrenService.require_active_child(db, family_id, data.child_id)
        fingerprint = sha256(
            json.dumps(data.model_dump(mode="json"), sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        if idempotency_key:
            request = db.scalar(
                select(CalendarEventRequest).where(
                    CalendarEventRequest.family_id == family_id,
                    CalendarEventRequest.idempotency_key == idempotency_key,
                )
            )
            if request is not None:
                if request.request_fingerprint != fingerprint:
                    raise ConflictError("此日程提交标识已用于不同内容，请重新提交")
                if request.event_id is None:
                    raise RuntimeError("calendar event request is missing its event")
                return cls._event(db, family_id, request.event_id)
        ensure_timed_item_capacity(db, family_id, data.child_id)
        event = CalendarEvent(family_id=family_id, **data.model_dump())
        db.add(event)
        db.flush()
        if event.id is None:
            raise RuntimeError("calendar event id was not generated")
        if idempotency_key:
            db.add(
                CalendarEventRequest(
                    family_id=family_id,
                    idempotency_key=idempotency_key,
                    request_fingerprint=fingerprint,
                    event_id=event.id,
                )
            )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if not idempotency_key:
                raise
            request = db.scalar(
                select(CalendarEventRequest).where(
                    CalendarEventRequest.family_id == family_id,
                    CalendarEventRequest.idempotency_key == idempotency_key,
                )
            )
            if request is None:
                raise
            if request.request_fingerprint != fingerprint:
                raise ConflictError("此日程提交标识已用于不同内容，请重新提交") from None
            if request.event_id is None:
                raise RuntimeError("calendar event request is missing its event") from None
            return cls._event(db, family_id, request.event_id)
        return event

    @staticmethod
    def _event(db: Session, family_id: str, event_id: str) -> CalendarEvent:
        event = db.scalar(
            select(CalendarEvent).where(
                CalendarEvent.id == event_id, CalendarEvent.family_id == family_id
            )
        )
        if event is None:
            raise NotFoundError("没有找到这个日程")
        return event

    @classmethod
    def update_event(
        cls, db: Session, family_id: str, event_id: str, data: CalendarEventPatch
    ) -> CalendarEvent:
        event = cls._event(db, family_id, event_id)
        ChildrenService.require_active_child(db, family_id, event.child_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(event, key, value)
        if event.start_time is None or event.end_time is None:
            raise ValueError("日程必须包含开始和结束时间")
        if event.end_time <= event.start_time:
            raise ValueError("结束时间必须晚于开始时间")
        db.commit()
        return event

    @classmethod
    def delete_event(cls, db: Session, family_id: str, event_id: str) -> None:
        event = cls._event(db, family_id, event_id)
        ChildrenService.require_active_child(db, family_id, event.child_id)
        event.active = False
        db.commit()

    @classmethod
    def events_for_day(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        target: date,
        *,
        include_travel: bool = False,
    ) -> list[dict]:
        ChildrenService.get_child(db, family_id, child_id)
        direct = list(
            db.scalars(
                select(CalendarEvent).where(
                    CalendarEvent.family_id == family_id,
                    CalendarEvent.child_id == child_id,
                    CalendarEvent.active.is_(True),
                    CalendarEvent.event_date <= target,
                )
            )
        )
        result: list[dict] = []
        for event in direct:
            if (
                event.id is None
                or event.name is None
                or event.event_date is None
                or event.start_time is None
                or event.end_time is None
                or event.kind is None
                or event.repeat_weekly is None
            ):
                continue
            if event.event_date != target and not (
                event.repeat_weekly and event.event_date.weekday() == target.weekday()
            ):
                continue
            result.append(
                cls._event_view(
                    event.id,
                    event.name,
                    target,
                    event.start_time,
                    event.end_time,
                    event.kind,
                    event.repeat_weekly,
                    "calendar",
                    None,
                )
            )
        schedule_rows = db.execute(
            select(ActivitySchedule, Subject, ActivityScheduleSlot)
            .join(Subject, ActivitySchedule.subject_id == Subject.id)
            .join(ActivityScheduleSlot, ActivityScheduleSlot.schedule_id == ActivitySchedule.id)
            .where(
                ActivitySchedule.family_id == family_id,
                ActivitySchedule.child_id == child_id,
                ActivitySchedule.active.is_(True),
                Subject.active.is_(True),
                ActivityScheduleSlot.family_id == family_id,
                ActivityScheduleSlot.child_id == child_id,
                ActivityScheduleSlot.weekday == target.weekday(),
            )
        ).all()
        for schedule, subject, slot in schedule_rows:
            result.append(
                cls._event_view(
                    schedule.id,
                    subject.name,
                    target,
                    slot.start_time,
                    slot.end_time,
                    "activity",
                    True,
                    "activity_schedule",
                    subject.id,
                )
            )
        if include_travel:
            for arrangement in TravelService.projections_for_day(db, family_id, child_id, target):
                if (
                    arrangement.id is None
                    or arrangement.name is None
                    or arrangement.start_time is None
                    or arrangement.end_time is None
                ):
                    continue
                result.append(
                    cls._event_view(
                        arrangement.id,
                        arrangement.name,
                        target,
                        arrangement.start_time,
                        arrangement.end_time,
                        "travel",
                        True,
                        "travel_arrangement",
                        None,
                    )
                )
        ordered = sorted(
            result,
            key=lambda item: (
                item["start_time"],
                item["end_time"],
                item["source"],
                item["id"],
            ),
        )
        return attach_conflicts(ordered)

    @classmethod
    def occurrences_in_window(
        cls, db: Session, window_start: datetime, window_end: datetime
    ) -> list[ScheduledOccurrence]:
        """Every active schedule instance starting inside a bounded UTC window, all families.

        Reminders must not pre-materialise the whole future, so the caller passes a short window
        and re-derives it on every tick. Both sources of the calendar are included: dated events
        and the fixed weekly activity slots that the calendar screen also shows.
        """
        if window_end <= window_start:
            return []
        days = cls._local_days(window_start, window_end)
        children = {
            str(child.id): str(child.name)
            for child in db.scalars(
                select(Child).where(Child.active.is_(True), Child.deleting.is_(False))
            )
        }
        occurrences: list[ScheduledOccurrence] = []
        events = list(
            db.scalars(
                select(CalendarEvent).where(
                    CalendarEvent.active.is_(True),
                    CalendarEvent.event_date <= max(days),
                )
            )
        )
        for event in events:
            if (
                event.id is None
                or event.child_id not in children
                or event.name is None
                or event.event_date is None
                or event.start_time is None
            ):
                continue
            for day in days:
                if event.event_date != day and not (
                    event.repeat_weekly and event.event_date.weekday() == day.weekday()
                ):
                    continue
                if event.event_date > day:
                    continue
                candidate = cls._occurrence(
                    str(event.family_id),
                    str(event.child_id),
                    children[str(event.child_id)],
                    str(event.id),
                    str(event.name),
                    day,
                    event.start_time,
                    str(event.kind or "other"),
                    event.end_time,
                )
                if window_start <= candidate.start_at <= window_end:
                    occurrences.append(candidate)
        rows = db.execute(
            select(ActivitySchedule, Subject, ActivityScheduleSlot)
            .join(Subject, ActivitySchedule.subject_id == Subject.id)
            .join(ActivityScheduleSlot, ActivityScheduleSlot.schedule_id == ActivitySchedule.id)
            .where(
                ActivitySchedule.active.is_(True),
                Subject.active.is_(True),
                ActivityScheduleSlot.family_id == ActivitySchedule.family_id,
                ActivityScheduleSlot.child_id == ActivitySchedule.child_id,
            )
        ).all()
        for schedule, subject, slot in rows:
            if str(schedule.child_id) not in children:
                continue
            for day in days:
                if day.weekday() != slot.weekday:
                    continue
                candidate = cls._occurrence(
                    str(schedule.family_id),
                    str(schedule.child_id),
                    children[str(schedule.child_id)],
                    str(schedule.id),
                    str(subject.name),
                    day,
                    slot.start_time,
                    "activity",
                    slot.end_time,
                )
                if window_start <= candidate.start_at <= window_end:
                    occurrences.append(candidate)
        return sorted(occurrences, key=lambda item: (item.start_at, item.occurrence_id))

    @staticmethod
    def _local_days(window_start: datetime, window_end: datetime) -> list[date]:
        first = window_start.astimezone(SHANGHAI).date()
        last = window_end.astimezone(SHANGHAI).date()
        span = (last - first).days
        return [first + timedelta(days=offset) for offset in range(span + 1)]

    @classmethod
    def _occurrence(
        cls,
        family_id: str,
        child_id: str,
        child_name: str,
        occurrence_id: str,
        name: str,
        day: date,
        start: time,
        kind: str,
        end: time | None = None,
    ) -> ScheduledOccurrence:
        start_at = datetime.combine(day, start, tzinfo=SHANGHAI).astimezone(UTC)
        return ScheduledOccurrence(
            family_id=family_id,
            child_id=child_id,
            child_name=child_name,
            occurrence_id=occurrence_id,
            name=name,
            local_day=day,
            start_at=start_at,
            start_time_text=start.strftime("%H:%M"),
            kind=kind,
            duration_minutes=cls._span_minutes(start, end),
        )

    @staticmethod
    def _span_minutes(start: time, end: time | None) -> int | None:
        """Same-day span only: an end time at or before the start is treated as unknown."""
        if end is None:
            return None
        minutes = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
        return minutes if minutes > 0 else None

    @staticmethod
    def _event_view(
        event_id: str,
        name: str,
        target: date,
        start: time,
        end: time,
        kind: str,
        repeat_weekly: bool,
        source: str,
        subject_id: str | None,
    ) -> dict:
        start_at = datetime.combine(target, start, tzinfo=SHANGHAI).astimezone(UTC)
        end_at = datetime.combine(target, end, tzinfo=SHANGHAI).astimezone(UTC)
        return {
            "id": event_id,
            "name": name,
            "day": target.isoformat(),
            "start_time": start.strftime("%H:%M"),
            "end_time": end.strftime("%H:%M"),
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "kind": kind,
            "repeat_weekly": repeat_weekly,
            "source": source,
            "subject_id": subject_id,
            "past": end_at <= utcnow(),
        }

    @classmethod
    def create_record(
        cls, db: Session, family_id: str, data: ActivityRecordCreate
    ) -> ActivityRecord:
        ChildrenService.require_active_child(db, family_id, data.child_id)
        cls._activity_subject(db, family_id, data.child_id, data.subject_id)
        record = ActivityRecord(family_id=family_id, **data.model_dump())
        db.add(record)
        db.commit()
        return record

    @classmethod
    def list_records(cls, db: Session, family_id: str, child_id: str) -> list[ActivityRecord]:
        return cls.record_page(db, family_id, child_id)["items"]

    @classmethod
    def record_page(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        *,
        limit: int = 100,
        cursor: str | None = None,
    ) -> dict:
        ChildrenService.get_child(db, family_id, child_id)
        scope = ("activity-records-v1", family_id, child_id)
        anchor = None
        as_of = utcnow()
        if cursor:
            payload = decode_cursor(cursor, scope)
            try:
                as_of = datetime.fromisoformat(str(payload["as_of"]))
                anchor_at = datetime.fromisoformat(str(payload["occurred_at"]))
                anchor_id = str(payload["id"])
                if not as_of.tzinfo or not anchor_at.tzinfo or not anchor_id:
                    raise ValueError
                anchor = (anchor_at, anchor_id)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("分页已失效，请刷新列表") from exc
        query = select(ActivityRecord).where(
            ActivityRecord.family_id == family_id,
            ActivityRecord.child_id == child_id,
            ActivityRecord.created_at <= as_of,
        )
        if anchor:
            query = query.where(
                (ActivityRecord.occurred_at < anchor[0])
                | ((ActivityRecord.occurred_at == anchor[0]) & (ActivityRecord.id < anchor[1]))
            )
        items = list(
            db.scalars(
                query.order_by(ActivityRecord.occurred_at.desc(), ActivityRecord.id.desc()).limit(
                    limit + 1
                )
            )
        )
        more = len(items) > limit
        items = items[:limit]
        next_cursor = None
        if more and items:
            last = items[-1]
            if last.occurred_at is None:
                raise RuntimeError("活动记录缺少发生时间")
            next_cursor = encode_cursor(
                scope,
                {
                    "as_of": as_of.isoformat(),
                    "occurred_at": last.occurred_at.isoformat(),
                    "id": last.id,
                },
            )
        return {"items": items, "next_cursor": next_cursor}

    @classmethod
    def suggestions(
        cls, db: Session, family_id: str, child_id: str, day: date | None = None
    ) -> list[dict]:
        ChildrenService.get_child(db, family_id, child_id)
        target = day or local_date()
        schedules = db.execute(
            select(ActivitySchedule, Subject)
            .join(Subject, ActivitySchedule.subject_id == Subject.id)
            .where(
                ActivitySchedule.family_id == family_id,
                ActivitySchedule.child_id == child_id,
                ActivitySchedule.active.is_(True),
                Subject.active.is_(True),
            )
        ).all()
        result = []
        for schedule, subject in schedules:
            slot_values = cls._slot_values(db, str(schedule.id))
            today_slot = next(
                (slot for slot in slot_values if slot.weekday == target.weekday()), None
            )
            target_end = datetime.combine(
                target + timedelta(days=1), time.min, tzinfo=SHANGHAI
            ).astimezone(UTC)
            last_at = db.scalar(
                select(func.max(ActivityRecord.occurred_at)).where(
                    ActivityRecord.family_id == family_id,
                    ActivityRecord.child_id == child_id,
                    ActivityRecord.subject_id == subject.id,
                    ActivityRecord.occurred_at < target_end,
                )
            )
            days_since = (target - local_date(last_at)).days if last_at else None
            week_start = target - timedelta(days=target.weekday())
            week_start_at = datetime.combine(week_start, time.min, tzinfo=SHANGHAI).astimezone(UTC)
            week_end_at = datetime.combine(
                week_start + timedelta(days=7), time.min, tzinfo=SHANGHAI
            ).astimezone(UTC)
            completed_week = (
                db.scalar(
                    select(func.count(ActivityRecord.id)).where(
                        ActivityRecord.family_id == family_id,
                        ActivityRecord.child_id == child_id,
                        ActivityRecord.subject_id == subject.id,
                        ActivityRecord.occurred_at >= week_start_at,
                        ActivityRecord.occurred_at < week_end_at,
                    )
                )
                or 0
            )
            scheduled_today = today_slot is not None
            frequency_due = (
                completed_week < schedule.target_per_week
                if schedule.target_per_week is not None
                else not slot_values and (days_since is None or days_since >= 7)
            )
            result.append(
                {
                    "schedule_id": schedule.id,
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "scheduled_today": scheduled_today,
                    "suggested": scheduled_today or frequency_due,
                    "optional": True,
                    "time_text": schedule.time_text,
                    "start_time": today_slot.start_time.strftime("%H:%M") if today_slot else None,
                    "end_time": today_slot.end_time.strftime("%H:%M") if today_slot else None,
                    "last_practice_days_ago": days_since,
                    "completed_this_week": completed_week,
                    "target_per_week": schedule.target_per_week,
                    "message": (
                        "今天有固定安排" if scheduled_today else "距上次练习较久，今天可酌情安排"
                    ),
                }
            )
        return result
