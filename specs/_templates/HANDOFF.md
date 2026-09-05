# [TASK-ID] — Work Handoff Snapshot

> 用于换会话、换 Agent 或中断恢复。它不是 Spec 的替代品，只记录“从哪里安全继续”。

- Updated: YYYY-MM-DD HH:MM `[timezone]`
- Updated by: `[TODO]`
- Spec: `[path]`
- Spec status: `[IMPLEMENTING/VERIFYING/BLOCKED]`
- Baseline commit/branch: `[TODO]`
- Working tree status: `[clean/dirty + summary]`
- Affected Feature IDs: `[FEAT-xxx or N/A]`
- Feature current-state documents: `[paths]`
- Feature baseline revisions: `[TODO]`
- Feature merge status: not started / partial / complete / conflicted

## Frontend design handoff

- Frontend impact: `[yes/no]`
- Affected UI IDs/current-state documents: `[UI-xxx + paths or N/A]`
- Frontend baseline revision: `[FDB-* or N/A]`
- Frontend engineering constraint revision: `[FEC-* or N/A]`
- Affected frontend quality dimensions/budgets: `[IDs/list or N/A]`

- Figma project/file URL and node URL(s): `[URLs or N/A]`
- Current/approved Design Revision: `[DREV-* or N/A]`
- Prototype status and approval evidence: `[status + evidence]`
- Approval snapshot manifest: `[path or N/A]`
- Implemented states/viewports: `[list]`
- Not implemented or not verified: `[list]`
- Engineering verification completed: `[commands/evidence]`
- Engineering verification gaps/deviations: `[dimension, risk, Owner, next step]`

- Open design questions/deviations: `[none or list]`

A resumed Agent must not implement a user-visible frontend while the prototype
is unapproved, the project design baseline is incomplete, or a material design
divergence is unresolved.

## 1. Goal and approved scope

- Goal:
- Approved in scope:
- Explicit non-goals:
- Invariants:

## 2. Current verified understanding

- Current behavior:
- Target behavior:
- Relevant architecture/behavior/ADR links:
- Facts discovered since Spec approval:

## 3. Progress

### Completed

- [x] `[step + evidence]`

### In progress

- [ ] `[exact current step]`
- Files currently being edited:
- Intended outcome:

### Not started

- [ ] `[TODO]`

## 4. Changes so far

| File/path | Change | Why | Complete? |
|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | yes/no |

### Deleted/replaced

- `[old path → new authority]`

### Temporary compatibility paths

- None / `[path, authority, removal condition]`

## 5. Validation state

| Command/case | Last run | Result | Evidence/notes |
|---|---|---|---|
| `[exact command]` | `[time]` | pass/fail/not run | `[TODO]` |

### Current failures

- Failure:
- Exact reproduction:
- Current hypothesis:
- Evidence for/against:
- Attempts already made:

Do not repeat attempts without a new hypothesis.

## 6. Decisions and deviations

### Decisions made

| Decision | Owner/source | Rationale |
|---|---|---|
| `[TODO]` | `[Spec/comment/ADR]` | `[TODO]` |

### Spec deviations

- None / `[deviation, reason, approval status]`

Unapproved deviations block further implementation.

### Feature current-state merge

- Sections already merged:
- Sections still to merge:
- Superseded statements to replace/remove:
- Change References to add:
- Concurrent Feature revision/conflict:

## 7. Next safe actions

1. `[specific action, files, validation]`
2. `[specific action]`

### Do not do

- `[known wrong approach or out-of-scope change]`
- `[do not delete/modify because...]`

## 8. Blockers and questions

| Item | Evidence | Recommended resolution | Decision owner |
|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |

## 9. Residual risks

- `[risk + how to detect/mitigate]`

## 10. Resume checklist

Next agent/person MUST:

- [ ] Read root and nearest local `AGENTS.md`.
- [ ] Read the linked Spec and this snapshot.
- [ ] Re-read the latest affected Feature current-state documents and compare
      their revisions with this handoff.
- [ ] Inspect `git diff`/working tree; do not assume this snapshot is current.
- [ ] Re-run the last failing or focused validation before new edits.
- [ ] Confirm current scope and next step.
- [ ] Update this file after a meaningful checkpoint.
