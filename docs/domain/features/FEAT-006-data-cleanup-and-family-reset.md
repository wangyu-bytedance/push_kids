# FEAT-006 — 家庭资料清理与重新开始

- Feature ID: `FEAT-006`
- Status: `IMPLEMENTED_LOCALLY_PENDING_CLOUD_ACCEPTANCE`
- Current-state revision: `FEAT-STATE-20260907-02-NOTIFICATION-PURGE`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-07
- Authoritative implementation: `apps/api/src/push_kids/data_management/`、各 domain 的 `purge_data` 合同、Alembic `20260906_0007_durable_data_deletion` + `20260907_0009_notification_deletion_scope`、`apps/miniprogram/pages/data-cleanup/`
- Active change Specs: `SPEC-20260906-DATA-CLEANUP-01` + `BUG-SPEC-20260907-22`
- UI current state: `UI-010-family-access`、`UI-015-child-profile`、`UI-016-data-cleanup`

> 本文只描述当前本地事实。永久删除及无家庭重启流程已经实现并通过本地测试；通知数据集成修复正在完成独立复核。生产 MySQL 迁移、云端 worker、真实私有媒体与三视口真机证据尚未完成，因此不能把本 Feature 描述为已在生产可用。

## Purpose and scope

家庭管理员可以永久删除一个孩子的全部资料，或在自己是唯一有效成员时删除整个家庭；清理失败可观察、可重试，不会把部分清理报告为成功。归档仍是可恢复的日常路径，永久删除是独立且不可恢复的数据权利路径。删除家庭后 actor 回到“创建家庭 / 申请加入家庭”的无家庭入口。

## Current behavior

- 设置页以中性入口“删除配置”承载两条危险操作；最终确认明确显示影响并要求输入当前孩子称呼或家庭名。
- `POST /data-management/deletions/children/{child_id}` 与 `/family` 仅允许 verified active manager；家庭删除还要求只剩本人一名 active member。`Idempotency-Key` 支持安全重放，状态与 retry 通过 deletion-request API 查询。
- 请求接受时先把目标置为 deleting；新的孩子学习/科目/活动/日程等写入被拒绝，删除 worker 通过数据库租约执行媒体清理和跨领域数据库 purge。失败按有界策略重排，耗尽后为可人工重试的 `failed`。
- 数据库阶段在一个事务中调用各领域 owner 的 `purge_data`，随后删除 child，或删除 family member/family 并解绑 actor；任一 SQL 错误整体回滚，不能得到假的 `succeeded`。
- 通知域纳入 owned-data inventory：child-bearing delivery 使用 `notification_delivery_children` 表达完整归属。child 删除移除所有引用它的 delivery（多孩子摘要整条移除），保留家庭级偏好、授权与 receiver；family 删除清空 delivery/link/preference/subscription/destination。旧的无 scope 日程/复习 delivery 按隐私优先清理。
- 删除冻结与通知 planner/outbox/dispatch 使用数据库锁串行化；删除请求被接受后不会再为目标入队或调用发送渠道。
- 成功请求只保留 30 天最小墓碑，不保留原始目标 ID、确认名称、OpenID、通知正文或媒体路径；过期后可清理。
- child 删除成功后共享 child context 选择首个仍 active 的档案，或进入无档案空态；family 删除成功后清空本地选择并回到无家庭二选一入口。无家庭时深链到 child-edit 不会先发 `/children` 请求。

## State and contracts

```text
target: active | archived --accept--> deleting --worker succeeds--> physically absent

deletion request:
queued --lease--> running --success--> succeeded --30d--> pruned
                    | failure/restart
                    +--> queued(retry) --> failed --manual retry--> queued
```

- 同一 actor + idempotency key + 同一目标返回原请求；不同目标冲突。
- deleting 目标不允许新的业务写入；worker/retry 必须幂等。
- 媒体先清理、数据库后清理；若数据库阶段失败，已删除媒体不会复活，但请求不会报告成功，重试继续收敛。
- 删除后的业务数据不可恢复；代码回滚不得丢弃已经接受且尚未终态的请求。

## Data, permissions and architecture

- `data_management` 只拥有删除请求状态机、冻结与编排；learning/planning/activities/travel/media/children/families/notifications 各自拥有清理语义，避免 orchestration 直接写其他领域表。
- 所有查询和清理同时以 `family_id` 限定；客户端传入 ID、页面可见性或确认文本都不承担授权。
- notification delivery 的 child link 是 ownership 元数据，不从展示 payload 或孩子姓名反向解析。
- 当前单一 Alembic head 为 `20260907_0009`，`Database.expected_cloud_revision` 与其一致。

## Frontend UI mapping

- `UI-010`: 无家庭首屏仅有“创建家庭 / 申请加入家庭”；创建家庭不要求同时建孩子。
- `UI-016`: 删除配置 overview、孩子/家庭影响确认、处理中、失败/重试与完成状态。
- `UI-015`: 删除完成后通过共享 child context 清除 stale selection。
- Design revision: `DREV-20260906-DATA-01`，由一次性 Figma waiver 支持本地实现；公开发布前仍需补节点与原生矩阵证据。

## Verification evidence（2026-09-07，本地）

- 通知删除专项：`PYTHONPATH=. uv run pytest tests/integration/test_data_deletion.py tests/integration/test_notification_channel.py tests/integration/test_notification_channel_lifecycle.py tests/integration/test_notification_migration.py -q` → 24 passed，包含 claim 后 purge 先提交的 child/family 确定性交错。
- 完整后端：264 passed, 2 skipped；完整前端：124 passed；ruff、format、mypy（79 files）、architecture、Mini Program lint/validator 均 PASS。
- fresh SQLite `upgrade head/current` PASS（`20260907_0009`）。`alembic check` 暴露的是 `origin/main` 已存在的索引 metadata drift，本次迁移未新增该漂移；isolated MySQL 与云端验收仍待完成。

## Known gaps

1. 生产数据库仍未执行 `0007..0009` 的最终发布迁移/校验，本轮发布前必须先确认可恢复备份。
2. 真实云托管 worker、对象存储删除与两账号身份回归待部署验收。
3. `UI-016` 的正式 Figma node、320/390/430 原生节点几何和 iOS/Android 真机证据仍是公开发布门禁。
4. 若微信发送事务先取得锁并完成远端调用，删除请求会等待其提交后才被接受；外部已接受消息不可撤回。

## Source index

- Active Specs: `specs/active/FEAT-006-DATA-CLEANUP-AND-FAMILY-RESET.md`、`specs/active/BUG-016-NOTIFICATION-DELETION-INTEGRATION.md`
- Decisions: `docs/decisions/ADR-002-DURABLE-DATA-DELETION.md`
- Architecture/behavior: `docs/architecture/ARCHITECTURE.md`、`docs/domain/BEHAVIOR-CATALOG.md`
- Tests: `tests/integration/test_data_deletion.py`、`tests/integration/test_notification_channel.py`、`tests/integration/test_notification_migration.py`、`tests/frontend/data-cleanup.test.js`

## Change References

- 2026-09-06 — `SPEC-20260906-DATA-CLEANUP-01` / PR #6：实现 durable child/family deletion、无家庭重启流程与删除配置 UI。
- 2026-09-07 — `BUG-016 / BUG-SPEC-20260907-22`：补齐通知 owned-data inventory、delivery-child ownership、legacy 隐私清理，以及删除冻结后的入队/发送并发边界；最终 commit 与云端证据待发布后回填。
