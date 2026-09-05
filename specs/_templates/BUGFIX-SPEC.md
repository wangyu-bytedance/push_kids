# [BUG-ID] — [Bug title]

- Status: DRAFT / READY_FOR_REVIEW / APPROVED / IMPLEMENTING / VERIFYING / DONE / BLOCKED
- Severity: `[user/business impact]`
- Risk: R1 / R2 / R3
- Owner: `[TODO]`
- Implementer: `[TODO]`
- Reviewer/Verifier: `[TODO]`
- First observed: `[date/version/environment]`
- Related incident/ticket: `[link]`
- Spec revision: `[TODO]`
- User confirmation: `[revision + name/date or message reference, required before implementation]`
- Affected Feature IDs: `[FEAT-xxx]`
- Feature current-state documents: `[docs/domain/features/...]`
- Feature baseline revision: `[TODO]`
- Feature merge owner: `[TODO]`


## Frontend Design Impact and Figma Approval

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
- Figma project/file URL: `[URL or N/A]`
- Figma node URL(s): `[node-specific URL(s) or N/A]`
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

- Figma waiver: `[none, or user-approved scope/reason/risk/owner/expiry]`

When `Frontend impact: yes`, the project frontend design baseline and frontend
engineering constraints MUST both be `APPROVED`. Generate or update the Figma
prototype and obtain explicit user confirmation of the Task Spec revision +
Design Revision + Figma node(s) before frontend implementation. A live Figma
URL alone is not approval; store node-specific URLs and an approval snapshot
manifest. If implementation requires a visible divergence, stop, create a new
Design Revision, and obtain approval again. `N/A` requires a reason; Figma
unavailability is a blocker unless the user explicitly approves the recorded waiver.

When `Frontend engineering impact: yes`, cite the approved FEC revision and
select affected quality dimensions plus relevant rule/budget IDs even when
`Frontend impact: no` and no new Figma revision is needed. Do not run every
possible check blindly, but do not omit a changed or risk-relevant dimension
silently.

## 1. Symptom and impact

- Who/what is affected:
- Frequency:
- User-visible symptom:
- Business/data/security impact:
- First known good version:
- First known bad version:
- Workaround:

Do not write only the suspected implementation cause. Describe observable failure first.

## 2. Reproduction

### Preconditions

- Environment/version:
- Actor/permissions/tenant:
- Data/fixture:
- Feature flags/config:
- External dependencies:

### Steps

1. `[TODO]`
2. `[TODO]`

### Actual result

`[observable UI/API/data/event/log result]`

### Expected result

`[link behavior ID or describe exact contract]`

### Reproduction evidence

- Test/script:
- Request/trace/log ID:
- Screenshot/data query:
- Reproduction rate:

If not reproducible, state hypotheses and evidence needed. Do not implement a guess as a confirmed fix.

## 3. Triage

### Confirmed facts

| Fact | Evidence |
|---|---|
| `[TODO]` | `[TODO]` |

### Hypotheses

| Hypothesis | Supports | Contradicts | Experiment | Result |
|---|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | pending |

### Blast radius

- Entry points:
- Callers/consumers:
- Data already affected:
- Security/tenant boundary:
- Related behaviors:
- Other code with the same pattern:

### Link/call graph

```text
[failing entry] → [caller] → [faulty authoritative path]
                → [data/dependency/side effect]
```

## 4. Root cause

### Fault mechanism

`[从输入/状态到错误结果的确定性因果链]`

### Why existing controls missed it

- Missing/incorrect test:
- Review/spec gap:
- Monitoring gap:
- Architecture/process contributor:

### Root-cause evidence

- Code location:
- Failing test:
- Runtime evidence:

Avoid “AI wrote bad code” or “human error” as the root cause. Identify the missing system control or incorrect invariant.

## 5. Fix contract

### Required behavior

- `[TODO]`

### Must not change

- `[historical behavior/API/data/latency]`

### Feature current-state impact

- Current Feature sections affected:
- Incorrect/obsolete statement to correct:
- Final facts to merge after verification:
- Change Reference to add:

### Non-goals

- `[TODO]`

### State/data repair

- Does the fix prevent new corruption only?
- Is existing data repair required?
- How is affected data identified?
- Is repair idempotent/reversible/audited?

## 6. Fix design

### Selected change

- Existing path to modify:
- Logic to delete/replace:
- Why no parallel path is needed:
- Error/transaction/concurrency implications:

### Trade-offs and alternatives rejected

| Alternative | Why rejected |
|---|---|
| `[TODO]` | `[TODO]` |

### Sequence diagram

`N/A: [reason]` or a Mermaid `sequenceDiagram` comparing the failing and fixed
path.

### State machine

`N/A: [reason]` or legal/illegal state transitions affected by the defect.

### Architecture diagram

`N/A: [reason]` or a Mermaid diagram showing affected module, data, deployment,
or trust boundaries.

### Expected file changes

| File/path | Action: modify/add/move/delete | Expected change | Why required |
|---|---|---|---|
| `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |

### Compatibility and rollout

- Deployment order:
- Feature flag:
- Migration/backfill:
- Rollback/restore:
- Success/abort metrics:

## 7. Regression verification

### Required regression test

The test MUST fail on the faulty implementation and pass after the fix when feasible.

- Test point ID: `TP-001`
- Acceptance/expected behavior:
- Test level:
- Pre-fix failure evidence:
- Post-fix success evidence:
- Why this test proves the bug:

### Adjacent cases

| Case | Expected |
|---|---|
| Original reproduction | fixed |
| Prior valid path | unchanged |
| Invalid/unauthorized | rejected with no side effect |
| Boundary/empty/null | `[TODO]` |
| Duplicate/concurrent | `[TODO]` |
| Dependency failure | `[TODO]` |

### Verification commands

| Test point | Command/case | Environment | Result | Evidence |
|---|---|---|---|---|
| `TP-001` | `[exact command]` | `[TODO]` | not run | `[TODO]` |

All required test points must run after implementation. Record skipped checks,
their impact, and residual risk.

## 8. Review checklist

- [ ] Observable symptom and expected contract are clear.
- [ ] Root cause is evidence-backed, not only plausible.
- [ ] Same pattern was searched elsewhere.
- [ ] The fix modifies the authoritative path.
- [ ] Obsolete workaround/branch is removed.
- [ ] Required design views are complete or marked N/A with reasons.
- [ ] Expected changed, added, moved, and deleted files were reviewed.
- [ ] Regression test fails pre-fix.
- [ ] Every required test point ran or has an explicit skipped-check risk.
- [ ] Historical behavior tests pass.
- [ ] Data repair, compatibility and rollback are addressed.
- [ ] Monitoring detects recurrence.
- [ ] No unrelated refactor is mixed in.

## 9. Closure and prevention

- Changed behavior:
- Deleted workaround/logic:
- Data repaired:
- Monitoring added:
- Behavior catalog update:
- Feature current-state document update and Change Reference:
- Architecture/test/process change preventing recurrence:
- Independent Review:
- Residual risk:
- Follow-up owner/date:
