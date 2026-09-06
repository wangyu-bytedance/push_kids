from __future__ import annotations

import json
from datetime import date
from hashlib import sha256

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.activities.capacity import ensure_timed_item_capacity
from push_kids.children.service import ChildrenService
from push_kids.persistence.models import TravelArrangement, TravelArrangementRequest
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.travel.schemas import TravelArrangementCreate, TravelArrangementPatch


class TravelService:
    @staticmethod
    def purge_data(db: Session, family_id: str, child_id: str | None) -> None:
        query = select(TravelArrangement.id).where(TravelArrangement.family_id == family_id)
        if child_id is not None:
            query = query.where(TravelArrangement.child_id == child_id)
        arrangement_ids = list(db.scalars(query))
        db.execute(
            delete(TravelArrangementRequest).where(
                TravelArrangementRequest.family_id == family_id,
                TravelArrangementRequest.arrangement_id.in_(arrangement_ids),
            )
        )
        db.execute(delete(TravelArrangement).where(TravelArrangement.id.in_(arrangement_ids)))

    @staticmethod
    def view(item: TravelArrangement) -> dict:
        return {
            "id": item.id,
            "child_id": item.child_id,
            "name": item.name,
            "weekdays": [int(value) for value in (item.weekdays or "").split(",") if value],
            "start_time": item.start_time,
            "end_time": item.end_time,
            "active": item.active,
        }

    @classmethod
    def list_arrangements(
        cls, db: Session, family_id: str, child_id: str
    ) -> list[TravelArrangement]:
        ChildrenService.get_child(db, family_id, child_id)
        return list(
            db.scalars(
                select(TravelArrangement)
                .where(
                    TravelArrangement.family_id == family_id,
                    TravelArrangement.child_id == child_id,
                    TravelArrangement.active.is_(True),
                )
                .order_by(
                    TravelArrangement.start_time,
                    TravelArrangement.created_at,
                    TravelArrangement.id,
                )
            )
        )

    @classmethod
    def create(
        cls,
        db: Session,
        family_id: str,
        data: TravelArrangementCreate,
        idempotency_key: str | None = None,
    ) -> TravelArrangement:
        ChildrenService.require_active_child(db, family_id, data.child_id)
        fingerprint = sha256(
            json.dumps(data.model_dump(mode="json"), sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        if idempotency_key:
            existing = cls._request(db, family_id, idempotency_key)
            if existing is not None:
                if existing.request_fingerprint != fingerprint:
                    raise ConflictError("此出行安排提交标识已用于不同内容，请重新提交")
                if existing.arrangement_id is None:
                    raise RuntimeError("travel arrangement request is missing its arrangement")
                return cls._get(db, family_id, existing.arrangement_id)
        ensure_timed_item_capacity(db, family_id, data.child_id)
        item = TravelArrangement(
            family_id=family_id,
            child_id=data.child_id,
            name=data.name,
            weekdays=",".join(str(value) for value in data.weekdays),
            start_time=data.start_time,
            end_time=data.end_time,
        )
        db.add(item)
        db.flush()
        if idempotency_key:
            db.add(
                TravelArrangementRequest(
                    family_id=family_id,
                    idempotency_key=idempotency_key,
                    request_fingerprint=fingerprint,
                    arrangement_id=item.id,
                )
            )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if not idempotency_key:
                raise
            existing = cls._request(db, family_id, idempotency_key)
            if existing is None:
                raise
            if existing.request_fingerprint != fingerprint:
                raise ConflictError("此出行安排提交标识已用于不同内容，请重新提交") from None
            if existing.arrangement_id is None:
                raise RuntimeError(
                    "travel arrangement request is missing its arrangement"
                ) from None
            return cls._get(db, family_id, existing.arrangement_id)
        return item

    @staticmethod
    def _request(
        db: Session, family_id: str, idempotency_key: str
    ) -> TravelArrangementRequest | None:
        return db.scalar(
            select(TravelArrangementRequest).where(
                TravelArrangementRequest.family_id == family_id,
                TravelArrangementRequest.idempotency_key == idempotency_key,
            )
        )

    @staticmethod
    def _get(db: Session, family_id: str, arrangement_id: str) -> TravelArrangement:
        item = db.scalar(
            select(TravelArrangement).where(
                TravelArrangement.id == arrangement_id,
                TravelArrangement.family_id == family_id,
            )
        )
        if item is None:
            raise NotFoundError("没有找到这个出行安排")
        return item

    @classmethod
    def update(
        cls,
        db: Session,
        family_id: str,
        arrangement_id: str,
        data: TravelArrangementPatch,
    ) -> TravelArrangement:
        item = cls._get(db, family_id, arrangement_id)
        ChildrenService.require_active_child(db, family_id, item.child_id)
        values = data.model_dump(exclude_unset=True)
        if "weekdays" in values:
            values["weekdays"] = ",".join(str(value) for value in values["weekdays"])
        for key, value in values.items():
            setattr(item, key, value)
        if item.start_time is None or item.end_time is None:
            raise ValueError("出行安排必须包含开始和结束时间")
        if item.end_time <= item.start_time:
            raise ValueError("结束时间必须晚于开始时间")
        db.commit()
        return item

    @classmethod
    def delete(cls, db: Session, family_id: str, arrangement_id: str) -> None:
        item = cls._get(db, family_id, arrangement_id)
        ChildrenService.require_active_child(db, family_id, item.child_id)
        item.active = False
        db.commit()

    @classmethod
    def projections_for_day(
        cls, db: Session, family_id: str, child_id: str, target: date
    ) -> list[TravelArrangement]:
        return [
            item
            for item in cls.list_arrangements(db, family_id, child_id)
            if target.weekday()
            in [int(value) for value in (item.weekdays or "").split(",") if value]
        ]
