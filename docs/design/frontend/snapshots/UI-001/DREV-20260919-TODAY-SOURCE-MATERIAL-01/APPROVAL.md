# UI-001 — DREV-20260919-TODAY-SOURCE-MATERIAL-01 Approval Snapshot

- Status: `APPROVED`
- UI ID: `UI-001`
- Design Revision: `DREV-20260919-TODAY-SOURCE-MATERIAL-01`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/completed/BUG-023-TODAY-REVIEW-SOURCE-MATERIAL.md#BUG-SPEC-20260919-REVIEW-SOURCE-01`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20260919-TODAY-SOURCE-MATERIAL-01/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20260919-TODAY-SOURCE-MATERIAL-01/today-source-material.html`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20260919-TODAY-SOURCE-MATERIAL-01/today-source-material.html=0aee14362353d81fa2ba743a4fca5089b534db07333b8f23d4c917b92bb9c5ce`
- Prototype generated/updated at: `2026-09-19`
- Approved by: `产品负责人（用户）`
- Approved at: `2026-09-19`
- Approval evidence: `用户在明确列出 BUG-SPEC-20260919-REVIEW-SOURCE-01 + DREV-20260919-TODAY-SOURCE-MATERIAL-01 的批准请求后回复“批准”`
- Superseded by: `N/A`

## Approval identity

需要产品负责人明确批准：

`BUG-SPEC-20260919-REVIEW-SOURCE-01 + DREV-20260919-TODAY-SOURCE-MATERIAL-01`

## Candidate scope

- Surfaces/flows: Today 当前复习卡；知识点级原始材料底部弹层。
- States: 照片来源、文字来源；loading/混合/empty/retry/gone/unauthorized 在 Frontend Spec 中定义并由实现验证。
- Viewports: `320×568`、`390×844`、`430×932`，照片与文字各一组候选。
- Interaction behavior: 删除出现原因和带练提示；显示原题摘要；原地弹层查看材料；较矮完成按钮保留44px热区。
- Copy/semantics: 不生成复习内容、不判分、不声明掌握；只展示已确认 evidence 和原始上传材料。
- Permitted implementation-only deviations: 原生字体 fallback、真实内容导致的自然换行、微信图片解码造成的缩略图裁切差异。
- Explicitly not approved: 新 AI review 调用、新表/列、OCR/crop、跳历史页、客户端排期、原图首屏预取。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `today-source-photo-320.png` | Today / photo source sheet | 320×568 | 1x | `59e372e41a623173451c8260ef26682720c7e053a69c810e854d813f27b84756` | scrollable sheet; relevant image visible |
| `today-source-photo-390.png` | Today / photo source sheet | 390×844 | 1x | `d1a055f965cc5f7e1e06146ac076f7d590bfb5985c6a2e81cc05929b15584982` | reference viewport |
| `today-source-photo-430.png` | Today / photo source sheet | 430×932 | 1x | `81e132d92f13d634f5e0271db563c62ec097b45394a0afaef530eedb54b21d27` | wide phone |
| `today-source-text-320.png` | Today / text source sheet | 320×568 | 1x | `ed8ff8bc2b49be97922203f4fb15bfe6a717f31a1822f484586409fdfefc38f5` | narrow phone |
| `today-source-text-390.png` | Today / text source sheet | 390×844 | 1x | `796638263fbd8a49bbdef9cc68366114f59d25a6f90842a70aa39d18b0c06237` | reference viewport |
| `today-source-text-430.png` | Today / text source sheet | 430×932 | 1x | `d7656d00b3a2b10ea49964c695b1cefa0088b3dc384eea4898e57a621d96d2ae` | wide phone |

## Gaps and follow-up

- States not represented: loading、mixed、empty、retry、gone、unauthorized/not-found；行为由 Frontend Spec 和自动/原生验收覆盖，不单独扩大批准图数量。
- Manual assumptions: 设计源中的练习册题面为无身份布局占位，不作为模型或 OCR 正确性证据。
- Native runtime evidence: `DevTools preview compile PASS（603151 bytes）；repository exports do not replace native 320/390/430 node geometry, iOS/Android, large text or real private-media evidence, which remain NOT_RUN`。

## Integrity checklist

- [x] Editable source exists, is repository-local, and its SHA-256 matches.
- [x] Every listed export exists and its SHA-256 matches.
- [x] Required baseline viewports and photo/text states are represented; other states are explicitly listed.
- [x] Approval names the Task Spec revision and Design Revision.
- [x] Manifest frozen after approval; any visible divergence creates a new Design Revision.
