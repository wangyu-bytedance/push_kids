# FEAT-001 — 家庭学习持续跟进系统 MVP

- 2026-10-24旅行界面减法：用户明确批准足迹精简Spec01/DREV01，记录Tab旅行组件及原足迹页共享实现去掉重复身份标题、收起次要操作、设置只留开关和保存。最终331项前端、三尺寸27态原生及430实际菜单操作通过，CR-001在已批准迟到保护范围修复；UI文案要求已并入工程规范。原学习入口/表单及确认合同不变；[当前证据](../../quality/evidence/footprints-minimal-20261024/README.md)区分本地原生与真机待验，未上传部署。

- 2026-10-24年级确认本地增量：五Tab新增共享宿主，已有弹层/上传/未保存输入时等待，包含报表筛选表单；学习、复习和AI消费者仍只读取正式grade。年度建议确认只写children，不创建学习记录、Review或Todo；[FEAT-013证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)含零副作用、原API/启动/看板回归、三尺寸呈现及独立评审PASS。当前未部署，修复后原生端到端、设备与可访问性验收待补。

- 2026-10-24本地今日增量：两份Spec04、Architecture02/03与`DREV-20261024-TODAY-LEARNING-01`已获用户「批准，按此实现」。空白日先处理自然到期；没有到期才从符合3日/80%/2日条件的已复习知识中提前少量安排，≤10分钟且不超孩子预算，原日期不变。只有初始`provisional_empty`可因正式库存代次变化重判，处理过的计划和旧计划不补排。另见[FEAT-004](FEAT-004-daily-learning-suggestions.md)的两完整自然日无新增建议→家长批准待学→实际确认入档。两开关默认关闭，迁移0023/0024只在本地验证，本增量未上传部署，完整验收仍VERIFYING；[本轮证据](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)。

- 2026-10-24记录入口本地增量：用户批准`BUG-SPEC-20261024-RECORD-ENTRY-05 / DREV-20261024-RECORD-ENTRY-01`后，记录标题改为顶部两项下拉，右侧复用纸色孩子chip；类型菜单保留Tab，旅行照片/编辑面板仍隐藏Tab。普通Tab记住类型，未提交学习表单/幂等键/滚动保留；今日与报表明确学习入口经原离开保护切回学习，修复旧确认跨代结束未续接新学习意图的问题。旅行默认全部已确认足迹，删除日期筛选；列表按最多100条窗口续看，导入是内容下方48px普通按钮，权限/同意/人工/确认合同保持。替代10-23入口的对应外观与筛选描述，详见[本轮验证边界](../../quality/evidence/record-entry-20261024/README.md)。本增量未上传或部署，真机验收待补。

- 2026-10-20本地前后端增量：`SPEC-20261020-AUTO-SUPERSEDED-REVIEW-02`与`DREV-20261020-SUPERSEDED-REVIEW-01`已批准并实现；AI在原学习确认后自动应用单项完整覆盖，旧词条永久停止自动排期，历史不合并、不删除、不伪造。存量任务使用持久游标及租约；既有人工预约保留一次。独立页及报表内嵌默认「参与复习」，支持「已替代」筛选、承接关系与原学习记录，菜单仅删除。自动化通过，完整原生/真机验收待补，未部署。见[实现与验收边界](../../quality/evidence/AUTO-SUPERSEDED-REVIEW-20261020.md)。

- 2026-10-17本地复习完成协作：已批准并实现`SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01`。仅可信本人成功的手动complete在原反馈事务内新增去重完成游标；今日点击同步尝试已准备好的本人授权，首次说明须显式开启。复习结果、科目顺序和日期政策不变，每日任务不触发。真机及独立评审待补，未上传/部署。当前能力见[FEAT-011](FEAT-011-notification-auto-renewal.md)和[实现证据](../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)；此增量不代表线上发布。

- 2026-10-17通知受控验收：已批准`OPS-SPEC-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE-05`及家庭接收范围；经既有API创建1条临时非重复日程0F58（201），原通知调度使当前账号投递sent/ok（18:49:19 CST），随后仅停用该日程（204）并确认当日日程中匹配数0。用户随后明确确认微信“已收到”（call_5b80efd7f9504c4ca286e2df7e031c75），补齐该账号本次实际收件证据。未改日程/学习/复习合同、代码或发布状态；不代验其他成员。见[证据](../../quality/evidence/NOTIFICATION-HTTP-DIAGNOSIS-20261017.md)。

- 2026-10-16复习科目保序修复：`BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01`已批准并实现，反馈后仍按原计划各科最早ordinal展示；全组无待复习项才移除空组。后端518 passed/19 skipped、前端244 passed，补充MySQL18项及冻结容器检查通过。当次历史阶段为031 normal/0%、030 100%，当次定向smoke与全量人工门禁未留验收证据；2026-10-24只读复核当前031 normal/100%，不据此补写当次smoke PASS。见[历史发布](../../deploy/releases/20261016-review-subject-order-backend.md)、[验证证据](../../quality/evidence/REVIEW-SUBJECT-ORDER-20261016.md)及[当前部署准备](../../deploy/releases/20261023-fullstack-test-deployment.md)。

- 2026-10-15学科管理本地增量：SPEC-20261014-SUBJECT-MANAGEMENT-01 / DREV-20261014-SUBJECT-MANAGEMENT-01已批准并实现。学科行统一箭头进入管理面板，移出位于面板底部；基础三科与可移出自定义科目均二次确认，已有学习记录保留。未加入基础科目仍可加入，其他科目沿用 canRemove 限制；只读无写入口，失败留面板重试，切孩子/离页丢弃迟到回调。取代原学科行尾直接加入/移出入口，未上传/发布。验收与未执行项见 [本轮证据](../../quality/evidence/SUBJECT-MANAGEMENT-20261015.md)，Spec 保留 VERIFYING。

- 2026-10-15本地按钮与分页增量：SPEC-20261014-ACTION-PAGER-CONSISTENCY-02 / DREV-20261014-ACTION-PAGER-CONSISTENCY-02已批准并实现；每日任务无阴影胶囊，编辑计划共享分页固定三列、科目两列及显式禁用。243项前端测试和静态检查通过；430宽11态原生部分验证，完整三视口/内嵌/截图/真机待补，Spec为active/VERIFYING。本增量未上传；既有最新开发上传基线0.1.15（5837d59）。详见docs/quality/evidence/ACTION-PAGER-CONSISTENCY-20261015.md。

- 2026-10-13设置最新增量：SPEC-20261013-SETTINGS-CONSISTENCY-01 / DREV-20261013-SETTINGS-CONSISTENCY-01批准并实现；在学科目改活动同款单列行，保留原加入/移出限制。每日任务同款行、独立背景及候选/编辑半屏。239项测试、静态及430原生八态通过；源码5837d59随0.1.15开发上传成功（1027271字节），未体验/提审/正式发布；320/390原生、完整截图、真机待验收。详见docs/quality/evidence/SETTINGS-CONSISTENCY-20261013.md，任务VERIFYING。

- Design governance revision: `DOC-SPEC-20261013-02-01`；[门禁同步记录](../../../specs/completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md)，仅修订设计证据政策，不改变实现/发布状态。

- Local report panel refinement: `SPEC-20261013-REPORT-PANELS-01 / DREV-20261013-REPORT-PANELS-01` 已获用户批准并本地实现。历史和编辑计划统一展开容器，明确展开/收起及调整入口；查询与计划策略不变，外层背景由统一卡片样式负责。236项前端测试、三视口36态原生数字几何及静态校验通过；已随0.1.14开发上传，完整截图、字体放大与真机验收待补。证据：`docs/quality/evidence/REPORT-PANELS-20261013.md`。

- Status: `CURRENT`
- 当前发布状态：最新客户端开发上传仍为0.1.15（源码5837d59），本次仅启动完整本地客户端、不上传。2026-10-24用户指定同库升级顺序，10:55生产0019→0022/current/check与结构/队列核验通过；035部署后由用户100%接管并删除034，11:01–11:03官方观察旧实例0、035 normal/100%/1实例。真实微信18项读取含live/ready和新足迹/续订均200，本地实际进入旅行日记；coverage=false，永久替代关闭。见[本次发布](../../deploy/releases/20261023-fullstack-test-deployment.md)。全量前定向验收未执行，当前生产写路径/真实照片/多账号/完整原生真机待用户验收，未沿用历史030/0019的smoke结果。
- Local complete card backgrounds: SPEC-20261013-CARD-BACKGROUNDS-01已按用户明确指令本地实现，设置三块插画、每日任务同款卡片与新位置、报表背景均已接入；238测试和CLI预览通过，已随0.1.14开发上传，原生/真机/用户验收待补。证据docs/quality/evidence/CARD-BACKGROUNDS-20261013.md，未设体验版/正式版。
- Local illustrations: `SPEC-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01 / DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01` 已获用户批准并本地实现；记录/日程使用不同纸艺插画，原业务不变。233项前端测试及静态校验通过；原生三视口、真机及预览包预算待验证，未发布。证据：`docs/quality/evidence/RECORD-CALENDAR-ILLUSTRATIONS-20261013.md`。
- Local daily tasks: `SPEC-20261012-DAILY-TASKS-01 / DREV-20261012-DAILY-TASKS-01` 已获用户批准并实现前后端。
  设置可配置孩子的每日任务和分钟，今日复习安排下方完成/撤销；四区块空或全完成默认收起，有剩余展开，学习记录非空展开。
  具体当前事实见 `FEAT-010-daily-tasks.md`；本地验证记录 `docs/quality/evidence/DAILY-TASKS-20261012.md`，生产0019/030及读取smoke见`docs/deploy/releases/20261013-fullstack-diff.md`。隔离MySQL验证通过，完整原生/真机及生产写路径验收待补。
- Release gate policy: `SPEC-20261011-RISK-BASED-RELEASE-GATES-01` 已获用户批准；不涉及身份/权限/图片归属的前端发布不重复执行双账号隔离与 owner 验收，须记录影响判定并验证本次主路径及目标后端兼容性。首次公开生产发布仍需确认既有安全基线有效；历史验收结论不因门禁变化而改写。
- Local report disclosures: `SPEC-20261011-REPORT-DISCLOSURES-01 / DREV-20261011-REPORT-DISCLOSURES-01` 已获用户2026-10-11批准并在本地实现。
  报表「科目学习记录」与「课外活动投入」之间依次加入默认收起的「历史记录」「编辑计划」；两区独立展开，复用原有界历史及复习条目行为。记录页保留新增表单和待处理入口，完整历史移到报表；今日待处理和报表科目行均可带意图打开报表历史。三视口四状态原生数字几何及自动化检查已通过；`0.1.13` 开发版本已上传，iOS/Android 真机尚未验收，未设体验版/正式版。证据：`docs/quality/evidence/REPORT-DISCLOSURES-20261011.md`、`docs/deploy/releases/20261011-report-disclosures-frontend.md`。
- Local review-inventory redesign: `SPEC-20261010-REVIEW-INVENTORY-REDESIGN-01 / DREV-20261010-REVIEW-INVENTORY-02` 已获用户2026-10-10批准并在本地小程序实现。
  复习条目页移除重复内容标题，时间为双日单层筛选，科目/次数为当前值下拉；时间/次数仍按当前有界页科目折叠，单科改为直接清单，逐行完整显示次数、最近反馈、日期与今日状态。科目翻页不自动改变当前选择，原排期/删除接口及权限不变。
  前端216项、静态与三视口10组原生几何通过；该客户端实现随 `0.1.13` 开发版本上传，iOS/Android真机及风险状态补充证据待验收，未设体验版/正式版。证据：`docs/quality/evidence/REVIEW-INVENTORY-REDESIGN-20261010.md`。
- Local settings activity ordering: `SPEC-20261010-ACTIVITY-WEEKDAY-ORDER-02` 已获用户批准并实现。
  设置页课外活动按首时段星期（周一至周日）、开始时间升序；无有效星期/时段排最后，同键保序。
  原UI、其他列表、API与排期不变；前端213项及静态检查通过，该排序随 `0.1.13` 开发版本上传，原生三视口待验收，未设体验版/正式版。
  证据：`docs/quality/evidence/ACTIVITY-WEEKDAY-ORDER-20261010.md`。
- Historical review-inventory presentation superseded locally by the 2026-10-10 redesign: `SPEC-20261007-REVIEW-GROUP-CARDS-05` 曾获用户批准并在本地实现。
  复习条目目录按当前有界页的科目分组、可折叠；条目“…”菜单沿用既有调整/删除接口，筛选仍使用服务端原有日期、科目、精确次数条件。
  本修订只改变客户端呈现及交互，不改变复习计数、排期或反馈语义。三视口原生数字几何和前端测试已通过；设计快照和真机验收仍待完成，未部署。
- Local fair-review implementation: `SPEC-20261007-FAIR-REVIEW-01` 已批准并实现科目覆盖、首次/再次机会和实际计划日等待优先。
  预约优先、真实反馈计数与当日快照保持原合同；日期与安排状态分开。补充修订02已批准并实现事务性索引投影，
  最终5万条MySQL查询最大163ms；独立审查未发现剩余代码阻断项。旧业务兼容包已验证0014/0018启动校验。
  云端已创建旧业务兼容过渡灰度版本026；尚未确认其流量接管，生产迁移及新策略发布与原生验收待完成。
  证据见`docs/quality/evidence/FAIR-REVIEW-PROJECTION-20261007.md`。
- Local analysis change under verification: `BUG-SPEC-20261006-STAGED-ANALYSIS-01` — default provider
  changed to bounded per-material extraction, consolidation, server-owned history lookup and alias matching.
  Successful stage DTOs resume across retries; cancellation/manual confirmation/delete clean temporary data.
  This does not describe a deployed release. Evidence and remaining quality gates are in
  `specs/active/BUG-028-STAGED-ANALYSIS-RELIABILITY.md`.
- Revision: `FEAT-STATE-20261024-TODAY-LEARNING-01-LOCAL`（保留2026-10-15及更早增量的各自验收/发布状态）
- Review management: `SPEC-20261006-REVIEW-MANAGEMENT-03` 已获用户“落地并实现”批准并本地实现。
  报表独立条目页按明天/后天、单科学习科目、精确复习次数查看；删除清理相关历史和计划，手动改期不计复习。
  今日下一次复习入口移除；后端兼容字段暂保留。预约优先且显式提示预算超量，120项硬上限、幂等及状态冲突由服务端控制。
  自动化、真实MySQL与独立复查通过，原生视觉/真机验收待补；未发布。证据：`docs/quality/evidence/REVIEW-MANAGEMENT-20261006.md`。
- Last verified: 2026-10-06，`SPEC-20261006-SOURCE-DELETE-02` 精确原图与单知识点删除已本地实现；
  自动化、隔离 MySQL 5.7 与微信 preview 结果见该 Spec 的 verification record；未部署后端或发布前端。
  原生三视口、iOS/Android 与独立人员审查仍待完成。
- Previous verification: 2026-10-02（`SPEC-20261001-VOICE-INPUT-03` 已本地实现：前端 184 passed、后端
  389 passed / 5 optional skipped，ESLint、小程序静态 15 pages/685412 bytes、Ruff check/format、Mypy、
  架构与设计策略均通过；真实 AppID preview 650045 bytes 通过且未上传。开发者工具麦克风授权返回
  `errno 112`；管理员补充麦克风信息并清除 compile/network 缓存后复测仍未生效，原生三视口与
  iOS/Android 继续等待隐私指引审核/生效。
  此前 `BUG-SPEC-20260926-EMPTY-PROPOSAL-QUALITY-02`：后端
  389 passed / 5 optional skipped、前端 170 passed、性能/E2E 3 passed，Ruff check/format、Mypy 86 files、
  ESLint、架构 checked=3、设计策略与小程序静态 15 pages/667593 bytes均通过；隔离 MySQL 5.7.44
  已从空库重跑 migration/current/check 与 5 个运行时专项。全新固定交错 40-case live Ark 完整运行
  40/40，端到端与语文/数学/英语语义率均 100%，empty/remaining pending 与 formal writes 均为 0；
  后端不可变灰度版本 `flask-ik19-025` 已创建并为 `normal`，服务 `normal`、PUBLIC 关闭；尚未切换/核验
  灰度流量、执行真实 AppID smoke 或生产修复 apply）
- Source Spec: `specs/completed/FEAT-001-PUSH-KIDS-FINAL-SPEC.md` revision `SPEC-20260831-08`
- Latest implemented Spec: `specs/completed/BUG-027-EMPTY-ANALYSIS-PROPOSAL-QUALITY.md`
  revision `BUG-SPEC-20260926-EMPTY-PROPOSAL-QUALITY-02`（固定跨科目轮转与双分母门禁已实现并完成
  40/40 live Ark 验证及终态独立只读审查；后端 `flask-ik19-025` 灰度不可变版本已创建，生产数据
  apply 尚未执行）
- Pending completion Spec: `specs/active/FEAT-001-ARK-CONTEXT-REUSE-FLAG.md` revision
  `SPEC-20260919-ARK-CONTEXT-REUSE-01`（默认开启的 attempt-local Ark Responses 会话续接；未部署）
- Pending verification Spec: `specs/active/FEAT-001-VOICE-INPUT.md` revision
  `SPEC-20261001-VOICE-INPUT-03`（本地实现和自动化已完成；平台后台、隐私与原生真机门禁未完成）
- Previous applied Spec: `specs/completed/BUG-021-TODAY-REVIEW-PLAN-VISIBILITY.md` revision `BUG-SPEC-20260912-REVIEW-VISIBILITY-01`
- Previous applied Spec: `specs/completed/SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH.md` revision `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01`（frontend only）
- Pending verification Spec: `specs/active/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md`
  revision `SPEC-20261006-SOURCE-DELETE-02`（本地代码已实现；尚未满足全部原生验收与独立审查门禁）
- Current visible contract: `docs/design/frontend/prototypes/DREV-20261006-SOURCE-DELETE-01/FRONTEND-SPEC.md`
- Intermediate design artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`

## Purpose and current behavior

本地视觉增量revision `FEAT-VISUAL-20261021-HERO-ARC-01`：按已批准
[BUG-SPEC-20261021-HERO-ARC-01](../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md) 与
DREV-20261021-HERO-ARC-REMOVAL-01，所有共享卡片去掉右下角细弧线；今日正常/引导、日程、记录、
报表与设置四张卡一起生效。原渐变、插画、布局和业务保持现状；本轮验证、原生/真机边界见
[质量证据](../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)。仅本地实现，未上传/发布。

家长记录小学阶段孩子真实学过的内容。照片、手动文字或语音转成的可编辑文字创建异步分析任务；AI 只生成可编辑草稿，
家长确认实际已学后才写入学习记录、知识点出现历史和复习计划。复习仅安排已经学过的知识；FEAT-004独立提供一项可编辑增量提案，采纳只建立待学，不宣称下一课必须学什么，不自动批改或判断掌握。活动只进入日程、练习记录和温和提醒，不进入记忆曲线。

原生微信小程序有五个 Tab：今日、日程、记录、报表、设置，共 15 个已注册页面。五个一级页使用
共享 `components/primary-nav`，按状态栏和右上胶囊几何在导航中央显示唯一“芽图标 + 知芽”，内容区
直接从各页句子式 hero 开始；确认、记录详情、家庭与设置子页继续使用微信原生标题和返回行为。
视觉与交互基线是 PKDS-2.0（`FDB-20260913-04`），当前增量合同为
`DREV-20261001-RECORD-VOICE-INLINE-03` 与 `DREV-20261006-SOURCE-DELETE-01`。HTML DREV-03 与 UX-03/UX-04 保留为评审过程的阶段性产物，
不参与运行。

## Current invariants

- 复习待办每项返回结构化来源：`source_submission_id`、`source_occurred_on`、`review_round`
  （= `step + 1`）、`interval_days`（= 到期日减去最近一次复习反馈日期，无反馈则减去首次学习
  日期，两者都缺为 `null`），以及从首次确认 evidence 安全投影的可空 `source_summary`、
  `source_image_index`。坏 JSON、空证据和越界图片序号只降级可空展示字段，不隐藏 Todo。
  当前复习卡不再显示“出现原因”，而是按知识点显示最多两行原题提示，并仅在存在来源提交时提供
  当前页原始照片/文字弹层。照片按写入时分配的 `sort_order` 稳定排序（详情、分析取图一致）。
  Today 精确模式在请求预览之前，仅选择 `source_submission_id + media.index` 对应照片，保留原编号，
  隐藏混合批次的其他原文；历史详情仍展示整次提交。图片 index 必须为 1..9 的严格整数；
  主图取首条有效图片证据，摘要取同条描述。旧 evidence 必须能在来源提交确认提案中证明归属；
  不能证明时清空关联，不猜第一张，不回退全批。缺少来源 ID 的旧文字摘要保留但不提供原图入口。
  后续同知识确认不再为首次来源补入其他提交的 evidence。
  正式知识点保存机器识别的 `confidence` 与 `evidence`（仅识别可靠度与出处，不表示掌握程度），
  首次确认写入后不被后续确认覆盖；本次修订之前的历史数据没有这两个字段。科目区分系统预设
  （`语文/数学/英语` 且 `kind=learning`，`is_custom=false`）与家长自建（`is_custom=true`）。
- Today 更多菜单在“今天先跳过”下提供“删除记录”，manager/editor 经二次确认调用
  `DELETE /children/{child_id}/knowledge/{knowledge_id}`；viewer 不显示入口且服务端拒绝写入。
  单事务删除当前知识身份、全部出现关联、复习、反馈、搜索词和日计划关联，保留原提交、
  原总结、共享媒体和同批其他知识。重复请求为204；错误整体回滚。日计划不补入额外项目，
  删除物化计划之后新增的知识不减少旧计划计数；待发送复习通知在投递前按存活知识重算。
- 历史回看已在本地实现：记录页展示统一照片+文字新增表单和待处理入口，完整历史在报表科目统计后默认折叠；
  折叠时只读取待处理数量，展开、待处理入口或今日/报表显式意图才读取完整列表，
  viewer 展开后只读。已确认/待处理/全部共用分页入口；
  详情由独立的只读页面 `pages/record-detail/` 承载（已入档只读态与待处理态），确认页只承载
  可编辑草稿；两者共用同一份只读 mixin 与模板，展示正式总结、本次知识、原始材料和关联知识
  截至现在的复习反馈。今日和报表科目行可带日期/科目跳入；到期项回到今日反馈。浏览不写学习、
  知识、Review 或 Feedback。
- 记录页的学习内容输入框本地实现内嵌 44px 麦克风热区：已授权时按住调用 WechatSI 单次最多
  60 秒普通话识别，松开后只把最终结果以一个换行追加到既有 `text` 草稿。首次隐私/麦克风授权
  完成后必须重新按住；上滑 80rpx、`touchcancel`、切孩子、离页和卸载均取消并丢弃迟到回调。
  合并超过 4000 字时原文不变，待加入文字可编辑或放弃。音频、临时路径和插件 payload
  不进入业务后端、存储或日志；转写文字仅在家长主动提交后作为既有 `input_text` 进入草稿流程，
  不写客户端日志或本地存储。Submission source、API、数据库、AI 确认和复习策略均未改变。
- 记录详情的复习反馈读取先取最多 20 个关联 Review，再对每项执行 family-scoped、按
  `(occurred_at desc, id desc)` 稳定排序且 `LIMIT 4` 的查询；对外仍是每页 3 条与既有
  `next_before` 合同。零反馈返回空数组，失效或越界游标拒绝，不把后端错误伪装为空成功态。
- 历史列表每页 20 条、最多 50 条，稳定游标排序；已确认按学习日期，其他按提交日期。
  无 view 参数的旧 history 接口保留兼容；新 UI 不再依赖 100 条待处理草稿接口。
- 所有随历史增长的读取都有稳定顺序和服务端硬上限。Todo/dashboard 首屏最多 20 项，后续通过与
  家庭、孩子、日期和快照绑定的游标继续，精确总数与 required/optional 分组覆盖整个快照；并发新增或
  更新不会混入旧遍历。活动记录与提交兼容数组最多 100 项并通过响应头续页；报表最多 100 天，其
  总览、趋势和 `activity_subjects` 由同一范围的 SQL 聚合产生，科目明细最多 50 项且显式报告省略量。
- Dashboard 还嵌入最近一个未来 learning Review 日期的前 5 项、该日精确总量和分钟；续页接口每次
  最多 20 项，游标绑定家庭、孩子、查询日与快照。今日页把它作为只读计划透明度展示，不提供反馈或
  带练；有到期项时仍以今日 Todo 为主。缺少该新增字段的旧服务端只显示今日到期事实，不声称未来为空。
- Dashboard 的 `review_selection` 来自每天一个幂等物化的 `DailyReviewPlan`。候选为
  自然到期`Review.active=true AND due_date<=today`及既有人工预约优先，正常自动候选要求Knowledge.review_status=normal，按现行fair-v2有界候选和孩子分钟预算装入，不固定限制6条。启用空白日开关且自然到期总量为0时，才使用最多3槽/条的索引投影选少量提前项；首次复习、手动日期、无效科目不提前，原due_date保留。只有初始空计划可按库存代次重判；完成/部分/巩固/稍后只改变原计划项，当天不补题；未入选
  积压不改 due_date、不写 Feedback。返回精确 `total_due/backlog_count/earliest_due`、计划/待复习数量
  和分钟、policy revision。本地2026-10-16修复使sessions按各科在原计划中最早ordinal保序：已反馈行仍作
  顺序锚点，只把pending行放入卡片；全科无pending才移除空组。仅涵盖原计划行集合不变的反馈，不新增删除/
  手动改期后的保序保证。旧 `todo_groups` 分页合同继续保留；小程序优先消费稳定计划，并在两条
  投影中使用同一 source summary/index 合同。
- 原图每次经家庭/孩子/提交/媒体关联验证；viewer 允许读取，被移除成员拒绝新读取。
  云端签发最长 60 秒 GET 链接，本地下载每次带身份；临时文件退出清理。真实云端双账号 owner
  隔离与 metaid 解码已于 2026-09-06 由用户确认验收通过；合法域名和设备矩阵仍按各自发布门禁记录。
  搜索文字经编码请求头传输，不进入访问日志 URL；预览签发在单进程内限制为每成员每分钟 120 次
  （一次展开九图并逐张查看原图不再被自身限流打断）。云环境客户端直接使用签发的 HTTPS 地址渲染，
  本地环境保留带身份的容器下载。

- 所有查询与写入在 API 边界按家庭隔离；跨家庭资源返回 404。
- 云环境由微信入口 actor 的 HMAC binding 解析家庭，拒绝客户端 `X-Family-ID`；本地/测试
  仍保留显式开发身份。
- 运行时只允许 Ark；确定性 Provider 仅允许显式 `test/e2e` 环境，运行库没有种子/示例数据。
- 未确认草稿不能改变正式学习、知识、复习、Todo 或报表。
- 学习确认只接受服务端解析为 `learning` 的科目；新 activity 提案、已有 activity ID 或同名
  活动均返回 400，草稿保留且不写正式数据。家长显式选择已有 learning 科目时以该科目分类为准。
- 一份提交可以产生多条学习记录，每个科目一条：`learning_records.submission_id` 从唯一约束改为
  普通索引（Alembic `20260906_0004`）。科目身份由 `agent_processing/subject_routing.py` 的确定性
  路由决定，不采信模型字面：拆分 `、，,；;／/｜|＋+&＆·・.。：:` 与空格、去掉 `以及/和/与/及/跟`
  连接词与 `自定义/综合/混合/其他/未知/多科目/跨科目/多学科/合并` 等 stopword，再按家庭已配置科目
  别名匹配（`英文`→`英语`、`math`→`数学`）。因此不再创建 `数学、语文` 这类合成科目。
- 目录里没有的科目名标记为未列出，必须家长在确认时显式同意新增；缺同意时确认返回
  `409 consent_required`，草稿保留、不写任何正式数据，也不自动建科目。
- 确认支持 `groups[]`（每组 = 一个科目 + 该科目的知识点位置 + 可选摘要）。索引以客户端看到的
  知识点位置为权威，服务端只在每个科目桶内去重，避免全局去重造成索引移位。缺 `groups` 的旧客户端
  仍走单科目路径；`ConfirmationResult` 保留 `record_id`/`subject_id` 并新增 `records[]`。
- 活动从既有活动记录入口保存。历史 activity Review 保留但退出 Todo、带练、AI Todo 候选、
  手动/匹配反馈和复习统计；原有活动记录、日程、练习频次与建议不变，历史学习记录不重写。
- 旧Agent对照路径首轮输入包含本次图片/完整文字、实际发生时间、已填写年级、最多30个已配置学习科目，以及由这些
  科目加缺失系统预设 `语文/数学/英语` 组成的稳定去重分析科目集合（最多33个）。严格输出 Schema 与
  history tool 科目 enum 使用分析科目；确认仍只信任服务端科目目录，未配置预设科目仍需家长明确同意。
  输入还包含目标上海
  自然日内最多200个已确认条目，以及发生日为今天时的完整 `today_review_plan`；不一次性加载历史
  LearningRecord 或 KnowledgeItem。今日计划和历史候选都只是匹配上下文，不是本次已复习的证据。
- 当前本地默认：逐材料最多并发2，精确重复图片保留首图编号；必要时最多两组相邻页联合补充。
  合并必须完整覆盖每个提取候选，最多20项，不允许漏材料后成功。服务端对合并后的每个名称执行
  family/child/subject限定历史查询，再让模型只返回短别名；规范名称、数据库ID和证据由服务端装配。
  所有新阶段使用 `store=false`、显式关闭思考、45秒提取/30秒合并匹配上限，并服从整个租约预算。
  仅已验证阶段DTO进入24小时临时表，成功、取消、人工确认及家庭/孩子清理即删除；失败阶段不产生
  部分可确认草稿。原公开proposal、家长确认、计划策略和手动路径保持原合同。
- 以下旧Agent传输流程仅保留作对照工具和回归测试消费者，不是当前默认工厂行为：
  未由同日/今日计划匹配的每个候选，模型先生成关键词调用 `search_history_items`。工具由服务端注入
  family/child，只允许指定分析科目；未配置预设科目安全返回空历史，使用每 Item 最多32个确定性
  exact/token/n-gram 索引词；单次
  最多20项；一次工具调用以 `queries[1..20]` 批量提交当前全部未匹配候选，每个 query 仍计一次逻辑调用，
  总共最多20次/100个唯一候选/8轮。第8轮只允许 final；进入 Provider 前按持久化5分钟 Job lease
  的剩余时间扣除30秒写回余量，得到整个 Agent attempt 的动态截止时间（满额最多约270秒），并把
  剩余时间传给每次 Provider 调用。SDK 内部网络重试关闭，持久化 Job attempts 是唯一重试所有者。
  tool 参数 JSON/shape/type/range/subject 非法时不执行查询，只回传静态 `tool.arguments`，让模型在
  同一 loop 的剩余轮次内修正。每个 query 的 `candidate_key` 必须逐字等于准备输出的最终 `name`，
  `subject_name` 必须与最终科目键相同；成功查询后不得改名、合并或拆分，确需调整时按每个最终名称
  重新批量查询。Runner 持有可信 ledger 并把 final validator 回调交给 Provider；最终输出若仍出现
  未完成同名查询的 new 候选，Provider 在当前 Agent loop 内返回静态纠错说明，允许补查后重出完整 JSON，
  而不是立即升级为完整 Job attempt。Provider 不支持/遗漏回调时 Runner 仍保留最终拒绝防线。
  工具/时间/轮次耗尽或语义不确定时不能猜成新知识。
- 旧Ark对照Provider多轮传输启用 attempt-local Responses 会话续接：首轮 `store=true` 且 `expire_at` 最多10分钟，
  后续轮只通过 `previous_response_id` 发送新增工具结果或校验修正，终态 best-effort 删除本次 response。
  `ARK_CONTEXT_CACHE_ENABLED=false` 回退到 `store=false` 完整累计输入重发；它不能关闭 Ark 对当前模型
  自动启用的隐式前缀缓存。两种模式每轮都保留 strict JSON Schema，不发送显式 `caching`，response ID
  只存在于单次 Provider 调用内，不跨 Job/retry/家庭/孩子，也不写数据库或日志。
- 旧Provider规则在 `agent_processing/prompt.py` 以 `child-aware-history-agent-20260923-08` 版本化；新规则在
  `stage_contracts.py` 版本化，均不读取
  个人SKILL目录。Ark 必须按本次 analysis subjects 返回固定键的 strict JSON Schema，条目明确
  为 `new`、`today_review` 或 `history_item`；模型总输出最多20项、每项1–5分钟，`review_method`
  只能是主动回忆/变式练习/解释应用。条目按同科目、同目标和同动作聚合为家长可确认的短复习单元；
  Markdown fence、额外科目/字段和非法引用不再由正则修补。Provider
  校验失败后只把校验代码带入下一轮，不保存原文。输出/引用校验、Agent预算和临时 Provider/存储故障
  由显式 disposition 判为可重试，最多执行3个持久化 Job attempts；schema capability 和确定性输入/配置
  不变量首个 attempt 即终止。第3次非法输出终态为 `analysis_output_invalid`，传输/超时最终为
  `analysis_failed`，能力不支持为 `analysis_schema_unsupported`。
  `name` 必须表达家长可执行的知识动作，年龄、购物、动物等普通题目情境不能代替学习目标；
  `direct_evidence.detail` 用一句不编造条件、答案或步骤的家长可读原题摘要。模型 summary 必须是
  一句不超过 60 字、只描述本次实际学习/练习内容的简短事实；“没有识别到”
  “不包含”“未涉及”“无某科内容”等缺失项说明会以脱敏 `summary.exclusion_clause` 拒绝并进入同一
  有限重试。该限制不替代家长编辑和历史记录的 500 字合同，也不误伤“不规则图形”等真实概念。
  服务端再校验证据、历史/知识/Review引用并精确过滤同发生日重复项；最终知识点和 Todo 匹配同时为空
  时以 `proposal.actionable_items` 在同一 Agent loop 内纠正，持续为空才进入既有最多3次 Job retry，绝不
  写入 `pending_confirmation`。模型 uncertainty 声称 history/tool/API/database/system/service 调用失败时
  以 `uncertainty.runtime_claim` 拒绝；可信运行诊断只来自服务端静态码。语义正确性仍须家长核对。
- 批内相同图片字节只传一次，证据保持原照片编号；同家庭同孩子同一上海自然日的待确认/已确认
  提交内，相同文字+图片字节摘要触发重复材料提示并清空自动Todo匹配。摘要保存在草稿JSON的
  服务端元数据，不进模型/日志。无摘要旧记录、重新压缩/裁剪图片不保证识别；新学习事件仍可确认。
- AI可关联候选已有知识ID，服务端校验并统一名称/类别，确认页可取消关联；确认再次检查身份
  与科目/名称/类别。同份记录重复知识只产生一次出现；多次学习仍保留各次发生时间和记录。
- 上传材料中的复习内容必须引用服务端原始提案里的今日计划或工具返回的历史 Knowledge，不能同时
  作为新学习条目。两个来源都必须有本次材料直接证据且只是可编辑候选；家长确认前零正式写入。
  家长确认时，`new` 创建 LearningRecord/KnowledgeOccurrence/必要的 Knowledge/Review；
  `today_review` 与 `history_item` 只写 ReviewFeedback 并更新原 Review 的最近复习日、次数、间隔、热度、
  策略版本、状态版本和下次日期。历史 Review 可以提前推进、从 inactive 重启，或在缺失时重建；这些操作不会清除Knowledge的永久已替代状态，已替代项仍不自动排期。
  已推进、删除或身份事实已变化
  的原始匹配安全跳过，不阻断同一事务里的其余复习和新学习，也不会重复推进。全部匹配均已变化的纯复习
  草稿仍确认成终态并返回空 `records[]` 和 `updated_reviews[]`。客户端注入或篡改的复习引用继续拒绝且
  零写入。
- AI排队、分析中、失败或待确认均可人工确认，人工表单不自动匹配Todo；保存时才取消未完成Job，
  复用同一正式记录事务，来源标记人工录入。Worker成功/失败回写均校验状态、attempt和lease，
  丢弃人工确认、取消或新租约后的迟到结果；不把取消结果复活用于旧任务。
- Review 日期只来自确定性 `curve_heat_v1`：基础间隔1/3/7/14/30/60/90天，叠加有界热度衰减和实际
  间隔修正；同日重复事件不重复推进曲线，历史补录不回退当前投影。`defer` 不更新复习事实。
- `daily_budget_minutes` 不改变到期事实；新 `review_selection` 只以分钟为计划上限。任一 action 改变对应
  计划项状态，刷新不会补出新一批；到期但未入选项第二天自然重新参与选择，不执行批量改期。
- 固定活动提醒的星期、开始和结束时间是设置、日程和今日的同一事实源。
- 设置只固定展示数学、语文、英语；其他学习科目与课外活动必须由家长从目录或自定义名称显式添加。课外活动默认空，取消添加或提醒编辑不产生补偿写入。
- 设置页有在用孩子时不再在主内容重复展示学习档案列表；右上角孩子胶囊在单孩子时也可打开统一
  档案面板。档案行以姓名/年级两级信息为主，“当前使用”并入次级文字；可写成员通过透明 88rpx 铅笔
  点击区编辑，新增使用列表末尾动作行，归档恢复和上限说明保持独立；viewer 只可切换。无在用孩子时
  仍由页面空态提供首次建档和归档恢复路径。服务端档案权限、上限和生命周期合同未改。
- 今日在成功且全部为空时通过上方引导提供记录学习和添加日程入口；普通态由上方主卡提供添加日程。
  课外活动单栏为空时只显示居中空文案，不在下方重复显示添加按钮。日程七天、报表三档、基础科目和活动七星期不依赖横向滚动。
- 报表四个概览指标是只读摘要，不承担跳转；7/30/100 天均由服务端按 `Asia/Shanghai` 当前日窗口返回 7 个连续等时间桶，桶内计数求和且与概览总量守恒。新版完整全零数据画零基线，旧后端缺字段或无效趋势只显示“暂无趋势”。
- 单次照片学习记录支持 1–9 张：空态与已有照片后的“+”共用一个添加入口，每次由微信原生界面
  选择拍摄或相册；拍摄返回后可再次添加，相册可多选，所有轮次共享 9 张上限；全部图片只创建一个 Job。
- 新增记录不再要求选择“拍照/文字”模式：照片和学习内容始终同屏；有照片时沿用照片批次并携带
  可选文字，无照片但有文字时沿用 manual submission；两者皆空时客户端不发请求。历史中的
  照片/文字来源标签与筛选继续表示既有材料事实，不因入口合并而删除。
- 云环境图片使用后端 ticket + `wx.cloud.uploadFile` + uploader metadata claim；不经过
  `callContainer` 请求体或容器持久化磁盘。取消记录会同步尝试删除已 claim 文件；失败清理目前依赖
  当前 Worker 拓扑；相关决策只引用 `ADR-001 / TD-001`。
- 照片批次在创建 Job 前中断时仍可从服务端状态继续分析或取消；待确认草稿也可删除。
- Worker 普通循环异常以 1/2/4/8/16/30 秒退避自动继续，健康轮询后重置；清理故障单独隔离，
  最多每 60 秒尝试一次，不阻塞分析。任务准备/Provider 普通失败沿用最多三次尝试；数据库写回
  故障保留持久化状态，通过新 Session 和原 5 分钟过期租约恢复，避免伪造任务结果。任务领取按
  `available_at, created_at, id` 稳定排序，刚进入 backoff 的旧任务不再仅凭更早创建时间抢占已就绪任务。
- 受支持的云端数据库下限是 MySQL 5.7，单实例 Worker 的分析任务与过期媒体清理使用有界、排序的
  `SELECT ... FOR UPDATE` 事务领取；MySQL 8 才支持的 `SKIP LOCKED` 不进入运行时 SQL。多实例
  非阻塞领取仍是独立拓扑演进，不由当前单实例实现预留不兼容语法。
- Worker attempt 记录媒体查询、对象存储 materialize、上下文构建、Provider 和写回的脱敏阶段边界
  与耗时；Provider 每次 generation 和 history batch 额外记录 turn、状态、结果种类、输出项数、逻辑查询/
  结果累计量、剩余轮次/时间和归一化静态校验码。日志只允许 Job ID、attempt、计数和安全类别，不记录
  儿童内容、科目、关键词、对象路径、模型输入输出或异常原文。Job 内部错误字段只持久化公共错误码、
  静态 reason 和最多20个归一化 validation code；Submission/API 仍只暴露既有家长文案。云端 INFO
  路由与 Ark Key 启动门禁已随 `flask-ik19-008` 灰度部署；真实日志确认
  图片读取、Ark 调用和 proposal 校验成功，但 MySQL 秒级 lease 与内存微秒值比较误判导致写回跳过。
  revision 15 已在 claim 后重载持久化 lease，并将达到最大次数的过期任务终态化；
  `flask-ik19-009` 已达到 `normal`，真实新图片已完成 Ark 与写回并进入待家长确认。

- 2026-09-22 — `BUG-026 / BUG-SPEC-20260922-ANALYSIS-CORRECTION-02`：把 Runner 的历史检索
  completion ledger 作为 final validator 注入 Ark Provider loop；精确名称协议同时写入 Prompt 和工具描述，
  `history_search.incomplete` 在当前 attempt 内得到静态纠错并可补查，不再必然升级为完整 Job retry。
  Worker 改为 ready-time 稳定排序，并只在 Job 内保存有界安全诊断，家长可见文案、API、Schema、正式
  学习确认语义和最多3次 Job attempt 均不变。本地专项65 passed、全量后端366 passed/4 skipped、前端
  170 passed，静态/类型/架构/设计/小程序门禁通过；隔离 MySQL 5.7 空库 migration/current/check 与
  runtime 4 passed，冻结容器 UID 10001、live/ready、SIGTERM 均通过；云端灰度与真实 Ark smoke 仍是
  独立发布门禁。
- 2026-09-25 — `BUG-027 / BUG-SPEC-20260923-EMPTY-PROPOSAL-QUALITY-01`：分离 configured 与 analysis
  subjects，恢复未配置系统预设科目的合法识别；把零 actionable proposal 和模型伪运行时诊断变成
  same-loop 静态纠错，并在 Worker 写回前保留非空终检。新增默认 dry-run、显式 family/Submission ID
  才可 apply 的幂等 legacy empty-pending 修复工具，以及 12语文/12数学/12英语/4多科目的 40-case live
  Ark 门禁（30张合成图片）。本地全量、性能/E2E、前端、静态/架构与隔离 MySQL 5.7 门禁均通过；
  2026-09-25 live gate 完整执行为 38/40、总体 95%、数学/英语 100%，但语文 86.67%（两条样本各 3 次
  Ark timeout）低于单科 90%，因此门禁 FAIL，未发布或执行生产修复。
- 2026-09-26 — `BUG-027 / BUG-SPEC-20260926-EMPTY-PROPOSAL-QUALITY-02`：保持所有失败都进入
  40-case 端到端分母，仅把精确终态 `analysis_failed` 排除出单科语义分母；将分组 fixture 转换为固定
  语文/数学/英语轮转并每三轮插入一个多科目样本。新增 9 项纯调度/聚合合同测试。全新完整 live run
  为 40/40，各科语义均 15/15，operational terminal failure、empty/remaining pending 与 formal writes
  均为 0；运行中的 Provider retry 最终恢复，best-effort session cleanup 仍有告警并保留为残余风险。
- `SPEC-AI-OUTPUT-20260906-01` 的后端已实现并以 `flask-ik19-011` 灰度部署：新 AI 提案使用
  `hanzi/word/poem/arithmetic/concept/activity/other` 受控展示类别；其当时的 AI summary 120 字
  合同已由本地 BUG-017 收紧为上述 60 字正向事实合同，
  Submission read API 从原子知识点确定性派生有序 `display_groups`；旧提案按 category/name 兼容。
  该投影不参与授权、确认或正式知识写入。新列表前端仍受 `DREV-20260906-AI-02` 设计门禁阻塞。
- 启用 Worker 时，尚未启动、异常退避、停止或后台 Task 已结束均使 `/health/ready` 返回
  `503 worker_unavailable`；健康轮询恢复后为 200，正常分析不按耗时判死。明确禁用 Worker
  的开发/测试配置保留原 readiness；`/health/live` 保持进程存活语义。退避可被 stop 唤醒。
- ReviewFeedback 与 CalendarEvent 创建都使用 family-scoped 幂等请求记录，网络重试不双推进或双建。
  `POST /review-feedback-batches` 每批最多120项，先锁定并校验同家庭/孩子、active 且当前到期的全部 Review，
  再全量写入或回滚；`review_feedback_batch_requests` 按 family + idempotency key 保存请求指纹和结果，
  相同请求稳定重放，键复用到不同请求返回409。单项反馈接口保持兼容。
- 活动建议按请求的历史目标日和目标周计算，不使用“当前周”污染历史结果。
- `occurred_at` 与 `created_at` 分开保存；日历显示按 Asia/Shanghai 展开。
- 数据库时间列统一先转 UTC 再保存，读取后带 UTC 时区；历史无时区值遵循既有 UTC 约定。
  学习、活动、历史与任务时间不再因 SQLite/MySQL 丢失时区而让客户端误读当地时间。
- 零照片且无 Job 的草稿明确为等待上传，可在原草稿补传或取消；补传复用原批次 key 和照片
  槽号，失败后不重复占用上传票名额。已 claim 但响应丢失时，以服务端 media_count 恢复。
- 兼容提交接口仍先筛选 queued/analyzing/pending_confirmation/failed，再每页 100 条查询；
  新记录页改用 history 的 20 条游标分页及独立待处理总数，轮询保留当前页；已确认历史不轮询。
- Ark 接收完整已接受文字，不再静默截断到 2000 字；输出逐点校验直接证据、图片索引、
  上下文和 Todo 引用。家长可看到证据、低置信度和不确定项，手动新增知识点仍可确认。
- 已结束 Review 的新反馈返回 409，不再重新激活；同一已成功幂等请求允许回放原结果。

## Current contracts

| Responsibility | Current implementation |
|---|---|
| API composition | `apps/api/src/push_kids/bootstrap/app.py`, `/api/v1`, `/health/live`, `/health/ready` |
| learning profiles/subjects | `children` module; profile creation is backend-only in the product UI |
| submission lifecycle | `learning` module with local multipart or cloud ticket/claim multi-media finalize |
| provider/jobs | `agent_processing`; Ark + test-only deterministic adapter |
| deterministic review | pure curve/heat event policy in `planning/policies.py`; pure minute-budget selection in `planning/selection.py`; materialized plans in planning service |
| schedule/activity | `activities`; CalendarEvent CRUD + ActivitySchedule projection, plus read-only TravelArrangement calendar projection and cross-source conflict metadata |
| dashboard/report | `reporting`; bounded Today snapshot pages and SQL-owned 7/30/100-day aggregates, including exact activity subject totals |
| collection pagination | `platform.pagination`; opaque versioned scope/filter/snapshot cursors, per-page authorization and hard maximums |
| persistence/media | SQLAlchemy + Alembic；MySQL/cloud storage in cloud, SQLite/local media in dev/test |
| native UI | `apps/miniprogram`; callContainer + cloud upload transport, UI-001 DREV-20260830-03 |

## Runtime data state

The local runtime database was reset after archiving all prototype databases under
`data/archive/20260830-pre-native/`. `data/push_kids.db` is schema-only and passes
`tools/audit_database.py --require-empty`. Real profiles are configured explicitly with
`tools/configure_local_profile.py`; the command never creates learning records.

## Verification evidence

| Gate | Result on 2026-08-31 |
|---|---|
| Python unit/integration/contract | 38 passed, 1 optional MySQL test skipped in default suite |
| Isolated MySQL 8 | baseline migration/current/check passed；cloud identity/job/idempotency/confirmation 1 passed |
| Live HTTP E2E | 1 passed; worker, SQLite, history, multi-photo, confirmation, review and reports |
| Mini Program tests | 24 passed |
| Ruff / Mypy | passed; 40 source files typed |
| Container | 2026-09-05 image build passed；UID 10001；internal port 8000；`/health/live` and `/health/ready` passed；graceful stop passed |
| Cloud staging | `flask-ik19-003` normal；managed MySQL at `20260903_0001`；least-privilege runtime account；DB WAN closed；service PUBLIC closed |
| Real callContainer | domainless live/ready 200 after PUBLIC closure；unbound actor returns expected 403 |
| Architecture validator | `ARCHITECTURE_VALID checked=2` |
| Mini Program validator | 7 pages, 5 exact tabs, source package under budget |
| Runtime DB audit | integrity/FK/family checks passed; all business tables empty |
| WeChat DevTools CLI | project opened successfully; real preview/upload not run without registered AppID |
| Live Ark | `NOT_RUN`: no `ARK_API_KEY`; the four supplied Desktop paths no longer exist |

2026-09-05 BUG-005/006 本地增量验证：后端 unit/integration/contract **66 passed, 2 skipped**
（未配置隔离 MySQL）；前端测试 **28 passed**；Mypy、架构校验及小程序校验通过。
本次八个代码/测试文件 Ruff check 通过；全仓 Ruff check/format 在并行新增
`families/domain.py:1` 有 import/空行格式问题。独立只读复审 **PASS**；详细命令和修复前后
证据见对应 Spec。上述历史云端证据不代表本次修复已重新部署或完成云端验收。

BUG-007 后续本地验证：后端 **80 passed, 2 skipped**（隔离 MySQL 未配置），前端 **34 passed**；
Ruff check/format、Mypy（47 source files）、ESLint、架构和小程序校验通过，独立第二轮复审 PASS。
此前并行家庭模块的格式问题在最新全仓检查中已消失。真实 Ark/云上传和受影响页面视口仍未验收。

## Current limitations / release blockers

BUG-010 本地实现已通过微信开发者工具 registered AppID preview 编译，最终预览包 175,099 bytes；
执行时 macOS 锁屏导致 CUA 与三视口原生截图仍未运行，不能据此声称布局完成视觉验收或云端已更新。

- Real Cloud Hosting actor binding, two-account isolation, owner-only object rules, metaid decode and public-ingress
  rejection passed operator-confirmed staging acceptance on 2026-09-06. This is no longer a release blocker.
- Current cloud Worker topology is documented here only as a runtime fact; its decision is referenced as
  `ADR-001 / TD-001`.
- Database credential rotation, least-privilege account and cloud Alembic execution are complete. Backup/restore
  remains a release gate; the previously shared password is revoked and must not be reused.
- Bounded-read migration `20260911_0011` is verified on fresh local MySQL 8.0.45, but production backup,
  index-build lock observation, cloud schema upgrade and staged slow/large-route signals remain mandatory before
  traffic promotion. Leading-wildcard history substring search remains scan-based within the approved 50k-row budget.
- Registered AppID, HTTPS legal domains, privacy declaration, iOS/Android real-device verification and
  preview/upload remain mandatory before an experience or public build.
- 小程序尚未留存最低基础库设置证据，也未对 `callContainer`、`uploadFile`、`chooseMedia` 做能力门禁；
  媒体权限失败、安全错误分类和上传取消恢复按 `BUG-SPEC-20260905-02` 待批准实施。
- Live Doubao image analysis remains unverified until a rotated secret and accessible test images are supplied.
- BUG-005/006 的故障注入及分类回归目前仅在本地隔离环境验证，未重新部署或执行真实云端/MySQL
  故障恢复验收。取消中的 Provider 失败竞争（CR-004）已在BUG-009本地修复；媒体路径清理
  （CR-005）仍属独立问题。
- 当前设计门禁按 `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01` 要求仓库内可编辑 SVG/HTML、视口/状态导出与匹配 SHA-256 审批清单；旧工具 waiver 仅为历史审批记录。
- 三视口、字体放大、键盘和 iOS/Android 实机证据仍待补齐。

## Change references

- 2026-10-16 — [`BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01`](../../../specs/active/BUG-029-REVIEW-SUBJECT-ORDER.md)：恢复反馈后的科目组序，未改SQL/Schema/选题；[证据](../../quality/evidence/REVIEW-SUBJECT-ORDER-20261016.md)及[发布状态](../../deploy/releases/20261016-review-subject-order-backend.md)区分本地与云端。

- 2026-10-06 — `SPEC-20261006-SOURCE-DELETE-02 / DREV-20261006-SOURCE-DELETE-01`：本地实现Today精确原图、
  单知识删除、关联/计划/通知一致性；验证与未完成门禁见 `docs/quality/evidence/SOURCE-DELETE-20261006.md`。

- 2026-10-01 — `SPEC-20261001-VOICE-INPUT-03 / DREV-20261001-RECORD-VOICE-INLINE-03`：记录页
  新增输入框内嵌 WechatSI 语音转文字，单次最多 60 秒；结果只进入既有可编辑 `text` 草稿，不新增
  source、API、表或音频存储。首次授权不自动续录，上滑/离页/切孩子/权限丢失取消，迟到回调按孩子
  上下文丢弃，4000 字超限保留原文。专项 13 passed、全量前端 184 passed、后端 389 passed / 5
  optional skipped，静态包 685412 bytes；真实 AppID preview 650045 bytes 通过、未上传。开发者工具
  授权因目标 AppID 隐私协议未声明麦克风 scope 返回 `errno 112`；iOS/Android 真机仍为 NOT_RUN。

- 2026-09-19 — `BUG-025 / BUG-SPEC-20260919-REVIEW-ONLY-CONFIRM-01`：共享草稿确认映射在没有
  新知识点分组、但存在合法复习匹配时，保留服务端原提案科目，不再把 `proposal.subject_name`
  覆盖为空字符串。后端非空合同、Review 引用复核、事务、科目分组及页面视觉交互均未改变。
  修复前专项 1 个回归断言失败，修复后专项 10 passed、全量前端 170 passed、后端
  362 passed / 4 skipped，静态、类型、架构与设计策略门禁通过；真实 AppID preview PASS，
  小程序 0.1.12 开发版本已上传（603182 bytes / 589.0 KB），未设体验版、未提审、未正式发布。

- 2026-09-19 — `BUG-023 / BUG-SPEC-20260919-REVIEW-SOURCE-01 / DREV-20260919-TODAY-SOURCE-MATERIAL-01`：
  Prompt 将知识名称收紧为可执行学习动作，并要求一句不编造的家长可读原题摘要；Planning 在稳定日
  计划和旧 Todo 兼容投影中读取首次确认 evidence。Today 删除“出现原因”和通用“带练提示”，改为
  知识点级原题提示与当前页原始照片/文字弹层；无新模型调用、数据库迁移、路由或 Review 写入。

- 2026-09-19 — `SPEC-20260919-ARK-CONTEXT-REUSE-01`：新增默认开启、可回退的 Ark attempt-local
  Responses 会话续接，保留 strict Schema、8轮和 Job retry 边界，并提供不输出内容、ID或密钥的真实
  延迟 A/B 工具。协议与回归在本地验证；真实 Ark A/B 和部署待独立门禁。

- 2026-09-19 — `BUG-024 / BUG-SPEC-20260919-MYSQL57-WORKER-01 /
  ARCH-20260919-MYSQL57-WORKER-01`：隔离 MySQL 5.7.44 发布门禁确认 `SKIP LOCKED` 会稳定触发
  SQL 1064；分析任务、过期媒体、通知投递与删除请求改为普通事务行锁领取，保持现有单实例、租约、
  重试、幂等与终态语义。空库迁移/current/check 与 MySQL 专项 4 passed，冻结容器非 root、live/ready、
  SIGTERM 通过；无 Schema、API 或前端变化，云端发布状态见 release 021。

- 2026-09-19 — `BUG-022 / BUG-SPEC-20260919-AGENT-RETRY-02`：修复合法图片分析在 8 轮 Agent loop
  耗尽后于 attempt 1/3 提前终态的问题。历史搜索工具改为每轮批量 1–20 个逻辑查询，保留 8 turns、
  20 calls、100 unique results 边界并把最终轮留给结构化结果；单 attempt 截止时间按5分钟 lease
  剩余量扣除30秒写回余量动态产生，SDK 内部重试关闭。非法 tool 参数不执行查询并在同 loop 修正。新增仅含
  Job/attempt/计数/安全状态码的逐轮日志和显式 failure disposition：输出/引用/预算及临时依赖错误最多
  3 attempts，能力/输入不变量立即终止；SQL 不确定性、lease/迟到结果和家长确认边界不变。无 Schema、
  API、前端或正式数据语义变化；本地自动化证据见已完成 Spec，未部署、未自动重跑生产失败任务。

- 2026-09-12 — `BUG-SPEC-20260912-REVIEW-VISIBILITY-01 / DREV-20260912-TODAY-NEXT-REVIEW-01`：今日页
  “待复习”改为“复习安排”；无今日到期项时自动展开最近一个未来复习日，显示完整知识点、精确项数/分钟，
  有今日到期项时仅以低强调 disclosure 提示下一次安排。Planning 新增 family/child/day/snapshot 绑定的
  最近日只读分页合同，Dashboard 预览 5 项，续页硬上限 20；未来项没有反馈/带练。10k 规模与联合索引、
  混合版本三态、分页去重/迟到响应/失败保留和 44px 热区均有自动化覆盖；独立 R2 复核 PASS。真实
  MySQL 5.7、原生 320/390/430、iOS/Android、上传与部署仍为 release gate，本轮未执行。

- 2026-09-12 — `BUG-SPEC-20260912-STALE-CONFIRM-01 / DREV-20260912-STALE-CONFIRM-01`：确认事务先校验
  客户端 Review 匹配来自服务端原始提案，再跳过确认前已结束、推进、改期、删除或身份变化的项；仍有效项
  恰好推进一次，新学习继续原子入档。共享草稿删除手动“刷新/查看最新”冲突提示，非 consent 的 409 自动
  读取服务端最新状态；仅在 confirmed/cancelled 时进入最新只读详情，否则恢复本地编辑并显示错误。
  后端 297 passed/4 skipped、前端 155 passed，质量、架构、静态与空库检查证据见本页 Last verified；
  Schema/API 响应形状未变，未上传或部署，原生视口/真机仍为 `NOT_RUN`。

- 2026-09-12 — `BUG-SPEC-20260912-MYSQL57-01 / ARCH-20260912-MYSQL57-01`：生产运行的托管数据库确认为腾讯
  CynosDB MySQL `5.7.18-cynos-2.1.14-log`，不支持窗口函数/CTE。Today/Todo/报表读路径的 `OVER()`
  投影改写为等价的“精确 COUNT + 预算前缀（<=121 行）+ 有界明细页”与“分组子查询聚合 + LIMIT 50 明细”，
  在 MySQL 5.7 与本地 SQLite 上均兼容，响应字段、稳定排序、分页、精确总数与必做/可选语义不变。已随后端
  发布上线并在生产 MySQL 5.7 正常服务；`ARC-015` 固化 5.7 能力下限，`TEST-STRATEGY.md` 将隔离 5.7
  受影响路径套件作为后续含 SQL 变更发布的阻断门禁（本次因未配置 `PUSH_KIDS_TEST_MYSQL_URL` 未在本地运行）。

- 2026-09-11 — `BUG-SPEC-20260911-PERF-01 / ARCH-20260911-READ-PERF-01 / FEC-20260911-READ-PERF-01`：
  Todo/dashboard 改为有界快照游标与精确总数，报表改为同范围 SQL 聚合并直接返回活动科目统计，活动记录
  和提交兼容数组增加有界续页，历史/Review/提交/知识/活动增长路径增加复合索引；请求边界新增脱敏的
  慢请求/大响应信号。SQLite 10k/50k 性能、查询预算、游标并发边界与 fresh MySQL 8.0.45 migration/
  `EXPLAIN` 已通过；生产备份、索引锁时长、云端阶段信号和体验版验收仍是发布门禁。

- 2026-09-11 — `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01 / DREV-20260911-SETTINGS-PROFILE-MANAGER-02`：
  学习档案面板改为姓名/年级两级信息，当前状态收为次级文字；块状“编辑”替换为透明 88rpx 铅笔点击区，
  新增入口并入列表。既有切换、编辑、归档恢复、viewer、limit、路由、权限和后端合同不变。验证为
  focused frontend 32 passed、全量 frontend 140 passed，ESLint、架构、小程序静态（630368 bytes）、
  图标幂等与 diff check 通过，真实 AppID preview 575988 bytes。三状态三视口 HTML fixture 已生成；
  PNG 与修改后原生三视口/iOS/Android 为 `NOT_RUN`。未上传/部署；后端 API、Schema 未修改。

- 2026-09-11 — `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01 / DREV-20260911-SETTINGS-PROFILE-MANAGER-01`：
  设置页主内容删除重复学习档案区块，档案切换、编辑、归档恢复、添加和上限说明收敛到右上角面板；
  单孩子可打开，viewer 只可切换，无孩子空态保留，后端权限与生命周期合同不变。验证为 focused frontend
  32 passed、全量 frontend 140 passed，ESLint、架构、小程序静态（629228 bytes）和图标幂等通过，真实
  AppID preview 574991 bytes。三档 HTML fixture 已生成；PNG 与本修订原生三视口/iOS/Android 为
  `NOT_RUN`。未上传/部署；后端 API、Schema 未修改。

- 2026-09-11 — `SPEC-20260911-PRIMARY-NAV-BRAND-01 / DREV-20260911-PRIMARY-NAV-BRAND-01`：
  五个一级 Tab 逐页启用 custom navigation，共享 `components/primary-nav` 根据窗口与右上胶囊尺寸
  居中显示生成嫩芽图标 + “知芽”，平台 API 失败时回退为 20px 状态栏、44px 导航行和保守标题边距；
  尺寸变化时重新测量。内容区 `brand-head/.under-brand` 已删除，today/calendar/reports 的上下文信息
  移入 hero，详情与子流程页仍用原生导航。前端 138 passed，ESLint、架构、小程序静态（629240 bytes）
  与图标幂等通过；五页 320/390/430 近似 PNG 横向溢出 0，真实 AppID preview 574832 bytes，开发者工具
  iPhone 15 Pro Max 记录/设置页标题/胶囊无重叠且调试器 0 errors。完整原生三视口、字体放大及代表性 iOS/Android 真机
  为 `NOT_RUN`；未上传/部署，后端/API/Schema/业务状态未变。

- 2026-09-11 — `SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01 / DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`：
  今日页课外活动为 0 项时只显示“今天没有活动安排”，删除其下方重复的“添加日程”；普通主卡和
  首次引导态保留互斥入口，日程意图与活动数据合同不变。当前工作树前端 138 passed，ESLint、架构、
  小程序静态与图标幂等通过，真实 AppID preview 574832 bytes；三档 HTML fixture 已生成，PNG/原生
  三视口/iOS/Android 为 `NOT_RUN`。未上传/部署；后端 API、Schema 未修改。

- 2026-09-11 — `SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02 / DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02`：
  首张和后续“+”统一调用微信原生媒体选择并同时开放拍摄/相册，解决首张拍摄后只能从相册追加的问题；
  支持连续多轮拍摄、相册多选、剩余额度与 9 张硬上限，取消/失败保留表单，上传中不重复打开。
  验证为前端 135 passed、ESLint、架构、小程序静态校验与图标幂等通过，真实 AppID preview
  573065 bytes；0/1/8/9 图三视口近似 fixture 已生成，原生来源面板、连续拍摄与 iOS/Android
  真机为 `NOT_RUN`。未上传/部署；后端 API、Schema 与既有照片提交流程未修改。

- 2026-09-11 — `SPEC-20260911-RECORD-SIMPLIFICATION-01 / DREV-20260911-RECORD-SIMPLIFICATION-01`：
  记录页删除“新增/历史”和“拍照/文字”切换，统一照片+学习内容表单并按是否含照片自动复用既有
  photo/manual 提交通路；空材料不请求，失败保留表单。历史移到页底默认折叠，viewer 与显式历史
  意图自动展开，既有筛选、分页、详情和来源语义不变。验证为前端 133 passed、ESLint、架构、
  小程序静态校验与图标生成幂等通过，真实 AppID preview 编译 572,709 bytes。320/390/430 近似截图
  已走查；开发者工具模拟器重载超时导致原生矩阵、键盘、字体放大与真机仍为 NOT_RUN；未上传/部署。
  后续用户原生截图发现提交栏与 TabBar/历史入口发生触控遮挡；记录页现用专属偏移避开 TabBar、安全区和
  中央凸起键，并用页面尾部占位保证历史入口能滚动到固定栏上方。全量前端仍为 133 passed，修复后
  preview 572,880 bytes；修复后的原生点击复验为 NOT_RUN，未上传/部署。

- 2026-09-11 — `BUG-017 / BUG-SPEC-20260911-01 / DREV-20260911-AI-SUMMARY-01`：模型生成的
  学习总结收紧为一句、最多 60 字且只描述本次实际内容；缺失科目/任务的排除说明由服务端语义校验
  拒绝，并通过既有脱敏代码有限重试，家长 500 字编辑合同与历史数据保持不变。记录详情删除部署运行时
  不可靠的 window/rank 反馈读取，改为最多 20 个 Review × 每项 `LIMIT 4` 的 family-scoped 稳定查询，
  保持每页 3 条 DTO、复习算法和客户端状态不变。验证：修复前新增摘要反例 5 failed / 正例 1 passed；
  修复后定向 unit/provider 24 passed、SQLite history 6 passed、隔离 MySQL 8 history 1 passed；全量后端
  271 passed / 3 optional skipped，当前工作树前端 132 passed，Ruff/format/Mypy、架构与小程序校验通过。
  默认全量命令受仓库 `.env` 提醒配置与 `tests` 导入路径污染，隔离配置后全绿。未执行真实 Ark、
  修复后云端请求或部署，因此当前线上 500 不得视为已消失。

- 2026-09-06 — `BUG-015 / BUG-SPEC-20260906-21 / DREV-20260906-REPORT-01`：删除报表四张概览卡
  不一致的跨 Tab、页内滚动和空值 Toast 路径，保留科目列表的明确下钻；API additive 增加四项共用的
  `overview_trends`，7/30/100 天都按 7 个连续近等宽时间桶求和，并以 `Asia/Shanghai` 今天作为
  上界。前端拒绝结构、日期或总量不一致的序列，旧服务端降级“暂无趋势”，真实新用户全零显示水平线。
  自动化证据：前端 109 passed、ESLint 通过；定向后端 13 passed；全量 Python 到报表后续旅程前
  212 passed / 2 skipped，唯一 E2E 失败发生在工作区既有 AI 匹配改动且未到达报表断言；ruff
  check/format（225 files）、mypy（68 files）、`ARCHITECTURE_VALID checked=2`、
  `MINIPROGRAM_VALID pages=14 source_bytes=606116`。320/390/430 近似 HTML 已生成，390 已视觉走查；
  微信开发者工具 CLI 本地编译预览成功，包体 545.7 KB（558772 bytes），未上传。报表页原生三视口与
  真机仍为 `NOT_RUN`，本轮未部署。

- 2026-09-06 — 云端验收状态更新：用户确认 `BHV-019` 原生/云端验收与 `BHV-020` 真实双参与者
  owner/metaid 测试通过；测试策略要求的真实双账号 owner 规则、metaid 解码和公网拒绝标记为 PASS。
  该证据只关闭对应 staging 安全测试，不关闭隐私/删除、备份恢复或真机视口门禁；Worker 状态只见
  `ADR-001 / TD-001`。

- 2026-09-06 — `FEAT-007 / SPEC-20260906-TRAVEL-02 / DREV-20260906-TRAVEL-01`：设置新增按孩子维护的
  每周出行安排；出行只进入日程，不进入今日、Todo、报表或活动练习。日程对 CalendarEvent、
  ActivitySchedule 与 TravelArrangement 的明确时段统一采用半开区间检测，并为冲突双方返回结构化
  对象与重叠分钟数。自动化已通过，原生三视口和 iOS/Android 仍为 `NOT_RUN`，本轮未部署。

- 2026-09-06 — `BUG-013 / BUG-SPEC-20260906-16`：多科目照片一次确认后按科目分别入档（迁移
  `20260906_0004` 把 `learning_records.submission_id` 的唯一约束降为普通索引，Alembic head 由
  `20260905_0003` 升至 `20260906_0004`，downgrade 遇到多记录数据会显式报错而不是丢数据）；
  新增确定性科目路由与 `consent_required` 同意闸门；待确认草稿可在记录详情页就地确认；
  活动图标按语义派生；报表指标可点；今日默认折叠复习与学习；云环境照片预览改用签发 HTTPS 地址、
  预览限额提至 120/min。API 全部新增字段可选、旧客户端不变。自动化证据：后端 171 passed / 2 skipped，
  ruff check + format（172 files）、mypy（55 files）、`ARCHITECTURE_VALID checked=2`，前端 78 passed、
  ESLint 通过、`validate_miniprogram.py pages=12 source_bytes=533311`、图标生成器幂等。
  三视口原生几何、真机与真实 Ark 多科目语义准确率仍为 `NOT_RUN`，本轮未部署；历史上已落库的
  合成科目名不做自动回改。

- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01`（FEAT-005）改变了本 Feature 的孩子上下文前提：一个家庭
  可以同时保留多个在用学习档案，孩子选择由小程序共享 `utils/child-context.js` 统一解析并在选中档案
  失效时回落；已归档档案的学习/科目/活动新增返回 409，但看板、报表、历史与原图仍可读。
  开通家庭不再必须创建孩子。孩子档案生命周期的权威现状见
  `docs/domain/features/FEAT-005-multi-child-profiles.md`；Alembic head 升至 `20260906_0005`（FEAT-005 的迁移在 review 合并时重链到 BUG-013 的
  `20260906_0004` 之后）。

- 2026-09-06 — `SPEC-20260906-PKDS-01`：小程序全部页面改为 PKDS-1.0 视觉与交互合同，新增只读
  记录详情页并把"可编辑草稿"与"只读记录"拆成两个路由；后端字段级新增 Todo 溯源、媒体稳定
  排序、知识点识别把握程度与证据、科目自定义标记，使界面上"为什么出现、来自哪张照片、
  这条草稿有多可靠、这个科目是谁加的"都能被解释而不是被猜测。新字段全部可空、历史数据允许
  `null`、界面缺字段时隐藏对应展示而不显示占位，因此对旧数据和旧客户端向后兼容。
  Alembic head 由 `20260905_0002` 升至 `20260905_0003`（含 downgrade 与回填测试）。
  自动化证据：后端 131 passed / 2 skipped，ruff / mypy / architecture check 通过，前端 59 passed、
  ESLint 通过、`validate_miniprogram.py pages=12`。三视口原生几何、字体放大、键盘态与真机
  弱网仍为 `NOT_RUN`，因此仍不满足公开发布门禁，本轮也未部署。

- `SPEC-HISTORY-20260905-01 / DREV-20260905-HISTORY-01`: 历史列表、复用只读详情、原始材料读取、
  复习反馈回看和今日/报表联通。本地后端 119 passed / 2 MySQL skipped；前端 58 passed；
  Ruff/Mypy/ESLint/架构/包体检查通过；DevTools preview 编译通过。原生三视口、云端双账号预览和部署未完成。

- `SPEC-20260831-08`: native five-Tab conversion, real local services, no runtime mock data,
  context-aware Doubao proposal, unified schedule and strict E2E/database validation.
- `DREV-20260830-03`: accepted HTML interaction artifact and source of the native conversion.
- `BUG-002`: developer-owned API URL and unambiguous backend-configured profile copy.
- `BUG-003 / BUG-SPEC-20260905-01`: keep UID 10001 and move the CloudBase/Docker internal port from 80
  to 8000 after the real cloud runtime rejected the privileged bind.
- `CLOUD-SPEC-20260903-03`: WeChat Cloud Hosting callContainer, trusted actor binding, MySQL/Alembic,
  private object-storage ticket/claim and single-instance staging Worker.
- `WX-API-BASELINE-20260905-01 / BUG-SPEC-20260905-02`: current `wx.*` inventory, minimum base-library
  recommendation and proposed compatibility/permission/error/upload recovery hardening; implementation pending approval.
- `BUG-005 / BUG-SPEC-20260905-03`: Worker 循环恢复、清理隔离、任务准备异常保护和执行器 readiness。
- `BUG-006 / BUG-SPEC-20260905-04`: 服务端活动分类边界，以及历史活动 Review 的读写和统计隔离。
- `BUG-007 / BUG-SPEC-20260905-05`: 六项 P2 修复（CR-010–015），上传恢复、UTC 时间、模型证据、
  完整文字、待处理分页和复习终态；前端增量 `DREV-20260905-P2-01`，真机验证仍待完成。
- `BUG-008/009 / BUG-SPEC-20260905-06/07`: AI上下文、重复材料/知识/Todo、保留复习进度、人工兜底
  和迟到结果保护；UI增量 `DREV-20260905-AI-01`。本次仅本地修改，验证与未运行项见BUG-009。
- `BUG-010 / BUG-SPEC-20260905-11 / DREV-20260905-UX-03`: 原生控件几何、设置目录、今日空态、
  拍照对齐、家庭详情、邀请申请及100天30项分页；本地实现与390 CUA完成，其他视口证据待补齐。
- `BUG-011 + BUG-012 / BUG-SPEC-20260905-14`: 安全阶段日志云端 INFO 路由、Worker 生命周期事件、
  Ark Key `SecretStr` 与 cloud+ark 启动门禁；本地回归通过，冻结白名单目录已灰度部署为
  `flask-ik19-008` 并达到 `normal`。尚未用新图片证明对象存储、Ark 与写回全链路成功；本 revision
  没有修改重试、租约、数据或 Worker 架构。
- `BUG-011 / BUG-SPEC-20260906-15`: 修复 MySQL `DATETIME` 精度导致的 lease 假冲突，并阻止过期
  running 任务突破 max_attempts；本地回归通过，灰度版本 `flask-ik19-009` 已达到 `normal`，
  新图片端到端 smoke 已进入待家长确认。
- `2026-09-06 release 010`: 远端前端样式基线与 BUG-011/BUG-012 本地修复已在 commit `72970f3`
  合并并推送；最小白名单后端版本 `flask-ik19-010` 已达到 `normal`。开发者工具五个主 Tab、
  320/390/430 视口和云数据加载通过且 0 console error；真机双账号、前端上传和全量切流仍为门禁。
  证据见[发布记录](../../deploy/releases/20260906-010.md)。
- BUG-010 后续截图回归：目录/星期/日历/FAB与报表切换条已继续修正，最新58项前端测试通过；390视觉与320部分复查。详见[回归证据](../../design/frontend/ui/BUG-010-20260905-layout-followup.md)，整体仍未完成真机矩阵或部署。
