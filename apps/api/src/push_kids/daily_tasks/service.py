from datetime import date

from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.daily_tasks.schemas import DailyTaskCreate, DailyTaskPatch, DailyTaskView
from push_kids.persistence.models import Child, DailyTask, DailyTaskCompletion
from push_kids.platform.errors import ConflictError, ForbiddenError, NotFoundError
from push_kids.platform.time import local_date, utcnow

MAX_DAILY_TASKS = 20


class DailyTasksService:
    @staticmethod
    def _lock_child(db: Session, family_id: str, child_id: str) -> None:
        ChildrenService.get_child(db, family_id, child_id)
        # SQLite has no SELECT FOR UPDATE. Acquire its writer lock before the current read.
        if db.get_bind().dialect.name == "sqlite":
            db.execute(
                update(Child)
                .where(Child.id == child_id, Child.family_id == family_id)
                .values(id=child_id)
            )
        child = db.scalar(
            select(Child)
            .where(Child.id == child_id, Child.family_id == family_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if child is None:
            raise NotFoundError("没有找到这个孩子")
        if not child.active:
            raise ForbiddenError("已归档的孩子不能修改每日任务")
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理")

    @staticmethod
    def _active_query(family_id: str, child_id: str):
        return (
            select(DailyTask)
            .where(
                DailyTask.family_id == family_id,
                DailyTask.child_id == child_id,
                DailyTask.active.is_(True),
            )
            .order_by(DailyTask.created_at, DailyTask.id)
            .limit(MAX_DAILY_TASKS)
        )

    @classmethod
    def list_tasks(cls, db: Session, family_id: str, child_id: str) -> list[DailyTask]:
        ChildrenService.get_child(db, family_id, child_id)
        return list(db.scalars(cls._active_query(family_id, child_id)))

    @staticmethod
    def _task(db: Session, family_id: str, child_id: str, task_id: str) -> DailyTask:
        task = db.scalar(
            select(DailyTask)
            .where(
                DailyTask.id == task_id,
                DailyTask.family_id == family_id,
                DailyTask.child_id == child_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if task is None:
            raise NotFoundError("没有找到这个每日任务")
        return task

    @classmethod
    def _admit(
        cls, db: Session, family_id: str, child_id: str, name: str, task_id: str | None = None
    ) -> None:
        # Locking reads see the latest committed tasks on MySQL REPEATABLE READ.
        tasks = list(
            db.scalars(
                cls._active_query(family_id, child_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        )
        if any(task.name == name and task.id != task_id for task in tasks):
            raise ConflictError("这个每日任务已经存在")
        if task_id is None and len(tasks) >= MAX_DAILY_TASKS:
            raise ConflictError("每个孩子最多设置 20 个每日任务，请先删除不再需要的任务")

    @classmethod
    def create(cls, db: Session, family_id: str, child_id: str, body: DailyTaskCreate) -> DailyTask:
        cls._lock_child(db, family_id, child_id)
        cls._admit(db, family_id, child_id, body.name)
        task = DailyTask(family_id=family_id, child_id=child_id, **body.model_dump())
        db.add(task)
        db.commit()
        return task

    @classmethod
    def patch(
        cls, db: Session, family_id: str, child_id: str, task_id: str, body: DailyTaskPatch
    ) -> DailyTask:
        cls._lock_child(db, family_id, child_id)
        task = cls._task(db, family_id, child_id, task_id)
        if not task.active:
            raise NotFoundError("这个每日任务已删除")
        if body.name is not None:
            cls._admit(db, family_id, child_id, body.name, task_id)
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        db.commit()
        return task

    @classmethod
    def remove(cls, db: Session, family_id: str, child_id: str, task_id: str) -> None:
        cls._lock_child(db, family_id, child_id)
        task = cls._task(db, family_id, child_id, task_id)
        task.active = False
        db.commit()

    @classmethod
    def today(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        day: date | None = None,
        *,
        known_child: Child | None = None,
    ) -> dict:
        child = known_child or ChildrenService.get_child(db, family_id, child_id)
        if child.family_id != family_id or child.id != child_id:
            raise ValueError("孩子范围无效")
        target = day or local_date()
        rows = db.execute(
            cls._active_query(family_id, child_id)
            .add_columns(DailyTaskCompletion.occurred_at)
            .outerjoin(
                DailyTaskCompletion,
                and_(
                    DailyTaskCompletion.family_id == family_id,
                    DailyTaskCompletion.child_id == child_id,
                    DailyTaskCompletion.task_id == DailyTask.id,
                    DailyTaskCompletion.day == target,
                ),
            )
        ).all()
        items = [
            {
                **DailyTaskView.model_validate(task).model_dump(),
                "completed": occurred_at is not None,
                "occurred_at": occurred_at,
            }
            for task, occurred_at in rows
        ]
        items.sort(key=lambda item: item["completed"])
        return {
            "day": target,
            "items": items,
            "total_count": len(items),
            "remaining_count": sum(not item["completed"] for item in items),
        }

    @classmethod
    def complete(
        cls, db: Session, family_id: str, child_id: str, task_id: str, completed: bool
    ) -> dict:
        cls._lock_child(db, family_id, child_id)
        task = cls._task(db, family_id, child_id, task_id)
        if not task.active:
            raise NotFoundError("这个每日任务已删除")
        now = utcnow()
        day = local_date(now)
        scope = (
            DailyTaskCompletion.family_id == family_id,
            DailyTaskCompletion.child_id == child_id,
            DailyTaskCompletion.task_id == task_id,
            DailyTaskCompletion.day == day,
        )
        existing = db.scalar(select(DailyTaskCompletion).where(*scope).with_for_update())
        if completed and existing is None:
            db.add(
                DailyTaskCompletion(
                    family_id=family_id,
                    child_id=child_id,
                    task_id=task_id,
                    day=day,
                    occurred_at=now,
                    created_at=now,
                    name_snapshot=task.name,
                    minutes_snapshot=task.target_minutes,
                )
            )
        elif not completed and existing is not None:
            db.delete(existing)
        db.commit()
        # Midnight may have passed during the transaction: return the actual current day.
        return cls.today(db, family_id, child_id)

    @staticmethod
    def purge_data(db: Session, family_id: str, child_id: str | None) -> None:
        for model in (DailyTaskCompletion, DailyTask):
            statement = delete(model).where(model.family_id == family_id)
            if child_id is not None:
                statement = statement.where(model.child_id == child_id)
            db.execute(statement)
