# UI-001 — 今日待学与提前复习设计候选

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261024-TODAY-LEARNING-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md#SPEC-20261024-EMPTY-DAY-EARLY-REVIEW-04；specs/active/FEAT-004-INCREMENTAL-LEARNING-PATH.md#SPEC-20261024-INCREMENTAL-LEARNING-PATH-04
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-01/index.html=84f5fb4ccf8511b9c812af819e23a58855942b13749c023662a1f635dd4f1f6b
- Prototype generated/updated at: 2026-10-24
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-24
- Approval evidence: 用户在明确列出两份Spec04、复习Architecture02/学习建议Architecture03及本DREV01的审批问题后回复「批准，按此实现」。未改HTML、PNG或SHA。
- Superseded by: DREV-20261024-TODAY-LEARNING-02（仅学习建议主态头部及底部操作层级；Task Spec为SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01）；DREV-20261024-TODAY-LEARNING-03（仅今日学习卡片显隐与样式；SPEC-20261024-TODAY-CARD-VISIBILITY-01，用户2026-10-24于call_ac391833df284fc7b0afcb71c55abec7明确批准）。原HTML/78张PNG/SHA不变；其他范围继续有效。

## Candidate scope

两份Spec03需求由产品负责人「按照这个方案 落地」批准；随后两份Spec04、各自Architecture02/03与本Design01经明确审批问题后的「批准，按此实现」批准。自本次批准起冻结设计与导出。

范围：今日待学卡、建议编辑/审批/换项/暂缓、部分/完成实际记录、删除再生成；复习提前标识及原日期、目录安排信息和只读。其余五Tab/今日已确认记录/目录筛选布局不改。26状态全部覆盖320×568、390×844、430×932，共78张PNG，1x。review-early/long/viewer截取内容区滚动220px，其余从顶部；keyboard为210px占位。具体交互/质量矩阵见FRONTEND-SPEC.md。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| review-due-320x568.png | UI-001/review-due | 320×568 | 1x | fb7176b773b9ff45acf8b25463b0c8c08b1a0096ff2c15b82b10c934da18f450 | 合成HTML设计；非原生验收 |
| review-early-320x568.png | UI-001/review-early | 320×568 | 1x | c3141cbacb045dac40800a1a32834749fd5fc7076e2568934fff912e4586629d | 合成HTML设计；非原生验收 |
| review-empty-320x568.png | UI-001/review-empty | 320×568 | 1x | 7577fda62d77804277cde0bd00e1f084c0d99c88d1e901b1781486c39091798b | 合成HTML设计；非原生验收 |
| review-handled-320x568.png | UI-001/review-handled | 320×568 | 1x | 8ae860e4e0ed894c9ac978837e3942359fd6049b18793fa8b26826a75e1f65be | 合成HTML设计；非原生验收 |
| review-inventory-320x568.png | UI-001/review-inventory | 320×568 | 1x | 8b69b212f3d8df84244f65c8277ccc55965408cec9c33ee0cc811a6c294fac7b | 合成HTML设计；非原生验收 |
| review-viewer-320x568.png | UI-001/review-viewer | 320×568 | 1x | b569f42142e61ff2b4dc89371d33e6e810d7585cba918c62b658fd1a2155e35a | 合成HTML设计；非原生验收 |
| review-source-320x568.png | UI-001/review-source | 320×568 | 1x | 7ceb2053fe3573ddfac22cad1e8264aa1a4866ed86f6bf34e7ae5ae0ce899f67 | 合成HTML设计；非原生验收 |
| review-long-320x568.png | UI-001/review-long | 320×568 | 1x | c86d2e78e680af89727b7d309c78bf4d4a0b54b26b1e5572a9da842de8758ca8 | 合成HTML设计；非原生验收 |
| review-error-320x568.png | UI-001/review-error | 320×568 | 1x | 18c4a52702764ac72f0f551ccb42cb773a8325ca4b33c813ea8b3de3df942adb | 合成HTML设计；非原生验收 |
| suggestion-320x568.png | UI-001/suggestion | 320×568 | 1x | 4e77b6a1e7fa5fec292b77224172eb7d9d689ed6df94a2841657e7c48b2ef4c2 | 合成HTML设计；非原生验收 |
| suggestion-edit-320x568.png | UI-001/suggestion-edit | 320×568 | 1x | b94b1088b3916bca44929dc7df85aa8c88d4437fb802d7e2892cedaa805aec46 | 合成HTML设计；非原生验收 |
| suggestion-deferred-320x568.png | UI-001/suggestion-deferred | 320×568 | 1x | 4da9858e9e591dbdcab44086f6ae25c64f975b311296710526ab59291b555a19 | 合成HTML设计；非原生验收 |
| suggestion-planned-320x568.png | UI-001/suggestion-planned | 320×568 | 1x | 4ffa146b443bd27bfbd8537b422a8e0d0021de88ab32ea679bc23444f640cbe1 | 合成HTML设计；非原生验收 |
| suggestion-partial-320x568.png | UI-001/suggestion-partial | 320×568 | 1x | 6949671dc72565c68c608064e23c657fab47348fe7a12ee21a0577ccfd13dea7 | 合成HTML设计；非原生验收 |
| suggestion-delete-320x568.png | UI-001/suggestion-delete | 320×568 | 1x | 529e6e790895382a14107fedaaa36e0c989cfdd676f4a1ce7b0b222891a5fd3c | 合成HTML设计；非原生验收 |
| suggestion-record-320x568.png | UI-001/suggestion-record | 320×568 | 1x | 8dd8ab35540647477c9457fde5b2d4825ce2b8d21f6dfba955304152a20d41f8 | 合成HTML设计；非原生验收 |
| suggestion-no-history-320x568.png | UI-001/suggestion-no-history | 320×568 | 1x | 5d77e38fc89049bdad59ca5ec603c268206d39ed616b0c459b76508f0be1c21c | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-320x568.png | UI-001/suggestion-missing-grade | 320×568 | 1x | 33ba5b6b445149efae93a8c4a669d8a6fadd04c64ba673f598751bce02c1be7d | 合成HTML设计；非原生验收 |
| suggestion-loading-320x568.png | UI-001/suggestion-loading | 320×568 | 1x | da2c20638b59e57de0b511400bdbb4494c50c19ca68164deca2bfd90976ccc19 | 合成HTML设计；非原生验收 |
| suggestion-error-320x568.png | UI-001/suggestion-error | 320×568 | 1x | 68f4d8acd4d134ecc4a60571281bf3d342f0ff40ca6ec5e48280fac0d12e07d4 | 合成HTML设计；非原生验收 |
| suggestion-viewer-320x568.png | UI-001/suggestion-viewer | 320×568 | 1x | 6ac9daf687b608454d418385cb3c014324c5ffbce60a8c67afcd4dbb9cf44363 | 合成HTML设计；非原生验收 |
| suggestion-stale-320x568.png | UI-001/suggestion-stale | 320×568 | 1x | 30225daf0d1f81c22b0dec3c66e409b64e58816d4b9266d23e1b24aa80b8d6b0 | 合成HTML设计；非原生验收 |
| suggestion-long-320x568.png | UI-001/suggestion-long | 320×568 | 1x | b5f2e12ca5c483b86082bcaa3e48cb272f35de77724b4c9452a135ec3a8f1ac0 | 合成HTML设计；非原生验收 |
| suggestion-keyboard-320x568.png | UI-001/suggestion-keyboard | 320×568 | 1x | d671b911581fe655ce4b11f1a342b9867a40bfbbd8c963f009283be9ecae3997 | 合成HTML设计；非原生验收 |
| suggestion-saved-320x568.png | UI-001/suggestion-saved | 320×568 | 1x | 769b238f118682f49b735322f0f62b518d3bed771a2c47a1eb3b20d898599f57 | 合成HTML设计；非原生验收 |
| suggestion-offline-320x568.png | UI-001/suggestion-offline | 320×568 | 1x | 7f9bb9ba58b4cf08d0ae440ae11c519223e1d5bc4a79e448f5f22e8c927152fb | 合成HTML设计；非原生验收 |
| review-due-390x844.png | UI-001/review-due | 390×844 | 1x | 68667b30740af5ffda7a1cb0dedbd545d1d1ab4cced2352a94666345c26126bd | 合成HTML设计；非原生验收 |
| review-early-390x844.png | UI-001/review-early | 390×844 | 1x | bb05654eec57f59b4730a9da2f1d16b7737fca21366e63b7663ddea1b6b8ffd6 | 合成HTML设计；非原生验收 |
| review-empty-390x844.png | UI-001/review-empty | 390×844 | 1x | 02cb69ffa4585283076bd5cdd8dccd11a06e391c7a0f989477d2400d13df6e12 | 合成HTML设计；非原生验收 |
| review-handled-390x844.png | UI-001/review-handled | 390×844 | 1x | 63da28f6c36328a5f736cdd58a5ca4ea8d2502bc0a90c3b5219c8cfe10d1a6ec | 合成HTML设计；非原生验收 |
| review-inventory-390x844.png | UI-001/review-inventory | 390×844 | 1x | 0c73a2471696d82b9cedbc8a71ed175e501de15669d244c245cf21f6dd383105 | 合成HTML设计；非原生验收 |
| review-viewer-390x844.png | UI-001/review-viewer | 390×844 | 1x | f6ec03a2e91dedd48851745303c84142f625bccde124b8033b731bca52f1f0c8 | 合成HTML设计；非原生验收 |
| review-source-390x844.png | UI-001/review-source | 390×844 | 1x | 4bd746c7a16d883c3bfee0c4bff0064f724bd8b26e2b45349057b8e302c3ed27 | 合成HTML设计；非原生验收 |
| review-long-390x844.png | UI-001/review-long | 390×844 | 1x | 9205ded6b881a29467a148de2f7720ba5abaa6dc7c4a893e4f91481362244e2f | 合成HTML设计；非原生验收 |
| review-error-390x844.png | UI-001/review-error | 390×844 | 1x | e6d35abe26ddb2bfa8f3d4a95e71dd1e34e32a8626d549758374dec181b29e7c | 合成HTML设计；非原生验收 |
| suggestion-390x844.png | UI-001/suggestion | 390×844 | 1x | 48fcf588ceff50a60236ffb0e67decc14a04462d901f18fc9f14ae53bf305eb5 | 合成HTML设计；非原生验收 |
| suggestion-edit-390x844.png | UI-001/suggestion-edit | 390×844 | 1x | 4d860875ef591cd37a295718b628efa808e7a788b445a1fb9335f63d020f9a4e | 合成HTML设计；非原生验收 |
| suggestion-deferred-390x844.png | UI-001/suggestion-deferred | 390×844 | 1x | 76f141589f4f1f20ec65ce097548bc360a25b596bece79fc3694107b869e688f | 合成HTML设计；非原生验收 |
| suggestion-planned-390x844.png | UI-001/suggestion-planned | 390×844 | 1x | 3c429931be63375886c0bfee45c4223b9c030b744761bf3e6bca5a7fb982e10e | 合成HTML设计；非原生验收 |
| suggestion-partial-390x844.png | UI-001/suggestion-partial | 390×844 | 1x | 57efb03600a04019d3f19aed3a256532c890de734f2996eb876896df111d270c | 合成HTML设计；非原生验收 |
| suggestion-delete-390x844.png | UI-001/suggestion-delete | 390×844 | 1x | f4c9f162409160f5e347c1223928b5e12e83fba2a69f812203a70895122d15c6 | 合成HTML设计；非原生验收 |
| suggestion-record-390x844.png | UI-001/suggestion-record | 390×844 | 1x | ab2b9e66f3c54e06af61eea0be8b4aa3b24de92b35eea8af1fc820f657f7973f | 合成HTML设计；非原生验收 |
| suggestion-no-history-390x844.png | UI-001/suggestion-no-history | 390×844 | 1x | 32afe72e979cccd6b9d5c0d4ab260197dbc5a479fadeb081c70c930a9ab0757d | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-390x844.png | UI-001/suggestion-missing-grade | 390×844 | 1x | 8633214b346fbe6966364b49ae2e304c9ca66bef41c7f24dfa6b2686fddaf55d | 合成HTML设计；非原生验收 |
| suggestion-loading-390x844.png | UI-001/suggestion-loading | 390×844 | 1x | a7196cc7e56b4226a7026d967c90c0d7a529dc75a00fe10a86fd9f913b1e9aaf | 合成HTML设计；非原生验收 |
| suggestion-error-390x844.png | UI-001/suggestion-error | 390×844 | 1x | fa6bb55925e2628cb4fc6eed9f51b724cf6ba9e02ba85999836d7b996dc632d2 | 合成HTML设计；非原生验收 |
| suggestion-viewer-390x844.png | UI-001/suggestion-viewer | 390×844 | 1x | 77afa7c8d1c9dfca4bfba0a4e7f6dab4e2d114aba12a0c68073af61499cf33d4 | 合成HTML设计；非原生验收 |
| suggestion-stale-390x844.png | UI-001/suggestion-stale | 390×844 | 1x | bf9e03dd1557bbf5a0ba2c233b8a32ba6a16eb8e6b0c6f49dea30ee0b0cf3ccc | 合成HTML设计；非原生验收 |
| suggestion-long-390x844.png | UI-001/suggestion-long | 390×844 | 1x | ddf682cb3139e846575d74c1fc485ad6baeb6e672a2ba674e247c9b980a2453d | 合成HTML设计；非原生验收 |
| suggestion-keyboard-390x844.png | UI-001/suggestion-keyboard | 390×844 | 1x | 3509335eacfd6318eed47ed2635dbd77327f455f6a17aac4bc2470e5a9b801af | 合成HTML设计；非原生验收 |
| suggestion-saved-390x844.png | UI-001/suggestion-saved | 390×844 | 1x | f1898a5857145fc31a4cec18ff664c1cbf2b33e0e2c057d718e0c7d3b7a9ff4c | 合成HTML设计；非原生验收 |
| suggestion-offline-390x844.png | UI-001/suggestion-offline | 390×844 | 1x | 57ab8a3e220ad89908cdea8127876434c964682f23b188b6a10d6ece322442ad | 合成HTML设计；非原生验收 |
| review-due-430x932.png | UI-001/review-due | 430×932 | 1x | 3ade1b615587f32b93ce2dd0429c732a490bbb83d8f7064ed7f060083d4d7313 | 合成HTML设计；非原生验收 |
| review-early-430x932.png | UI-001/review-early | 430×932 | 1x | e2bf879ab0cffea36ade9be731d502db2808e3617b0db93bbc0ef10a3abc5808 | 合成HTML设计；非原生验收 |
| review-empty-430x932.png | UI-001/review-empty | 430×932 | 1x | e2d68c96c64eeaba4507b6b203a8bdc90f6d0bee9b204cfa1f4a106e194f5cb8 | 合成HTML设计；非原生验收 |
| review-handled-430x932.png | UI-001/review-handled | 430×932 | 1x | 0ee27529e4d1613f8eafe57e84530c13686467c05ae4e38cc834ccc266c1a04a | 合成HTML设计；非原生验收 |
| review-inventory-430x932.png | UI-001/review-inventory | 430×932 | 1x | f6b788606c08e11d14daf54d402650aca8d22f7fd4942ce6f006278ecee60285 | 合成HTML设计；非原生验收 |
| review-viewer-430x932.png | UI-001/review-viewer | 430×932 | 1x | 913002f007d030a4e9e706314ad9ac8a3a6a8394dfd63a96708886dc40c2eca2 | 合成HTML设计；非原生验收 |
| review-source-430x932.png | UI-001/review-source | 430×932 | 1x | 3636fd056461c4bc1066575b63f1605fc70dc61a2989fac77abe140d86922558 | 合成HTML设计；非原生验收 |
| review-long-430x932.png | UI-001/review-long | 430×932 | 1x | 48501ac2f5305d5bf8540dd49212b79a628d1977c8dd7b6cfb5c5fc5d015190e | 合成HTML设计；非原生验收 |
| review-error-430x932.png | UI-001/review-error | 430×932 | 1x | b22fac610f0cf32a4c4551b14ca5720137a27fe50e22ba131f079bf66ed8ed60 | 合成HTML设计；非原生验收 |
| suggestion-430x932.png | UI-001/suggestion | 430×932 | 1x | 08ef988aaeb2c4830a3aa13daf8ba6ce95948607b3dcbd4fed6c273f7ceb5198 | 合成HTML设计；非原生验收 |
| suggestion-edit-430x932.png | UI-001/suggestion-edit | 430×932 | 1x | 534ca9edfab94a46eb525028b586b33dbbccc80f2807730107d5b3ac83175c3e | 合成HTML设计；非原生验收 |
| suggestion-deferred-430x932.png | UI-001/suggestion-deferred | 430×932 | 1x | 26daa8f4e6831e48d5665f98d419c1e948b482af8f1dd6c3350a58193fe105ca | 合成HTML设计；非原生验收 |
| suggestion-planned-430x932.png | UI-001/suggestion-planned | 430×932 | 1x | cf084841ccd806861ac8f04684420b1cf4410cc0ca4e0e07d4797e9b266ed051 | 合成HTML设计；非原生验收 |
| suggestion-partial-430x932.png | UI-001/suggestion-partial | 430×932 | 1x | 951b47875928597f85151f0cb32bf64d10c07bbbb3366cab9e03777c866e0a45 | 合成HTML设计；非原生验收 |
| suggestion-delete-430x932.png | UI-001/suggestion-delete | 430×932 | 1x | 309d0ac7faeabac8ade6f63f82bb96498182c9c65a8c5690110538442fe9fc02 | 合成HTML设计；非原生验收 |
| suggestion-record-430x932.png | UI-001/suggestion-record | 430×932 | 1x | 46ff7c816b7dd83eebdd6ae07799e09ed719b93bf9a9f99a8ac221c752da7348 | 合成HTML设计；非原生验收 |
| suggestion-no-history-430x932.png | UI-001/suggestion-no-history | 430×932 | 1x | c948c8e1908f0fb3ec6f63eca079ab49479a73f5432583b5c7f7544d3c41bee5 | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-430x932.png | UI-001/suggestion-missing-grade | 430×932 | 1x | b63211788baaaa4503c96b52cc26fa166e04c42ad7620545bc3a92514157861d | 合成HTML设计；非原生验收 |
| suggestion-loading-430x932.png | UI-001/suggestion-loading | 430×932 | 1x | d8c8aa08fd028b1389f8573e41816332f2e1669511cacc7d87b94a1380b329b1 | 合成HTML设计；非原生验收 |
| suggestion-error-430x932.png | UI-001/suggestion-error | 430×932 | 1x | 628a2e36f5eac609182fd374a01df8b2d1fee91f7ce0a476fd0499326040218f | 合成HTML设计；非原生验收 |
| suggestion-viewer-430x932.png | UI-001/suggestion-viewer | 430×932 | 1x | 2745624d55e1e64a1538968c5c9f63b39c8f777aeb24f1efda117e5e9529e768 | 合成HTML设计；非原生验收 |
| suggestion-stale-430x932.png | UI-001/suggestion-stale | 430×932 | 1x | f193d7e478ff76e4c189e7a357d22b6f9cc2cbc13e44a2de701d1bb8e1187f64 | 合成HTML设计；非原生验收 |
| suggestion-long-430x932.png | UI-001/suggestion-long | 430×932 | 1x | 8d0ad72e229eb9ce9a5bfd1c4e7fac0b63a112e97aaf9f6f4b6550afa2e7de4f | 合成HTML设计；非原生验收 |
| suggestion-keyboard-430x932.png | UI-001/suggestion-keyboard | 430×932 | 1x | 3847a041d8b4eee8e3a3cdfdf50cb42951de2160db56dde933ad9d7e333e3005 | 合成HTML设计；非原生验收 |
| suggestion-saved-430x932.png | UI-001/suggestion-saved | 430×932 | 1x | a723bcae6b1d5ff8ef0ab51104fc654115261c6eaf6634d038a05352152b4007 | 合成HTML设计；非原生验收 |
| suggestion-offline-430x932.png | UI-001/suggestion-offline | 430×932 | 1x | 14ce23d8cc05621528b4b85ee41b9c939b9ff8ebef7107b04e808990186eb308 | 合成HTML设计；非原生验收 |

## Gaps and follow-up

- HTML原型检查78份控件横向包含/44px/键盘操作区、8条点击转移与Tab焦点循环通过；Runtime异常0，见prototypes内render-report.json。
- 仅合成资料；未调用后端、模型或读取真实儿童数据。复习/建议的权限、并发与正式写入由Spec业务测试验证，不能由这些PNG证明。
- 原生三视口节点、字体放大、安全区、读屏、iOS/Android、业务/内容/合规与真实MySQL验收均NOT_RUN。
- 批准后冻结source/PNG/hash；本清单只补批准人/日期/明确原话，不改被批准的内容。可见差异需新DREV。

## Integrity checklist

- [x] Editable HTML及SHA已生成。
- [x] 78份PNG覆盖全部26态×3视口。
- [x] 仓库candidate validator返回DESIGN_EVIDENCE_VALID；链接/状态/索引检查通过，结果记录于两份Spec04。
- [x] 两份Spec04（含Architecture02/03）+Design01明确批准。
- [ ] 原生及真机验收（实现后执行）。

