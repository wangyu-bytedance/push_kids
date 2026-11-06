# BUG-036 Cache Spec02: Final Independent Cross-Group And Document Review

## Findings

**1 confirmed document-only P2 issue in a late EVD amendment; 0 confirmed code issues.** The frozen code and original 16-document snapshot had no confirmed cross-group/cache-fact defect. Final exit-time inspection caught a later evidence-count discrepancy described below. `cross.jsonl` contains one finding record. This final result supersedes the preliminary zero-finding report; known global static failures and incomplete content/cloud acceptance remain real limits.

### CROSS-DOC-001: Evidence-Copy Ruff Count Is Inaccurate

- Location: `specs/evidence/EVD-20261101-BUG036-CACHE02.md:63`.
- Severity/category: P2 / BUSINESS_SEMANTICS; repository MINOR; confidence9/10.
- Introduced: later documentation amendment, not a production-code change.
- Observed late EVD hash: `1965bede726d80890ffd7482db74bcc3a5da71ae1ec0b757ca9df1271decdebb`.
- The added paragraph says evidence `.py` copies produced **16 additional evidence-path errors**. Retained private `ruff-with-evidence.log` instead lists **10 I001 evidence-path errors plus seven external E501 errors, 17 total**. `ruff-final.log` retains the same seven external errors after the snapshots became inert `.py.txt`. Thus this recorded run supports ten additional evidence-copy errors, not sixteen.
- Correction: record10 evidence-copy I001 /17 total including seven external errors and identify the log. If16 refers to another run, retain and cite that exact run instead. Refresh document evidence and reconcile the prematurely copied zero-finding EVD/TP-C08 summary with this final finding.
- Owner/action: coordinator/TRAE; no correction performed by this reviewer. This is an evidence-fact correction, not a style request, global lint finding, or release blocker inferred from the cache code.

This is an independent, strictly read-only, R2 cross-group/static-document review. It is not another full implementation review, an executed test PASS, whole-repository approval, cloud approval, merge permission, or release authorization.

- Date: 2026-11-01.
- SKILL_ROOT: `/Users/bytedance/.trae-cn/skills/bits-code-guard`.
- REPO_ROOT: `/Users/bytedance/Documents/push_kids`.
- WORK_DIR: `/var/folders/hq/l74_1q417nbdffshwhtw79640000gn/T/tmp.QmgzUCkpZn/review`, existing private directory.
- Authority: repository `AGENTS.md`, `REVIEW.md` revision `REVIEW-20261028-01`, approved `BUG-SPEC-20261101-KNOWLEDGE-CACHE-02` / `ARCH-20261101-KNOWLEDGE-CACHE-02`; FEAT-001.
- Skill procedure: read `SKILL.md`, `general-workflow.md` Steps 3.1-3.4 and Step 4 cross-group validation, `review-dimensions.md`, `review-rule.md`, `review_groups.md`, both group Markdown reports and both JSONL files. Python has no additional language-specific checklist in this skill.
- Inputs: exact cache task delta and relevant direct callers, not the whole HEAD/worktree diff. Earlier BUG-036 content-rule implementation and BUG-037 implementation are excluded. BUG-037's concurrent documentation/status is retained, not signed off.
- Only writes by this reviewer: private `cross.jsonl` and `cross.md`. No repository artifact was edited or synchronized.

## Bound Versions

| Input | SHA-256 |
|---|---|
| `task.diff` | `ae1571aadb25141fdc5a2f64d28f3cddb85ee32df3bfcd5ee2fe289713e65e48` |
| `source-manifest.json` | `ce15f7d9290550004df546c35393ed7111337793d4780a87677b04bfab643ca3` |
| `source-manifest-round1.json` | `36dfaeba36236c572618f1841412e2a9e9615cf9c0204ea5a6c6fdc019828dfe` |
| Refreshed `doc-source-manifest.json` | `8adb0b46b5bf5f3dafa64858cb79c96c46d6a570c2c16a8b39ffe7226a009e20` |
| `group1.md` | `d19fb0e96160e8d883bc0fc773fcc69def43b18d21863aa855f1203155e19daf` |
| `group2.md` | `288c6efe8d3cc3d210796335ab04d0192fc4b2736eeb152a1d5496c4ee996983` |
| Each group JSONL, empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Base label: `0576ac304649 plus pre-task snapshot`. Baseline provenance is supplied, not reconstructed from Git. The cache delta spans nine files / 756 changed lines; group partition is four pipeline/contract/unit-test files and five checkpoint/worker/service/integration-test files, with shared pipeline and revision context.

All nine live code/test sources matched the final source manifest. All nine retained final `.py.txt` snapshots also matched their declared source hashes. The prompt hash is unchanged at `61152c25593aee2665a6ae59bb489e90b9b031bc48df69a24892e82fea242823`; current runtime identities are `staged-20261101-10` and `child-aware-history-agent-20261031-13`.

### Worker Drift Resolution

Comparing the two source manifests identifies exactly one changed hash:

- Original Group2 worker: `1098f52db7aad2a9323b1a6b2f0f78884722aea6391a4d14b20d7ee75bfcc920`.
- Final live worker: `32f8cb9f7b4a7e181ae4227bbffadfa5f2c582c4cfabf02ae8528f7172cbc2b8`.

Independent read-only stream verification reproduced the original hash exactly:

```bash
awk 'NR==32 {previous=$0; next} NR==33 {print; print previous; next} {print}' apps/api/src/push_kids/agent_processing/worker.py | shasum -a 256
```

Only the `runner` and `stage_contracts` import lines are swapped. No worker body, signature, guard, tuple, transaction, or error-handling change exists between Group2's original source and the final worker. The final worker's complete task delta against the pre-task worker was also read. This resolves the specific Group2 exclusion; it does not retrospectively change Group2's report or claim that Group2 reviewed the later hash.

### Document Refresh During Review

An intermediate comparison found four mismatches against the earlier document manifest: cache Spec02, TEST-STRATEGY, local release record, and EVD. The coordinator subsequently refreshed the manifest. Their affected paragraphs were re-read: they now record the latest global Ruff seven E501 errors, one-file format failure, and EVD link/count bookkeeping. No cache contract, approval, implementation scope, content judgment, or lifecycle expansion was found in these updates.

At the reviewed snapshot comparison, **16/16 document hashes matched the refreshed manifest** below. EVD and TP-C08 then explicitly recorded cross-review `IN_PROGRESS`; that was honest pending coordination. During report construction the coordinator subsequently added EVD provenance and copied the preliminary zero-finding closure into EVD/TP-C08. Those later versions are outside the table hashes. Exit-time inspection caught CROSS-DOC-001 in the added EVD provenance; final review closure must use this result, not the preliminary report. Source hashes still all matched at exit.

## Cross-Group Contracts

| Boundary | Direct implementation and caller evidence | Assessment |
|---|---|---|
| Final semantic failure tuple | `pipeline.py:464-474` emits `(quality, review, review1)` with `retryable=False`; `pipeline.py:689-710` emits `(validation, reuse, reuse)` with `retryable=False` | Exact agreement with `worker.py:500-508` whitelist; no final-refusal cleanup omission found |
| Error propagation/public contract | `failures.py:108-124` preserves reason/stage/unit/retryable; `runner.py:102-118` propagates StageFailure and only translates TimeoutError; `contracts.py:209-228` consumes the actual retryable flag and retains `analysis_output_invalid` | No signature, flag, return-type, or public-code mismatch |
| Cache result eligibility | `pipeline.py:78-84,109-124,143-157`: schema/reference validation precedes both reads and writes; same predicate excludes final refusal/uncertainty | Symmetric policy; review0 refusal and passed review1/accept/reject remain recoverable |
| Durable purge API | `checkpoints.py:172-184`: `(Session, family_id, child_id, submission_id) -> int`; fixed six-unit, three-scope DELETE, no commit or revision filter | Worker supplies four arguments and consumes count for safe telemetry; LearningService supplies four arguments and intentionally ignores count |
| Explicit parent retry | `learning/router.py:225-231` delegates scoped retry unchanged; `learning/service.py:954-998` locks Family -> Child -> Job -> Submission, refreshes identity-map state, rechecks failed, purges, resets and commits | Caller synchronized; archived existing work remains allowed, deletion freeze rejected; competing retry sees current state |
| Late failure/SQL boundary | `worker.py:434-518` performs scope/lease/attempt/state guards before purge and terminal commit; `worker.py:420-433` preserves SQL unknown-outcome propagation | No cleanup before guards or compensating queued/failed overwrite introduced; exceptions within failure handling propagate |
| Revision/ownership | Shared `PIPELINE_REVISION` remains in `stage_contracts.py:11`; pipeline fingerprints, checkpoint validation/write and worker telemetry use the same constant | No new module/interface/extension point or conflicting revision consumer |

Static call-site search found exactly the two production purge consumers and the two predicate consumers. Existing full purge has a distinct success/cancel/confirmation/deletion purpose; it is not obsolete. The changed paths create no formal learning, knowledge occurrence, review, or feedback records. That conclusion comes from the inspected write set, not an exhaustive runtime table audit.

Cross-boundary tests were read, not executed: seeded/unseeded verdict matrix; real Worker final refusal then explicit retry; intermediate refusal plus correction timeout; old06 semantic deletion; rollback and stale attempt/lease/cancel/deletion; reuse uncertainty; actual MySQL overlapping retries, missing-job repair, four-table lock observations and late checkpoint rejection. Expectations use independent key sets/call counts and fresh-session state, not only the production predicate or whitelist.

## Code Necessity And Placement

All operations below are modifications in the supplied task delta; this is not a Git tracking-state claim.

| File | Necessary change / consequence of omission | Placement / residue |
|---|---|---|
| `agent_processing/pipeline.py` | Final result eligibility and explicit terminal failures; omission reuses/refails old final semantic decisions | Correct existing semantic pipeline owner; predicate has two consumers |
| `agent_processing/checkpoints.py` | One fixed scoped semantic purge for two callers; omission retains decisions or duplicates SQL | Correct temporary persistence owner; distinct from full purge |
| `agent_processing/worker.py` | Guarded terminal purge and bounded diagnostics; omission retains terminal semantic branch | Correct failure transaction owner; import reorder has no body effect |
| `agent_processing/stage_contracts.py` | Revision isolation; omission leaves prior execution-contract checkpoints eligible | Correct shared revision owner; no DTO/prompt drift in task hunk |
| `learning/service.py` | Atomic scoped retry refresh/lock/state re-read/lease reset; omission reuses decisions or accepts stale state | Correct use-case transaction owner; delegates stage SQL |
| `tests/unit/test_staged_proposal_recovery.py` | Cache read/write verdict matrix and actual terminal flags | Correct existing policy/recovery suite; meaningful controls against overbroad exclusion |
| `tests/unit/test_staged_analysis.py` | Explicit contract revision assertion synchronized | Correct existing suite; reconstructed supplemental source is not historical Red evidence |
| `tests/integration/test_analysis_checkpoints.py` | Persistence, terminal/recoverable paths, tenant/lifecycle/stale-state and rollback assertions | Correct existing SQLite/API/Worker suite; pre-commit fault injection only |
| `tests/integration/test_staged_mysql.py` | Actual dialect concurrency/repair/lock ordering/rollback and scoped fixture cleanup | Correct existing isolated MySQL suite; not a MySQL8 substitute or production test |

Necessary: nine. Questionable/unnecessary/misplaced: zero confirmed. No safe deletion or unrelated revert recommendation. No new long-lived utility, cache framework, orphan abstraction, duplicated domain rule, or additional module boundary was identified.

## Document Audit

This audit covers affected current cache paragraphs and necessary historical distinction, not every historical paragraph or unrelated concurrent feature.

Task operations: the local release record, cache EVD, cache ISS and cache REG are additions; the other twelve scoped documents are modifications. No scoped document was moved or deleted.

| Document / affected section | Contract/evidence and necessity | Status / action / owner |
|---|---|---|
| `docs/domain/features/FEAT-001-push-kids-mvp.md`, cache preamble/revision and content baseline | Local10/13 cache facts, parent-confirmation/budgets and 09/13 failed content; necessary current-feature merge | aligned; correctly placed; no correction identified; Feature owner/TRAE |
| `docs/domain/features/README.md`, cache/index paragraph | Routes to current Feature, local VERIFYING and matching-cloud distinction | aligned; necessary/correct index; Feature owner/TRAE |
| `docs/domain/BEHAVIOR-CATALOG.md`, cache preamble, BHV-032 and BHV-003 | Specific final-semantic exceptions in BHV-032/preamble coexist with generic schema/transient bounded retry; max3 is an upper bound, not a promise to repeat terminal refusals | aligned in inspected scope; necessary/correct behavior owner |
| `docs/architecture/ARCHITECTURE.md`, current staged pipeline/checkpoints | Actual semantic/persistence/transaction owners, six units, four-table locks, bounded cache, old cloud06 vs local10 | aligned; necessary/correct architecture owner/TRAE |
| `docs/design/frontend/ui/UI-001-parent-miniapp.md`, backend-only note | Same retry entry, no frontend code/DREV/FEC/viewport implementation change or new native/device PASS | aligned; necessary impact note, not a new design approval; UI owner/TRAE |
| `docs/quality/TEST-STRATEGY.md`, cache scope/current result | Required real5.7 isolation and concurrency, Red/Green distinction, 52 default skips, latest global static failures | aligned; necessary/correct quality owner/TRAE |
| `specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md`, approval, TP-C01-C08/lifecycle | Exact Spec02/Architecture02 approval is local only; tests bounded; TP-C06 COMPLETE_WITH_FAILURES, TP-C07 PARTIAL; TP-C08 was IN_PROGRESS in bound snapshot | aligned at bound snapshot; necessary/correct authoritative Spec; later preliminary PASS/0 summary must be reconciled with final finding |
| `specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md`, cache supplement and 09 baseline | Original Spec01 intent/approval and content FAIL retained; distinct later cache revision local10/13 | aligned; necessary/correct parent traceability; Spec owner/TRAE |
| `specs/README.md`, cache/current counts and historical section | 12 active/109 completed/13 rejected; old09 evidence remains dated, not relabeled10 | aligned in affected scope; necessary/correct index; coordinator |
| `specs/STATUS.md`, current directory/cache rows | Three VERIFYING include both BUG036 Specs plus independent BUG037; no matching10/13 cloud delivery | aligned; necessary/correct lifecycle index; coordinator |
| `docs/deploy/releases/20261101-knowledge-cache-local.md` | LOCAL_IMPLEMENTED/VERIFYING and DEPLOY NOT_RUN, no production reset/DDL/commit; new release approval required | aligned; necessary/correct local release record; release owner |
| `specs/evidence/EVD-20261101-BUG036-CACHE02.md` | Version hashes, retained failures, scope-limited mechanism result, latest global FAIL, cross-review pending in bound snapshot | aligned at bound snapshot; later provenance count conflicting (CROSS-DOC-001); necessary/correct evidence owner; coordinator |
| `docs/quality/issues/ISS-20261101-FINAL-REFUSAL-CACHE-RETRY.md` | Production06 observation versus deterministic09 Red; locally resolved, no release observation, not closed | aligned with ISS lifecycle; necessary/correct issue owner/TRAE |
| `docs/quality/regressions/REG-20261101-FINAL-REFUSAL-CACHE-RETRY.md` | Actual Red12/47, frozen bad/good production and final test source; first Red test source not separately frozen | aligned with stated limitation; necessary/correct behavior REG, not reviewer benchmark; quality owner/TRAE |
| `docs/quality/issues/README.md`, cache entry/lifecycle | Local resolved is distinct from closed and released | aligned; necessary/correct navigation; maintenance owner |
| `docs/quality/regressions/README.md`, cache case | Active behavior evidence and historical test-source limitation, no CI/scheduler claim | aligned; necessary/correct navigation; maintenance owner |

All 16 document modifications/additions are necessary and correctly placed for this cache closeout. No stale/conflicting/missing cache implementation fact or safe deletion candidate was found in the bound snapshot. The later EVD evidence-count discrepancy is separately confirmed above. Unrelated travel/current-state history and BUG037 implementation are not approved by this table.

### Exact Document Hashes

The following are the refreshed manifest values, all independently matched at the reviewed snapshot comparison before later closure edits. Later EVD and TP-C08 edits are not covered by these hashes:

| Repository-relative document | SHA-256 |
|---|---|
| `specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md` | `5898b2ea3e97953dc2799299589ba4775f73c49f09e3167c3c284681b54d8cc1` |
| `specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md` | `d833fc3c86fa9d878e95ea65c552350db761d287f7b562787a013a9bb8ea6252` |
| `docs/domain/features/FEAT-001-push-kids-mvp.md` | `5eb8d4d7d7af11c1ec6928ccdccb5f954e0727006115c4162427ad96bc33e7cd` |
| `docs/domain/features/README.md` | `be9b7094e61f17e8ebf1b5fa3b19833eee0a7ddbd873ab19f18e980dfc7328a5` |
| `docs/domain/BEHAVIOR-CATALOG.md` | `5f036ef218c11ab001bc9057c843856d29beca1d6d14a736445028082f8a95a6` |
| `docs/architecture/ARCHITECTURE.md` | `cbfe386a3c6e5450e4a33561f965fed55f839624bd6a897ed5137c9a3b65dd5a` |
| `docs/design/frontend/ui/UI-001-parent-miniapp.md` | `9e855483b1d31806967f0c24071727bfd05e6e3bb6f3a709004b1ced54efad4c` |
| `docs/quality/TEST-STRATEGY.md` | `71a7ca2434eba4f57679749e9b032f27a66a3248f7a05dc2f91d436c7c04d3cc` |
| `docs/deploy/releases/20261101-knowledge-cache-local.md` | `13b7f8f306eb1ccaa9da2332068140cac446ba519a3a5cf4db96063f9b42c9b6` |
| `specs/README.md` | `c31914f7a0cb9638729111f5dba82fa80f17dd02a432b35395268440ca4a3b7c` |
| `specs/STATUS.md` | `5783903730f5fd8c57951e15a90228dde29e17a465b0e8843df8c9020002b5ab` |
| `specs/evidence/EVD-20261101-BUG036-CACHE02.md` | `21336eaf6ef89d8f9425ddce9f377948a6faf0e28218daecffb35c1b9f092caf` |
| `docs/quality/issues/ISS-20261101-FINAL-REFUSAL-CACHE-RETRY.md` | `1fa2afa8d3402b276b046348cafe06bcf5ec3e464ff41803c08c517fde0d4e12` |
| `docs/quality/regressions/REG-20261101-FINAL-REFUSAL-CACHE-RETRY.md` | `af595959185254c38dbea762b4b0f0c4a2fd0bd54c8a180a6a8118793a0b4984` |
| `docs/quality/issues/README.md` | `4ebca27186b99d8dbe8e2a190a1bf5dc4450874d8d01471620d57d7c6d2e7192` |
| `docs/quality/regressions/README.md` | `95b1d8164c8a706374dd206147e230f61cc21c34958d13d02ee511b64ec1dd3a` |

Coordinator link-check evidence: 542 links, zero missing, as recorded in the document manifest; this reviewer did not rerun the link checker. Independent read-only file enumeration confirmed active12/completed109/rejected13; reading active Status fields confirmed 3 VERIFYING / 7 READY_FOR_REVIEW / 2 DRAFT.

## Evidence Honesty

Evidence below was inspected in retained logs/manifests, not regenerated:

| Evidence | Observed result / interpretation |
|---|---|
| Original `red.log` | Actual 12 failed / 47 passed, 6.36s, on pre-fix implementation; do not replace with a later baseline replay |
| `green-initial.log` | Actual 78 passed / 1 failed; pre-commit injection did not trigger; EVD retains fixture diagnosis |
| `green-focused.log` | Actual 80 passed; intermediate scope, not the final complete suite |
| `focused-final.log` | Actual 116 passed, 6.96s |
| `backend-full-first.log` | Actual 856 passed / 1 failed / 52 skipped; old pipeline revision assertion is visible |
| `backend-full-final.log` | Actual 857 passed / 52 skipped, 108.67s; default external-environment skips are not converted to PASS |
| `import-only-recheck.log` | Actual 44 passed, 5.86s; separate affected Worker/checkpoint recheck, not a new full-suite run |
| `mysql-summary.json`, migration/schema logs and `mysql-staged.log` | Engine is `5.7.18-cynos-2.1.14-log`; isolated utf8mb4, migration/schema exit0, 8 passed / 0 skip, 14.62s, disposed true. Eight is the case count, not MySQL version8 |
| First/second MySQL logs | Each 7 passed / 1 failed; first leftover queued fixture interfered with Worker claim, second is a connection timeout. Failures remain visible, not silent successful reruns |
| Task `ruff-task-final.log` | All checks passed for the stated nine-file command scope; not a global PASS |
| Private `ruff-with-evidence.log` | Seventeen total: ten I001 in baseline/final evidence `.py` copies, six BUG037 E501 and one travel E501. This directly contradicts the late EVD's16 additional evidence-path errors |
| Latest `ruff-final.log` | Seven E501 errors across two unrelated files: travel preparation and BUG037 evidence script |
| `format-final.log` vs `format-with-parallel-artifact.log` | Earlier832 already formatted; latest one file would be reformatted / 840 already formatted. Latest global format is FAIL |
| `mypy-final.log`, `architecture-final.log` | Actual151 source files successful, untyped-body note retained; architecture4 policies/151 modules valid |
| Original three-source09/13 report/JSON | 1 content PASS / 1 FAIL / 1 NO_OUTPUT; 2 outputs, six original images; authorized-family61 table fingerprints match and private cleanup recorded. No new live retest, no Worker/checkpoint verification |

The EVD/task list report the55-test pre-task baseline; its standalone stdout was not located among the retained files inspected, so this reviewer does not claim independent raw-log verification of that count. The original Red log is retained; first Red test source is not separately frozen and REG explicitly limits historical replay. Final tests and inert `.py.txt` snapshots cannot retroactively supply the missing first-Red test revision. No historical execution is fabricated by this report.

The safe snapshots remain version evidence under `specs/evidence/`, not new production/test implementations. No raw provider responses, child images, real credentials or new live content are copied into these review artifacts.

## Dimensions And Residual Limits

All generic dimensions were considered: logic (cache symmetry/tuples), business semantics (intermediate versus final refusal and explicit retry), security (fixed scoped deletion and no new sensitive logging/formal writes), concurrency (lock ordering/current-state/late lease), robustness (finite recovery and transaction error propagation), performance (bounded keys/DTOs/calls and no unbounded read), and quality (necessary files/owners/duplication). Repository dimensions additionally covered test effectiveness, document correctness and evidence/version/approval honesty. Style-only findings were not emitted.

Remaining limits and coordinator actions:

- No tests, collection, production query, model call, linter/formatter/type/architecture validator, deployment, data reset, commit, or repository edit was run by this reviewer. Retained runtime evidence is not an independently repeated result.
- MySQL coverage is actual5.7 but finite: no exhaustive concurrent schedules, corrupted cross-scope associations, same-family different-child runtime negative case, post-commit lost acknowledgement, or real-connection terminal-cleanup failure replay. Existing SQL/scope protections were checked statically.
- No exhaustive runtime formal-table fingerprint was taken for the synthetic cache tests; checked production write paths and explicit LearningRecord/Knowledge counts support only their stated scope.
- New10/13 live content, release40-case gate, native/device acceptance, cloud deployment/production retry and release observation remain NOT_RUN. Historical09 content FAIL and original three-source outcomes remain independent.
- Global Ruff seven errors and latest global format one-file failure remain unresolved release checks; this cache-only review neither fixes nor approves BUG037 or travel scripts.
- Coordinator must correct or substantiate CROSS-DOC-001, reconcile EVD/TP-C08 and exported reports with the final finding, and refresh affected document evidence. The bound IN_PROGRESS was honest; the later copied preliminary zero-finding closure is not this final result and is outside the document hashes above.
- Cache Spec02 remains `VERIFYING` at `specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md`; parent Spec01 remains `VERIFYING` at `specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md`. No matching10/13 cloud delivery, no DONE/completed claim. Future cloud delivery and release still require their own approval/gates.

Conclusion: zero confirmed code/cross-group defects; one confirmed MINOR/P2 documentation-evidence discrepancy in a later EVD amendment. Nine code/test changes and sixteen document changes are necessary/correctly placed. No implementation/current-cache-contract conflict was confirmed. Correct the evidence count and update final review bookkeeping; residual runtime/content checks and release authority remain separate.
