"""Bounded, idempotent photo intake with preallocated archive-safe slots."""

import hashlib
import json
from datetime import timedelta

from sqlalchemy import func, or_, select

from push_kids.footprints import access
from push_kids.footprints.models import FootprintImport, FootprintPhoto
from push_kids.footprints.policies import draft_expiry
from push_kids.footprints.service import view
from push_kids.media.store import LocalMediaStore, WeChatCloudMediaStore
from push_kids.persistence.models import new_id
from push_kids.platform.errors import ConflictError, ForbiddenError, NotFoundError
from push_kids.platform.time import utcnow


class FootprintImports:
    @staticmethod
    def manual(db, family, member, body, key):
        from push_kids.footprints.schemas import ImportCreate, PhotoPatch
        from push_kids.footprints.service import FootprintsService

        fingerprint = hashlib.sha256(body.model_dump_json().encode()).hexdigest()
        batch = FootprintImports.create(
            db,
            family,
            member,
            ImportCreate(child_id=body.child_id, count=1, consented=True),
            key,
            fingerprint,
        )
        item = access.photo(db, family, body.child_id, batch["photos"][0]["id"], write=True)
        if item.received_at:
            return FootprintImports.get(db, family, body.child_id, batch["id"])
        now = utcnow()
        item.is_manual, item.derived_ready = True, True
        item.received_at, item.draft_expires_at = now, draft_expiry(now)
        db.flush()
        values = body.model_dump(exclude={"child_id", "version", "day_order", "order_revision"})
        FootprintsService.patch(
            db, family, body.child_id, item.id, PhotoPatch(version=item.version, **values)
        )
        return FootprintImports.get(db, family, body.child_id, batch["id"])

    @staticmethod
    def create(db, family, member, body, request_key, fingerprint=None):
        access.guard(db, family, body.child_id, write=True)
        fingerprint = (
            fingerprint
            or hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True).encode()).hexdigest()
        )
        old = db.scalar(
            select(FootprintImport).where(
                FootprintImport.family_id == family,
                FootprintImport.member_id == (member or "local"),
                FootprintImport.request_key == request_key,
            )
        )
        if old:
            if old.request_fingerprint != fingerprint:
                raise ConflictError("本次导入请求已用于其他照片，请重新发起")
            return FootprintImports.get(db, family, body.child_id, old.id)
        access.guard(db, family, body.child_id, write=True, intake=True)
        now = utcnow()
        outstanding = (
            db.scalar(
                select(func.count())
                .select_from(FootprintPhoto)
                .where(
                    FootprintPhoto.family_id == family,
                    FootprintPhoto.child_id == body.child_id,
                    FootprintPhoto.state.not_in(["confirmed", "expired", "deleted", "cancelled"]),
                    or_(
                        FootprintPhoto.draft_expires_at > now,
                        (FootprintPhoto.draft_expires_at.is_(None))
                        & (FootprintPhoto.ticket_expires_at > now),
                    ),
                )
            )
            or 0
        )
        if outstanding + body.count > 200:
            raise ConflictError("待整理照片最多200张，请先确认或删除部分草稿")
        batch = FootprintImport(
            family_id=family,
            child_id=body.child_id,
            member_id=member or "local",
            request_key=request_key,
            request_fingerprint=fingerprint,
            slot_count=body.count,
        )
        db.add(batch)
        db.flush()
        family_hash = hashlib.sha256(family.encode()).hexdigest()[:16]
        for ordinal in range(body.count):
            photo_id = new_id()
            db.add(
                FootprintPhoto(
                    id=photo_id,
                    family_id=family,
                    child_id=body.child_id,
                    import_id=batch.id,
                    ordinal=ordinal,
                    upload_path=f"footprints/{family_hash}/{batch.id}/{photo_id}/original",
                    ticket_expires_at=now + timedelta(minutes=15),
                    job_state="cancelled",
                )
            )
        access.advance(db, family, body.child_id)
        db.commit()
        return FootprintImports.get(db, family, body.child_id, batch.id)

    @staticmethod
    def get(db, family, child_id, import_id):
        access.guard(db, family, child_id)
        batch = db.scalar(
            select(FootprintImport).where(
                FootprintImport.family_id == family,
                FootprintImport.child_id == child_id,
                FootprintImport.id == import_id,
            )
        )
        if batch is None:
            raise NotFoundError("没有找到这批照片")
        rows = list(
            db.scalars(
                select(FootprintPhoto)
                .where(
                    FootprintPhoto.family_id == family,
                    FootprintPhoto.child_id == child_id,
                    FootprintPhoto.import_id == batch.id,
                )
                .order_by(FootprintPhoto.ordinal)
                .limit(20)
            )
        )
        return {"id": batch.id, "child_id": child_id, "photos": [view(item) for item in rows]}

    @staticmethod
    def ticket(db, family, child_id, photo_id, member):
        item = access.photo(db, family, child_id, photo_id, write=True)
        batch = db.get(FootprintImport, item.import_id)
        if batch.member_id != (member or "local"):
            raise ForbiddenError("请由本批照片的上传者继续上传")
        if item.received_at:
            return {"photo": view(item), "cloud_path": None, "expires_at": None}
        return {"cloud_path": item.upload_path, "expires_at": item.ticket_expires_at}

    @staticmethod
    def _received(db, item, storage_ref, digest):
        now = utcnow()
        item.original_ref = storage_ref
        prefix = storage_ref.rsplit("/", 1)[0]
        # Record deterministic derivative paths before worker I/O, so crashes cannot orphan them.
        item.display_ref = prefix + "/display.jpg"
        item.thumbnail_ref = prefix + "/thumbnail.jpg"
        item.sha256 = digest
        item.duplicate_of = db.scalar(
            select(FootprintPhoto.id)
            .where(
                FootprintPhoto.family_id == item.family_id,
                FootprintPhoto.child_id == item.child_id,
                FootprintPhoto.id != item.id,
                FootprintPhoto.sha256 == digest,
                FootprintPhoto.state.not_in(["expired", "deleted", "cancelled"]),
                or_(FootprintPhoto.state == "confirmed", FootprintPhoto.draft_expires_at > now),
            )
            .order_by(FootprintPhoto.id)
            .limit(1)
        )
        item.received_at = now
        item.draft_expires_at = draft_expiry(now)
        item.state, item.job_state = "queued", "queued"
        item.version += 1
        item.available_at = now
        access.advance(db, item.family_id, item.child_id)
        db.commit()
        return view(item)

    @staticmethod
    async def upload(db, family, child_id, photo_id, member, store, upload):
        FootprintImports.ticket(db, family, child_id, photo_id, member)
        item = access.photo(db, family, child_id, photo_id, write=True)
        if item.received_at:
            content = await upload.read(10 * 1024 * 1024 + 1)
            if not content or len(content) > 10 * 1024 * 1024:
                raise ValueError("单张照片不能超过10MB")
            if hashlib.sha256(content).hexdigest() != item.sha256:
                raise ConflictError("这张照片已上传，请刷新核对")
            return view(item)
        if not isinstance(store, LocalMediaStore):
            raise ValueError("云端照片请使用私有对象直传")
        saved = await store.save(family, f"footprints/{item.id}", upload)
        with store.materialize(saved.path) as path:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return FootprintImports._received(db, item, saved.path, digest)

    @staticmethod
    def claim(db, family, child_id, photo_id, context, store, body):
        FootprintImports.ticket(db, family, child_id, photo_id, context.member_id)
        item = access.photo(db, family, child_id, photo_id, write=True)
        if item.received_at:
            if item.original_ref != body.file_id:
                raise ConflictError("这张照片已上传，请刷新核对")
            return view(item)
        if not isinstance(store, WeChatCloudMediaStore) or not context.openid:
            raise ValueError("当前环境不支持云对象认领")
        claimed = store.claim(body.file_id, item.upload_path, context.openid)
        return FootprintImports._received(db, item, claimed.storage_ref, claimed.sha256)
