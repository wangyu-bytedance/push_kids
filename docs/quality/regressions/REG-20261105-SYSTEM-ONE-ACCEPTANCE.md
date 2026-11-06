---
id: "REG-20261105-SYSTEM-ONE-ACCEPTANCE"
type: regression
created: "2026-11-05"
updated: "2026-11-05"
status: active
kind: behavior
owner: "agent_processing maintainer / Codex"
issue: "docs/quality/issues/ISS-20261105-ACCEPTANCE-DB-TRANSACTION.md"
bad_revision: "Spec06 candidate01; start-manifest及真实Red见EVD"
fixed_revision: "candidate02; source manifest及唯一AST等价格式修正见EVD"
test_path: "tests/integration/test_worker_acceptance.py"
command: "uv run pytest tests/unit/test_proposal_acceptance.py tests/unit/test_system_one_provider.py tests/unit/test_system_one_workflow.py tests/integration/test_worker_acceptance.py tests/integration/test_worker_resilience.py tests/integration/test_system_one_confirmation.py tests/integration/test_system_one_index_migration.py -q"
red_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
green_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
reviewer_fixture: "N/A: behavior-only"
reviewer_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# 原Pro生成后的辅助验收边界

批准Spec06；关联事务[ISS](../issues/ISS-20261105-ACCEPTANCE-DB-TRANSACTION.md)、提示[ISS](../issues/ISS-20261105-ACCEPTANCE-HINT-GROUPING.md)及归档术语[ISS](../issues/ISS-20261105-ACCEPTANCE-ARCHIVE-TERMINOLOGY.md)。真实模型生成率与家长内容验收不能由本REG代验。

| 触发 | 必须保持 | 可执行消费者 |
|---|---|---|
| source/scope/summary/coverage为0.95，subject/granularity/action/separate为0.90；检查报疑点或未报 | 相同学习事实/证据/关联，只有提示可变；等于阈值不报警 | test_proposal_acceptance.py |
| 429/5xx/超时/缺答案/非法概率/容量或低预算 | 明确降级终态，保留原产物，不增加生成或Job attempt | test_proposal_acceptance.py、test_system_one_provider.py、test_worker_acceptance.py |
| 多标准指向同一条目、已有20条提示 | 按目标合并，逐标准内部记录；原提示内容保留 | test_proposal_acceptance.py |
| 9图/20点、64KiB响应、两请求槽 | 有界问题与读流，停止超限响应，正确释放槽与取消资源 | test_system_one_provider.py、test_proposal_acceptance.py |
| 外呼期间取消、删除冻结、家庭失效、lease/attempt变化或耗尽 | 无DB事务，拒绝迟到写回，0正式事实 | test_worker_acceptance.py |
| 外呼期间家长手动确认、实际归档 | 人工确认胜出；归档已有任务允许收尾 | test_worker_acceptance.py |
| 开启/关闭验收、match uncertain缓存 | 同一Pro生成路由，不重启分类/最近40/关系实验；uncertain不复用 | test_system_one_workflow.py、test_analysis_checkpoints.py |
| 待确认/原家长确认、旧覆盖快照、0027迁移 | 只家长确认产生正式事实；兼容保留，不生成新旧判定元数据 | test_worker_acceptance.py、test_system_one_confirmation.py、test_system_one_index_migration.py |

实际执行、失败/重试、源SHA和独立Review见EVD。MySQL、原生/设备及云观察单列，不由SQLite或Node测试冒充。
