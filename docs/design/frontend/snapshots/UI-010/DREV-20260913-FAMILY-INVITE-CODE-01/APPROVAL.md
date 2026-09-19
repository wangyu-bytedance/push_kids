# UI-010 — DREV-20260913-FAMILY-INVITE-CODE-01 Approval Snapshot

- Status: `APPROVED`
- UI ID: `UI-010`
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

- Surface: 首次 onboarding / 手动申请加入家庭。
- Visible change: 输入 `6 位家庭邀请码` 后查看家庭；微信分享进入时无需手填。
- Interaction: 数字键盘、六位边界、字段级错误、保留输入、显式用户触发预览。
- Terminology: 前置值叫“家庭邀请码”；申请创建后的值叫“申请核验码”。
- Explicitly unchanged: 最小家庭预览、关系选择、manager 审批与获批前数据隔离。
- Native implementation gates: loading/invalid/expired/revoked/rate-limited/pending/approval、键盘、三视口、iOS/Android。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `join-320x568.png` | Applicant / six-digit entry | 320×568 | 1x | `ddb1a5c20e02bbb81af8b99229aa0fc9fe33d5c276bd832d94534c589e91f4bc` | narrow viewport; primary action remains visible |
| `join-390x844.png` | Applicant / six-digit entry | 390×844 | 1x | `9f86489fc26741e066c6b822f5468166894351e6eecfddfcac7e28c37fd4fe8c` | reference viewport |
| `join-430x932.png` | Applicant / six-digit entry | 430×932 | 1x | `09b4aad2e554be6f8778cff5d0734b790afeec43b9fe278a6365c83547d8c353` | wide viewport |

## Integrity checklist

- [x] Editable source and all exports exist with matching SHA-256.
- [x] Required viewports are represented.
- [x] Unexported states are listed as native implementation gates.
- [x] Approval names the Task Spec revision and Design Revision.
