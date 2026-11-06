# BUG-036 Group 1 Review03 prompt-contract audit

- Date: 2026-10-31. Final bounded default review round; no further review/fix loop initiated.
- Authority: approved `BUG-SPEC-20261031-KNOWLEDGE-GENERATION-01`, `ARCH-20261031-KNOWLEDGE-GENERATION-01`, AC-005 and TP-005/010. Read the Review03 frozen Spec, incremental diffs, complete affected stage/legacy compositions, REVIEW.md and applicable bits-code-guard 3.1–3.4/dimension/severity rules. Python has no separate language-specific supplement in that workflow.
- Base: Review02 implementation, not git HEAD. Target: `/private/tmp/push-kids-bug036-review-20261031/review03/{snapshot,diffs,manifest.json}`. Diff files use flattened `__` paths and `.py.diff` names; initial nonexistent nested-path reads were corrected after listing the actual inventory and did not affect review scope.
- **0 confirmed introduced defects.** `group_1-review03.jsonl` is empty. No resolved original finding is repeated. This is a source/prompt-contract conclusion, not content-generation acceptance.
- No production/docs/tests edits, subagents, DB, live model/provider API or real30case content evaluation. Only the two requested Review03 group reports were written.

## Exact frozen evidence

All5 manifest entries were independently SHA-256 verified; current workspace matched each frozen file with0 mismatches.

| Manifest file | SHA-256 |
|---|---|
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` | `e9ad60dc39520423da3b2f9857f3dec5ea89c379a0b9bd9d62b5b53a2bb68a7e` |
| `apps/api/src/push_kids/agent_processing/prompt.py` | `cbeee804ce78ad21a55d223583a74386531640a8562ba3c78f397ebb16e33cf7` |
| `tests/unit/test_provider_evidence.py` | `c838a64e59da30e22318b2e5471dc1b0cfce7fcd8af49e31c781a38d80fee6cc` |
| `tests/unit/test_staged_analysis.py` | `afd655c1e8cf31d9e0bf39b7346517336343a3723423bad2f9d36a0132a6ecd7` |
| `specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md` | `d3a799d2126287c7ddb46d321539bd8f661d7d9c075a6df6f20f9f4cd9331474` |

Pipeline revision changes from07to08 in stage_contracts.py:11; legacy prompt revision changes from11to12 in prompt.py:10. These changes invalidate preceding stage caches through the existing imported revision/digest contract. Other Review02 implementation, internal/public DTOs, query/count/checkpoint/token budgets and parent-confirmation behavior remain unchanged.

## Per-file necessity and placement

| File / action | Necessity | Placement / evidence / limits |
|---|---|---|
| stage_contracts.py / modify | necessary within AC-005/TP-005/010: clarify evidence/real-object/merge-priority/readability/finite-sequence boundaries after the recorded same30 feedback; bump revision so the old rules cannot supply cache results | correct authoritative stage-rules owner. Shared evidence rules and role-specific review rules are composed once. Additional examples remain at the end. No feature flag, new provider, new DTO or hardcoded30-case answer mapping. Actual model behavior is unverified here. |
| prompt.py / modify | necessary matching legacy revision update for shared-rule consumption | correct existing legacy transport owner; its ID-emitting contract remains intact. Only revision literal changes in this file’s direct diff. |
| test_staged_analysis.py / modify | necessary current revision assertion update | correct unit placement. Existing rules-once/end-of-prompt and orchestration tests still run; this change itself is a revision assertion, not a new semantic regression test. |
| test_provider_evidence.py / modify | necessary current legacy revision assertion update | correct unit placement; existing no-conflicting-ID requirement and source/schema tests remain. This assertion cannot prove real content quality. |
| approved BUG-036 Spec / read current version | necessary source of approved scope and actual increment/verification status | records08/12 refinement as TP-005/010 feedback within the approved contract, preserves first-run outcomes, no cloud delivery and pending content acceptance. Existing07/11 implementation and test statements are prior-step facts; main thread must reconcile final current facts/evidence after the last retest. No reviewer edits or fact certification of the supplied832PASS claim. |

All four changed implementation/test files are necessary and correctly placed. No wholly questionable/unnecessary file, misplaced new abstraction, dead path or safe deletion candidate was confirmed. No broader behavior/API/data/architecture changes were introduced by this increment.

## Contract review conclusions

**Evidence and subject boundaries.** stage_contracts.py:105–111 distinguishes incidental numbers/time/objects in prose from explicit teaching or parent-provided learning evidence. Parent text cannot be claimed as image contents; missing audio/video/conditions/answers remain unsupported. Added partial-readability rules at146–151 retain clearly identifiable objects, keep ambiguity/confidence visible and do not convert guesses into known characters. EXTRACT at200–207 still uses only given subjects/material aliases and reserves unreadable for unusable material under the composed narrower rule. Fully failed source extraction still fails through the existing pipeline; this increment does not permit publishing a partial draft from a failed original source.

**Finite-sequence precision.** New119–120 explicitly allows concrete visible objects/sequence/relation conditions when a complete numerical range cannot be established, and prohibits promoting a finite sequence into an unsupported full odd/even set or broader range. This is consistent with existing117–118 prohibition on deriving a full range from isolated examples and with the final historical exact-range requirement. Naming an observed adjacent-difference relation is not permission to output missing answers or infer an unobserved infinite continuation; output rules still prohibit answers/unsupported content.

**New integration vs history equivalence.** New136–142 prioritizes the actual complete teaching/checking target over coarse review_method/category/page/exercise labels. Companion letter/word objectives, word relations and a taught grammatical structure can share a check; independently taught reading/writing with different objects or completion checks may remain separate. Existing131–144 still requires compatible supported scope, a common concrete check, independent rules kept apart and1–5minutes. MERGE at216–224 expressly distinguishes new-proposal consolidation from strict historical equivalence. HISTORY_RULES at172–180 is unchanged and still requires exact core/object/range/condition/skill equality; it appears only in MATCH/REUSE stage compositions. The new-proposal examples do not grant looser history matching or a server same-name bypass.

**Quality review.** REVIEW at235–250 keeps precise i/o/member issue mapping, bounded basis, no renaming, no historical query, omission review and prior-review correspondence. Added237–239 correctly permits candidate evidence as a source summary rather than demanding verbatim quotes. Added245–246 rules out conflicting merge/split requirements for the same complete group while permitting identified independent partial targets. The≤40-character core-basis guidance is stricter than, and satisfiable within, the unchanged80-character Schema cap; it does not alter the schema or authorize losing evidence. Summary/uncertainty at165–169 describes learning/material facts rather than internal candidate counts/aliases or runtime errors.

**Composed prompt placement and identity compatibility.** Independently checked all5 EXTRACT/MERGE/REVIEW/MATCH/REUSE values and legacy ANALYSIS_RULES: each contains exactly one full KNOWLEDGE_RULES and ends with the complete KNOWLEDGE_EXAMPLES. New examples7/8 at193–195 are last, after the general rules and existing6examples, with explicit rule/Schema priority at184. They calibrate a letter/companion-word case and a word-relation case, including a separate-check counterexample. The prompt body is not an input/output answer table. Legacy still copies provided existing_knowledge_id/review_id atprompt.py:36–37/45–47; shared OUTPUT_RULES at168 defers identity representation to the transport. Stage-specific alias-only rules still forbid arbitrary database IDs. No reintroduction of original G1-02 conflict found.

**Scope.** These are refinements of already approved evidence/granularity/uncertainty/strict-history rules under AC-005 and required TP-005/010 feedback. No automatic formal writes, grading/mastery/next-lesson policy, tenant control, deterministic review-date logic, visible frontend, storage migration, additional loop, new output authority or relaxed test standard appears in the diff. They remain closed versioned prompt rules; no new extensibility boundary is introduced.

## Independently executed checks

Commands used `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python`. Loaded changed modules from Review03, then Review02 and Review01 frozen package paths. No production fixture or real model client was selected.

- Frozen Review03 `test_staged_analysis.py`, `test_provider_evidence.py` and unchanged Review02 `test_staged_proposal_recovery.py`, via pytest `-c /Users/bytedance/Documents/push_kids/pyproject.toml -p no:cacheprovider -q`: **71 passed in2.93seconds**.
- Independently loaded Review02 stage_contracts and compared all11 internal DTO schemas with Review03: **all exactly unchanged** (ExtractedPoint, MaterialResult, MergedPoint, OmittedCandidates, ConsolidatedResult, MatchDecision, MatchingResult, QualityIssue, QualityReviewResult, ReuseDecision, ReuseReviewResult).
- All5 stages and legacy: shared rules exactly once, examples last. HISTORY_RULES appears in MATCH/REUSE and not EXTRACT/MERGE/REVIEW. Legacy does not contain the stage-only no-DB-ID prohibition and still requires trusted-ID copying. PASS.
- All5 manifest hashes and current-workspace comparisons matched. PASS.

Passing assertion/fake tests verify composition, revisions, schema compatibility and bounded mechanics. They do not establish the semantic success of partial handwriting extraction, companion-object merging, finite sequences, or the same30cases.

## Evidence limits and final closure

- No real30-case content was opened, scored or generated by this reviewer; TP-005/010 semantic outcomes, original6PASS preservation, non-example holdout behavior and first/latest30 comparisons remain main-thread responsibilities. Do not use71PASS or0source findings as content acceptance.
- The quality review actually receives candidate summaries/material aliases, not raw images or the extraction excerpt dictionary in its normal review payload. New excerpt wording at237 does not add those inputs; source-summary review remains an existing visibility limit. This review does not claim the model can independently verify all extraction details from the original source. Real-source content evaluation is still necessary. No deterministic introduced failure from that descriptive wording was established.
- Existing queue/local simultaneous-expiry labeling and downstream formal confirmation normalized identity remain prior documented limits, unchanged in Review03. No re-review of resolved original5 findings was required beyond confirming this increment does not alter their code paths.
- Main thread must reconcile current Feature/Behavior/Architecture/Spec/prompt-evidence/test/release facts to08/12 and preserve07/11 first-retest results as historical evidence. The frozen Spec still intentionally records earlier implementation/test facts plus the increment; final tests/content/cleanup and pending statuses must be updated from actual last-run evidence.
- No matching08/12 cloud delivery: development remains in active/VERIFYING, and this review does not authorize DONE/completed, deployment, native/device acceptance or business data changes. No further default review/fix round was started.
