from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.families.service import FamilyService
from push_kids.footprints.models import FootprintPhoto, FootprintScope
from push_kids.footprints.policies import is_expired
from push_kids.platform.errors import ConflictError, GoneError, NotFoundError
from push_kids.platform.time import utcnow


def eligible_work():
    return (
        FamilyService.data_scope_available(FootprintPhoto.family_id),
        ChildrenService.data_scope_available(FootprintPhoto.family_id, FootprintPhoto.child_id),
    )


def guard(db: Session, family: str, child_id: str, *, write=False, intake=False):
    if write:
        FamilyService.lock_active_data_scope(db, family)
        child = ChildrenService.lock_existing_data_scope(db, family, child_id)
    else:
        child = ChildrenService.get_child(db, family, child_id)
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理")
    if intake and not child.active:
        raise ConflictError("已归档孩子不能新增照片，可继续整理已有草稿")
    return child


def photo(db: Session, family: str, child_id: str, photo_id: str, *, write=False):
    guard(db, family, child_id, write=write)
    item = db.scalar(
        select(FootprintPhoto)
        .where(
            FootprintPhoto.family_id == family,
            FootprintPhoto.child_id == child_id,
            FootprintPhoto.id == photo_id,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
        if write
        else select(FootprintPhoto).where(
            FootprintPhoto.family_id == family,
            FootprintPhoto.child_id == child_id,
            FootprintPhoto.id == photo_id,
        )
    )
    if item is None:
        raise NotFoundError("没有找到这张照片")
    if item.state in {"deleted", "expired", "cancelled"} or is_expired(item, utcnow()):
        raise GoneError("这张照片已删除或草稿已到期")
    return item


def scope(db: Session, family: str, child_id: str) -> FootprintScope:
    item = db.get(FootprintScope, (family, child_id), populate_existing=True)
    if item is None:
        item = FootprintScope(family_id=family, child_id=child_id, revision=0)
        db.add(item)
        db.flush()
    return item


def advance(db: Session, family: str, child_id: str) -> int:
    item = scope(db, family, child_id)
    item.revision = int(item.revision or 0) + 1
    db.flush()
    return item.revision
