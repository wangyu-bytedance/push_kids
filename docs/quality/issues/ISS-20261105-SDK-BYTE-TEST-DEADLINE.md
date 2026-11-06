---
id: "ISS-20261105-SDK-BYTE-TEST-DEADLINE"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: test
owner: "Provider/test maintainer / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "HEAD0576ac304649 + Spec06 final source"
source_evidence: "docs/deploy/releases/20261105-fullstack-update-preparation.md"
regression_case: "tests/unit/test_stage_provider.py::test_request_bytes_match_real_sdk_transport_body"
closure_evidence: "specs/evidence/EVD-20261105-FULLSTACK-OPS01.md"
observation_evidence: "local only; no cloud writes"
prevention_control: "保留真实SDK精确字节验证；专门deadline测试独立"
closure_reason: "批准OPS01仅测试预算3→30，25专项/988全量及独立故障注入通过；本地resolved，非生产修复或云交付"
---

# 字节合同测试被3秒SDK预算阻断

本轮全量987PASS/56SKIP/1FAIL，唯一失败在真实SDK＋本地MockTransport字节测试；隔离运行仍1FAIL。此前Spec06相同源曾988PASS，也有两次同类失败，故旧PASS不证明稳定。3秒截止覆盖本地SDK初始化/序列化，当前失败在字节断言之前；尚未证明生产运输字节计算错误，不重开已解决的REQUEST-BODY-BYTE-ACCOUNTING根因。

用户明确批准[OPS01](../../../specs/completed/OPS-20261105-FULLSTACK-UPDATE.md)后仅字节测试预算改为有界30秒，真实SDK、中文/图片和精确字节/单次请求断言保持，生产预算和专门deadline/取消/排队测试未改。改后本轮整文件25PASS、全量988PASS/56条件skip；独立25PASS及错误字节/重复请求故障注入均被原断言拒绝。证据绑定afterSHA，原失败不覆盖，现本地resolved；这不是生产改进或完整发布PASS，不记closed。
