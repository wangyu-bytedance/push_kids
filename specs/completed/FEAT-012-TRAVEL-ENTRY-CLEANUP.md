# FEAT-012 — 旅行日记入口精简（Spec Lite）

- Status: DONE
- Risk: R1（单一 footprints 前端领域内可逆删除，API、数据与权限合同不变）
- Owner: 产品负责人（用户）
- Implementer: TRAE
- Reviewer: TRAE 的独立只读复核阶段；没有第二名 reviewer 签字
- Date: 2026-10-31
- Spec revision: SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01
- Architecture revision: ARCH-20261031-TRAVEL-ENTRY-CLEANUP-01
- User confirmation: APPROVED；用户于2026-10-31在本对话回复“批准”，对应唯一待批的 Spec01 / Architecture01 / DREV01
- Request reference: 2026-10-31 本对话两张截图；仅用于定位，不将含孩子信息的截图复制进仓库
- Affected Feature IDs: FEAT-012；FEAT-001 仅学习手动录入回归
- Feature current-state documents: docs/domain/features/FEAT-012-child-photo-footprints.md
- Feature baseline revision: FEAT-STATE-20261026-PHOTO-FOOTPRINTS-26-DELIVERED-BASE-LOCAL-INCREMENTS
- Feature merge owner: TRAE
- Implementation state: FRONTEND_0.1.17_UPLOADED / DEVELOPMENT_DONE / ACCEPTANCE_PARTIAL / EXPERIENCE_REVIEW_PRODUCTION_NOT_RUN
- Delivery target: 0.1.17开发版本16:15:08上传成功1,191,019字节，168份冻结源绑定；用户本轮确认039照片回看/分页/双账号门禁PASS，版本基准已bump0.1.17，见[上传报告](../../docs/deploy/releases/20261101-client-0.1.17-upload.md)。三尺寸原生/局部动作与健康PASS，设备/可访问性缺项独立保留。
- Source baseline: 0576ac3 加任务开始时已有工作区修改；不得还原既有 footprints 等改动

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes
- Frontend impact reason: 移除三视图下方零草稿时的“查看待整理照片”及时间线空态“手动记录”，收回其占位
- Frontend engineering impact: yes
- Frontend engineering impact reason: 同一领域 WXML 和新建手动到访的无消费者客户端路径删除；共用控制器与既有回归调整
- Affected UI IDs: UI-018；UI-001 内嵌旅行组件回归
- UI current-state documents: docs/design/frontend/ui/UI-018-child-photo-footprints.md；docs/design/frontend/ui/UI-001-parent-miniapp.md
- Frontend baseline revision: FDB-20260913-04（APPROVED）
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02（APPROVED）
- Affected frontend quality dimensions: component/state/form/responsive/a11y/browser/performance/security/privacy/observability
- Frontend quality budgets/requirements: 320×568、390×844、430×932；正文≥14px；普通触控≥44px；主 CTA≥48px；删除占位，不用隐藏溢出消除越界；不增加请求、依赖、日志或持久化状态
- Frontend quality verification plan: TP01..TP06；SVG设计、HTML浏览器与生产原生证据单列；批准后按最终生产源采原生节点、截图和真实点击
- Approved frontend engineering deviations: none；学习手动录入与照片日期/地点人工纠正继续可用
- Current Design Revision(s): DREV-20261025-TRAVEL-IMPORT-02 的入口区；UI-018 其余有效 DREV 保留原范围
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261031-TRAVEL-ENTRY-CLEANUP-01/index.html
- Design source SHA-256: b32248dd6ac059403665f7f640bb8bfd69f8109f77c3687d83e933ccbd48304e（index.html）；22个内联SVG/独立源摘要见snapshot manifest
- Proposed Design Revision: DREV-20261031-TRAVEL-ENTRY-CLEANUP-01
- Required viewport/state exports: empty/drafts/legacy/loading/error/viewer/archived × 三个精确视口，共21张主图；320错误顶部辅助1张，总22张，DPR1
- Prototype status: APPROVED
- Approved Task Spec revision: SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01
- Approved Design Revision: DREV-20261031-TRAVEL-ENTRY-CLEANUP-01
- Design approval evidence: 用户，2026-10-31，本对话最近消息“批准”；批准对象是前述旅行入口精简 Spec01 / Architecture01 / DREV01
- Snapshot manifest path: docs/design/frontend/snapshots/UI-018/DREV-20261031-TRAVEL-ENTRY-CLEANUP-01/APPROVAL.md
- Permitted implementation deviations: none；设计示意不替代微信系统地图/相册本身外观
- UI current-state merge owner: TRAE
- UI current-state merge evidence: Feature/UI/Behavior归并revision07；168源不变，fresh preview1191019、三尺寸双宿主42组原生及本地模式/草稿/取消/学习输入PASS；账号主路径缺项独立保留。
- Frontend visual/a11y/resolution verification: 22张批准设计源/导出不变，320/390/430各两宿主七态42组原生节点/PNG/SHA PASS；本地方法/CUA范围另记，真机/实际键盘/读屏/大字NOT_RUN。
- Frontend engineering verification evidence: docs/quality/evidence/travel-entry-cleanup-20261031/README.md
- External design dependency: none

## Approval record

- Approver: 产品负责人（用户）
- Date: 2026-10-31 Asia/Shanghai
- Message reference: 本对话在旅行入口精简 Spec01 / Architecture01 / DREV01 待批交接摘要后的用户消息“批准”
- Approved scope: SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01 + ARCH-20261031-TRAVEL-ENTRY-CLEANUP-01 + DREV-20261031-TRAVEL-ENTRY-CLEANUP-01
- Authorization: 按本修订实施和本地验证；批准不包含上传、部署、提交、推送或删除业务数据

### 后续本地效果确认与前端上传授权

- Approver/operator: 产品负责人（用户）
- Date: 2026-10-31 Asia/Shanghai
- Message reference: 本对话用户“当前效果OK 上传前端准备发布”
- Local acceptance: PASS_OPERATOR_CONFIRMED_LOCAL_EFFECT；仅确认当前整体本地效果，未声明七态三视口、两宿主全部动作、iOS/Android或可访问性矩阵通过。
- Additional authorization: 上传当前已批准前端并准备后续平台发布；用户随后于本对话明确“后端也已经授权”，补充BUG-035兼容后端部署授权。全量切流、提审、正式发布或业务数据修改继续遵守独立门禁。
- Release preparation: [0.1.17上传准备及阻断证据](../../docs/deploy/releases/20261031-client-upload-preparation.md)；168份前端源与本次已验证清单一致，当前基准仍0.1.16，没有推进版本号。
- Merged current-state revisions: FEAT-STATE-20261031-TRAVEL-ENTRY-CLEANUP-02-RELEASE-PREP / UI-STATE-20261031-TRAVEL-ENTRY-CLEANUP-02-RELEASE-PREP / BHV-20261031-TRAVEL-ENTRY-CLEANUP-02-RELEASE-PREP；仅更新已验证本地确认与上传准备事实，批准Spec01/Architecture01/DREV01的产品范围不变。

## 1. Problem and outcome

截图第一处是 `index.wxml` 三视图控件下的零草稿兜底按钮；第二处是时间线“还没有足迹”下的新建手动到访按钮。当前 DREV02 明确保留它们，本请求是新的可见修订。

目标：旅行日记不再出现这两个常驻入口。无足迹时保留原插画、空态标题和下方唯一“导入照片”主操作；删除按钮后按现有布局自然收高。已有真实待核对照片仍显示“X 张待核对”并能继续处理。这里“删除”指界面入口及其废弃客户端创建路径，不删除照片、草稿或历史到访。

## 2. Scope

- 删除 `canWrite`、零草稿分支中的“查看待整理照片”；有草稿的 `summary.drafts` 数量按钮保留。
- 删除时间线空态的“手动记录”按钮，不在更多、帮助或其他位置重新增加这个创建入口。
- 删除仅由该按钮进入的 `manualEntry`、`manualKey`、新建 `manual` 标志、`POST /footprints/manual` 客户端分支及对应标题/CTA 条件。
- 保留历史 `is_manual` 到访的文本展示、分页、日期必填、纠正和删除；照片日期/地点人工输入继续走既有编辑流程。
- 保留导入、缺日期编辑、核对/确认、实际草稿数量、三视图、家庭/孩子权限、归档和离开/保存保护。
- FEAT-001 学习手动录入与手动 Todo 反馈仍是现有正式路径。

非目标：删除云数据、删除/修改后端 manual API、重绘地图/插画、调整 AI 或保留期、更换导航、发布/上传代码包。

批准并验证后，替换 Feature/UI 当前“人工可无图记录”“手动记录仍在空态”等描述：本地旅行客户端没有新建无图到访入口；服务端兼容 API 与历史记录支持单独保留。Behavior Catalog 的学习手动确认、照片元数据人工纠正与历史 manual 展示不得误删。

## 3. Impact map

- 入口：记录 Tab → 旅行日记内嵌组件；`pages/footprints/index` 独立深链接。
- 权威路径：两种宿主共用 `pages/footprints/index.wxml`、`controller.js`、`photos.js`；直接改现有路径，不加平行组件。
- 依赖：`presentation` 的历史 `is_manual` 展示、`imports`/`openDrafts` 和后端 API 保留。
- 测试：`tests/frontend/footprints.test.js`、`record-types.test.js` 及原学习手动输入测试。
- 当前正文：FEAT-012、BHV-038/039/040（按实际受影响范围）、ARCHITECTURE 的 footprints 描述、UI-018/UI-001、设计索引和 Spec 状态索引。

## 4. Required design views

### Link/call graph

```text
记录 Tab / footprints Page
  → 同一个 footprints WXML + controller
    → summary.drafts > 0 → openDrafts → 原核对/编辑/确认
    → 导入照片 → beginImport → 原相册/导入流程
    → 已有到访 → openVisit → 原查看/纠正/删除
删除：零草稿 openDrafts 兜底按钮；空态 manualEntry → POST manual 创建路径
```

### Sequence diagram

N/A：未更改存活调用的请求顺序、权限、事务或异步恢复；被删除的入口没有替代调用。

### State machine

`summary.drafts = 0`：没有草稿入口；`summary.drafts > 0 && canWrite`：实际数量按钮继续可用。`visits = [] && !loading`：插画与标题；活动且可写时保留导入。只读/归档不出现新建入口。删除仅新建无图到访状态；既有照片 edit/review/confirm 和历史到访的合法转换不变。

### Architecture diagram

N/A：边界、共享抽象、依赖方向和扩展点不变；Architecture01 仅确认上述现有 owner 与删除路径。

### Trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 删除截图两处入口，保留真实草稿数量和导入 | 页面收紧；现有草稿可继续核对 | 旅行页不能新建无图到访；历史数据仍可处理 | 推荐 |
| 把两入口迁至更多菜单 | 保留新建能力 | 新增用户未要求的操作位置，更多菜单复杂化 | 不采用 |
| 连实际草稿数量入口一起移除 | 完全去掉顶部草稿动作 | 已有草稿恢复路径变差，超出零草稿截图指示 | 不采用 |

## 5. Expected file changes and deletion plan

| File/path | Action | Intended change | Why required |
|---|---|---|---|
| apps/miniprogram/pages/footprints/index.wxml | modify | 删除两按钮和创建 manual 专用条件；保留历史 is_manual 呈现 | 可见范围及无空壳 |
| apps/miniprogram/pages/footprints/photos.js | modify | 删除无消费者的新建手动到访函数/键/保存分支，编辑保护沿用 | 删除权威旧路径 |
| apps/miniprogram/pages/footprints/controller.js | modify | 删除新建 manual 默认标志 | 不保留不可达状态 |
| tests/frontend/footprints.test.js | modify if needed | 调整对已删除函数的旧调用；保留真实导入、批量/单张编辑、权限和历史到访回归 | 已有测试与存活合同一致 |
| docs/domain/features/FEAT-012-child-photo-footprints.md；docs/domain/BEHAVIOR-CATALOG.md | modify after verification | 替换客户端新建能力/空态入口正文 | 当前事实闭合 |
| docs/design/frontend/ui/UI-018-child-photo-footprints.md；UI-001-parent-miniapp.md；FRONTEND-DESIGN.md | modify after verification | 当前入口、DREV、验证边界 | 代码/设计一致 |
| docs/architecture/ARCHITECTURE.md | audit; modify only if conflicting | 保留领域及兼容 API；客户端创建路径描述按实际修订 | 不虚构边界变更 |
| specs/README.md；specs/STATUS.md | modify | 新候选索引、状态/数量 | 不遗漏活动任务 |
| 本 Spec、DREV01 源/快照、quality/evidence/travel-entry-cleanup-20261031 | add/update | 审阅对象、精确摘要与实际结果 | 版本化证据 |
| docs/deploy/releases/20261031-travel-entry-cleanup-local.md | add after implementation | 仅本地实现/编译状态，旧0.1.16不覆盖增量 | 发布事实闭合 |

最终权威仍是原 footprints owner。后端 `/footprints/manual` 作为既有兼容合同保留；不是本地新建 UI 的恢复入口。批准快照不改内容；本 DREV 获批时只给其接管的入口区域添加 Superseded by 指针。

## 6. Acceptance criteria

### AC-001 — 删除与收高

任一旅行宿主、任何三视图模式、没有草稿时不显示“查看待整理照片”；空时间线不显示“手动记录”。按钮节点及其占位被删除，没有替代说明或新菜单。插画/标题自然靠近三视图控件，下方导入仍可滚动到达。

### AC-002 — 恢复与已有记录

有实际草稿时数量和核对路径可用；导入取消/失败/重试、单张/批量编辑、所选ID和version、未知日期与确认继续原合同。旧无图到访仍以文字显示，能查看/纠正/删除，不伪造照片或修改数量。

### AC-003 — 权限与学习路径

只读/归档不提供新增导入/手动入口；家庭/孩子切换和在途保护不变。学习手动录入、人工照片日期/地点编辑和手动 Todo 反馈继续可用。

## 7. Required test points

| Test point | Criterion | Level / command | Required result |
|---|---|---|---|
| TP01 | AC-001 | DREV01 7态×3视口SVG主图与320错误顶部辅助图；设计清单 `--allow-pending`，批准后去该参数 | 精确尺寸/SHA、设计声明≥44px/14px、无横向越界、主操作位置可达；SVG、浏览器与原生明确区分 |
| TP02 | AC-001/002/003 | 批准后 `npm test`；先跑已有 footprints/record-types 基线，再删旧路径并重跑 | 存活导入/编辑/权限/历史记录/学习路径通过；不增加逐字镜像删除测试 |
| TP03 | all | `npm run lint:miniapp`；`uv run python tools/validate_miniprogram.py`；`uv run python tools/check_architecture.py`；设计校验 | 仅最终源码结果；全仓既有失败单列，不伪装为通过 |
| TP04 | AC-001/003 | 最终生产源在320/390/430采7态原生节点/截图，记录宿主与源码SHA | 删除节点、边界、触控、主CTA、空态收高、已有草稿与历史manual展示通过 |
| TP05 | AC-002/003 | DevTools实际打开记录→旅行、独立深链接；三视图、草稿恢复、导入取消、学习手动路径 | 原生编译/可操作；真实云写入不是本次删除要求，不用自动确认真实照片充验收 |
| TP06 | all | 当前文档正文、链接、旧批准源SHA与diff边界核对 | 实现/自动化/原生/设备/上传分开记录；旧用户改动保留；Spec位置符合云交付规则 |

纯 UI 删除不制造虚假 Red；使用已有行为基线、可失败渲染验收和原回归。移除客户端创建分支后，重点重跑真实单张/批量保存及未知/正式日期校验；如发现运行时修复需要新行为测试，按 Gate E 记录诚实 Red/Green。

## 8. Plan

1. 完成候选设计导出、摘要及范围自查；取得本 Spec01 / Architecture01 / DREV01 的具体批准。
2. 跑当前既有相关基线；在原 WXML/controller/photos 路径删入口与只属于新建的代码，核对全部消费者和历史 is_manual 支持。
3. 跑 TP02/03，重新编译最终本地源码；执行 TP04/05，受系统权限限制的项记 NOT_RUN 与恢复条件。
4. 按实际 diff 同步 Feature/Behavior/Architecture/UI/Spec/证据/本地交付记录，核对无当前正文冲突。

## 9. Verification

当前验证：2026-11-01official login/auto/fresh preview与upload均PASS、包体1,191,019字节。
TP04 PASS_LOCAL_NATIVE，三尺寸两宿主七态共42组节点/PNG与源SHA；TP05 PASS_LOCAL_SCOPE，
三模式/草稿/两宿主系统相册取消/旅行返回学习setField通过；设备/键盘/读屏/大字仍NOT_RUN。
039真实微信健康/me/visits200；本轮用户“已完成039照片回看与双账号验收”补齐正向focus/前后分页及
双家庭/非owner门禁，记PASS_OPERATOR_CONFIRMED，代理较早NOT_RUN保留原日志。
0.1.17成功上传并bump，开发DONE；Feature/UI/Behavior归并revision08，[上传报告](../../docs/deploy/releases/20261101-client-0.1.17-upload.md)
与[原生矩阵](../../docs/quality/evidence/client-release-20261101/native-matrix-resumed.json)版本分别绑定。

以下为初次实施验证记录；当前补验与PARTIAL结论见本节上方续接段。

| Test point | Result | Notes |
|---|---|---|
| TP01 批准SVG清单 | PASS | 本轮不带allow-pending执行指定manifest与current-policy校验，DESIGN_EVIDENCE_VALID；22张导出保留原设计生成证据，浏览器/交互NOT_RUN |
| TP02 生产行为 | PASS | 修改前相关61项基线通过；最终npm test为349 passed/0 failed/0 skipped，含导入/单张与批量保存/未知和正式日期/历史manual/权限/学习手动路径；仅迁移3处废弃方法测试调用 |
| TP03 生产检查 | PASS | ESLint退出0；MINIPROGRAM_VALID pages=17 source_bytes=1233761；ARCHITECTURE_VALID policies=4 modules=151；已批准设计清单/当前政策通过，绑定本轮最终源码 |
| TP04 最终原生 | NOT_RUN | 本轮CLI初始化无法打开微信工具用户缓存Default/.cli，EPERM；未取得320/390/430的本增量原生节点或截图 |
| TP05 本地启动命令 | FAIL_ENVIRONMENT | 官方CLI open退出255；初始化被沙箱拒绝。没有编译成功、已打开模拟器或真实可操作结论 |
| TP05 真实交互 | PASS_OPERATOR_CONFIRMED_LOCAL_EFFECT / PATH_MATRIX_NOT_RUN | 用户2026-10-31确认“当前效果OK”；代理未执行原生点击，用户没有逐项确认内嵌/独立宿主、三视图、导入取消/草稿恢复/学习手动的完整动作矩阵，不将整体确认扩张到这些逐项结果 |
| TP06 设计提案阶段 | PASS（历史范围） | 批准前362源未变及候选引用检查只证明当时DRAFT/AWAITING_APPROVAL；不追认为实施证据 |
| TP06 实施后当前正文闭合 | PASS | 本任务相对388份实施前源清单仅3生产文件/1测试调用者变化；全部前端仍匹配349项验证对象。另任务后续7份后端变化保留并单列版本，当前DAG151复验通过，不代验其后端行为。18份文档/611链接、旧批准源SHA、Spec状态/目录和残留路径检查无错误，见closure-check.json；Feature/Behavior/UI/测试/Spec/本地交付记录一致，Architecture/API/Schema合同无冲突 |

初次上传准备中的21项局部后端与CLI环境失败保留在[原检查](../../docs/quality/evidence/client-release-20261031/checks.json)；
当前CLI/fresh preview和三尺寸双宿主已补，本地动作与039真实微信健康见[续接报告](../../docs/deploy/releases/20261101-client-upload-attempt.md)。
真实iOS/Android、读屏/大字、键盘和完整体验验收仍缺；本轮用户已确认正向focus/分页与双家庭/非owner。

## 10. Completion and lifecycle

- 本Spec01 / Architecture01 / DREV01于2026-10-31获批，0.1.17成功上传；Status DONE，归档specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md。
- 本修订批准已单独记录，不追认旧DREV的批准为本修订批准。
- 本增量168份冻结源覆盖0.1.17成功上传，按GOV-002开发DONE归档；本地42组原生/动作、云健康和用户正向回看/双账号门禁分别PASS。真机/完整产品验收缺项保持，不等同正式发布。
- 039 normal/100%后端与实际账号Schema已验；未更改Schema、运行配置或生产业务数据。BUG-036与并行BUG-037两份页脚源不在0.1.17，原改动保留。
- 已bump基准0.1.17；无Git提交/推送、体验选择、提审或正式发布。批准设计源/快照不变，下一平台阶段遵守管理员门禁。
