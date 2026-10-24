import pytest
from push_kids.notifications.renewal_policy import auto_eligible, renewal_status


@pytest.mark.parametrize("completed,status", [(0, "cooldown"), (9, "cooldown"), (10, "ready")])
def test_completion_boundary(completed, status):
    value = renewal_status(
        available=True,
        enabled=True,
        quota=0,
        consented=True,
        choice="enabled",
        completed=completed,
        last_prompt=0,
        stop_reason=None,
        pending=False,
    )
    assert value == status
    assert auto_eligible(status=value, remembered=None, main_switch=True, retry_ready=True) == (
        completed >= 10
    )
    assert auto_eligible(status=value, remembered="accept", main_switch=True, retry_ready=True)


@pytest.mark.parametrize("quota", [-1, 1, 50])
def test_positive_or_long_term_quota_never_renews(quota):
    value = renewal_status(
        available=True,
        enabled=True,
        quota=quota,
        consented=True,
        choice="enabled",
        completed=100,
        last_prompt=0,
        stop_reason=None,
        pending=False,
    )
    assert value == "has_quota"
    assert not auto_eligible(status=value, remembered="accept", main_switch=True, retry_ready=True)


@pytest.mark.parametrize(
    "status",
    [
        "off",
        "disabled",
        "pending",
        "needs_consent",
        "unavailable",
        "ban",
        "filter",
        "remembered_reject",
        "main_switch_off",
    ],
)
def test_remembered_allow_never_overrides_hard_stops(status):
    assert not auto_eligible(status=status, remembered="accept", main_switch=True, retry_ready=True)


@pytest.mark.parametrize(
    "main,remembered,retry",
    [(False, "accept", True), (True, "reject", True), (True, "accept", False)],
)
def test_device_and_technical_stops(main, remembered, retry):
    assert not auto_eligible(
        status="ready", remembered=remembered, main_switch=main, retry_ready=retry
    )
