from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.children.schemas import ChildCreate, ChildUpdate, SubjectCreate, SubjectUpdate
from push_kids.persistence.models import Child, Subject
from push_kids.platform.errors import ConflictError, NotFoundError


class ChildrenService:
    @staticmethod
    def list_children(db: Session, family_id: str) -> list[Child]:
        return list(
            db.scalars(select(Child).where(Child.family_id == family_id).order_by(Child.created_at))
        )

    @staticmethod
    def get_child(db: Session, family_id: str, child_id: str) -> Child:
        child = db.scalar(select(Child).where(Child.id == child_id, Child.family_id == family_id))
        if child is None:
            raise NotFoundError("没有找到这个孩子")
        return child

    @classmethod
    def create_child(cls, db: Session, family_id: str, data: ChildCreate) -> Child:
        child = Child(family_id=family_id, **data.model_dump())
        db.add(child)
        db.commit()
        return child

    @classmethod
    def update_child(cls, db: Session, family_id: str, child_id: str, data: ChildUpdate) -> Child:
        child = cls.get_child(db, family_id, child_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(child, key, value)
        db.commit()
        return child

    @classmethod
    def create_subject(cls, db: Session, family_id: str, data: SubjectCreate) -> Subject:
        cls.get_child(db, family_id, data.child_id)
        exists = db.scalar(
            select(Subject).where(
                Subject.family_id == family_id,
                Subject.child_id == data.child_id,
                Subject.name == data.name.strip(),
            )
        )
        if exists:
            raise ConflictError("这个科目已经存在")
        subject = Subject(family_id=family_id, **data.model_dump())
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

    @staticmethod
    def update_subject(
        db: Session, family_id: str, subject_id: str, data: SubjectUpdate
    ) -> Subject:
        subject = db.scalar(
            select(Subject).where(Subject.id == subject_id, Subject.family_id == family_id)
        )
        if subject is None:
            raise NotFoundError("没有找到这个科目")
        subject.active = data.active
        db.commit()
        return subject
