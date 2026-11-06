---
id: "ISS-20261101-FINAL-REFUSAL-CACHE-RETRY"
type: issue
created: "2026-11-01"
updated: "2026-11-01"
status: resolved
source: production
owner: TRAE
severity: MAJOR
disposition: confirmed
observed_revision: "production staged-20261031-06; reproduced on local staged-20261031-09"
source_evidence: "specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md"
regression_case: "docs/quality/regressions/REG-20261101-FINAL-REFUSAL-CACHE-RETRY.md"
closure_evidence: "specs/evidence/EVD-20261101-BUG036-CACHE02.md"
observation_evidence: "NOT_RUN: local staged10 has not been deployed; production jobs/cache not reset"
prevention_control: "Final-verdict cache eligibility plus terminal Worker cleanup and atomic explicit-retry semantic refresh"
closure_reason: "Resolved locally by approved cache Spec02 and deterministic/isolated MySQL verification; no release observation, not closed"
---

# 最终语义否决缓存与明确重试

- FEAT-001 / agent_processing + learning；原三个生产任务均failed/3attempts/无提案，复审再次should_merge/over_merged/vague_name。没有逐attempt云日志，因此“后续每次均复用缓存”仍是未直接观测假设。
- 本地09/13确定性复现：结构有效的review1false或reuseuncertain被缓存，StageFailure默认可重试，明确retry只重置次数/状态而不刷新语义分支。实际12项预期Red与原三份只读来源在缓存Spec/EVD。
- 根因：阶段结构完成未区分终态业务否决；任务恢复和家长明确重试共用旧语义结果。原测试只验证有效结果续接，没有最终否决/刷新/并发状态重查断言。
- 获批修复：`BUG-SPEC-20261101-KNOWLEDGE-CACHE-02` / `ARCH-20261101-KNOWLEDGE-CACHE-02`。review0中间否决保留，review1false/reuseuncertain不读写可复用缓存并终态；Worker守护失败事务及家长明确retry只清本提交语义units，保留有效提取/group；retry使用四表锁和重查failed，删除/状态reset共同回滚。
- 控制：31新增case、116专项、857后端/52默认skip、真实MySQL5.7 8专项；真实Red/Green、独立Review与代码快照见EVD。网络/非法结构有限恢复、18键/33调用预算和取消/确认/未知SQL提交保护保持。
- 仍未验证：10/13云交付/生产重试/发布观察、真实模型内容。原09/13三份为1内容PASS/1FAIL/1NO_OUTPUT，名字长度/拼音归类/教学角色失败另属内容ISS，不由本缓存修复声明通过。全库Ruff范围外错误保留为发布缺项。
- 复查：Owner产品负责人/TRAE；后续获授权发布后按匹配revision核对云结果与家长明确重试，不批量重置生产任务。无上线观察，不closed。
