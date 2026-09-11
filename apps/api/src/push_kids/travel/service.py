from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, time
from hashlib import sha256

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.activities.capacity import ensure_timed_item_capacity
from push_kids.activities.weekly_slots import WeeklySlotValue, slots_from_legacy, uniform_range
from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    TravelArrangement,
    TravelArrangementRequest,
    TravelArrangementSlot,
)
from push_kids.platform.errors import ClientUpgradeRequiredError, ConflictError, NotFoundError
from push_kids.travel.schemas import TravelArrangementCreate, TravelArrangementPatch


@dataclass(frozen=True)
class TravelProjection:
    id: str
    name: str
    start_time: time
    end_time: time


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
        db.execute(
            delete(TravelArrangementSlot).where(
                TravelArrangementSlot.family_id == family_id,
                TravelArrangementSlot.arrangement_id.in_(arrangement_ids),
            )
        )
        db.execute(delete(TravelArrangement).where(TravelArrangement.id.in_(arrangement_ids)))

    @staticmethod
    def _slot_values(db: Session, arrangement_id: str) -> tuple[WeeklySlotValue, ...]:
        rows = db.scalars(
            select(TravelArrangementSlot)
            .where(TravelArrangementSlot.arrangement_id == arrangement_id)
            .order_by(TravelArrangementSlot.weekday)
        )
        values = []
        for row in rows:
            if row.weekday is None or row.start_time is None or row.end_time is None:
                raise RuntimeError("travel arrangement slot is incomplete")
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
        item: TravelArrangement,
        *,
        client_supports_slots: bool,
    ) -> dict:
        slots = cls._slot_values(db, str(item.id))
        cls._ensure_client_supports_slots(slots, client_supports_slots)
        common = uniform_range(slots)
        return {
            "id": item.id,
            "child_id": item.child_id,
            "name": item.name,
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
            "active": item.active,
        }

    @staticmethod
    def _replace_slots(
        db: Session, item: TravelArrangement, slots: tuple[WeeklySlotValue, ...]
    ) -> None:
        db.execute(
            delete(TravelArrangementSlot).where(
                TravelArrangementSlot.arrangement_id == item.id,
                TravelArrangementSlot.family_id == item.family_id,
            )
        )
        for slot in slots:
            db.add(
                TravelArrangementSlot(
                    family_id=item.family_id,
                    child_id=item.child_id,
                    arrangement_id=item.id,
                    weekday=slot.weekday,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                )
            )
        common = uniform_range(slots)
        item.weekdays = ",".join(str(slot.weekday) for slot in slots)
        mirror = common or (slots[0].start_time, slots[0].end_time)
        item.start_time = mirror[0]
        item.end_time = mirror[1]

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
        *,
        client_supports_slots: bool = False,
    ) -> TravelArrangement:
        slots = data.slot_values()
        cls._ensure_client_supports_slots(slots, client_supports_slots)
        ChildrenService.require_active_child(db, family_id, data.child_id)
        fingerprint = sha256(
            json.dumps(
                {
                    "child_id": data.child_id,
                    "name": data.name,
                    "time_slots": [
                        {
                            "weekday": slot.weekday,
                            "start_time": slot.start_time.isoformat(),
                            "end_time": slot.end_time.isoformat(),
                        }
                        for slot in slots
                    ],
                },
                sort_keys=True,
                ensure_ascii=False,
            ).encode()
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
            weekdays="",
            start_time=slots[0].start_time,
            end_time=slots[0].end_time,
        )
        db.add(item)
        db.flush()
        cls._replace_slots(db, item, slots)
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
        *,
        client_supports_slots: bool = False,
    ) -> TravelArrangement:
        item = cls._get(db, family_id, arrangement_id)
        ChildrenService.require_active_child(db, family_id, item.child_id)
        current_slots = cls._slot_values(db, arrangement_id)
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
            if not slot_values:
                raise ValueError("请至少选择一天")
        if slot_values is not None:
            cls._ensure_client_supports_slots(slot_values, client_supports_slots)
        values = data.model_dump(
            exclude_unset=True,
            exclude={"weekdays", "start_time", "end_time", "time_slots"},
        )
        for key, value in values.items():
            setattr(item, key, value)
        if slot_values is not None:
            cls._replace_slots(db, item, slot_values)
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
    ) -> list[TravelProjection]:
        ChildrenService.get_child(db, family_id, child_id)
        rows = db.execute(
            select(TravelArrangement, TravelArrangementSlot)
            .join(
                TravelArrangementSlot,
                TravelArrangementSlot.arrangement_id == TravelArrangement.id,
            )
            .where(
                TravelArrangement.family_id == family_id,
                TravelArrangement.child_id == child_id,
                TravelArrangement.active.is_(True),
                TravelArrangementSlot.family_id == family_id,
                TravelArrangementSlot.child_id == child_id,
                TravelArrangementSlot.weekday == target.weekday(),
            )
            .order_by(
                TravelArrangementSlot.start_time,
                TravelArrangement.created_at,
                TravelArrangement.id,
            )
        ).all()
        return [
            TravelProjection(
                id=str(item.id),
                name=str(item.name),
                start_time=slot.start_time,
                end_time=slot.end_time,
            )
            for item, slot in rows
        ]
