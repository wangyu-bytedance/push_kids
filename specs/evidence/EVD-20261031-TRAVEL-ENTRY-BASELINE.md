---

本文件保留原执行时点的实施/验证与未交付结论；2026-11-01旅行三Spec已由039/0.1.17交付，DONE/completed，用户照片回看/分页/双账号门禁确认PASS。当前生命周期与平台阶段以[成功上传记录](../../docs/deploy/releases/20261101-client-0.1.17-upload.md)为准；下方VERIFYING/active/未上传仅代表原时点，设备/内容未验及历史FAIL不改为通过。
created: "2026-10-31"
updated: "2026-10-31"
type: evidence
status: recorded
owner: TRAE
---

# Version-bound Evidence — 旅行入口精简 Baseline

- Evidence ID: EVD-20261031-TRAVEL-ENTRY-BASELINE
- Requirement / acceptance: [旅行入口精简Spec01](../completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)，AC-002/003，TP02
- spec_revision: SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01
- subject_revision: 0576ac30464908154c624effed41df6dfa3110cc＋[实施前388份源清单](../../docs/quality/evidence/travel-entry-cleanup-20261031/source-before-implementation.json)；规范化files映射SHA-256 `c8792533094fbbfabf19b3456ba8522b2e31d9ccab3cf2cfdefe42243b510e12`
- 方法/命令: `node --test tests/frontend/footprints.test.js tests/frontend/record-types.test.js tests/frontend/manual-analysis.test.js`
- result: passed

## Scope and output

本机Node v22.22.0已有环境，在批准记录写入后、修改生产代码前执行。实际61 passed/0 failed/0 skipped，退出0；[原始输出](../../docs/quality/evidence/travel-entry-cleanup-20261031/baseline-related-tests.log)保留全部案例。未制造失败、未重新定义期望来适配变更。源清单覆盖当时既有未提交后端/客户端改动，HEAD本身不代替基线。

## Coding slice

- Slice / test point / phase: 两处入口删除及manual创建路径清理 / TP02 / Baseline
- Expected / observed: 原存活照片导入/编辑/权限/历史文本、宿主隔离与学习手动路径应通过；61/61通过
- Related final EVD: [最终自动化证据](EVD-20261031-TRAVEL-ENTRY-FINAL.md)
- Test exception: 低影响可逆删除不增加逐字镜像Red；可失败的原生入口/几何验收独立执行，当前NOT_RUN
- Risk / Owner: 此基线不能证明按钮已删除、最终布局或真机可用；用户/原生验证者补测，后续实现版本使用新源清单而不追认本基线
