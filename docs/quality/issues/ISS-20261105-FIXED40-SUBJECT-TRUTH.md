---
id: "ISS-20261105-FIXED40-SUBJECT-TRUTH"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: test
owner: "Knowledge quality maintainer / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "staged-20261101-13 / child-aware-history-agent-20261101-16 / fixed40 v1"
source_evidence: "docs/deploy/releases/20261105-fullstack-update-ops01.md"
regression_case: "fixed40 multi-04; original FAIL retained"
closure_evidence: "specs/evidence/EVD-20261105-FIXED40-V2.md; local v2 fixture only, not cloud"
observation_evidence: "one diagnostic pass, temporary SQLite only, formal writes0"
prevention_control: "评测期望须有直接材料证据；测试输入版本化，原评分阈值保持"
closure_reason: "Spec07获批后新增v2唯一词汇补充，完整单轮40/40通过；原40及37/40不追改，生产未变，家长内容仍PENDING"
---

# 三科评测材料只有英语主题，却要求英语知识产物

原40中multi-04的expected包含英语，但英语内容仅为主题，没有具体词汇。当前`stage_contracts.py`共同规则要求词汇学习提供具体对象或封闭范围，禁止用主题猜词表；`evaluate_analysis_quality.py::_score`只判断产物科目集合是否与expected完全相等，不核对该科材料是否足够。

原门禁为subject.mismatch，原产物临时库已清理，不能补称已观察原产物具体省略项。本次一次诊断明确观察到提取needs_context=true，merge保留语文/数学并以indeterminate_object省略英语，最终产物为两科；评分仍报subject.mismatch。诊断不是完整门禁，不修改原37/40结果。

材料最早可查提交为`b3db2198a56caa50112b0a2b0e212ce3444b64dc`（Git author wangyu，2026-09-26）；规则文件最后可查提交为`26714b997465fd2d1d9199f45ed931bd85c39405`，当前还有已批准Spec06工作区增量。Git author不是PR提交人身份，未查到对应PR/MR；不据日期/提交人判断正确语义。当前批准的证据规则和真实诊断支持材料冲突结论；完整文件SHA随新EVD绑定。

用户已明确批准[材料Spec07](../../../specs/completed/BUG-036-FIXED40-MATERIAL-ALIGNMENT.md)。新增v2仅补三个明确英语词汇，三科目标/分母及原40/原FAIL保留；独立逐字段Review确认唯一差异和40条分布，原评分完整单轮40/40、三科各15/15、零empty/pending/formal，见[新EVD](../../../specs/evidence/EVD-20261105-FIXED40-V2.md)。本地材料冲突记resolved，不closed，不代表生产改进或家长内容通过；最终文档/结果增量复核另记。复查2026-11-06或下一次生成发布准备前取先到者。
