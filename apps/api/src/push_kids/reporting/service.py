from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from push_kids.activities.service import ActivitiesService
from push_kids.children.service import ChildrenService
from push_kids.learning.history import LearningHistory
from push_kids.persistence.models import (
    ActivityRecord,
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
    def dashboard(cls, db: Session, family_id: str, child_id: str, day: date | None = None) -> dict:
        child = ChildrenService.get_child(db, family_id, child_id)
        target = day or local_date()
        todos = PlanningService.daily_todos(db, family_id, child_id, target)
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
        summary = cls.daily_summary(db, family_id, child_id, target)
        schedule = ActivitiesService.events_for_day(db, family_id, child_id, target)
        return {
            "day": target.isoformat(),
            "child": {
                "id": child.id,
                "name": child.name,
                "grade": child.grade,
                "daily_budget_minutes": child.daily_budget_minutes,
            },
            "todo_groups": todos,
            "todo_count": sum(len(group["items"]) for group in todos),
            "required_todo_count": sum(
                len(group["items"]) for group in todos if not group["optional"]
            ),
            "estimated_minutes": sum(
                group["estimated_minutes"] for group in todos if not group["optional"]
            ),
            "pending_confirmation_count": pending,
            "analyzing_count": analyzing,
            "failed_count": failed,
            "daily_summary": summary,
            "activity_suggestions": ActivitiesService.suggestions(db, family_id, child_id, target),
            "schedule_items": schedule,
        }

    @staticmethod
    def daily_summary(db: Session, family_id: str, child_id: str, day: date) -> dict:
        start = _utc_boundary(day)
        end = _utc_boundary(day + timedelta(days=1))
        rows = db.execute(
            select(LearningRecord, Subject)
            .join(Subject, LearningRecord.subject_id == Subject.id)
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.occurred_at >= start,
                LearningRecord.occurred_at < end,
            )
            .order_by(LearningRecord.occurred_at.desc())
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
            "record_count": len(rows),
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
        year, month_number = (int(item) for item in month.split("-"))
        start_day = date(year, month_number, 1)
        end_day = date(
            year + (month_number == 12), 1 if month_number == 12 else month_number + 1, 1
        )
        learning = db.scalars(
            select(LearningRecord).where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.occurred_at >= _utc_boundary(start_day),
                LearningRecord.occurred_at < _utc_boundary(end_day),
            )
        )
        activities = db.scalars(
            select(ActivityRecord).where(
                ActivityRecord.family_id == family_id,
                ActivityRecord.child_id == child_id,
                ActivityRecord.occurred_at >= _utc_boundary(start_day),
                ActivityRecord.occurred_at < _utc_boundary(end_day),
            )
        )
        days: dict[str, dict[str, int]] = defaultdict(lambda: {"learning": 0, "activity": 0})
        for learning_item in learning:
            days[local_date(learning_item.occurred_at).isoformat()]["learning"] += 1
        for activity_item in activities:
            days[local_date(activity_item.occurred_at).isoformat()]["activity"] += 1
        return {
            "month": month,
            "days": [{"day": key, **value} for key, value in sorted(days.items())],
        }

    @staticmethod
    def report(db: Session, family_id: str, child_id: str, days: int = 7) -> dict:
        child = ChildrenService.get_child(db, family_id, child_id)
        today = local_date()
        date_start = today - timedelta(days=days - 1)
        start = _utc_boundary(date_start)
        end = _utc_boundary(today + timedelta(days=1))
        record_times = list(
            db.scalars(
                select(LearningRecord.occurred_at).where(
                    LearningRecord.family_id == family_id,
                    LearningRecord.child_id == child_id,
                    LearningRecord.occurred_at >= start,
                    LearningRecord.occurred_at < end,
                )
            )
        )
        knowledge_times = list(
            db.scalars(
                select(KnowledgeItem.created_at).where(
                    KnowledgeItem.family_id == family_id,
                    KnowledgeItem.child_id == child_id,
                    KnowledgeItem.created_at >= start,
                    KnowledgeItem.created_at < end,
                )
            )
        )
        feedback_times = list(
            db.scalars(
                select(ReviewFeedback.occurred_at)
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
            )
        )
        subject_rows = db.execute(
            select(Subject.id, Subject.name, func.count(KnowledgeOccurrence.id))
            .join(KnowledgeItem, KnowledgeItem.subject_id == Subject.id)
            .join(KnowledgeOccurrence, KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id)
            .where(
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                KnowledgeOccurrence.occurred_at >= start,
                KnowledgeOccurrence.occurred_at < end,
            )
            .group_by(Subject.id)
            .order_by(func.count(KnowledgeOccurrence.id).desc())
        ).all()
        activity_times = list(
            db.scalars(
                select(ActivityRecord.occurred_at).where(
                    ActivityRecord.family_id == family_id,
                    ActivityRecord.child_id == child_id,
                    ActivityRecord.occurred_at >= start,
                    ActivityRecord.occurred_at < end,
                )
            )
        )
        occurrence_rows = db.execute(
            select(KnowledgeOccurrence.occurred_at, ReviewItem)
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
        ).all()
        urgency_by_day: dict[str, dict] = {}
        for occurred_at, review in occurrence_rows:
            key = local_date(occurred_at).isoformat()
            item = urgency_by_day.setdefault(
                key, {"pending_count": 0, "level": 0, "passed": True, "has_items": True}
            )
            if review.active:
                overdue = (today - review.due_date).days
                level = (
                    3
                    if review.last_feedback == "reinforce" or overdue >= 4
                    else 2
                    if overdue >= 2
                    else 1
                )
                item["pending_count"] += 1
                item["level"] = max(item["level"], level)
                item["passed"] = False
        feedback_by_day: dict[str, int] = defaultdict(int)
        for occurred_at in feedback_times:
            feedback_by_day[local_date(occurred_at).isoformat()] += 1
        urgency = []
        activity = []
        for offset in range(days):
            current = date_start + timedelta(days=offset)
            key = current.isoformat()
            empty_urgency = {
                "pending_count": 0,
                "level": 0,
                "passed": False,
                "has_items": False,
            }
            urgency.append({"day": key, **urgency_by_day.get(key, empty_urgency)})
            count = int(feedback_by_day.get(key, 0))
            thresholds = (0, 2, 5, 8)
            activity_level = sum(count > threshold for threshold in thresholds) if count else 0
            activity.append({"day": key, "count": count, "level": activity_level})
        event_days = {
            "learning_records": [local_date(item) for item in record_times],
            "new_knowledge_items": [local_date(item) for item in knowledge_times],
            "review_feedback_count": [local_date(item) for item in feedback_times],
            "activity_records": [local_date(item) for item in activity_times],
        }
        overview = {key: len(event_days[key]) for key in TREND_METRIC_KEYS}
        return {
            "child": {"id": child.id, "name": child.name},
            "range_days": days,
            "overview": overview,
            "overview_trends": build_overview_trends(date_start, days, event_days),
            "subjects": [
                {"id": sid, "name": name, "occurrences": count} for sid, name, count in subject_rows
            ],
            "review_urgency": urgency,
            "review_activity": activity,
        }
