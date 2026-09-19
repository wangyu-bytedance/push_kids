# UI-001 — DREV-20260913-UNIFIED-REVIEW-01 Approval Snapshot

- Status: `APPROVED`
- UI ID: `UI-001`
- Design Revision: `DREV-20260913-UNIFIED-REVIEW-01`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/active/FEAT-001-UNIFIED-ITEM-REVIEW-STRATEGY.md#SPEC-UNIFIED-REVIEW-20260913-04`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/today-plan-390.svg; docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-390.svg`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/today-plan-390.svg=385d89c8fc16aa4ad98677d23bc8757272f572bd6aa47e30b6973dc574128875; docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-390.svg=606029185a92a1954129c6f3366b1049911f3ed747156594e06465d57e577d87`
- Prototype generated/updated at: `2026-09-13`
- Approved by: `产品负责人（用户）`
- Approved at: `2026-09-13`
- Approval evidence: `用户在收到“SPEC-UNIFIED-REVIEW-20260913-04 + DREV-20260913-UNIFIED-REVIEW-01”精确批准请求后回复“批准”`
- Superseded by: `N/A`

## Approval identity

需要产品负责人明确批准：

`SPEC-UNIFIED-REVIEW-20260913-04 + DREV-20260913-UNIFIED-REVIEW-01`

## Candidate scope

- Surfaces/flows: Today 稳定日计划；上传确认三类 Item。
- States: 正常、有未选到期项、当日完成不补题、空态、旧后端、new/today_review/history_item、stale 409。
- Viewports: 320×568、390×844、430×932；六张候选图覆盖两个关键状态的三档视口，原生证据在实现后另行提供。
- Interaction behavior: 不增加家长设置或类别选择；取消关联、编辑、移除与整批确认沿用现有操作。
- Copy/semantics: 只描述计划和已确认事实，不评价掌握度，不使用“欠账/落后”。
- Permitted implementation-only deviations: 原生字体 fallback 和状态数据长度导致的自然换行。
- Explicitly not approved: 客户端排期、完成后补题、全量到期列表、家长 pace/重要性/算法设置。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `today-plan-320.png` | Today / stable plan + backlog | 320×568 | 1x | `9e7f62de6ed8465c97c8b773a84b2083b18646c97d5bfd0d8de21669024ab412` | `today-plan-390.svg`; scroll continuation below viewport |
| `today-plan-390.png` | Today / stable plan + backlog | 390×844 | 1x | `a39da56a0d0b4d6076464929ae70fdbf16ef911a7bd4dbc83649c1f5e466eb2a` | `today-plan-390.svg` |
| `today-plan-430.png` | Today / stable plan + backlog | 430×932 | 1x | `b40a3353f7091d8622fdf1653f92b800184c18aa76f7ae9ba500057a728ff91d` | `today-plan-390.svg` |
| `confirm-kinds-320.png` | Confirm / three classifications | 320×568 | 1x | `6f489e01c1ad76dead696b154be6d661be8a85b95e6985deadbe08d4f3c891f4` | `confirm-kinds-390.svg`; scroll continuation below viewport |
| `confirm-kinds-390.png` | Confirm / three classifications | 390×844 | 1x | `fcfe9981fd449ece2c1bb4816eaf6a3ca8bf9eaee89bd63145907f9e4e35174b` | `confirm-kinds-390.svg` |
| `confirm-kinds-430.png` | Confirm / three classifications | 430×932 | 1x | `485d0957d0b1ee9f335c2445cf0b0009c395481b70bf99bddcad4ecb3af1c2ef` | `confirm-kinds-390.svg` |

## Gaps and follow-up

- External design dependency: `none` under `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`.
- Visual exports anchor Today normal/backlog and Confirm three-kind content. Loading、empty、completed、legacy
  backend、stale/error and long-content behavior are specified in `FRONTEND-SPEC.md` and remain required
  native implementation evidence; they are not represented as separate approval PNGs.
- Native 320/390/430 geometry、iOS、Android: `NOT_RUN — implementation/release evidence`。

## Integrity checklist

- [x] Every editable source exists and its SHA-256 matches.
- [x] Every listed export exists and its SHA-256 matches.
- [x] Required viewports are represented; unexported states are explicitly listed with their verification gate.
- [x] Approval names the Task Spec revision, Design Revision and snapshots.
- [x] Approval freezes this manifest; any visible deviation requires a new Design Revision.
