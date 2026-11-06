---
id: "ISS-20261031-KNOWLEDGE-GENERATION-MECHANISMS"
type: issue
created: "2026-10-31"
updated: "2026-10-31"
status: resolved
source: test
owner: TRAE
severity: MAJOR
disposition: confirmed
observed_revision: "staged-20261031-06 and BUG036 Review01"
source_evidence: "specs/completed/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md"
regression_case: "docs/quality/regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md"
closure_evidence: "specs/evidence/EVD-20261031-BUG036-IMPLEMENTATION.md"
observation_evidence: "N/A: 本次仅本地实施，未部署当前增量"
prevention_control: "完整成员/省略账本、同alias纠正、真实历史名称核验、执行预算owner、静态诊断及18/33容量回归"
closure_reason: "机制已在隔离测试和独立Review02验证；内容验收及云交付不由这些证据证明，暂不closed"
---

# 知识生成机制与防复发

## Impact and reproduction

- FEAT-001 / agent_processing；旧默认生成在质量纠正、省略、排队预算、历史范围及缓存容量上存在机制缺陷。原30来源评测13条无输出；不能将全部内容失败归因于确定性机制。
- 获批预期：完整覆盖或合法省略；纠正不改错对象；拿到请求槽后开始执行限额；历史复用受实际旧名/范围/技能核验；不产生业务写入或未审查草稿。
- 使用合成Provider、内存SQLite及冻结旧实现重放，精确命令和观察时间顺序见EVD。儿童图、身份和原模型阶段不作为仓库夹具。

## Root cause and escaped controls

- 原合并要求所有候选必须发布，审查要求省略无证据候选，两者冲突；问题编号与纠正对象不一致。
- 旧局部执行限额在排队前开始；历史输入不足，最终旧名称覆盖此前已审查目标。
- Review01又发现同名装配旁路、过小全局身份容量、共享身份指令矛盾、超长未知数字字段诊断、Worker丢失新诊断。冻结快照、8条诚实Red与Green、两组独立Review02及跨组核验保留原结果。
- 旧测试偏重流程/字符串/调用次数，缺少失败机制及真实素材整批质量验证。最靠近根因的控制是现有生产owner中的有界验证及行为回归。

## Fix and verification

- 用户批准BUG-036 Spec01 / Architecture01 / Prompt04，仅本地实施与零写入验证。
- 机制修复在staged07完成；staged08/09只细化同批准规则并更新指纹，DTO、调用、缓存、API和Schema不变。当前09独立审查71与全量832pass/46skip见[09EVD](../../../specs/evidence/EVD-20261031-BUG036-PROMPT09.md)。
- [REG](../regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md)纳入本轮required点。真实基线52pass，4项先Red后Green；10项保存旧实现的事后基线重放明确标注；Review01的8项Red与修复Green不混记。
- 832pass/46条件skip；目标lint、format796、mypy151、架构4/151通过；全仓Ruff在无关旅行工具103字符行失败。
- 内容一致性另见[未关闭内容问题](ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md)，不能由合成测试或内部审查passed追认。

## Closure and recurrence

本地机制resolved，非整项BUG-036已验收。排队与绝对到期同时发生的错误标签仍PARTIAL；未发现早截止或槽泄漏。当前增量未部署，未伪造上线观察。后续复查由项目维护者在下次该域变更或发布前执行。
