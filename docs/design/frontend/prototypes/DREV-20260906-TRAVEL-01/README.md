# DREV-20260906-TRAVEL-01 — 出行安排候选设计

- Status: `AWAITING_APPROVAL / FIGMA_BLOCKED`
- Related Feature: `FEAT-007`
- Related UI: `UI-017`
- Baseline: `FDB-20260906-02 / PKDS-1.0`
- Engineering contract: `FEC-20260906-04`
- Review artifact: `index.html`
- Rendered review board: `review-board.png`
- Render SHA-256: `ed3d1348245f1c08730626600f8b9533847fd83aaec47ca23d2c6fc0e9fdd6ac`
- Required viewports: `320×568 / 390×844 / 430×932`

## Direction

沿用暖纸底、墨绿主色、描边分层的 PKDS-1.0。出行安排是安静的时间占用信息；只有真正发生时间重叠时使用砖红色，同时提供“时间冲突”文字和具体冲突对象，避免只靠颜色传达。

## Candidate screens

| Screen | Purpose |
|---|---|
| `G7` | 设置页新增“出行安排”卡，按当前孩子列出每周重复时段 |
| `G8` | 新增/编辑出行半屏：常用名称、名称、星期、开始/结束时间 |
| `C4` | 日程正常态：用“出行”标签展示，不出现练习入口 |
| `C5` | 日程冲突态：冲突双方标红，并显示对象和重叠分钟数 |

## Interaction decisions proposed for approval

1. 出行安排是 child-scoped 的每周重复配置。
2. 只在“日程” Tab 展示；不进入“今日”、Todo、报表或活动记录。
3. 冲突检测覆盖当天全部有明确时段的出行、课外活动及临时/重复日程。
4. 冲突是 warning，不阻止保存；端点相接不算冲突。
5. MVP 不含地点、路线、接送人、提醒和跨午夜安排。

## Figma status

2026-09-06 调用现有 Figma 文件 `FAyfmjNrA3btWztwyxI6Zj` 时，Starter 套餐返回 MCP tool-call limit；当前账号也是 `View` seat，无法建立可编辑 node。本 HTML 与截图仅供本轮产品评审，不自动替代项目要求的 node-specific Figma 证据。实现前需要 Figma 恢复可写，或由产品负责人对本 Feature 明确批准一次性 scoped waiver。
