from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from push_kids.activities.service import ActivitiesService
from push_kids.children.service import ChildrenService
from push_kids.learning.history import LearningHistory
from push_kids.persistence.models import (
    ActivityRecord,
    Child,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
    SubmissionState,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.time import SHANGHAI, local_date
from push_kids.reporting.trends import TREND_METRIC_KEYS, build_overview_trends


def _utc_boundary(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=SHANGHAI).astimezone(UTC)


def _local_day_expression(db: Session, column):
    """Return a database-side Shanghai calendar day for the supported runtimes."""
    if db.get_bind().dialect.name == "mysql":
        return func.date(func.convert_tz(column, "+00:00", "+08:00"))
    return func.date(column, "+8 hours")


def _coerce_day(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _daily_counts(rows, start_day: date, days: int) -> list[int]:
    counts = [0] * days
    for raw_day, count in rows:
        parsed_day = _coerce_day(raw_day)
        offset = (parsed_day - start_day).days
        if 0 <= offset < days:
            counts[offset] = int(count or 0)
    return counts


class ReportingService:
    @staticmethod
    def history_page(db: Session, family_id: str, child_id: str, **filters) -> dict:
        return LearningHistory.page(db, family_id, child_id, **filters)

    @staticmethod
    def history_detail(db: Session, family_id: str, child_id: str, submission_id: str) -> dict:
        return LearningHistory.detail(db, family_id, child_id, submission_id)

    @staticmethod
    def history_reviews(
        db: Session,
        family_id: str,
        child_id: str,
        submission_id: str,
        review_id: str | None = None,
        before: str | None = None,
    ) -> dict:
        detail = LearningHistory.detail(db, family_id, child_id, submission_id)
        return PlanningService.history_for_knowledge(
            db,
            family_id,
            child_id,
            [item["id"] for item in detail["knowledge"]],
            review_id,
            before,
        )

    @classmethod
    def dashboard(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        day: date | None = None,
        *,
        todo_cursor: str | None = None,
        todo_limit: int = 20,
    ) -> dict:
        child = ChildrenService.get_child(db, family_id, child_id)
        target = day or local_date()
        todo_page = PlanningService.daily_todo_page(
            db,
            family_id,
            child_id,
            target,
            cursor=todo_cursor,
            limit=todo_limit,
            known_child=child,
        )
        pending = (
            db.scalar(
                select(func.count(LearningSubmission.id)).where(
                    LearningSubmission.family_id == family_id,
                    LearningSubmission.child_id == child_id,
                    LearningSubmission.state == SubmissionState.pending_confirmation.value,
                )
            )
            or 0
        )
        analyzing = (
            db.scalar(
                select(func.count(LearningSubmission.id)).where(
                    LearningSubmission.family_id == family_id,
                    LearningSubmission.child_id == child_id,
                    LearningSubmission.state.in_(
                        [SubmissionState.queued.value, SubmissionState.analyzing.value]
                    ),
                )
            )
            or 0
        )
        failed = (
            db.scalar(
                select(func.count(LearningSubmission.id)).where(
                    LearningSubmission.family_id == family_id,
                    LearningSubmission.child_id == child_id,
                    LearningSubmission.state == SubmissionState.failed.value,
                )
            )
            or 0
        )
        summary = cls.daily_summary(db, family_id, child_id, target, limit=20, known_child=child)
        schedule = ActivitiesService.events_for_day(db, family_id, child_id, target)
        return {
            "day": target.isoformat(),
            "child": {
                "id": child.id,
                "name": child.name,
                "grade": child.grade,
                "daily_budget_minutes": child.daily_budget_minutes,
            },
            "todo_groups": todo_page["groups"],
            "todo_count": todo_page["total_count"],
            "required_todo_count": todo_page["required_count"],
            "estimated_minutes": todo_page["estimated_minutes"],
            "todo_returned_count": todo_page["returned_count"],
            "todo_remaining_count": todo_page["remaining_count"],
            "todo_next_cursor": todo_page["next_cursor"],
            "pending_confirmation_count": pending,
            "analyzing_count": analyzing,
            "failed_count": failed,
            "daily_summary": summary,
            "activity_suggestions": ActivitiesService.suggestions(db, family_id, child_id, target),
            "schedule_items": schedule,
        }

    @staticmethod
    def daily_summary(
        db: Session,
        family_id: str,
        child_id: str,
        day: date,
        *,
        limit: int = 20,
        known_child: Child | None = None,
    ) -> dict:
        start = _utc_boundary(day)
        end = _utc_boundary(day + timedelta(days=1))
        child = known_child or ChildrenService.get_child(db, family_id, child_id)
        if child.family_id != family_id or child.id != child_id:
            raise ValueError("孩子范围无效")
        total = (
            db.scalar(
                select(func.count(LearningRecord.id)).where(
                    LearningRecord.family_id == family_id,
                    LearningRecord.child_id == child_id,
                    LearningRecord.occurred_at >= start,
                    LearningRecord.occurred_at < end,
                )
            )
            or 0
        )
        rows = db.execute(
            select(LearningRecord, Subject)
            .join(Subject, LearningRecord.subject_id == Subject.id)
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.occurred_at >= start,
                LearningRecord.occurred_at < end,
            )
            .order_by(LearningRecord.occurred_at.desc(), LearningRecord.id.desc())
            .limit(limit)
        ).all()
        subjects: dict[str, dict] = {}
        for record, subject in rows:
            group = subjects.setdefault(
                subject.id,
                {
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "summaries": [],
                    "record_count": 0,
                },
            )
            group["summaries"].append(record.summary)
            group["record_count"] += 1
        return {
            "day": day.isoformat(),
            "subjects": list(subjects.values()),
            "record_count": int(total),
            "returned_record_count": len(rows),
            "remaining_record_count": max(0, int(total) - len(rows)),
        }

    @staticmethod
    def history(db: Session, family_id: str, child_id: str, limit: int = 100) -> list[dict]:
        ChildrenService.get_child(db, family_id, child_id)
        rows = db.execute(
            select(LearningRecord, Subject)
            .join(Subject, LearningRecord.subject_id == Subject.id)
            .where(LearningRecord.family_id == family_id, LearningRecord.child_id == child_id)
            .order_by(LearningRecord.occurred_at.desc())
            .limit(limit)
        ).all()
        return [
            {
                "id": record.id,
                "occurred_at": record.occurred_at.isoformat(),
                "created_at": record.created_at.isoformat(),
                "summary": record.summary,
                "source": record.source,
                "subject_id": subject.id,
                "subject_name": subject.name,
                "subject_color": subject.color,
            }
            for record, subject in rows
        ]

    @classmethod
    def calendar(cls, db: Session, family_id: str, child_id: str, month: str) -> dict:
        ChildrenService.get_child(db, family_id, child_id)
        year, month_number = (int(item) for item in month.split("-"))
        start_day = date(year, month_number, 1)
        end_day = date(
            year + (month_number == 12), 1 if month_number == 12 else month_number + 1, 1
        )
        range_days = (end_day - start_day).days
        learning_day = _local_day_expression(db, LearningRecord.occurred_at)
        learning_rows = db.execute(
            select(learning_day, func.count(LearningRecord.id))
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.occurred_at >= _utc_boundary(start_day),
                LearningRecord.occurred_at < _utc_boundary(end_day),
            )
            .group_by(learning_day)
        ).all()
        activity_day = _local_day_expression(db, ActivityRecord.occurred_at)
        activity_rows = db.execute(
            select(activity_day, func.count(ActivityRecord.id))
            .where(
                ActivityRecord.family_id == family_id,
                ActivityRecord.child_id == child_id,
                ActivityRecord.occurred_at >= _utc_boundary(start_day),
                ActivityRecord.occurred_at < _utc_boundary(end_day),
            )
            .group_by(activity_day)
        ).all()
        learning_counts = _daily_counts(learning_rows, start_day, range_days)
        activity_counts = _daily_counts(activity_rows, start_day, range_days)
        return {
            "month": month,
            "days": [
                {
                    "day": (start_day + timedelta(days=offset)).isoformat(),
                    "learning": learning_counts[offset],
                    "activity": activity_counts[offset],
                }
                for offset in range(range_days)
                if learning_counts[offset] or activity_counts[offset]
            ],
        }

    @staticmethod
    def report(db: Session, family_id: str, child_id: str, days: int = 7) -> dict:
        child = ChildrenService.get_child(db, family_id, child_id)
        today = local_date()
        date_start = today - timedelta(days=days - 1)
        start = _utc_boundary(date_start)
        end = _utc_boundary(today + timedelta(days=1))

        record_day = _local_day_expression(db, LearningRecord.occurred_at)
        record_rows = db.execute(
            select(record_day, func.count(LearningRecord.id))
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.occurred_at >= start,
                LearningRecord.occurred_at < end,
            )
            .group_by(record_day)
        ).all()
        knowledge_day = _local_day_expression(db, KnowledgeItem.created_at)
        knowledge_rows = db.execute(
            select(knowledge_day, func.count(KnowledgeItem.id))
            .where(
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                KnowledgeItem.created_at >= start,
                KnowledgeItem.created_at < end,
            )
            .group_by(knowledge_day)
        ).all()
        feedback_day = _local_day_expression(db, ReviewFeedback.occurred_at)
        feedback_rows = db.execute(
            select(feedback_day, func.count(ReviewFeedback.id))
            .join(ReviewItem, ReviewFeedback.review_item_id == ReviewItem.id)
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .where(
                ReviewFeedback.family_id == family_id,
                ReviewItem.child_id == child_id,
                ReviewFeedback.occurred_at >= start,
                ReviewFeedback.occurred_at < end,
                Subject.kind == "learning",
            )
            .group_by(feedback_day)
        ).all()
        activity_day = _local_day_expression(db, ActivityRecord.occurred_at)
        activity_rows = db.execute(
            select(activity_day, func.count(ActivityRecord.id))
            .where(
                ActivityRecord.family_id == family_id,
                ActivityRecord.child_id == child_id,
                ActivityRecord.occurred_at >= start,
                ActivityRecord.occurred_at < end,
            )
            .group_by(activity_day)
        ).all()
        daily_counts = {
            "learning_records": _daily_counts(record_rows, date_start, days),
            "new_knowledge_items": _daily_counts(knowledge_rows, date_start, days),
            "review_feedback_count": _daily_counts(feedback_rows, date_start, days),
            "activity_records": _daily_counts(activity_rows, date_start, days),
        }
        overview = {key: sum(daily_counts[key]) for key in TREND_METRIC_KEYS}

        occurrence_count = func.count(KnowledgeOccurrence.id)
        subject_rows = db.execute(
            select(
                Subject.id,
                Subject.name,
                occurrence_count.label("occurrences"),
                func.count().over().label("total_subjects"),
                func.sum(occurrence_count).over().label("total_occurrences"),
            )
            .join(KnowledgeItem, KnowledgeItem.subject_id == Subject.id)
            .join(KnowledgeOccurrence, KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id)
            .where(
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                KnowledgeOccurrence.occurred_at >= start,
                KnowledgeOccurrence.occurred_at < end,
            )
            .group_by(Subject.id, Subject.name)
            .order_by(occurrence_count.desc(), Subject.name, Subject.id)
            .limit(50)
        ).all()
        subject_total = int(subject_rows[0].total_subjects) if subject_rows else 0
        total_occurrences = int(subject_rows[0].total_occurrences) if subject_rows else 0
        returned_occurrences = sum(int(row.occurrences) for row in subject_rows)

        activity_count = func.count(ActivityRecord.id)
        activity_subject_rows = db.execute(
            select(
                Subject.id,
                Subject.name,
                activity_count.label("records"),
                func.coalesce(func.sum(ActivityRecord.duration_minutes), 0).label("minutes"),
                func.max(ActivityRecord.occurred_at).label("last_occurred_at"),
                func.count().over().label("total_subjects"),
                func.sum(activity_count).over().label("total_records"),
            )
            .join(ActivityRecord, ActivityRecord.subject_id == Subject.id)
            .where(
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.kind == "activity",
                ActivityRecord.family_id == family_id,
                ActivityRecord.child_id == child_id,
                ActivityRecord.occurred_at >= start,
                ActivityRecord.occurred_at < end,
            )
            .group_by(Subject.id, Subject.name)
            .order_by(activity_count.desc(), Subject.name, Subject.id)
            .limit(50)
        ).all()
        activity_subject_total = (
            int(activity_subject_rows[0].total_subjects) if activity_subject_rows else 0
        )
        activity_record_total = (
            int(activity_subject_rows[0].total_records) if activity_subject_rows else 0
        )
        returned_activity_records = sum(int(row.records) for row in activity_subject_rows)

        occurrence_day = _local_day_expression(db, KnowledgeOccurrence.occurred_at)
        active = ReviewItem.active.is_(True)
        urgency_level = case(
            (
                and_(
                    active,
                    or_(
                        ReviewItem.last_feedback == "reinforce",
                        ReviewItem.due_date <= today - timedelta(days=4),
                    ),
                ),
                3,
            ),
            (and_(active, ReviewItem.due_date <= today - timedelta(days=2)), 2),
            (active, 1),
            else_=0,
        )
        urgency_rows = db.execute(
            select(
                occurrence_day,
                func.sum(case((active, 1), else_=0)).label("pending_count"),
                func.max(urgency_level).label("level"),
                func.count(KnowledgeOccurrence.id).label("item_count"),
            )
            .select_from(KnowledgeOccurrence)
            .join(ReviewItem, ReviewItem.knowledge_item_id == KnowledgeOccurrence.knowledge_item_id)
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .where(
                KnowledgeOccurrence.family_id == family_id,
                KnowledgeOccurrence.occurred_at >= start,
                KnowledgeOccurrence.occurred_at < end,
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                Subject.kind == "learning",
            )
            .group_by(occurrence_day)
        ).all()
        urgency_by_day = {
            _coerce_day(raw_day): (
                int(pending_count or 0),
                int(level or 0),
                int(item_count or 0),
            )
            for raw_day, pending_count, level, item_count in urgency_rows
        }

        urgency = []
        review_activity = []
        feedback_counts = daily_counts["review_feedback_count"]
        for offset in range(days):
            key = (date_start + timedelta(days=offset)).isoformat()
            pending_count, level, item_count = urgency_by_day.get(
                date_start + timedelta(days=offset), (0, 0, 0)
            )
            has_items = bool(item_count)
            urgency.append(
                {
                    "day": key,
                    "pending_count": pending_count,
                    "level": level,
                    "passed": has_items and pending_count == 0,
                    "has_items": has_items,
                }
            )
            count = feedback_counts[offset]
            review_activity.append(
                {
                    "day": key,
                    "count": count,
                    "level": sum(count > threshold for threshold in (0, 2, 5, 8)) if count else 0,
                }
            )

        return {
            "child": {"id": child.id, "name": child.name},
            "range_days": days,
            "overview": overview,
            "overview_trends": build_overview_trends(date_start, days, daily_counts),
            "subjects": [
                {"id": row.id, "name": row.name, "occurrences": int(row.occurrences)}
                for row in subject_rows
            ],
            "subjects_meta": {
                "total": subject_total,
                "returned": len(subject_rows),
                "omitted_occurrences": max(0, total_occurrences - returned_occurrences),
            },
            "activity_subjects": [
                {
                    "subject_id": row.id,
                    "subject_name": row.name,
                    "records": int(row.records),
                    "minutes": int(row.minutes or 0),
                    "last_occurred_on": local_date(row.last_occurred_at).isoformat(),
                }
                for row in activity_subject_rows
            ],
            "activity_subjects_meta": {
                "total": activity_subject_total,
                "returned": len(activity_subject_rows),
                "omitted_records": max(0, activity_record_total - returned_activity_records),
            },
            "review_urgency": urgency,
            "review_activity": review_activity,
        }
