from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.evaluate_analysis_quality import (
    CaseResult,
    _build_report,
    _ordered_cases,
)

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests" / "fixtures" / "analysis_quality" / "cases.json"


def _cases() -> list[dict[str, object]]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _results(
    cases: list[dict[str, object]],
    failures: dict[str, str] | None = None,
) -> list[CaseResult]:
    failures = failures or {}
    results = []
    for case in cases:
        subjects = case["subject"]
        expected = {subjects} if isinstance(subjects, str) else set(subjects)
        case_id = str(case["id"])
        results.append(
            CaseResult(
                case_id=case_id,
                expected=frozenset(expected),
                failure_code=failures.get(case_id),
                attempts=3 if case_id in failures else 1,
            )
        )
    return results


def _report(
    results: list[CaseResult],
    *,
    empty_pending_count: int = 0,
) -> dict[str, object]:
    return _build_report(
        results,
        empty_pending_count=empty_pending_count,
        remaining_pending_count=0,
        formal_write_count=0,
    )


def test_grouped_fixture_is_scheduled_as_stable_cross_subject_round_robin() -> None:
    ordered = _ordered_cases(_cases())
    ids = [str(case["id"]) for case in ordered]

    assert len(ids) == len(set(ids)) == 40
    assert ids == [
        "zh-01",
        "math-01",
        "en-01",
        "zh-02",
        "math-02",
        "en-02",
        "zh-03",
        "math-03",
        "en-03",
        "multi-01",
        "zh-04",
        "math-04",
        "en-04",
        "zh-05",
        "math-05",
        "en-05",
        "zh-06",
        "math-06",
        "en-06",
        "multi-02",
        "zh-07",
        "math-07",
        "en-07",
        "zh-08",
        "math-08",
        "en-08",
        "zh-09",
        "math-09",
        "en-09",
        "multi-03",
        "zh-10",
        "math-10",
        "en-10",
        "zh-11",
        "math-11",
        "en-11",
        "zh-12",
        "math-12",
        "en-12",
        "multi-04",
    ]


def test_analysis_failed_stays_in_end_to_end_but_not_subject_semantic_denominator() -> None:
    report = _report(_results(_cases(), {"zh-09": "analysis_failed", "zh-10": "analysis_failed"}))

    assert report["status"] == "passed"
    assert report["end_to_end"] == {"passed": 38, "total": 40, "rate": 0.95}
    assert report["operational_failure_count"] == 2
    assert report["operational_failure_codes"] == {"analysis_failed": 2}
    semantic = report["subject_semantic"]
    assert semantic["语文"] == {"passed": 13, "total": 13, "rate": 1.0}
    assert semantic["数学"] == {"passed": 15, "total": 15, "rate": 1.0}
    assert semantic["英语"] == {"passed": 15, "total": 15, "rate": 1.0}


@pytest.mark.parametrize(
    "failure_code",
    [
        "analysis_output_invalid",
        "subject.mismatch",
        "evidence.missing",
        "proposal.actionable_items",
    ],
)
def test_semantic_failures_reduce_both_end_to_end_and_subject_rates(
    failure_code: str,
) -> None:
    report = _report(_results(_cases(), {"zh-09": failure_code, "zh-10": failure_code}))

    assert report["status"] == "failed"
    assert report["end_to_end"] == {"passed": 38, "total": 40, "rate": 0.95}
    assert report["operational_failure_count"] == 0
    assert report["subject_semantic"]["语文"] == {
        "passed": 13,
        "total": 15,
        "rate": 0.8667,
    }


def test_zero_subject_semantic_denominator_rejects_gate() -> None:
    cases = _cases()
    failures = {
        str(case["id"]): "analysis_failed"
        for case in cases
        if "语文"
        in ({case["subject"]} if isinstance(case["subject"], str) else set(case["subject"]))
    }

    report = _report(_results(cases, failures))

    assert report["subject_semantic"]["语文"] == {"passed": 0, "total": 0, "rate": 0.0}
    assert report["status"] == "failed"


def test_report_contains_only_aggregate_fields_and_static_failure_metadata() -> None:
    report = _report(_results(_cases(), {"zh-09": "analysis_failed"}))

    assert set(report) == {
        "status",
        "case_count",
        "passed",
        "overall_rate",
        "end_to_end",
        "operational_failure_count",
        "operational_failure_codes",
        "subject_rates",
        "subject_semantic",
        "empty_pending_count",
        "remaining_pending_count",
        "formal_write_count",
        "failures",
    }
    assert report["failures"] == [{"case_id": "zh-09", "code": "analysis_failed", "attempts": 3}]
    encoded = json.dumps(report, ensure_ascii=False)
    for forbidden in ("material", "prompt", "keyword", "api_key", "secret"):
        assert forbidden not in encoded.lower()


def test_empty_pending_still_blocks_gate() -> None:
    report = _report(_results(_cases()), empty_pending_count=1)

    assert report["end_to_end"]["rate"] == 1.0
    assert report["status"] == "failed"
