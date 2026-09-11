import pytest
from push_kids.platform.pagination import decode_cursor, encode_cursor


def test_cursor_round_trip_is_scope_bound() -> None:
    scope = ("submissions", "family-a", "child-a", "pending")
    anchor = {"created_at": "2026-09-11T08:00:00+00:00", "id": "submission-20"}

    token = encode_cursor(scope, anchor)

    assert decode_cursor(token, scope) == anchor
    with pytest.raises(ValueError, match="分页已失效"):
        decode_cursor(token, ("submissions", "family-a", "child-b", "pending"))


@pytest.mark.parametrize("token", ["", "not-base64", "e30=", "a" * 1501])
def test_cursor_rejects_malformed_or_oversized_values(token: str) -> None:
    with pytest.raises(ValueError, match="分页已失效"):
        decode_cursor(token, ("activity-records", "family-a", "child-a"))
