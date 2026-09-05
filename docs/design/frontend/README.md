# Frontend Design Governance

This directory separates current UI facts from per-change design history.

```text
docs/design/frontend/
├── FRONTEND-DESIGN.md                 # project-wide approved product/design baseline and Figma index
├── FRONTEND-ENGINEERING-CONSTRAINTS.md # approved code/quality/budget/evidence policy
├── UI-CURRENT-STATE-TEMPLATE.md       # template; do not edit as a real UI record
├── ui/UI-xxx-<surface-or-flow>.md     # current effective state per stable UI surface/flow
└── snapshots/UI-xxx/DREV-*/
    ├── APPROVAL.md                    # immutable approval manifest
    └── *.png                          # approved viewport/state exports
```

## Information model

- **Frontend Design Baseline**: approved project-wide style, interaction conventions, resolution support, Figma file, and implementation constraints.
- **Frontend Engineering Constraints**: approved component/state/form,
  accessibility, localization, browser, performance, security/privacy,
  data-visualization, observability, and verification policy.

- **UI Current-State**: the final effective design and implementation mapping for one stable `UI-ID`.
- **Task Spec**: one change's intent, proposed Design Revision, approval, scope, and verification.
- **Approval Snapshot**: immutable local evidence of what was approved when a live Figma file can later change.

Do not concatenate old Specs to infer the current UI. Read
`FRONTEND-DESIGN.md`, then the affected `ui/UI-*.md`; follow Change References
only for rationale or history.

## Baseline gate

Before the first Figma prototype or frontend implementation, instantiate
`FRONTEND-DESIGN.md` and set exactly one state:

- `Frontend scope: PRESENT`, `Baseline status: APPROVED`, plus
  `Frontend engineering scope: PRESENT` and `Constraint status: APPROVED`; or
- both documents declare `NOT_APPLICABLE` with the same evidence-based reason and Owner.

For `PRESENT`, the baseline MUST define and be approved for:

1. **Style consistency** — product/brand style, Design System, tokens, typography, colors, spacing, shape, elevation, icons, component states, and exception policy.
2. **User interaction conventions** — target users/platform, navigation, feedback, forms, validation, destructive actions, input methods, accessibility, and localization conventions.
3. **Resolution support** — supported devices, viewport matrix, min/max widths, breakpoints, orientation, zoom/DPR, density, and required states at each viewport.

If users have not supplied concrete values, the Agent proposes a technically
reasoned default and alternatives. `MISSING` or `DRAFT` is not permission to
design or code a user-visible frontend.
The engineering constraint baseline additionally defines component/state/form
boundaries, complete UI states, accessibility, localization, compatibility,
performance/resource budgets, client security/privacy, tables/charts,
motion/media/AI behavior, observability, and the verification matrix. If users
have not supplied values, propose project-specific defaults and trade-offs;
do not invent passed measurements.

## UI identity

Use a stable `UI-ID` for an independently evolving page, component family, or
cross-page flow. Feature IDs and UI IDs may be many-to-many. Use a separate
Design Revision such as `DREV-YYYYMMDD-N`; do not reuse a Task Spec revision as
a Design Revision.

## Figma and approval workflow

A user-visible frontend change follows:

```text
resolve Feature ID and UI-ID
→ read approved baseline and UI current state
→ read approved frontend engineering constraints and quality budgets

→ create/update the Figma prototype
→ record file URL and node-specific URL(s)
→ export the required viewport/state snapshots
→ record snapshot hashes and approval manifest
→ obtain approval for Task Spec revision + Design Revision + nodes
→ implement only the approved design
→ verify behavior, visual state, responsive support, and accessibility
→ verify affected component/state/form, localization/browser/performance,
  security/privacy, data-viz, observability, and other declared quality dimensions

→ semantically merge final facts into the UI current-state document
```

A generic file URL is not enough when a node-specific URL can be produced.
Figma is the editable design source; the local snapshot is the immutable
approval evidence. A branch/version URL should also be recorded when available.

## When no new prototype is required

A new Figma revision is not required only when:

- a pure internal refactor changes no user-visible design or interaction;
- build/test/type work changes no UI contract; or
- code is being restored to an existing, unambiguous, still-approved Design Revision.

The Task Spec still records `Frontend impact: no` or `Design change: no` and the
reason. Restoring a prior design cites its `UI-ID`, Design Revision, node URL,
and approval snapshot. If the target cannot be determined uniquely, re-enter
the Figma gate.

## Change control

Any implementation discovery that changes approved layout, flow, state,
responsive behavior, accessibility semantics, or copy meaning requires a new
Design Revision and approval before continuing. A one-time waiver is valid only
when the user explicitly approves its scope, risk, Owner, and expiry; no Agent
may silently bypass unavailable Figma access.

At closure, replace superseded body text in the UI current-state document. Add
a Change Reference to the Task Spec, approval snapshot, commit/release, and
verification. Do not append conflicting designs as a diary.
