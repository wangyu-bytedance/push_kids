---
id: "ISS-20261031-REVIEW-STAGE-RETRY-BOUND"
type: issue
created: "2026-10-31"
updated: "2026-10-31"
status: resolved
source: ai-review
owner: Codex
severity: MAJOR
disposition: confirmed
observed_revision: "SPEC-20261031-KNOWLEDGE-POINT-PROMPT-02 uncommitted implementation before CR-001 fix"
source_evidence: "CR-001 in the 2026-10-31 read-only review for SPEC-20261031-KNOWLEDGE-POINT-PROMPT-02"
regression_case: "tests/unit/test_staged_analysis.py::test_quality_review_rejects_invalid_contract"
closure_evidence: "49 focused and 402 unit tests passed on 2026-10-31; Ruff, format, Mypy and architecture checks passed"
observation_evidence: "N/A: local-only backend change, not deployed"
prevention_control: "Each review position has one provider attempt; malformed review output fails after one call"
closure_reason: "Resolved locally; not closed because no cloud delivery or release observation exists"
---

# Review stage retry bound

## Impact and reproduction

- Scope: FEAT-001 staged analysis provider-call budget and fail-closed quality gate.
- Expected at most an initial review and one final review after correction. Before the fix, generic validation retry could allow two calls at each position, for four total reviews.
- Reproduction: return a structurally inconsistent `QualityReviewResult`; the shared `_call` loop treated `review` like `match`.
- No production or child-data impact: the implementation was uncommitted and not deployed.

## Root cause and escaped controls

- The generic retry policy distinguished only extraction/group from all other stages. The new review stage needed a stricter fail-closed policy.
- The approved Spec required at most two review calls. Read-only review found the mismatch before completion.

## Fix and verification

- Approved fix: `SPEC-20261031-KNOWLEDGE-POINT-PROMPT-02`; the product owner confirmed that generation failure and parent supplementation are preferable to unchecked output.
- `_call` now gives `review` one attempt; total stage-call ceiling is the proven bound of 18.
- Malformed pass/issue state and unknown aliases fail after one review call; semantic rejection permits exactly one correction and one final review.
- Verification: focused 49 passed; unit 402 passed; Ruff check/format, Mypy and architecture check passed.

## Closure and recurrence

- Confirmed and locally resolved. Closure remains pending cloud delivery/observation.
