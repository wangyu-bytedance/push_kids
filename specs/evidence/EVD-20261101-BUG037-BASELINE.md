---
created: "2026-11-01"
updated: "2026-11-01"
type: evidence
status: recorded
owner: GPT-6
---

# BUG-037 — 提示Red差异与分页Baseline

- Evidence ID: EVD-20261101-BUG037-BASELINE
- Requirement / acceptance: [BUG-037](../completed/BUG-037-REPORT-FOOTER-TIPS.md)，AC-001/002，TP-001
- spec_revision: BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- subject_revision: content.wxml=3a3ecd9e51a8dedc692ae1361cbe230b4f3a2cc054f7caf939d052330563f933；content.wxss=e64d7736ad8644ceb2f14109072a56fdd0760d9814e49ccf98960d16f3d7cfe7
- 方法/命令: 专用官方auto项目中`node /tmp/push-kids-footer-design-20261101/native.cjs baseline <320|390> <embedded|standalone>`；真实原生节点/截图
- result: failed

## Scope and output

- 微信开发者工具2.01.2510290、基础库3.16.2；2026-11-01，隔离只读合成数据、改前真实生产WXML/WXSS/controller。
- 提示预期左右16px，实际`.notice`左右0px、13px字，用户报告的贴边已复现；这是真实预期行为差异。
  三种筛选分页同排、透明禁用，用户分页掉行未复现，原因NEEDS_VERIFICATION。
- 两宿主320/390各5态，共20组JSON/PNG；[详细记录](../../docs/quality/evidence/REPORT-FOOTER-TIPS-20261101.md)
  和`docs/quality/evidence/report-footer-tips-20261101/baseline/`保留原结果。
- 初次`:not()`节点探测失败留在`baseline-selector-attempt01/`，属于不支持的选择器，非Red；
  后续使用简单类选择器。430截图超时无有效基线。
- 未覆盖430基线和分页掉行的故障版本/设备条件；Owner为GPT-6（证据恢复）及用户（实际设备核验）。

## Coding slice

- Slice / test point / phase: 提示几何Red、分页Baseline / TP-001。
- Expected behavior failure or baseline / observed result: 只将真实padding0与批准16px的差异标为预期失败；
  不宣称分页已复现，不将新专用类在旧WXML不存在或截图服务错误当作产品Red。
- Related phase EVD and versions: [实施EVD](EVD-20261101-BUG037-FINAL.md)绑定改后源；本EVD不能追认改后对象。
- Test exception / alternative verification / risk / Owner: 可逆样式按批准Spec不新增CSS镜像单测；
  原生computedStyle与PNG为可失败验证。完整矩阵和真机开放，未借此通过发布验收。
