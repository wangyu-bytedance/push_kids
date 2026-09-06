# UI-001 / DREV-20260906-REPORT-01 approval

- Design Revision: `DREV-20260906-REPORT-01`
- Related Spec at approval time: `BUG-SPEC-20260906-20`
- Approved implementation Spec: `BUG-SPEC-20260906-21`（用户于 2026-09-06 明确批准前后端实现）
- Approval date: 2026-09-06
- Approver: 王宇
- Approval evidence: 用户在查看 7/30/100 天固定 mock 与新用户状态后回复“按照这个方案 生成代码，前后端都需要”。
- Approved scope: 报表四张概览卡移除跳转与箭头；数字右侧显示固定 7 点直线趋势；7 天逐日，30/100 天按 7 个连续等宽时间段汇总；字段缺失显示“暂无趋势”；新后端完整零序列显示零基线。
- Prototype: `docs/design/frontend/prototypes/DREV-20260906-REPORT-01/index.html`
- Prototype SHA-256: `f52a44ed6ab18f6d7d1602e1ffa0dfc35c2a7207d8327ac5e42bd769d82d20fc`
- Figma node: `N/A — 沿用 FEAT-001 scoped Starter-plan waiver；根节点 anchor 不冒充 node-specific 证据`
- Waiver owner/expiry: repository owner；公开生产发布前失效。
- Native viewport evidence: pending implementation；必须补 320×568、390×844、430×932，且不能以本 HTML 原型代替。
