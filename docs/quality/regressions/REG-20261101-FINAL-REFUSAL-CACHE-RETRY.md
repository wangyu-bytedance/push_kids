---
id: "REG-20261101-FINAL-REFUSAL-CACHE-RETRY"
type: regression
created: "2026-11-01"
updated: "2026-11-01"
status: active
kind: behavior
owner: TRAE
issue: "docs/quality/issues/ISS-20261101-FINAL-REFUSAL-CACHE-RETRY.md"
bad_revision: "pre-implementation staged-20261031-09 snapshot; see cache02 baseline manifest"
fixed_revision: "staged-20261101-10; see cache02 source manifest"
test_path: "tests/unit/test_staged_proposal_recovery.py"
command: "uv run --no-sync pytest tests/unit/test_staged_proposal_recovery.py tests/integration/test_analysis_checkpoints.py tests/integration/test_worker_resilience.py -q"
red_evidence: "specs/evidence/EVD-20261101-BUG036-CACHE02.md"
green_evidence: "specs/evidence/EVD-20261101-BUG036-CACHE02.md"
reviewer_fixture: "N/A: behavior-only; fixed/baseline source snapshots retained"
reviewer_evidence: "N/A: not a reviewer identification benchmark"
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# 终态缓存与家长明确重试恢复契约

合成Provider/SQLite及独占新utf8mb4 MySQL5.7；不使用儿童图、真实身份、生产缓存或正式学习。测试仍在既有tests目录，安全源快照仅支持版本重放。

| Phase | 实际行为/版本 | 结果/证据 |
|---|---|---|
| Red | 在实施前09/13执行新增终态/cache/retry断言，未改生产源 | 12FAIL/47PASS；[Red日志](../../../specs/evidence/bug036-cache-20261101/red.log)和[EVD](../../../specs/evidence/EVD-20261101-BUG036-CACHE02.md)。首轮测试源未单独快照；日志为实际顺序证据，后续最终测试快照不能冒充首轮测试源 |
| Green | 最终10/13两次_call拒收最终否决、首attempt终态、明确retry新判断/保留提取、租户/rollback/lease guards | 116专项/857全量PASS，52默认环境skip；配置独占MySQL8PASS/0skip。首败/夹具/网络问题保持原分类 |

必须覆盖review0否决仍恢复纠正、review1/reuse各verdict、旧06语义unit删除、兄弟/其他家庭保留、archived许可/deleting拒绝、迟到attempt/lease/cancel、提交失败原状态、缺Job/双并发只有一次转移、四表锁顺序、晚checkpoint拒收、零正式新增。禁止通过删断言/扩大重试/审查抽签/清所有提取来“修复”。

坏/好生产源和最终测试源由[manifest](../../../specs/evidence/bug036-cache-20261101/source-manifest.json)绑定。后续旧快照重放必须在隔离副本用当前用例，标记为新的事后replay，而非伪造当初Red。行为active已有实际Red/Green且纳入Spec TP-C01–07；没有新CI/定时规则或人工审查器标签。
