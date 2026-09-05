from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import (
    FamilyInvite,
    FamilyJoinRequest,
    FamilyMember,
    InviteStatus,
    JoinRequestStatus,
    MemberStatus,
    WeChatActorBinding,
)


class FamilyRepository:
    @staticmethod
    def actor_binding(db: Session, app_id: str, subject: str, *, lock: bool = False):
        statement: Select[tuple[WeChatActorBinding]] = select(WeChatActorBinding).where(
            WeChatActorBinding.app_id == app_id,
            WeChatActorBinding.subject_hmac == subject,
        )
        if lock:
            statement = statement.with_for_update()
        return db.scalar(statement)

    @staticmethod
    def active_member(db: Session, binding_id: str, *, lock: bool = False):
        statement: Select[tuple[FamilyMember]] = select(FamilyMember).where(
            FamilyMember.actor_binding_id == binding_id,
            FamilyMember.status == MemberStatus.active.value,
        )
        if lock:
            statement = statement.with_for_update()
        return db.scalar(statement)

    @staticmethod
    def pending_request(db: Session, binding_id: str, *, lock: bool = False):
        statement: Select[tuple[FamilyJoinRequest]] = select(FamilyJoinRequest).where(
            FamilyJoinRequest.applicant_binding_id == binding_id,
            FamilyJoinRequest.status == JoinRequestStatus.pending.value,
        )
        if lock:
            statement = statement.with_for_update()
        return db.scalar(statement)

    @staticmethod
    def invite_by_hash(db: Session, token_hash: str, *, lock: bool = False):
        statement: Select[tuple[FamilyInvite]] = select(FamilyInvite).where(
            FamilyInvite.token_hash == token_hash
        )
        if lock:
            statement = statement.with_for_update()
        return db.scalar(statement)

    @staticmethod
    def active_invites(db: Session, family_id: str) -> list[FamilyInvite]:
        return list(
            db.scalars(
                select(FamilyInvite).where(
                    FamilyInvite.family_id == family_id,
                    FamilyInvite.status == InviteStatus.active.value,
                )
            )
        )
