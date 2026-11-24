# 家庭写入和通知租约独立评审

- Applicable policy: `REVIEW-20261028-01`，R3。
- Scope: [Spec01](../active/BUG-20261124-CORE-REVIEW-REMEDIATION.md)、[Architecture01](../../docs/architecture/decisions/ADR-20261124-CORE-TRANSACTION-BOUNDARIES.md)，产品负责人 2026-11-24 批准。
- Reviewer: 独立只读 `critical_reviewer`，`gpt-6.1-sol` / high。主会话执行实现和测试，未测量委派收益。
- Base: `a1ea8f61e642271b906575c5b4d202b21a2b0fe3`。
- Round 1: [manifest](core-review-20261124/review-snapshot-01.json)，SHA-256 `73e12cdc0ef30c3fbac2a5fa5043a3bd9984967c3fb0b0930f1b897d239d66b0`，28 条验证过的路径。结论 `REQUEST_CHANGES`，MAJOR 1，MINOR 1。
- Round 2: [manifest](core-review-20261124/review-snapshot-02.json)，SHA-256 `ce7a46baa0b80a90718ec9fdb8e6fb6382afc9fc543205d0a88c2e512d91265d`。独立复核所有 34 个哈希和 15 个增量文件。代码评审通过，原两项已修复，0 项新增已确认问题。原始快照与日志位于 `/tmp/push-kids-core-mysql.RDgjbt`。

## Findings and disposition

| Finding | 已确认的因果与证据 | 修复及复验 |
| --- | --- | --- |
| `CORE-R3-001`，MAJOR | `notifications/service.py` 循环在提交后仍持有 Session 中的已授权订阅对象。两次投递间，另一个调度器可以用完额度。独立文件 SQLite 复现三条消息、两次额度却调用 Provider 三次。补测在 SQLite 和 MySQL 5.7 都失败。 | 已修复。每条发送读取并刷新当前订阅，偏好与接收标识用标量查询，规划入队读取当前额度字段。两个数据库复测通过，Reviewer 单独运行文件 SQLite 新回归 1 项通过。 |
| `DOC-R3-001`，MINOR | FEAT-002 正文确认过往协作交付，架构映射与限制仍将它列为未实施或未部署。 | 已修复。更正当前架构映射及限制，区分既有协作交付、此次授权修复待交付与真实账号待验收。 |

## Per-file and mandatory review

第一轮按快照逐文件核对。`platform/context.py` 是统一授权边界，两个题库路由仅移除重复授权和提前回滚。`families/service.py` 保持家庭优先锁序并阻止本人移除。`children` schema 和 service 分别执行输入检查及剩余业务规则。`notifications/service.py`、`outbox.py` 和 `planner.py` 分别负责投递所有权、当前规划状态与 SQLite 事务入口。`platform/database.py` 仅为读取上下文。相关 API、SQLite 和 MySQL 测试与批准的验收绑定。README、架构、Feature、行为目录和 Spec 仅按此次切片审查，混合在同一文件的既有题库或教材增量保留各自审批和交付证据。

复评重点是原问题、相邻授权状态、额度扣减事务、测试屏障、Fixture 的显式隔离、文档与本地阶段结果。完整 Red/Green 和首败重试见[验证 EVD](EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md)。真实微信双账号、owner、收件以及云端版本切换保留为发布检查。UI 运行时无本次变化，DREV、FEC、真机节点与主题视口不适用。
