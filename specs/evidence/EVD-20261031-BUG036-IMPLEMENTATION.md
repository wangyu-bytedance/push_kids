---
created: "2026-10-31"
updated: "2026-10-31"
type: evidence
status: verified-local
owner: TRAE
---

# BUG-036 Spec01 implementation evidence

本EVD保留07/08实施与原审查/评测的执行结果。当前源码已推进09/13，后续证据以[09EVD](EVD-20261031-BUG036-PROMPT09.md)为准；下文“current08/当前08”指本EVD原记录时点，不代表现在，也不追认09。此前各真实运行不被当前会话新判断覆盖。

- Evidence ID: `EVD-20261031-BUG036-IMPLEMENTATION`
- Requirement: [BUG-036 Spec01](../completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md), AC-001..007 / TP-001..009; TP-010..012 have separate content/audit closure.
- spec_revision: `BUG-SPEC-20261031-KNOWLEDGE-GENERATION-01`
- subject_revision: mechanism and independent Review02 subject `staged-20261031-07` / `child-aware-history-agent-20261031-11`; current clarified Prompt04 subject `staged-20261031-08` / `child-aware-history-agent-20261031-12`. Provider parameter revision includes review8192, match/reuse2048, queue-deadline and execute45-30, unchanged between07/08.
- Scope: local working-tree implementation relative to approval-time snapshot, preserving unrelated travel/UI/governance edits. No deployment, migration or production business writes.
- result: passed for the stated mechanism tests; full-repository Ruff has a pre-existing failure stated below. Model content quality is not inferred from these tests.

## Coding slices and honest baseline

`UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync` prefixes each Python test/check command.
Baseline environment is Python3.12.11, existing .venv and uv.lock; fixtures use local in-memory SQLite and synthetic image bytes, never the production database.

| Phase / test points | Exact command after prefix | Object and observed result |
|---|---|---|
| Baseline | `pytest tests/unit/test_staged_analysis.py tests/unit/test_stage_provider.py tests/integration/test_analysis_checkpoints.py -q` | Approval-time code: 52 passed |
| Red TP-001/002 | `pytest tests/unit/test_staged_analysis.py -k 'single_material_schema_failure or leaves_request_queue' -q` | 2 expected failures: material validation has no recovery; provider receives30 seconds rather than original270-second absolute budget |
| Red TP-003/004 | `pytest tests/unit/test_staged_analysis.py -k 'unsupported_candidate_is_accounted or uses_review_alias' -q` | 2 expected failures: omission ledger rejected; correction lacks i0 mapping |
| Green first slices | Same four new tests with combined `-k` | 4 passed after local recovery, deadline, omission and correction implementation |
| Saved baseline replay TP-006/007 | `PYTHONPATH=/private/tmp/push-kids-bug036-baseline-20261031 BUG036_BASELINE_MODULES=pipeline,stage_provider,checkpoints uv run --no-sync pytest -p baseline_override tests/unit/test_staged_proposal_recovery.py tests/unit/test_stage_provider.py tests/integration/test_analysis_checkpoints.py -k 'final_history_rejection or history_matching_receives or same_name_does_not or queued_request_gets or queue_deadline_does_not or schema_diagnostics_only or model_field_names or all_eighteen_successful' -q --tb=short` | Saved old implementations executed with compatible new DTO test shapes: 10 behavior failures, including old SDK budget245 instead of30 after queue, missing diagnostics/reuse, old14-key cap. This is **post-implementation saved-baseline replay**, not a claim of prior TDD Red. An earlier fake-clock setup used a real-clock outer deadline; corrected version preserved245-versus30 behavior difference. |
| Review01-driven Red | `pytest tests/unit/test_staged_proposal_recovery.py tests/unit/test_stage_provider.py tests/unit/test_provider_evidence.py -k 'same_name or new_global_option_cap or numeric_unknown or worker_preserves or requires_actionable_names' -q --tb=short` | 8 expected failures on Review01 snapshot: same-name loss, global-cap regression, numeric unknown field0/100/5000 behavior, lost durable diagnostic, contradictory legacy ID instruction |
| Review02 Green | Same8 checks | 8 passed; explicit same-name rejection retains new target without turning it into historical reuse; unknown fields never retained or converted without a bound |
| Focused final | `pytest tests/unit/test_staged_analysis.py tests/unit/test_staged_proposal_recovery.py tests/unit/test_stage_provider.py tests/unit/test_provider_evidence.py tests/unit/test_analysis_context_contract.py tests/integration/test_analysis_checkpoints.py tests/integration/test_worker_resilience.py tests/unit/test_structured_analysis_output.py -q` | 139 passed |
| Full first | `pytest tests/unit tests/integration tests/contract -q` | 825 passed,46 skipped,1 failed because an old contract test required the removed literal example森林超市; no production behavior failure claimed |
| Full after old contract update | Same full command | 826 passed,46 skipped |
| Full final Review02 | Same full command | **832 passed,46 skipped**,108 dependency deprecation warnings; final run115seconds approximately. The46 skips require isolated MySQL/other environment setup and are not passes. |
| Full current08 | Same full command | **832 passed,46 skipped**,108 warnings,120.51s; actual output retained in [review03/full-suite](bug036-20261031/reviews/review03/full-suite.txt). Prior07 runs do not replace this current-version check. |
| Static | `ruff check .` | FAIL: existing unrelated `tools/prepare_travel_diary_native.py:36` is103characters. It was not modified for BUG-036. |
| Static changed scope | `ruff check apps/api/src/push_kids/agent_processing/{contracts,failures,worker,pipeline,prompt,stage_contracts,stage_provider,telemetry,checkpoints}.py tests/staged_analysis_fakes.py tests/unit/{test_staged_analysis,test_staged_proposal_recovery,test_stage_provider,test_provider_evidence,test_analysis_context_contract}.py tests/integration/test_analysis_checkpoints.py` | PASS |
| Static | `ruff format --check .` | PASS,794 files at historical07 check; current08 run796 files PASS |
| Static | `mypy apps/api/src` | PASS,151 source files; pre-existing untyped-body note in footprints/reads.py |
| Architecture | `python tools/check_architecture.py` | PASS,4 policies,151 modules, runtime/lazy DAG |

Current08 scoped Ruff, format796, Mypy151 and architecture4/151 were executed and passed. Full Ruff was rerun and still fails at the same unrelated103-character line. Captured synthetic outputs and immutable source/test snapshots are retained in the [safe evidence index](bug036-20261031/README.md). No child data or credentials are present; `.py.txt` snapshots are evidence, not a second production package. Approved baseline, Review01, Review02 and current08 remain separate objects.

## Proven mechanism boundaries

- Original9 images+text,2 bounded context groups,initial+corrective merges,2 reviews,match,reuse yield18 successful stage positions; one structural correction at each eligible position reaches33 provider calls. Tests assert both counts and actual returned historical identity.
- Local checkpoint integration stores18 unique validated keys, rejects19th, still enforces64KiB/row and512KiB/job, and resumes the same successful result with0 provider calls. Cancellation/lease/family isolation and no formal records continue passing.
- All candidates belong once to a knowledge item or omission; duplicate, foreign, missing and all-omitted candidates fail. Review sees omission reasons and accurate i/o aliases. Unaffected member targets cannot drift during correction.
- Match inputs carry both actual skill and evidence. Shared historical directory supports200 same-day+120 today+100 historical identities,320 per candidate and512KiB request serialization; only history evidence is reduced and explicitly marked incomplete.20 query and100 unique-history limits remain.
- One reuse review accepts/rejects/marks uncertain before canonical assembly and same-day elimination. Reject/null does not get overridden by name equality; internal verified-new keys only affect duplicate filtering, with all public reference/evidence/scope validation retained.
- Structured failures have closed field paths/categories; arbitrary model key names, including5000digits, collapse to `stage.fields`. The worker persists bounded stage/unit/schema metadata and keeps older `.codes` callers compatible.

## Independent read-only review

`bits-code-guard` grouped workflow required2 independent reviewers; no implementation delegation or model-judging delegation occurred. Review baseline is approval-time working tree, not HEAD, because the repository contains unrelated pre-existing edits.

Review01 found3 P1 flow/compatibility/capacity bugs and1 P1 numeric-diagnostic defect plus1 P2 durable-diagnostic loss. The8 new regression checks failed before the fixes. Review02 reported0 new confirmed findings: independent flow129 passed and runtime22 passed. Cross-group review reported0 confirmed defects, and additionally proved the Runner still rejects missing history-search completion and oversized-key schema failure can locally recover and reach safe worker metadata. Original review snapshots/reports are retained without rewriting their results.

Review03 examined only the two-file08 prompt delta against the frozen Review02 rules. Shared quality/output/review instruction ownership, transport, DTO, call/cache ceilings and dependency direction are unchanged; current fingerprint is incremented.0 new confirmed static defect. This was direct review in the continuation context, not a claim of a third independent group or real-source semantic success. See [delta audit](bug036-20261031/reviews/review03/audit.md).

## Fixed-source content verification

07 first replay completed2026-10-31 18:26:49+08:00:24/30 output;13 strictPASS/10FAIL/1PARTIAL/5NO_OUTPUT/1INSUFFICIENT_MATERIAL. The initial14PASS assessment was corrected to13 after checking case02's false14-unit summary against actual8new+1reuse. Source results were not rerun or replaced. Case25, one of original6PASS, omitted visible letters and regressed. Original13no-output had10 new outputs, not necessarily content passes. The approved same-rule08 clarification was then applied and fingerprinted; final08 results are separate.

[07 immutable report](../../dist/knowledge-generation-evaluation-20261031-prompt04/revision07/evaluation-30.md) binds10 generator source hashes and all30 source digests to the original06. Actual07 metrics:192calls,600709input/49939output tokens,median31.89s/P95113.66s; original06 had178calls,335054/41409tokens,median31.695s/P9576.52s. Increased tokens and stage paths are observed, not a causal cost estimate or universal speed guarantee.6 synthetic Doubao holdouts passed their boundaries, including one correct rejection, independent of the30 denominator.

08 completed2026-10-31 18:46:52+08:00 on unchanged10-generator-module SHA fingerprints:25/30 output,9 strictPASS/16FAIL/4NO_OUTPUT/1INSUFFICIENT_MATERIAL. Original13no-output has10 outputs; original6PASS regressed at18 and25.3 terminal quality failures at03/14/16, one merge length validation at29 after both bounded calls, and correct missing-object rejection at11. The actual output summaries at09/27 contain prohibited exclusion/process prose; these are separate existing proposal-contract violations, not invented C1–C6 criteria or changes to the denominator.207calls,780424input/51041output tokens,median35.5s/P95113.42s/max132.96s.6 current08holdouts passed their stated boundaries. [Current report](../../dist/knowledge-generation-evaluation-20261031-prompt04/revision08/evaluation-30.md) and [summary comparison](../../dist/knowledge-generation-evaluation-20261031-prompt04/evaluation.md) preserve07/08 separately. AC-008 and TP-005/010 **FAIL**; more outputs did not achieve content acceptance.

07 and08 READ ONLY MySQL5.7 before/after audits each compared61table counts and content fingerprints, all equal; final audit observed2026-10-31 18:47:23+08:00. Generation had no database connection, businessPOST, Worker or checkpoint. Safe reports and artifact/source SHA manifests were retained under this evidence index and dist deliverables before cleanup. At18:51:30+08:00,173task-owned private images/contact sheets/identity snapshots/raw-stage files totaling56717611bytes were removed; [cleanup evidence](bug036-20261031/cleanup.json) confirms absence, known production identity/runtime-secret scan and manifest checks. Other task directories were untouched. New source verification needs authorized READ ONLY re-acquisition; these historic results cannot stand in for a new run.

Documentation conflict audit: Feature revision06, Behavior generation02/BHV003/032, Architecture01, Test Strategy, approved Spec/Prompt record, ISS/REG and indexes reflect08local behavior and actual results. Prior038/staged06 delivery remains historical and does not cover this increment. UI current-state, publicAPI and schema were inspected as unaffected and require no new fact revision; release documents are unchanged because no deployment occurred. No design/implementation approval is inferred from test success. Spec remainsVERIFYING/active due no matching cloud delivery and content acceptance failure.

Final read-only closure validation executed:11 task-document local-link sets, four retained report manifests, all30 distinct case denominators,10 current generator source hashes, all retained source/test snapshot hashes, actual cleanup andVERIFYING/active location PASS; `git diff --check` PASS. The current generator fingerprints exactly match the08 replay and Review03 delta, so no later source change is being covered by stale tests. This verifies the stated documentation/evidence scope, not a whole-repository historical-document audit. Unrelated working-tree edits, commits, deployment and frontend checks were not performed by BUG-036.

## Verification limits and recovery

- The exact-expiry outer pipeline timeout can label a queued request `local_deadline` while the direct Provider uses `queue_deadline`; deadlines expire simultaneously. No early cutoff, slot leak, retry change or partial output was found. Complete queue-versus-total error labeling is **PARTIAL**, not fully verified.
- Parent confirmation's existing normalized-name/category identity handling is unchanged and was not exercised with production writes. A generated new proposal is not proof of creation of a distinct formal historical identity.
- Model behavior is stochastic; passing scripted providers proves orchestration, not C1–C6 content quality. Same30 real-source report, holdout and database after-audit remain versioned separately. Content issue remains [open](../../docs/quality/issues/ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md); mechanism issue and actual Red/Green [REG](../../docs/quality/regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md) do not close it.
- Frontend, native/real device, release40-case gate, cloud deployment and true callContainer business writes: N/A/NOT_RUN for this local-only Spec. Existing manual paths and public DTOs are unchanged; no completion or acceptance evidence is borrowed from038.
- Rollback is the exact BUG-036 patch/revisions against approval-time snapshot; preserve unrelated edits. No stored business-data recovery is necessary.
