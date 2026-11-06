# BUG-036 Review02 — runtime findings re-review

- Date: 2026-10-31. Read-only incremental group 2 review; no delegation.
- Contract: approved BUG-SPEC-20261031-KNOWLEDGE-GENERATION-01, AC-003/004/007; original REVIEW policy and bits-code-guard 3.1–3.4 remain applicable.
- Evidence: `/private/tmp/push-kids-bug036-review-20261031/review02/{diffs,snapshot,manifest.json}`. Compared Review01 → Review02 diffs, then complete changed functions and direct consumers. Git HEAD was not used.
- Snapshot and working-tree SHA-256 matched for failures, worker, pipeline, contracts and the two consulted unit test files before execution.
- Result: **0 new confirmed findings**; `group_2-review02.jsonl` is empty. The original two findings are fixed within the approved AC-004/007 scope.

## Original finding dispositions

| Original finding | Disposition | Concrete Review02 evidence |
| --- | --- | --- |
| Group2-01, P1 numeric schema-path conversion/retention | fixed | `failures.py:89` preserves loc types before string conversion. Only real integer indexes 0–199, excluding bool, or closed known field names survive. Any omitted loc component collapses the whole path to stage.fields. `safe_stage_diagnostics` bounds serialized index length to at most3 before int(), preventing the previous conversion exception. Synthetic unknown strings of1/100/5000 zeroes all collapse to stage.fields:extra_forbidden; a5000-digit serialized index is rejected without conversion failure. Existing real list-index/name diagnostics continue through the same whitelist. |
| Group2-02, P2 new-stage durable error metadata loss | fixed | `worker.py:68` uses StageFailure.diagnostics and preserves `.codes` for other error classes. Closed stage/unit lists cover review0/review1, merge-correction and reuse plus internal static unit labels. Metadata is emitted before bounded validation codes, preserving location when the300-character limit clips code detail. `pipeline.py:692` emits a static reuse/reuse validation failure trace before raising post-call uncertainty; model basis/content is excluded. Synthetic reuse/review1/merge-correction diagnostics preserve location and safe schema code. |

## Incremental per-file audit

| File/change | Necessity | Placement | Redundancy / unintended effects |
| --- | --- | --- | --- |
| `agent_processing/failures.py` — modify | necessary: malformed untrusted numeric field names previously defeated the intended local correction and bounded diagnostic contract. | correct: central closed schema-error carrier and sanitizer. | Fix replaces the unsafe conversion; no alternate sanitizer introduced. String keys can no longer masquerade as integer loc indexes. Three-digit textual index acceptance is bounded, including any leading-zero spelling; actual model string keys still collapse. |
| `agent_processing/worker.py` — modify | necessary: new failures/diagnostics must reach the existing durable Job error owner. | correct: durable failure rendering owns compatibility and300-character storage boundary. | StageFailure uses its new validated property; AnalysisOutputExhaustedError/AnalysisOutputValidationError still use codes and unknown values become validation.other. The ordering change does not alter non-StageFailure diagnostic strings or public Submission messages. Static unit regex is closed and cannot echo arbitrary model paths/content. |
| `agent_processing/pipeline.py` — modify, runtime subset | necessary: post-call reuse uncertainty needs an explicit safe trace; other Review02 history/verified-new changes are reviewed independently by group1. | correct: orchestration knows the completed semantic stage and deterministic failure location. | Added log contains only event/stage/unit/revision/static reason. No basis, payload, prompt or child/model content added. Request-slot/deadline behavior is unchanged in this incremental fix. |
| `tests/unit/test_stage_provider.py` — modify | necessary: numeric0/100/5000 regressions catch both type confusion and conversion failure; safe worker test checks new durable metadata. | acceptable: numeric boundary belongs to provider validation; worker rendering test is a direct no-DB helper check adjacent to provider failure contracts. | Tests fail on the old code and use independent expected safe path/metadata. Existing extra-field/list-index tests remain meaningful. No redundant production helper or low-value mirror suite added. |

Consulted context: complete current schema-diagnostic/trace renderer, StageFailure and old `.codes` error classes, direct worker persistence caller, provider ValidationError consumer, existing worker resilience safe-log/durable-code tests, and the frozen reuse-uncertainty path. `contracts.py`, `stage_contracts.py`, prompt changes and semantic tests in the Review02 bundle are principally group1 scope; group2 does not claim an independent semantic review of those edits.

All four runtime/test files audited here are necessary; placement is correct or acceptable. No wholly questionable/unnecessary file, misplaced production logic, dead helper or safe deletion candidate was identified. No code/test/doc implementation file was edited by this reviewer.

## Independent verification

Ran:

```text
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python -B -m pytest tests/unit/test_stage_provider.py tests/integration/test_worker_resilience.py::test_worker_persists_only_safe_internal_validation_diagnostic tests/integration/test_worker_resilience.py::test_failed_stage_log_contains_only_safe_diagnostics -q -p no:cacheprovider --basetemp=/private/tmp/push-kids-bug036-review-20261031/group/group_2-review02-pytest-tmp
```

Result: **22 passed**, one existing Starlette/httpx deprecation warning,0.90 seconds. Explicit local fixtures use sqlite:///:memory: and temporary media; no production database or model API was accessed.

Additional direct no-DB/no-API synthetic checks confirmed:

- Unknown model numeric strings of lengths1/100/5000 all return stage.fields:extra_forbidden.
- A serialized5000-digit numeric path is rejected without ValueError.
- reuse/reuse, review/review1 and merge/merge-correction preserve static stage/unit and stage.decisions.match:reference within300 characters.
- Both old `.codes` classes, AnalysisOutputExhaustedError and AnalysisOutputValidationError, retain history_search.incomplete and collapse an unknown synthetic code to validation.other; unknown text does not survive rendering.

Parent-reported139 targeted PASS and observed Red→Green are implementation evidence, not an independent reviewer execution. Full backend/static gates were not rerun in this group. New reuse trace safety is verified from its closed literal fields; this group did not construct another persisted maximum Job/provider E2E.

## AC-003 deadline masking assessment

The original Review01 synthetic busy-slot observation remains: exact absolute expiry through `_call` can be categorized local_deadline by the enclosing timeout instead of queue_deadline by the provider. Pipeline and provider use the same absolute deadline, so both expiry conditions are true. No independent queue-duration budget is consumed, and the classification does not cause earlier termination, bypass a still-valid45/30 execution allowance, alter retry disposition, publish partial output or leak a request slot.

This is **not a functional/resource blocker** for this fix. It remains an observability acceptance limitation under AC-003's requirement to distinguish queue, execution and overall expiry. Documentation/evidence should explicitly retain the exact-expiry classification ambiguity; do not claim every production orchestration queue expiry is separately labeled. If strict categorical distinction is later required, add an integrated phase/queue-state test and adjust the timeout owner's reporting. No additional confirmed severity is assigned for the unchanged coincident-deadline behavior.

## Remaining closure and evidence

The prior per-file audit and document closure table still apply. Synchronize verified local staged-07 rules/budgets/cache and corrected diagnostic facts into FEAT-001, BHV-032/BHV-003, architecture, test strategy, Spec/evidence and indexes while preserving historical038 delivery facts. Keep actual skipped/unverified gates explicit. The fixed30 original-source content evaluation, cleanup/read-only fingerprint evidence, final full/static checks and any maximum persisted-job/model E2E remain separate from this re-review. Matching cloud delivery is absent; BUG-036 remains active, with development/acceptance status recorded honestly. No deployment/native-device acceptance is claimed.
