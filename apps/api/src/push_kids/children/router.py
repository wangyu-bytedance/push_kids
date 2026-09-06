from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from push_kids.children.schemas import (
    ChildCreate,
    ChildUpdate,
    ChildView,
    SubjectCreate,
    SubjectUpdate,
    SubjectView,
)
from push_kids.children.service import ChildrenService
from push_kids.platform.context import RequestContext, family_id, manager_context
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["children"])


@router.get("/children", response_model=list[ChildView])
def list_children(
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    include_archived: bool = False,
):
    return ChildrenService.list_children(db, family, include_archived)


@router.post("/children", response_model=ChildView, status_code=201)
def create_child(
    body: ChildCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.create_child(db, family, body)


@router.patch("/children/{child_id}", response_model=ChildView)
def update_child(
    child_id: str,
    body: ChildUpdate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.update_child(db, family, child_id, body)


@router.post("/children/{child_id}/archive", response_model=ChildView)
def archive_child(
    child_id: str,
    context: Annotated[RequestContext, Depends(manager_context)],
    db: Annotated[Session, Depends(get_db)],
):
    """Archiving hides a profile from the whole family, so it stays a manager decision."""
    return ChildrenService.archive_child(db, context.family_id, child_id, context.actor_binding_id)


@router.post("/children/{child_id}/restore", response_model=ChildView)
def restore_child(
    child_id: str,
    context: Annotated[RequestContext, Depends(manager_context)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.restore_child(db, context.family_id, child_id, context.actor_binding_id)


@router.get("/children/{child_id}/subjects", response_model=list[SubjectView])
def list_subjects(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.list_subjects(db, family, child_id)


@router.post("/subjects", response_model=SubjectView, status_code=201)
def create_subject(
    body: SubjectCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.create_subject(db, family, body)


@router.patch("/subjects/{subject_id}", response_model=SubjectView)
def update_subject(
    subject_id: str,
    body: SubjectUpdate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChildrenService.update_subject(db, family, subject_id, body)
