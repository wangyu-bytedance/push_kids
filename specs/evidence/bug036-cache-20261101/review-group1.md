# BUG-036 Cache Spec02: Independent Group1 Review

## Verdict

**0 confirmed findings.** No actionable P0/P1/P2 code or test defect was identified in the exact Group1 increment. This is a static Group1 conclusion, not a whole-task approval, test PASS, documentation-closure approval, or release authorization.

- Reviewer: independent Group1 reviewer; no other group's conclusions consumed.
- Date: 2026-11-01.
- Policy: `REVIEW.md`, `REVIEW-20261028-01`; repository `AGENTS.md`.
- Skill: `bits-code-guard`, `general-workflow.md` Steps 3.1-3.4, `review-dimensions.md`, and `review-rule.md`.
- Approved scope: `BUG-SPEC-20261101-KNOWLEDGE-CACHE-02`, `ARCH-20261101-KNOWLEDGE-CACHE-02`.
- Feature: FEAT-001; Spec-declared baseline `FEAT-STATE-20261031-KNOWLEDGE-GENERATION-07`.
- Review depth: R2 independent static inspection. Confidence is high for the narrow cache classification and failure propagation inspected, not for unexecuted runtime acceptance.

## Snapshot And Boundaries

- `SKILL_ROOT`: `/Users/bytedance/.trae-cn/skills/bits-code-guard`.
- `REPO_ROOT`: `/Users/bytedance/Documents/push_kids`.
- `WORK_DIR`: `/var/folders/hq/l74_1q417nbdffshwhtw79640000gn/T/tmp.QmgzUCkpZn/review`, already existing.
- Authoritative delta: [task.diff](task.diff), not the whole HEAD diff.
- Authoritative source identity: [source-manifest.json](source-manifest.json).
- Base: `0576ac304649 plus pre-task snapshot`, as supplied. The pre-task diff distinguishes this cache increment from earlier BUG-036 prompt/implementation changes.
- Group1: four modified files, 101 added and 14 removed lines, including blank diff lines. The complete task manifest's 756 changed lines is not Group1's review size.
- Final `task.diff` SHA-256: `ae1571aadb25141fdc5a2f64d28f3cddb85ee32df3bfcd5ee2fe289713e65e48`.
- Final `source-manifest.json` SHA-256: `ce15f7d9290550004df546c35393ed7111337793d4780a87677b04bfab643ca3`.
- Initial identities, before the import-order-only refresh described below: `task.diff` = `08fd96fe77b339841faa3a4ada1a101c17e5ba960f97494fb1ab86a71565e44d`; `source-manifest.json` = `36dfaeba36236c572618f1841412e2a9e9615cf9c0204ea5a6c6fdc019828dfe`.

All four Group1 sources matched the manifest on initial and final source checks:

| File | SHA-256 |
|---|---|
| `apps/api/src/push_kids/agent_processing/pipeline.py` | `d14bb5682a75d9bd734e039f110b5a46de0c081b6b3537c95307f5a666b3c4ac` |
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` | `056cd0eb6bde33429c6eb56c9f9b11c7a96237671a6378046490ca2c18df6e6a` |
| `tests/unit/test_staged_proposal_recovery.py` | `0251062bcea8b109990737f9b487d436e4cda3f04382fae2f44876e3efb5a313` |
| `tests/unit/test_staged_analysis.py` | `8bb19e2cd44a257f8ccfab25451d6fc947ef9600b1426db5ef1b181778606bbb` |

Context read: complete affected pipeline functions and nested validators, runner, `StageFailure`, failure disposition, checkpoint get/put and guards, worker result consumption, stage provider/deadline handling, stage I/O, telemetry, shared test fakes, and relevant recovery integration cases. Group2 persistence changes were read only as boundary context, not independently signed off here.

Auxiliary snapshot observation: live `worker.py` hashed to `32f8cb9f7b4a7e181ae4227bbffadfa5f2c582c4cfabf02ae8528f7172cbc2b8`, rather than the initial manifest's `1098f52db7aad2a9323b1a6b2f0f78884722aea6391a4d14b20d7ee75bfcc920`. A read-only stream swapping lines 32 and 33 reproduced the initial manifest hash exactly. The discrepancy is limited to ordering the `runner` and `stage_contracts` imports; inspected function bodies are unchanged. The supplied whole-task diff/manifest were subsequently refreshed outside this reviewer to the live worker hash. The final Group1 hunks, counts and all four source hashes remain unchanged. This is not a code finding or an unresolved Group1 snapshot mismatch. Checkpoint and recovery-integration context files matched their manifest hashes.

Excluded: unrelated travel/BUG-037 changes, earlier BUG-036 prompt behavior, production data, live model content evaluation, full Group2 review, and current documentation closure. Python has no language-specific rules in this skill; generic dimensions remain applicable.

## Per-File Necessity And Placement

| File / change | Main change | Necessity and counterfactual | Placement | Redundancy / accidental edits |
|---|---|---|---|---|
| `agent_processing/pipeline.py`, modify, +20/-11 | Gate checkpoint reads/writes by final semantic outcome; mark final quality and reuse uncertainty nonretryable | **necessary**: without the gate a structurally valid final refusal remains reusable; without the two explicit flags the worker still automatically retries it | **correct**: result semantics belong to the existing pipeline, while durable deletion remains with the checkpoint/transaction owners | None identified; one predicate serves both read and write |
| `agent_processing/stage_contracts.py`, modify, +1/-1 | Change pipeline revision from `staged-20261031-09` to `staged-20261101-10` | **necessary**: otherwise old execution-contract checkpoints remain eligible under the same revision | **correct**: existing shared revision owner consumed by fingerprinting and checkpoint validation | No DTO, prompt-rule, signature, or speculative extension change in this delta |
| `tests/unit/test_staged_proposal_recovery.py`, modify, +79/-1 | Assert actual terminal exception flags; add seeded/unseeded two-call cache policy matrix | **necessary**: prior outcome-only assertions cannot distinguish automatic retry semantics or final refusal cache hits/writes | **correct**: existing staged outcome/recovery test module, with local test doubles | No duplicate production path or persistent harness; matrix covers distinct read/write/result cases |
| `tests/unit/test_staged_analysis.py`, modify, +1/-1 | Synchronize the explicit revision assertion | **necessary**: the old assertion would reject the required revision bump | **correct**: existing pipeline contract assertion | No unrelated assertion rewrite; reconstructed supplemental revision assertion is not Red evidence |

Necessary files: all four. Questionable, unnecessary, or misplaced files: none in Group1. Safe deletion/revert candidates: none identified in this approved increment.

## Seven Required Repository Dimensions

### 1. Functional Correctness

Static alignment with AC-C01/C02/C04 is supported by these paths:

| Requirement | Implementation and caller evidence | Assessment |
|---|---|---|
| Final `review1.passed=false` is neither a cache hit nor a new reusable write | `pipeline.py:78-84,109-124,143-157`; `_call` first performs schema and supplied reference validation | Aligned by static inspection |
| Intermediate failed `review0` remains recoverable | The predicate restricts quality refusal exclusion to `review1`; `run:414-464` always routes failed review0 through bounded correction and review1 | Aligned; no bypass of final review found |
| Passed final review and accept/reject reuse results remain recoverable | Predicate preserves passed review1 and requires no uncertain decision across the entire reuse result | Aligned |
| Final quality refusal stops automatic retry | `pipeline.py:464-474` raises the explicit nonretryable stage/unit; runner preserves it; `contracts.py:209-230` consumes `exc.retryable`; worker checks disposition before requeue | Aligned at inspected boundary |
| Final reuse uncertainty cannot guess a new proposal | `pipeline.py:677-710` validates complete selected aliases and match identities, then raises nonretryable validation on uncertainty before assembly | Aligned; explicit reject still clears the match and retains the reviewed target |
| Fingerprint/revision and original limits remain effective | `pipeline.py:98-108,125-156,230-243`; checkpoint revision/TTL and write limits; unchanged provider absolute deadline and request slots | No expansion or validation bypass introduced |

AC-C03 manual-retry locking/deletion and the full worker transaction are Group2 responsibilities. AC-C05 live material/content evaluation is outside this review. AC-C04 still permits the existing optional coverage call outside the core 18/33 pipeline positions; this increment does not change it.

### 2. Design Rationality

The change addresses the stated cause: caching a valid DTO does not imply a successful semantic decision. It separates recoverability from final proposal acceptance without deleting all intermediate work or adding model retries. Keeping review0 refusal is essential to correction recovery rather than a broad false-result exclusion.

No new module, dependency edge, provider interface, transport field, shared cache framework, or extension point is introduced in Group1. `_call` keeps existing validation and checkpoint serialization; `run` keeps terminal result decisions. There is no exception swallowing or unbounded retry introduced by this delta.

### 3. Modification Necessity

The per-file counterfactuals above account for every Group1 change. The revision update and test assertions follow the approved execution-contract change. No unrelated refactor, prompt adjustment, or metadata churn was included in the exact Group1 delta.

### 4. Placement

Semantic reuse policy stays in the pipeline; the common contract revision stays in `stage_contracts.py`; regression assertions stay with existing staged analysis tests. Durable lease/tenant/transaction enforcement remains with checkpoint and worker/service owners. No domain policy was moved into a router, framework module, or unowned common utility.

### 5. Redundancy And Residue

The new predicate has two real consumers, preventing read/write policy divergence. Generic retryable `StageFailure("quality")` remains supported, but the actual final-review path now opts out explicitly; this does not require globally changing every quality failure.

Uncertainty at the earlier matching stage remains the existing behavior and is not the approved final-reuse uncertainty change. Old terminal checkpoint rows are ignored by the predicate, with semantic cleanup owned by Group2. Existing rollback/legacy-provider code is not made obsolete by this increment. No new dead path, duplicate DTO, orphan abstraction, temporary flag, or safely deletable code was identified.

### 6. Test Effectiveness

These are source-inspection conclusions, not executed test results:

| Test / inspected lines | What can fail meaningfully | Limits |
|---|---|---|
| `test_staged_proposal_recovery.py:505-577`, 12 seeded/unseeded matrix cases | Checks provider-call and write counts independently of the production predicate; seeded final refusals must invoke the provider, fresh final refusals must not write, second calls distinguish reuse from regeneration; review0 refusal and passed/accepted/rejected controls catch overbroad exclusions | Local store and no-op validation intentionally isolate policy; not a TTL, SQL, lease, or complete worker-attempt test |
| `test_uncertain_reuse_never_falls_back_to_new`, lines 129-135 | Calls real `run`, captures the actual exception and requires `retryable=False`; keeps one reuse invocation | No durable storage in this unit case |
| `test_review_cannot_hide_supported_knowledge_in_omissions`, lines 299-306 | Calls real run/correction/review1; captures actual terminal flag, two review calls, no history queries, and preserved omission members | Does not by itself prove worker requeue suppression |
| Existing `test_staged_analysis.py` validation/deadline cases, lines 123-223 | Real pipeline paths reject inconsistent passed/issues and aliases, invalid material/reference coverage, and expired deadlines; supplied deadline reaches provider unchanged | Unexecuted; no new cache-validation-specific assertion was added |
| Existing maximum-position case, `test_staged_proposal_recovery.py:486-502` | Independent expected 18/33 counts and final output detect budget drift | Unexecuted; core pipeline budget only |
| Integration context `test_analysis_checkpoints.py:394-448` | Real worker terminal failure/manual retry and transport-interrupted correction; counts and persisted keys require extraction/merge/review0 recovery and a later final review, not skipped acceptance | Read as Group1 boundary evidence; belongs to Group2, not executed or fully reviewed here |
| Integration context `test_analysis_checkpoints.py:511-558` | Worker reuse uncertainty ends at attempt 1, retains extraction, and creates no formal learning record | Same Group2/runtime limits |
| `test_staged_analysis.py:75` | Explicit revision identity catches a missing contract bump | Supplemental reconstructed assertion is not pre-fix Red evidence |

The unchanged `test_quality_review_rejects_after_one_failed_correction` creates a separate generic `StageFailure("quality")` when asserting retryable disposition; it does not test the actual caught exception's flag. That old assertion is not evidence of terminal behavior, and is not an introduced defect in this snapshot. The changed recovery tests do inspect the actual exceptions.

From the baseline side of `task.diff`, the new refusal-cache counts and terminal-flag assertions are capable of detecting the old policy. No baseline replay, mutation check, or Red/Green run was performed by this reviewer. Claimed focused 80-pass and MySQL 8-pass results remain context only, not inherited verification.

### 7. Documentation Validity And Consistency

The approval block and AC-C01-C04 of the specified active Spec were read as the authoritative cache contract; FEAT-001's applicable learning/confirmation, history, recovery, and budget facts were read as context. No Group1 implementation deviation from the approved cache semantics was identified.

Final current-state document closure is **NOT VERIFIED / explicitly deferred** by the user's code/test-only assignment. Stale FEAT-001 preambles and Spec test-status/lifecycle prose observed during that work are not reported as code defects. Behavior Catalog, Architecture, final evidence/index reconciliation, and release-document closure are not signed off here.

The coordinator remains responsible for merging final facts, distinguishing static/local testing from content acceptance and cloud delivery, and reconciling all current prose and references. No repository document was modified or synchronized by this reviewer. The Spec was observed as `APPROVED` at `specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md`; its status/location was not changed.

## Generic Skill Dimensions

All seven generic dimensions were considered separately from the repository dimensions:

- Logic: symmetric cache policy, complete final-outcome branches, unchanged validators and fingerprint consumers.
- Business semantics: refusal versus intermediate correction, nonretryable terminal errors, reject preserving new proposals, parent-confirmation boundary.
- Security: no new identity source, raw-content logging, external input, persistence type, or formal-write path; existing tenant guards read as context.
- Concurrency: predicate is stateless; existing checkpoint lock, stage I/O, runner isolation and worker late-result guards retain their roles.
- Robustness: schema/reference validation precedes cache acceptance and writes; terminal flags reach disposition; transport and validation errors retain original finite recovery.
- Performance: no added query, larger DTO, loop, or key budget; refusal misses consume the existing call/deadline budget.
- Quality: necessity, placement, duplication and retained consumers inspected; no style-only finding emitted.

## Independent Evidence And Unverified Scope

Executed by this reviewer: read-only `cat`, `sed`, `nl`, `rg`, `ls`, `awk` and `shasum` inspection, including exact diff counts and source hash comparisons. The worker import-order comparison used only a stream:

```bash
awk 'NR==32 {previous=$0; next} NR==33 {print; print previous; next} {print}' apps/api/src/push_kids/agent_processing/worker.py | shasum -a 256
```

Not executed: tests, pytest collection, Red/Baseline replay, Ruff/format, mypy, architecture or design validators, MySQL queries/tests, deployments, production queries, model calls, commits, or repository edits. No runtime PASS or release-ready conclusion is asserted.

Remaining limits: full Group2 transaction/concurrency review, runtime cache and cancellation behavior, required complete-suite/static/MySQL evidence, final current-state documentation closure, and independent live-model content acceptance. Any subsequent substantive source or delta change requires renewed affected-scope review. Missing runtime evidence is not a fabricated code finding.

Only report artifacts `group1.jsonl` and `group1.md` were written in the existing private review directory. `group1.jsonl` contains zero finding records; no placeholder or non-schema finding is emitted.
