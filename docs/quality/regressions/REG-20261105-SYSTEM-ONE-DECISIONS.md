---
id: "REG-20261105-SYSTEM-ONE-DECISIONS"
type: regression
created: "2026-11-05"
updated: "2026-11-05"
status: retired
kind: behavior
owner: "Product owner / Codex"
issue: "docs/quality/issues/ISS-20261105-MATCH-UNCERTAINTY-CACHE.md"
bad_revision: "specs/evidence/bug036-systemone05-20261105/baseline-manifest.json; mysql57-plan-red-manifest.json"
fixed_revision: "specs/evidence/bug036-systemone05-20261105/final-source-manifest.json"
test_path: "tests/unit/test_system_one_workflow.py"
command: ".venv/bin/python -m pytest tests/unit/test_system_one_provider.py tests/unit/test_system_one_workflow.py tests/integration/test_system_one_history.py tests/integration/test_system_one_confirmation.py tests/integration/test_system_one_index_migration.py tests/integration/test_analysis_checkpoints.py -q"
red_evidence: "specs/evidence/bug036-systemone05-20261105/workflow-red.txt"
green_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE05.md"
reviewer_fixture: "N/A: behavior-only; no reviewer capability claim"
reviewer_evidence: "N/A: independent review not performed"
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: "获批Spec06替代未交付Spec05生成实验；历史证据保留，当前消费者转REG-20261105-SYSTEM-ONE-ACCEPTANCE"
---

# REG-20261105-SYSTEM-ONE-DECISIONS

2026-11-05已退役：此文下方命令/测试映射仅绑定Spec05历史冻结源，部分测试随路由删除，不能当作当前可执行命令。保留原失败与通过证据；当前协议、共享match缓存及旧覆盖/迁移兼容由[辅助验收REG](REG-20261105-SYSTEM-ONE-ACCEPTANCE.md)维护，不新增原关系路由。

- Feature：FEAT-001；批准`BUG-SPEC-20261105-SYSTEM-ONE-05`。
- Issues：ISS-20261105-MATCH-UNCERTAINTY-CACHE；新判定协议/资源与确认边界。
- Evidence：[SystemOne05 EVD](../../../specs/evidence/EVD-20261105-BUG036-SYSTEMONE05.md)，首败/诊断/Green分开，未云交付或独立Review。

| 触发 | 必须保持的结果 | 可执行消费者 |
|---|---|---|
| 专用接口乱序答案、缺题、额外题、NaN/越界、HTTP400/401/429/503 | 按question ID校验，错误分类且单次外呼；不记录材料/响应 | test_system_one_provider.py |
| 选项概率≥0.95但confidence小于0.95 | 按批准的选项概率阈值关联；不引入第二个门槛，confidence仍须有限合法 | test_system_one_workflow.py |
| 同名旧内容被判部分重叠 | 不让确认阶段的旧name/category唯一身份静默复用，终态拒绝 | test_system_one_workflow.py |
| Q1来源标准不通过，纠正仍不通过 | 最多一次纠正，然后不可自动重试，无正式写 | test_system_one_workflow.py |
| match uncertain缓存；家长明确retry | uncertain不读写复用；同事务清classify及其他语义、保留提取、不清兄弟/外家庭 | test_system_one_workflow.py、test_analysis_checkpoints.py |
| 9图+文字+两组+纠正+历史复用 | 仍最多18临时键，派生reuse不新增一键；不提升预算 | test_system_one_history.py |
| 最近历史100项含未来与superseded | 每科取最近40个normal且不含未来/外scope；两条SQL并使用复合索引 | test_system_one_history.py |
| MySQL5.7五万项、20科、同刻排序 | 返回精确800项、11条SQL；每分支强制复合索引且无库存filesort，外层只排最多80项 | test_system_one_mysql.py |
| 新覆盖正常/旧版本变化/当天已复习/重复应用 | 正常observed再替代；过期跳过；同日不重复计数，重复应用零副作用 | test_system_one_confirmation.py |
| 新索引0027升级/降级 | 只加/删有序复合索引，保留并行0026，启动guard跟真实head | test_system_one_index_migration.py、test_child_profile_lifecycle_migration.py |

运行：`.venv/bin/python -m pytest tests/unit/test_system_one_provider.py tests/unit/test_system_one_workflow.py tests/integration/test_system_one_history.py tests/integration/test_system_one_confirmation.py tests/integration/test_system_one_index_migration.py tests/integration/test_analysis_checkpoints.py -q`。

隔离MySQL5.7.44实际运行上述新MySQL5项与既有checkpoint/并发8项，最终13 PASS；最初查询计划FAIL与夹具时间精度FAIL保留，生产改动仅限定MySQL新索引。测试容器已删除，未使用生产数据库。

此REG证明确定性机制，不把模型内容、全量生产成功率或速度目标记为PASS。关系40的85%正例召回和固定40首波36/40 FAIL仍保留。极限token/原真实30+3材料和独立review缺项见EVD。
