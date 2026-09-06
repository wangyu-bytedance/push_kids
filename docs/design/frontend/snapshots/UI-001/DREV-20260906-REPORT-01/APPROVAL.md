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
- Implementation state: 前后端与自动化验证已完成；报表指标卡使用原生 WXML/WXSS 线段，不含运行时 mock 或图表依赖。
- Approximate viewport evidence: `tools/preview` 已生成 320/390/430 三档源码近似 HTML；390px 已于 2026-09-06 走查，数字、折线和标签无明显重叠。该证据不替代原生验收。
- Local compile evidence: 微信开发者工具 CLI 已登录并完成 `open` + `preview`，包体 545.7 KB（558772 bytes）；只生成本地预览，未上传。
- Native viewport evidence: `NOT_RUN`；仍须补报表页 320×568、390×844、430×932 微信开发者工具节点几何、字体放大和真机证据。Playwright fallback 因本机缺少 Chromium 未运行。
