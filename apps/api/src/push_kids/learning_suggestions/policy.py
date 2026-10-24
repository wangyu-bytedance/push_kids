"""Pure natural-day eligibility; learning duration is not a review budget."""

from datetime import date, timedelta


def eligibility(context: dict, today: date, *, enabled: bool, pending: bool = False) -> str:
    if pending:
        return "pending"
    if not enabled:
        return "disabled"
    if not context.get("active"):
        return "inactive"
    if not context.get("grade"):
        return "missing_grade"
    if not context.get("subjects"):
        return "no_subject"
    if not context.get("knowledge"):
        return "no_history"
    observed = context.get("observed_since")
    # The partial day when observation begins cannot prove a whole quiet day.
    if not observed or date.fromisoformat(observed) >= today - timedelta(days=2):
        return "warming_up"
    last = context.get("last_new_confirmed_on")
    if last and date.fromisoformat(last) >= today - timedelta(days=2):
        return "recent_new"
    return "eligible"
