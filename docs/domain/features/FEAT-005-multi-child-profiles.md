# FEAT-005 — 一家庭多孩子档案管理与切换

2026-11-06当前交付revision `FEAT-RELEASE-20261106-ARCHIVE-05`：[040/0.1.18](../../deploy/releases/20261106-fullstack-040-client-0.1.18.md)交付已批准归档UI，BUG033 DONE/completed。三视口21组节点/PNG保持，320/390/430原生确认框视觉与实际取消均完成；设备/可访问性/真实归档业务仍按原缺项保留。

2026-10-26开发归档：已交付037后端/0.1.16客户端所覆盖的需求按用户批准规则标记开发DONE，验收缺项独立保留；后续BUG-035和旅行导入精简尚未交付，继续active。当前归档和待验入口见[Spec状态清单](../../../specs/STATUS.md)，依据为[治理Spec](../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。本轮不改产品合同、测试结论、设计或发布阶段。

2026-10-25交付revision CLIENT-0.1.16-UPLOAD-01：已实现客户端随0.1.16开发上传（1178991字节），用户已确认旅行照片双账号隔离；未体验/审核/正式发布。产品、真机和可访问性未完成项仍开放。[发布记录](../../deploy/releases/20261025-latest-client-upload.md)。

2026-10-24运行证据revision LATEST-037-01：生产0025新增共享年级确认列，迁移保留原grade、确认年级为空/revision0；获批CRUD启动检查修复后的037 normal/100%，真实微信孩子/年级候选读取200，用户确认/档案写入尚未验收。客户端已随0.1.16开发上传、未体验或正式发布，档案/归档合同不变，旧035为0%且不能在0025重启。[本轮记录](../../deploy/releases/20261024-latest-backend-test-deployment.md)。

- 2026-11-05本地归档UI增量：用户“批准”明确批准[BUG-033 Spec01](../../../specs/completed/BUG-033-CHILD-ARCHIVE-UI.md)与[DREV01](../../design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)。归档/恢复区域已改为左对齐整行操作和14px短说明，完整影响集中到原生确认框；未完成数量、权限和生命周期接口保持。验证与未覆盖范围见[本轮EVD](../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)，本增量现已由0.1.18上传，设备/可访问性待验。

- 2026-10-18本地增量revision `FEAT-STATE-20261018-FOOTPRINTS-ARCHIVE-01`：足迹页单独提供“查看已归档孩子”，可继续既有批次的核对/确认/删除和预分配槽位上传，不接受新导入/手填。168h仍从原上传成功时算。deleting冻结优先，学习草稿入口不改。相关[Spec04](../../../specs/completed/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)、[验证证据](../../quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md)，仅本地实现，原生验收待补。

- Feature ID: `FEAT-005`
- Status: `CLOUD_DELIVERED / ARCHIVE_UI_0.1.18_UPLOADED / VERIFICATION_PENDING`
- Current-state revision: `FEAT-STATE-20261106-CHILD-ARCHIVE-UI-05`
- Owner: 产品负责人（用户 王宇）
- Last verified: 2026-11-06（0.1.18上传；三视口原生状态及确认框视觉/取消；真实业务、设备和可访问性仍待验）
- Authoritative implementation: `apps/api/src/push_kids/children/`、`apps/api/migrations/versions/20260906_0005_child_profile_lifecycle.py`、
  `apps/miniprogram/utils/child-context.js`、`apps/miniprogram/pages/child-edit/`
- Applied Spec: `specs/completed/FEAT-005-MULTI-CHILD-PROFILE-MANAGEMENT.md` revision `SPEC-20260906-MULTI-CHILD-01`；
  归档写入边界见 `specs/completed/BUG-014-ARCHIVED-CHILD-WRITE-BOUNDARY.md` revision `BUG-SPEC-20260906-17`

> 上述037/0.1.16及039/0.1.17均为历史交付；当前阶段见[040/0.1.18记录](../../deploy/releases/20261106-fullstack-040-client-0.1.18.md)。归档UI已交付，年级/足迹原生证据见各自记录。
> 本地SQLite历史证据不代表完整档案真机/业务验收通过，尚未正式发布。

## Purpose and scope

一个家庭常常有两个及以上小学生。此前后端数据模型已经是 `Family 1:N Child`，但产品入口只在开通家庭时
创建一个孩子，之后没有任何新增、编辑或退场路径，所以家长实际只能管理一个孩子。本 Feature 补齐孩子
学习档案的完整生命周期与切换体验，让同一家庭可以并行维护多个孩子的学习记录，并让不再使用的档案能
体面退场而不丢历史。

## Current user/system behavior

- 2026-10-24增量 `FEAT-STATE-20261024-ANNUAL-GRADE-LOCAL-06`：年级显示/选项扩展至九年级；新建支持级与明确触碰年级后保存建立当前学年确认基准，名字/时长普通保存不确认。人工改级提交意图与版本，冲突保留草稿、读取最新事实并要求重选；旧表单同级可保存、旧改级409。年度建议/共享确认由[FEAT-013](FEAT-013-annual-grade-promotion.md)拥有。归档保留基准，恢复累计建议并安全刷新，归档/确认失效旧在途候选；本轮不改变既有归档写入门禁。见[Spec02](../../../specs/completed/FEAT-013-ANNUAL-GRADE-PROMOTION.md)及[证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)：三尺寸呈现/档案控件与独立review通过，修复后原生端到端/设备验收待补，未发布。

- 每日任务配置与当天完成事实也按当前家庭/孩子隔离；切换后清除旧任务展示与表单，忽略迟到响应。
  归档孩子可读取任务但不得新增、编辑、删除或完成/撤销；该域边界见 `FEAT-010-daily-tasks.md`，SQLite验证已通过，MySQL待补。
- 家庭开通与建档解耦：`POST /families` 的 `child` 变为可选，家长可以先建家庭、之后再建档案；
  旧客户端继续传 `child` 时行为不变。
- 一个家庭同时最多保留 5 个在用档案（`ChildrenService.MAX_ACTIVE_CHILDREN`）；超出返回 409，且不留下半条记录。
- 在用档案之间名字唯一（前后空白归一化）；重名新建或重命名返回 409。已归档档案释放名字，
  同一个称呼可以重新启用；但恢复归档档案时若名字已被占用会返回 409。
- 新建档案可附带 `subject_names` 预置初始学习科目，避免新档案是空科目死态；重复与空白名字被折叠，
  预置三科（语文/数学/英语）不计为自定义科目。
- 档案有 `active` 生命周期：`GET /children` 默认只返回在用档案，`GET /children?include_archived=true`
  返回全部，`ChildView.active` 明确标记状态。
- 归档只停新增、不删历史：已归档档案的学习提交、科目、活动与日程新增返回 409「这个学习档案已归档，
  恢复后才能继续记录」；看板、报表、历史列表、原图预览仍然 200 可读。
- 归档拦的是「开始一件新的事」，不拦「结束一件已经开始的事」（`BUG-SPEC-20260906-17`）：归档前已存在的
  待确认草稿仍可确认并落出正式记录，已存在的复习项仍可反馈，已上传照片仍可补传/继续分析/重试，
  档案资料仍可编辑。这样两个家长一个在确认、一个在归档时，先前编辑的草稿不会变成确认不掉的僵尸数据；
  确认仍然是家长显式动作，复习日期仍由确定性策略产生。
- 小程序在用档案显示整行“归档档案”与“保留全部记录，随时可恢复”；有未完成数量（待确认 + 分析中 + 失败）时另加短提醒“还有 N 条记录待处理，归档后仍可继续完成。”。二次确认集中说明隐藏、不能新增、历史/报表保留、可恢复，并补充未完成确认和复习反馈可继续。数量读不到时不显示数字、不阻塞归档；已归档档案不请求数量，操作行改为“恢复档案”与“重新加入孩子列表，继续记录”。进行中显示“正在归档…/正在恢复…”、移除箭头并沿用重复点击保护；失败保留表单和原错误区（BUG-033，0.1.18已上传）。
- 归档与恢复幂等：重复归档或恢复已在用档案返回 200，不产生重复副作用。
- 归档/恢复是家庭可见范围的变更，只有 manager 可执行（403「只有家庭管理员可以执行此操作」）；
  editor 可以新建与编辑日常档案；viewer 任何写入都是 403。角色仍是家庭级，没有按孩子授权。
- 归档与恢复在云身份路径下写入 `FamilyAuditEvent`（`child.archived` / `child.restored`，`resource_type=child`）；
  本地 `X-Family-ID` 路径没有成员绑定，不伪造操作人，因此不留痕。
- `/api/v1/me` bootstrap 与邀请预览 `child_names` 只列在用档案，受邀家人不会看到已退场的孩子。
- 小程序：今日、日程、记录、报表、设置五个 Tab 通过共享 `utils/child-context.js` 解析当前孩子；
  选中的档案被归档或消失时自动回落到第一个在用档案，全部档案归档后清空选择，不会白屏或 404。
- 小程序：设置页新增「学习档案」区（在用列表、已归档列表与恢复入口、建档空态入口），四个 Tab 的
  「选择孩子」弹层底部新增「添加孩子」；`pages/child-edit` 承担新建、编辑、归档与恢复。
  新建成功后自动切换到新档案；创建失败保留已填内容。

## Current behavior matrix

| Capability | Current status | Evidence |
|---|---|---|
| 多个在用档案并行且数据隔离 | implemented locally | `tests/integration/test_multi_child_profiles.py::test_family_can_hold_several_children_with_separate_data` |
| 在用档案上限 5 | implemented locally | `test_active_child_limit_is_enforced` |
| 在用档案名字唯一、归档释放名字 | implemented locally | `test_duplicate_active_child_name_is_rejected_but_archived_name_is_reusable` |
| 归档停新增、保历史 | implemented locally | `test_archiving_stops_new_writes_but_keeps_history_readable` |
| 归档后仍可完成归档前的草稿确认与复习反馈 | implemented locally | `test_archived_profile_finishes_work_that_started_before_archiving` |
| 归档前提示未完成数量且不阻塞归档 | implemented locally | `tests/frontend/child-profiles.test.js`（数量汇总、看板失败降级、归档档案不请求） |
| 建档可预置初始科目 | implemented locally | `test_creating_a_child_can_seed_the_subjects_the_parent_picked` |
| 家庭开通与建档解耦 | implemented locally | `test_family_can_be_opened_without_a_child_and_get_one_later` |
| 跨家庭隔离 | implemented locally | `test_child_profiles_are_scoped_to_their_own_family` |
| viewer/editor/manager 边界 | implemented locally | `test_role_boundaries_for_profile_management` |
| 归档/恢复审计留痕 | implemented locally（云身份路径） | `test_archive_and_restore_are_recorded_in_the_family_audit_trail` |
| 迁移升级/回滚与存量档案落为在用 | implemented locally | `tests/integration/test_child_profile_lifecycle_migration.py` |
| 前端失效选择回落与档案表单 | implemented locally | `tests/frontend/child-profiles.test.js` |
| 本轮归档UI三视口原生验收 | PARTIAL | 21组节点/PNG及320/390/430确认框视觉/取消已完成；真实业务、设备和可访问性未验，见当前发布报告 |
| 云端迁移与发布 | development delivered | 040 normal/100%、Schema0027、0.1.18开发上传；体验/审核/正式发布独立，见 `docs/deploy/` |
| 跨孩子聚合红点/家庭总览 | not implemented | 明确非目标（Spec Q-001） |
| 按孩子授权 | not implemented | 明确非目标，角色仍是家庭级 |

## Current state machine

```text
（不存在） --create--> active --archive--> archived --restore--> active
active --archive--> archived（幂等，重复归档仍 200）
archived --restore--> active（受上限与在用重名校验约束）
```

没有物理删除态。归档只改变默认可见性与新增写入许可，不改变任何历史行数据，也不冻结归档前
已经开始的草稿、上传与复习项。

## Current contracts

| Endpoint | Change | Notes |
|---|---|---|
| `GET /api/v1/children` | 新增 `include_archived` 查询参数，响应新增 `active` | 默认只返回在用档案 |
| `POST /api/v1/children` | 请求新增可选 `subject_names` | 409 覆盖上限与重名 |
| `PATCH /api/v1/children/{child_id}` | 重命名走在用重名校验 | — |
| `POST /api/v1/children/{child_id}/archive` | 新增，manager only，幂等 | 200 返回 `active:false` |
| `POST /api/v1/children/{child_id}/restore` | 新增，manager only | 超限或重名返回 409 |
| `POST /api/v1/families` | `child` 由必填改为可选 | 旧客户端不受影响 |

契约由 `tests/contract/test_api_contract.py::test_child_profile_lifecycle_is_part_of_the_contract` 锁定。

## Data and permissions

- `children.active BOOLEAN NOT NULL DEFAULT 1` 加索引 `ix_children_active`，由迁移 `20260906_0005` 引入（该迁移在与 BUG-013 一起合并时重链到 `20260906_0004` 之后）；
  存量行全部落为在用，`downgrade()` 可回滚（只丢归档信息，不丢档案本体）。
- 应用启动时的云 Schema 校验 `Database.expected_cloud_revision` 已同步为 `20260906_0005`；
  本地既有 SQLite 开发库在 `create_schema()` 时自愈补列。
- 所有 child 维度读写继续按 `(family_id, child_id)` 双键校验；跨家庭访问返回 404。
- 读路径与「收尾类写入」使用 `ChildrenService.get_child`（允许归档档案），新增意图统一使用
  `require_active_child`；两个方法的 docstring 写明了这条边界，避免后续被顺手改成任一极端。

## Architecture mapping

- `children` 模块是孩子档案生命周期规则的唯一 owner：上限、重名、归档/恢复、初始科目预置与
  `require_active_child` 门禁都在 `children/service.py`。
- `learning`、`activities` 通过 `require_active_child` 复用该门禁，不各自实现归档判断。
- `families/service.py` 通过 `ChildrenService` 创建首个档案并读取在用档案列表，方向是 families → children，
  children 不反向依赖 families，依赖图保持无环（`tools/check_architecture.py` 通过）。
- 归档/恢复留痕直接写共享持久化模型 `FamilyAuditEvent`，避免为一条审计记录制造反向依赖。
- 小程序侧新增共享模块 `utils/child-context.js`（owner：小程序孩子上下文），职责是孩子列表装饰、
  选中解析与回落、全局选中态同步、上限提示；替代此前五个页面各自复制的解析逻辑。

## Frontend UI current-state mapping

- `UI-015-child-profile` 是本 Feature 的当前状态文档（档案管理区与 `pages/child-edit`）。
- `UI-001-parent-miniapp` 的档案切换弹层与设置页受影响：弹层底部新增「添加孩子」入口。
- 实施依据 `SPEC-20260906-MULTI-CHILD-01`；当前设计证据按 `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`
  使用仓库内可编辑 SVG/HTML、视口/状态导出和匹配 SHA-256 审批清单。320×568 / 390×844 / 430×932 三视口原生节点几何证据仍须补齐。

## Current quality and operations

2026-11-05归档UI本地验证为42项定向/349项前端、ESLint/小程序/架构/设计政策通过；三视口21组原生几何PASS，原21组PNG和三视口确认框视觉/取消现已补齐；设备/可访问性与其余Review缺项保持，本增量已随0.1.18上传，详见[本轮EVD](../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)。以下命令结果为2026-09-06历史基线，不抵扣本轮或其他增量。

- `uv run pytest tests/unit tests/integration tests/contract -q`：186 passed, 2 skipped（与 BUG-013 合并并补齐 BUG-014 边界用例后）。
- `npm test`：94 pass。
- `uv run ruff check .`、`uv run ruff format --check .`、`uv run mypy apps/api/src`、`npm run lint:miniapp` 全部通过。
- `uv run python tools/check_architecture.py`：`ARCHITECTURE_VALID checked=2`。
- `uv run python tools/validate_miniprogram.py`：`MINIPROGRAM_VALID pages=13 source_bytes=554513`。
- 发布顺序为「迁移 → 后端 → 小程序」，遵循 `docs/deploy/`；新后端 + 旧小程序可用，旧后端 + 新小程序
  仅归档/恢复不可用。

## Limitations

- 三视口21组节点/PNG与确认框视觉/取消已完成；真实归档业务、设备和可访问性验收待补，正式发布门禁未满足。
- 云端迁移及两端开发交付已完成；本次未重跑真机双账号写入验证，沿用原安全基线并独立记录范围。
- 本地 `X-Family-ID` 路径的归档/恢复不留审计痕迹（无成员绑定，不伪造操作人）。
- 红点与首屏摘要仍是「当前孩子」口径，多孩子家长可能漏看另一个孩子的待确认（Spec Q-001）。
- 上限 5 是产品默认值，不可按家庭配置。
- 归档档案的待确认草稿没有直达入口：家长只能在归档前处理，或恢复档案后处理。
- 归档不取消 `queued/analyzing` 的批次，所以归档后仍可能有一次后台分析完成并进入待确认。
- 无孩子档案头像、生日、学校等扩展字段，也无物理删除与数据清理路径。

## Source index

- Applied Spec: `specs/completed/FEAT-005-MULTI-CHILD-PROFILE-MANAGEMENT.md`
- Behavior catalog: `docs/domain/BEHAVIOR-CATALOG.md`（`BHV-022`、`BHV-023`）
- Current architecture: `docs/architecture/ARCHITECTURE.md`
- UI current state: `docs/design/frontend/ui/UI-015-child-profile.md`
- Related features: `docs/domain/features/FEAT-001-push-kids-mvp.md`、`docs/domain/features/FEAT-002-family-collaboration.md`

## Change References

- 2026-11-05 — [BUG-033 Spec01](../../../specs/completed/BUG-033-CHILD-ARCHIVE-UI.md) / DREV01获批准后本地精简归档/恢复卡和文案，旧危险区样式删除；[验证及差异边界](../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)保留原生截图、设备、独立Review及云交付缺项。

- 2026-10-13 — [DOC-SPEC-20261013-02-01](../../../specs/completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md)：删除失效外部设计工具门禁，统一仓库原生设计证据；实现/发布状态和原生/真机验收要求不变。

- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01` 获用户批准并实施：新增 `children.active` 生命周期、
  归档/恢复接口与审计留痕、在用上限与重名规则、初始科目预置、家庭开通与建档解耦，新增小程序
  `pages/child-edit` 与共享 `utils/child-context.js`，并修复设置页无档案空态的死路指引。
  本地自动化全绿；云端迁移、发布与三视口视觉证据仍待补齐。
- 2026-09-06 — `BUG-SPEC-20260906-17`：把归档后的写入边界显式确定为「拦新增、放收尾」，
  在 `children/service.py`、`learning/service.py`、`planning/service.py` 写明该决定（无行为回退），
  补两条服务端边界断言与三条小程序用例，并在归档前展示未完成记录数量。无迁移、无契约变更。
