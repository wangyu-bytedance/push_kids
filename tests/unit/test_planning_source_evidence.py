import json

import pytest
from push_kids.planning.service import _source_evidence


def test_source_evidence_uses_first_valid_confirmed_reference() -> None:
    payload = json.dumps(
        [
            {"source": "image", "image_index": 1, "detail": "  "},
            {"source": "parent_text", "image_index": None, "detail": "家长记录的原题文字"},
            {"source": "image", "image_index": 2, "detail": "后续证据"},
        ],
        ensure_ascii=False,
    )

    assert _source_evidence(payload) == ("家长记录的原题文字", None)


def test_source_evidence_keeps_summary_when_only_image_index_is_invalid() -> None:
    payload = json.dumps([{"source": "image", "image_index": 10, "detail": "练习册年龄题"}])

    assert _source_evidence(payload) == ("练习册年龄题", None)


@pytest.mark.parametrize("payload", [None, "", "not-json", "{}", "[1, null]"])
def test_source_evidence_degrades_untrusted_history(payload: str | None) -> None:
    assert _source_evidence(payload) == (None, None)
