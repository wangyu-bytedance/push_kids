# FEAT-001 / FEAT-010 — 设置列表与每日任务统一（Spec Lite）

- Status: DONE
- Development status: COMPLETE_CLOUD_DELIVERED
- Verification status: PARTIAL / FOLLOW_UP_RETAINED（具体结果见原验收记录）
- Completion date: 2026-10-26（开发归档口径确认日，非新增发布日期）
- Spec revision: SPEC-20261013-SETTINGS-CONSISTENCY-01
- Completion policy revision: GOV-SPEC-20261026-CLOUD-DELIVERY-DONE-01
- Completion approval: 产品负责人（用户），本对话2026-10-26“如果已经发布到云端就认为需求已经开发完成，你来更新”。
- Previous development lifecycle: VERIFYING

## 当前开发完成结论

本Spec对应实现已包含在已交付源码中：后端范围由[037部署记录](../../docs/deploy/releases/20261024-latest-backend-test-deployment.md)及冻结02覆盖，客户端范围由[0.1.16开发上传](../../docs/deploy/releases/20261025-latest-client-upload.md)及168份源码清单覆盖，按本Spec涉及的端适用。0576ac304649的168份客户端文件及152份后端源码/依赖与发布清单逐项SHA-256匹配；本次未执行新的部署/上传。

按[用户批准的完成规则](GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)认定开发DONE并移至completed；未验收项独立保留：320/390原生、完整截图和双平台真机；430八态已有证据。这些缺项不是本次补验通过，也不再作为开发归档阻塞；具体PASS/PARTIAL/NOT_RUN/FAIL仍以原证据为准。当前发布阶段为后端037正常部署、相关客户端0.1.16开发上传，未据此宣称体验/审核/正式发布、开关启用或完整产品验收。

## 原批准范围与历史执行记录

以下保留原Spec批准范围、实现决策和原始验收结果，仍用于追溯实现合同；其中“VERIFYING/留active/未部署/不能DONE”等过程判断属于2026-10-26口径调整前的历史阶段，当前开发状态由上节及Status定义。原缺失批准和未执行检查不因归档得到追认；后续本地BUG-035及旅行导入精简不在此前云端交付范围。

- Risk: R1
- Owner / Reviewer: 用户
- Implementer / Feature merge owner: Codex
- Date: 2026-10-13
- Spec revision: SPEC-20261013-SETTINGS-CONSISTENCY-01
- User confirmation: 用户2026-10-13回复“样式修改的 按这个方案实施”，明确批准前一条展示的SPEC-20261013-SETTINGS-CONSISTENCY-01与DREV-20261013-SETTINGS-CONSISTENCY-01。
- Affected Feature IDs: FEAT-001、FEAT-010
- Feature current-state documents: docs/domain/features/FEAT-001-push-kids-mvp.md；docs/domain/features/FEAT-010-daily-tasks.md
- Feature baseline revision: FEAT-STATE-20261013-DAILY-TASKS-02-DEPLOYED；FEAT-001既有增量

### Frontend Design Impact and Repository-native Approval

- Frontend impact / engineering impact: yes — 科目单列、每日任务背景、行入口与候选面板。
- Affected UI IDs / current state: UI-001；docs/design/frontend/ui/UI-001-parent-miniapp.md
- Frontend baseline revision: FDB-20260913-04 APPROVED
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected frontend quality dimensions: component/state/form/responsive/a11y/media/performance/security/privacy/observability
- Budgets: 原生触控≥44px，正文≥14px，包≤1.5MiB，新增装饰≤40KiB；三档无横向溢出。
- Proposed Design Revision: DREV-20261013-SETTINGS-CONSISTENCY-01
- Editable design source: docs/design/frontend/prototypes/DREV-20261013-SETTINGS-CONSISTENCY-01/render.py 及SVG
- Snapshot manifest / Source SHA-256: docs/design/frontend/snapshots/UI-001/DREV-20261013-SETTINGS-CONSISTENCY-01/APPROVAL.md
- Required viewport/state exports: 320×568、390×844、430×932 × content/subjects/empty/readonly/catalog/form/error/pending/long-name/no-art
- Prototype status: APPROVED
- Approved Task Spec revision / Design Revision / approval evidence: SPEC-20261013-SETTINGS-CONSISTENCY-01 / DREV-20261013-SETTINGS-CONSISTENCY-01 / 用户2026-10-13“样式修改的 按这个方案实施”
- Permitted implementation deviations / approved engineering deviations: none（平台字体抗锯齿除外）
- UI current-state merge owner: Codex
- Visual / engineering / UI merge evidence: pending
- External design dependency: none

### 1. Problem and outcome

科目仍为三列块，每日任务保留预设按钮与独立编辑按钮，缺少独立装饰。将三块统一为既有纸面渐变、标题与小图、轻分隔列表、底部添加入口。每日任务仍位于课外活动下方。

### 2. Scope

在学科目固定三科与已加科目使用同一行布局，保留基础科目加入/移出与自定义移出限制。每日任务标题增加本地书本/时钟装饰（不同于课外活动运动图），使用整行点击编辑与尾部箭头。移除常驻预设按钮及独立编辑按钮；底部“添加每日任务”打开与活动目录相同形式的半屏候选，阅读20、跳绳10、练字20、户外运动20分钟，另有自定义入口。沿用既有分钟默认值，选择后进入名称/时长表单，保存才创建。

不改API、数据库、家庭/孩子范围、20项上限、1～180分钟、名称长度及冲突校验、删除确认、只读权限、失败保留输入、防重和跨孩子迟到响应处理。候选不自动启用。背景失败不影响操作。无需发布。

### 3. Impact map

设置Tab → settings.load → baseLearning/addedLearning/dailyTasks → 统一行。
行入口 → toggleBaseLearning/removeLearning/openDailyTaskForm；候选 → 既有表单 → saveDailyTask/deleteDailyTask → 原API。
相关测试：tests/frontend设置与daily task用例。验证后更新FEAT-001/010、UI-001及相关行为呈现描述，架构边界不变。

### 4. Required design views

- Link/call graph: 上述入口链；保留settings页面作为唯一实现路径。
- Sequence: 添加入口 → 候选半屏 → 选择预设/自定义 → 可编辑表单 → 校验 → 保存原API → 刷新列表；编辑行直接进入表单。
- State machine: closed → catalog → editing → saving/deleting → success；失败回editing保留输入；只读无写入口；切孩子关闭候选/表单并作废迟到请求。
- Architecture: N/A，页面内部视图状态改变，没有模块边界、共享抽象或依赖方向改变。
- Trade-offs: 采用候选半屏与活动一致、卡片更清爽，但多一次点击；保留常驻按钮可少一次点击，但与用户明确要求的活动形式不一致；不新增自动创建默认数据。

### 5. Expected file changes and deletion plan

- settings/index.wxml、index.wxss、index.js：统一科目与任务行，候选面板及装饰失败状态；移除失用subj-grid、preset/Edit样式。
- assets/illustrations：新增≤40KiB每日任务本地装饰，由设计SVG导出，不加运行时依赖。
- tests/frontend：覆盖候选分钟、保存确认、编辑、只读、防重、切孩子与失败保留输入。
- 本设计证据、Spec、FEAT-001/010、UI-001：合并实测最终事实；旧科目待批稿及每日任务视觉稿按实际取代范围整理生命周期。

### 6. Acceptance criteria

AC-001：科目无三列色块，三块卡片的标题/图标/分隔/添加入口一致；每日任务有独立背景装饰且在活动下方。
AC-002：预设仅填表；分钟可编辑，保存才生效；自定义、编辑、删除、权限、错误恢复和范围不变。
AC-003：三视口所有状态、最长30字符任务名、键盘表单可达且无重叠；触控44px；图失效仍可用。

### 7. Required test points

TP-001：npm test、npm run lint:miniapp；有意义的候选/交互/权限/失败/跨孩子回归。
TP-002：三视口微信原生矩形与截图；科目选/未选、任务空/只读/候选/表单/错误/pending/长名/无图。
TP-003：iOS/Android添加预设、修改分钟、自定义、取消、编辑/删除确认及读屏检查。
TP-004：validate_miniprogram、validate_design_evidence、check_architecture；素材alpha、大小和包预算检查。

### 8. Plan

确认本Spec与DREV → 页面实施 → 自动检查与原生验收 → 更新当前状态及Spec生命周期。

### 9. Verification

设计已批准，已实施；npm test 239项、lint、静态、架构、设计、diff与资源检查PASS。430原生八态PASS，320/390原生、完整截图、真机NOT_RUN：Mac锁屏、截图接口unimplemented、无真机。详见docs/quality/evidence/SETTINGS-CONSISTENCY-20261013.md。

### 10. Completion

本地实现与自动检查完成，已合并FEAT-001/010及UI-001；API/架构不变。源码5837d59，前端0.1.15开发上传成功，1027271字节，13项云端读smoke 200；未体验/提审/正式发布。两档原生、完整截图及真机验收仍待补，保留VERIFYING，见docs/deploy/releases/20261013-settings-consistency-frontend.md。全部门禁完成后DONE并移completed。
