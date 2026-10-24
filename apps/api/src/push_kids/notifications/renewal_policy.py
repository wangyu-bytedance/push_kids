"""Closed renewal rules; no framework, storage, provider or device dependencies."""

COOLDOWN_COMPLETIONS = 10
LEASE_SECONDS = 60


def renewal_status(
    *,
    available: bool,
    enabled: bool,
    quota: int,
    consented: bool,
    choice: str,
    completed: int,
    last_prompt: int,
    stop_reason: str | None,
    pending: bool,
) -> str:
    if not available:
        return "unavailable"
    if not enabled:
        return "disabled"
    if pending:
        return "pending"
    if quota == -1 or quota > 0:
        return "has_quota"
    if not consented:
        return "needs_consent"
    if stop_reason:
        return stop_reason
    if choice != "enabled":
        return "off"
    if completed - last_prompt < COOLDOWN_COMPLETIONS:
        return "cooldown"
    return "ready"


def auto_eligible(
    *, status: str, remembered: str | None, main_switch: bool | None, retry_ready: bool
) -> bool:
    if main_switch is False or remembered == "reject" or not retry_ready:
        return False
    return status == "ready" or (status == "cooldown" and remembered == "accept")
