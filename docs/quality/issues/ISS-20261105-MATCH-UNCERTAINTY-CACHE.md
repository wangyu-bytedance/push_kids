---
id: "ISS-20261105-MATCH-UNCERTAINTY-CACHE"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: triaged
source: test
owner: "Product owner / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "staged-20261101-13 / child-aware-history-agent-20261101-16"
source_evidence: "specs/evidence/EVD-20261105-BUG036-SUCCESS04.md"
regression_case: "docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md"
closure_evidence: "specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md"
observation_evidence: "N/A: 本轮仅私有快照生成，无云发布或生产重试；未证明线上同类输入的实际结果"
prevention_control: "匹配不确定的语义有效性须覆盖缓存写入及重试政策；严格历史等价不得降级"
closure_reason: "Spec05获批本地修复，Spec06保留并独立复核回归；云观察未完成，不标closed"
---

# 历史匹配不确定结果被缓存并在自动重试中重复复用

## 当前本地修复

用户已明确批准SystemOne Spec05及替代Spec06。`_checkpoint_reusable`拒绝match uncertain读写的共享修复保持；Spec05消歧/分类新路由已清退，当前启闭验收均为原Pro匹配/复用合同。旧classify键仅清理兼容，原人工retry锁序与事务保护保留。[原修复EVD](../../../specs/evidence/EVD-20261105-BUG036-SYSTEMONE05.md)记录Red/Green；[Spec06 EVD](../../../specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md)和新REG绑定当前缓存回归及独立代码Review。无匹配云交付/线上观察，不据本地修复关闭ISS。下文是Spec04原始观察，不表示当前仍未修复。

FEAT-001 / agent_processing / 本地真实回放。近期固定样本real07首attempt在match后validation失败；后两次extract/merge/review/match均命中相同内存checkpoint，匹配模型累计仅调用一次，三次均无提案。样本真实内容、身份和最终DTO不进入仓库。

原始基线根因：`pipeline.validate_matches`只验证candidate覆盖与引用；`_call`成功后先缓存MatchingResult；`any(choice.uncertain)`在调用之外抛出默认retryable validation。当时缓存可复用政策覆盖review1和reuse不确定，未覆盖match不确定。这条机制在Spec04冻结12/15基线已存在，不是成功率Spec04新增；Spec04没有修改它，后续Spec05已本地修复。

## 复现与证据

无模型/生产DB的合成StageFake把合法匹配DTO的一个decision设为uncertain，使用同一有界MemoryStages运行三次pipeline：

`.venv/bin/python /private/tmp/push-kids-success04-20261105/match_probe.py`

[探针JSON](../../../specs/evidence/bug036-success04-20261105/match-uncertainty-probe.json)实测三次`validation / match / match / retryable=true`，extract/merge/review/match各一次Provider调用、两次match缓存命中。该私有脚本SHA与来源在本轮工件清单绑定；这是剩余缺陷的确定性反证，不是修复Green。真实样本实际阶段缓存轨迹与之吻合。

## 原修复授权边界及当前对应

- 原需单独批准具体缓存/恢复Spec修订：成功率Spec04 AC-F03只批准审查后空提案终态，不能扩展授权。现在由用户明确批准的SystemOne Spec05覆盖本地修复，未追认Spec04授权。
- 推荐将match不确定的语义判断纳入缓存有效性校验，并明确自动恢复与家长retry的有限政策。备选为与reuse一致的终态/语义缓存清理，避免空转，但不能把停止重试本身当成功率提高。
- 不允许把不确定历史强行复用、改成无审核新目标或放宽匹配；不增加调用槽/阶段超时/整体attempt上限。
- 后续须有缓存重放的诚实Red/Green、Worker事务/明确retry与取消测试，及固定同源真实复测；本轮内容review和旧门禁结果不被后续运行覆盖。

当前triaged/open，已本地修复与回归；Spec06独立代码Review已核对保留修复，云观察NOT_RUN，不标closed。
