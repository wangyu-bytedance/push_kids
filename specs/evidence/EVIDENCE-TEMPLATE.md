---
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
type: evidence
status: draft
owner: NEEDS_VERIFICATION
---

# Version-bound Evidence

- Evidence ID: EVD-[TODO: stable-id]
- Requirement / acceptance: [TODO: Spec路径/revision及AC/TP；无需新建DLV台账]
- spec_revision: NEEDS_VERIFICATION
- subject_revision: NEEDS_VERIFICATION
- 方法/命令: NEEDS_VERIFICATION
- result: not_run

## Scope and output

- 环境/工具版本、范围、前提、开始时间：
- 预期/实际、首次失败和重试（不得覆盖首败）：
- 产物：已有报告/日志/快照的仓库相对路径或受控位置；无产物说明原因：
- 未覆盖行为及剩余风险/Owner：

## Coding slice (when applicable)

- Slice / test point / phase: Red / Baseline / Green / Refactor verification / final verification:
- Expected behavior failure or baseline / observed result:
- Related phase EVD and versions:
- Test exception / alternative verification / risk / Owner:

result枚举：passed / failed / stale / unknown / not_run。Red测试结果为failed，
阶段标签说明预期原因；不能把环境错误算Red。非编码切片写N/A并说明。
不同实现/测试/Spec版本和阶段分别留证，旧EVD对新对象为stale并需重验；保留
原运行记录，不能改旧spec_revision/subject_revision追认。passed仅证明声明范围，
不等于完整产品验收或发布。历史 `docs/quality/evidence/` 留在原路径，EVD只引用。
