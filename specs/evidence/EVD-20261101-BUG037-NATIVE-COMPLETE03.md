---
created: "2026-11-01"
updated: "2026-11-01"
type: evidence
status: recorded
owner: GPT-6
---

# BUG-037 — 三视口原生矩阵03

- Evidence ID: EVD-20261101-BUG037-NATIVE-COMPLETE03
- Requirement / acceptance: [BUG-037 Spec01](../completed/BUG-037-REPORT-FOOTER-TIPS.md)，TP-004/005/006
- spec_revision: BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- subject_revision: content.wxml=c481d7021d56095123378d2d368c022c3d77cfdaf13374d35a3ffb75c7587e72；content.wxss=390bf6fa08c65729639bd027bc4aa402043df9c4b39c002d8688bfe77bd21e11
- 方法/命令: [齐套03报告](../../docs/quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)
- result: passed

## Scope and output

- 用户“已经解锁”后继续专用微信开发者工具2.01.2510290、基础库3.16.2；
  真实320×568，两宿主各24态48组PNG/JSON通过；结合02的390/43096组共144组。
- passed仅覆盖TP-004默认字体合成只读原生模拟器节点/PNG矩阵、解码/SHA和文档闭合。
  [manifest03](../../docs/quality/evidence/report-footer-tips-20261101/native-complete-manifest-03.json)绑定同一生产源码对象。
- 原01/02失败/缺项不覆盖，320新图在recovered-03；其余图保留recovered-01。
- 官方Tool.enableRemoteDebug返回无线真机二维码；等待扫码，手机未验证。
  生产debug本地插件41002失败及固定库后仍失败均保留，不伪装插件已修复。
- 原生产preview成功1192127字节保持原对象；无upload、体验、提审、正式发布；
  Spec VERIFYING/active。真实iOS/Android/大字/读屏/实际触摸NOT_RUN。

## Coding slice

- N/A: 本轮仅恢复环境和执行已批准测试点，无生产编码或范围扩展。
- Related phase EVD: [恢复02](EVD-20261101-BUG037-SCREENSHOT-RECOVERY02.md)、
  [实施01](EVD-20261101-BUG037-FINAL.md)和原Baseline分别绑定当时对象。
- Owner / remaining work: 用户用项目开发者微信扫码；GPT-6继续核对真实设备元数据并留真机证据，
  不将解锁消息解释为扫码成功，不把模拟器图片充当真机图片。
