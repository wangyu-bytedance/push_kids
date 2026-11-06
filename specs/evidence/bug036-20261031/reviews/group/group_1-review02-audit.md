# BUG-036 Group 1 Review02 incremental audit

- Date: 2026-10-31. Baseline: Group1 frozen Review01; target: `/private/tmp/push-kids-bug036-review-20261031/review02/snapshot/`, incremental diffs in `review02/diffs/`.
- Scope: original G1-01/G1-02/G1-03 fixes, shared public validation bridge, associated behavioral tests and affected direct legacy callers. Provider/failures/worker changes remain the other reviewer’s scope.
- All **9 Review02 manifest hashes matched**. Pipeline: `fd4c17b5bca2d2dd6289f06a98b49c5050ab77d45250bde0cdbe3527d07e0221`; contracts: `7524e52c4ffbc27e1127d54bb7ac33f676165d8f303961374ad68b959df25564`; stage_contracts: `250bae7912b1a686068659b384830aeb851e4ee49d4610bb7a32bfe06b15155e`.
- Followed original read-only review contract and bits-code-guard 3.1–3.4. No code/docs/tests edits, production DB, live model API or business API call. Only the two requested Review02 group outputs were written.
- **0 new confirmed defects.** `group_1-review02.jsonl` is empty. All three original findings are **fixed within reviewed generation scope**; this is not real-material semantic acceptance or cloud delivery.

## Original finding dispositions

| Finding | Disposition / exact Review02 refs | Verification |
|---|---|---|
| BUG036-G1-01 | fixed: pipeline.py:773–777 builds a server-owned immutable set only for reviewed current candidates with null final matching; contracts.py:337–342 accepts optional keyword with empty default; only same-day skip at430–431 and historical skip at443–448 consult the set | Frozen test covers explicit same-name reject and null match. Independent mixed-batch replay now returns both `十以内加法` and `十以内减法`, no Todo matches, uncertainties=[], exactly one reuse gate. Public default duplicate behavior remains unchanged. |
| BUG036-G1-02 | fixed: stage_contracts.py:152 defers identifiers to the transport contract; EXTRACT at181, MERGE at197 and REVIEW at214 retain no-database-ID requirements. prompt.py is byte-for-byte unchanged from Review01, retaining legacy valid-ID copying at36–37/45–47 and consuming the corrected shared rule | Legacy ANALYSIS_RULES no longer contains the contradictory prohibition. Existing fake-provider history/reference tests pass; shared quality/history/few-shot composition remains. No live model accuracy inference. |
| BUG036-G1-03 | fixed: pipeline.py:503 raises only at420 global aliases, derived from200same-day+120today+100history. Existing per-candidate320 check at562–563 and512KiB bound_history_payload at527–534 remain | New valid cross-subject behavioral test constructs200same-day/120today and40history over2queries, verifies360global options and180per candidate, and produces two current proposals. Other bound/query/call tests pass. |

The verified-new set is not part of `AnalysisInput`, `AnalysisProposal` or `ModelAnalysisResult` fields/transport Schema, and no model-provided field forwards into it. The only production caller providing the keyword is the staged pipeline. Direct legacy callers in providers.py:361/777 omit it and retain empty-default semantics. A null match represents the validated matching stage’s explicit non-equivalence decision; uncertain results still fail before assembly. Accepted reused candidates are excluded from the set and remain on their existing reference/identity-validation path.

## Per-file necessity and placement

| File / incremental diff | Necessity | Placement and evidence |
|---|---|---|
| pipeline.py +16/-2 | necessary: carry validated new decisions and restore prior valid aggregate capacity; extra static reuse failure trace is consistent with existing diagnostics | correct orchestration owner; set has no raw IDs or model-controlled transport field; G1-01/G1-03 fixes are bounded. No duplicate policy or new business writer. |
| contracts.py +8/-3 | necessary public-validator bridge: without it final name-only filtering overturns approved non-equivalence | correct owner of existing duplicate validation; keyword-only frozenset empty default changes only two skip conditions. Public DTO/Schema unchanged. Foreign references, review references, subject, evidence, context, summary and actionable gates retain their prior checks. |
| stage_contracts.py +6/-4 | necessary removal of conflicting shared transport permission | correct contract owner; reusable knowledge/history/field constraints remain shared and alias-only stages own their identifier prohibition. |
| prompt.py +0/-0 | unchanged source, affected through shared OUTPUT_RULES import | correct consumer; no direct patch needed for G1-02. SHA matches Review01. |
| test_staged_proposal_recovery.py +85/-4 | necessary regression correction/additions | correct unit placement; formerly tolerated same-name failure now requires retained proposal; explicit reject and360-option outcomes independently fail on original wrong behavior. No permanent test edits made by reviewer. |
| test_provider_evidence.py +1/-0 | necessary direct conflicting-rule assertion | correct unit placement; string absence establishes removal of a source contradiction only. Existing legacy fake provider tests supply independent output/reference compatibility checks. |

All changed scoped files are necessary; none is misplaced or unnecessary. No further safe-deletion item or unowned abstraction was identified. Incremental runtime facts still require implementer documentation closure after the real retest; Review01 audit lists affected Feature/Behavior/Architecture/Spec/evidence sources.

## Executed evidence

All checks used `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python`. To run frozen code, inserted repository `apps/api/src`, then prepended the Review02 snapshot and Review01 snapshot to `push_kids.agent_processing.__path__` before importing task modules. Review02 supplies changed files; Review01 supplies the other frozen BUG-036 modules. Test adapters remain in repository test-only package. No DB fixture or real provider client was used.

1. Frozen relevant unit suite with pytest `-c /Users/bytedance/Documents/push_kids/pyproject.toml -p no:cacheprovider -q`: Review02 staged_proposal_recovery/provider_evidence; Review01 staged_analysis/analysis_context_contract; unchanged repository subject_grouped_analysis/structured_analysis_output. **129 passed, 1 dependency deprecation warning in2.17s.** Warning: Starlette’s current httpx TestClient import is deprecated; no test failed. This is this reviewer’s executed result; the implementer’s reported139 and8Red→Green remain separate evidence, not claimed as rerun here.
2. Independent mixed replay: Review02 HistoryReview(reject), delegates extract/merge to TwoTargets, quality passes both current objects; history name=`十以内加法`, skill=`主动回忆`, current=`变式练习`. Result points=`['十以内加法','十以内减法']`, matches=[], uncertainties=[], reuse_count=1. Both same-name and unrelated targets survive.
3. Compared `AnalysisInput.model_json_schema()`, `AnalysisProposal.model_json_schema()` and `ModelAnalysisResult.model_json_schema()` with baseline contracts.py loaded independently: **all exactly equal**.
4. Direct default compatibility: identical-name new item with either historical or same-day context still raises `proposal.actionable_items` without the keyword. With server-generated verified-new key the current new item is retained. This isolates the change to opted-in staged semantics.
5. Direct adversarial validation with verified-new key still rejects **unknown linked knowledge ID**, **new item with review ID**, **foreign context record**, **blank evidence detail**, **image reference without available image**, and **existing linked knowledge from the wrong subject** with their original validation categories. Key membership does not suppress these validators. Reused item branch is unchanged and does not consult the set.
6. Verified Review02 manifest:9 entries,0 mismatches.

These behaviors were checked with in-memory synthetic data and fake provider clients. Model fields remain untrusted and are checked through the existing schema/reference boundaries. The set itself is produced by the server after full candidate/review/match validation; no transport accepts it.

## Remaining acceptance and closure limits

- Formal learning confirmation’s normalized identity behavior remains the old contract and is **unchanged/outside this generation task**. The review proves correct editable proposal outcomes, not creation of distinct formal identities for identical names. No formal transaction or parent confirmation was executed.
- Same30-source Doubao retest, C1–C6 content judgments, original6PASS preservation and no-write source audit: **NOT_RUN by reviewer**. The now-passing orchestration fakes cannot substitute for model/content acceptance.
- Provider/checkpoint/worker/telemetry secondary changes, full backend/static checks and release gates are outside this group’s executed evidence; other reviewer/implementer owns them.
- Current-state docs remain a closure requirement: accurately record local -07/-11 behavior, omission/reuse/capacity contracts and these fixed finding dispositions; do not convert older038 delivery or reported tests into current-version acceptance.
- No current cloud delivery evidence: BUG-036 remains active; Review02 and local tests do not authorize DONE/completed or deployment. No new product/Spec decision was identified in this scoped fix.
