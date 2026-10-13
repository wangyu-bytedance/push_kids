# FEAT-010 — 设置每日任务视觉统一（Spec Lite）

- Status: VERIFYING
- Risk: R1
- Owner / Reviewer: 用户
- Implementer / Feature merge owner: Codex
- Date: 2026-10-13
- Spec revision: SPEC-20261013-SETTINGS-TASK-VISUAL-02
- User confirmation: 用户2026-10-13否决候选01，要求参考课外活动；助手明确提出复用现有卡片/标题/列表/添加入口、去掉渐变插画并置于课外活动下方，用户随后“尽快推进”，批准此唯一纠正方案。Design02复用现有课外活动基线。
- Affected Feature IDs: FEAT-010、FEAT-001
- Current state: docs/domain/features/FEAT-010-daily-tasks.md（FEAT-STATE-20261012-DAILY-TASKS-01-LOCAL）；docs/design/frontend/ui/UI-001-parent-miniapp.md

## Frontend Design Impact and Repository-native Approval

- Frontend impact / engineering impact: yes；仅设置页每日任务卡片与区块顺序。
- Baseline: FDB-20260913-04 APPROVED
- FEC: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected UI IDs: UI-001
- Dimensions: component/state/form/responsive/a11y/performance/security/privacy/media
- Design Revision: DREV-20261013-SETTINGS-TASK-VISUAL-01
- Prototype status: AWAITING_APPROVAL
- Editable source: docs/design/frontend/prototypes/DREV-20261013-SETTINGS-TASK-VISUAL-01/render.py 及生成SVG
- Manifest: docs/design/frontend/snapshots/UI-001/DREV-20261013-SETTINGS-TASK-VISUAL-01/APPROVAL.md
- Exports: 320×568、390×844、430×932 × content/empty/readonly/form/error/pending
- Budgets: 控件≥44px，正文≥14px，窄屏不横向溢出；图片本地、无人物或真实家庭数据；新增装饰资源≤40KiB，主包≤1.5MiB。
- Deviations / external dependencies: none
- Approval / engineering evidence / UI merge: pending
- Implementation: 已按用户修正后的课外活动同款列表与添加入口实现，并移至课外活动下方；纸面背景随SPEC-20261013-CARD-BACKGROUNDS-01接入，无独立清单插画。证据docs/quality/evidence/CARD-BACKGROUNDS-20261013.md；原生与用户验收待补，保留VERIFYING。

## Outcome and scope

顺序：在学科目 → 课外活动 → 每日任务 → 出行安排。复用现有课外活动的pk-card/set-card/card-head/act-list/act-row/act-mark/add-entry样式，不增加渐变和插画；保留独立编辑按钮、预设和表单。

保留预设点击后需保存、名称/分钟限制、20项上限、只读权限、错误保留输入、保存/删除pending防重与删除确认。设置JS/API/数据库不改，其他三个设置卡片不扩展实现。

## Design and alternatives

推荐：仅本卡增加纸面渐变和清单装饰，复用set-card/act-mark/add-entry，保留原表单。替代：平色卡片改动更小，但缺少用户要求的当前效果；整页重做会扩大范围。采用推荐方案，不提取共享组件或改依赖方向。

- Link/call graph: 设置WXML每日任务入口 → 既有openDailyTaskForm/saveDailyTask/deleteDailyTask → 原API；调用不变。
- Sequence: 点击预设或编辑 → 原表单 → 原校验 → 原保存 → 更新原列表；不变。
- State machine: closed → editing → saving/deleting → success或保留输入的error；仅视觉调整。
- Architecture: N/A，无模块或边界变更；只修改settings/index.wxml、index.wxss及≤40KiB本地装饰。
- Expected files: 上述页面、装饰资源、设计证据、本Spec、FEAT-010/UI-001增量事实和验证报告。

## Acceptance / verification

1. 新顺序和清单样式对齐批准设计；现有每日任务测试与全套npm test、lint、静态/架构/设计证据校验通过。
2. 原生三视口检查长任务名、空、只读、表单、错误、pending；控件44px、正文不被装饰遮挡、纵向可滚动、键盘可达。
3. 本地资源解码/无图回退、包预算；iOS/Android表单与读屏验收。没有证据不声称通过。
4. 原接口与数据合同不改，后端检查N/A。验证事实合并FEAT-010/UI-001；全部门禁完成后移completed，否则VERIFYING。
