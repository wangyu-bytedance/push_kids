# BUG-036 Content03 Independent Review: Group 1

- Date: 2026-11-01. Reviewer: independent Group1 review session; read-only.
- Decision: **1 confirmed P1 / MAJOR finding**, confidence 9/10. Not a complete-patch approval.
- Stable finding ID: **BUG036-C03-G1-001**, corresponding to the single JSONL entry titled "Use audited material ownership when authorizing material corrections".
- Artifacts: [findings](group/group_1.jsonl) and this audit only.
- SKILL_ROOT: `/Users/bytedance/.trae-cn/skills/bits-code-guard`.
- REPO_ROOT: `/Users/bytedance/Documents/push_kids`.
- WORK_DIR: `/Users/bytedance/Documents/push_kids/specs/evidence/bug036-content03-20261101/review`.

## Scope And Version

The authoritative scope is [manifest.json](../manifest.json) and [content03.diff](../content03.diff), approval baseline `staged-20261101-10 / child-aware-history-agent-20261031-13` to candidate `staged-20261101-11 / child-aware-history-agent-20261101-14`. Minus lines are old; plus lines are new. `diff_stats.json` and the HEAD inventory are not this review's patch.

Reviewed seven Group1 files: pipeline, stage contracts, legacy prompt revision, shared staged fakes, staged analysis tests, proposal recovery tests, and provider evidence tests. Their retained patch has **639 additions / 94 deletions, 733 changed lines**. Full affected functions and their direct contracts were read, not just hunks.

Verification actually performed:

- All 22 baseline/current file snapshots and all 11 retained check artifacts matched the manifest SHA-256 values.
- Reconstructed unified diffs from every retained baseline/current pair exactly matched `content03.diff`.
- Diff SHA-256: `956450b1ab80f611dc4a7deeb7bffdbd377802b763df40fba06063c501c0dcc7`.
- All 11 live implementation/test files matched the retained current hashes at the verification step. Review reasoning and runtime probes still used retained snapshots, not live source or git HEAD.
- Pipeline current SHA-256: `b6b958d0300ad0a6f3ee825ef95fa9d3756e782e1a63306a5d40696b99441b78`.
- Stage contracts current SHA-256: `b23d6ab0aaf67784e4e4701dbdc65db9b45c25a8722f2b5d984d475932670a64`.

Read `REVIEW.md` revision `REVIEW-20261028-01`, the approved Content03 Spec, Prompt05, review groups/files, the skill's general workflow Steps 3.1-3.4, all seven dimensions, and grading rules. Python has no language supplement. The retained custom workflow list is empty; no external workflow was fetched. No other group's findings were read.

Approval evidence is the Spec's Product owner confirmation dated 2026-11-01: "approved BUG-036 Content Spec03, including Architecture03 and Prompt05", recorded there in the original language. Implementer/merge owner is TRAE per Spec. Commit author/committer and MR identity are UNAVAILABLE for this retained working-tree patch; they were not inferred from HEAD. This review grants no implementation, commit, deployment, or acceptance approval.

## Confirmed Finding

### BUG036-C03-G1-001: Obsolete Candidate Provenance Expands Correction Authority

- Classification: P1 / MAJOR, conditional functional defect, introduced by Content03; confidence 9/10.
- Location: [pipeline.py:483-495](file:///Users/bytedance/Documents/push_kids/apps/api/src/push_kids/agent_processing/pipeline.py#L483-L495), especially the union with candidate materials at 486-489. Further expansion occurs at 500-504; the resulting entries are no longer protected at 512-517.
- Authority: approved Content03 AC-S02 says candidates are fallible hints and formal evidence has one owner. AC-S03, lines 99-102, permits material-local correction but forbids changing other sources' passed targets and requires deterministic scope checks.
- Trigger: `c1.materials=["m1"]`; consolidation has corrected `i0` to `evidence_keys=["e0"]`, with `e0.material="m2"` and source checks showing only m2 supports i0. First review reports only an m1 teaching-role issue.
- Actual: `entry_materials(i0)` becomes `{m1,m2}`, so i0 is affected instead of protected. A correction changes its name without an i0 or m2 issue. The validator accepts it, second scripted review passes, history runs, and the changed m2-only target reaches the proposal.
- Expected: reject the unauthorized m2-only target drift before second review/history. The m1 source-check correction itself may proceed.
- Concrete verification: retained snapshot execution with a scripted Provider and two existing non-sensitive snapshot files as inert source bytes. No vision model, image creation, database, or checkpoint storage.
- Control: candidate attribution also on m2 rejected the same correction at `merge`, `stage.members:reference`, zero history queries. Candidate attribution on m1 accepted it and made one history query.
- Existing protections checked: merge reference validation and source-check equality both accept the initial audited m2 attribution; protected-entry comparison does not apply once i0 enters `affected_entries`; later model review is not a deterministic scope guard.
- Repair owner: authorized implementer TRAE. Separate omission attribution from item ownership: items use audited evidence, while omissions may need candidate-source lineage. Add the migrated-attribution rejection regression, then repeat affected correction/evidence/cache checks. No repair was made.

This is an authorization-boundary reproduction, not a claim about the probability of a particular model response or visual recognition quality. Other material-associated corrections should not be prohibited by an unrelated semantic heuristic.

## Seven Dimensions

| Dimension | Assessment and concrete evidence |
|---|---|
| Logic | Source payload reaches merge/correction/review0/review1; review receives summary, uncertainties, evidence, source checks, items and omissions. Candidate membership remains exactly-once. G1-001 is the confirmed correction-set error. |
| Business semantics | Final evidence/confidence and history facts use the formal directory, not extraction confidence. Legal subject correction and empty candidates are supported. q/i/o protections and evidence identity preservation exist; material ownership is incomplete under G1-001. Parent-confirmation and deterministic planning boundaries are unchanged. |
| Security | No new identity/query authority, raw-output logging, credential, image persistence, SQL, or command execution in Group1's patch. Aliases are validated against supplied sources/items. Inputs remain untrusted in shared instructions. Formal evidence text is not added to telemetry. No broader security approval is inferred. |
| Concurrency | Source and correction sets are run-local; the existing checkpoint lock remains. No new global mutable production state or transaction ownership. Real concurrent source changes, cancellation, request slots and storage recovery are Group2/retained integration context, not freshly verified here. |
| Robustness | Bounded DTOs, existing/unique evidence references, exact per-source ledger, legal subjects, nonblank detail/basis, and nonempty public proposal safeguards are present. Missing/foreign/duplicate references, empty evidence keys, all-omitted output and reuse uncertainty have failing assertions. New content-empty extraction can reach source verification. |
| Performance | Item/evidence/source collections remain bounded at 20/40/10; candidate accounting is capped at 200 and history at 20 queries/100 results. Rebuilding a 40-entry directory per item is bounded, not a meaningful performance finding. SHA reads and image/request resource limits require Group2 assessment. |
| Quality | Changes fit existing orchestration/DTO/prompt/test owners; no new generic shared module or dependency direction. No pure style/length/naming finding was reported. The fixture helper is protocol scaffolding, not semantic ground truth. |

## Per-File Necessity And Placement

All classifications below concern the retained Content03 delta, not earlier staged/cache work.

| File | Action; delta | Why necessary / what remains broken without it | Necessity | Placement | Residue / incorrect change |
|---|---|---|---|---|---|
| `apps/api/src/push_kids/agent_processing/pipeline.py` | modify; +194/-52 | Original-source visibility, directory/ledger validation, authorized corrections, formal evidence in history and assembly, byte validation. Old downstream stages cannot verify sources or replace erroneous extracted evidence. | necessary | correct: orchestration and deterministic boundary owner | G1-001 must be repaired; no unrelated refactor identified. |
| `apps/api/src/push_kids/agent_processing/stage_contracts.py` | modify; +59/-13 | Introduces formal evidence/source DTOs, final confidence and empty-member discoveries; centralizes approved Prompt05 roles and revision. Without it consumers cannot express approved source ownership. | necessary | correct: provider-neutral stage contract and shared rule owner | No answer table or service-side semantic renaming. Existing examples retained; no duplicate independent rule owner. |
| `apps/api/src/push_kids/agent_processing/prompt.py` | modify; +1/-1 | Version the legacy consumer of changed shared rules; otherwise its recorded prompt identity remains stale. | necessary | correct: legacy transport prompt owner | Only revision changes here; no staged DTO instructions copied into legacy transport. |
| `tests/staged_analysis_fakes.py` | modify; +61/-4 | Existing shared recovery tests need valid evidence/ledger/confidence DTOs and stage accounting after source payload introduction. | necessary | correct: test-only shared protocol adapter | Helper derives evidence from candidate fixtures and auto-builds ledgers. It is not independent evidence-owner or visual truth; dedicated tests must bypass it for altered provenance. |
| `tests/unit/test_staged_analysis.py` | modify; +253/-19 | Covers source input, independent final evidence/subject, byte bounds, source mutations and malformed evidence/ledger/granularity references; updates existing DTO fixtures. | necessary | correct: pipeline contract tests | Added expectations are fail-capable; empty-candidate fixture uses `non_learning`, not the newly allowed `content`/empty branch. No migrated source-attribution case. |
| `tests/unit/test_staged_proposal_recovery.py` | modify; +70/-4 | q/material isolation and unaffected evidence protections; existing history/capacity fixtures require coherent formal references. | necessary | correct: proposal/recovery behavior tests | Material fixtures keep candidate and audited sources equal and miss G1-001. Positive omission restoration/new-discovery correction and protected evidence after split/reorder need additional evidence. |
| `tests/unit/test_provider_evidence.py` | modify; +1/-1 | Update the legacy prompt-revision assertion for the shared rule change. | necessary | correct: existing legacy contract test | No unrelated assertion weakening; common rule appears once and examples remain last. |

Necessary files: all seven. Questionable/unnecessary/misplaced files: none confirmed. Safely deletable code/files: none identified. Necessary placement does not mean the implementation is correct; G1-001 is specifically in a necessary, correctly placed change.

Context only: `contracts.py` public validators/history projection, `coverage.py` optional coverage, `checkpoints.py` bounded scoped storage, `stage_io.py`, architecture constraints, existing checkpoint integration tests, and Group2's retained `stage_provider.py`/`failures.py`/`telemetry.py`. Earlier worker/retry/learning changes and frontend changes were not counted or independently rated.

## Test Evidence And Limits

Fresh, strictly read-only execution used `.venv/bin/python -B` with `PYTHONPATH=apps/api/src`. Retained source/test modules were SHA-checked and compiled in memory. No pytest runner, conftest, fixture setup, bytecode/cache files, database instance, or live SDK was used.

- **82 direct invocations / 36 test functions PASS** in retained staged analysis and proposal recovery tests, including all 14 invalid-directory cases, 4 invalid-granularity cases, 4 q/item protected-drift cases, both final-evidence-owner cases, both byte-budget variants, 12 seeded/unseeded terminal-cache cases, omission/empty-output cases, and history scope/identity/bounded-input cases.
- **3 additional direct invocations PASS**: legacy prompt revision/shared-owner assertions, complete accepted parent-text preservation, and public evidence/manual-addition validation.
- The reproducible G1-001 probe below has both a rejection control and the unauthorized-acceptance case. It also exercises `content` with empty candidate items on the other source without writing material files.
- An initial reviewer harness attempt aborted on a failure-disposition assertion because it loaded a second `StageFailure` class after `contracts.py` had imported the first. This was a harness setup failure, not repository Red. Loading `failures` before `stage_contracts` fixed class identity; the complete 82-invocation rerun passed. No repository change was needed.

These are direct test invocations, **not an independently rerun 163-test or 893-test pytest suite**. Fifteen staged/recovery functions requiring filesystem/monkeypatch fixtures or a timing probe were excluded from direct execution, including original-image mutation, multi-photo/group coverage, duplicate images, maximum18/33 calls, and material-isolation filesystem cases. Their code and retained evidence were reviewed.

Retained, hash-verified evidence reports baseline127PASS, final163PASS, full893PASS/52conditionalSKIP. EVD records targeted lint/type/architecture PASS and full-Ruff/format failures outside this patch. Those are implementer observations, not new reviewer-run checks. Intermediate Red outputs demonstrate intended mechanism failures but do not retain every intermediate full source/test fingerprint; their temporal provenance was not independently reconstructed.

Coverage gaps and residual risks, not additional confirmed defects:

- A scripted Provider cannot prove character accuracy, educational role, complete word/letter sets, deduplication/granularity, truthful summaries, or reliable history-name semantics. Fixed30/68-image and supplemental3/6-image acceptance remains NOT_RUN by this reviewer.
- Full-output source test asserts images/text/materials/excerpts/summary/uncertainties, but not every reviewed directory/ledger/item field together. Static payload construction covers those fields; a stronger integrated assertion is still useful.
- The byte-budget test's checkpoint store always returns `None`; it tests configured storage and pre-save rejection, not oversized poisoned-cache reads. `_call` does apply `validate_merge` on cache hits, verified statically.
- Fixtures/probes do not establish successful necessary omission restoration, new-object split/merge correction, protected evidence identities across every reorder, or shared-source ledger isolation. Do not convert these gaps into PASS.
- Provider request memory/latency, bounded reads, source races, real concurrency/cancellation, SQLite/MySQL recovery, worker confirmation, native/device/UI, live model/content and release gates were not executed here. Group2 owns the provider/budget review; no result is presumed.

## Joint Document Audit

Documents were read as current contextual facts on 2026-11-01; they are not entries in the retained code/test patch manifest. The following document notes are separate from the single confirmed code-finding JSONL pool. Owner for updates is authorized implementer/Feature merge owner TRAE; Product owner is required only for a new semantic decision, not routine reconciliation to the already approved scope. No document was edited.

| Document / section | Status against reviewed version | Evidence and required action |
|---|---|---|
| Content03 Spec approval, AC-S01-S05, lifecycle | aligned design; implementation conflicting under G1-001 | Approval and one-owner/local-correction rules are explicit. Preserve them and fix the implementation rather than weakening the Spec. `VERIFYING` in `specs/completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md` is correct with no matching cloud delivery. |
| Content03 Spec required-point table, lines225-235 | **stale, note G1-D03** | Every row still says current NOT_RUN despite header/EVD's local implementation and measured tests. Record actual per-layer results; TP-S04 now has G1-001 FAIL and TP-S10/11 cannot be blanket PASS. Keep unexecuted content/resource/live points genuinely NOT_RUN/PARTIAL. |
| Prompt05 sections and stage-contract instructions | aligned | Shared source priority, object/skill coverage, local correction and legacy history rules are implemented as instructions. Local rule presence is not model semantic acceptance. |
| FEAT-001 line8; lines95 and234-238 | aligned new header; **stale current body, note G1-D01**; G1-001 contradicts claimed strict source isolation | Header identifies11/14, but current revision/body still names cache08/09 and only i/o correction without the formal directory/source/q contract. Reconcile the existing current section, retain separately labeled historical results, and link unresolved G1-001 rather than calling all isolation complete. |
| Behavior Catalog line7 and BHV-032 line36 | **stale, note G1-D02** | Still declares current10/13 and lacks Content03's source/evidence/q contract. Update current behavior/revision/evidence while retaining cache02 and historical09 results; do not claim stronger protection than verified. |
| Architecture current sequence, lines185-229 | aligned topology/owners/budgets; conflicting material-isolation guarantee under G1-001 | Accurately documents original sources, formal DTOs and unchanged owners. Scope claim at203-205 needs G1-001 disposition/evidence. No new module/ADR/frontend baseline is justified solely for this repair. |
| Architecture constraints and REVIEW.md | aligned applicable policies | Existing purpose/ownership/validated-state/independent-review rules apply; constraints were not re-executed as a tool gate. |
| Test Strategy, lines128-159 | **missing Content03 slice, note G1-D04** | Cache02 and Prompt04 history are explicitly versioned; no Content03 source-directory/ledger/q/migrated-attribution/full-output contract or matching current EVD. Add the new slice and actual validation limits; do not relabel old test counts. |
| Content03 implementation EVD and manifest | aligned retained observations; scope completion unresolved | Hashes and retained baseline/Red/Green/full-run counts agree. Its complete isolation assertion requires G1-001 follow-up. Keep content/DB-after-audit/cleanup/cloud NOT_RUN rather than using synthetic PASS to close content. |
| Content ISS root-cause line35 versus fix line40 | **ambiguous stale wording, note G1-D05** | Root section says source visibility is "currently not implemented", while fix describes11/14 implementation. Label that sentence explicitly as09/13 historical fact. Keep ISS open; no actual content acceptance was reviewed. |
| Existing mechanism REG | aligned as historical07/08/09 record; new prevention evidence missing | Do not rewrite its historical hashes or claim it covers all Content03 boundaries. Add version-bound G1-001 regression/evidence through the authorized maintenance process after repair. |
| UI-001 draft evidence/manual-entry sections, lines145-189 | aligned / frontend N/A for this delta | Existing editable draft, confidence/evidence display and manual path remain. No Group1 frontend field/component/style/interaction change or new native acceptance is claimed. |
| Deploy README and cache-local/preparation records | aligned distinct scope; Content03 delivery NOT_VERIFIED | Records concern frozen10/13 preparation or old039/staged06, not11/14 delivery. No deployment was queried/run here; no DONE/archive or release state is justified for Content03. |

Relevant reviewed links to Spec/Prompt/EVD/manifest/snapshots/Feature/Behavior/Architecture/Test/ISS/REG/UI/release documents resolved. An exploratory guessed `ui/learning.md` path did not exist; the actual UI-001 document was located and reviewed. External references and private content artifacts were not fetched.

Documentation closure result: **not fully aligned**. G1-D01 through G1-D05 record current-fact/version/table omissions; G1-001 additionally conflicts with strict isolation claims. These require authorized follow-up, not read-only reviewer edits or silent semantic expansion. This is not a demand to update unrelated historical/frontend documents.

## Reproduction

Run from REPO_ROOT. This probe reads existing safe snapshots as inert source bytes, compiles retained code in memory, disables optional coverage and supplies scripted responses. It does not create images, construct a database/checkpoint store, contact a model or write bytecode.

```bash
PYTHONPATH=apps/api/src .venv/bin/python -B - <<'PY'
import asyncio
import hashlib
import json
import sys
import types
from pathlib import Path
from time import monotonic

ev = Path.cwd() / "specs/evidence/bug036-content03-20261101"
manifest = json.loads((ev / "manifest.json").read_text())
for short in ("failures", "telemetry", "stage_contracts", "pipeline"):
    path = f"apps/api/src/push_kids/agent_processing/{short}.py"
    meta = manifest["files"][path]
    source = (ev / meta["current_snapshot"]).read_bytes()
    assert hashlib.sha256(source).hexdigest() == meta["current_sha256"]
    name = f"push_kids.agent_processing.{short}"
    module = types.ModuleType(name)
    module.__file__ = str(ev / meta["current_snapshot"])
    sys.modules[name] = module
    exec(compile(source, path, "exec"), module.__dict__)

from push_kids.agent_processing.contracts import AnalysisInput
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.stage_contracts import (
    ConsolidatedResult, ExtractedPoint, MatchDecision, MatchingResult,
    MaterialResult, QualityIssue, QualityReviewResult,
)
from push_kids.agent_processing.telemetry import AnalysisTrace

class ScriptedProvider:
    concurrency = 2
    parameter_revision = "group1-read-only-probe"
    coverage_enabled = False

    def __init__(self, candidate_owner):
        self.candidate_owner = candidate_owner
        self.events = []
        self.reviews = 0

    async def generate_stage(self, stage, instructions, payload, schema,
                             images, deadline, trace):
        self.events.append(stage)
        if stage == "extract":
            alias = payload["materials"][0]
            return MaterialResult(
                status="content", needs_context=False, excerpt="",
                items=[ExtractedPoint(
                    subject="Math", name="Addition within 10",
                    evidence="Extraction hint", materials=[alias], confidence="high"
                )] if alias == self.candidate_owner else []
            )
        if stage == "merge":
            corrected = "review_issues" in payload
            return ConsolidatedResult.model_validate({
                "summary": "Practice addition", "uncertainties": [], "omissions": [],
                "items": [{
                    "members": ["c1"], "subject": "Math",
                    "name": "Subtraction within 10" if corrected else "Addition within 10",
                    "category": "Calculation", "display_kind": "arithmetic",
                    "review_method": "\u53d8\u5f0f\u7ec3\u4e60", "estimated_minutes": 2,
                    "evidence_keys": ["e0"], "confidence": "high"
                }],
                "evidence": [{
                    "key": "e0", "material": "m2", "detail": "m2 addition teaching area"
                }],
                "source_checks": [
                    {"material": "m1",
                     "disposition": "non_learning" if corrected else "indeterminate",
                     "item_aliases": [],
                     "basis": "Footer is nonlearning" if corrected else "Check teaching role"},
                    {"material": "m2", "disposition": "covered",
                     "item_aliases": ["i0"], "basis": "Addition teaching area"}
                ]
            })
        if stage == "review":
            self.reviews += 1
            return QualityReviewResult(
                passed=self.reviews > 1,
                issues=[] if self.reviews > 1 else [QualityIssue(
                    code="unsupported_by_evidence", items=["m1"],
                    basis="m1 footer is nonlearning"
                )]
            )
        assert stage == "match"
        return MatchingResult(decisions=[
            MatchDecision(candidate="i0", match=None, uncertain=False)
        ])

sources = [
    ev / manifest["files"][f"apps/api/src/push_kids/agent_processing/{short}.py"]["current_snapshot"]
    for short in ("pipeline", "stage_contracts")
]
for owner in ("m2", "m1"):
    provider, queries = ScriptedProvider(owner), []
    try:
        result = asyncio.run(StagedPipeline(provider, AnalysisTrace.disabled()).run(
            AnalysisInput(image_paths=sources, existing_subjects=["Math"]),
            lambda request: queries.append(request) or [], monotonic() + 10
        ))
        observed = {"outcome": "accepted", "names": [p.name for p in result.knowledge_points]}
    except StageFailure as exc:
        observed = {"outcome": "rejected", "stage": exc.stage, "reason": exc.reason,
                    "diagnostics": exc.diagnostics}
    print(json.dumps({"candidate_source": owner, "audited_source": "m2",
                      "review_target": "m1", "history_queries": len(queries),
                      "stages": provider.events, **observed}))
    assert observed["outcome"] == ("rejected" if owner == "m2" else "accepted")
PY
```

Observed: control `m2` rejected at merge with `stage.members:reference` and zero history queries; obsolete hint `m1` accepted `Subtraction within 10`, ran review1 and one history query. This deliberately asserts the observed defect, not the desired post-repair behavior.

## Closure

Only reviewer artifacts were written. Production, tests, docs, approval snapshots, manifest, Git index/commits, model service and database state were not modified. No deployment or Spec movement occurred.

The Spec remains **VERIFYING**, at `specs/completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md`, appropriately pending development delivery and separate content acceptance. G1-001 needs authorized repair and regression evidence; document notes need reconciliation. Group2/cross-group review, actual content acceptance, live/resource/storage gates and cloud delivery remain outside this completed Group1 review.
