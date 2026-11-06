# [TASK-ID] — Independent Review Report

- Reviewer: `[TODO]`
- Review date: YYYY-MM-DD
- Reviewed target: `[commit/range/branch/diff]`
- Spec/version: `[path + revision]`
- Affected Feature IDs/documents: `[FEAT-xxx + paths]`
- Feature baseline/current revisions: `[TODO]`
- Baseline: `[target branch/commit]`
- Review mode: read-only / manual + tools
- Validation executed by reviewer: `[commands or not run]`
- Review policy / revision: `[root REVIEW.md + explicitly declared module rules]`
- Review round / previous report: `[1/2/3 + path; further rounds need hypothesis/scope/budget]`
- Applicable historical ISS / REG: `[IDs/paths or none with reason]`

## 1. Verdict

- **Decision**: APPROVE / APPROVE_WITH_MINOR / REQUEST_CHANGES / BLOCK
- **Blockers**: `[count]`
- **Majors**: `[count]`
- **Minors**: `[count]`
- **Review confidence**: high / medium / low
- **Confidence limits**: `[missing environment/context/tests]`

Start with the confirmed finding count; if none, state “0 confirmed findings”
and the unverified scope. Unverified suspicions are not confirmed defects.

## 2. Reviewed scope

### In scope

- Spec requirements:
- Files/modules:
- Contracts/data/migrations:
- Tests and evidence:

### Not reviewed

- `[area + reason + risk]`

## 2.1 Modified file inventory and necessity audit

Review every changed file, not just the ones that look risky.

| File | Change type | Main change | Necessity | Why this change is needed or questionable | Placement | Redundancy / accidental change |
|---|---|---|---|---|---|---|
| `[path]` | add/modify/delete/move | `[summary]` | necessary/questionable/unnecessary | `[reason]` | correct/acceptable/misplaced | `[none or details]` |

Decision rules:

- `necessary`: directly required to satisfy the approved Spec, validation, compatibility, deletion, or architecture constraint.
- `questionable`: may be useful, but the reviewer cannot prove it is required for this task, or a smaller/safer change may exist.
- `unnecessary`: unrelated, avoidable, accidental, or cosmetic-only for this task.
- `misplaced`: the code may work, but it lives in the wrong layer/module/file/owner boundary.

Any file judged `questionable`, `unnecessary`, or `misplaced` must be referenced again in Findings or residual risk unless explicitly waived.

## 3. Spec and behavior alignment

| Requirement/behavior | Implementation evidence | Test evidence | Status |
|---|---|---|---|
| `[AC/BEH-xxx]` | `[file/line]` | `[test/case]` | pass/gap/deviation |

### Scope deviations

- None / `[unapproved added behavior or omitted requirement]`

### Feature current-state consistency

| Feature ID | Current-state document | Final implementation merged? | Superseded text removed? | Change Reference complete? | Status |
|---|---|---|---|---|---|
| `[FEAT-xxx]` | `[path]` | yes/no | yes/no | yes/no | pass/finding |

Review the Feature document as a current-state snapshot. It must independently
describe the final behavior without requiring readers to concatenate historical
Specs.

### Documentation validity and shared understanding

Select by affected behavior/contracts, including unchanged Markdown. Verify
current facts and approved intent; a newer commit does not automatically win.

| Document/section | Contract and applicable version | Code/test/runtime and decision evidence | Conclusion | Update / Owner / ISS |
|---|---|---|---|---|
| `[Feature/Behavior/Architecture/ADR/API/README/runbook/rules/Spec/test policy]` | `[claim + scope]` | `[immutable revision/evidence]` | aligned/stale/conflicting/missing/ambiguous/not_verified | `[action or reasoned N/A]` |

- Missing/unverified documents and impact:
- Can a new reader explain current behavior, boundaries, rationale and validation?:
- Original/source and current references verified?:

### Human decisions for document ambiguities

Apply root REVIEW section 7 and the repository template
`docs/quality/issues/DOC-AMBIGUITY-TEMPLATE.md`. A read-only reviewer supplies
the packet to the authorized coordinator instead of writing an ISS.

- Original/current full SHA/link (or UNCOMMITTED + base + full snapshot hash),
  PR/MR, Spec/revision, submitter and identity source, statements/scope/evidence:
- Missing history and searches attempted (do not invent identity or Spec):
- Recommended unified behavior/terms/documents, code/test changes, alternatives/risks:
- ISS / exact decision requested / paused dependent scope:
- Decision maker, answer/reference/date and approved scope/revision:
- pending/answered/applied/verified; applied revision and doc-review EVD:
- Re-review and closure evidence (an answer alone does not close an issue):

## Frontend design alignment

- Frontend impact: `[yes/no]`
- UI IDs/current-state documents reviewed: `[paths or N/A]`
- Approved frontend baseline revision: `[FDB-* or N/A]`
- Approved frontend engineering constraint revision: `[FEC-* or N/A]`
- Affected quality dimensions/budget IDs: `[list or N/A]`

- Approved Task Spec / Design Revision: `[revisions or N/A]`
- Editable design source path(s) and hash result: `[paths + verification or N/A]`
- Approval snapshot manifest verified: `[path + hash result or N/A]`

| Audit | Evidence | Status/finding |
|---|---|---|
| Implementation stays within approved DREV/Spec scope | `[code vs source/snapshot]` | pass/finding/N/A |
| Style consistency and token/component reuse | `[paths/nodes]` | pass/finding/N/A |
| Target-user/platform interaction conventions | `[flow/evidence]` | pass/finding/N/A |
| Required states and viewport matrix | `[exports/tests]` | pass/finding/N/A |
| Keyboard, focus, semantics, contrast, screen reader, reduced motion | `[tests/manual]` | pass/finding/N/A |
| Component/state/form ownership, recovery, duplicate/race handling | `[code/tests]` | pass/finding/N/A |
| Localization/RTL/format/timezone and long-content behavior | `[evidence]` | pass/finding/N/A |
| Browser/device/progressive enhancement matrix | `[evidence]` | pass/finding/N/A |
| Performance/resource budgets under declared conditions | `[report]` | pass/finding/N/A |
| Client security/privacy and telemetry consent/minimization | `[review/tests]` | pass/finding/N/A |
| Tables/charts/data integrity and accessible alternatives | `[evidence]` | pass/finding/N/A |
| Motion/media/AI and reduced-motion/review behavior | `[evidence]` | pass/finding/N/A |
| Errors/analytics/RUM schema, deduplication, release correlation | `[evidence]` | pass/finding/N/A |
| Replaced UI/CSS/flags deleted or on an owned exit plan | `[search/plan]` | pass/finding/N/A |
| UI current-state merge and Change Reference complete | `[document]` | pass/finding/N/A |

Any material implementation divergence without a newly approved Design Revision
is at least a MAJOR finding; coding started before required design approval is a
process BLOCKER.

## 4. Findings

Only report actionable issues with a concrete failure scenario or policy violation.

Use stable finding IDs across rounds, verify triggers/callers/existing defenses,
and distinguish introduced/pre-existing from severity. Record dispositions and
evidence; recurring/manual/production findings link ISS/REG as appropriate.

| Finding ID | Severity / origin | Evidence / verification | Disposition | Reason / Owner / follow-up | ISS / REG |
|---|---|---|---|---|---|
| `[stable ID]` | `[BLOCKER/MAJOR/MINOR/NOTE + introduced/pre-existing]` | `[path:line + case]` | fixed/false_positive/intentional/deferred | `[decision/evidence]` | `[IDs or N/A]` |

Unresolved BLOCKER/MAJOR findings prevent a passing local verification/release
verdict. Preserve GOV-002's separate development-DONE archival rule for already
delivered scope; unresolved verification is still unresolved.

### BLOCKER — `[title]`

- **Location**: `[file:line or artifact]`
- **Rule/requirement**: `[AC/BEH/ARC/security contract]`
- **Evidence**: `[what the code/test shows]`
- **Trigger**: `[inputs/state/environment]`
- **Impact**: `[user/data/security/availability/compatibility]`
- **Why existing tests miss it**:
- **Recommended direction**: `[not a full patch]`
- **Verification after fix**:

### MAJOR — `[title]`

- **Location**:
- **Evidence**:
- **Trigger**:
- **Impact**:
- **Recommended direction**:
- **Verification after fix**:

### MINOR — `[title]`

- **Location**:
- **Evidence/impact**:
- **Recommendation**:

### NOTE — `[non-blocking observation]`

- `[TODO]`

## 5. Deletion and duplication audit

- Existing authoritative path:
- New path:
- Old path removed?:
- Duplicate rule/state/schema/config introduced?:
- Legacy exports/callers/tests/config remaining?:
- Temporary coexistence has owner and removal condition?:
- Search/command used:

| Legacy candidate | Evidence | Required action |
|---|---|---|
| `[TODO]` | `[path/search]` | delete/retain with reason |

## 6. Correctness and risk audit

Mark PASS / FAIL / N/A / NOT VERIFIED with evidence.

| Area | Status | Evidence/notes |
|---|---|---|
| Success behavior | `[TODO]` | `[TODO]` |
| Validation/boundaries | `[TODO]` | `[TODO]` |
| Authentication | `[TODO]` | `[TODO]` |
| Authorization/tenant isolation | `[TODO]` | `[TODO]` |
| State transitions | `[TODO]` | `[TODO]` |
| Transactions/partial failure | `[TODO]` | `[TODO]` |
| Concurrency/lost update | `[TODO]` | `[TODO]` |
| Idempotency/duplicates | `[TODO]` | `[TODO]` |
| Async retry/cancel/dead letter | `[TODO]` | `[TODO]` |
| External dependency failure | `[TODO]` | `[TODO]` |
| API/event compatibility | `[TODO]` | `[TODO]` |
| Schema/migration/data repair | `[TODO]` | `[TODO]` |
| Security/privacy/secrets | `[TODO]` | `[TODO]` |
| Performance/resource use | `[TODO]` | `[TODO]` |
| Logs/metrics/audit | `[TODO]` | `[TODO]` |
| Rollout/rollback | `[TODO]` | `[TODO]` |
| Feature current-state merge | `[TODO]` | `[TODO]` |

## 7. Test effectiveness audit

For each critical test ask:

- Can it fail if the implementation is broken?
- Does it invoke the changed path?
- Does it verify observable results and forbidden side effects?
- Are expectation and implementation derived from independent logic?
- Does it use real wiring at the required level?
- Does a bugfix test fail on the pre-fix code?

| Test/case | Risk covered | False-positive risk | Finding |
|---|---|---|---|
| `[TODO]` | `[TODO]` | low/medium/high | `[TODO]` |

Missing evidence:

- `[TODO]`

### Coding-discipline evidence

| Slice / test point | Red cause or pre-refactor Baseline + revision | Green evidence + revision | Post-refactor behavior evidence | Exception / risk / Owner |
|---|---|---|---|---|
| `[slice/TP]` | `[expected behavioral failure / baseline / reasoned N/A]` | `[command/result/version]` | `[same contract/regression evidence]` | `[none or record]` |

- A compiler/dependency/fixture failure is not Red; refactors preserve baseline.
- Check causal repairs and changed paths, rather than guards hiding crashes.
  Repeated failed repairs need premise/state/actor-ownership evidence.
- Read the project's quality-tool policy: actual tool/version/scope/budget,
  reports and missing checks; similarity/uncovered data does not prove duplicate
  semantics/dead code, and a successful tool exit does not prove acceptance.

## 8. Architecture audit

| Rule | Status | Evidence |
|---|---|---|
| Dependency direction | `[TODO]` | `[TODO]` |
| Module ownership | `[TODO]` | `[TODO]` |
| Single source of truth | `[TODO]` | `[TODO]` |
| Boundary authorization | `[TODO]` | `[TODO]` |
| Transaction/outbox semantics | `[TODO]` | `[TODO]` |
| No speculative abstraction | `[TODO]` | `[TODO]` |

## 8.1 Design rationality and placement audit

Mark PASS / FAIL / N/A / NOT VERIFIED with evidence.

| Area | Status | Evidence/notes |
|---|---|---|
| Chosen implementation is the simplest sufficient design | `[TODO]` | `[TODO]` |
| No over-design / speculative abstraction | `[TODO]` | `[TODO]` |
| State ownership is in the correct layer/module | `[TODO]` | `[TODO]` |
| New logic is placed in the correct file/directory | `[TODO]` | `[TODO]` |
| Shared code extraction is justified and has real consumers | `[TODO]` | `[TODO]` |
| Caller-specific logic is not leaking into shared/core layers | `[TODO]` | `[TODO]` |
| Framework/interface code does not own domain rules | `[TODO]` | `[TODO]` |
| Refactor size is proportional to task scope | `[TODO]` | `[TODO]` |

## 8.2 Redundancy and unnecessary change audit

| Check | Status | Evidence/notes |
|---|---|---|
| No unrelated files were modified | `[TODO]` | `[TODO]` |
| No “while here” cleanup without explicit need | `[TODO]` | `[TODO]` |
| No duplicate logic/branch/mapper/config introduced | `[TODO]` | `[TODO]` |
| No dead code / orphan abstraction / unused parameter added | `[TODO]` | `[TODO]` |
| Old code was deleted when superseded | `[TODO]` | `[TODO]` |
| The same goal could not be reached with materially smaller change | `[TODO]` | `[TODO]` |

New exception/ADR required:

- None / `[TODO]`

## 9. Validation evidence

| Command/case | Result | Evidence | Reviewer interpretation |
|---|---|---|---|
| `[exact command]` | pass/fail/not run | `[TODO]` | `[TODO]` |

Do not inherit “pass” from the implementation report without checking the evidence.

## 10. Residual risk and re-review

- Changed/affected scope since prior round; stable IDs fixed/reopened/resolved:
- Same-class bugs checked elsewhere:
- Round cap / premise reconsideration / next scope and budget:
- New commits/snapshots requiring fresh validation/approval:
- Residual risks if merged:
- Required fixes before re-review:
- Areas to re-review after fixes:
- Required release observation:
- Necessary files:
- Questionable files:
- Unnecessary files:
- Misplaced implementations:
- Deletable or revertable code:
- Correctness conclusions with evidence:
- Correctness conclusions still lacking evidence:
- Reviewer sign-off:
