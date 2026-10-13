# FEAT-001 — 设置页在学科目风格统一 (Spec Lite)

- Status: DRAFT
- Risk: R1
- Owner: 产品负责人（用户）
- Implementer: Codex
- Reviewer: 用户
- Date: 2026-10-12
- Spec revision: SPEC-20261012-SETTINGS-SUBJECT-LIST-05
- Revision evidence: 用户2026-10-12“还是不好看，可以增加一下 图像嘛”，授权制作插画候选。三块标题区增加同风格纸艺插画，修订05待确认。
- User confirmation: PENDING
- Affected Feature IDs: FEAT-001；FEAT-007出行仅同步卡片/图标底色，不改变行为
- Feature current-state documents: docs/domain/features/FEAT-001-push-kids-mvp.md；docs/domain/features/FEAT-007-travel-arrangements.md（仅视觉记录）
- Feature baseline revision: FEAT-STATE-20261006-REVIEW-MANAGEMENT-03-LOCAL（含后续增量）
- Feature merge owner: Codex

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes — 科目网格改为单列行
- Frontend engineering impact: yes — WXML/WXSS及必要视图映射
- Affected UI IDs: UI-001；UI-017（仅设置主页出行卡片底色）
- UI current-state documents: docs/design/frontend/ui/UI-001-parent-miniapp.md；docs/design/frontend/ui/UI-017-travel-arrangements.md
- Frontend baseline revision: FDB-20260913-04 APPROVED
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected frontend quality dimensions: component/state/responsive/a11y/performance/security/privacy/observability
- Frontend quality budgets/requirements: 三档原生矩形、44px触控、14px正文、无横向溢出、语义token、既有权限和有界数据路径、1.5MiB包预算
- Frontend quality verification plan: npm test；npm run lint:miniapp；小程序/设计/架构验证；三视口原生节点与截图；iOS/Android基本操作
- Approved frontend engineering deviations: none
- Current Design Revision(s): 设置主页面基于DREV-20260906-PKDS-01，档案面板DREV-20260911-SETTINGS-PROFILE-MANAGER-02
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-05/*.svg
- Design source SHA-256: 见Snapshot manifest
- Proposed Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-05
- Required viewport/state exports: 320×568、390×844、430×932 × content/unselected/readonly/pending/long-name/error
- Prototype status: AWAITING_APPROVAL
- Approved Task Spec revision: PENDING
- Approved Design Revision: PENDING
- Design approval evidence: PENDING
- Snapshot manifest path: docs/design/frontend/snapshots/UI-001/DREV-20261012-SETTINGS-SUBJECT-LIST-05/APPROVAL.md
- Permitted implementation deviations: none（原生系统字体/抗锯齿差异除外）
- UI current-state merge owner: Codex
- UI current-state merge evidence: pending
- Frontend visual/a11y/resolution verification: pending
- Frontend engineering verification evidence: pending
- External design dependency: none

## 1. Problem and outcome

科目三列大色块与活动/出行单列行不一致，其他科目又使用单独列表。统一为小图标、名称、次级状态、右侧操作的单列轻分隔行，复用现有设计语言。

## 2. Scope

设置主页在学科目统一单列，三类卡片/图标底色同步柔和渐变；基础三科保留固定展示和开关语义，其他科目保留现有移出条件；目录、学习记录、API、家庭权限、活动和出行编辑不变。其他科目长名称换行。
卡片表面精确复用现有pk-hero：暖白158deg线性纸面 + 右上角rgba(127,166,92,.16)径向晕光 + 右下淡弧线，沿用Hero的--pk-r-2xl（52rpx）圆角、--pk-border边框和--pk-e2阴影。图标/操作使用既有平面色，不新增渐变token。三块标题区右侧增加82×70px纸艺插画，书本嫩芽/运动/书包路线，正文独立在下方。插画装饰、无点击、无图不影响功能。无动画，状态仍由文字表达。
验证后向FEAT-001及UI-001合并列表事实及证据；本轮不发布。

## 3. Impact map

- Entry/caller: 设置Tab → pages/settings/index
- Authoritative path: 现有baseLearning/addedLearning → 科目渲染
- Dependencies/callees: toggleBaseLearning/removeLearning/openCatalog → utils/api → 现有subjects API
- Existing tests: tests/frontend中settings相关用例
- Docs: FEAT-001、UI-001、此Spec及DREV证据

## 4. Required design views

### Link/call graph

```text
设置Tab → settings.load → baseLearning/addedLearning → 统一科目行
科目操作 → toggleBaseLearning/removeLearning → subjects POST/PATCH → load
添加其他科目 → openCatalog → 现有目录半屏
```

### Sequence diagram

N/A：沿用现有请求顺序，没有新增业务时序。

### State machine

```text
在学 ↔ 操作中 ↔ 未加入（基础三科）
其他科目在学 → 确认移出 → 操作中 → 不展示
请求失败 → 保留原状态 + 现有反馈；只读 → 展示状态且无写入口
```

### Architecture diagram

N/A：纯页面呈现，模块、依赖方向与扩展点不变，不新增共享抽象。

### Trade-offs

| 方案 | 收益 | 成本 | 决策 |
|---|---|---|---|
| 科目统一单列行，右侧加入/移出 | 与相邻区域一致、状态清晰、保留当前用例 | 比三列网格占用更多纵向空间 | 推荐 |
| 三个区域都改网格 | 科目改动少 | 活动时间/出行信息不易扫描，范围扩大 | 不采用 |
| 只展示在学科目，基础科目都移入目录 | 主列表最简 | 改变基础三科固定入口与添加习惯 | 不采用 |

## 5. Expected file changes and deletion plan

| File/path | Action | Intended change | Why |
|---|---|---|---|
| apps/miniprogram/pages/settings/index.wxml | modify | 统一科目单列行 | 样式一致 |
| apps/miniprogram/pages/settings/index.wxss | modify | 行几何、长文、操作触控，删除失用网格样式 | 无遗留分叉 |
| apps/miniprogram/pages/settings/index.js | modify if needed | 现有科目图标/显示状态映射；保持请求路径 | 视图数据 |
| apps/miniprogram/assets/settings-*.png | add after approval | 三张本地装饰插画，总计≤120KiB，初始包≤1.5MiB | 改善卡片视觉 |
| tests/frontend/*settings* | modify if needed | 仅有意义的交互/权限回归 | 验证行为不变 |
| FEAT-001、UI-001、设计及Spec | modify/add | 记录验证后事实 | 治理要求 |

Final authoritative path: 现有settings页面。不新增组件或业务路径。

## 6. Acceptance criteria

- AC-001：三类设置使用相同卡片、行图标尺寸、标题、间距及分隔线；科目区无三列大色块。
- AC-002：基础三科加入/移出、其他科目移出条件及确认、目录添加、只读权限不变；忙状态不重复提交，失败可恢复。
- AC-003：三档视口长名称、操作和状态不重叠、不溢出；操作触控≥44px，关键信息不只依赖颜色。
- AC-005：三张插画风格一致，不压住标题/列表/操作，无图仍可用，总资源≤120KiB且包大小符合既有预算；透明背景，不使用远程图片。
- AC-004：三类卡片复用今日顶部pk-hero的暖白纸面与右上径向晕光，文字清晰可辨，右下弧线不遮挡操作；不新增图片或动效依赖。

## 7. Required test points

| Test point | AC | Level/command | Required result |
|---|---|---|---|
| TP-001 | 001/002 | npm test；npm run lint:miniapp | 回归通过 |
| TP-002 | 001/003 | 三档微信原生矩形 + 截图，已选/未选/只读/忙/长文/错误 | 无溢出重叠且触控达标 |
| TP-003 | 002 | iOS/Android加入、移出、取消确认、目录、只读及失败恢复 | 现有合同不变 |
| TP-004 | 001/003 | uv run python tools/validate_miniprogram.py；tools/validate_design_evidence.py --manifest <本清单>；tools/check_architecture.py | 通过 |
| TP-005 | 003 | 图标生成幂等、包大小、bundle隐私检查 | 无新增资源风险 |
| TP-007 | 005 | 三视口原生插画/长文截图、无图恢复、素材alpha及总大小、初始包大小 | 全部达标 |
| TP-006 | 004 | 三档原生渐变/文字对比检查，验证Hero样式复用及活动/出行编辑回归 | 三卡一致且文字可读，交互不变 |

## 8. Plan

1. 用户明确确认Spec + DREV后实施页面改动。
2. 执行测试、原生和设备检查，记录实测结果与未运行原因。
3. 更新当前状态；满足完成门槛后设DONE并迁移specs/completed。

## 9. Verification

旧DREV01的18张SVG与精确视口PNG已导出并通过候选hash验证。DREV02渐变候选验证见下方本轮记录。
- 2026-10-12：DREV02共18张SVG及精确尺寸PNG导出完成；`python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261012-SETTINGS-SUBJECT-LIST-05/APPROVAL.md --allow-pending` PASS；`git diff --check` PASS；390内容渐变候选图已检查。
`uv run`因沙箱无法读取uv缓存未执行，使用系统python3完成同一设计校验；默认批准模式按预期因尚未批准而拒绝。生产实施、自动化回归、原生几何和真机均NOT_RUN，原因：等待具体Spec与DREV批准。

## 10. Completion

尚未实施。生产代码未修改；完成后更新本节与Feature/UI事实，核对范围、测试、无旧样式与无无关Diff，再评估生命周期。
- 本轮修订03：18组SVG/PNG生成完成，候选设计证据校验PASS；390内容图已检查。实施、原生和真机仍NOT_RUN（待批准）。
- 本轮修订04：已查看用户截图；18组候选SVG/PNG导出及--allow-pending清单验证PASS，390内容图已检查；生产与原生/真机NOT_RUN（待批准）。
- 修订05：已读取imagegen技能，用内置工具生成三张透明插画；工作区assets已保存，220px最大边。18组候选SVG/PNG已导出，候选清单SHA校验及git diff --check PASS；390完整页已检查。图片总大小见本轮工具wc输出，≤120KiB。生产代码未修改，原生/真机/初始包验收NOT_RUN（待批准后实施）。
