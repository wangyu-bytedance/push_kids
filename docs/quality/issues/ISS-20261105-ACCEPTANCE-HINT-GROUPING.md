---
id: "ISS-20261105-ACCEPTANCE-HINT-GROUPING"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: review
owner: "agent_processing maintainer / Codex"
severity: MINOR
disposition: confirmed
observed_revision: "Spec06 candidate01; R2-CR-003"
source_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
regression_case: "docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md"
closure_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
observation_evidence: "NOT_RUN: 无对应云交付"
prevention_control: "同一目标多标准低分仍只产生一条定位提示，同时保留逐标准内部findings"
closure_reason: "真实Red后本地Green及独立复核；未上线，不标closed"
---

# 同条目的多个验收意见占满提示容量

原实现仅全文去重，每个低分标准独立生成提示；四个条目各五个低分，加摘要/来源意见就超过20项，退化为单条通用说明，违背Spec06同目标合并要求。Reviewer独立复现；合成四目标测试在修复前FAIL，未改标签或标准。

现在按可信target汇聚固定标准短语，i0等目标输出一条中性定位提示；服务端内部findings仍逐标准留存。原学习事实不变、既有20条提示保留。Green及candidate02独立只读复核通过，具体SHA/命令见EVD，家长实际使用效果未代验。
