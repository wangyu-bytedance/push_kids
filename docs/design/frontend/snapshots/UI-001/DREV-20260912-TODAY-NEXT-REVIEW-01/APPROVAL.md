# 今日页最近复习安排批准候选

- Status: `APPROVED`
- Task Spec: `BUG-SPEC-20260912-REVIEW-VISIBILITY-01`
- Design Revision: `DREV-20260912-TODAY-NEXT-REVIEW-01`
- Owner/approver: `产品负责人（用户），2026-09-12`
- Scope: `“待复习”改为“复习安排”；今天为 0 时显示最近已排期日期与完整知识点；今天有任务时未来安排降级为一行预告；知识名称完整换行；未来项只读；有界展开`
- Baseline/FEC: `FDB-20260906-03 / FEC-20260911-READ-PERF-01`
- User screenshot SHA-256: `4c21c6599da229fb9e5d6137a58bb42b294bb80f90f8beea08551bcfbb18b72b`
- Candidate: `today-next-review-390.png`；editable source: `today-next-review-390.svg`
- Candidate SHA-256: `76ee3ba9426c5e29312017d6c12d9e528a9b7ab2659cbc042a6a51e1cd8087ee`；SVG SHA-256: `c43ba5ff634326b0b963f8c57833230248f570ae898e5798daad93dc8360b544`
- Figma: `https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1`（既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: `沿用 FEAT-001 scoped Figma Starter-limit waiver；仅覆盖 UI-001 今日页复习分区的本 revision；公开生产发布前到期；不免除三视口、字体放大及 iOS/Android 原生验收`
- Approval evidence: `用户在收到 Spec、Design Revision 与候选图后回复“按照这个修复”`
- Authorized delivery state: `local implementation and verification only; no upload/deployment/release`

## Approval identity

需要用户明确批准：

`BUG-SPEC-20260912-REVIEW-VISIBILITY-01 + DREV-20260912-TODAY-NEXT-REVIEW-01 + today-next-review-390.png`

## Verification status

- Source/code implementation: `PASS — local implementation complete; frontend 161 passed; independent R2 review PASS`
- Required state/source evidence: `PASS — next-only/due/no-plan/old-server/continuation-error and >=88rpx source contracts covered`
- Native viewport evidence: `NOT_RUN — 320×568 / 390×844 / 430×932 remains a release gate`
- Native device evidence: `NOT_RUN — release gate`
