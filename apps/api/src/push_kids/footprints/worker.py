"""Durable per-photo leases and independent resource cleanup; no request background tasks."""

import asyncio
import json
import logging
import tempfile
from contextlib import suppress
from datetime import timedelta
from pathlib import Path

from sqlalchemy import or_, select

from push_kids.footprints import access
from push_kids.footprints.metadata import prepare_bounded as prepare
from push_kids.footprints.models import FootprintImport, FootprintPhoto
from push_kids.footprints.policies import capture_instant, is_expired
from push_kids.footprints.service import FootprintsService, clear_metadata
from push_kids.media.store import WeChatCloudMediaStore
from push_kids.platform.time import utcnow

logger = logging.getLogger("push_kids.footprints")


class FootprintWorker:
    def __init__(self, database, store, provider, places, poll_seconds=1):
        self.database, self.store = database, store
        self.provider, self.places = provider, places
        self.poll_seconds = poll_seconds
        self._stop = asyncio.Event()
        self.is_ready = False

    def stop(self):
        self._stop.set()

    async def run(self):
        try:
            while not self._stop.is_set():
                try:
                    worked = await asyncio.to_thread(self.process_one)
                    self.is_ready = True
                except Exception as exc:
                    self.is_ready = False
                    logger.warning("footprint_iteration_failed error_type=%s", type(exc).__name__)
                    worked = False
                if not worked:
                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self._stop.wait(), self.poll_seconds)
        finally:
            self.is_ready = False

    def process_one(self):
        if self.cleanup_one():
            return True
        now = utcnow()
        with self.database.session_factory() as db:
            candidate = db.execute(
                select(FootprintPhoto.id, FootprintPhoto.family_id, FootprintPhoto.child_id)
                .where(
                    *access.eligible_work(),
                    FootprintPhoto.state.in_(["queued", "ready", "failed"]),
                    or_(
                        FootprintPhoto.job_state == "queued",
                        (FootprintPhoto.job_state == "running")
                        & (FootprintPhoto.lease_until < now),
                    ),
                    FootprintPhoto.available_at <= now,
                    FootprintPhoto.draft_expires_at > now,
                )
                .order_by(FootprintPhoto.available_at, FootprintPhoto.id)
                .limit(1)
            ).first()
            if not candidate:
                return False
            try:
                item = access.photo(db, candidate[1], candidate[2], candidate[0], write=True)
            except Exception:
                db.rollback()
                return False
            if (
                item.state not in {"queued", "ready", "failed"}
                or item.job_state not in {"queued", "running"}
                or (item.job_state == "running" and item.lease_until >= now)
            ):
                return False
            if item.attempts >= 3:
                item.job_state, item.state, item.error_code = "failed", "failed", "analysis_failed"
                db.commit()
                return True
            item.job_state, item.attempts = "running", item.attempts + 1
            item.lease_until = now + timedelta(minutes=5)
            lease = (item.id, item.attempts, item.version, item.family_id, item.child_id)
            original, display, thumbnail = item.original_ref, item.display_ref, item.thumbnail_ref
            batch = db.get(FootprintImport, item.import_id)
            ai_enabled = FootprintsService.preferences(db, item.family_id, batch.member_id)[
                "ai_enabled"
            ]
            db.commit()
        try:
            with tempfile.TemporaryDirectory(prefix="footprint-") as folder:
                output, small = Path(folder) / "display.jpg", Path(folder) / "thumbnail.jpg"
                with self.store.materialize(original) as source:
                    metadata = prepare(source, output, small).values
                hints = []
                if metadata.get("latitude") is not None:
                    try:
                        lat, lon = metadata["latitude"], metadata["longitude"]
                        address = self.places.reverse(lat, lon)
                        converted = self.places.convert(lat, lon)
                        if address:
                            metadata.update(
                                place_name=address.place_name,
                                city=address.city,
                                country=address.country,
                            )
                        if converted:
                            metadata.update(
                                latitude=converted.latitude,
                                longitude=converted.longitude,
                                coordinate_system="gcj02",
                            )
                    except Exception:
                        pass  # Keep original WGS84; queries explicitly report unconverted points.
                # Recheck preference and parent values immediately before any AI transmission.
                with self.database.session_factory() as db:
                    current = access.photo(db, lease[3], lease[4], lease[0], write=True)
                    latest = FootprintsService.preferences(db, lease[3], batch.member_id)
                    from push_kids.families.service import FamilyService

                    active_member = batch.member_id == "local" or batch.member_id in (
                        FamilyService.active_member_ids(db, {batch.member_id})
                    )
                    allow_ai = (
                        ai_enabled
                        and latest["ai_enabled"]
                        and current.version == lease[2]
                        and active_member
                        and current.state in {"queued", "ready", "failed"}
                        and not current.place_name
                        and current.latitude is None
                        and metadata.get("latitude") is None
                    )
                    ai_failed = False
                    # The family lock serializes dispatch with consent withdrawal and deletion.
                    # This bounded provider call holds the lock for at most its 30s timeout.
                    if allow_ai:
                        try:
                            hints = [
                                {
                                    "place_name": hint.name,
                                    "city": hint.city,
                                    "country": hint.country,
                                    "precision": "unknown",
                                }
                                for hint in self.provider.locate(output).candidates
                            ]
                        except Exception:
                            ai_failed = True
                    db.commit()
                with self.database.session_factory() as db:
                    item = access.photo(db, lease[3], lease[4], lease[0], write=True)
                    if (
                        item.state not in {"queued", "ready", "failed"}
                        or item.job_state != "running"
                        or item.attempts != lease[1]
                    ):
                        return True
                    # Serialize derivative writes with deletion's family/child freeze. Inventory
                    # paths were recorded at receipt, before any external I/O.
                    self.store.write_derived(display, output)
                    self.store.write_derived(thumbnail, small)
                    item.derived_ready = True
                    if item.original_delete_after is None:
                        item.original_delete_after = utcnow() + timedelta(hours=24)
                    if item.version == lease[2]:
                        for name, value in metadata.items():
                            setattr(item, name, value)
                        item.candidates_json = json.dumps(hints, ensure_ascii=False)
                        item.occurred_at = capture_instant(
                            item.local_date, item.local_time, item.offset_minutes
                        )
                    item.state, item.lease_until = "ready", None
                    item.job_state = (
                        "queued"
                        if ai_failed and item.attempts < 3
                        else ("failed" if ai_failed else "succeeded")
                    )
                    item.error_code = "location_unavailable" if ai_failed else None
                    item.available_at = utcnow() + timedelta(seconds=5 * item.attempts)
                    item.version += 1
                    access.advance(db, item.family_id, item.child_id)
                    db.commit()
        except Exception as exc:
            logger.warning("footprint_processing_failed error_type=%s", type(exc).__name__)
            with self.database.session_factory() as db:
                try:
                    item = access.photo(db, lease[3], lease[4], lease[0], write=True)
                    if (
                        item.state in {"queued", "ready", "failed"}
                        and item.job_state == "running"
                        and item.attempts == lease[1]
                    ):
                        retry = item.attempts < 3 and not isinstance(exc, ValueError)
                        item.job_state = "queued" if retry else "failed"
                        item.state = "queued" if retry else "failed"
                        item.error_code = (
                            "invalid_image" if isinstance(exc, ValueError) else "analysis_failed"
                        )
                        item.lease_until = None
                        item.available_at = utcnow() + timedelta(seconds=5 * item.attempts)
                        db.commit()
                except Exception:
                    db.rollback()  # Deleted, frozen, expired or superseded: never resurrect.
        return True

    def cleanup_one(self):
        now = utcnow()
        with self.database.session_factory() as db:
            row = db.scalar(
                select(FootprintPhoto)
                .where(
                    *access.eligible_work(),
                    or_(
                        (FootprintPhoto.cleanup_state == "pending")
                        & (FootprintPhoto.cleanup_after <= now),
                        (FootprintPhoto.original_ref.is_not(None))
                        & (FootprintPhoto.original_delete_after <= now),
                        (
                            FootprintPhoto.state.not_in(
                                ["confirmed", "expired", "deleted", "cancelled"]
                            )
                        )
                        & (
                            (FootprintPhoto.draft_expires_at <= now)
                            | (
                                FootprintPhoto.received_at.is_(None)
                                & (FootprintPhoto.ticket_expires_at <= now)
                            )
                        ),
                    ),
                )
                .order_by(FootprintPhoto.created_at)
                .limit(1)
                .with_for_update()
            )
            if row is None:
                return False
            # Every lifecycle mutation uses the same family->child lock order as commands/deletion.
            family, child_id, photo_id = row.family_id, row.child_id, row.id
            db.rollback()
            try:
                access.guard(db, family, child_id, write=True)
            except Exception:
                db.rollback()
                return False  # Owned family deletion handles its complete inventory.
            item = db.scalar(
                select(FootprintPhoto)
                .where(
                    FootprintPhoto.family_id == family,
                    FootprintPhoto.child_id == child_id,
                    FootprintPhoto.id == photo_id,
                )
                .with_for_update()
            )
            if item is None:
                return False
            expired = is_expired(item, now) and item.state not in {
                "deleted",
                "expired",
                "cancelled",
            }
            full = expired or item.state in {"expired", "deleted", "cancelled"}
            if expired:
                item.state, item.job_state = "expired", "cancelled"
                item.version += 1
                clear_metadata(item)
                item.cleanup_state = "pending"
                access.advance(db, family, child_id)
            try:
                refs = [item.original_ref]
                if full:
                    refs += [item.display_ref, item.thumbnail_ref]
                for ref in refs:
                    if ref:
                        self.store.delete(ref)
                if full and isinstance(self.store, WeChatCloudMediaStore):
                    self.store.delete_path(item.upload_path)
                item.original_ref, item.original_delete_after = None, None
                if full:
                    item.display_ref, item.thumbnail_ref = None, None
                    item.derived_ready = False
                    item.cleanup_state, item.cleanup_after = "succeeded", None
                else:
                    item.cleanup_state, item.cleanup_after = "none", None
            except Exception:
                item.cleanup_attempts += 1
                item.cleanup_state = "pending" if item.cleanup_attempts < 3 else "failed"
                item.cleanup_after = now + timedelta(minutes=5 * item.cleanup_attempts)
                # Stop an expired deadline selecting failed cleanup in a tight loop.
                item.original_delete_after = None
            db.commit()
            return True
