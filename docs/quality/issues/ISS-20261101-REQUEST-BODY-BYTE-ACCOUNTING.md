---
id: "ISS-20261101-REQUEST-BODY-BYTE-ACCOUNTING"
type: issue
created: "2026-11-01"
updated: "2026-11-01"
status: resolved
source: AI Review
owner: TRAE
severity: MINOR
disposition: confirmed
observed_revision: "staged-20261101-11"
source_evidence: "specs/evidence/bug036-content03-20261101/review/group/group_2-audit.md"
regression_case: "docs/quality/regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md"
closure_evidence: "specs/evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md"
observation_evidence: "N/A: 本地12/15未云交付"
prevention_control: "HTTPX request hook只计已序列化body长度；真实SDK本地transport精确断言"
closure_reason: "运输字节回归PASS；无上线观察，未closed"
---

# pre-SDK估计被标为实际发送字节

`BUG036-C03-G2-001`：SDK合并extra_body并用紧凑JSON发送，先序列化Python参数字典
所得字节数不是真实HTTP body。独立探针1013≠912；新回归1179≠1070。
旧mock测试比较同一pre-SDK字典，因此不能发现错误。这是遥测错误，不声称容量旁路。

12版本在HTTPX request event hook计`len(request.content)`，只保留整数，不记录内容；
payload/image计数独立。真实SDK+本地MockTransport的中文/图片输入精确断言通过，
客户端在SDK上下文退出时关闭，原超时/取消/两槽/无SDK重试合同保持。首败与166专项、
源码SHA和独立复审见12 EVD，第二轮确认fixed、0新确认问题。12固定30/补充/边界成功请求运输字节已实际留存；失败请求完整成本及最大9图SDK/云峰值未验，资源PARTIAL。原11合成request大小继续标为构造值，不改写历史观测。

resolved-local；下次Provider变更或发布前复查。总费用、失败请求资源和云内存独立验收。
