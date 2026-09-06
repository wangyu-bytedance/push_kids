from __future__ import annotations

import json
from datetime import UTC, date, datetime, time, timedelta
from hashlib import sha256

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.activities.schemas import (
    ActivityRecordCreate,
    ActivityScheduleCreate,
    ActivityScheduleUpdate,
    CalendarEventPatch,
    CalendarEventWrite,
)
from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    ActivityRecord,
    ActivitySchedule,
    CalendarEvent,
    CalendarEventRequest,
    Subject,
)
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import SHANGHAI, local_date, utcnow


class ActivitiesService:
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
        cls, db: Session, family_id: str, data: ActivityScheduleCreate
    ) -> ActivitySchedule:
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
            existing.weekdays = ",".join(str(item) for item in data.weekdays)
            existing.time_text = data.time_text
            existing.start_time = data.start_time
            existing.end_time = data.end_time
            existing.target_per_week = data.target_per_week
            existing.note = data.note
            db.commit()
            return existing
        schedule = ActivitySchedule(
            family_id=family_id,
            child_id=data.child_id,
            subject_id=data.subject_id,
            weekdays=",".join(str(item) for item in data.weekdays),
            time_text=data.time_text,
            start_time=data.start_time,
            end_time=data.end_time,
            target_per_week=data.target_per_week,
            note=data.note,
        )
        db.add(schedule)
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
    ) -> ActivitySchedule:
        schedule = db.scalar(
            select(ActivitySchedule).where(
                ActivitySchedule.id == schedule_id, ActivitySchedule.family_id == family_id
            )
        )
        if schedule is None:
            raise NotFoundError("没有找到这个活动提醒")
        values = data.model_dump(exclude_unset=True, exclude={"child_id", "subject_id"})
        if "weekdays" in values:
            values["weekdays"] = ",".join(str(item) for item in (values["weekdays"] or []))
        for key, value in values.items():
            setattr(schedule, key, value)
        has_weekdays = bool(schedule.weekdays)
        if has_weekdays and (schedule.start_time is None or schedule.end_time is None):
            raise ValueError("固定提醒必须包含开始和结束时间")
        if not has_weekdays and (schedule.start_time is not None or schedule.end_time is not None):
            raise ValueError("时间不固定时不能设置开始或结束时间")
        if schedule.start_time and schedule.end_time and schedule.end_time <= schedule.start_time:
            raise ValueError("结束时间必须晚于开始时间")
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
        event.active = False
        db.commit()

    @classmethod
    def events_for_day(cls, db: Session, family_id: str, child_id: str, target: date) -> list[dict]:
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
            select(ActivitySchedule, Subject)
            .join(Subject, ActivitySchedule.subject_id == Subject.id)
            .where(
                ActivitySchedule.family_id == family_id,
                ActivitySchedule.child_id == child_id,
                ActivitySchedule.active.is_(True),
                Subject.active.is_(True),
            )
        ).all()
        for schedule, subject in schedule_rows:
            weekdays = [int(item) for item in schedule.weekdays.split(",") if item]
            if target.weekday() not in weekdays or not schedule.start_time or not schedule.end_time:
                continue
            result.append(
                cls._event_view(
                    schedule.id,
                    subject.name,
                    target,
                    schedule.start_time,
                    schedule.end_time,
                    "activity",
                    True,
                    "activity_schedule",
                    subject.id,
                )
            )
        return sorted(result, key=lambda item: item["start_time"])

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
        ChildrenService.get_child(db, family_id, child_id)
        return list(
            db.scalars(
                select(ActivityRecord)
                .where(ActivityRecord.family_id == family_id, ActivityRecord.child_id == child_id)
                .order_by(ActivityRecord.occurred_at.desc())
                .limit(100)
            )
        )

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
            weekdays = [int(item) for item in schedule.weekdays.split(",") if item]
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
            scheduled_today = target.weekday() in weekdays
            frequency_due = (
                completed_week < schedule.target_per_week
                if schedule.target_per_week is not None
                else not weekdays and (days_since is None or days_since >= 7)
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
                    "start_time": (
                        schedule.start_time.strftime("%H:%M") if schedule.start_time else None
                    ),
                    "end_time": schedule.end_time.strftime("%H:%M") if schedule.end_time else None,
                    "last_practice_days_ago": days_since,
                    "completed_this_week": completed_week,
                    "target_per_week": schedule.target_per_week,
                    "message": (
                        "今天有固定安排" if scheduled_today else "距上次练习较久，今天可酌情安排"
                    ),
                }
            )
        return result
