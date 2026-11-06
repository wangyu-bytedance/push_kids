---
id: "ISS-20261105-ACCEPTANCE-DB-TRANSACTION"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: review
owner: "agent_processing maintainer / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "Spec06 candidate01; R2-CR-001"
source_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
regression_case: "docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md"
closure_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
observation_evidence: "NOT_RUN: 无对应云交付/线上观察"
prevention_control: "真实Worker验收回调使用Session事务事件，断言无活动事务；随后验证迟到状态不能覆盖"
closure_reason: "本地修复与独立复核通过；未上线，不标closed"
---

# 验收外呼前访问过期ORM对象重新打开读事务

Worker构造上下文后rollback会expire ORM对象；随后读submission.family_id/child_id/id隐式SELECT并开启事务，验收外呼因此持有DB事务。新验收暴露该既有Pro路径问题，违反Spec06事务外外呼合同。独立Reviewer以SQLAlchemy最小实例复现，真实Worker取消/lease/deleting测试同样失败。

修复捕获的family_id/child_id/submission_id标量在rollback后完整传递给scope、StageCheckpoints和Runner，避免五处隐式ORM加载；不修改锁序、scope义务、事务提交或租约策略。首次仅修scope/checkpoints遗漏Runner参数，三项仍FAIL；保留失败后核对共同前提，确认剩余ORM访问，再完成修复，52专项PASS。新增真实family失效、attempt接管、lease耗尽、人工确认和实际归档回归后，77专项PASS；独立candidate02复核59PASS。

原问题未在只断言pending草稿的测试暴露，因为验收异常会正常降级；新增事务事件断言和状态副作用断言同时观察I/O边界与写回，防止仅吞异常让测试误过。candidate01真实试跑因此中止且不纳入最终成功率。candidate02 Worker SHA以EVD为准，未部署，后续发布仍需线上观察。
