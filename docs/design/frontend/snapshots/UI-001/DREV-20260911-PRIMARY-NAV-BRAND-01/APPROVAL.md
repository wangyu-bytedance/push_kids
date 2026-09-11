# 一级页品牌导航批准快照

- Spec: `SPEC-20260911-PRIMARY-NAV-BRAND-01`
- Design: `DREV-20260911-PRIMARY-NAV-BRAND-01`
- Owner/approver: 用户，2026-09-11
- Approval: “好的 按照这个落地”
- Scope: 五个一级 Tab 删除内容区“芽图标 + 知芽”；导航栏中央显示生成的芽图标 + “知芽”；today/calendar/reports 的上下文元信息移入 hero；详情与子流程继续使用微信原生导航
- Design artifact: `docs/design/frontend/prototypes/DREV-20260911-PRIMARY-NAV-BRAND-01/FRONTEND-SPEC.md`
- Baseline: `FDB-20260906-03`；`FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1（既有 FEAT-001 waiver anchor，非本次新增节点）
- User reference image SHA-256: `474a166cf331f52d39b9b3fc46c8728e4aa76185a132c63729c7a6690d3f97f7`
- Evidence exception: 用户批准沿用 FEAT-001 scoped waiver，公开生产前到期；不覆盖详情页自定义导航，也不免除原生视口/真机验证
- Required native evidence: 五个一级页 320×568、390×844、430×932；代表性 iOS/Android 胶囊；字体放大；进入详情并返回；实施后执行
- Verification status: 本地实现完成；focused 5 passed、全量前端 138 passed、ESLint/架构/小程序静态/图标幂等通过；五页 320/390/430 近似 PNG 已走查且横向溢出 0；真实 AppID preview 574832 bytes，开发者工具 iPhone 15 Pro Max 记录/设置页标题与胶囊无重叠。完整原生三视口、字体放大、深页返回与代表性 iOS/Android 真机为 NOT_RUN；未上传/部署
