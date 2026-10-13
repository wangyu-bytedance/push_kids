# FEAT-001 — 卡片背景与插画全面接入

- Status: VERIFYING
- Spec revision: SPEC-20261013-CARD-BACKGROUNDS-01
- Design Revision: DREV-20261013-CARD-BACKGROUNDS-01
- Approved by: 用户，2026-10-13
- Approval evidence: 助手逐项说明设置三块和报表背景尚未接入、每日任务同课外活动后，用户要求“你先全面完成这个任务 我来验收”；批准补齐本会话已有统一风格方案，本地完成后交用户验收。
- Risk: R1；Owner/Reviewer: 用户；Implementer: Codex
- Affected Feature/UI: FEAT-001、FEAT-007、FEAT-010；UI-001、UI-017
- Current states: docs/domain/features/FEAT-001-push-kids-mvp.md、FEAT-007-travel-arrangements.md、FEAT-010-daily-tasks.md；docs/design/frontend/ui/UI-001-parent-miniapp.md、UI-017-travel-arrangements.md
- Baseline: FDB-20260913-04 APPROVED；FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Editable design evidence: 既有设置DREV-20261012-SETTINGS-SUBJECT-LIST-05 SVG及本修订render.py/SVG；补充manifest见snapshots/UI-001/DREV-20261013-CARD-BACKGROUNDS-01/APPROVAL.md。
- Dimensions: component/state/form/a11y/responsive/media/resource/privacy；原生三档320×568、390×844、430×932，触控≥44px，文字不被插画遮挡，装饰失败不影响功能，本地资产，无远程请求；主包≤1.5MiB。

## Scope / alternatives / trade-offs

推荐沿用已认可暖白纸面浅绿渐变，设置三卡标题右侧分别书本/运动/出行插画；每日任务同款纸面与列表、位于课外活动后，不增加独立清单插画。报表顶部成长记录插画，正文统计卡仅同款纸面，避免装饰进入数据绘图区。记录/日程保留本地已实现插画；今日保留原Hero。
替代整页背景大图会影响文字和加载预算，故使用小尺寸本地透明装饰。无需新共享模块或依赖。只改呈现，不改科目加入/移出、每日任务配置、报表统计、历史和计划交互。

- Call graph: Page WXML → 原事件控制器 → 原API，不变；新增onIllustrationError仅更新页面装饰失败标志。
- Sequence/state: 图片加载成功显示；失败移除装饰，所有业务状态继续原流程。表单/权限/错误/保存合同不变。
- Architecture: N/A，不改变模块边界、依赖方向或扩展点。
- Expected files: settings/reports WXML/WXSS/局部失败处理，本地PNG、设计/质量证据、Feature/UI增量文档；不覆盖并行报表内部布局。
- Required tests: 全套npm test、lint、miniapp/architecture/design验证、资源alpha/大小；三视口native布局和截图、用户视觉验收、iOS/Android交互。未运行门禁记录待验收，不声明通过。
- Release: 仅本地开发，未经授权不上传或发布；验证未齐保持VERIFYING，门禁完成才移completed。
- Local implementation: 已接入全部上述背景；238项测试、lint、miniapp/architecture检查、PNG透明度与CLI预览通过。完整证据见docs/quality/evidence/CARD-BACKGROUNDS-20261013.md。用户视觉/原生完整状态矩阵/真机验收待补。
