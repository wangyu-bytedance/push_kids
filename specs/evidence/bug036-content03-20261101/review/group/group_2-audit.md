# BUG-036 Content03 Independent Review: Group 2

## Scope And Authority

- Date: 2026-11-01. Strictly read-only independent review; only this audit and `group_2.jsonl` are written. No other group's findings were read.
- SKILL_ROOT: `/Users/bytedance/.trae-cn/skills/bits-code-guard`
- REPO_ROOT: `/Users/bytedance/Documents/push_kids`
- WORK_DIR: `/Users/bytedance/Documents/push_kids/specs/evidence/bug036-content03-20261101/review`
- Read `REVIEW.md` revision `REVIEW-20261028-01`, the approved active Content03 Spec, `review_groups.md`, `review_files.md`, `general-workflow.md` Steps 3.1-3.4, `review-dimensions.md` and `review-rule.md`.
- Approved revision: `BUG-SPEC-20261101-KNOWLEDGE-CONTENT-03`, Architecture03, Prompt05. Review direction: approval baseline 10/13 -> candidate 11/14. `scope: diff_only`; HEAD and earlier cache/frontend changes are not the patch.
- Authoritative scope: parent `manifest.json` and `content03.diff`. Patch SHA-256: `956450b1ab80f611dc4a7deeb7bffdbd377802b763df40fba06063c501c0dcc7`.
- Verified all 22 baseline/current snapshot hashes, all 11 current workspace file hashes, and all 11 retained check/resource hashes against the manifest. In-memory application of every authoritative patch hunk produced all 11 exact current snapshots.
- Native `diff` regenerated equivalent but differently grouped hunks, so byte comparison of that regenerated patch was not used as proof. Exact in-memory patch application and content hashes are the binding evidence.
- All changed files are Python. Step 3.3 has no applicable specialization; no Python-specific review rules were added.

## Result

One confirmed, newly introduced P2 / MINOR issue, confidence 10/10: `BUG036-C03-G2-001`, provider request-byte accounting at `stage_provider.py:126-129`. No confirmed new P0/P1 issue in Group 2. This is not approval of release, real-source semantics, or unexecuted acceptance.

The new counter reports pre-SDK JSON size rather than transmitted body size. Real SDK + local MockTransport: reported **1,013**, captured **912**, difference **101 bytes**. `extra_body` is flattened by the SDK and HTTPX uses compact JSON. The counter is observational only, so this finding does not allege that the 512 KiB input gate is bypassed. `test_stage_provider.py:343-345` checks the pre-SDK fake dictionary rather than a transmitted request, explaining why the new test passes.

## Steps 3.1-3.4 And Seven Dimensions

Read each Group 2 diff, its complete current implementation and baseline, direct caller `_call`, shared DTOs, error disposition and diagnostic consumers. Reviewed the current checkpoint, runner, worker failure, explicit retry, materialization and relevant integration test contracts as context only. Severity was assessed after tracing consumers; unsupported source-mutation and pre-existing boundary observations were not promoted into new defects.

| Dimension | Evidence and conclusion |
|---|---|
| LOGIC | New 512 KiB payload/count/file-size gates and bounded provider reads are coherent. The new request counter is incorrect as an actual HTTP-body measurement: G2-001. |
| BUSINESS_SEMANTICS | New evidence/source DTOs are validated before assembly; the 64 KiB merge gate runs on fresh and cached values. `review1` refusal/reuse uncertainty remain nonreusable and terminal, while `review0` refusal remains correction input. Exact 64 KiB discrepancy is retained baseline behavior, excluded below. |
| SECURITY | New diagnostics add only closed field/category names, not evidence, alias values or source content. Provider response parsing produces static schema diagnostics; worker filters stage/unit and bounds persisted messages. New byte counters are integers. No new content/credential leak confirmed. |
| CONCURRENCY | Request semaphore acquisition remains nonblocking polling; `acquired` guards release in `finally`. Direct tests exercise cancellation, queued timeout, execution timeout and subsequent calls. Synchronous image/hash/serialization work is not independently cancellation-preemptible; limits of this evidence are recorded below. |
| ROBUSTNESS | Provider checks image count/size before SDK use and reads at most `upload_max_bytes + 1` afterward, closing the stat-to-read growth gap at that boundary. Failure/retry mapping and safe diagnostics are retained. Hash reads are not independently bounded, so end-to-end source-read acceptance is not established. |
| PERFORMANCE | Input and image counts bound normal provider construction; base64 is included in the constructed request counter, though that counter is not wire-exact. Retained resource probe excludes real SDK serialization/live memory. No unbounded provider retry or new database query loop found. |
| QUALITY | Extensions stay in existing owners without a new shared abstraction. No unrelated rename/refactor or removable new dead path found. Style-only observations are not findings. Test strengths and gaps are recorded separately. |

## Per-File Necessity And Placement

| File | Action / delta | Necessity and reason | Placement / residue |
|---|---|---|---|
| `agent_processing/stage_provider.py` | modify, +22/-4 | necessary: AC-S05 needs input/image resource enforcement and safe counts; otherwise the adapter reads full images and has no new counters | correct owner for external request construction; no unrelated edits. Actual request-size implementation requires correction under G2-001. |
| `agent_processing/failures.py` | modify, +9/-0 | necessary: new formal evidence/source fields and byte/pattern errors would otherwise degrade to generic diagnostics | correct closed operational-error owner; existing path/index bounds remain. No redundant dynamic alias whitelist. |
| `agent_processing/telemetry.py` | modify, +3/-0 | necessary: provider's new counters would otherwise be rejected as unknown fields on enabled traces | correct narrow telemetry owner; no evidence/response logging added. Counter names alone do not prove measurement accuracy. |
| `tests/unit/test_stage_provider.py` | modify, +59/-0 | necessary: proves new capacity refusals precede SDK calls and byte/image counts contain no child text | correct adapter test location. Fake-client request-size assertion misses real serialization, linked to G2-001 rather than a duplicate finding. |

All four files: necessary; correctly placed. No questionable/unnecessary file, misplaced implementation, or safely deletable new code identified.

Shared boundary `pipeline.py`: necessary/ correctly placed for original-source propagation, integrity checks, correction/assembly ownership and the new merge byte gate. Shared `stage_contracts.py`: necessary/ correctly placed for the formal evidence/source contract, constants and single rule owner. Their full semantic review belongs to Group 1; Group 2 checked provider/cache/resource interactions, not independent visual truth.

## Bounded Sources And Recovery

- Provider `stage_provider.py:54-59,80-84`: UTF-8 payload >524,288 bytes, >9 images and oversized stat reject before SDK creation. The actual file read is capped at configured maximum +1 and rejects overflow again. Raw bytes, base64 and the constructed request are accounted separately.
- Pipeline `pipeline.py:101,151,247`: SHA computation still uses `Path.read_bytes()` without a read cap. Initial/per-call hashing predates this patch; Content03 adds the post-response hash and sends original images through more stages. A provider-only capacity test does **not** prove all source reads bounded. Normal cloud materialization has its own capped download; no current application path that grows its yielded local file beyond that bound was established here. Late growth, slow hash I/O and synchronous cancellation behavior remain **not verified**, not an invented new P1 bug.
- Source SHA checks reject a mismatch before a quality-stage call/cache hit and after a fresh successful response. The retained changed-source test mutates bytes during review and expects nonretryable `input`. It does not establish bounded hashing or an immutable single-byte snapshot across the provider read.
- `_call` retains at most one structure/reference correction for extract/group/merge/match and one attempt per review/reuse position; provider SDK retries remain zero. 18 normal/33 worst core calls and optional coverage <=1 remain the declared limits.
- `StageCheckpoints` retains 18 rows, 512 KiB/job, TTL24h, revision/fingerprint/child checks and scoped lease-guarded writes. New pipeline revision invalidates old DTO reuse. New merge byte validation also runs before returning cached values.
- Final negative `review1` and uncertain `reuse` are not returned/written as reusable cache entries. Worker only purges semantic units after current scope/lease guards and in the terminal failure transaction. Explicit retry retains family -> child -> job -> submission lock/recheck order and purges scoped semantic units with Job reset. No changes to these earlier policies are attributed to Content03.

## Executed Independent Evidence

Execution prefix: `PYTHONPATH=apps/api/src:. PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -c ...`. Python 3.12.11; OpenAI 2.54.0; HTTPX 0.28.1; Pydantic 2.13.5; pytest 8.4.2.

1. Manifest SHA verification and in-memory patch application: PASS, all declared source/check hashes match and 11/11 patched snapshots match.
2. Real SDK transport-size reproduction: PASS as defect confirmation. Used synthetic key/model/text, `review`, `MatchingResult`, no images, and `httpx.MockTransport` with a synthetic completed response. Captured only `len(request.content)`, not content. Counter 1,013 versus wire body 912. No network or database access.
3. Direct invocation of all parameter-expanded functions in `test_stage_provider.py`: **24 PASS**. Used `pytest.MonkeyPatch`, an in-memory `MemoryPath`/`BytesIO`, fake SDK clients and in-memory log capture. No pytest runner, on-disk fixtures, cache writes, external service or database was used. This is not represented as a normal pytest-suite run.
4. Candidate exact-64-KiB probe: Pydantic JSON and checkpoint compact JSON both **65,536 bytes**. Without checkpoints: one-point proposal. With checkpoint persistence size precheck: nonretryable `capacity`, stage/unit `merge`, before any database access. The DTO remained schema-valid; padding was synthetic whitespace in one uncertainty string.
5. Approval-baseline replay from retained baseline pipeline/contracts/fake sources loaded in memory: the **same** no-cache proposal / cached nonretryable-capacity outcomes. Therefore this behavior is pre-existing and excluded from Content03 JSONL. The new `>64*1024` guard does not close the existing 65,535-byte storage edge.

Initial transport probe without `PYTHONPATH` failed import setup (`ModuleNotFoundError: push_kids`); rerun with the explicit package path produced the evidence above. This setup failure is not Red or product failure.

Retained implementer outputs are hash-verified evidence, **not independently rerun suites**: 163 focused PASS, 893 backend PASS, 52 conditional skips, scoped Ruff/mypy/architecture PASS; full Ruff/format failures in unrelated files remain failures. The retained synthetic two-request resource probe reports 279,687,811-byte Python peak / 359,038,976-byte process RSS and explicitly excludes live SDK serialization/model memory.

## Document Audit

Observed document state is bound to this review's reads; no authoritative document was edited.

| Document / section | State | Evidence / required owner action |
|---|---|---|
| Approved Content03 Spec, AC-S05 / required points / lifecycle | partially aligned, not fully verified | 11/14 and approval are explicit; TP-S05 actual request counting is not met by G2-001. Required-point rows still say NOT_RUN despite the local mechanism summary/EVD; implementer should reconcile verified subsets while preserving live/content gaps. |
| `FEAT-001-push-kids-mvp.md:8,95,239-243` | conflicting current revision metadata | Intro correctly records Content09/11/14; the current `Revision` line still declares Cache08/10/13. Resource claims require G2-001 correction and bounded-hash evidence, not stronger prose. Implementer/Feature owner should reconcile the current block, preserving historical cache results. |
| `BEHAVIOR-CATALOG.md:7,36` / BHV-032 | stale | Still declares staged10/13 current and candidate-only consolidation, omitting Content03 formal evidence/source ownership. Behavior owner should synchronize current 11/14 behavior; retain old mechanism/content evidence separately. |
| `ARCHITECTURE.md:8,183-243` | mostly aligned; resource claim incomplete | Ownership/current 11/14 are consistent. SHA checks are implemented but not capped hash reads; request counts are constructed estimates. Architecture owner should resolve implementation/evidence gaps before claiming end-to-end resource acceptance. |
| `TEST-STRATEGY.md:128-153` | missing current Content03 coverage | Cache02 and Prompt04 baseline sections exist; no Content03 source/evidence/correction/bounded-read/wire-size test contract is incorporated. Test owner should add current requirements without recasting historical suites as new acceptance. |
| Content03 implementation EVD / parent manifest / resource probe | aligned with limitations | Correctly separates 163/893 local mechanism results, 52 skips, unrelated lint failures, synthetic construction, absent live SDK measurement and pending content/cloud delivery. Future actual-byte evidence must address G2-001. |
| `ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md:40` | aligned | Records approved local11/14 and keeps real-content failures/open status. No content PASS inferred here. |
| `REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md` | missing Content03 increment | Existing replay matrix is candidate/cache baseline only. Regression owner should incorporate current source/evidence/byte-boundary and transport-size coverage with versioned evidence. |
| UI / public API / Schema / release state | unchanged scope; not independently accepted | No frontend/API/DDL diff in the 11-file patch. Content03 stays VERIFYING in `specs/completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md`; no matching cloud delivery, deployment or lifecycle write occurred in this review. |

Document staleness and the retained 64-KiB edge are recorded transparently but not inflated into new production defects. Authorized implementer/Feature/test owners should reconcile them; the reviewer neither creates ISS records nor rewrites current facts.

## Context Fingerprints

These existing boundary files were read as context, not reviewed as new Content03 changes:

| File | SHA-256 |
|---|---|
| `agent_processing/checkpoints.py` | `45a0ce6401bc2780bf849fa7acec70a938f24fa77fde36c02afedae909e18e80` |
| `agent_processing/worker.py` | `32f8cb9f7b4a7e181ae4227bbffadfa5f2c582c4cfabf02ae8528f7172cbc2b8` |
| `agent_processing/contracts.py` | `7524e52c4ffbc27e1127d54bb7ac33f676165d8f303961374ad68b959df25564` |
| `agent_processing/runner.py` | `78a16f4d94ede7d292eb43a01f59533c992d1d98d6f6aeaa22c2fb8821408b75` |
| `agent_processing/stage_io.py` | `1b27b9cf4d5bf53887449ba30ec35d658bfb08ae43fb51bca7a9118c3cf20f4e` |
| `learning/service.py` | `c0d3e595a7b9b6b947b5ad1bf38931d2988a484e985c959ad97c39b587766e27` |
| `tests/integration/test_analysis_checkpoints.py` | `2d7c739e6047cc4dbb80fe1ca9424b0b6ed31edbc200fa861ac25ff89fe4c1db` |
| `tests/integration/test_worker_resilience.py` | `918a1ea53f716b021efb3d8b2445aa596f22a31dd18bdf9847d0ab32125c744c` |
| `tests/integration/test_staged_mysql.py` | `67e39c6e78c7a3e3cafa5adcc93f277c36ba9793fe85c7aea589570838fbf896` |

## Limitations And Closure

Normal pytest, database integration/MySQL, full backend/lint/type/architecture commands, real media/live model evaluation, sustained real SDK memory, native/device checks and deployment were **NOT_RUN** by this reviewer. The restriction to two output files excludes normal fixtures/cache generation and database writes. Source-integrity semantic truth and slow/mutating filesystem cancellation remain unverified.

No production, test, current-state document, Spec, Git or external state was changed. One new finding is returned to the coordinating reviewer; no merge/release approval or document-conflict closure is implied.
