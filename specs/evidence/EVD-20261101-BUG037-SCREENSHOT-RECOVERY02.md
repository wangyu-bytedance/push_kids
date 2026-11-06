---
created: "2026-11-01"
updated: "2026-11-01"
type: evidence
status: recorded
owner: GPT-6
---

# BUG-037 — 截图恢复02

- Evidence ID: EVD-20261101-BUG037-SCREENSHOT-RECOVERY02
- Requirement / acceptance: [BUG-037](../completed/BUG-037-REPORT-FOOTER-TIPS.md)，TP-004/005与当前证据闭合
- spec_revision: BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- subject_revision: content.wxml=c481d7021d56095123378d2d368c022c3d77cfdaf13374d35a3ffb75c7587e72；content.wxss=390bf6fa08c65729639bd027bc4aa402043df9c4b39c002d8688bfe77bd21e11（无新生产diff）
- 方法/命令: [恢复报告](../../docs/quality/evidence/REPORT-FOOTER-TIPS-SCREENSHOT-RECOVERY-20261101.md)
- result: passed

## Scope and output

- 官方工具2.01.2510290、基础库3.16.2；2026-11-01新专用进程/窗口，原生合成只读项目。
- passed只声明390/430两宿主96组PNG/JSON、0几何失败、图像解码/SHA匹配，
  以及168份冻结生产源＋批准2份替换的官方preview成功（1,192,127字节）。
- 首次截图超时、旧窗口失效与机型切换失败按报告保留；屏幕锁定为直接环境证据。
  重开项目/刷新窗口后截图恢复不等于所有超时根因已确认。
- [恢复manifest](../../docs/quality/evidence/report-footer-tips-20261101/recovery-manifest-02.json)绑定原生新图，
  [真机preview源](../../docs/quality/evidence/report-footer-tips-20261101/device-preview-source-manifest.json)绑定扫码包。
- 320、真实iOS/Android、大字/读屏/实际触摸NOT_RUN；手机未连接，扫码待用户。
  Spec VERIFYING/active，无upload、体验、审核或正式发布。

## Coding slice

- N/A: 本轮无生产编码；执行已批准TP与用户明确要求的工具恢复/设备验收准备。
- 原[实施01 EVD](EVD-20261101-BUG037-FINAL.md)的当时缺项保持原结果，本记录不追认旧图。
- 环境阻断与剩余Owner：用户解锁桌面/微信扫码；GPT-6继续320节点/截图与真机取证。
  未授终端屏录权限不是默认追加门禁，优先已恢复的官方截图与Computer Use链路。
