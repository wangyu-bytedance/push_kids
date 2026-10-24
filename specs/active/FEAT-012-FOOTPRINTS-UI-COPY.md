# FEAT-012 — 足迹界面文案精简（Spec Lite）

- Status: VERIFYING
- Risk: R1，局部可逆的文案和重复说明删除。
- Owner: 产品负责人（用户）；Implementer: Codex；Reviewer: 独立只读评审。
- Date: 2026-10-18
- Spec revision: SPEC-20261018-FOOTPRINTS-UI-COPY-01
- User confirmation: 产品负责人（用户）于2026-10-23在审阅精简候选并选择标题切换方案后要求“完成这个功能的代码编写”；批准本Spec01与DREV02的既定文案清单。入口组合另见SPEC-20261023-RECORD-TYPE-SWITCHER-01。
- Affected Feature IDs: FEAT-012；不修改其他Feature。
- Feature current-state documents: [FEAT-012](../../docs/domain/features/FEAT-012-child-photo-footprints.md)
- Feature baseline revision: FEAT-STATE-20261018-PHOTO-FOOTPRINTS-07
- Feature merge owner: Codex；主功能Spec04仍VERIFYING，不因文案任务完成而转DONE。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes，删除重复说明、压短标签与提示。
- Frontend engineering impact: yes，WXML和前端可见字符串，保留现有处理器及状态。
- Affected UI IDs: UI-018；[current state](../../docs/design/frontend/ui/UI-018-child-photo-footprints.md)，基线UI-STATE-20261018-PHOTO-FOOTPRINTS-06。
- Frontend baseline revision: FDB-20260913-04，APPROVED。
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02，APPROVED。
- Affected frontend quality dimensions: state/form、a11y、native resolution、privacy、AI/data-viz语义。
- Requirements: 44px操作区、14px正文、三视口边界/间距/遮挡、必要授权及删除影响、AI候选/地图示意不能误导。无新增资源或请求，1.5MiB预算及FEC-PERF-READ-001..004不变。
- Quality verification: HTML27态×3导出及主要点击；批准后npm test、小程序静态检查、设计完整性检查、变化页面的三视口原生节点和截图。文案专用镜像测试不新增。
- Approved engineering deviations: none。
- Current Design Revision: DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02（文案增量）；DREV01冻结保留历史。
- Companion entrance Design Revision: DREV-20261023-RECORD-TYPE-SWITCHER-01。
- Editable design source: [HTML](../../docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/index.html)，SHA-256见候选清单。
- Required exports: 320×568、390×844、430×932；27态见[逐态规格](../../docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md)。
- Prototype status: APPROVED。
- Approved Task Spec revision / Approved Design Revision / Approval evidence: SPEC-20261018-FOOTPRINTS-UI-COPY-01 / DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02；2026-10-23用户“完成这个功能的代码编写”，见上方批准记录。
- Snapshot manifest: [APPROVAL.md](../../docs/design/frontend/snapshots/UI-018/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/APPROVAL.md)。
- Permitted implementation deviations: none；本次仅批准文案，主Spec04原有设计/全球地图等差异仍开放。
- UI current-state merge owner: Codex；merge evidence: 2026-10-23应用文案增量，见本轮实现证据及UI-018。
- External design dependency: none。

## 1. Problem and outcome

足迹界面反复解释元数据、坐标转换、时间不补造、三视图同步重算等内部规则，让照片浏览和核对操作被说明挤占。以照片、日期、地点和动作表达任务；必要同意与后果在当前决策处简洁呈现。原“处理细则留在设置”方案已由2026-10-24获批[MINIMAL UI Spec01](FEAT-012-FOOTPRINTS-MINIMAL-UI.md)/DREV01覆盖：细则留在Feature/Spec，设置只留开关与保存，不新建帮助层。

## 2. Scope

仅足迹首页、导入/同意、草稿核对/批量编辑/确认、回放/点亮、详情/删除/设置及对应反馈文案。精确目标见[逐项清单](../../docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/COPY-CHANGES.md)。不增加帮助页、弹窗、业务分支或依赖，不扩展到其他页面。

不改变：权限/归档、家长确认、AI主动同意和按需候选、固定7天、条件24h、未知值、分页、日期/孩子筛选、三视图共享事实、删除重算。照片与AI处理范围不能因删文案而变宽。地图仍诚实标示示意/缺位置。

Feature更新范围：合并文案批准、本地实施及验证事实，替换旧候选状态；不将主功能未验收事实改成已完成。

## 3. Impact map

入口由配套标题切换Spec改为记录Tab内旅行组件，旧pages/footprints深链接保留。本文案路径为共享index.wxml、controller.js、presentation.js、imports.js、photos.js；沿用现有API与处理器。既有tests/frontend/footprints.test.js验证状态/权限/业务路径，文案变更不引入新领域合同。

Behavior Catalog、Architecture、发布记录均检查一致性；本次不改领域行为、架构或发布阶段，按实际事实记录N/A，不更改其合同正文。

## 4. Required design views

Link/call graph：`记录入口 → 足迹页面 → 现有处理器 → 现有API`；只改渲染文字与重复说明节点，无新调用。

Sequence diagram：N/A，交互顺序、请求和确认步骤不变。

State machine：N/A，现有导入/处理/草稿/确认/到期/删除状态及转移不变。

Architecture diagram：N/A，无边界、依赖方向、共享抽象或扩展点变更，沿用ARCH-20261017-CHILD-PHOTO-FOOTPRINTS-03。

| 方案 | 收益 | 代价 | 选择 |
|---|---|---|---|
| 删重复说明，保留决定性信息，细则放现有设置 | 当时降低主流程阅读负担 | 设置仍积累长文 | 历史方案；设置部分已被MINIMAL UI Spec01覆盖 |
| 所有提示一律删除 | 字数最少 | 丢失授权、未知值、到期及示意边界 | 拒绝 |
| 新增帮助折叠或教程 | 可容纳全部说明 | 增加交互与维护，不符合本次目标 | 拒绝 |

## 5. Expected file changes and deletion plan

| 文件 | 操作 | 内容 |
|---|---|---|
| 新DREV目录、UI-018 snapshots | add | 精简候选、文案清单、导出工具及PNG/SHA |
| pages/footprints/index.wxml | modify（批准后） | 删除重复说明节点、压短标题/标签；现有绑定和事件保留 |
| pages/footprints/{index,presentation,imports,photos}.js | modify（批准后，仅命中的可见字符串） | 简化来源/反馈/确认影响文字，无流程变更 |
| FEAT-012、UI-018、Spec/设计索引、验证证据 | modify/add | 区分候选、批准、生产与验证事实 |

不创建平行生产实现；旧DREV01保留冻结。冗余提示直接从原渲染路径删除，不以CSS隐藏。

## 6. Acceptance criteria

AC-001：浏览和核对页不再显示元数据处理、坐标转换、统计重算和操作教学；对象、日期、地点、照片与操作可辨认。

AC-002：未知/失败/AI候选、草稿具体到期日期、实际到访确认、处理同意、删除和放弃后果仍明确；不以删除说明改变既有规则。

AC-003：同一操作链和数据结果保持，三视口控件可达、无遮挡/越界；不隐藏溢出冒充通过。不声称本次设计导出等于原生或发布验收。

## 7. Required test points

| Test point | 验收 | 检查 | 结果要求 |
|---|---|---|---|
| TP-001 | AC-001/002/003 | 新DREV render.py，27态×3及点击流程 | 无JS错误、边界/操作区通过、必要语义保留 |
| TP-002 | AC-002/003 | npm test；validate_miniprogram.py | 状态/权限/确认/到期等既有测试通过 |
| TP-003 | AC-001/002/003 | 批准后变化页三视口原生节点及截图 | 当前源码绑定、读字/换行/按钮可达性通过 |
| TP-004 | AC-001/002 | validate_design_evidence.py --check-current-policy、git diff --check、独立只读复核及文档核对 | 冻结源未变，候选SHA匹配，事实/链接一致 |

## 8. Plan

完成精简候选、导出、逐项变更和具体批准后，在原页面删除对应说明和压短可见字符串，执行所需验证，再合并当前状态和生命周期。

## 9. Verification

| 项目 | 状态 | 说明 |
|---|---|---|
| TP-001 | PASS（设计候选） | 27态×3共81手机图及桌面图，DOM/点击通过；[本轮证据](../../docs/quality/evidence/CHILD-FOOTPRINTS-UI-COPY-20261018.md) |
| TP-002 | PASS | 2026-10-23 npm test 275项、ESLint及小程序静态检查通过，使用本轮源码 |
| TP-003 | PARTIAL（合成布局PASS） | 用户再次解锁后最终29态×320/390/430共87份节点/PNG通过，见[实现证据](../../docs/quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)；源SHA未变，旧72份及中间58份不代验。合成标签用于压力长度，完整27态逐字/设计核对及真机/字体/键盘/读屏仍待补 |
| TP-004 | 见本轮证据 | 冻结源、设计政策、diff、独立代码复核与文档核对按最终源码记录，历史候选结果保留独立范围 |

## 10. Completion

已于2026-10-23按批准清单修改本地生产源码：删除重复说明、简化来源/反馈/确认文字，保留同意、AI候选、到期、家长确认和删除后果。文案源与旧快照保持冻结，配套入口Spec独立管理组件组合。保留active/VERIFYING，恢复条件为补齐完整状态原生、真机及设计差异验收；本任务及主Spec04均不标DONE。无部署、上传、体验、审核或正式发布。

- [x] 范围与不变量明确。
- [x] 本具体Spec及DREV获批（2026-10-23）。
- [x] 本地生产文案实施；自动化回归通过。
- [ ] 完整原生/真机和设计差异验收通过。
- [x] Feature/UI同步当前本地事实；验收未闭环，暂不归档。
