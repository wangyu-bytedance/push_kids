from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from push_kids.activities.weekly_slots import has_weekly_time_slots_capability
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db
from push_kids.travel.schemas import (
    TravelArrangementCreate,
    TravelArrangementList,
    TravelArrangementPatch,
    TravelArrangementView,
)
from push_kids.travel.service import TravelService

router = APIRouter(tags=["travel"])


@router.get(
    "/children/{child_id}/travel-arrangements",
    response_model=TravelArrangementList,
)
def list_travel_arrangements(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    items = TravelService.list_arrangements(db, family, child_id)
    return {
        "items": [
            TravelService.view(db, item, client_supports_slots=supports_slots) for item in items
        ]
    }


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
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    item = TravelService.create(
        db,
        family,
        body,
        idempotency_key,
        client_supports_slots=supports_slots,
    )
    return TravelService.view(db, item, client_supports_slots=supports_slots)


@router.patch("/travel-arrangements/{arrangement_id}", response_model=TravelArrangementView)
def update_travel_arrangement(
    arrangement_id: str,
    body: TravelArrangementPatch,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    client_capabilities: Annotated[str | None, Header(alias="X-Client-Capabilities")] = None,
):
    supports_slots = has_weekly_time_slots_capability(client_capabilities)
    item = TravelService.update(
        db,
        family,
        arrangement_id,
        body,
        client_supports_slots=supports_slots,
    )
    return TravelService.view(db, item, client_supports_slots=supports_slots)


@router.delete("/travel-arrangements/{arrangement_id}", status_code=204)
def delete_travel_arrangement(
    arrangement_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    TravelService.delete(db, family, arrangement_id)
