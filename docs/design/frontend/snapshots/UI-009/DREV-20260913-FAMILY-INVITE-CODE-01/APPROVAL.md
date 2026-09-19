# UI-009 — DREV-20260913-FAMILY-INVITE-CODE-01 Approval Snapshot

- Status: `APPROVED`
- UI ID: `UI-009`
- Design Revision: `DREV-20260913-FAMILY-INVITE-CODE-01`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/active/BUG-015-SIX-DIGIT-FAMILY-INVITE-CODE.md#BUG-SPEC-20260913-19`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html=de5e54eb908f2a938a070467a86930d91b92f9629dd26826cc32d49e958f8d59`
- Prototype generated/updated at: `2026-09-13`
- Approved by: `产品负责人（用户）`
- Approved at: `2026-09-13`
- Approval evidence: `本对话“按照方案生成代码”明确对应上一轮 BUG-SPEC-20260913-19 + DREV-20260913-FAMILY-INVITE-CODE-01`
- Superseded by: `N/A`

## Approval identity

需要产品负责人明确批准：

`BUG-SPEC-20260913-19 + DREV-20260913-FAMILY-INVITE-CODE-01`

## Candidate scope

- Surface: 家庭与成员 / manager 邀请就绪态。
- Visible change: 创建成功后展示 `6 位家庭邀请码`，提供复制邀请码与微信邀请。
- Interaction: 六位码一次显示且不持久化；失败原地重试；旧 active invite 仍可撤销。
- Explicitly unchanged: 成员列表、角色、审批入口、单次邀请、24 小时有效期和服务端权限。
- Native implementation gates: loading/error/permission、长文、触控、三视口、iOS/Android。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `manager-320x568.png` | Manager / invite ready | 320×568 | 1x | `50339eea8508bdbe90e34f50021dc57da80b4179da1c18fe08a64090d4f36a2a` | narrow viewport; actions stack vertically |
| `manager-390x844.png` | Manager / invite ready | 390×844 | 1x | `76a29409ba8fc683a21742f932c18ecb4e57c7e031ba6c33b49e5cf1c404bda3` | reference viewport |
| `manager-430x932.png` | Manager / invite ready | 430×932 | 1x | `2aa7201091a9c8533037634b721663c24b01c8eb4918ec9729f15541a00a1e42` | wide viewport |

## Integrity checklist

- [x] Editable source and all exports exist with matching SHA-256.
- [x] Required viewports are represented.
- [x] Unexported states are listed as native implementation gates.
- [x] Approval names the Task Spec revision and Design Revision.
