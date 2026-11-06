# BUG-036 bounded evidence-premise experiment review

- Date: 2026-10-31. Baseline: Review03 -08/-12. Target: `review04-evidence-premise/{snapshot,diffs,manifest.json}`, -09/-13.
- Method: read approved Spec acceptance/experiment note and actual rules first, then applied bits-code-guard general-workflow3.1–3.4, review-dimensions/review-rule and REVIEW.md. Reviewed changed lines, complete composed stage/legacy prompts and the directly affected existing alias/duplicate/correction validators. Python has no language supplement in that workflow.
- Authorization boundary: Spec metadata explicitly states the new falsifiable premise, scope under existing AC-001/002/005, and budget of one same30source run,6synthetic boundaries and one independent incremental review. This review is that one bounded review beyond the prior default rounds; no additional agent or follow-up loop was started.
- **0 confirmed introduced defects.** `group_1-evidence-premise.jsonl` is empty. This conclusion covers source/prompt contracts, not real30case or holdout content quality.
- No implementation/docs/tests edits, model/database/business API calls or cleanup. Original/new source directories were not inspected or modified. Only the requested review result files were written.

## Exact snapshot binding

All5 manifest entries matched their frozen bytes and current workspace;0 mismatches.

| File | SHA-256 |
|---|---|
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` | `e616952181fff6eebee1a3d21c5a16c157fe351dc0681d50ce42eeb498803179` |
| `apps/api/src/push_kids/agent_processing/prompt.py` | `61152c25593aee2665a6ae59bb489e90b9b031bc48df69a24892e82fea242823` |
| `tests/unit/test_staged_analysis.py` | `fd82d98280a94d25d06dc3681635701a48f5c02c8c8608fc140ebec1165bc158` |
| `tests/unit/test_provider_evidence.py` | `2e90a983dbb990800f21631370ec83bff6ee9ef3298283b30549a72e9e2ae204` |
| `specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md` | `29881b71f47a13830eb7aa4c5a9fa391e5ea2ba8b13b2ec52dee9486f5bd40fb` |

Revision literals at stage_contracts.py:11 and prompt.py:10 now identify09/13. Existing imported pipeline revision invalidates08checkpoint/digest reuse. The11internal DTO schemas, strict historical rules,8examples, Provider budgets and implementation dependency/call boundaries remain unchanged.

## Per-file necessity and placement

| File / action | Necessity | Placement / residue / evidence |
|---|---|---|
| stage_contracts.py / modify | necessary within recorded experiment: prior teaching-evidence premise could limit recognition to markings/selected answers, conceal different read/write sets, reverse unsupported activity omissions or produce invalid/partial connected review issues | correct shared stage-rules owner. Changes target evidence, completeness and precise existing review contracts; no alternate generator, new schema or arbitrary rewrite authority. Their effect on actual model behavior must be measured by the planned experiment. |
| prompt.py / modify revision | necessary matching legacy fingerprint change for new shared rules | correct transport owner. Identity-copying legacy behavior is unchanged; only the direct revision literal changes. |
| test_staged_analysis.py / modify revision assertion | necessary current stage revision assertion | correct unit placement. Existing bounded orchestration/rule-composition tests remain; revision assertion alone is not evidence of semantic learning-object preservation. |
| test_provider_evidence.py / modify revision assertion | necessary current legacy revision assertion | correct unit placement. Existing trusted-ID and end-example checks remain; no claim it proves vocabulary interpretation. |
| Spec / modify metadata and prior evidence status | necessary explicit new hypothesis/scope/budget and honest preservation of07/08 outcomes | appropriate Spec owner. Spec remains VERIFYING, preserves previous failed/partial acceptance and does not label prior08evidence as09. This reviewer reads the provided prior results as metadata, not independently adjudicated content facts. Final09closure must update current-body facts from the actual new result. |

All five changed files are necessary and correctly placed. No wholly unnecessary/questionable file, new unowned abstraction, inappropriate dependency direction or safe deletion item was confirmed. No code/data/API/loop/cache budget expansion appears in the delta.

## Focused contract conclusions

**Teaching area vs incidental text** — stage_contracts.py:105–114. New108–110 identifies textbooks’ word/character/letter/explanation/practice areas and explicitly submitted word-practice whiteboards as learning-object evidence, without requiring circles/ticks/answers. This does not make all visible text an additional learning goal:106–107 still requires a teaching role;111–112 excludes interface/illustration and incidental numbers/time/objects;113–114 preserves parent-text/image separation and missing-media boundaries. Markings remain evidence of practice, not grading or mastery. All resulting outputs remain editable proposals requiring parent confirmation.

**Unmarked/distractor vocabulary and readable-object coverage** —109–110 and153–160. The whole readable word-discrimination option set is a comparison object, not only the correct/selected choice. This rule is limited to actual word-discrimination teaching and does not turn ordinary scene words into a vocabulary list. The reviewer/extractor must not determine correctness or drop the distractors. Existing partial-readability and confidence rules still prohibit substituting guessed characters. New158 demands enumerated-object evidence and a completeness check. New159 preserves reading/writing sets separately and permits merging differing sets only with explicit skill-to-object coverage, which is consistent with147’s independent-check exception. It does not permit naming only their intersection or implying every object received both skills.

**Unspecified activities** —121–122,230 and256. A parent’s broad activity label alone cannot become a placeholder knowledge point without concrete object/rule/scope. An indeterminate_object omission is valid and must describe its missing information; the quality reviewer cannot alternate between compulsory inclusion and rejection for the identical missing-object premise. Existing163–166 still requires complete candidate ledger, an allowed reason and omission review; all-omitted/non-actionable results still fail through unchanged pipeline behavior. This does not change the separate first-class manual activity/learning recording paths or permit guessing a detailed activity range.

**Accurate unique issues** —249–252. Reviewer must inspect actual current name/member mappings and preserve limited word lists. A code plus the same participating alias set has only one issue, matching the existing pipeline validator’s identity `(issue.code, tuple(sorted(issue.items)))` at pipeline.py:384–386. It does not merge different codes or discard independently located real defects. A should_merge issue must identify at least2current items with a common check, avoiding a spurious merge issue on an already-merged single item. Over-merge requires a concrete independent member target and cannot conflict with merge for the same complete group. Existing alias/ref/basis/extra-field validation stays unchanged.

**Complete connected merge handling** —233–236. Shared-member should_merge issues must be processed together across the connected common-check target, not by resolving only one pair and leaving another unhandled. This remains bounded by138–151’s same subject/domain, compatible supported scope, concrete common check, independent-rule separation,1–5minutes and no lost objects; it is not unconditional transitive historical equivalence. It also preserves unaffected member sets, single-accounting ledger and the one-semantic-correction/two-quality-review bounds. The instruction adds no recursive agent/tool loop or server-side rewrite mechanism.

**Scope, examples and historical/legacy compatibility.** All8examples at192–205 are byte-for-byte unchanged from Review03 and remain the final section in every composed stage and legacy prompt. General rule bodies remain primary; this increment adds no30case answer mapping or named-source result. HISTORY_RULES at181–190 is unchanged and present only in staged MATCH/REUSE; MERGE explicitly separates new consolidation from strict history equivalence at226. Legacy prompt still copies provided database IDs under its transport contract and has no stage-only no-DB-ID prohibition. Internal/public identity fields, family scope, new-key bridge, review gate, deterministic dates and parent-confirmation authority are unchanged.

No concrete unsatisfiable prompt contract, new source-evidence authority, code-level alias mismatch or introduced deterministic failure was found in this bounded delta. The truth of the model-quality hypothesis remains falsifiable and unproven by this source review.

## Independently executed checks

Used `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python`. Loaded current changed modules from the evidence-premise snapshot, then Review02 and Review01 frozen package paths. Tests selected no DB fixture or real external provider client.

- Frozen evidence-premise `test_staged_analysis.py` and `test_provider_evidence.py`, plus unchanged Review02 `test_staged_proposal_recovery.py`, pytest `-c /Users/bytedance/Documents/push_kids/pyproject.toml -p no:cacheprovider -q`: **71passed in8.87seconds**.
- Compared all11internal model schemas against independently loaded Review03 stage_contracts: **exactly unchanged**.
- Checked HISTORY_RULES and KNOWLEDGE_EXAMPLES bytes against Review03: **both unchanged**.
- All5stage strings and legacy: full KNOWLEDGE_RULES occurs once, full examples are last, staged history rules occur only MATCH/REUSE, legacy permitted-ID contract remains. PASS.
-5snapshot/manifest/current hashes matched. PASS.

These are mechanical/schema/compatibility checks. The two changed assertion tests only update revisions; they do not independently prove that Doubao preserves all unmarked/distractor words or completes every connected merge.

## Limits, experiment budget and closure

- The main thread’s one09same30run and six synthetic/holdout cases, with its own semantic assessment, remain the actual experimental evidence. No real case or holdout was opened/judged by this reviewer. Preserve original07 and both08reports, denominator and failures; do not replace them with the09run or this71PASS.
- Source-summary reviewer input still lacks original images/extraction excerpt dictionary in the normal quality payload; candidate summaries/material aliases cannot independently certify all source details. This existing visibility limitation is unchanged. Actual source-content evaluation remains required.
- Reading the Spec’s supplied prior08PASS/FAIL/cleanup statements is not independent verification of those artifacts. Its current09metadata and trailing08closure/evidence paragraphs need final version-scoped reconciliation after the experiment; no09semantic PASS or completed cleanup should be inferred in advance.
- Original5fixed findings, queue/local exact-expiry labeling and formal confirmation’s unchanged normalized canonical identity retain prior dispositions/acceptance limits. This delta changes none of those production paths or18/33calls/18cache capacities.
- No matching09/13cloud delivery: Spec remains active/VERIFYING, no DONE/completed/deployment or formal business-write conclusion.
- This exhausts the recorded one-review experiment budget. No additional review cycle, source fetch, artifact cleanup or subagent was initiated. Any later different hypothesis/scope/budget must be separately recorded; this report itself authorizes no continuation.
