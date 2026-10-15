# FEAT-001 — 学科管理与删除入口统一（Spec Lite）

- Status: VERIFYING
- Risk: R1
- Owner / Reviewer: 用户
- Implementer / Feature merge owner: Codex
- Date: 2026-10-14
- Spec revision: SPEC-20261014-SUBJECT-MANAGEMENT-01
- User confirmation: 用户，2026-10-15，本聊天在具体 Spec 与 DREV 确认请求后回复“落地和实现”，明确批准本修订及 DREV-20261014-SUBJECT-MANAGEMENT-01。
- Affected Feature IDs: FEAT-001
- Feature current-state documents: docs/domain/features/FEAT-001-push-kids-mvp.md
- Feature baseline revision: 现有设置统一增量 SPEC-20261013-SETTINGS-CONSISTENCY-01

## Frontend Design Impact and Repository-native Approval

- Frontend impact / engineering impact: yes；学科列表入口、管理半屏、移出确认。
- Affected UI IDs / current state: UI-001 / docs/design/frontend/ui/UI-001-parent-miniapp.md
- Frontend baseline revision: FDB-20260913-04 APPROVED
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected frontend quality dimensions: component/state/responsive/a11y/security/privacy/observability
- Budgets: 触控≥44px、正文≥14px、初始包≤1.5MiB、无横向溢出；不新增图片或依赖。
- Proposed Design Revision: DREV-20261014-SUBJECT-MANAGEMENT-01
- Editable source: docs/design/frontend/prototypes/DREV-20261014-SUBJECT-MANAGEMENT-01/render.py 与生成的 SVG
- Snapshot manifest / Source SHA-256: 原批准记录 docs/design/frontend/snapshots/UI-001/DREV-20261014-SUBJECT-MANAGEMENT-01/APPROVAL.md；同一冻结SVG的PNG导出及完整校验清单见同目录 VALIDATION.md。
- Required viewport/state exports: 320×568、390×844、430×932 × list/panel/unselected/confirm/readonly/restricted/pending/error/long-name
- Prototype status: APPROVED
- Approved Task Spec revision / Design Revision / approval evidence: SPEC-20261014-SUBJECT-MANAGEMENT-01 / DREV-20261014-SUBJECT-MANAGEMENT-01 / 用户2026-10-15“落地和实现”。
- Approved engineering / permitted implementation deviations: none
- UI current-state merge owner: Codex；merge evidence: docs/quality/evidence/SUBJECT-MANAGEMENT-20261015.md；Feature/UI/Behavior已合并本地事实。
- External design dependency: none

## 1. Problem and outcome

代码现状：学科行直接显示加入/移出按钮，活动和每日任务为整行进入面板；基础学科移出直接 PATCH，自定义学科移出有确认。统一入口层级与删除位置，基础学科也必须确认后移出。

## 2. Scope

保留基础三科固定展示、未加入状态、现有目录、自定义及 canRemove 限制。可操作学科整行点击且尾部箭头；只读或不可移出项无可操作箭头。管理半屏展示名称、状态和关闭入口；已加入且允许移出的项底部使用与既有面板一致的危险操作“移出此科目”。未加入基础项显示主按钮“加入此科目”。移出二次确认标题为“移出「名称」？”，内容“已有的学习记录会保留，只是不再出现在选项里。”，确认“移出”，取消不写数据。

沿用 active=false 语义及服务端权限，不删除学习数据，不新增改名或 API。失败保留面板并允许重试；忙时禁止重复写入；切孩子、关闭和页面离开使迟到响应失效。不发布。

## 3. Impact map

设置 → settings.load → baseLearning/addedLearning → 管理面板 → 确认 → utils/api → 既有 subjects PATCH/POST → 刷新。
修改 settings/index.js、index.wxml、index.wxss；复用页面已有半屏和语义样式。影响 tests/frontend 学科用例、FEAT-001、UI-001、BEHAVIOR-CATALOG；架构与发布文档核对并记录无变更。

## 4. Required design views

- Link/call graph: 见第3节；单一 settings 页面路径。
- Sequence: 点击学科 → 面板 → 点击移出 → 确认弹窗 → 同孩子/权限再次校验 → PATCH → 刷新；取消无请求。
- State machine: closed → panel → confirming → pending → closed；取消回 panel；失败回 error → retry；切孩子回 closed 并拒绝迟到写入/回填。未加入 panel → joining → closed。
- Architecture: N/A，页面内部交互变化，不改变模块边界、依赖方向、共享抽象、扩展点或服务端合同。
- Trade-offs: 推荐面板底部移出，与相邻设置一致且避免误触；代价多一次点击。保留行尾直接移出点击更少，但无法解决本次入口不一致。称“删除科目”容易误解为删除学习记录，因此沿用准确的“移出”。

## 5. Expected file changes and deletion plan

settings 三文件：新增学科管理面板、统一确认及页面瞬态保护，删除行尾 subject-action 和失用样式。测试：有意义的确认/取消/失败/权限/防重/跨孩子回归。设计与本 Spec：保存新候选；旧批准快照不修改。实施验证后替换 Feature/UI/行为目录中冲突正文，修复索引与引用。

## 6. Acceptance criteria

- AC-001：学科入口与活动/任务一致；移出只在管理面板底部，无行尾删除按钮。
- AC-002：基础和自定义学科均确认后移出；取消无请求；记录保留；加入和限制不变。
- AC-003：只读无写入口；防重复、失败重试、切孩子和迟到响应正确。
- AC-004：三档中文长名称/面板/确认/错误/忙状态无溢出或遮挡，正文及触控符合 FEC。

## 7. Required test points

- TP-001：npm test；npm run lint:miniapp；增加上述关键交互回归。
- TP-002：三档微信原生节点几何与截图覆盖本设计状态；iOS/Android移出、取消、加入、只读与读屏验收。
- TP-003：uv run python tools/validate_miniprogram.py；uv run python tools/check_architecture.py；uv run python tools/validate_design_evidence.py --check-current-policy；git diff --check。

## 8. Plan

具体 Spec + DREV 批准 → 实施 → 执行测试与验收 → 文档冲突核对及更新 → 门禁全通过后 DONE 并迁移 completed。

## 9. Verification

- TP-001 PASS：npm test 244项；npm run lint:miniapp。新增5项学科回归覆盖基础/自定义移出确认、取消无写、加入/恢复、只读/受限、防重、失败重试、关闭/离页/跨孩子迟到回调。
- TP-002 PARTIAL：320×568、390×844、430×932三档微信模拟器八态原生节点几何PASS（24组）；确认弹窗原生截图、完整视觉截图、iOS/Android及读屏NOT_RUN，本机未连接真机，截图尚未形成完整证据。保留VERIFYING，不用合成SVG/PNG替代验收。
- TP-003 PASS：系统python3执行validate_miniprogram、check_architecture、validate_design_evidence --check-current-policy；VALIDATION.md的27张PNG/source SHA检查PASS；git diff --check PASS。uv原命令因缓存权限失败，改可写缓存后遇macOS system-configuration panic；相同脚本通过系统Python执行。
- 详细证据：docs/quality/evidence/SUBJECT-MANAGEMENT-20261015.md。

## 10. Completion

本地实现与自动检查完成；Feature、UI、Behavior已同步，移除了旧行尾操作路径/样式并纠正UI“只有自定义项可移出”的冲突正文。架构、API、数据库和发布手册核对无变化；旧批准快照不重生成，新增同源PNG补充清单。2026-10-15用户授权两项功能提交，联合检查见docs/quality/evidence/TWO-FEATURE-PRECOMMIT-20261015.md；未上传或发布。本Spec留在specs/active/，状态VERIFYING：补齐原生确认/视觉截图及iOS/Android、读屏验收并全部通过后才DONE迁移completed。
