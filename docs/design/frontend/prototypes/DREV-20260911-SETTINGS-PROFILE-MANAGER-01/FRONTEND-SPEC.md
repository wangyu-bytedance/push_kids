# DREV-20260911-SETTINGS-PROFILE-MANAGER-01 — 设置页学习档案入口收敛

- Status: APPROVED
- Related Spec: `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01`
- Affected UI: `UI-001 / pages/settings/index`
- Baseline: `FDB-20260906-03`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260906-04`
- Figma anchor under existing FEAT-001 waiver: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Interaction direction

设置页是 Operate 型页面，继续采用既有“暖纸底、松绿主操作、低装饰”。本修订用渐进披露收敛重复档案列表：
主页面聚焦当前孩子的科目与活动设置，低频的切换/编辑/恢复/添加统一进入右上角档案面板。

## Target page

```text
按你们的节奏来                         [旺 旺仔⌄]

在学科目
┌────────────────────────────────────┐
│ 数学  语文  英语                   │
│ + 添加其他科目                     │
└────────────────────────────────────┘

课外活动 …
```

主页面删除：

```text
学习档案
┌ 旺仔 · 一年级   当前  > ┐
│ 六六 · 学前-中班       > │
└─────────────────────────┘
+ 添加孩子
```

## Right-top profile manager sheet

```text
────────
学习档案                                      [关闭]

旺  旺仔 · 一年级                    当前   编辑
六  六六 · 学前-中班                         编辑

已归档
满  满满 · 二年级                         去恢复

+ 添加孩子
```

- 点击孩子行：切换当前孩子并关闭面板。
- “编辑”：进入对应在用档案的既有编辑页，不触发切换；触控目标 ≥44px，具有独立 accessible name。
- “去恢复”：进入该归档档案的既有恢复态，不在面板直接写数据。
- “添加孩子”：沿用既有创建页；达到上限时替换为 `childLimitHint`。
- 只读成员：只显示在用档案切换，不显示编辑、已归档管理或添加入口。
- 单孩子：右上角仍显示 chevron 且可以打开面板。
- 无在用孩子：右上角胶囊不存在，继续使用页面原有首次建档/恢复空态。

## State matrix

| State | Main page | Sheet |
|---|---|---|
| 1 active / writable | no profile block | current row + edit + add |
| 2+ active / writable | no profile block | switch rows + per-row edit + add |
| archived present / writable | no profile block | archived section + restore entry |
| limit reached | no profile block | add hidden + limit reason |
| viewer | no profile block | switch rows only |
| 0 active | existing first-profile empty state | not available |

## Responsive and accessibility matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / main + sheet | main starts at subjects; sheet scrolls vertically; row and action remain within width |
| 390×844 / main + sheet | primary visual comparison; switch and edit targets are distinct |
| 430×932 / main + sheet | max content width preserved; no desktop stretching |
| screen reader semantics | chip announces profile management; row announces switch; edit/restore/add have separate names |

## Approval boundary

批准即授权：删除设置页普通态整个学习档案区块，把切换、编辑、归档恢复、添加和上限说明迁入右上角面板；
无孩子首次建档保留，只读权限和后端合同不变。请明确批准：

- `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01`
- `DREV-20260911-SETTINGS-PROFILE-MANAGER-01`
- 本修订继续沿用 FEAT-001 scoped Figma waiver，且该 waiver 在公开生产发布前到期

Approval evidence: 用户于 2026-09-11 回复“落地”。批准快照：
`docs/design/frontend/snapshots/UI-001/DREV-20260911-SETTINGS-PROFILE-MANAGER-01/APPROVAL.md`。

## Local implementation evidence

- 设置页普通态已删除重复档案区块；右上角胶囊在单孩子和多孩子时均可打开“学习档案”面板。
- 可写成员可切换、编辑、恢复归档档案和添加；只读成员只可切换；达到上限时显示既有原因。
- 独立编辑按钮最小高度为 88rpx，编辑/恢复/添加导航前关闭面板；后端/API/Schema 未改。
- 自动化：focused frontend 32 passed，full frontend 140 passed，ESLint、静态小程序、架构与图标幂等通过。
- 本地 registered AppID preview 为 574991 bytes，未上传；三档 HTML fixture 已生成，PNG 与原生三视口/
  iOS/Android 为 `NOT_RUN`，因此本记录不是公开发布视觉验收。
