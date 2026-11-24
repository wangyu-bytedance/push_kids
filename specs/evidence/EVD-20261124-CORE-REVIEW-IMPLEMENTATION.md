---
created: "2026-11-24"
updated: "2026-11-24"
type: evidence
status: verified
owner: 项目维护者
---

# 家庭权限、通知租约与孩子档案修复验证

- Evidence ID: `EVD-20261124-CORE-REVIEW-IMPLEMENTATION`
- Requirement: [修复 Spec](../active/BUG-20261124-CORE-REVIEW-REMEDIATION.md)，TP-01 至 TP-06。
- spec_revision: `BUG-SPEC-20261124-CORE-REVIEW-01`，架构 `ARCH-20261124-CORE-TRANSACTION-01`。
- subject_revision: Git 基线 `a1ea8f61e642271b906575c5b4d202b21a2b0fe3` 上的 2026-11-24 本地工作树。原工作树包含已交付但未纳入该 Git 基线的题库代码和其他无关增量。[最终源码与测试快照](core-review-20261124/review-snapshot-02.json) SHA-256 `ce7a46baa0b80a90718ec9fdb8e6fb6382afc9fc543205d0a88c2e512d91265d`。快照中的文档冻结在评审时点，当前 EVD 补记结果。[主分支的独立验证](EVD-20261124-CORE-REVIEW-MAIN.md)
- 方法: 合成 API 数据、文件 SQLite 双连接屏障、Docker 隔离 MySQL 5.7.44 双连接屏障、只记录调用的 Provider、仓库静态检查和独立评审。
- result: passed（本地验证和 R3 独立评审；云验收单列）。

## 预期失败与兼容基线

保留首败日志。命令均从仓库根目录运行，使用 `uv run --no-sync pytest -q`，后接下表文件和对应单例，MySQL 行从隔离环境注入 `PUSH_KIDS_TEST_MYSQL_URL`。各阶段首次测试源未单独冻结，Red 对象是相应生产修复前的工作树版本，依据日志和执行顺序关联。发现阶段的 1,166 通过／84 跳过及旧 MySQL 验证见[发现证据](EVD-20261124-CORE-REVIEW-DISCOVERY.md)。

| 测试点 | 早期命令选择器（相对 `tests/integration/`） | 实际结果及日志 |
| --- | --- | --- |
| TP-01 | `test_mysql_runtime.py::test_waiting_family_write_uses_current_membership` | 预期两例失败。管理员提交降级和移除后等待中的 API 仍返回 200，应返回 403。`red-auth.log` |
| TP-02 | `test_notification_resilience.py -k 'reclaim_cannot_replace or replacement_lease or queue_tail'` | 预期三例失败。回收更新 1 行、旧持有者未丢弃、队尾过早 `sending`。`red-notification.log` |
| TP-02 相邻路径 | `test_notification_resilience.py -k 'planner_cannot_cancel or planner_cannot_rearm'`，分别执行 | 预期两例失败。规划器从旧快照取消 1 行、从旧快照重排。`red-cancellation.log`、`red-rearm.log` |
| TP-02 独立评审发现 | `test_notification_resilience.py::test_dispatch_refreshes_quota_between_claims` | SQLite/MySQL 两例预期失败。另一 Session 已用完授权，原调度器仍按旧授权发送第三条。`red-review-quota.log` |
| TP-03、TP-04 | `test_family_onboarding.py::test_invite_is_single_use_and_self_removal_is_forbidden test_multi_child_profiles.py -k 'self_removal or explicit_null or omission'` | 预期三例失败。两位管理员自移除返回 204，两个非法 `null` 返回 500。原合法年级清空／省略用例通过。`red-contract.log` |

Q-001 已以 `a1ea8f6` 提交。原型源和六主题、两视口生成的 HTML、228 张 PNG 和清单已确认字节一致。其验证对象与本次后端变更分开。

## Green 和检查

| 范围 | 命令（`uv run --no-sync` 前缀适用于 Python） | 实际结果 |
| --- | --- | --- |
| MySQL 变更及相邻行为 | `pytest -q tests/integration/test_mysql_runtime.py tests/integration/test_review_worksheet_mysql.py tests/integration/test_notification_resilience.py` | 36 通过（含同文件引用的 SQLite 用例），全新隔离库升级到 `20261115_0030`，`alembic check` 无漂移。`migration-r3.log`、`green-mysql-r3.log` |
| 全量后端 | `pytest tests/unit tests/integration tests/contract -q` | 1,172 通过、90 条件跳过。全量未注入可选外部环境，受影响的 MySQL 路径在独立专项验证。`green-backend-r3.log` |
| 复评定向 | `pytest -q tests/integration/test_notification_resilience.py tests/integration/test_notification_channel.py tests/integration/test_multi_child_profiles.py tests/integration/test_review_worksheets.py`（配置隔离 MySQL） | 80 通过，含两个数据库上的并发额度回归和 403/404 禁止副作用。`green-r3-focus.log` |
| 前端自动化 | `npm test` | 424 通过。`green-frontend.log` |
| 代码与结构 | `ruff check .`、`ruff format --check .`、`mypy apps/api/src`、`python tools/check_architecture.py`、`python tools/validate_design_evidence.py --check-current-policy`、`python tools/validate_miniprogram.py`、`git diff --check` | 通过。1,180 个文件格式、183 个 API 模块、19 个小程序页面。`green-static-r3.log` |
| HTTP 生成合同 | 构建本地 FastAPI OpenAPI，核对 `ChildUpdate` 字段 | 名称和预算可省略且显式值分别为字符串与整数，范围为 1–40 字符及 5–120 分钟，年级可为 `null`。`openapi.log` |
| 本地通知 tick | 文件 SQLite 中通过真实 API 设置合成提醒和订阅，记录型 Provider 和固定时钟连续执行两次 `NotificationScheduler.tick()` | 首次发送 1、次次发送 0、Provider 总调用 1，投递保留 `sent`。`scheduler-tick.log` |
| 独立 R3 | 独立审查两轮冻结源码，复跑文件 SQLite 额度回归 | 首轮发现 1 MAJOR、1 MINOR，均修复。第二轮 0 项新增已确认问题。[评审报告](CORE-REVIEW-20261124-R3.md) |

中间失败如实保留。初版档案 validator 因约束执行顺序仍触发两次 `TypeError`，移至 before 校验、分支约束后复测。MySQL 首轮 30 通过／4 失败，旧题单用例要求成员查询先于家庭锁，调整屏障到绑定查询与家庭锁之间，保留失效科目和日计划的持久状态断言。用已运行的 schema 重试有两项夹具数据重复，换全新 schema 后 34 项通过，评审修复后换另一全新 schema 最终 36 项通过。第一轮全量后端 1,166 通过／89 跳过／5 失败，三次外键错误及两次 404 发生在通用测试的内存 SQLite；本机环境启动了共享连接的后台调度器。通用夹具关闭隐式调度，第二轮全量 1,170 通过／89 跳过／1 失败，题单夹具同样出现 SQLite 外键失败。两个非调度夹具均明确禁用后全量通过。专门通知用例直接驱动规划、投递和受信任 HTTP 入口，另作单次工作循环 smoke，定时任务完整生命周期未验收。首轮、重试和最终日志分开保留。

## 文档及交付边界

核对 FEAT-002（家庭）、FEAT-003（提醒）、FEAT-005（档案）、FEAT-013（年级兼容）、FEAT-014（题库）、FEAT-006（删除）及 FEAT-011（续订）。前三项与年级合同已同步。行为目录的 BHV-012/023/026 与架构事务不变量已同步。README 题库章节以 11 月 16 日 042/043/0.1.21 的历史交付记录和配置为据。UI-009/010/011 的交互与证据无此次后端修订；原生和六主题视口不适用。架构依赖检查通过，沿用当前 Schema、API 路由和发布手册。回归契约见[REG](../../docs/quality/regressions/REG-20261124-CORE-TRANSACTION-REPAIR.md)。

- 本地报告和日志的受控位置为 `/tmp/push-kids-core-mysql.RDgjbt`，测试数据均为合成。真实微信双账号、owner、真实订阅送达、生产锁等待和混合版本互斥为 `NOT_RUN`，在实际发布流程继续核验。此次后端验证绑定当前工作树。Git 基线中尚无题库路由及复用的 SQLite 事务入口，不能将基于该快照的通过结论用于仅包含修复文件的 Git 提交。
- 状态为 `active/VERIFYING`。本次无匹配的云端部署证据。已知外部调用成功、进程退出而本地事务未提交时依然是尽力投递，恢复不包含生产历史记录自动重放。
