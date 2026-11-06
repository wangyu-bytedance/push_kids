---
id: "ISS-20261101-AUDITED-SOURCE-CORRECTION-SCOPE"
type: issue
created: "2026-11-01"
updated: "2026-11-01"
status: resolved
source: AI Review
owner: TRAE
severity: MAJOR
disposition: confirmed
observed_revision: "staged-20261101-11"
source_evidence: "specs/evidence/bug036-content03-20261101/review/group_1-audit.md"
regression_case: "docs/quality/regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md"
closure_evidence: "specs/evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md"
observation_evidence: "N/A: 本地12/15未云交付"
prevention_control: "item素材归属以正式evidence为准；改变候选来源的局部纠正正/负回归"
closure_reason: "本地行为回归PASS；无上线观察，未closed"
---

# 旧候选来源扩大素材局部纠正权限

`BUG036-C03-G1-001`：提取候选归属第一页，但merge已根据正式证据纠正到第二页；
Review仅要求修正第一页备注，旧实现仍把该item视为受影响，允许改动第二页已审查目标。
成员完整账本和随后模型review通过都不能代替确定性修改范围。

获批内容Spec03 AC-S02/S03要求证据唯一owner和无关目标不漂移。12版本的item归属
只取正式evidence；没有正式目录的omission仍沿候选lineage。新测试允许原页账本修正，
禁止第二页目标漂移并在history前拒绝。修复前负例未raise，修复后两路径及166专项PASS。
旧/新完整SHA和2FAIL/1PASS首败见12 EVD，不含原儿童素材。第二轮独立复审确认fixed、0新确认问题；真实case03及补充failed02的纠正漂移被确定性拒绝，未产生越界提案，但素材内容验收仍失败。

resolved-local；下次该域变更或发布前复查。内容质量、云交付和真实长期观察独立。
