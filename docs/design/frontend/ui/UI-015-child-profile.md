# UI-015 — 学习档案管理与切换入口

当前本地呈现revision `UI-STATE-20261106-THEMES-01`：[DESIGN-002 Spec08 / Architecture01](../../../../specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)与DREV08已获用户“好的 按照以上方案落地”批准并实施，DREV06视觉方向保持。档案字段、复习预算、归档/恢复和年级确认保留；child-edit及隔离grade-confirmation组件显式接入六主题，年级建议/共享确认合同不变。 本增量尚未上传；原生合成呈现、共享业务回归及真机/独立评审缺项见[当前证据](../../../quality/evidence/themes-20261106/README.md)。下方原特性发布与验收记录保持其版本范围，不能代验六主题。

2026-11-06归档UI交付revision `UI-RELEASE-20261106-ARCHIVE-07`：[当前交付](../../../deploy/releases/20261106-fullstack-040-client-0.1.18.md)绑定相同child-edit源，三视口21组节点/PNG及320/390/430确认框视觉/取消已完成。DREV01及生命周期不变，0.1.18已上传，BUG033 DONE/completed；设备/可访问性及真实业务待验。

2026-10-26开发归档：已交付037后端/0.1.16客户端所覆盖的需求按用户批准规则标记开发DONE，验收缺项独立保留；后续BUG-035和旅行导入精简尚未交付，继续active。当前归档和待验入口见[Spec状态清单](../../../../specs/STATUS.md)，依据为[治理Spec](../../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。本轮不改产品合同、测试结论、设计或发布阶段。

2026-10-25交付revision UI-DELIVERY-0.1.16-01：当前实现随0.1.16开发上传，未设体验版、未提审/正式发布；批准设计源/快照及验收缺口保持原范围。[发布记录](../../../deploy/releases/20261025-latest-client-upload.md)。

2026-10-24运行证据revision LATEST-037-01：年级Schema0025保留旧年级，CRUD启动检查修复已批准并验证；037 normal/100%，真实微信年级候选GET200，用户确认写入尚未验收。客户端已随0.1.16开发上传，未体验或正式发布；本页呈现/归档合同和批准设计不变。[本轮记录](../../../deploy/releases/20261024-latest-backend-test-deployment.md)。

- 当前年级弹窗增量 `UI-STATE-20261024-ANNUAL-GRADE-05`：[精简Spec01](../../../../specs/completed/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)与[DREV02](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md)获用户2026-10-24“继续”批准并本地实现，保留孩子名标题、单个年级选择和并排操作，失败/冲突按需显示行内短提示，最新事实不可覆盖。33张批准设计导出冻结，最终327项前端/53项定向、三尺寸51组原生及实际选级/重试/稍后通过；真实设备/可访问性及全业务原生端到端边界见[实施证据](../../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)。档案字段仍用年级DREV01；归档卡由下述BUG-033局部替代。

- 当前归档增量 `UI-STATE-20261106-CHILD-ARCHIVE-07`：用户2026-11-05“批准”明确批准[BUG-033 Spec01](../../../../specs/completed/BUG-033-CHILD-ARCHIVE-UI.md)及[DREV-20261024-CHILD-ARCHIVE-01](../prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)。已本地实现左对齐整行归档/恢复、短说明及集中确认文案，删除泛标题、长段落、垃圾桶和常驻危险色。批准源/21张HTML导出冻结；[本轮EVD](../../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)分别记录生产回归、原生和未验证项，本增量已由0.1.18上传，验收缺项独立保留。

- Status: `CLOUD_DELIVERED / ARCHIVE_UI_0.1.18_UPLOADED / VERIFICATION_PENDING`
- Related Feature: `FEAT-005` / `FEAT-013`
- Related Spec: `SPEC-20260906-MULTI-CHILD-01` / `SPEC-20261024-ANNUAL-GRADE-PROMOTION-02` / `SPEC-20261024-GRADE-DIALOG-SIMPLIFICATION-01` / `BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01`
- Current annual-grade baseline / engineering: `FDB-20260913-04` / `FEC-20261007-NATIVE-GEOMETRY-02`
- Current annual-grade design: 弹窗`DREV-20261024-ANNUAL-GRADE-PROMOTION-02`；档案表单`DREV-20261024-ANNUAL-GRADE-PROMOTION-01`（均APPROVED / LOCAL / 验收缺口见本轮证据）
- Historical baseline: `FDB-20260906-02`（PKDS-1.0）
- Historical engineering contract: `FEC-20260906-04`
- Historical design revision: `DREV-20260906-CHILD-02`（DRAFT，视觉沿用 `DREV-20260906-PKDS-01` 既有 token 与组件类；
  增量仅为归档危险区的未完成提醒条）
- Last reviewed artifact date: 2026-11-06（0.1.18交付、三视口原生状态及确认框视觉/取消；设备/业务验收独立）
- Current archive design/manifest: [DREV-20261024-CHILD-ARCHIVE-01](../prototypes/DREV-20261024-CHILD-ARCHIVE-01/index.html) / [APPROVED](../snapshots/UI-015/DREV-20261024-CHILD-ARCHIVE-01/APPROVAL.md)，仅替代归档卡，年级设计其他范围继续有效。
- Interactive artifact: [DREV02弹窗](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/index.html) / [DREV01档案表单](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/index.html)
- Snapshot manifest: [DREV02 APPROVED](../snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md) / [DREV01 APPROVED](../snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/APPROVAL.md)；2026-09-06基础档案快照仍为历史pending
- Editable design source: 上述两个HTML按各自范围冻结，不用DREV01旧弹窗抵扣DREV02验收。
- Design evidence governance: `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`；旧 waiver 仅为历史批准记录

> 本文描述已在工作区实现并通过 `npm test` / `npm run lint:miniapp` / `tools/validate_miniprogram.py` 的当前状态。
> DREV01三视口呈现/档案字段已在解锁后采集；DREV02弹窗已按新布局单独完成三尺寸呈现和局部交互验收。当前原生、真实设备、可访问性状态以本轮证据为准，不再沿用早期“未采集/锁屏”结论。

## Information architecture

2026-10-24增量 `UI-STATE-20261024-ANNUAL-GRADE-03`：年级显示小/中/大班及一至九年级；原canonical值兼容存储，未知旧值保留。child-edit仅在家长触碰年级picker后提交明确确认意图/version，名字/时长普通保存不确认。冲突保留草稿，在既有错误区域显示只读刷新的最新正式年级，要求重新选择；未重选时保存只重读，失败读取不能绕过。年度待确认由五Tab独立弹窗处理，直接改级或保持原级，稍后本会话不重弹；后台正式年级只在家长确认时更新。恢复安全刷新，归档/确认失效旧在途候选。既有人工入口、归档恢复和危险区保留，不加常驻年度规则说明。

- 入口一：设置页新增「学习档案」区，列出在用档案（标记「当前」）与已归档档案（标记「已归档」），
  底部是「添加孩子」；达到上限时该入口替换为上限说明文案。
- 入口二：今日、日程、报表、设置四个页面的「选择孩子」弹层底部新增「添加孩子」。
- 入口三：无档案空态提供「建立学习档案」主按钮，与「家庭与成员」并列。此前空态只指向「家庭与成员」，
  而该页面无法建档，是死路；现已修复。
- 目标页：`pages/child-edit`（导航标题「学习档案」），同一页面承担新建、编辑、归档与恢复。

```text
设置 / 学习档案 ─┬─ 在用档案行 → child-edit（编辑 / 归档）
                 ├─ 已归档档案行 → child-edit（恢复）
                 └─ 添加孩子 → child-edit（新建）
今日 / 日程 / 报表 / 设置 选择孩子弹层 └─ 添加孩子 → child-edit（新建）
```

## Review states

| State | Visible contract |
|---|---|
| 新建 | 名字、年级、每天复习时长、「已经在学的科目」多选（语文/数学/英语）、主按钮「建立档案」 |
| 编辑（在用，manager） | 名字/年级/时长 + 整行「归档档案」及「保留全部记录，随时可恢复」；有未完成时另加左对齐数量短提醒 |
| 编辑（已归档，manager） | 原顶部归档说明 + 整行「恢复档案」及「重新加入孩子列表，继续记录」 |
| 编辑（editor） | 只有资料表单，无归档/恢复操作卡 |
| 只读成员（viewer） | 设置页不展示建档与添加入口；页面级也不进入表单 |
| 达到上限 | 新建页顶部提示上限文案；设置页隐藏「添加孩子」并显示上限说明 |
| loading | 表单区骨架屏 `card-sk` |
| error | 页内 `pk-notice err`，不使用只在 Toast 里出现的关键错误 |
| 年度年级确认（DREV02） | 孩子名标题、一个原生picker、并排“稍后 / 确认”；失败为行内短提示，保存禁用，最新态正式级＋继续 |

## Interaction and safety contract

- 名字是切换列表的识别依据：同时在用的档案不能重名，帮助文案在输入框下明确说明；
  服务端 409 文案回显在页内错误区。
- 空名字不发请求；创建失败保留已填内容与已选科目，家长不必重填。
- 创建成功后自动把全局选中孩子切换为新档案并返回上一页，避免「建完却看不到」。
- 归档与恢复是改变全家可见范围的操作：仅 manager 可见入口，归档需二次确认，
  文案明确说明「不会删除任何记录，报表和历史仍可查看」；服务端拒绝时展示错误而不静默。
- 归档前把未完成数量（待确认 + 分析中 + 失败）摆给家长：卡片只显示“还有 N 条记录待处理，归档后仍可继续完成。”；原生二次确认集中说明隐藏/停止新增/保留/恢复，并补充“归档后仍可完成确认和复习反馈”（BUG-033；领域边界仍为`BUG-SPEC-20260906-17`）。这是提醒不是闸门：家长仍可直接归档；数量读不到时退回通用文案，
  绝不编造数字，也不把编辑页变成错误页；已归档档案不发这个请求。
- 归档档案的顶部说明补一句「归档前留下的待确认草稿和复习反馈也仍能完成」，与服务端边界一致。
- 选中的档案被归档或消失时，各 Tab 自动回落到第一个在用档案；全部归档后清空选择并回到空态，
  不出现白屏或 404。
- 设置页请求带代际标记（race guard），快速切换或重复刷新时丢弃迟到响应，不展示上一个孩子的数据。
- 保存仍沿用`is-disabled`和“正在保存…”；归档/恢复整行沿用`working`保护及`aria-disabled`，显示“正在归档…/正在恢复…”并移除箭头，避免重复提交。

## Visual and responsive contract

沿用 PKDS-1.0：`pk-card`、`pk-field`、`pk-input`、`pk-picker`、`pk-notice`、`rowlist/rowitem`、
`btn`、`link-btn`、`add-entry`、`pill`、`sk`。不新增配色、字号、圆角或图像依赖；`add-entry` 由
设置页局部样式提升为 `styles/atoms.wxss` 中的全局原子，供四个弹层与设置页复用。评审矩阵为
320×568、390×844、430×932；正文不小于 14px，主要触控目标不小于 44px；「当前 / 已归档」状态
同时用文字标签表达，不只依赖颜色。图标均带 `aria-role` / `aria-label`。

## Approval status

DREV02与精简Spec01于2026-10-24获用户“继续”批准，当前实现和验收边界见页首。下面为DREV01初版及历史档案事实：其中旧弹窗的全宽纵向按钮由DREV02并排操作替代；其余领域规则与档案字段保持。

2026-10-24 FEAT-013复核revision `UI-STATE-20261024-ANNUAL-GRADE-03`：[Spec02](../../../../specs/completed/FEAT-013-ANNUAL-GRADE-PROMOTION.md)、Architecture02、[DREV01设计合同](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/FRONTEND-SPEC.md)及[19态三视口/SHA清单](../snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/APPROVAL.md)已获用户“好的 按照这个方案落地”批准并本地实现。采用有效FDB-20260913-04/FEC-20261007-NATIVE-GEOMETRY-02；原设计源/57张导出冻结，不追认头部历史快照。三尺寸各17态原生节点/截图、系统picker打开/取消及九年级编辑字段已采集；按钮铺满内容列，320档案保存补足44px。随后恢复/冲突/在途修复通过自动化与独立评审；[本轮证据](../../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)明确原生端到端、真实设备与可访问性待验收，开发状态DONE、验收待补，已随037/0.1.16交付，未体验/审核/正式发布。下列94项为2026-09-06历史证据，不冒充当前diff结果。

`SPEC-20260906-MULTI-CHILD-01` 与 `BUG-SPEC-20260906-17` 已在本地实现。自动化证据：`npm test` 94 pass
（其中 `tests/frontend/child-profiles.test.js` 16 例覆盖回落、上限、只读成员、创建/归档/恢复流程、
迟到响应丢弃，以及归档前未完成提醒的数量汇总、看板失败降级与归档档案不请求）、`npm run lint:miniapp`
通过、`MINIPROGRAM_VALID pages=13 source_bytes=554513`。
待补齐：repository-native 审批快照、三视口原生节点几何、真机与双账号验证。

## Change references

- 2026-11-05 — BUG-033 Spec01 / DREV-20261024-CHILD-ARCHIVE-01获“批准”后本地实现归档/恢复整行与短文案；42定向/349前端/21组原生几何通过，原生截图、确认框、设备与独立Review待补，未上传，见本轮EVD。

- 2026-10-24 — `GRADE-DIALOG-SIMPLIFICATION Spec01 / DREV02`：原共享组件收敛为单标题/选择与并排操作，删除说明段落及错误卡；327/53项及三尺寸51组、实际局部交互通过，真实设备/可访问性状态见本轮实施证据，未发布。
- 2026-10-24 — `Spec02 / Architecture02 / DREV01`：独立学年核对、一至九年级、明确意图/version及冲突保留草稿；本地自动化与独立评审通过，三尺寸呈现已采集，原生端到端/设备验收未完成，见本轮证据。
- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01 / DREV-20260906-CHILD-01`：新增 `pages/child-edit` 与设置页
  「学习档案」区，四个选择孩子弹层新增「添加孩子」，修复无档案空态死路；新增共享
  `utils/child-context.js` 统一孩子装饰、选中解析与失效回落，并为设置页补齐请求代际保护。
  三视口证据为 `NOT_RUN`；旧外部工具 waiver 仅保留为当时历史。
- 2026-09-06 — `BUG-SPEC-20260906-17 / DREV-20260906-CHILD-02`：归档危险区新增未完成记录提醒条，
  归档二次确认弹窗与归档说明补齐「收尾仍可完成」的事实；仅一条几何样式（长句提醒左对齐），
  无新配色、字号、圆角或图标。三视口证据仍为 `NOT_RUN`。
