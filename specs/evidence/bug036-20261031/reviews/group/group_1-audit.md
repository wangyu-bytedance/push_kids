# BUG-036 Group 1 independent read-only review

- Date: 2026-10-31; scope: approved `BUG-SPEC-20261031-KNOWLEDGE-GENERATION-01`, `ARCH-20261031-KNOWLEDGE-GENERATION-01`, Prompt04.
- Baseline: `/private/tmp/push-kids-bug036-baseline-20261031`, not git HEAD. Workspace contains unrelated existing edits.
- Reviewed code: frozen `/private/tmp/push-kids-bug036-review-20261031/snapshot/`; task diffs under `diffs/` use suffix `.diff` replacing `.py`.
- Manifest: all 14 snapshot entries were SHA-256 verified with **0 mismatches**. Main pipeline hash `5a58e3a86691ee49f596e6271e9e739f969d0ccca78667134eb60bfe0cc519bb`; stage_contracts `8532c172af3344a03efdcff068376ff2e72f4c7779fbef7e83fc8262c2a60674`; prompt `bcaad016726eb04d6475a35d25c64394f9cf9f36b037fc0791fd5f03e27986a3`.
- Followed bits-code-guard general-workflow 3.1–3.4, review-dimensions and review-rule. No Python-specific language supplement exists in that workflow. Read AGENTS.md, REVIEW.md, approved Spec/Prompt04, FEAT-001, relevant Behavior/Architecture, direct contracts/runner/history readers and context builder for the concrete capacity path.
- Result: **3 confirmed P1 findings**, `BUG036-G1-01` through `BUG036-G1-03`, in `group_1.jsonl`. No code, docs or tests were edited. Only this review directory received handwritten review results. No production DB, external model, cloud deployment or business API call was used.

## Per-file necessity, placement and evidence

| File | Action / task diff | Necessity | Placement | Evidence and residue |
|---|---|---|---|---|
| `apps/api/src/push_kids/agent_processing/pipeline.py` | modify +297/-97 | necessary: prior pipeline cannot account for omitted candidates, locate correction members, recover structural errors or review substituted historical names; **questionable additional global320 cap** | correct owner for ledger, orchestration, alias resolution and validation; G1-01 requires explicit bridge to existing public validation semantics | Inspected full changed functions and direct callers. Region check preserves unaffected item/member/evidence dictionaries; review consumes omissions; all-omitted stays non-actionable. No arbitrary name fallback or new business writer. G1-01/G1-03 remain. No broad style/refactor request. |
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` | modify +177/-61 | necessary: omission/basis/reuse DTOs and shared quality/history rules implement approved scope | correct domain/provider-neutral stage contract owner | Strict extras, count/length/enums and revision remain; few shots appear only at the end. Shared OUTPUT_RULES is valid for alias-only stages; its legacy consumer is inappropriate under G1-02. Prompt wording is evidence of the required contract, not measured model accuracy. |
| `apps/api/src/push_kids/agent_processing/prompt.py` | modify +16/-26 | necessary: legacy quality/history rules must follow same approved semantics | acceptable consumer of shared quality/history rules; **alias-only OUTPUT_RULES is misplaced for legacy output contract** | ID-emitting legacy schema and its own transport rule contradict newly appended output permissions. G1-02. No second generator or new helper module was introduced. |
| `tests/staged_analysis_fakes.py` | modify +117/-2 | necessary: omission fields, alias dictionary, new reuse stage and bounded maximum stage positions require adapter updates | correct test-only adapter placement | Reuse fake accepts by default; MaximumStages deliberately creates first failures and counts positions. These prove orchestration/resource invariants and cannot demonstrate semantic judgment or the real 30-case outcome. |
| `tests/unit/test_staged_analysis.py` | modify +155/-21 | necessary: local structure recovery, queue deadline delegation, omission review and explicit correction aliases | correct unit scope | New assertions can fail on old deadline and missing omission/alias payload. Single-target alias test alone cannot prove unaffected-item integrity; the new TwoTargets case supplies that separate evidence. Shared prompt count/end tests only verify composition. |
| `tests/unit/test_staged_proposal_recovery.py` | add +418/-0 | necessary: real observable proposals/failures, unchanged target guard, selected-history verification and capacity budgets | correct unit scope | Covers reject with different old name, accept, uncertain, corrupt aliases, same-day resolved bad old name, drift, invalid/all omissions, 20queries/100history/512KiB,18/33calls. **Missing explicit same-name reject and legitimate multi-subject global-directory boundary**, now reproduced independently. Null-match test permits public guard failure and must not redefine approved reject fallback. Supported-knowledge omission test configures the fake reviewer to reject; it verifies gate wiring, not model ability to detect unsupported omission. |
| `tests/unit/test_provider_evidence.py` | modify +5/-12 | necessary mechanical adjustment to shared rules/revision | correct unit scope | Checks rule inclusion and few-shot placement, direct evidence and transport constraints. Does not detect ID permission conflict. No live provider success claim. |
| `tests/unit/test_analysis_context_contract.py` | modify +3/-3 | necessary adjustment from removed examples to shared rules | correct unit scope | Checks current prompt text/structured context, not its semantic output or scale. No new behavior-only test duplicated production implementation. |

Necessary files: all eight above. Questionable change: global320 registration cap in pipeline. Unnecessary files: none confirmed. Misplaced content: alias-only output rule in legacy prompt. Safe deletion: remove that inappropriate legacy inclusion while preserving applicable shared constraints; no other deletion is proposed. No new unowned abstraction, module dependency inversion or unrelated production rename was found within this scoped diff.

## Executed validation and reproducible triggers

The first standalone Python reproduction attempt did not set the repository `apps/api/src` import path and failed with `ModuleNotFoundError: push_kids`; it is an environment setup failure, not Red evidence. Subsequent checks inserted that path and inserted frozen `agent_processing` into the package search path before loading task modules. The loaded pipeline path was printed and confirmed to be the frozen snapshot. Synthetic material/context stays in process memory. `PYTHONDONTWRITEBYTECODE=1` and pytest `-p no:cacheprovider` were used for completed review checks.

Executed frozen unit suite through `UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python`, then `pytest.main` with repository `pyproject.toml` and the four frozen unit paths for staged_analysis, staged_proposal_recovery, provider_evidence and analysis_context_contract: **76 passed in 4.99s**. No integration or production DB fixture was selected. This does not establish acceptance of the three missing/contradictory contracts.

The shared setup for no-DB reproductions was:

```python
import sys

sys.path.insert(0, "/Users/bytedance/Documents/push_kids/apps/api/src")
import push_kids.agent_processing

push_kids.agent_processing.__path__.insert(
    0,
    "/private/tmp/push-kids-bug036-review-20261031/snapshot/apps/api/src/push_kids/agent_processing",
)
```

**G1-01 single target:** use `HistoryReview('reject')`, `history_input('十以内加法', method='主动回忆', evidence='只口述加法含义，没有变式运算练习')`, then `run(provider,data)` from the reviewed `test_staged_proposal_recovery` helpers. Current target has `review_method=变式练习`; historical has `主动回忆`. Output: `AnalysisOutputValidationError: proposal.actionable_items`; `reuse_count=1`.

**G1-01 mixed batch:** subclass HistoryReview, delegate extract/merge to TwoTargets, return `QualityReviewResult(passed=True,issues=[])` for review, keep HistoryReview reject decisions for match/reuse. With same identical-name history input and text `十以内加法和十以内减法`, review/match/reuse covers i0/i1. Output: points=`['十以内减法']`, matches=`[]`, uncertainty=`数学“十以内加法”是已有知识，未作为新学条目输出。`. Expected both reviewed current targets to survive explicit rejects. This loss comes from unchanged normalized-name public guards, not from extraction or reviewer fakes. Same-day new-name collision has the parallel guard at contracts.py:425.

**G1-02:** source contract inspection confirms prompt.py:36–37 and45–47 require valid database IDs for historical output, and ANALYSIS_RULES appends OUTPUT_RULES, which forbids them at stage_contracts.py:152. This is an unsatisfiable prompt contract for historical legacy output. No real model call was used to estimate incidence.

**G1-03:** custom fake emits one mathematics current target and one English current target, both with direct parent-text evidence; quality passes and match would return null for both. Construct200 SameDayKnowledgeContext (100 per subject),120 TodoCandidate today-plan entries (60 per subject), all distinct IDs. Search closure appends20 distinct ExistingKnowledgeContext per call, scoped to request subject, matching how the Runner updates trusted context. Two calls leave40 distinct history and180 options per subject. Frozen pipeline reports `{reason: 'capacity', stage: 'match', unit: 'history_options', queries: 2, history_results: 40, same_day: 200, today_plan: 120}` before match. Production context.py bounds the same-day rows at200 and consumes the complete plan; provider context explicitly documents max120. Baseline pipeline bounds each candidate at320 and has no global320 registration limit. Payload values were short, so this did not exercise the512KiB fallback.

## Contract and confirmation limits

G1-01 affects generation's bridge into `AnalysisInput.validate_model_result`, especially normalized-name suppression at contracts.py:425–426 and438–443. Any narrow fix must carry trusted candidate/knowledge decision provenance and preserve the public DTO, identity/evidence/tenant checks, legacy defaults, and the final actionable-proposal gate. A generic client or model field that disables duplicate checks would not be equivalent. The downstream `AnalysisAgentRunner.validate_final` still checks proposal references and the successful scoped search ledger; it must continue to do so.

Generation and confirmation are separate: these reproductions never exercised the formal confirmation transaction. Downstream formal learning confirmation canonical identity remains unchanged and outside this generation task. Same-name knowledge linking/deduplication during an eventual parent confirmation has **not** been verified by this review and remains an acceptance limitation; a new same-name proposal does not prove creation of separate formal knowledge identities. The current approved task does not permit storage cleanup, renaming old records or automatic confirmation.

## Required current-document reconciliation (implementer scope)

| Current source | Status against frozen task | Required update / owner |
|---|---|---|
| `docs/domain/features/FEAT-001-push-kids-mvp.md:208` generation paragraphs and rule/revision paragraphs around233 | stale for local code; old038 delivery remains valid history | Replace current all-candidates-in-items language with complete items/omissions ledger, reviewed reasons, no empty proposal, explicit correction region, strict historical scope/skill/evidence, final alias-only reuse gate and reject/uncertain behavior. Distinguish local -07/-11 from gray038 -06/-10. Update accurate queue/execution/review budgets; owner TRAE. Do not claim G1 findings fixed before rerun. |
| `docs/domain/BEHAVIOR-CATALOG.md:30` BHV-032 plus top generation increment | stale/missing current local behavior; old delivery evidence is historical | Add/reconcile independent quality/correction+omission and final reuse stages,20queries/100history/512KiB and no business writes; preserve public/manual/parent confirmation behavior. BHV-003/BHV-014 remain legacy context and must not be silently rewritten as staged execution. Owner TRAE. |
| `docs/architecture/ARCHITECTURE.md:168` Current staged pipeline and capacity paragraphs | stale: names -06, no reuse gate,14 rows, queue-inclusive stage wording | Record local -07 pipeline order/ownership, payload dedup/budgets, queue-vs-model execution ownership,18/33 calls,18 successful checkpoint keys, shared quality/history rules with compatible legacy output. Preserve old038 delivery and rollout facts. Owner TRAE. |
| Active BUG-036 Spec and `specs/README.md`, `specs/STATUS.md` | approved; implementation/evidence closure not yet reconciled | Record actual Red/Baseline/Green, these review findings/disposition and version, local checks and semantic retest limits. Reviewer metadata currently says no child agent delegation; actual independent grouped review should be described truthfully. Keep active without matching cloud delivery, do not set DONE/completed from local tests. Owner TRAE. |
| Issue/regression/evidence inventory | missing task-final evidence in scope supplied | Link confirmed findings and narrow fixes, identity/same-name/multi-scope replay contracts, exact snapshot/hash and commands. No old793 suite or038 evidence can count for this diff. Owner TRAE. |
| UI current-state and frontend constraints | aligned for no UI code changes; native acceptance not exercised | Explicit no frontend design/engineering change; do not convert backend content checks into native/device/accessibility PASS. Existing gates remain. |
| Release docs | prior038 stage remains historical; no current cloud delivery | Retain uploaded/gray/experience/review/production distinctions, record this local-only increment. No release playbook was executed. |

Current documentation was intentionally not edited by this reviewer. Stale items above are closure actions, not extra code findings. No discovered wording ambiguity requires a new product decision: approved AC-006 specifically requires reject fallback while old guard behavior is an implementation mismatch.

## Remaining evidence limits

- Real same30-source Doubao retest, session C1–C6 semantic judgments and original6 PASS preservation: NOT_RUN by this reviewer; fake gates cannot prove model quality.
- Production READ ONLY before/after61-table audit and private original-image cleanup: NOT_RUN here; no production source/artifact was fetched.
- Full backend unit/integration/contract, Ruff/mypy/architecture checks and checkpoint/provider/telemetry behavior: not run by Group1 beyond the76 unit tests; second reviewer/implementer owns those evidence claims.
- Native Mini Program, cloud delivery and formal parent confirmation: NOT_RUN / outside this group task.
- Dynamic contexts were reviewed through direct service/contract callers; no deeper codebase-wide recursion or external systems assumptions were used. No security or business-write defect was confirmed within the frozen group.
