# [UI-ID] — [Design Revision] Approval Snapshot

> Copy to `docs/design/frontend/snapshots/<UI-ID>/<DREV>/APPROVAL.md`.
> Do not mutate an approved manifest; create a new Design Revision instead.

- UI ID: `[UI-xxx]`
- Design Revision: `[DREV-YYYYMMDD-N]`
- Frontend baseline revision: `[FDB-YYYYMMDD-N]`
- Frontend engineering revision: `[FEC-YYYYMMDD-N]`
- Task Spec path and revision: `[path#revision]`
- Frontend spec path: `[docs/design/frontend/prototypes/<DREV>/FRONTEND-SPEC.md]`
- Editable design source path(s): `[repository SVG/self-contained HTML paths]`
- Editable source SHA-256: `[path=sha256; ...]`
- Prototype generated/updated at: `[timestamp]`
- Approved by: `[user/design owner]`
- Approved at: `[timestamp]`
- Approval evidence: `[message/record]`
- Superseded by: `[DREV/N/A]`

## Approved scope

- Surfaces/flows:
- States:
- Viewports:
- Interaction behavior:
- Copy/semantics:
- Permitted implementation-only deviations:
- Explicitly not approved:

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `[desktop.png]` | `[VP-DESKTOP/default]` | `[1440×900]` | `[1x]` | `[sha256]` | `[source path/notes]` |

## Gaps and follow-up

- States not represented:
- Manual assumptions:
- Native runtime evidence: `[pending before implementation, or retained evidence paths]`

## Integrity checklist

- [ ] Every editable source exists, is repository-local, and its SHA-256 matches.
- [ ] Every listed export exists and its SHA-256 matches.
- [ ] Required baseline viewports/states are represented or explicitly excluded.
- [ ] Approval names the Task Spec revision and Design Revision.
- [ ] The manifest is not modified after approval except `Superseded by`.
