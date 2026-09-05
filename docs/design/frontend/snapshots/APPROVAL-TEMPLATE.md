# [UI-ID] — [Design Revision] Approval Snapshot

> Copy to `docs/design/frontend/snapshots/<UI-ID>/<DREV>/APPROVAL.md`.
> Do not mutate an approved manifest; create a new Design Revision instead.

- UI ID: `[UI-xxx]`
- Design Revision: `[DREV-YYYYMMDD-N]`
- Frontend baseline revision: `[FDB-YYYYMMDD-N]`
- Task Spec path and revision: `[path#revision]`
- Figma project/file URL: `[URL]`
- Figma file key: `[key]`
- Figma node URL(s): `[node-specific URLs]`
- Figma branch/version URL: `[URL/N/A]`
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
| `[desktop.png]` | `[VP-DESKTOP/default]` | `[1440×900]` | `[1x]` | `[sha256]` | `[notes]` |

## Gaps and follow-up

- States not represented:
- Manual assumptions:
- Waiver: `[none or approved scope/Owner/expiry]`

## Integrity checklist

- [ ] URLs point to the approved file and exact nodes.
- [ ] Every listed export exists and its SHA-256 matches.
- [ ] Required baseline viewports/states are represented or explicitly excluded.
- [ ] Approval names the Task Spec revision and Design Revision.
- [ ] The manifest is not modified after approval except `Superseded by`.
