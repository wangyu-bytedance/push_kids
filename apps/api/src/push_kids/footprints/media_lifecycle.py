"""Footprint-owned resource inventory for family/child deletion."""

from sqlalchemy import select

from push_kids.footprints.models import FootprintPhoto
from push_kids.media.store import WeChatCloudMediaStore


class FootprintMediaCleanup:
    @staticmethod
    def delete_owned(database, store, family, child_id=None):
        last_id = ""
        while True:
            with database.session_factory() as db:
                query = select(FootprintPhoto).where(
                    FootprintPhoto.family_id == family, FootprintPhoto.id > last_id
                )
                if child_id:
                    query = query.where(FootprintPhoto.child_id == child_id)
                rows = list(db.scalars(query.order_by(FootprintPhoto.id).limit(100)))
            if not rows:
                return
            for item in rows:
                for ref in (item.original_ref, item.display_ref, item.thumbnail_ref):
                    if ref:
                        store.delete(ref)
                if isinstance(store, WeChatCloudMediaStore):
                    store.delete_path(item.upload_path)
            last_id = rows[-1].id
