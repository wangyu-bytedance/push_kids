"""Private footprint delivery; expiry and ownership are checked before issuing capabilities."""

from push_kids.footprints import access
from push_kids.media.store import LocalMediaStore, WeChatCloudMediaStore
from push_kids.platform.errors import GoneError


class FootprintMedia:
    @staticmethod
    def preview(db, family, child_id, photo_id, size, store, limiter, actor):
        item = access.photo(db, family, child_id, photo_id)
        if not item.derived_ready or item.is_manual:
            raise GoneError("照片仍在处理或无法读取")
        limiter.check(actor)
        ref = item.display_ref if size == "display" else item.thumbnail_ref
        if isinstance(store, WeChatCloudMediaStore):
            return {"url": store.preview_url(ref), "expires_in": 60}
        return {
            "download_path": (
                f"/footprints/photos/{photo_id}/content?child_id={child_id}&size={size}"
            )
        }

    @staticmethod
    def content(db, family, child_id, photo_id, size, store):
        item = access.photo(db, family, child_id, photo_id)
        if not isinstance(store, LocalMediaStore) or not item.derived_ready or item.is_manual:
            raise GoneError("请重新读取照片")
        ref = item.display_ref if size == "display" else item.thumbnail_ref
        with store.materialize(ref) as path:
            if not path.is_file() or path.stat().st_size > store.max_bytes:
                raise GoneError("照片已删除或不可用")
            return path.read_bytes()
