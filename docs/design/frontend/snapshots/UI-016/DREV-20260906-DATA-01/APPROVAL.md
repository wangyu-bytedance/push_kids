# UI-016 / DREV-20260906-DATA-01 approval

- UI ID: `UI-016-data-cleanup`
- Design revision: `DREV-20260906-DATA-01`
- Task Spec: `SPEC-20260906-DATA-CLEANUP-01`
- Status: `APPROVED_BY_SCOPED_WAIVER`
- Approver: 产品负责人（用户）
- Approval date: 2026-09-06
- Approval evidence: 用户明确回复“批准 SPEC-20260906-DATA-CLEANUP-01 和 ADR-002，并批准为 DREV-20260906-DATA-01 使用一次性 Figma waiver 后实现”。
- Figma node: `N/A — Starter/当前工具环境未提供可编辑节点，本次使用显式 waiver`
- Approved visible contract: `docs/design/frontend/ui/UI-016-data-cleanup.md`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`

## Waiver boundary

- ID: `FIGMA-WAIVER-FEAT006-20260906-01`
- Scope: UI-016 删除配置、UI-010 无家庭二选一/家庭独立创建、UI-015 无家庭路由保护与删除后回落。
- Risk: 缺少 editable Figma node 和正式图片 hash，视觉差异只能由 PKDS-1.0 token/atoms、源码和原生视口证据约束。
- Owner: 产品负责人（用户）。
- Expiry/remediation: 公开生产发布前必须补齐 node-specific Figma URL、正式 approval exports/hash，以及 320×568 / 390×844 / 430×932 原生节点几何与 iOS/Android smoke；完成后 waiver 失效。
- Not authorized: 新颜色、字体、圆角、信息架构、删除范围或其他 Feature 的可见变更。

## Current evidence

- Approval export images: `NOT_AVAILABLE_BY_WAIVER`.
- Native viewport/device evidence: `NOT_RUN — implementation has not completed`.
- Automated frontend evidence: `NOT_RUN — implementation has not completed`.
