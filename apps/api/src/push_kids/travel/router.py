from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db
from push_kids.travel.schemas import (
    TravelArrangementCreate,
    TravelArrangementPatch,
    TravelArrangementView,
)
from push_kids.travel.service import TravelService

router = APIRouter(tags=["travel"])


@router.get("/children/{child_id}/travel-arrangements")
def list_travel_arrangements(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    items = TravelService.list_arrangements(db, family, child_id)
    return {"items": [TravelService.view(item) for item in items]}


@router.post("/travel-arrangements", response_model=TravelArrangementView, status_code=201)
def create_travel_arrangement(
    body: TravelArrangementCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ] = None,
):
    return TravelService.view(TravelService.create(db, family, body, idempotency_key))


@router.patch("/travel-arrangements/{arrangement_id}", response_model=TravelArrangementView)
def update_travel_arrangement(
    arrangement_id: str,
    body: TravelArrangementPatch,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return TravelService.view(TravelService.update(db, family, arrangement_id, body))


@router.delete("/travel-arrangements/{arrangement_id}", status_code=204)
def delete_travel_arrangement(
    arrangement_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    TravelService.delete(db, family, arrangement_id)
