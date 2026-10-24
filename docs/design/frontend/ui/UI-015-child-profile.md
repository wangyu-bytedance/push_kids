# UI-015 — 学习档案管理与切换入口

- 当前年级弹窗增量 `UI-STATE-20261024-ANNUAL-GRADE-05`：[精简Spec01](../../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)与[DREV02](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md)获用户2026-10-24“继续”批准并本地实现，保留孩子名标题、单个年级选择和并排操作，失败/冲突按需显示行内短提示，最新事实不可覆盖。33张批准设计导出冻结，最终327项前端/53项定向、三尺寸51组原生及实际选级/重试/稍后通过；真实设备/可访问性及全业务原生端到端边界见[实施证据](../../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)。档案编辑表单仍用DREV01，归档区候选未实施。

- 待批准候选（非当前实现）：用户2026-10-24截图指出档案状态区UI/文字堆砌；[BUG-033 Spec01](../../../../specs/active/BUG-033-CHILD-ARCHIVE-UI.md)及[DREV-20261024-CHILD-ARCHIVE-01](../prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)提议整行操作、短说明、详细影响集中到原确认框。21张合成三视口导出已生成，待具体批准；下面的已实现行为暂不被提案替换。

- Status: `CURRENT_LOCAL / MATRIX_PENDING / HISTORICAL_DESIGN_EVIDENCE`
- Related Feature: `FEAT-005` / `FEAT-013`
- Related Spec: `SPEC-20260906-MULTI-CHILD-01` / `SPEC-20261024-ANNUAL-GRADE-PROMOTION-02` / `SPEC-20261024-GRADE-DIALOG-SIMPLIFICATION-01`
- Current annual-grade baseline / engineering: `FDB-20260913-04` / `FEC-20261007-NATIVE-GEOMETRY-02`
- Current annual-grade design: 弹窗`DREV-20261024-ANNUAL-GRADE-PROMOTION-02`；档案表单`DREV-20261024-ANNUAL-GRADE-PROMOTION-01`（均APPROVED / LOCAL / 验收缺口见本轮证据）
- Historical baseline: `FDB-20260906-02`（PKDS-1.0）
- Historical engineering contract: `FEC-20260906-04`
- Historical design revision: `DREV-20260906-CHILD-02`（DRAFT，视觉沿用 `DREV-20260906-PKDS-01` 既有 token 与组件类；
  增量仅为归档危险区的未完成提醒条）
- Last reviewed artifact date: 2026-10-24
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
| 编辑（在用，manager） | 名字/年级/时长 + 「档案状态」卡的归档危险区；有未完成记录时危险区内多一条 `pk-notice quiet` 提醒（含数量） |
| 编辑（已归档，manager） | 顶部归档说明提示 + 「恢复这个档案」 |
| 编辑（editor） | 只有资料表单，无「档案状态」卡 |
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
- 归档前把未完成数量（待确认 + 分析中 + 失败）摆给家长：危险区提醒与二次确认弹窗都写明
  「归档不会丢掉它们，确认和复习反馈仍然可以完成，但归档后档案不在切换列表里，建议先处理完再归档」
  （`BUG-SPEC-20260906-17`）。这是提醒不是闸门：家长仍可直接归档；数量读不到时退回通用文案，
  绝不编造数字，也不把编辑页变成错误页；已归档档案不发这个请求。
- 归档档案的顶部说明补一句「归档前留下的待确认草稿和复习反馈也仍能完成」，与服务端边界一致。
- 选中的档案被归档或消失时，各 Tab 自动回落到第一个在用档案；全部归档后清空选择并回到空态，
  不出现白屏或 404。
- 设置页请求带代际标记（race guard），快速切换或重复刷新时丢弃迟到响应，不展示上一个孩子的数据。
- 保存与归档进行中按钮进入 `is-disabled` 并展示「正在保存…/处理中…」，避免重复提交。

## Visual and responsive contract

沿用 PKDS-1.0：`pk-card`、`pk-field`、`pk-input`、`pk-picker`、`pk-notice`、`rowlist/rowitem`、
`btn`、`link-btn`、`add-entry`、`pill`、`sk`。不新增配色、字号、圆角或图像依赖；`add-entry` 由
设置页局部样式提升为 `styles/atoms.wxss` 中的全局原子，供四个弹层与设置页复用。评审矩阵为
320×568、390×844、430×932；正文不小于 14px，主要触控目标不小于 44px；「当前 / 已归档」状态
同时用文字标签表达，不只依赖颜色。图标均带 `aria-role` / `aria-label`。

## Approval status

DREV02与精简Spec01于2026-10-24获用户“继续”批准，当前实现和验收边界见页首。下面为DREV01初版及历史档案事实：其中旧弹窗的全宽纵向按钮由DREV02并排操作替代；其余领域规则与档案字段保持。

2026-10-24 FEAT-013复核revision `UI-STATE-20261024-ANNUAL-GRADE-03`：[Spec02](../../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md)、Architecture02、[DREV01设计合同](../prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/FRONTEND-SPEC.md)及[19态三视口/SHA清单](../snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/APPROVAL.md)已获用户“好的 按照这个方案落地”批准并本地实现。采用有效FDB-20260913-04/FEC-20261007-NATIVE-GEOMETRY-02；原设计源/57张导出冻结，不追认头部历史快照。三尺寸各17态原生节点/截图、系统picker打开/取消及九年级编辑字段已采集；按钮铺满内容列，320档案保存补足44px。随后恢复/冲突/在途修复通过自动化与独立评审；[本轮证据](../../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)明确原生端到端、真实设备与可访问性待验收，状态VERIFYING，未发布。下列94项为2026-09-06历史证据，不冒充当前diff结果。

`SPEC-20260906-MULTI-CHILD-01` 与 `BUG-SPEC-20260906-17` 已在本地实现。自动化证据：`npm test` 94 pass
（其中 `tests/frontend/child-profiles.test.js` 16 例覆盖回落、上限、只读成员、创建/归档/恢复流程、
迟到响应丢弃，以及归档前未完成提醒的数量汇总、看板失败降级与归档档案不请求）、`npm run lint:miniapp`
通过、`MINIPROGRAM_VALID pages=13 source_bytes=554513`。
待补齐：repository-native 审批快照、三视口原生节点几何、真机与双账号验证。

## Change references

- 2026-10-24 — `GRADE-DIALOG-SIMPLIFICATION Spec01 / DREV02`：原共享组件收敛为单标题/选择与并排操作，删除说明段落及错误卡；327/53项及三尺寸51组、实际局部交互通过，真实设备/可访问性状态见本轮实施证据，未发布。
- 2026-10-24 — `Spec02 / Architecture02 / DREV01`：独立学年核对、一至九年级、明确意图/version及冲突保留草稿；本地自动化与独立评审通过，三尺寸呈现已采集，原生端到端/设备验收未完成，见本轮证据。
- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01 / DREV-20260906-CHILD-01`：新增 `pages/child-edit` 与设置页
  「学习档案」区，四个选择孩子弹层新增「添加孩子」，修复无档案空态死路；新增共享
  `utils/child-context.js` 统一孩子装饰、选中解析与失效回落，并为设置页补齐请求代际保护。
  三视口证据为 `NOT_RUN`；旧外部工具 waiver 仅保留为当时历史。
- 2026-09-06 — `BUG-SPEC-20260906-17 / DREV-20260906-CHILD-02`：归档危险区新增未完成记录提醒条，
  归档二次确认弹窗与归档说明补齐「收尾仍可完成」的事实；仅一条几何样式（长句提醒左对齐），
  无新配色、字号、圆角或图标。三视口证据仍为 `NOT_RUN`。
