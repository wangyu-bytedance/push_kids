# 学习档案面板视觉降噪批准快照

- Spec: `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01`
- Design: `DREV-20260911-SETTINGS-PROFILE-MANAGER-02`
- Owner/approver: 用户，2026-09-11
- Approval: “落地”
- Scope: 姓名/年级两级排版；当前状态改为次级文字；块状“编辑”改为透明 88rpx 铅笔点击区；新增入口并入列表；功能、权限、路由和后端合同不变
- Baseline/FEC: `FDB-20260906-03 / FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 （既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: 沿用 FEAT-001 scoped Figma waiver，公开生产发布前到期；不免除 320×568、390×844、430×932 与代表性 iOS/Android 的原生面板验收

## Implementation evidence

- Local implementation: 已按批准范围落地；后端/API/Schema 未改。
- Automated: focused frontend 32 passed；full frontend 140 passed；ESLint、静态、架构、图标幂等与 diff check 通过。
- Preview: registered AppID local preview 575988 bytes；未上传/部署。
- Visual boundary: 9 个 HTML fixture 已生成；PNG 因缺少 Playwright Chromium executable 未运行；修改后原生三视口、字体放大与代表性 iOS/Android 为 `NOT_RUN`。
