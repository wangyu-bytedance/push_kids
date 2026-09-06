from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from push_kids.children.schemas import ChildCreate, ChildUpdate, SubjectCreate, SubjectUpdate
from push_kids.persistence.models import Child, FamilyAuditEvent, Subject
from push_kids.platform.errors import ConflictError, NotFoundError

# The system preset learning catalog owned by this module; everything else is parent-built.
PRESET_LEARNING_SUBJECTS = ("语文", "数学", "英语")

# A family may keep at most this many profiles in use at once. Archived profiles do not count,
# so a parent can retire an old profile and add a new one without hitting the ceiling.
MAX_ACTIVE_CHILDREN = 5


def is_custom_subject(name: str, kind: str) -> bool:
    """A subject is custom unless it is one of the system preset learning subjects."""
    return not (kind == "learning" and name.strip() in PRESET_LEARNING_SUBJECTS)


class ChildrenService:
    @staticmethod
    def purge_data(db: Session, family_id: str, child_id: str | None) -> None:
        subject_scope = [Subject.family_id == family_id]
        child_scope = [Child.family_id == family_id]
        if child_id is not None:
            subject_scope.append(Subject.child_id == child_id)
            child_scope.append(Child.id == child_id)
        db.execute(delete(Subject).where(*subject_scope))
        db.execute(delete(Child).where(*child_scope))

    @staticmethod
    def list_children(db: Session, family_id: str, include_archived: bool = False) -> list[Child]:
        """Profiles in creation order. Archived profiles stay hidden unless asked for."""
        statement = select(Child).where(
            Child.family_id == family_id,
            Child.deleting.is_(False),
        )
        if not include_archived:
            statement = statement.where(Child.active.is_(True))
        return list(db.scalars(statement.order_by(Child.created_at)))

    @staticmethod
    def get_child(db: Session, family_id: str, child_id: str) -> Child:
        """Resolve a profile for reading. Archived profiles resolve so history stays readable."""
        child = db.scalar(select(Child).where(Child.id == child_id, Child.family_id == family_id))
        if child is None:
            raise NotFoundError("没有找到这个孩子")
        return child

    @classmethod
    def require_active_child(cls, db: Session, family_id: str, child_id: str | None) -> Child:
        """Resolve a profile that may receive a new record. Archiving must stop new writes."""
        if not child_id:
            raise NotFoundError("没有找到这个孩子")
        child = cls.get_child(db, family_id, child_id)
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理，暂时不能修改")
        if not child.active:
            raise ConflictError("这个学习档案已归档，恢复后才能继续记录")
        return child

    @staticmethod
    def _count_active(db: Session, family_id: str) -> int:
        total = db.scalar(
            select(func.count())
            .select_from(Child)
            .where(Child.family_id == family_id, Child.active.is_(True))
        )
        return int(total or 0)

    @classmethod
    def _require_capacity(cls, db: Session, family_id: str) -> None:
        if cls._count_active(db, family_id) >= MAX_ACTIVE_CHILDREN:
            raise ConflictError(
                f"一个家庭最多同时保留 {MAX_ACTIVE_CHILDREN} 个学习档案，可以先归档不再使用的档案"
            )

    @classmethod
    def _require_free_name(
        cls, db: Session, family_id: str, name: str, exclude_child_id: str | None = None
    ) -> str:
        """Names identify a profile in the switcher, so two profiles in use may not share one."""
        cleaned = name.strip()
        if not cleaned:
            raise ConflictError("请填写孩子的名字")
        statement = select(Child).where(
            Child.family_id == family_id,
            Child.active.is_(True),
            Child.name == cleaned,
        )
        if exclude_child_id is not None:
            statement = statement.where(Child.id != exclude_child_id)
        if db.scalar(statement) is not None:
            raise ConflictError("这个名字已经在用了，换一个更好区分的名字")
        return cleaned

    @classmethod
    def create_child(cls, db: Session, family_id: str, data: ChildCreate) -> Child:
        child = cls.create_child_in_transaction(db, family_id, data)
        db.commit()
        return child

    @classmethod
    def create_child_in_transaction(cls, db: Session, family_id: str, data: ChildCreate) -> Child:
        cls._require_capacity(db, family_id)
        payload = data.model_dump(exclude={"subject_names"})
        payload["name"] = cls._require_free_name(db, family_id, data.name)
        child = Child(family_id=family_id, **payload)
        db.add(child)
        db.flush()
        if child.id is None:
            raise RuntimeError("child id was not generated")
        cls._seed_subjects(db, family_id, child.id, data.subject_names)
        return child

    @classmethod
    def _seed_subjects(
        cls, db: Session, family_id: str, child_id: str, names: list[str] | None
    ) -> None:
        """Give a fresh profile the subjects the parent picked, so it is not an empty shell."""
        seen: set[str] = set()
        for raw in names or []:
            name = raw.strip()
            if not name or name in seen:
                continue
            seen.add(name)
            db.add(
                Subject(
                    family_id=family_id,
                    child_id=child_id,
                    name=name,
                    kind="learning",
                    is_custom=is_custom_subject(name, "learning"),
                )
            )
        if seen:
            db.flush()

    @classmethod
    def update_child(cls, db: Session, family_id: str, child_id: str, data: ChildUpdate) -> Child:
        child = cls.require_active_child(db, family_id, child_id)
        values = data.model_dump(exclude_unset=True)
        if "name" in values and values["name"] is not None:
            values["name"] = cls._require_free_name(
                db, family_id, values["name"], exclude_child_id=child_id
            )
        for key, value in values.items():
            setattr(child, key, value)
        db.commit()
        return child

    @staticmethod
    def _audit(
        db: Session,
        family_id: str,
        actor_binding_id: str | None,
        action: str,
        child_id: str,
    ) -> None:
        """Record who changed what the whole family can see.

        The local `X-Family-ID` path has no actor binding, and the audit row requires one, so an
        unattributable local change is skipped instead of being logged against a fabricated actor.
        """
        if actor_binding_id is None:
            return
        db.add(
            FamilyAuditEvent(
                family_id=family_id,
                actor_binding_id=actor_binding_id,
                action=action,
                resource_type="child",
                resource_id=child_id,
            )
        )

    @classmethod
    def archive_child(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        actor_binding_id: str | None = None,
    ) -> Child:
        """Archiving is reversible and never deletes a record; repeating it is a no-op."""
        child = cls.get_child(db, family_id, child_id)
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理")
        if child.active:
            child.active = False
            cls._audit(db, family_id, actor_binding_id, "child.archived", child_id)
            db.commit()
        return child

    @classmethod
    def restore_child(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        actor_binding_id: str | None = None,
    ) -> Child:
        child = cls.get_child(db, family_id, child_id)
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理")
        if child.active:
            return child
        cls._require_capacity(db, family_id)
        cls._require_free_name(db, family_id, str(child.name), exclude_child_id=child_id)
        child.active = True
        cls._audit(db, family_id, actor_binding_id, "child.restored", child_id)
        db.commit()
        return child

    @classmethod
    def create_subject(cls, db: Session, family_id: str, data: SubjectCreate) -> Subject:
        cls.require_active_child(db, family_id, data.child_id)
        exists = db.scalar(
            select(Subject).where(
                Subject.family_id == family_id,
                Subject.child_id == data.child_id,
                Subject.name == data.name.strip(),
            )
        )
        if exists:
            raise ConflictError("这个科目已经存在")
        subject = Subject(
            family_id=family_id,
            **data.model_dump(),
            is_custom=is_custom_subject(data.name, data.kind),
        )
        db.add(subject)
        db.commit()
        return subject

    @classmethod
    def list_subjects(cls, db: Session, family_id: str, child_id: str) -> list[Subject]:
        cls.get_child(db, family_id, child_id)
        return list(
            db.scalars(
                select(Subject)
                .where(Subject.family_id == family_id, Subject.child_id == child_id)
                .order_by(Subject.kind, Subject.created_at)
            )
        )

    @classmethod
    def update_subject(
        cls, db: Session, family_id: str, subject_id: str, data: SubjectUpdate
    ) -> Subject:
        subject = db.scalar(
            select(Subject).where(Subject.id == subject_id, Subject.family_id == family_id)
        )
        if subject is None:
            raise NotFoundError("没有找到这个科目")
        cls.require_active_child(db, family_id, subject.child_id)
        subject.active = data.active
        db.commit()
        return subject
