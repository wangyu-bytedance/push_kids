---
id: ISS-20261124-CORE-TRANSACTION-REPAIR
type: issue
created: "2026-11-24"
updated: "2026-11-24"
status: triaged
source: ai-review
owner: 项目维护者
severity: BLOCKER
disposition: confirmed
observed_revision: "a1ea8f61e642271b906575c5b4d202b21a2b0fe3 + 修复前工作树"
source_evidence: specs/evidence/EVD-20261124-CORE-REVIEW-DISCOVERY.md
regression_case: docs/quality/regressions/REG-20261124-CORE-TRANSACTION-REPAIR.md
closure_evidence: specs/evidence/EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md
observation_evidence: NEEDS_VERIFICATION
prevention_control: specs/active/BUG-20261124-CORE-REVIEW-REMEDIATION.md
closure_reason: NEEDS_VERIFICATION
---

# 家庭写入、通知投递和档案输入缺陷

- CORE-001 影响 MySQL 的已绑定写入授权。普通读取建立了旧角色快照，家庭加锁后未再读当前成员。原题单针对单一路由复核，不能保护其他写入。新回归覆盖通用孩子 PATCH 与原题单相邻入口。
- CORE-002 影响过期租约、迟到发送者和规划状态转换。旧条件外更新会覆盖已经提交的投递，批量预领让队尾在发送前过期。R3 评审还复现逐条领取后 Session 继续复用旧额度的问题。回收、规划与发送分别覆盖当前状态和双连接重放。
- CORE-003 原单管理员回归只能命中最后一位管理员保护。两管理员场景检查本人被拒且可移除另一成员，核对绑定和审计记录。
- CORE-004 旧部分更新 schema 接受数据库不可空的两个字段，触发持久层错误。真实请求检查两个 422、状态不变、字段省略以及合法年级清空。

[批准的修复 Spec](../../../specs/active/BUG-20261124-CORE-REVIEW-REMEDIATION.md)约束修复和回退。[回放步骤](../regressions/REG-20261124-CORE-TRANSACTION-REPAIR.md)和[分阶段证据](../../../specs/evidence/EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md)保留预期首败。生产受影响记录数量和历史变化待核验，问题保留 `triaged`。后续实际发布时核验双账号写权限、锁等待、调度互斥和真实通知恢复，再依据观察决定关闭。
