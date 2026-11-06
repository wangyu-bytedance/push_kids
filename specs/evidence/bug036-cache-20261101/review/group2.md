# Group2 Independent Read-Only Review

## Findings

**0 confirmed issues.** No P0/P1/P2 finding met the evidence and introduced-change requirements. `group2.jsonl` contains zero finding objects, not a placeholder finding. This is a static code/test review, not a runtime PASS or release approval.

## Scope And Version

- Date: 2026-11-01.
- SKILL_ROOT: `/Users/bytedance/.trae-cn/skills/bits-code-guard`.
- REPO_ROOT: `/Users/bytedance/Documents/push_kids`.
- WORK_DIR: `/var/folders/hq/l74_1q417nbdffshwhtw79640000gn/T/tmp.QmgzUCkpZn/review` (existing private directory).
- Authority: approved `specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md`, `BUG-SPEC-20261101-KNOWLEDGE-CACHE-02` / `ARCH-20261101-KNOWLEDGE-CACHE-02`; affected FEAT-001.
- Exact change input: `task.diff`, not the whole HEAD/worktree diff. Its base label is `0576ac304649 plus pre-task snapshot`; baseline provenance was supplied, not independently reconstructed.
- Primary review: five Group2 files, +635/-6 (641 changed lines). Shared boundary context: `stage_contracts.py` revision and `pipeline.py` direct failure/cache outputs, +21/-12. The complete supplied task spans nine files and 756 changed lines.
- Read the skill's general workflow Step 3.1-3.4, review dimensions, severity/confidence rules, repository AGENTS.md and REVIEW.md, approved Spec, relevant FEAT-001 invariants, architecture constraints and related retry-bound ISS / mechanism REG. Python has no additional language-specific checklist in this skill.
- Inspected changed functions in full, their direct callers, relevant model constraints/indexes, failure disposition, telemetry, StageFake and test fixtures. Did not use another group's findings.
- All nine source SHA-256 values matched `source-manifest.json` at the review's initial source check. Prior "Focused80pass/MySQL8pass" context is not independent evidence and was not used to establish a PASS.
- Finish-time recheck: `worker.py` changed concurrently from manifest hash `1098f52db7aad2a9323b1a6b2f0f78884722aea6391a4d14b20d7ee75bfcc920` to `32f8cb9f7b4a7e181ae4227bbffadfa5f2c582c4cfabf02ae8528f7172cbc2b8`. The original manifest-matching worker was read in full before this drift. Findings and worker line references bind to that original version; the newer version was not reviewed. The other six primary/shared sources rechecked still match their manifest values. Coordinator must bind any worker increment to a new snapshot and review its affected scope; this report does not approve the live worktree.
- Earlier BUG036 generation, travel and BUG037 changes are excluded. Group1 internals are not a second full pipeline review. Documentation closure is underway and outside this code/test finding scope.

Input SHA-256:

```text
task.diff             08fd96fe77b339841faa3a4ada1a101c17e5ba960f97494fb1ab86a71565e44d
source-manifest.json  36dfaeba36236c572618f1841412e2a9e9615cf9c0204ea5a6c6fdc019828dfe
```

## Seven Repository Dimensions

### 1. Functional Correctness

- Semantic deletion is a parameterized DELETE constrained by all of family, child and submission, with a server-owned fixed six-unit whitelist. It has no revision filter, so old06 semantic units are removed too; extraction/text/group units are untouched (`checkpoints.py:172-184`). The added API does not accept externally selected units.
- Explicit retry performs a family-scoped discovery read, then locks Family -> Child -> Job -> Submission. Family/child/job reads use `populate_existing=True`; `_submission(..., for_update=True)` also refreshes the identity-mapped submission. The failed-state check and purge happen after that current locking read (`learning/service.py:174-189,954-998`). Archiving remains allowed; deletion freeze is rejected.
- Existing jobs keep their identity and max-attempt budget; retry resets state, attempts, availability, safe errors and lease. Missing-job repair retains the pre-existing constructor path, whose defaults are queued/0/3; family/child serialization and the unique submission constraint protect competing repairs (`models.py:438-450`). A competing retry sees the current queued/analyzing state and conflicts rather than refreshing decisions twice.
- Worker cleanup accepts only non-retryable `(quality, review, review1)` or `(validation, reuse, reuse)` failures. It runs after the existing active-scope, unexpired lease, attempt, lease-token and analyzing/running-state checks, in the same terminal-state transaction (`worker.py:434-518`). Network/schema retry paths do not take this cleanup branch.
- Direct pipeline outputs match those two tuples (`pipeline.py:464-474,689-710`); `analysis_failure_disposition` consumes `retryable=False` and preserves the public `analysis_output_invalid` contract (`contracts.py:209-237`). Intermediate review0 refusal remains resumable.
- No changed production path calls confirmation, planning, or writes formal LearningRecord/Knowledge/Occurrence/Review/Feedback. It updates only existing submission/job state and temporary stages. Runtime absence of all formal writes was not independently measured.

### 2. Design Reasonableness

The selected policy addresses the causal cache problem: intermediate valid work is recoverable, final semantic refusal stops, and explicit parent retry refreshes the entire decision branch. It does not rely on randomized repeated review of the same correction or increase automatic retry budgets. Both consumers delegate deletion to the existing checkpoint owner, which neither commits nor creates another cache subsystem. Existing dependency directions and pure planning boundaries are preserved in the inspected change.

### 3. Modification Necessity

Each primary change serves approved AC-C02/AC-C03 recovery or their transaction tests. Without the helper, callers would duplicate persistence details; without worker cleanup, terminal semantic state would remain retained; without retry locking/refresh/purge, explicit retry could reuse the old branch or race another retry. Per-file judgments and test motivations are below. No questionable or unnecessary change was confirmed in the exact task scope.

### 4. Placement

Persistence deletion stays in `agent_processing/checkpoints.py`; worker owns guarded terminal failure; learning service owns explicit retry and its transaction; tests remain in existing integration files. The shared revision stays in `stage_contracts.py` and direct refusal classification in pipeline. No router persistence logic, generic shared helper, provider call in a domain, or new module boundary is introduced.

### 5. Redundancy And Residue

The new semantic-only purge and existing full purge have distinct consumers/contracts. Full purge still serves success/cancel/manual confirmation/deletion; it is not abandoned code. Test unit sets are independent expected values, not imported from the implementation whitelist. SQLite workflow/rollback coverage and MySQL contention coverage are not redundant substitutes. No orphan new API, unused flag, accidental rename, or safely deletable task artifact was confirmed.

### 6. Test Effectiveness

These are source-level assessments only; no tests were executed:

| Added coverage | Evidence in test source | Assessment / limit |
|---|---|---|
| Explicit retry scope and whitelist | `test_analysis_checkpoints.py:295-340` | Independent retained/deleted key sets; sibling submission and foreign family unchanged; wrong-family 404; repeat retry 409; old06 semantic rows seeded. Seed payloads intentionally test deletion rather than DTO validity. |
| Retry atomic rollback and lifecycle scope | `test_analysis_checkpoints.py:343-391`; `test_staged_mysql.py:356-422` | Fresh-session durable state assertions, not only in-memory values. MySQL mock checks purge/reset inside the transaction before throwing. Archive success and deletion rejection are distinguished. |
| Final refusal then parent retry | `test_analysis_checkpoints.py:394-419`; `test_staged_mysql.py:425-470` | Uses the actual Worker/pipeline/checkpoint path with valid StageFake DTOs; checks failed attempt 1, retained extraction, same job success after retry, new decision calls and no LearningRecord. |
| Intermediate refusal plus transport interruption | `test_analysis_checkpoints.py:422-448` | Injects correction timeout; checks review0 cache remains and extract/merge/review call counts prove resume without bypassing final review. |
| Stale worker refusal | `test_analysis_checkpoints.py:451-480` | Changes attempt, lease expiry, cancellation or child deletion during provider execution; checks semantic stages and nonterminal/cancelled submission remain unchanged. |
| Terminal cleanup commit failure | `test_analysis_checkpoints.py:483-508` | Throws before actual terminal commit and checks original durable running lease and cache from a fresh session. Does not demonstrate post-commit lost acknowledgement. |
| Reuse uncertain | `test_analysis_checkpoints.py:511-558` | Real selected-history path; terminal at attempt 1, only text extraction remains, existing knowledge count unchanged and no LearningRecord. |
| Concurrent retry, including missing-job repair | `test_staged_mysql.py:233-298` | Barrier is before the family SELECT FOR UPDATE, after both initial scope reads. Asserts exactly queued/conflict, full lock sequence in both threads, one job and expected retained keys. Would detect stale submission reuse in the loser. Missing-job setup removes FK-dependent stages first. |
| Retry versus late checkpoint | `test_staged_mysql.py:301-353` | Coordinates retry holding outer locks with a competing checkpoint; checks matching order, rejection and no resurrected stage. Starts from a failed job, so this alone does not prove every running-worker interleaving. |

Existing capacity/revision/fingerprint tests were read as context (`test_analysis_checkpoints.py:119-134,181-269`). They are not new execution evidence. Fixtures disable background worker execution and use synthetic inputs; MySQL tests are conditional on an explicitly configured isolated URL. New disposal cancels that fixture family's queued jobs to avoid later worker-claim interference.

### 7. Documentation Validity And Consistency

The approved Spec provides explicit policy, state, locking, ownership and non-side-effect requirements; inspected code/test changes align with that intent. FEAT-001, BHV-015/BHV-025 and architecture constraints supplied the parent-confirmation, archive/deletion and tenant boundaries. No new API/DTO/Schema/frontend change was found in Group2's task diff.

Current-state documents are being edited concurrently for closure, and their preambles/test-point statuses are not a frozen review input. Final Feature/Behavior/Architecture/Spec/evidence/index reconciliation is **not verified by this Group2 code/test review**. Stale preambles were not converted into code defects. Documentation closure remains with the authorized implementer/coordinator. The observed Spec is APPROVED in `specs/active/`; this reviewer neither edits its lifecycle nor claims cloud delivery.

## Per-File Necessity And Placement

All paths are relative to REPO_ROOT. Every listed task operation is modify; repository tracking state is not inferred from task headers.

| File | Task change | Necessity and consequence of omission | Placement | Redundancy / unintended edits |
|---|---|---|---|---|
| `apps/api/src/push_kids/agent_processing/checkpoints.py` | +17/-1: narrow semantic purge | necessary: one owned, tenant/child/submission-scoped operation for both callers; omission retains decisions or duplicates SQL | correct: temporary-stage persistence owner | none confirmed; cast describes DELETE result, not untrusted domain input |
| `apps/api/src/push_kids/agent_processing/worker.py` | +24/-1: guarded terminal purge and safe cleanup telemetry | necessary: implements final semantic cleanup without modifying retryable recovery | correct: existing failure transaction after lease/scope guards | none confirmed; original unknown-SQL handling remains |
| `apps/api/src/push_kids/learning/service.py` | +28/-3: lock/refresh scope, purge, lease reset | necessary: explicit retry must receive fresh decisions and serialize existing/missing-job transitions | correct: learning retry use-case transaction delegates stage SQL | none confirmed; existing repair and archive semantics retained |
| `tests/integration/test_analysis_checkpoints.py` | +292/-0: eight test functions, 13 parameter-expanded cases | necessary: persistence scope, terminal/recoverable paths, rollback and stale-write assertions are absent without additions | correct: existing SQLite/API/worker checkpoint suite | none confirmed; source assertions have independently derived expectations |
| `tests/integration/test_staged_mysql.py` | +274/-1: five test functions, six parameter-expanded cases; fixture helpers | necessary: real locking contention, missing-job serialization, late checkpoint and transactional rollback need dialect-level regression paths | correct: existing conditional isolated MySQL suite | none confirmed; family-scoped fixture cancellation prevents new queued-job residue |
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` (shared) | +1/-1: revision09 -> staged-20261101-10 | necessary: separates the approved cache runtime contract from old checkpoints | correct: shared revision owner | no prompt/DTO change in this task hunk |
| `apps/api/src/push_kids/agent_processing/pipeline.py` (shared direct context only) | +20/-11: final-refusal reuse filter and nonretryable outputs | necessary: worker requires unambiguous terminal inputs, and final refusals must not be reusable | correct: pipeline outcome/cache eligibility policy | full Group1 behavior audit not claimed here |

## Unverified Scope And Residual Risk

- No test, linter, formatter, type checker, architecture checker, deployment, production query or commit was run. Only local reads/hash checks and these two report artifacts were performed.
- Actual SQLite/MySQL execution, timeouts, connection failures, query plans and concurrent schedules are not independently evidenced. In particular MySQL 8 context cannot establish the required MySQL 5.7.18 compatibility/locking gate.
- New failure mocks throw before commit. Post-commit acknowledgement loss, fresh-session recovery after that event, and terminal cleanup failure on a real MySQL connection were not reproduced. Static control flow preserves the existing protection: SQL failures propagate without a compensating failed/queued rewrite; exceptions in terminal cleanup leave the session context to roll back instead of entering another failure handler.
- Added negative fixtures do not independently demonstrate a same-family different-child boundary or corrupted cross-scope associations. The DELETE's explicit child predicate was verified statically; no such defect was established.
- No exhaustive formal-table fingerprint or runtime Review/Feedback/Occurrence write check was performed. The static changed write set is limited as described above.
- No whole-HEAD, unrelated feature, native/device/content-quality, provider live-output or complete Group1 review is claimed. Final documentation closure and cloud-delivery/lifecycle evidence are separate.
- The finish-time worker increment is excluded from this snapshot review and requires separate affected-scope review. Zero findings here must not be presented as a conclusion on its newer hash.

Summary: five primary files are necessary and correctly placed; two shared boundaries are necessary and correctly placed within the inspected scope. Zero questionable/unnecessary/misplaced files or safe deletion recommendations. Correctness conclusions are static, source-hash-bound assessments only; runtime and documentation-closeout conclusions remain unverified.
