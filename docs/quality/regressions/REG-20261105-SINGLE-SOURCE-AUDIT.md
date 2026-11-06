---
id: "REG-20261105-SINGLE-SOURCE-AUDIT"
type: regression
created: "2026-11-05"
updated: "2026-11-05"
status: active
kind: behavior
owner: "Product owner / Codex"
issue: "docs/quality/issues/ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md"
bad_revision: "staged-20261101-12 / prompt15; specs/evidence/bug036-success04-20261105/baseline/manifest.json"
fixed_revision: "staged-20261101-13 / prompt16; specs/evidence/bug036-success04-20261105/final-source-manifest.json"
test_path: "tests/unit/test_staged_analysis.py"
command: ".venv/bin/pytest tests/unit/test_staged_analysis.py tests/unit/test_staged_proposal_recovery.py -q -k 'single_source or unreadable_single or all_omitted' --tb=short"
red_evidence: "specs/evidence/bug036-success04-20261105/red.log"
green_evidence: "specs/evidence/EVD-20261105-BUG036-SUCCESS04.md"
reviewer_fixture: "N/A: behavior-only; no reviewer capability claim"
reviewer_evidence: "N/A: implementer verification is not independent review"
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# 单份未解来源核验与审查后空结果终态

FEAT-001 / agent_processing / MAJOR。冻结12/15对单文字或单图的needs_context在构组处直接失败；有候选或可读空候选均不能进入完整原来源核验。审查后全省略仍被标记为可重试，重复空转。

由[批准Spec04](../../../specs/completed/BUG-036-FIXED40-SUCCESS-REPAIR.md)将单份未解来源交给原merge/review，保留原excerpt、来源和逐素材账本；审查后无目标不可自动重试。技能规则的真实语义效果单独测量，不能用合成fake证明。

| 阶段 | 隔离环境与版本 | 实际结果 | 证据 |
|---|---|---|---|
| Red | 冻结12/15；无生产DB或模型请求；上述精确命令 | 5个预期FAIL、1PASS、105deselected；4个单来源早退、1个空结果retryable断言 | [red.log](../../../specs/evidence/bug036-success04-20261105/red.log) |
| Green | 本地13/16；同命令及相邻阶段/来源/重试测试 | 最终专项与全量结果见EVD；文字/图像×有候选/空候选均保留充分目标；unreadable仍拒绝 | [EVD](../../../specs/evidence/EVD-20261105-BUG036-SUCCESS04.md) |
| Worker/明确retry/取消 | 隔离SQLite；`tests/integration/test_analysis_checkpoints.py` | 空结果一次终态；不创建正式记录；重试保留提取并清语义；取消清全部临时阶段 | 同一EVD及最终测试日志 |

边界：不可读、来源SHA变化、多页group覆盖/上限、原历史严格等价和局部纠正保持。禁止编造缺失页、关闭质量检查、修改原40 fixture或扩充调用预算。原来源/最终DTO只在私有目录评阅，不提交儿童材料或模型原响应。

Reviewer evaluation：N/A，仅behavior回归；本轮没有独立新上下文Reviewer，不将实施者自查写成独立审查。内容ISS保持open，真实生成产出与家长验收分别记录。已纳入Spec04 TP-F01–05；没有新增CI/定时配置或生产观察，不冒称云回归通过。
