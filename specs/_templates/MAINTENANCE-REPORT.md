# AI Coding Governance Maintenance Report — [Period]

- Audit type: weekly / monthly / quarterly / post-incident
- Baseline commit/range: `[TODO]`
- Auditor: `[TODO]`
- Date: YYYY-MM-DD
- Previous report: `[link or N/A]`
- Mode: read-only audit / approved low-risk cleanup

## 1. Executive summary

- Overall health: GREEN / AMBER / RED
- New Blockers:
- New Majors:
- Overdue actions:
- Stale instructions found:
- Legacy paths eligible for removal:
- Critical behavior/test gaps:
- Top three actions:

## 2. Scope and evidence

### Reviewed

- Instruction files:
- Architecture/domain/ADR docs:
- Specs:
- Commit/PR range:
- CI/test reports:
- Runtime/incident evidence:

### Not reviewed

- `[area + reason + risk]`

### Commands/searches

| Command/query | Purpose | Result/evidence |
|---|---|---|
| `[exact command]` | `[TODO]` | `[TODO]` |

## 3. Previous action closure

| Prior ID | Action | Owner | Due | Status | Evidence / next step |
|---|---|---|---|---|---|
| `[MAINT-xxx]` | `[TODO]` | `[TODO]` | `[date]` | closed/open/overdue | `[TODO]` |

## 4. Findings

### MAINT-001 — `[Title]`

- Severity: BLOCKER / MAJOR / MINOR / NOTE
- Classification: DELETE / CORRECT / MOVE / AUTOMATE / DECIDE / TASK / KEEP / NEEDS_VERIFICATION
- Area: instructions / architecture / behavior / frontend-design / ADR / Spec / tests / legacy / operations
- Evidence: `[file:line, command, CI, runtime]`
- Conflict/staleness:
- Impact:
- Recommended action:
- Can be handled as low-risk doc cleanup?: yes/no
- Owner:
- Due/removal condition:
- Verification of closure:

Repeat per finding.

## 5. Instruction audit

| File/rule | Status | Issue | Action |
|---|---|---|---|
| `[AGENTS.md section]` | current/stale/conflict/duplicate | `[TODO]` | `[TODO]` |

- Root vs nested precedence checked: yes/no
- Temporary overrides checked: yes/no
- Referenced commands/paths exist: yes/no
- Rules suitable for automation identified:
- Content to move out of AGENTS:
- Approximate instruction-size concern:

## 6. Architecture and behavior drift

| Source-of-truth item | Code/test/runtime evidence | Status | Action |
|---|---|---|---|
| `[ARC/BEH/ADR]` | `[TODO]` | aligned/drift/unknown | `[TODO]` |

### Multiple-source-of-truth candidates

- `[behavior → implementations → authoritative recommendation]`

### Feature current-state drift

| Feature ID/document | Drift or missing merge | Related completed Spec | Evidence | Action/owner |
|---|---|---|---|---|
| `[FEAT-xxx]` | `[TODO]` | `[spec]` | `[code/test/runtime]` | `[TODO]` |

- Completed Specs missing Feature Change Reference:
- Feature documents containing superseded/conflicting body text:
- Feature baseline revisions stale against parallel active Specs:

### Architecture exceptions

| Exception | Expired? | Still needed? | Owner/action |
|---|---|---|---|
| `[EX-xxx]` | yes/no | yes/no/unknown | `[TODO]` |

## Frontend design governance health

| UI ID/task | Baseline/Design Revision | Figma node valid? | Approval snapshot + hashes | UI current-state merged? | Code/design verification | Action |
|---|---|---|---|---|---|---|
| `[UI-xxx]` | `[FDB/DREV]` | yes/no/unknown | complete/gap | yes/no | current/drift/unknown | `[TODO]` |

Check for completed frontend Specs without UI current-state merges, file-only
Also check unapproved/stale frontend engineering constraints, missing
component/state/form rules, unverifiable browser or accessibility claims,
performance budgets without comparable reports, expired security/privacy or
quality deviations, duplicate UI toolchains, stale analytics schemas, and
charts/tables without current data-integrity/accessibility evidence.

Figma links without node IDs, missing approval manifests or hashes, unsupported
claimed resolutions, stale style/interaction baselines, and code that diverges
from the current Design Revision. Keep approved evidence required for audit;
remove unnecessary draft exports rather than accumulating every iteration.

## 7. Legacy and deletion queue

| Candidate | Evidence no longer needed | Remaining consumers/risk | Removal task/owner | Due |
|---|---|---|---|---|
| `[path/flag/adapter]` | `[TODO]` | `[TODO]` | `[TODO]` | `[date]` |

No code should be deleted from an uncertain candidate without a separate approved change.

## 8. Spec health

| Spec | Status age | Owner | Issue | Action |
|---|---:|---|---|---|
| `[path]` | `[days]` | `[TODO]` | stale/scope drift/missing evidence | `[TODO]` |

- Completed but unarchived:
- Approved with blockers:
- Implementation without approval:
- Missing deletion plan:
- Missing verification record:
- Oversized tasks to split:

## 9. Test and CI health

| Test/control | Issue | Evidence | Risk | Action/owner |
|---|---|---|---|---|
| `[TODO]` | flaky/skipped/mock-only/missing | `[TODO]` | `[TODO]` | `[TODO]` |

- Critical behavior coverage gaps:
- Quarantined tests:
- Repeated rerun-to-green:
- Local/CI command mismatch:
- Test duration bottlenecks:
- Repeated Review issue suitable for automation:

## 10. Metrics

| Metric | Current | Previous | Direction | Interpretation |
|---|---:|---:|---|---|
| Lead time | `[TODO]` | `[TODO]` | ↑/↓/→ | `[TODO]` |
| Rework rate | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| Escaped defects | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| Stale-doc incidents | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| Legacy removal time | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| Flaky rate | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |

Avoid interpreting code-line volume as productivity.

## 11. Approved low-risk cleanup applied

| Change | Files | Why safe | Validation |
|---|---|---|---|
| `[TODO]` | `[TODO]` | `[docs-only/no semantic change]` | `[TODO]` |

## 12. Action plan

| Priority | Action | Type | Owner | Due/condition | Closure evidence |
|---|---|---|---|---|---|
| P0 | `[TODO]` | doc fix / automation / Spec / decision | `[TODO]` | `[TODO]` | `[TODO]` |

## 13. Decisions required

| Decision | Recommended option | Alternatives | Consequence of delay | Owner |
|---|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |

## 14. Sign-off

- Maintainer:
- Architecture/domain owner:
- Quality owner:
- Next audit date:
