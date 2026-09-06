from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from push_kids.data_management.schemas import DeletionConfirmation, DeletionRequestView
from push_kids.data_management.service import DataDeletionService
from push_kids.platform.context import (
    RequestContext,
    TrustedActorContext,
    manager_context,
    trusted_actor_context,
)
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["data-management"])
DeletionKey = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=8,
        max_length=100,
        pattern=r"^[A-Za-z0-9._:-]+$",
    ),
]


def _secret(request: Request) -> str:
    configured = request.app.state.settings.actor_hmac_key
    return configured.get_secret_value() if configured else "local-data-deletion-development-only"


@router.post(
    "/children/{child_id}/deletion-requests",
    response_model=DeletionRequestView,
    status_code=202,
)
def delete_child_data(
    child_id: str,
    body: DeletionConfirmation,
    request: Request,
    context: Annotated[RequestContext, Depends(manager_context)],
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: DeletionKey,
):
    return DataDeletionService.request_child_deletion(
        db,
        context,
        actor,
        child_id,
        body.confirmation_name,
        idempotency_key,
        _secret(request),
    )


@router.post(
    "/families/current/deletion-requests",
    response_model=DeletionRequestView,
    status_code=202,
)
def delete_family_data(
    body: DeletionConfirmation,
    request: Request,
    context: Annotated[RequestContext, Depends(manager_context)],
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: DeletionKey,
):
    return DataDeletionService.request_family_deletion(
        db,
        context,
        actor,
        body.confirmation_name,
        idempotency_key,
        _secret(request),
    )


@router.get("/deletion-requests/{request_id}", response_model=DeletionRequestView)
def deletion_status(
    request_id: str,
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return DataDeletionService.get_request(db, actor, request_id)


@router.post("/deletion-requests/{request_id}/retry", response_model=DeletionRequestView)
def retry_deletion(
    request_id: str,
    actor: Annotated[TrustedActorContext, Depends(trusted_actor_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return DataDeletionService.retry_request(db, actor, request_id)
