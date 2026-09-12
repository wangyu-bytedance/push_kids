# 草稿确认自动展示最新状态批准快照

- Spec: `BUG-SPEC-20260912-STALE-CONFIRM-01`
- Design: `DREV-20260912-STALE-CONFIRM-01`
- Owner/approver: `产品负责人（用户），2026-09-12`
- Approval: `“修复”——紧接完整 Spec revision、推荐方案和准确批准提示`
- Scope: `删除“刷新会离开当前编辑的草稿/查看最新”冲突提示；服务端安全跳过已变化的原始 Review 匹配并继续确认；终态冲突自动读取并展示最新只读详情；普通错误与新增科目同意路径不变`
- Baseline/FEC: `FDB-20260906-03 / FEC-20260911-READ-PERF-01`
- User screenshot SHA-256: `3c8e31e3826fbb9dc55eb82bfa322162adc1452f1cc88e6c99b6e16a6255fd9d`
- Figma: `https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1`（既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: `沿用 FEAT-001 scoped Figma Starter-plan waiver；仅覆盖 UI-001 既有确认页/记录详情页的本次错误恢复；公开生产发布前到期；不免除 320×568、390×844、430×932、字体放大及代表性 iOS/Android 原生验收`
- Authorized delivery state: `local implementation and verification only; no upload/deployment/release`

## Approved state transition

```text
confirming + stale original Review match -> skip duplicate Review progression -> confirm remaining content
confirming + terminal submission conflict -> automatic GET latest -> read-only latest
confirming + ordinary recoverable error -> keep edited draft + visible error
```

## Verification status

- Implementation: `PASS — shared draft conflict state/manual refresh notice removed; terminal 409 automatically loads authoritative latest; unresolved errors preserve edits`
- Automated evidence: `PASS — focused frontend 28 passed; full frontend 155 passed; ESLint, architecture checked=3 and Mini Program static validation 15 pages/644006 bytes passed`
- Native viewport/device evidence: `NOT_RUN — no WeChat DevTools/device execution in this local-only change; required before release`
