# FEAT-002 — 家庭协作与孩子授权

- Feature ID: `FEAT-002`
- Status: `PLANNED`
- Current-state revision: `FEAT-STATE-20260903-03-PLANNED`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-03
- Authoritative implementation: not implemented
- Active change Spec: `specs/active/FEAT-002-USER-FAMILY-BINDING.md` revision `SPEC-20260831-06`

> 本文只说明当前事实与已批准/待批准边界。`PLANNED` 不表示家庭身份、关系、审批或
> 家庭身份、关系或审批已经实现。FEAT-001 现在有一个只用于受控 staging 的微信 actor →
> family binding 基础设施，但它没有成员角色、共享、申请或审批语义。

## Purpose and scope

目标能力是让一个家庭中的父亲、母亲和长辈共同关注同一孩子，通过创建者分享、申请人提交、
孩子 manager 审批建立关系，并让学习、活动和日程显示真实操作者与监督者。

## Current user/system behavior

- 当前系统没有 User、FamilyMember、ChildGuardian、Share 或 AccessRequest 实现。
- 本地请求仍使用 `X-Family-ID`。云环境拒绝它，并把微信入口 actor 的 HMAC 绑定到一个 family；
  该绑定只能证明受控 staging 数据范围，不能证明家庭成员角色或授权关系。
- 当前学习/活动记录没有可信的上传人、监督人、确认人和编辑版本归属。
- 因此本 Feature 尚不可用，公开发布被阻断。

## Current behavior matrix

| Capability | Current status | Evidence |
|---|---|---|
| create child in local workspace | available in FEAT-001 | children API + Mini Program settings |
| controlled cloud actor binding | infrastructure only | `platform/context.py` + `wechat_actor_bindings`；real staging pending |
| verified collaboration identity/roles | not implemented | no user/member/guardian role model |
| family member list | not implemented | no models/routes/pages |
| share/apply/approve | not implemented | no models/routes/pages |
| manager/editor/viewer enforcement | not implemented | no guardian authorization |
| actor/supervisor attribution | not implemented | current persistence schema |

## Current state machine

N/A: share/application/member lifecycle is planned in the active Spec but has no current implementation.

## Current contracts

There is no production FEAT-002 API/UI contract. The target contracts in
`SPEC-20260831-06` are proposals until the exact revision and Figma Design Revision are approved and implemented.

## Data and permissions

No FEAT-002 collaboration tables exist. `wechat_actor_bindings` is FEAT-001 staging infrastructure, not a
member/guardian model. Current `family_id` strings are data-scope keys only and must not be described as
authenticated family relationships. No role authorizes collaboration access.

## Architecture mapping

- Current runtime adapters: FastAPI + MySQL/private cloud media for cloud staging, SQLite/local media for dev/test;
  one in-process Worker instance.
- Planned modules: `identity` and `families`, plus attribution changes in `learning`/`activities`.
- The earlier single-host SQLite production target is superseded by `ARCH-TARGET-20260903-06` for FEAT-001.
  FEAT-002 must be revised against the cloud runtime before implementation.

## Frontend UI current-state mapping

- Existing `UI-001` contains only the FEAT-001 parent application.
- Planned `UI-009` family/member and `UI-010` share/application/approval documents do not exist yet.
- Visible implementation is blocked until `DREV-20260831-05` node-specific Figma approval and snapshots exist.

## Current quality and operations

- FEAT-001 automated/DevTools evidence does not prove family authorization.
- Required future evidence includes role/cross-family/concurrency/session/SQLite migration/backup/restore tests and real AppID staging.
- Public production remains blocked by `ARC-011`.

## Limitations

- Cloud actor code exists, but real two-account gateway trust and lifecycle evidence is pending.
- No safe multi-person binding.
- No manager approval or relationship permission.
- No member revocation/session/account lifecycle or public-production privacy evidence.

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
