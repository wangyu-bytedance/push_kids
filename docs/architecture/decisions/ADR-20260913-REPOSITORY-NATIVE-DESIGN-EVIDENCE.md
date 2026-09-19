# ADR-20260913 — Repository-native frontend design evidence

- Status: `ACCEPTED`
- Decision date: 2026-09-13
- Architecture revision: `ARCH-LOCAL-DESIGN-EVIDENCE-20260913-01`
- Approved by: 产品负责人（用户）
- Approval evidence: 用户回复“好的按照这个方案落地”批准
  `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`
- Related Spec: `specs/completed/GOV-001-REPOSITORY-NATIVE-FRONTEND-DESIGN-EVIDENCE.md`

## Context

The repository previously required a Figma file and node-specific URL before every visible frontend change.
The current environment cannot reliably use that external tool, so otherwise reviewable work was blocked or
needed repeated temporary waivers. The project still needs editable design input, immutable approval identity,
responsive evidence and an explicit user decision before implementation.

## Decision

Use repository-native design evidence:

1. `docs/design/frontend/prototypes/<DREV>/FRONTEND-SPEC.md` defines interaction, states and data mapping.
2. The same DREV directory contains at least one editable `.svg` or self-contained `.html` source.
3. `docs/design/frontend/snapshots/<UI-ID>/<DREV>/` contains exact viewport/state PNG exports.
4. `APPROVAL.md` binds the UI ID, Task Spec revision, Design Revision, source files, export dimensions and
   SHA-256 values to explicit user approval.
5. A deterministic offline validator checks evidence integrity. It cannot approve a design.
6. Native Mini Program geometry, interaction, accessibility and representative iOS/Android behavior are
   verified independently after implementation.

Figma, external design URLs, node IDs and tool-availability waivers are not part of the active contract.
Historical documents retain their original Figma evidence as an audit record.

## Consequences

- Frontend work is no longer blocked by an external design tool or quota.
- Editable source and approval evidence are reviewable in the same versioned change as the Spec and code.
- PNG and SVG assets increase repository size; each DREV must therefore contain only risk-relevant states and
  the exact required viewports.
- Repository preview fidelity is not treated as native runtime proof.
- Approved manifests are immutable except for a `Superseded by` pointer; a visible change requires a new DREV.

## Alternatives

- Keep Figma mandatory: rejected because availability is outside the repository's control.
- Approve repeated waivers: rejected because it creates permanent exceptional process.
- Keep screenshots only: rejected because screenshots are not editable design sources.
- Remove design approval: rejected because it removes the visible-contract and accountability gate.

## Extension policy

Editable formats are open only to deterministic, offline, non-secret SVG or self-contained HTML. External
design services, including Figma, are deferred. Reintroducing one requires a new approved governance Spec that
defines compatibility, security, offline fallback, observability and contract tests; it must not silently become
mandatory.

## Rollback

The documents, templates and validator can be reverted without production data changes. Reverting this ADR
does not itself authorize Figma use; restoring an external dependency requires a new approved decision.
