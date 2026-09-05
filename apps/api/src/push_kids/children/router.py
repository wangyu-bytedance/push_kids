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
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db

router = APIRouter(tags=["children"])


@router.get("/children", response_model=list[ChildView])
def list_children(
    family: Annotated[str, Depends(family_id)], db: Annotated[Session, Depends(get_db)]
):
    return ChildrenService.list_children(db, family)


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
