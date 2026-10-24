"""Child-owned, bounded proposals and atomic shared confirmation facts."""

from typing import cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from push_kids.children.grade_policy import canonical_grade, propose_grade, school_year
from push_kids.children.schemas import (
    ChildView,
    GradeConfirmation,
    GradeConfirmationResult,
    GradeConfirmations,
    PendingGradeConfirmation,
)
from push_kids.persistence.models import Child
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import local_date

MAX_GRADE_CANDIDATES = 5


class GradeConfirmationConflict(ConflictError):
    code = "grade_confirmation_conflict"


class GradeSchoolYearChanged(ConflictError):
    code = "grade_school_year_changed"


class GradeConfirmationService:
    @staticmethod
    def initialize(child: Child) -> None:
        value = canonical_grade(child.grade)
        child.grade_confirmed_school_year = school_year(local_date()) if value else None
        child.grade_revision = 1 if value else 0
        if value:
            child.grade = value

    @staticmethod
    def pending(db: Session, family_id: str, *, can_confirm: bool) -> GradeConfirmations:
        year = school_year(local_date())
        if not can_confirm:
            return GradeConfirmations(school_year=year, can_confirm=False, items=[])
        children = list(
            db.scalars(
                select(Child)
                .where(
                    Child.family_id == family_id, Child.active.is_(True), Child.deleting.is_(False)
                )
                .order_by(Child.created_at, Child.id)
                .limit(MAX_GRADE_CANDIDATES + 1)
            )
        )
        if len(children) > MAX_GRADE_CANDIDATES:
            raise ConflictError("在用档案数量异常，请先核对学习档案")
        items = []
        for child in children:
            try:
                proposal = propose_grade(child.grade, child.grade_confirmed_school_year, year)
            except ValueError as error:
                raise GradeConfirmationConflict("年级确认状态异常，请核对档案年级") from error
            if proposal:
                items.append(
                    PendingGradeConfirmation(
                        id=child.id,
                        name=child.name,
                        current_grade=child.grade,
                        suggested_grade=proposal.grade,
                        reason=proposal.reason,
                        revision=child.grade_revision,
                    )
                )
        return GradeConfirmations(school_year=year, can_confirm=True, items=items)

    @staticmethod
    def _write(
        db: Session, child: Child, grade: str | None, year: int | None, expected_revision: int
    ) -> None:
        result = db.execute(
            update(Child)
            .where(
                Child.family_id == child.family_id,
                Child.id == child.id,
                Child.active.is_(True),
                Child.deleting.is_(False),
                Child.grade_revision == expected_revision,
            )
            .values(
                grade=grade,
                grade_confirmed_school_year=year,
                grade_revision=Child.grade_revision + 1,
            )
            .execution_options(synchronize_session=False)
        )
        if cast(CursorResult, result).rowcount != 1:
            raise GradeConfirmationConflict("年级已更新，请刷新后核对最新结果")
        db.refresh(child)

    @classmethod
    def save_manual_grade(
        cls, db: Session, child: Child, grade: str | None, expected_revision: int
    ) -> None:
        value = canonical_grade(grade)
        cls._write(
            db,
            child,
            value or grade,
            school_year(local_date()) if value else None,
            expected_revision,
        )

    @classmethod
    def confirm(
        cls, db: Session, family_id: str, child_id: str, data: GradeConfirmation
    ) -> GradeConfirmationResult:
        year = school_year(local_date())
        child = db.scalar(
            select(Child)
            .where(Child.family_id == family_id, Child.id == child_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if child is None:
            raise NotFoundError("没有找到这个孩子")
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理，暂时不能修改")
        if not child.active:
            raise ConflictError("这个学习档案已归档，恢复后才能核对年级")
        if data.school_year != year:
            raise GradeSchoolYearChanged("学年已变化，请重新核对年级")
        value = canonical_grade(data.grade)
        if child.grade_confirmed_school_year == year:
            if value != canonical_grade(child.grade):
                raise GradeConfirmationConflict("年级已由家长确认，请查看最新结果")
            outcome = "already_confirmed"
        else:
            try:
                proposal = propose_grade(child.grade, child.grade_confirmed_school_year, year)
            except ValueError as error:
                raise GradeConfirmationConflict("年级确认状态异常，请核对档案年级") from error
            if proposal is None or data.expected_grade_revision != child.grade_revision:
                raise GradeConfirmationConflict("年级已更新，请查看最新结果")
            cls._write(db, child, value, year, data.expected_grade_revision)
            outcome = "confirmed"
        db.commit()
        return GradeConfirmationResult(child=ChildView.model_validate(child), outcome=outcome)
