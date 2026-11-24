---
id: REG-20261124-CORE-TRANSACTION-REPAIR
type: regression
created: "2026-11-24"
updated: "2026-11-24"
status: active
kind: behavior
owner: 项目维护者
issue: docs/quality/issues/ISS-20261124-CORE-TRANSACTION-REPAIR.md
bad_revision: "a1ea8f61e642271b906575c5b4d202b21a2b0fe3 + 2026-11-24 修复前工作树，评审增量 Red 见 EVD"
fixed_revision: "BUG-SPEC-20261124-CORE-REVIEW-01 对应的冻结源码，见 EVD"
test_path: tests/integration/test_notification_resilience.py
command: "uv run --no-sync pytest -q tests/integration/test_mysql_runtime.py tests/integration/test_notification_resilience.py tests/integration/test_notification_channel.py tests/integration/test_family_onboarding.py tests/integration/test_multi_child_profiles.py tests/contract/test_api_contract.py"
red_evidence: specs/evidence/EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md
green_evidence: specs/evidence/EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md
reviewer_fixture: N/A
reviewer_evidence: N/A
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# 家庭写权限与通知当前状态回放

使用合成家庭、档案、投递和授权。设置 `PUSH_KIDS_TEST_MYSQL_URL` 指向环回地址上刚迁移至检出版本 head 的临时 MySQL 5.7 库。SQLite 并发回归使用文件库。本地假渠道只计数。主分支结果见[主分支验证](../../../specs/evidence/EVD-20261124-CORE-REVIEW-MAIN.md)。首败及题单路由的附加验证见[原工作区证据](../../../specs/evidence/EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md)。

| 覆盖 | 稳定回放与观察结果 |
| --- | --- |
| 家庭写入 | `test_waiting_family_write_uses_current_membership` 在管理员持锁时送出 PATCH，管理员提交降级或解绑后等待请求返回 403，孩子和成功审计不变。原题单并发回归覆盖 SQLite 写入先获锁也能正常完成。 |
| 通知恢复 | `test_mysql_reclaim_cannot_replace_a_committed_send` 暂停发送回执到回收 UPDATE 下发，随后提交 `sent`，回收更新为零。`test_old_dispatcher_cannot_send_under_replacement_lease` 与 `test_dispatch_does_not_lease_queue_tail_before_it_can_send` 检查迟到持有者、队尾等待超过一次租约时长和逐条领取顺序。 |
| 通知计划和额度 | `test_mysql_planner_cannot_cancel_a_delivery_from_an_old_pending_snapshot` 和 `test_mysql_planner_cannot_rearm_a_delivery_from_an_old_skipped_snapshot` 保留已提交终态。`test_dispatch_refreshes_quota_between_claims` 让另一 Session 在两次领取之间花光额度，第三条投递 `skipped / not_authorized`，渠道恰调用两次。 |
| 档案与自移除 | 两位管理员时自移除 409；成员、绑定与成功审计保留，移除另一成员仍成功。`test_patch_rejects_explicit_null_without_changing_child` 与 `test_patch_omission_preserves_values_and_explicit_grade_can_clear` 检查空值和合法变更。相邻测试分别验证 viewer 和跨家庭的 PATCH 拒绝。 |

本条为行为回放。独立 R3 代码评审记录随 EVD 保留。真实平台验收依发布手册单独记录。
