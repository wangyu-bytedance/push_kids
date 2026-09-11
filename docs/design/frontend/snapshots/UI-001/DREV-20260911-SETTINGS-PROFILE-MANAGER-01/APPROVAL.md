# 设置页学习档案入口收敛批准快照

- Spec: `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01`
- Design: `DREV-20260911-SETTINGS-PROFILE-MANAGER-01`
- Owner/approver: 用户，2026-09-11
- Approval: “落地”
- Scope: 删除设置页普通态整个学习档案区块；把切换、编辑、归档恢复、添加和上限说明迁入右上角面板；无孩子首次建档保留；只读权限和后端合同不变
- Baseline/FEC: `FDB-20260906-03 / FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 （既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: 沿用 FEAT-001 scoped Figma waiver，公开生产发布前到期；不免除 320×568、390×844、430×932 与代表性 iOS/Android 的原生面板验收

## Implementation evidence

- Local implementation: complete
- Automated evidence: focused frontend 32 passed；full frontend 140 passed；ESLint、Mini Program validation、architecture and icon idempotence passed
- Local preview: registered AppID package 574991 bytes；not uploaded or deployed
- Approximate states: settings main/sheet/viewer/limit fixtures generated at 320×568、390×844、430×932
- Native evidence: `NOT_RUN` for the modified sheet across the three viewports, font scaling and representative iOS/Android devices
