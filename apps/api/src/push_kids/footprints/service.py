"""Parent commands and visit ownership. Each mutation owns one transaction."""

import json

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from push_kids.footprints import access
from push_kids.footprints.models import FootprintPhoto, FootprintPreference, FootprintVisit
from push_kids.footprints.policies import capture_instant, is_expired, place_key
from push_kids.footprints.schemas import Confirm, PhotoPatch, PhotoView, Place
from push_kids.platform.errors import ConflictError
from push_kids.platform.time import utcnow


def view(item: FootprintPhoto) -> dict:
    if item.state in {"expired", "deleted", "cancelled"} or is_expired(item, utcnow()):
        return {
            "id": item.id,
            "import_id": item.import_id,
            "child_id": item.child_id,
            "version": item.version,
            "state": "expired" if is_expired(item, utcnow()) else item.state,
            "has_display": False,
            "received_at": None,
            "candidates": [],
        }
    result = PhotoView.model_validate(item).model_dump(mode="json")
    result["has_display"] = bool(item.derived_ready and not item.is_manual)
    result["candidates"] = json.loads(item.candidates_json or "[]")
    return result


def clear_metadata(item):
    for field in (
        "local_date",
        "local_time",
        "offset_minutes",
        "occurred_at",
        "sha256",
        "duplicate_of",
        "place_name",
        "city",
        "country",
        "latitude",
        "longitude",
        "coordinate_system",
    ):
        setattr(item, field, None)
    item.time_source = item.location_source = item.precision = "unknown"
    item.candidates_json = "[]"


def check_version(item, version: int):
    if item.version != version:
        raise ConflictError("照片已被修改，请刷新后核对")


def _attach_visit(db, item):
    key = place_key(item)
    visit = db.scalar(
        select(FootprintVisit).where(
            FootprintVisit.family_id == item.family_id,
            FootprintVisit.child_id == item.child_id,
            FootprintVisit.local_date == item.local_date,
            FootprintVisit.place_key == key,
        )
    )
    if visit is None:
        visit = FootprintVisit(
            family_id=item.family_id,
            child_id=item.child_id,
            local_date=item.local_date,
            sort_time=item.local_time or "24:00:00",
            sort_created_at=item.confirmed_at,
            place_key=key,
            **{name: getattr(item, name) for name in Place.model_fields},
        )
        db.add(visit)
        db.flush()
    item.visit_id = visit.id


def _refresh_order(db, family, child_id, visit_ids):
    db.flush()
    for visit_id in set(visit_ids) - {None}:
        visit = db.get(FootprintVisit, visit_id)
        if visit is None:
            continue
        timing = db.execute(
            select(
                func.min(func.coalesce(FootprintPhoto.local_time, "24:00:00")),
                func.min(FootprintPhoto.confirmed_at),
            ).where(
                FootprintPhoto.family_id == family,
                FootprintPhoto.child_id == child_id,
                FootprintPhoto.visit_id == visit_id,
                FootprintPhoto.state == "confirmed",
            )
        ).one()
        if timing[0]:
            visit.sort_time, visit.sort_created_at = timing


def _remove_empty_visits(db, family, child_id):
    db.flush()
    populated = select(FootprintPhoto.visit_id).where(
        FootprintPhoto.family_id == family,
        FootprintPhoto.child_id == child_id,
        FootprintPhoto.state == "confirmed",
        FootprintPhoto.visit_id.is_not(None),
    )
    db.execute(
        delete(FootprintVisit).where(
            FootprintVisit.family_id == family,
            FootprintVisit.child_id == child_id,
            FootprintVisit.id.not_in(populated),
        ),
        execution_options={"synchronize_session": False},
    )


class FootprintsService:
    @staticmethod
    def search_places(provider, limiter, actor, keyword, region):
        limiter.check(actor)
        return {"items": provider.search(keyword, region)}

    @staticmethod
    def order_visit(db, family, child_id, visit_id, body):
        access.guard(db, family, child_id, write=True)
        scope = access.scope(db, family, child_id)
        if scope.revision != body.revision:
            raise ConflictError("足迹已更新，请刷新后排序")
        visit = db.scalar(
            select(FootprintVisit)
            .where(
                FootprintVisit.family_id == family,
                FootprintVisit.child_id == child_id,
                FootprintVisit.id == visit_id,
            )
            .with_for_update()
        )
        if visit is None:
            from push_kids.platform.errors import NotFoundError

            raise NotFoundError("没有找到这次到访")
        visit.day_order = body.day_order
        revision = access.advance(db, family, child_id)
        db.commit()
        return {"revision": revision, "day_order": visit.day_order}

    @staticmethod
    def failed_cleanup(db, family, child_id):
        access.guard(db, family, child_id)
        criteria = [
            FootprintPhoto.family_id == family,
            FootprintPhoto.child_id == child_id,
            FootprintPhoto.cleanup_state == "failed",
        ]
        rows = db.execute(
            select(FootprintPhoto.id, FootprintPhoto.version, FootprintPhoto.cleanup_attempts)
            .where(*criteria)
            .order_by(FootprintPhoto.id)
            .limit(50)
        )
        return {
            "items": [{"id": row[0], "version": row[1], "attempts": row[2]} for row in rows],
            "total": db.scalar(select(func.count()).select_from(FootprintPhoto).where(*criteria)),
        }

    @staticmethod
    def retry_cleanup(db, family, child_id, photo_id, version):
        access.guard(db, family, child_id, write=True)
        item = db.scalar(
            select(FootprintPhoto)
            .where(
                FootprintPhoto.family_id == family,
                FootprintPhoto.child_id == child_id,
                FootprintPhoto.id == photo_id,
            )
            .with_for_update()
        )
        if item is None or item.cleanup_state != "failed":
            raise ConflictError("没有可重试的资源清理任务")
        check_version(item, version)
        item.cleanup_state, item.cleanup_attempts, item.cleanup_after = "pending", 0, utcnow()
        item.version += 1
        db.commit()
        return {"id": item.id, "version": item.version, "cleanup_state": item.cleanup_state}

    @staticmethod
    def preferences(db, family, member_id):
        item = db.get(FootprintPreference, (family, member_id or "local"))
        return {
            "ai_enabled": bool(item and item.ai_enabled),
            "consented": bool(item and item.consented),
        }

    @staticmethod
    def set_preferences(db, family, member_id, body):
        from push_kids.families.service import FamilyService

        FamilyService.lock_active_data_scope(db, family)
        key = (family, member_id or "local")
        item = db.get(FootprintPreference, key)
        if item is None:
            item = FootprintPreference(family_id=key[0], member_id=key[1])
            db.add(item)
        item.ai_enabled = body.ai_enabled
        item.consented = body.consented
        item.updated_at = utcnow()
        db.commit()
        return {"ai_enabled": item.ai_enabled, "consented": item.consented}

    @staticmethod
    def patch(db: Session, family: str, child_id: str, photo_id: str, body: PhotoPatch):
        item = access.photo(db, family, child_id, photo_id, write=True)
        check_version(item, body.version)
        old_visit = item.visit_id
        if "day_order" in body.model_fields_set and (
            item.state != "confirmed"
            or body.day_order is None
            or access.scope(db, family, child_id).revision != body.order_revision
        ):
            raise ConflictError("足迹已更新，请刷新后调整同日顺序")
        payload = body.model_dump(
            exclude_unset=True, exclude={"version", "day_order", "order_revision"}
        )
        merged = {name: payload.get(name, getattr(item, name)) for name in Place.model_fields}
        try:
            validated_place = Place.model_validate(merged)
        except ValueError as exc:
            raise ValueError("地点信息不完整，请一起核对经纬度和坐标来源") from exc
        for name, value in payload.items():
            setattr(item, name, value)
        for name, value in validated_place.model_dump().items():
            setattr(item, name, value)
        if item.state == "confirmed" and not item.local_date:
            raise ValueError("正式照片需要拍摄日期")
        if any(name in payload for name in ("local_date", "local_time", "offset_minutes")):
            item.time_source = "parent"
        if any(name in payload for name in Place.model_fields):
            item.location_source = "parent"
        item.occurred_at = capture_instant(item.local_date, item.local_time, item.offset_minutes)
        item.candidates_json = "[]"
        item.version += 1
        if item.derived_ready:
            item.job_state = (
                "cancelled" if item.job_state in {"queued", "running"} else item.job_state
            )
            item.lease_until = None
        if item.state == "confirmed":
            _attach_visit(db, item)
            if body.day_order is not None:
                visit = db.get(FootprintVisit, item.visit_id)
                assert visit is not None
                visit.day_order = body.day_order
            _refresh_order(db, family, child_id, [old_visit, item.visit_id])
            _remove_empty_visits(db, family, child_id)
        elif item.received_at:
            item.state = "ready"
        access.advance(db, family, child_id)
        db.commit()
        return view(item)

    @staticmethod
    def confirm(db, family, child_id, import_id, body: Confirm):
        access.guard(db, family, child_id, write=True)
        items = []
        for selected in body.photos:
            item = access.photo(db, family, child_id, selected.id, write=True)
            if item.import_id != import_id:
                raise ConflictError("照片不属于本批次")
            if item.state == "confirmed" and item.version == selected.version + 1:
                items.append(item)
                continue
            check_version(item, selected.version)
            if not item.local_date or not item.derived_ready or not item.received_at:
                raise ConflictError("请先补充拍摄日期并完成展示图处理")
            item.state = "confirmed"
            item.confirmed_at = utcnow()
            item.job_state = (
                "cancelled" if item.job_state in {"queued", "running"} else item.job_state
            )
            item.lease_until = None
            item.version += 1
            _attach_visit(db, item)
            items.append(item)
        _refresh_order(db, family, child_id, [item.visit_id for item in items])
        access.advance(db, family, child_id)
        db.commit()
        return {"confirmed": [view(item) for item in items]}

    @staticmethod
    def delete_photo(db, family, child_id, photo_id, version):
        access.guard(db, family, child_id, write=True)
        item = db.scalar(
            select(FootprintPhoto)
            .where(
                FootprintPhoto.family_id == family,
                FootprintPhoto.child_id == child_id,
                FootprintPhoto.id == photo_id,
            )
            .with_for_update()
        )
        if item and item.state == "deleted" and item.version == version + 1:
            return
        item = access.photo(db, family, child_id, photo_id, write=True)
        check_version(item, version)
        old_visit, item.visit_id = item.visit_id, None
        item.state, item.job_state = "deleted", "cancelled"
        item.version += 1
        clear_metadata(item)
        _refresh_order(db, family, child_id, [old_visit])
        item.cleanup_state, item.cleanup_after = "pending", utcnow()
        _remove_empty_visits(db, family, child_id)
        access.advance(db, family, child_id)
        db.commit()

    @staticmethod
    def retry(db, family, child_id, photo_id, version):
        item = access.photo(db, family, child_id, photo_id, write=True)
        check_version(item, version)
        if item.state == "confirmed" or not item.original_ref or item.job_state == "running":
            raise ConflictError("当前照片不能重新解析")
        if item.attempts >= 3:
            raise ConflictError("已达解析重试上限，可手动补充或重新导入")
        item.job_state, item.state, item.error_code = "queued", "queued", None
        item.available_at = utcnow()
        item.version += 1
        db.commit()
        return view(item)

    @staticmethod
    def purge_data(db, family, child_id=None):
        from push_kids.footprints.models import FootprintImport, FootprintScope

        for model in (FootprintPhoto, FootprintVisit, FootprintImport, FootprintScope):
            query = delete(model).where(model.family_id == family)
            if child_id is not None:
                query = query.where(model.child_id == child_id)
            db.execute(query, execution_options={"synchronize_session": False})
        if child_id is None:
            db.execute(delete(FootprintPreference).where(FootprintPreference.family_id == family))

    @staticmethod
    def pending_count(db, family, child_id):
        return (
            db.scalar(
                select(func.count())
                .select_from(FootprintPhoto)
                .where(
                    FootprintPhoto.family_id == family,
                    FootprintPhoto.child_id == child_id,
                    FootprintPhoto.state.not_in(["confirmed", "expired", "deleted", "cancelled"]),
                    FootprintPhoto.draft_expires_at > utcnow(),
                )
            )
            or 0
        )
