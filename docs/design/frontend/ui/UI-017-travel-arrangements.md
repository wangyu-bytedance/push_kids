# UI-017 — 出行安排

- Status: `CURRENT_LOCAL / AUTOMATION_PASSED / NATIVE_ACCEPTANCE_PENDING`
- Related Feature: `FEAT-007`
- Related Spec: `SPEC-20260906-TRAVEL-02`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Proposed design revision: `DREV-20260906-TRAVEL-01`
- Candidate prototype: `docs/design/frontend/prototypes/DREV-20260906-TRAVEL-01/index.html`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `PENDING — Starter tool-call limit and View seat`
- Snapshot manifest: `local candidate render SHA-256 ed3d1348245f1c08730626600f8b9533847fd83aaec47ca23d2c6fc0e9fdd6ac；Figma snapshot pending under approved scoped waiver`

> 本 UI 于 2026-09-06 获用户批准，并已在当前本地工作树实现；Figma node 仍受已批准的 FEAT-007
> scoped waiver 约束。尚未完成原生三视口、字体放大、键盘态与 iOS/Android 真机验收。

## Current local information architecture

```text
设置（当前孩子）
└─ 出行安排
   ├─ 上学 · 周一至周五 · 07:30–08:10 ›
   ├─ 放学 · 周一至周五 · 16:30–17:10 ›
   └─ 添加出行安排

日程（当前孩子、所选日期）
└─ 当天时间线
   ├─ 正常出行：名称 + “出行” + 时间
   └─ 冲突出行/日程：红色边界 + “时间冲突” + 冲突对象及重叠分钟数
```

## Implemented screen contract

| Screen/state | Visible contract |
|---|---|
| `G7 settings/content` | 在课外活动后增加独立卡片；副文案明确“只显示在日程” |
| `G7 settings/empty` | “还没有出行安排” + 单一“添加出行安排”操作 |
| `G7 settings/viewer` | 列表可读，新增/编辑/删除不可用并有只读说明 |
| `G8 form/create-edit` | 常用名称 chips、可编辑名称、7 天多选、开始/结束时间、保存；编辑态另有删除 |
| `G8 form/validation` | 名称为空、星期为空、结束≤开始时字段旁报错；失败保留输入 |
| `C4 calendar/normal` | 时间线显示“出行”，不出现“记录练习”链接 |
| `C5 calendar/conflict` | 顶部摘要冲突数量；冲突双方红色轻底/左边界/圆点并显示文字原因 |
| `calendar/loading-empty-error` | 复用 UI-001 现有 skeleton、空态和保留旧内容的可重试错误条 |

## Conflict presentation

- 红色使用既有 `--pk-danger / --pk-danger-bg / --pk-danger-line`，不新增状态色。
- 颜色不是唯一线索：每个冲突项必须展示“时间冲突”，并列出冲突对象和重叠分钟数。
- 多重冲突时显示“与 2 项安排冲突”，展开或逐行列出对象；不得因空间省略全部对象信息。
- 当前实现逐行展示每个对象的名称、起止时间和重叠分钟数，并保留总数摘要。
- 过去的冲突仍显示冲突语义，但整体按现有 past 规则弱化，不能弱化到读不清。

## Form and interaction

- 快捷名称为“上学 / 放学 / 接送 / 自定义”；选择后仍可编辑名称，后端只保存普通字符串。
- 星期允许多选且至少一项；MVP 每周重复，不在 Sheet 中引入单次/例外日期模式。
- 结束时间必须晚于开始时间；跨午夜暂不支持。
- 保存中的按钮显示 pending 并阻止重复；恢复性失败保留全部输入；删除需要确认。
- 设置中的新增/编辑是唯一写入口；日程点击出行项切回设置并定位对应安排。

## Responsive, accessibility and privacy

- 视口：320×568、390×844、430×932；普通页面不横向滚动。
- 触控目标 ≥44px，正文 ≥14px；星期在 320px 仍完整显示且不裁切。
- 冲突摘要和行项目有可读名称；不能只用红色、图标或振动表达。
- 名称最大 30 个 Unicode code points，安全换行；不进 URL、日志或 analytics。
- 地点、路线、接送人不在本 revision 收集，降低儿童行踪隐私风险。

## Design and evidence status

- HTML review artifact: created and visually reviewable.
- Figma: blocked on 2026-09-06 by Starter MCP limit; authenticated seat is View.
- Approval: `2026-09-06 用户明确批准 SPEC-20260906-TRAVEL-01 + DREV-20260906-TRAVEL-01 + 全部日程项冲突范围 + FEAT-007 scoped Figma waiver`.
- Production implementation: current local working tree.
- Automated evidence: backend full suite 200 passed / 2 skipped；frontend full suite 107 passed；full Ruff check、format check、Mypy、ESLint、Mini Program validator (`pages=14`, `source_bytes=576887`) and architecture validator passed.
- WeChat DevTools: registered-AppID preview compiled; package `530964 bytes`. This is compile evidence only, not upload/deployment or viewport acceptance.
- Native evidence: WeChat 320×568 / 390×844 / 430×932, font scaling, keyboard and iOS/Android remain `NOT_RUN`; no deployment or upload is claimed.
