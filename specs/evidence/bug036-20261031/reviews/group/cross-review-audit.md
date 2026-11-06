# BUG-036 final cross-group contract check

- Date: 2026-10-31. Scope: bits-code-guard general-workflow Step4 boundary check after the two independent groups and their Review02 fixes. This is cross-group contract verification, not another fix cycle.
- Read Group1/Group2 original findings, both original audits and both Review02 audits. Reviewed current pipeline/contracts/worker/provider/failures/telemetry/checkpoints and unchanged runner bridge, bound to latest frozen files.
- **0 confirmed cross-group defects.** `cross-review.jsonl` is empty. No resolved finding is re-reported.
- No production/docs/tests edits, subagents, DB connection, live provider/model API, business API or cloud action. Only the requested cross-review outputs were written.

## Snapshot scope and freshness

Authority is task baseline `/private/tmp/push-kids-bug036-baseline-20261031`, Review01 `snapshot-manifest.json` and Review02 `review02/manifest.json`; git HEAD is not the baseline. Latest frozen production set takes each Review02 file when present and otherwise its Review01 snapshot.

**9 latest frozen production files matched both their declared SHA-256 and current workspace content**, with0 frozen mismatches and0 working-tree mismatches: pipeline, contracts, stage_contracts, prompt, stage_provider, failures, telemetry, checkpoints and worker. The generation30 run already started against this unchanged code; no result or acceptance claim is made here.

Unchanged direct bridges were additionally compared byte-for-byte against the task baseline:

| Bridge | Baseline matches / current SHA-256 |
|---|---|
| runner.py | yes; `78a16f4d94ede7d292eb43a01f59533c992d1d98d6f6aeaa22c2fb8821408b75` |
| coverage.py | yes; `44f3f6340b6fcc20367efe7dedd3d311e246acc282bd02d8ea742b6ef6c0aaf4` |
| stage_io.py | yes; `1b27b9cf4d5bf53887449ba30ec35d658bfb08ae43fb51bca7a9118c3cf20f4e` |

## Original five findings disposition

| Finding | Final disposition | Boundary evidence / latest refs |
|---|---|---|
| BUG036-G1-01, P1 rejected same-name target lost | fixed within generation scope | pipeline.py:773–777 supplies server-owned reviewed/null-match keys; contracts.py:337–342 keyword defaults empty and only430–431/443–448 duplicate skips consult it. Group1 Review02 independently proved mixed-target preservation and unchanged legacy defaults. Runner final ledger remains enforced. |
| BUG036-G1-02, P1 legacy contradictory ID output rule | fixed | stage_contracts.py:152 uses current transport identity contract; extract/merge/review retain explicit no-DB-ID constraints, match/reuse remain alias-only Schema. Legacy prompt.py:36–37/45–47 still copies trusted IDs. Public result Schema is unchanged. |
| BUG036-G1-03, P1 multi-subject global320 narrowing | fixed | pipeline.py:503 permits420 global aliases from200same-day+120today+100history; per-candidate320 remains at562–563. Group1 Review02 valid360-options test passes; query/result and512KiB payload boundaries remain. |
| Group2-01, P1 numeric model key diagnostic conversion | fixed | failures.py:89–106 retains loc types before conversion, collapses unknown string components to stage.fields, and serialized index validation at75–81 is bounded before int(). Provider atstage_provider.py:136–141 returns safe StageFailure diagnostics; pipeline.py:158–179 propagates them and attaches stage/unit. |
| Group2-02, P2 new-stage durable metadata dropped | fixed | worker.py:68–94 consumes StageFailure.diagnostics, retains legacy.codes, includes review/reuse/merge-correction and closed unit labels. Pipeline.py:692–699 emits a static post-reuse uncertainty trace. Durable metadata precedes bounded code details within300characters. |

No fourth fix cycle or new product/architecture decision was required by this contract check.

## Cross-group contract conclusions

**DTOs and callers.** StagedProvider.generate_stage returns a BaseModel under the supplied strict stage schema; pipeline._call revalidates the dumped value and then applies the actual stage/reference validator. Cache hits receive the same schema and stage checks. ConsolidatedResult accounts for every candidate via exactly one item or omission; quality reviews both mappings. Matching and reuse decisions must exactly cover candidate/selected aliases, with invalid or uncertain identities rejected. Final ModelAnalysisResult/AnalysisProposal public shapes are unchanged; worker consumes the same compatible proposal.

**Verified-new keyword vs Runner.** Only pipeline supplies verified_new_keys; model/transport DTOs cannot supply it. It permits a reviewed non-equivalent current new target to survive name-only filtering while accepted reused records remain on the unchanged reference branch. It does not bypass subject keys, max20items, linked knowledge/review references, evidence/context checks, summary rules or the actionable-proposal gate. Legacy provider callers omit the keyword. Runner still calls `data.validate_proposal` and checks every remaining new point against its server-owned `(subject,normalized_name)` successful query ledger at runner.py:87–100; family/child scope is injected by execute, not chosen by the model. No internal verification key substitutes for a successful query.

**Provider → pipeline → telemetry → worker failure path.** Provider constructs safe diagnostics from Pydantic validation errors, pipeline retains diagnostics while adding static stage/unit, telemetry uses the same closed sanitizer, and Worker renders the StageFailure.diagnostics property. Legacy AnalysisOutputValidationError/AnalysisOutputExhaustedError retain `.codes`. Model basis/names, numeric extra-key strings, raw payloads and untrusted field names are not rendered. Local structural correction receives only safe codes and static requirements; final errors retain their stage location. The durable/public error owner and bounded Job retry behavior remain unchanged.

**Counts, cache and revisions.** Closed core maximum remains33calls:12extract/group positions×2,2merge positions×2,2quality reviews×1,match×2,reuse×1. Successful unique keys remain18:10extract,2group,2merge,2review,match,reuse. Checkpoints load≤19 to detect overflow, reject19th unique key, cap each payload65,535bytes and aggregate512KiB, keep24h TTL and recheck family/child/job/submission/attempt/lease/deadline. Core digest includes PIPELINE_REVISION, provider parameter revision, payload, image hashes and relevant identity context; unit names distinguish the stages. Revision is `staged-20261031-07`, legacy prompt `child-aware-history-agent-20261031-11`; Provider fingerprint records4096extract/group,8192merge/review,2048match/reuse and queue/execution policy. Output token map agrees with those settings. Optional coverage is at most one separate fail-soft request using the same total deadline, outside the33core calls and18core cache keys. No old-06 cache reuse across the revision was found.

**Deadlines and Worker.** Worker computes remaining five-minute Job lease minus the existing30-second writeback reserve before Runner; Runner passes a single absolute deadline. Extract/group share min(totaldeadline,start+180seconds); Provider queue wait uses absolute expiry and actual model execution gets45seconds extract/group or30seconds otherwise, beginning only after acquiring one of2process slots. Existing exact-expiry queue/local classification ambiguity remains the group2 acceptance limitation: nested owners can both expire at the same absolute instant and label local_deadline. This is not a new cross-group failure or earlier termination; do not claim every queue expiry is separately labeled.

## Executed bounded cross checks

Checks used `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync python`. Task modules were loaded from Review02 then Review01 frozen package paths. No broad suite was repeated after the already executed Group1 Review02 129unit PASS and Group2 Review02 22local PASS; those remain their own versioned evidence.

1. **Synthetic provider diagnostic through pipeline and Worker**, without a provider/API client: actual MaterialResult Pydantic validation receives an extra key with5000zeroes, then the provider-shaped stub raises StageFailure(validation, schema_diagnostics). Pipeline tries exactly2local attempts, correction input contains only `stage.fields:extra_forbidden`, and final error is extract/t. Actual Worker renderer returns `code=analysis_output_invalid;reason=validation;stage=extract;unit=t;validation=stage.fields:extra_forbidden`, under300characters. Unknown model string is absent. PASS.
2. **Runner final-ledger rejection without DB/model**, using a NoDatabase stub whose session_factory raises if touched and a StageProvider stub whose API method raises if invoked. Temporarily replaced StagedPipeline.run in process memory with a completed valid new proposal made using verified_new_keys, without executing any search. Actual Runner final check still raises `history_search.incomplete`; DBcalls=0, providercalls=0. Original method was restored in finally. PASS.
3. **Freshness verification** described above:9latest frozen/current production hashes, plus3unchanged bridge baseline comparisons. PASS.

These checks did not mutate repository files or connect to any real service. They test boundary behavior, not model quality or persistence E2E.

## Remaining acceptance and document closure

- Same30-source generation/content evaluation is running separately; source fingerprint audit, denominator-preserving C1–C6 judgments, original6PASS preservation, remaining failures and cleanup must be recorded from actual results. This cross check assigns no semantic PASS.
- Formal parent confirmation’s normalized canonical identity remains the old contract and is unchanged/outside this generation task. No transaction or separate identical-name formal identity was tested or promised.
- Full/static gates, maximum persisted Job/real provider E2E and any missing release/native/device evidence retain their actual status. Group tests and this check do not substitute for them.
- Final Feature/Behavior/Architecture/Spec/ISS/REG/test/release documentation still needs implementer reconciliation after results, as detailed in the two group audits. Keep local07/11 separate from previously delivered038/06/10, and record the queue-expiry labeling limit.
- No new cloud delivery is part of this task: BUG-036 remains active until a matching future authorized cloud delivery. Local review/tests and the30case replay do not establish DONE, native acceptance or production release.
