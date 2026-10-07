import json

import pytest
from push_kids.agent_processing.contracts import EvidenceReference, ModelEvidenceReference
from push_kids.planning.service import _confirmed_source_evidence, _source_evidence
from pydantic import ValidationError


def test_source_evidence_uses_first_valid_confirmed_reference() -> None:
    payload = json.dumps(
        [
            {"source": "image", "image_index": 1, "detail": "  "},
            {"source": "parent_text", "image_index": None, "detail": "家长记录的原题文字"},
            {"source": "image", "image_index": 2, "detail": "后续证据"},
        ],
        ensure_ascii=False,
    )

    assert _source_evidence(payload) == ("后续证据", 2)


def test_source_evidence_keeps_summary_when_only_image_index_is_invalid() -> None:
    payload = json.dumps([{"source": "image", "image_index": 10, "detail": "练习册年龄题"}])

    assert _source_evidence(payload) == ("练习册年龄题", None)


@pytest.mark.parametrize("payload", [None, "", "not-json", "{}", "[1, null]"])
def test_source_evidence_degrades_untrusted_history(payload: str | None) -> None:
    assert _source_evidence(payload) == (None, None)


@pytest.mark.parametrize("index", [0, -1, 10, True, "2", 2.5])
def test_invalid_image_indices_are_not_coerced(index):
    for model in (EvidenceReference, ModelEvidenceReference):
        with pytest.raises(ValidationError):
            model(source="image", image_index=index, detail="合成题目")
    assert _source_evidence(
        json.dumps([{"source": "image", "image_index": index, "detail": "题目"}])
    ) == ("题目", None)


def test_source_submission_must_prove_the_stored_image_evidence():
    evidence = [{"source": "image", "image_index": 2, "detail": "A提交的题目"}]
    proposal = json.dumps({"knowledge_points": [{"name": "年龄题", "direct_evidence": evidence}]})
    assert _confirmed_source_evidence(json.dumps(evidence), "A", "年龄题", proposal) == (
        "A提交的题目",
        2,
    )
    later = [{"source": "image", "image_index": 2, "detail": "B提交的其他题目"}]
    assert _confirmed_source_evidence(json.dumps(later), "A", "年龄题", proposal) == (None, None)
    assert _confirmed_source_evidence(json.dumps(evidence), "A", "其他知识", proposal) == (
        None,
        None,
    )
    assert _confirmed_source_evidence(json.dumps(evidence), None, "年龄题", proposal) == (
        None,
        None,
    )


def test_text_summary_also_requires_the_original_confirmed_source():
    evidence = [{"source": "parent_text", "detail": "A的原文"}]
    proposal = json.dumps({"knowledge_points": [{"name": "加法", "direct_evidence": evidence}]})
    assert _confirmed_source_evidence(json.dumps(evidence), "A", "加法", proposal) == (
        "A的原文",
        None,
    )
    later = [{"source": "parent_text", "detail": "B的原文"}]
    assert _confirmed_source_evidence(json.dumps(later), "A", "加法", proposal) == (None, None)
