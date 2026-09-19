# [TASK-ID] — [Task title] (Spec Lite)

> 仅用于 R1 局部、可逆、边界清楚的变更。涉及 API、数据、权限、异步、迁移、安全或多个模块时改用完整 Feature/Bugfix/Refactor Spec。

- Status: DRAFT / APPROVED / IMPLEMENTING / VERIFYING / DONE / BLOCKED
- Risk: R1
- Owner: `[TODO]`
- Implementer: `[TODO]`
- Reviewer: `[TODO]`
- Date: YYYY-MM-DD
- Spec revision: `[TODO]`
- User confirmation: `[revision + name/date or message reference]`
- Affected Feature IDs: `[FEAT-xxx or N/A with reason]`
- Feature current-state documents: `[docs/domain/features/... or N/A]`
- Feature baseline revision: `[TODO or N/A]`
- Feature merge owner: `[TODO or N/A]`


## Frontend Design Impact and Repository-native Approval

- Frontend impact: `[yes/no — visible design or interaction]`
- Frontend impact reason: `[what visible contract changes, or why no visible contract changes]`
- Frontend engineering impact: `[yes/no — frontend code, quality, toolchain, or policy]`
- Frontend engineering impact reason: `[affected code/quality facts, or why none]`
- Affected UI IDs: `[UI-xxx or N/A]`
- UI current-state documents: `[docs/design/frontend/ui/... or N/A]`
- Frontend baseline revision: `[approved FDB-* or N/A]`
- Frontend engineering constraint revision: `[approved FEC-* or N/A]`
- Affected frontend quality dimensions: `[component/state/form/responsive/a11y/i18n/browser/performance/security/privacy/table-chart/motion-media-AI/observability or N/A]`
- Frontend quality budgets/requirements: `[budget/rule IDs or N/A with reason]`
- Frontend quality verification plan: `[test points, commands, environments, retained reports or N/A]`
- Approved frontend engineering deviations: `[none or rule/scope/risk/Owner/expiry/approval]`

- Current Design Revision(s): `[DREV-* or N/A]`
- Editable design source path(s): `[repository SVG/self-contained HTML path(s) or N/A]`
- Design source SHA-256: `[hash(es) or N/A]`
- Proposed Design Revision: `[DREV-YYYYMMDD-N or N/A]`
- Required viewport/state exports: `[viewport IDs + states or N/A]`
- Prototype status: `[N/A/DRAFT/AWAITING_APPROVAL/APPROVED]`
- Approved Task Spec revision: `[revision or N/A until approved]`
- Approved Design Revision: `[DREV-* or N/A until approved]`
- Design approval evidence: `[approver/date/message or N/A until approved]`
- Snapshot manifest path: `[docs/design/frontend/snapshots/<UI-ID>/<DREV>/APPROVAL.md or N/A]`
- Permitted implementation deviations: `[none or explicit non-visible limits]`
- UI current-state merge owner: `[owner or N/A]`
- UI current-state merge evidence: `[document + Change Reference or pending/N/A]`
- Frontend visual/a11y/resolution verification: `[evidence paths/commands or pending/N/A]`
- Frontend engineering verification evidence: `[state/form/a11y/i18n/browser/performance/security/privacy/data-viz/observability evidence or pending/N/A]`

- External design dependency: `none`

When `Frontend impact: yes`, the project frontend design baseline and frontend
engineering constraints MUST both be `APPROVED`. Generate or update a
repository-local editable SVG or self-contained HTML source, export the required
viewport/states, record matching SHA-256 values, and obtain explicit user
confirmation of the Task Spec revision + Design Revision before frontend
implementation. If implementation requires a visible divergence, stop, create a
new Design Revision, and obtain approval again. `N/A` requires a reason.

When `Frontend engineering impact: yes`, cite the approved FEC revision and
select affected quality dimensions plus relevant rule/budget IDs even when
`Frontend impact: no` and no new Design Revision is needed. Do not run every
possible check blindly, but do not omit a changed or risk-relevant dimension
silently.

## 1. Problem and outcome

- Problem:
- Intended observable outcome:
- Evidence/current behavior:

## 2. Scope

### In scope

- `[TODO]`

### Non-goals

- `[TODO]`

### Must not change

- `[existing behavior/API/data/invariant]`

### Feature current-state impact

- Current Feature sections affected:
- Final facts to merge after verification:
- Superseded Feature statements to replace/remove:
- Change Reference to add:

## 3. Impact map

- Entry/caller:
- Existing authoritative path to modify:
- Dependencies/callees:
- Existing tests:
- Behavior/architecture docs:

## 4. Required design views

Write `N/A: [reason]` for each view that is not relevant.

### Link/call graph

```text
[entry] → [caller] → [authoritative path] → [dependencies/side effects]
```

### Sequence diagram

`N/A: [reason]` or a Mermaid `sequenceDiagram`.

### State machine

`N/A: [reason]` or legal/illegal state transitions.

### Architecture diagram

`N/A: [reason]` or a Mermaid diagram showing changed boundaries.

### Trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | selected/rejected |

## 5. Expected file changes and deletion plan

| File/path | Action: modify/add/move/delete | Intended change | Why required |
|---|---|---|---|
| `[path/function]` | `[TODO]` | `[TODO]` | `[TODO]` |

Final authoritative path:

Old path/logic to delete or retain:

- None / `[item + why existing path cannot serve]`

## 6. Acceptance criteria

### AC-001 — `[name]`

- Given:
- When:
- Then:
- And not:

### AC-002 — `[failure/boundary]`

- Given:
- When:
- Then:
- State remains:

## 7. Required test points

| Test point | Acceptance criterion | Test level | Command/case | Required result |
|---|---|---|---|---|
| `TP-001` | `AC-001` | unit/integration/E2E | `[TODO]` | `[TODO]` |

All required test points must be executed after implementation. A skipped point
must record the reason, impact, and residual risk.

## 8. Plan

1. `[modify/delete + focused validation]`
2. `[tests + full applicable validation]`

## 9. Verification

| Test point / command | Result | Evidence/notes |
|---|---|---|
| `TP-001 / [exact command]` | not run | `[TODO]` |

## 10. Completion

- Changed behavior:
- Deleted/replaced behavior:
- Files changed:
- Review findings:
- Residual risk:

- [ ] Scope/non-goals preserved.
- [ ] Acceptance criteria pass.
- [ ] Required commands ran.
- [ ] No duplicate/legacy path remains.
- [ ] Docs updated if facts changed.
- [ ] Every affected Feature current-state document was merged to the verified
      final state and links this Spec/evidence.
- [ ] No unrelated Diff.
