# 今日页活动空态行动收敛批准快照

- Spec: `SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`
- Design: `DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`
- Owner/approver: 用户，2026-09-11
- Approval: “落地”
- Scope: 保留上方普通主卡“添加日程”和首次引导态的互斥日程入口；删除课外活动空态下方重复按钮；保留“今天没有活动安排”
- Baseline/FEC: `FDB-20260906-03 / FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 （既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: 沿用 FEAT-001 scoped Figma waiver，公开生产发布前到期；不免除 320×568、390×844、430×932 原生空态验收
- Implementation evidence: 本地实现已完成；前端 138 passed，ESLint、小程序静态/架构检查通过，真实 AppID preview 574832 bytes；三档 HTML fixture 已生成，PNG/原生三视口/iOS/Android 为 NOT_RUN；未上传、未部署
