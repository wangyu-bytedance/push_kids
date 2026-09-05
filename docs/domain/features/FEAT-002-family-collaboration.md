# FEAT-002 — 家庭协作与孩子授权

- Feature ID: `FEAT-002`
- Status: `IMPLEMENTING`
- Current-state revision: `FEAT-STATE-20260905-06-BUG010-LOCAL`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-05
- Authoritative implementation: `apps/api/src/push_kids/families/`, family persistence models,
  `apps/miniprogram/pages/family-*`
- Active change Spec: `specs/active/FEAT-002-USER-FAMILY-BINDING.md` revision `SPEC-20260905-12`

> 本文只说明当前事实与已批准边界。家庭创建、邀请、申请、审批和成员角色已经在工作区实现并
> 完成本地 SQLite/MySQL 验证，但尚未迁移或部署到微信云托管；因此不能描述为线上可用。

## Purpose and scope

目标能力是让一个家庭中的父亲、母亲和长辈共同关注同一孩子，通过创建者分享、申请人提交、
孩子 manager 审批建立关系，并让学习、活动和日程显示真实操作者与监督者。

## Current user/system behavior

- 新 actor 通过 `/api/v1/me` 得到 `unbound`，可原子创建家庭、manager membership 和首个孩子，
  或凭短时邀请提交待审批申请。
- 云环境拒绝客户端家庭标识，并从可信微信 actor 解析 active membership；本地家庭流程可用
  `X-Debug-Actor`，旧的 `X-Family-ID` 仅保留给非家庭流程兼容测试。
- active member 角色为 manager/editor/viewer；被移除成员保留历史记录，但 active 唯一投影被释放，
  因而可以再次加入原家庭或创建新家庭。
- 创建家庭、邀请、申请、审批和拒绝具有服务端幂等语义；小程序在失败重试时复用同一幂等键。
- 邀请是单次批准凭据：首个批准将邀请置为 exhausted，并使同邀请的其他 pending 申请失效；撤销邀请也同步释放 pending actor。
- 成员管理接口无条件拒绝自移除；客户端本人详情不提供移除或角色修改。有效邀请列表不返回 token，申请双方通过六位申请码核对。
- 当前学习/活动记录没有可信的上传人、监督人、确认人和编辑版本归属。
- 云端迁移、真实双 actor 和限流验收尚未完成，公开发布仍被阻断。

## Current behavior matrix

| Capability | Current status | Evidence |
|---|---|---|
| create child in local workspace | available in FEAT-001 | children API + Mini Program settings |
| controlled cloud actor binding | implemented locally | `platform/context.py` + active membership；cloud rollout pending |
| verified collaboration identity/roles | implemented locally | family models/service + role integration tests |
| family member list | implemented locally | members API + Mini Program page |
| share/apply/approve | implemented locally | invite/request APIs + Mini Program pages |
| manager/editor/viewer enforcement | implemented locally | server boundary role checks |
| actor/supervisor attribution | not implemented | current persistence schema |

## Current state machine

Implemented locally as invite `active → exhausted/expired/revoked`, request
`pending → approved/rejected/cancelled/expired`, and member `active → removed`. Removed memberships retain history;
only the nullable active actor projection is unique.

## Current contracts

`SPEC-20260905-12` is approved and implemented in the local working tree. Its API/UI contract is not yet the cloud
current state because the migration and service release have not been deployed.

## Data and permissions

The local target schema contains families, members, invites, join requests and audit events. A nullable unique
`active_actor_binding_id` enforces one active family without preventing removed actors from rejoining. Cloud MySQL
still remains on the previous revision until the controlled migration window.

## Architecture mapping

- Current runtime adapters: FastAPI + MySQL/private cloud media for cloud staging, SQLite/local media for dev/test;
  one in-process Worker instance.
- Implemented module: `families` plus a narrow evolution of the existing cloud actor context. The first release keeps
  one active family per actor and family-wide roles; multi-family and per-child grants remain explicitly deferred.
- The earlier single-host SQLite production target is superseded by `ARCH-TARGET-20260903-06` for FEAT-001.
  FEAT-002 must be revised against the cloud runtime before implementation.

## Frontend UI current-state mapping

- Existing `UI-001` contains only the FEAT-001 parent application.
- `UI-009` family/member and `UI-010` share/application/approval pages are implemented under the approved scoped
  `FIGMA-WAIVER-20260905-01`; three-viewport visual and real DevTools acceptance remain pending.

## Current quality and operations

- SQLite integration, frontend idempotency, clean MySQL migration, concurrent approval, and removed-member rejoin
  tests pass locally. The broader MySQL worker suite currently has an unrelated analyzing-state timeout under review.
- Invite preview has trusted-actor in-process rate limiting and 429 tests. Remaining evidence includes shared multi-instance limiting, real AppID two-actor cloud staging, and three-viewport UI.
- Public production remains blocked by `ARC-011`.

## Limitations

- Cloud actor code exists, but real two-account gateway trust and lifecycle evidence is pending.
- Cloud deployment and real two-account gateway evidence are pending.
- Invite-preview in-process limiting is implemented for controlled staging; shared multi-instance limiting is still required before public production.
- Session/account lifecycle and public-production privacy evidence remain incomplete.

## Source index

- Active Spec: `specs/active/FEAT-002-USER-FAMILY-BINDING.md`
- Current architecture: `docs/architecture/ARCHITECTURE.md`
- Deployment runbook: `docs/DEPLOYMENT.md`
- Existing feature: `docs/domain/features/FEAT-001-push-kids-mvp.md`

## Change References

- 2026-08-30 — Baseline created as `PLANNED`; no implementation or runtime verification exists yet.
- 2026-08-31 — Planned target revised by `SPEC-20260831-06` from unapproved CloudBase/MySQL to single-host SQLite + standard WeChat login; implementation remains absent.
- 2026-09-03 — FEAT-001 adopted WeChat Cloud Hosting actor binding and MySQL/cloud storage infrastructure;
  FEAT-002 collaboration behavior remains unimplemented and its old runtime target is superseded.
- 2026-09-05 — `SPEC-20260905-11` proposed the cloud-native replacement: gateway actor identity, managed MySQL,
  create/join/approve onboarding, one active family per actor, family-wide roles, and a controlled-test Figma waiver;
  exact approval and implementation remain pending.
- 2026-09-05 — The product owner approved revision 11. During implementation, gateway access-log analysis found
  that a backend URL containing an invite token could not be safely redacted by application code. Revision 12 moves
  backend token transport to JSON bodies without changing the approved user journey; implementation/deployment paused for approval.
- 2026-09-05 — Revision 12 was approved and implemented locally. Follow-up fixes replaced lifetime actor uniqueness
  with active-only membership uniqueness and made Mini Program retries reuse stable idempotency keys; cloud rollout
  remains blocked on rate limiting and the controlled MySQL migration window.
- 2026-09-05 — BUG-010 revision 10 added self-removal protection, single-use invite lifecycle, request-code verification,
  active invite management, cascading pending-request cleanup and the member-detail interaction locally. Cloud rollout and native visual evidence remain pending.
