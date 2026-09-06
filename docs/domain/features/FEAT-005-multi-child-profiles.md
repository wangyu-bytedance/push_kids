# FEAT-005 — 一家庭多孩子档案管理与切换

- Feature ID: `FEAT-005`
- Status: `IMPLEMENTED_LOCALLY`
- Current-state revision: `FEAT-STATE-20260906-01-MULTI-CHILD`
- Owner: 产品负责人（用户 王宇）
- Last verified: 2026-09-06
- Authoritative implementation: `apps/api/src/push_kids/children/`、`apps/api/migrations/versions/20260906_0004_child_profile_lifecycle.py`、
  `apps/miniprogram/utils/child-context.js`、`apps/miniprogram/pages/child-edit/`
- Active change Spec: `specs/active/FEAT-005-MULTI-CHILD-PROFILE-MANAGEMENT.md` revision `SPEC-20260906-MULTI-CHILD-01`

> 本文只描述当前事实。多档案管理已在工作区实现并通过本地 SQLite 自动化验证，尚未执行云端迁移、
> 尚未发布小程序，也没有三视口原生视觉证据；因此不能描述为线上可用。

## Purpose and scope

一个家庭常常有两个及以上小学生。此前后端数据模型已经是 `Family 1:N Child`，但产品入口只在开通家庭时
创建一个孩子，之后没有任何新增、编辑或退场路径，所以家长实际只能管理一个孩子。本 Feature 补齐孩子
学习档案的完整生命周期与切换体验，让同一家庭可以并行维护多个孩子的学习记录，并让不再使用的档案能
体面退场而不丢历史。

## Current user/system behavior

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
| 建档可预置初始科目 | implemented locally | `test_creating_a_child_can_seed_the_subjects_the_parent_picked` |
| 家庭开通与建档解耦 | implemented locally | `test_family_can_be_opened_without_a_child_and_get_one_later` |
| 跨家庭隔离 | implemented locally | `test_child_profiles_are_scoped_to_their_own_family` |
| viewer/editor/manager 边界 | implemented locally | `test_role_boundaries_for_profile_management` |
| 归档/恢复审计留痕 | implemented locally（云身份路径） | `test_archive_and_restore_are_recorded_in_the_family_audit_trail` |
| 迁移升级/回滚与存量档案落为在用 | implemented locally | `tests/integration/test_child_profile_lifecycle_migration.py` |
| 前端失效选择回落与档案表单 | implemented locally | `tests/frontend/child-profiles.test.js` |
| 三视口原生视觉验收 | not run | 本环境无微信开发者工具 |
| 云端迁移与发布 | not executed | 见 `docs/deploy/` |
| 跨孩子聚合红点/家庭总览 | not implemented | 明确非目标（Spec Q-001） |
| 按孩子授权 | not implemented | 明确非目标，角色仍是家庭级 |

## Current state machine

```text
（不存在） --create--> active --archive--> archived --restore--> active
active --archive--> archived（幂等，重复归档仍 200）
archived --restore--> active（受上限与在用重名校验约束）
```

没有物理删除态。归档只改变默认可见性与新增写入许可，不改变任何历史行数据。

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

- `children.active BOOLEAN NOT NULL DEFAULT 1` 加索引 `ix_children_active`，由迁移 `20260906_0004` 引入；
  存量行全部落为在用，`downgrade()` 可回滚（只丢归档信息，不丢档案本体）。
- 应用启动时的云 Schema 校验 `Database.expected_cloud_revision` 已同步为 `20260906_0004`；
  本地既有 SQLite 开发库在 `create_schema()` 时自愈补列。
- 所有 child 维度读写继续按 `(family_id, child_id)` 双键校验；跨家庭访问返回 404。
- 读路径使用 `ChildrenService.get_child`（允许归档档案），新增写入统一使用 `require_active_child`。

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
- 实施依据 `SPEC-20260906-MULTI-CHILD-01` 的 Figma waiver（Owner 王宇），公开生产发布前必须补齐
  Figma 节点、审批快照与 320×568 / 390×844 / 430×932 三视口原生节点几何证据，waiver 随即失效。

## Current quality and operations

- `uv run pytest tests/unit tests/integration tests/contract -q`：169 passed, 2 skipped（基线 155 passed, 2 skipped）。
- `npm test`：72 pass（基线 59 pass）。
- `uv run ruff check .`、`uv run ruff format --check .`、`uv run mypy apps/api/src`、`npm run lint:miniapp` 全部通过。
- `uv run python tools/check_architecture.py`：`ARCHITECTURE_VALID checked=2`。
- `uv run python tools/validate_miniprogram.py`：`MINIPROGRAM_VALID pages=13 source_bytes=484544`。
- 发布顺序为「迁移 → 后端 → 小程序」，遵循 `docs/deploy/`；新后端 + 旧小程序可用，旧后端 + 新小程序
  仅归档/恢复不可用。

## Limitations

- 三视口与 Figma 视觉证据缺失，公开生产发布门禁未满足。
- 云端迁移与真机双账号验证未执行。
- 本地 `X-Family-ID` 路径的归档/恢复不留审计痕迹（无成员绑定，不伪造操作人）。
- 红点与首屏摘要仍是「当前孩子」口径，多孩子家长可能漏看另一个孩子的待确认（Spec Q-001）。
- 上限 5 是产品默认值，不可按家庭配置。
- 无孩子档案头像、生日、学校等扩展字段，也无物理删除与数据清理路径。

## Source index

- Active Spec: `specs/active/FEAT-005-MULTI-CHILD-PROFILE-MANAGEMENT.md`
- Behavior catalog: `docs/domain/BEHAVIOR-CATALOG.md`（`BHV-022`、`BHV-023`）
- Current architecture: `docs/architecture/ARCHITECTURE.md`
- UI current state: `docs/design/frontend/ui/UI-015-child-profile.md`
- Related features: `docs/domain/features/FEAT-001-push-kids-mvp.md`、`docs/domain/features/FEAT-002-family-collaboration.md`

## Change References

- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01` 获用户批准并实施：新增 `children.active` 生命周期、
  归档/恢复接口与审计留痕、在用上限与重名规则、初始科目预置、家庭开通与建档解耦，新增小程序
  `pages/child-edit` 与共享 `utils/child-context.js`，并修复设置页无档案空态的死路指引。
  本地自动化全绿；云端迁移、发布与三视口视觉证据仍待补齐。
