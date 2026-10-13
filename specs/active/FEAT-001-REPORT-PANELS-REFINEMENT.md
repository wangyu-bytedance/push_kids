# FEAT-001 — 报表展开区视觉与交互修订（Spec Lite）

- Status: VERIFYING
- Risk: R1（局部展示与操作可发现性；实施若改变控制器/API边界须升级完整 Spec）
- Owner / Reviewer: 产品负责人（用户）
- Implementer: Codex
- Date: 2026-10-13
- Spec revision: SPEC-20261013-REPORT-PANELS-01
- User confirmation: 产品负责人（用户），2026-10-13，本会话回复“可以 这个方案可行”，批准 SPEC-20261013-REPORT-PANELS-01 + DREV-20261013-REPORT-PANELS-01；同时要求不影响并行的每个card背景优化。
- Affected Feature IDs: FEAT-001
- Feature current-state documents: `docs/domain/features/FEAT-001-push-kids-mvp.md`
- Feature baseline revision: 2026-10-11 REPORT-DISCLOSURES 本地状态
- Feature merge owner: Codex，实施验证后

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes，报表历史/计划展开区层级与入口标签。
- Frontend engineering impact: yes；已在本地实现报表宿主的有限展示变体。
- Affected UI IDs: UI-001；`docs/design/frontend/ui/UI-001-parent-miniapp.md`
- Frontend baseline revision: FDB-20260913-04（APPROVED）
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02（APPROVED）
- Affected quality dimensions: component/state/form/responsive/a11y/browser/performance/security/privacy/observability
- Budgets: 三视口320×568、390×844、430×932，操作目标≥44px，条目调整目标44×44px；历史每页20项，既有条目有界读取；主包≤1.5MiB。遵守FEC-PERF-READ-001～004。
- Current Design Revision: DREV-20261011-REPORT-DISCLOSURES-01；只修订本次两块展开区。
- Proposed Design Revision: DREV-20261013-REPORT-PANELS-01
- Editable design source: `docs/design/frontend/prototypes/DREV-20261013-REPORT-PANELS-01/index.html`
- Source SHA-256 / Snapshot manifest: `docs/design/frontend/snapshots/UI-001/DREV-20261013-REPORT-PANELS-01/APPROVAL.md`
- Required exports: collapsed/history/plan/both/menu × 三视口；额外整页导出便于看展开内容。
- Prototype status: APPROVED
- Approved Task Spec revision / Approved Design Revision / approval evidence: SPEC-20261013-REPORT-PANELS-01 / DREV-20261013-REPORT-PANELS-01；上述2026-10-13用户确认。
- Permitted implementation deviations: 用户同步批准卡片背景优化由并行任务负责；本任务只拥有展开区布局与交互，不修改全局tokens、pk-card背景/材质/装饰，不覆盖其他任务差异。
- Approved engineering deviations: none
- UI current-state merge: 已更新FEAT-001/UI-001本地事实；验证见 `docs/quality/evidence/REPORT-PANELS-20261013.md`。
- External design dependency: none

## 1. Problem and outcome

当前展开标题与完整历史/条目模块之间边界薄弱，筛选、独立条目卡、子分组叠加让报表像拼接多个页面；计划操作仅由省略号表达，家长不易发现。用户要求先审阅效果再实施。

推荐保持当前页面顺序及两个独立展开区：暖纸色完整容器，标题与内容由细线衔接，历史改为日期分组分隔行；计划行使用明确的「调整」操作标签并保留原菜单语义。首尾都有收起入口；顶部标签持续显示当前展开状态。默认仍收起，允许同时展开。

## 2. Scope

方案覆盖标题、内边距、分隔、搜索/状态/视图选择、日期、条目操作入口与收起。不新增API、记录、计数、复习策略或数据查询。示例数据只用于预览，不表示用户真实记录。页面其他统计和导航原样保留；预览截取科目至活动段落，不声称重设计整页。

保留历史搜索、日期/科目/来源筛选、状态、分页及详情；待处理失败/分析中仍按原合同展示。保留按时间/科目/次数、科目组收起、完整知识名称、次数/最近复习/建议或家长日期/今日状态、原安排菜单和删除二次确认。原生实施中「调整」为44×44px按钮，只读时显示「只读」及解释；不允许给每行新增固定按钮组。

## 3. Impact map and required design views

Link/call graph：报表折叠宿主 → 历史模板 / review-inventory → 原领域控制器 → 原有界API。

Sequence：点击标题 → 仅该区展开并按原合同读取 → 筛选/分页 → 点击历史行进入详情，或计划「调整」打开就近菜单 → 现有保存/删除确认 → 刷新局部状态。

State machine：收起 ↔ 展开；展开后 loading → content/empty/error/readonly；调整菜单 closed ↔ open → saving → success/error/conflict；切孩子旧响应失效，两个区默认收起。

Architecture diagram：N/A，无新增模块、边界或依赖方向。保留现有报表宿主与领域控制器结构。

| 方案 | 优点 | 代价 | 结论 |
|---|---|---|---|
| 完整纸卡 + 平铺分隔行 + 明确调整 | 延续现有展开位置，统一纸感层级，操作易发现 | 长列表仍占页面高度，需首尾收起与原分页 | 推荐 |
| 改成独立页面跳转 | 报表简洁 | 失去用户此前批准的内联展开上下文 | 不采用 |
| 两区互斥手风琴 | 缩短页面 | 查看另一块会自动收起当前块，改变既有行为 | 不采用 |

## 4. Expected file changes

已新增原型HTML、导出PNG/SHA与本Spec；修改 `pages/reports/index.{wxml,wxss}`、`pages/records/history.wxml`、`pages/review-inventory/content.wxml` 与 `components/review-inventory/index.{js,wxss}`。新增embedded呈现属性，查询及领域控制器不变。新增 `tools/report_panel_geometry.js` 和几何审计回归，更新FEAT-001/UI-001。旧获批设计清单只增加Superseded by。

## 5. Acceptance and required test points

| ID | 验收 / 验证 |
|---|---|
| TP-001 | 三视口五状态设计导出及SHA；原生实施须节点矩形验证无溢出、触控≥44px、调整按钮44×44、菜单在视口内、长标题无遮挡 |
| TP-002 | 默认收起、独立/同时展开、首尾收起、标题展开语义、筛选/搜索/分页/详情与跨页意图不回归 |
| TP-003 | 时间/科目/次数及分组，调整菜单所有原操作、只读、保存/冲突/删除确认、切孩子/迟到响应 |
| TP-004 | loading/empty/error/readonly/长中文、筛选打开、菜单打开及字体放大；错误保留已读内容，写失败保留输入 |
| TP-005 | npm test；npm run lint:miniapp；静态小程序/设计证据/架构校验；iOS/Android真机与原生三视口门禁 |

## 6. Verification and completion

已按批准范围本地实现。236项前端测试、miniapp lint、小程序静态校验、架构校验、设计SHA校验及diff检查通过；三档原生视口各12态共36态数字矩形审计通过。外层卡片继承统一pk-card背景，本任务未增加背景覆盖。

TP-001/004/005仍为PARTIAL：完整原生截图矩阵、字体放大、loading视觉和iOS/Android真机未完成；开发者工具自动化截图API未实现，320计划长标题通过CUA人工看图但未保存矩阵证据。TP-002/003复用既有回归通过，不声称完成真机全流程操作验收。详细命令与限制见 `docs/quality/evidence/REPORT-PANELS-20261013.md`。未上传或发布。完成剩余门禁后才能转DONE并迁移completed；当前保留active/VERIFYING。
