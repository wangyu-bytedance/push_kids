# FEAT-006 — 家庭资料清理与重新开始

- Feature ID: `FEAT-006`
- Status: `PLANNED / NOT_IMPLEMENTED`
- Current-state revision: `FEAT-STATE-20260906-01-PLANNED`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-06
- Authoritative implementation: `N/A — production implementation has not started`
- Active change Spec: `specs/active/FEAT-006-DATA-CLEANUP-AND-FAMILY-RESET.md` revision `SPEC-20260906-DATA-CLEANUP-01`

> 本文是新 Feature 的计划入口，不把目标行为描述成当前可用。当前产品只有孩子档案归档/恢复，
> 没有永久删除孩子或家庭的 API/界面；完整目标、安全门槛和审批状态以 Active Spec 为准。

## Purpose and scope

让家庭管理员在明确影响并二次确认后清理误建或不再需要的孩子/家庭资料，并让清理整个家庭后的用户
安全回到“创建家庭 / 申请加入家庭”两条起始路径。用户可见入口名称为“删除配置”，Feature 名称不直接
把孩子或家庭对象化为待删除项。

## Current behavior

- 孩子档案可以归档和恢复；归档保留全部历史，没有物理删除态。
- 家庭可以创建、邀请、申请和管理其他成员；成员管理禁止自移除，没有删除家庭能力。
- 无家庭 onboarding 的创建路径仍把建立家庭与填写首个孩子绑定在一个表单。
- 直接进入孩子建档页时没有先验证 bound family 的路由保护，可能向 `/children` 发出无家庭请求并显示错误。

## Planned behavior (not current)

- 设置页新增中性入口“删除配置”，具体操作明确区分“删除孩子资料”和“删除当前家庭”。
- 永久删除使用持久化、幂等、可重试的清理流程；成功必须证明数据库和私有媒体无目标残留。
- 家庭删除推荐仅允许只剩本人一名有效成员的 manager；多成员家庭拒绝并说明先处理成员关系。
- 无家庭首屏只保留“创建家庭 / 申请加入家庭”；先创建家庭，之后才允许建立孩子学习档案。

## State and contracts

Target lifecycle: `active/archived → deleting → deleted`，执行失败保持可观察、可重试且禁止新写入。
Exact API、DDL、retention、错误码和 UI 仍为 proposal，未获批准或实现。

## Data, permissions and architecture

- Risk R3: scope includes child/family rows, memberships, invitations, requests, audit, jobs and private media.
- Recommended owner is a bounded `data_management` orchestration capability; existing domains retain their own data/purge contracts.
- Authorization remains server-side and family-scoped; no client ID or UI visibility authorizes deletion.
- Archive remains the recoverable path; permanent deletion has no restore promise.

## Frontend UI mapping

- `UI-010`: unbound two-choice onboarding and family-only create flow.
- `UI-016`: planned “删除配置” page and destructive confirmation/status states.
- `UI-015`: deletion completion removes stale child selection through the existing shared child context.
- Proposed design revision: `DREV-20260906-DATA-01`；Figma nodes and approval snapshot pending.

## Quality and release status

- Spec approval: pending.
- Figma/Design approval: pending; no waiver.
- Implementation/tests/cloud migration/release: not started/not run.
- Public release remains subject to the repository deployment and privacy/deletion gates.

## Source index

- Active Spec: `specs/active/FEAT-006-DATA-CLEANUP-AND-FAMILY-RESET.md`
- Related current features: `FEAT-002-family-collaboration.md`、`FEAT-005-multi-child-profiles.md`
- Architecture: `docs/architecture/ARCHITECTURE.md`、`ARCHITECTURE-CONSTRAINTS.md`
- Proposed decision: `docs/decisions/ADR-002-DURABLE-DATA-DELETION.md`
- Frontend: `docs/design/frontend/FRONTEND-DESIGN.md`、`FRONTEND-ENGINEERING-CONSTRAINTS.md`

## Change References

- 2026-09-06 — Planned baseline created from the user's request. `SPEC-20260906-DATA-CLEANUP-01` is
  `READY_FOR_REVIEW`; no production code, API, schema, current Behavior or release state has changed.
