from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from sqlalchemy.orm import Session

from push_kids.families.schemas import (
    BootstrapView,
    FamilyCreate,
    InviteCreate,
    InviteListItem,
    InvitePreview,
    InviteTokenRequest,
    InviteView,
    JoinDecision,
    JoinRejection,
    JoinRequestCreate,
    JoinRequestView,
    MemberUpdate,
    MemberView,
)
from push_kids.families.service import FamilyService
from push_kids.platform.context import (
    RequestContext,
    TrustedActorContext,
    request_context,
    trusted_actor_context,
)
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["families"])
IdempotencyKey = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=8,
        max_length=100,
        pattern=r"^[A-Za-z0-9._:-]+$",
    ),
]


@router.get("/me", response_model=BootstrapView)
def bootstrap(
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return FamilyService.bootstrap(db, actor)


@router.post("/families", response_model=BootstrapView, status_code=201)
def create_family(
    body: FamilyCreate,
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: IdempotencyKey,
):
    return FamilyService.create_family(db, actor, body, idempotency_key)


@router.get("/families/current/members", response_model=list[MemberView])
def list_members(
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return FamilyService.list_members(db, context)


@router.patch("/families/current/members/{member_id}", response_model=MemberView)
def update_member(
    member_id: str,
    body: MemberUpdate,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return FamilyService.update_member(db, context, member_id, body)


@router.delete("/families/current/members/{member_id}", status_code=204)
def remove_member(
    member_id: str,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    FamilyService.remove_member(db, context, member_id)
    return Response(status_code=204)


@router.post("/families/current/invites", response_model=InviteView, status_code=201)
def create_invite(
    body: InviteCreate,
    request: Request,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: IdempotencyKey,
):
    configured = request.app.state.settings.actor_hmac_key
    secret = configured.get_secret_value() if configured else "local-family-invite-development-only"
    return FamilyService.create_invite(db, context, body, idempotency_key, secret)


@router.get("/families/current/invites", response_model=list[InviteListItem])
def list_invites(
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return FamilyService.list_invites(db, context)


@router.delete("/families/current/invites/{invite_id}", status_code=204)
def revoke_invite(
    invite_id: str,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    FamilyService.revoke_invite(db, context, invite_id)
    return Response(status_code=204)


@router.post("/family-invites/preview", response_model=InvitePreview)
def preview_invite(
    body: InviteTokenRequest,
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    request.app.state.invite_preview_limiter.check(actor.subject_hmac)
    return FamilyService.preview_invite(db, body.token)


@router.post("/family-requests", response_model=JoinRequestView, status_code=201)
def apply_to_family(
    body: JoinRequestCreate,
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: IdempotencyKey,
):
    return FamilyService.apply(db, actor, body.token, body, idempotency_key)


@router.delete("/family-requests/current", status_code=204)
def cancel_current_request(
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
):
    FamilyService.cancel_current_request(db, actor)
    return Response(status_code=204)


@router.get("/families/current/requests", response_model=list[JoinRequestView])
def list_requests(
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return FamilyService.list_requests(db, context)


@router.post("/family-requests/{request_id}/approve", response_model=MemberView)
def approve_request(
    request_id: str,
    body: JoinDecision,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: IdempotencyKey,
):
    return FamilyService.approve(db, context, request_id, body, idempotency_key)


@router.post("/family-requests/{request_id}/reject", response_model=JoinRequestView)
def reject_request(
    request_id: str,
    body: JoinRejection,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: IdempotencyKey,
):
    return FamilyService.reject(db, context, request_id, body, idempotency_key)
