---
id: "ISS-20261105-ACCEPTANCE-ARCHIVE-TERMINOLOGY"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: review
owner: "Product owner / Codex"
severity: MINOR
disposition: confirmed
observed_revision: "BUG-SPEC-20261105-SYSTEM-ONE-06; R2-CR-002"
source_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
regression_case: "docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md"
closure_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
observation_evidence: "N/A: 术语勘误，不新增生命周期行为"
prevention_control: "分别测试deleting冻结拒绝写回与active=False归档允许既有任务收尾"
closure_reason: "沿用既有权威合同的术语修正，代码行为未改变；最终文档复核见EVD"
---

# 将删除冻结误称为归档

Spec06 §2/TP04称“归档拒绝迟到写回”，新测试却只设置deleting=True。既有FEAT-005/BHV-025明确归档仅拦新增、已有分析和草稿可收尾；Worker原_lock_active_scope也只拦deleting/无效家庭。本Spec同时要求原状态机保持，没有批准改变归档产品行为。

本项是来源可确定的术语误用，无需在两个合理产品方案之间另作选择。Spec06原误称、既有合同及勘误理由均明确保留；测试改名deleting，补active=False实际归档成功收尾。Worker不新增归档阻断。原批准不被用于追认新行为；文档、Feature和Behavior采用既有语义，独立Reviewer核对处置与版本。
