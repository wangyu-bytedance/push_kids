# DREV-20260906-PKDS-01 — PKDS-1.0 视觉与交互设计修订

## 这是什么

`FRONTEND-SPEC.md` 是本轮 UI 改造的唯一可见合同（PKDS-1.0 设计系统 + 39 屏逐屏规格）。
`screenshots/` 是与规格一一对应的高保真参考屏，`manifest.json` 记录截图与屏 ID 的映射。
`tokens.reference.wxss` 是设计侧导出的 token 原件，代码侧的落地文件是
`apps/miniprogram/styles/tokens.wxss`；两者数值必须保持一致。

这些文件是设计历史与验收依据，**不会被小程序加载**，也不提供运行时数据。

## 与代码的对应关系

| 设计层 | 代码落地位置 |
|---|---|
| 语义色 / 圆角 / 间距 / 高度 / 动效 token | `apps/miniprogram/styles/tokens.wxss` |
| 原子与组件类（Card / Hero / Section / Button / Pill / Sheet / Timeline / 空态 / 骨架…） | `apps/miniprogram/styles/atoms.wxss` |
| 线性图标（27 个 × 6 个色变体） | `apps/miniprogram/styles/icons.wxss`，由 `tools/gen_icon_styles.py` 生成 |
| 纯展示派生逻辑（科目色、置信度、复习原因文案、偏好读写） | `apps/miniprogram/utils/ui.js` |
| 屏 A1–A4 | `pages/family-onboarding/`、`pages/family-join/` |
| 屏 B1–B5 | `pages/today/`、`components/todo-card/` |
| 屏 C1–C3 | `pages/calendar/` |
| 屏 D1–D6 | `pages/records/index.*`、`pages/records/history.*` |
| 屏 D7–D8 | `pages/record-detail/`、`pages/submission/detail.*` |
| 屏 E1–E4 | `pages/submission/confirm.*`、`components/submission-materials/` |
| 屏 F1–F4 | `pages/reports/` |
| 屏 G1–G3、G6 | `pages/settings/`、`pages/activity/edit.*` |
| 屏 G4–G5 | `pages/family-members/`、`pages/family-requests/` |
| 屏 H1–H5 | 全局状态规范，落在 `atoms.wxss` 的 `.sk` / `.pk-empty` / `.pk-notice` / `.asheet` |

## 图标资源如何重新生成

```bash
uv run python tools/gen_icon_styles.py
```

脚本内联 27 个线性 SVG，按 6 个语义色变体输出 base64 data URI。命令是幂等的：
在未修改脚本的情况下重复执行不会改变 `icons.wxss` 的内容，因此可以安全地放入校验流程。

## 未完成的验收项

三视口（320×568 / 390×844 / 430×932）原生几何证据、字体放大、键盘态和真机弱网仍为
`NOT_RUN`。HTML 参考屏不能替代原生节点几何证据，详见
`docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md` 与 `docs/quality/TEST-STRATEGY.md`。
