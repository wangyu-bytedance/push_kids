from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChannelView(BaseModel):
    available: bool
    reason: str = ""
    # Template ids the client must pass to wx.requestSubscribeMessage, in a stable order.
    template_ids: list[str] = Field(default_factory=list)
    # True only when WeChat granted a long-term template; otherwise each grant sends one message.
    long_term: bool = False


class PreferenceView(BaseModel):
    type: str
    label: str
    description: str
    enabled: bool
    managers_only: bool
    template_id: str | None = None
    subscription_status: str
    remaining_quota: int
    previously_granted: bool = False


class NotificationSettingsView(BaseModel):
    channel: ChannelView
    preferences: list[PreferenceView]
    last_sent_at: datetime | None = None


class PreferenceUpdate(BaseModel):
    type: str
    enabled: bool


class SubscriptionResult(BaseModel):
    """One entry of the wx.requestSubscribeMessage result, mapped back to a reminder type."""

    type: str
    accepted: bool


class SubscriptionRegister(BaseModel):
    results: list[SubscriptionResult] = Field(min_length=1, max_length=10)


ReminderType = Literal["review_digest", "schedule_reminder", "member_application"]
GrantDecision = Literal["accept", "reject", "cancel", "ban", "filter", "technical", "unknown"]


class RenewalUpdate(BaseModel):
    choice: Literal["enabled", "disabled"]
    expected_version: int = Field(ge=0)


class RenewalTypeView(BaseModel):
    type: str
    status: str
    consented: bool
    cooldown_remaining: int
    active_attempt_id: str | None = None


class RenewalView(BaseModel):
    settings: NotificationSettingsView
    choice: str
    version: int
    completion_cursor: int
    types: list[RenewalTypeView]
    server_time: datetime


class GrantPrepare(BaseModel):
    mode: Literal["auto", "onboarding", "manual"]
    types: list[ReminderType] = Field(min_length=1, max_length=3)
    expected_version: int = Field(ge=0)
    main_switch: bool | None = None
    remembered: dict[ReminderType, Literal["accept", "reject"]] = Field(default_factory=dict)


class GrantOutcome(BaseModel):
    type: ReminderType
    decision: GrantDecision


class GrantRegister(BaseModel):
    results: list[GrantOutcome] = Field(min_length=1, max_length=3)
    enable_renewal: bool = False


class GrantBindingView(BaseModel):
    type: str
    template_id: str


class GrantAttemptView(BaseModel):
    attempt_id: str
    mode: str
    state: str
    expires_at: datetime
    bindings: list[GrantBindingView]
    result: GrantRegister | None = None


class GrantPreparationView(BaseModel):
    attempt: GrantAttemptView | None
    renewal: RenewalView


class DeliveryView(BaseModel):
    type: str
    state: str
    headline: str
    detail: str
    scheduled_at: datetime
    sent_at: datetime | None = None
    result_code: str | None = None


class DispatchReport(BaseModel):
    queued_member_applications: int = 0
    queued_schedule_reminders: int = 0
    queued_review_digests: int = 0
    refreshed: int = 0
    cancelled: int = 0
    sent: int = 0
    skipped: int = 0
    retried: int = 0
    failed: int = 0
    # Queued for a member who has since left the family.
    dropped: int = 0
    # Members whose channel was cut because membership ended.
    revoked: int = 0
    # Delivery history removed past the retention window.
    pruned: int = 0
