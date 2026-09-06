from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from push_kids.children.schemas import ChildCreate, ChildView

Role = Literal["viewer", "editor", "manager"]


class FamilyCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=60)
    relationship_label: str = Field(min_length=1, max_length=30)
    # Optional so opening a family and building a learning profile stay separate steps.
    # A family with no profile is a valid state; settings offers the add-profile entry.
    child: ChildCreate | None = None


class FamilySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str


class MemberView(BaseModel):
    id: str
    role: Role
    relationship_label: str
    is_self: bool
    created_at: datetime


class JoinRequestSummary(BaseModel):
    id: str
    request_code: str
    family_id: str
    status: str
    relationship_label: str
    created_at: datetime


class BootstrapView(BaseModel):
    state: Literal["unbound", "pending", "bound"]
    family: FamilySummary | None = None
    member: MemberView | None = None
    children: list[ChildView] = Field(default_factory=list)
    request: JoinRequestSummary | None = None


class InviteCreate(BaseModel):
    expires_in_hours: int = Field(default=24, ge=1, le=72)


class InviteView(BaseModel):
    id: str
    token: str | None = None
    share_path: str | None = None
    status: str
    expires_at: datetime


class InviteListItem(BaseModel):
    id: str
    status: str
    expires_at: datetime


class InvitePreview(BaseModel):
    family_name: str
    child_names: list[str]
    expires_at: datetime


class InviteTokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=120)


class JoinRequestCreate(BaseModel):
    token: str = Field(min_length=32, max_length=120)
    relationship_label: str = Field(min_length=1, max_length=30)


class JoinRequestView(BaseModel):
    id: str
    request_code: str
    status: str
    relationship_label: str
    role: str | None = None
    created_at: datetime
    decided_at: datetime | None = None


class JoinDecision(BaseModel):
    role: Role = "viewer"
    reason: str | None = Field(default=None, max_length=160)


class JoinRejection(BaseModel):
    reason: str | None = Field(default=None, max_length=160)


class MemberUpdate(BaseModel):
    role: Role | None = None
    relationship_label: str | None = Field(default=None, min_length=1, max_length=30)
