# FEAT-010 / FEAT-001 — 今日按钮与编辑计划分页统一（Spec Lite）

- Status: DONE
- Development status: COMPLETE_CLOUD_DELIVERED
- Verification status: PARTIAL / FOLLOW_UP_RETAINED（具体结果见原验收记录）
- Completion date: 2026-10-26（开发归档口径确认日，非新增发布日期）
- Spec revision: SPEC-20261014-ACTION-PAGER-CONSISTENCY-02
- Completion policy revision: GOV-SPEC-20261026-CLOUD-DELIVERY-DONE-01
- Completion approval: 产品负责人（用户），本对话2026-10-26“如果已经发布到云端就认为需求已经开发完成，你来更新”。
- Previous development lifecycle: VERIFYING

## 当前开发完成结论

本Spec对应实现已包含在已交付源码中：后端范围由[037部署记录](../../docs/deploy/releases/20261024-latest-backend-test-deployment.md)及冻结02覆盖，客户端范围由[0.1.16开发上传](../../docs/deploy/releases/20261025-latest-client-upload.md)及168份源码清单覆盖，按本Spec涉及的端适用。0576ac304649的168份客户端文件及152份后端源码/依赖与发布清单逐项SHA-256匹配；本次未执行新的部署/上传。

按[用户批准的完成规则](GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)认定开发DONE并移至completed；未验收项独立保留：320/390、报表内嵌、完整截图及iOS/Android；430部分状态已采集。这些缺项不是本次补验通过，也不再作为开发归档阻塞；具体PASS/PARTIAL/NOT_RUN/FAIL仍以原证据为准。当前发布阶段为后端037正常部署、相关客户端0.1.16开发上传，未据此宣称体验/审核/正式发布、开关启用或完整产品验收。

## 原批准范围与历史执行记录

以下保留原Spec批准范围、实现决策和原始验收结果，仍用于追溯实现合同；其中“VERIFYING/留active/未部署/不能DONE”等过程判断属于2026-10-26口径调整前的历史阶段，当前开发状态由上节及Status定义。原缺失批准和未执行检查不因归档得到追认；后续本地BUG-035及旅行导入精简不在此前云端交付范围。

- Risk: R1
- Date: 2026-10-14
- Owner / Reviewer: 用户
- Implementer / Feature merge owner: Codex
- Spec revision: SPEC-20261014-ACTION-PAGER-CONSISTENCY-02
- User confirmation: 用户于2026-10-15回复“落地”，明确批准上一条展示的SPEC-20261014-ACTION-PAGER-CONSISTENCY-02及DREV-20261014-ACTION-PAGER-CONSISTENCY-02。
- Affected Feature IDs: FEAT-010、FEAT-001
- Feature current state: docs/domain/features/FEAT-010-daily-tasks.md；docs/domain/features/FEAT-001-push-kids-mvp.md

### Frontend Design Impact and Repository-native Approval

- Frontend impact / engineering impact: yes，今日每日任务完成/撤销按钮及编辑计划分页布局。
- Affected UI ID / state: UI-001 / docs/design/frontend/ui/UI-001-parent-miniapp.md
- Baseline: FDB-20260913-04 APPROVED
- FEC: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Quality dimensions: component/state/responsive/a11y/performance
- Budget: 触控≥44px，14px文字，无横向溢出，不新增资源/依赖。
- Proposed Design Revision: DREV-20261014-ACTION-PAGER-CONSISTENCY-02
- Editable source: docs/design/frontend/prototypes/DREV-20261014-ACTION-PAGER-CONSISTENCY-02/render.py及SVG
- Manifest / SHA-256: docs/design/frontend/snapshots/UI-001/DREV-20261014-ACTION-PAGER-CONSISTENCY-02/APPROVAL.md
- Viewports / states: 320×568、390×844、430×932 × content/completed/pending/last-page/long-page
- Prototype status: APPROVED
- Approved Task Spec / Design Revision / evidence: SPEC-20261014-ACTION-PAGER-CONSISTENCY-02 / DREV-20261014-ACTION-PAGER-CONSISTENCY-02 / 用户2026-10-15“落地”
- Permitted deviations: none；平台字体抗锯齿除外
- UI merge owner / evidence: Codex / docs/quality/evidence/ACTION-PAGER-CONSISTENCY-20261015.md
- External design dependency: none

### Problem and scope

每日任务daily-task-action覆盖为矩形圆角，并继承btn阴影；复习完成btn.sm为无阴影胶囊。同页同名动作风格不一致。
仅将每日任务操作复用既有胶囊radius token、box-shadow:none，与复习按钮同主色和14px字体；保留既有至少44px触控尺寸。撤销保留secondary语义。仅局部WXSS调整，不改复习按钮、点击事件、权限、API、数据与默认折叠。

用户随后提供编辑计划分页截图。content.wxss的pager允许flex-wrap，原生按钮缺少宽度约束，导致下一页掉行；禁用外观受到原生默认样式影响。新增范围：分页专用类（与报表统计pager隔离），固定三列、两侧宽度受控、中央页码居中；使用既有轻表面/松绿/圆角token，无阴影，disabled显式灰色透明底；触控≥44px。科目目录双按钮分页同样限定两列。复用共享content.wxml/content.wxss，覆盖独立页及报表内嵌；不改游标、页码、筛选或请求。超长页码仅中央栏换行，两侧按钮不掉行。

### Required views and trade-offs

- Link/call graph: 今日dailyTasks → daily-task-action → toggleDailyTask → 既有完成/撤销API，链路不变。
- Pagination graph: reports → review-inventory组件 → 共享content.wxml/WXSS；独立review-inventory页 → 同一共享content → reload/nextPage/firstSubjects/nextSubjects → 原游标读取。无新业务路径。
- Sequence: N/A，仅WXML类名与WXSS，原请求顺序不变。
- State machine: 未完成→提交中→完成→撤销中→未完成；失败保留原事实；只读无按钮。状态逻辑不变。
- Architecture: N/A，不改变模块、边界、依赖方向或扩展点。
- Trade-offs: 采用局部复用胶囊token/取消阴影，最小范围；全局改btn会影响表单主操作，不采用。不同业务完成动作不合并服务或组件。
- 分页取舍：专用三列稳定居中，减少折行；修改全局pager会扩大到统计图切页，不采用。

### Files and acceptance

- today/index.wxss：圆角与阴影；删除矩形覆盖，无新增重复按钮路径。
- review-inventory/content.wxml、content.wxss：分页专用类和两/三列、显式禁用及字体；移除该路径flex-wrap，其他pager不扩范围。组件与独立页共用，不复制实现。
- FEAT-010/001、UI-001、Spec及证据：合并已验证样式/阶段事实；Behavior Catalog与Architecture核对，业务未变则记录无需正文修改的理由。
- AC-001：每日任务完成/撤销为无阴影胶囊，字体及主色与复习完成一致，pending形状不跳变。
- AC-002：44px触控，三视口长名不重叠；完成/撤销、只读、防重和失败回退不变。
- AC-003：编辑计划分页一行三列，页码居中、两侧按钮不掉行，无原生白色大底块；首页禁用/末页禁用/加载/长页码、科目两列均可读，滚动分页及筛选保持原合同。

### Tests, plan and completion

确认Spec+DREV→局部WXSS/WXML→npm test/lint/小程序/设计/架构检查→三视口原生按钮content/completed/pending/readonly/long-name，分页首页/中页/末页/加载/长页码/科目/报表内嵌及独立页矩形与截图→iOS/Android点击及加载反馈→文档闭环。
现有业务回归覆盖动作，不新增镜像CSS实现的测试。API/后端测试N/A：合同未改。
修订01九张候选保留为历史；修订02的15张三视口候选及SHA校验通过，2026-10-15批准后实现。243项前端测试、lint、小程序静态、架构和批准设计校验通过。430宽原生内容视口430×834共11态数字几何与computedStyle已采集，完成/撤销为无阴影胶囊，分页同排等宽、触控44px、禁用透明底。320/390、报表内嵌、完整截图及iOS/Android真机NOT_RUN；未全部完成验收，不标DONE。证据见docs/quality/evidence/ACTION-PAGER-CONSISTENCY-20261015.md。
全部门禁通过才DONE并移completed，否则VERIFYING并明确缺口。本轮不自动上传或发布。
