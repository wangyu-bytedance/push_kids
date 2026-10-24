# UI-001 — 学习建议弹层精简候选

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261024-TODAY-LEARNING-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md#SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/index.html=0215d1d3f1be2ad080ecf49156c33bedb044034c962703a225b8a865d5321d66
- Prototype generated/updated at: 2026-10-24
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-24
- Approval evidence: 用户针对明确列出本Task Spec01、DREV02和两条批注改动清单的审批问题（call_989b0367f519481a9dc9b890f5ae9f1b）回复「批准，按此实现」。本次仅补批准记录，HTML/84张PNG及SHA未变。
- Superseded by: DREV-20261024-TODAY-LEARNING-04（仅学习标题输入的20码点有效保存上限、字数与字段错误；用户于2026-10-24在call_39aaa3dd3cdf4a52b2bfc9c4d862ee58明确批准。其余弹层布局/操作及旧长标题完整显示继续有效。）

## Candidate scope

依据用户两条浏览器批注，删除建议弹层的口号式前置标题，具体学习标题与时间优先；一个全宽主确认、两个等宽次操作、一个全宽弱化暂缓。AI标识与实际学习确认边界保留。原型补齐既有提交中/审批失败，编辑保存返回建议。只包含合成资料，无真实儿童数据/模型/API请求。

DREV01的26态加提交中、审批失败，共28态×320/390/430三视口=84张。1x/DPR1；早复习early/long/viewer滚动220px，其余顶部；keyboard为210px设计占位。此清单已于2026-10-24获具体批准，不更改旧DREV01，也不代表原生验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| review-due-320x568.png | UI-001/review-due | 320×568 | 1x | aa72b04290725751973118a240b113973b8dd04d91b6c9bf4993ea01e1d0669d | 合成HTML设计；非原生验收 |
| review-early-320x568.png | UI-001/review-early | 320×568 | 1x | 52fac9be9718ea368da4cb19f5fd5a97c9f4bd12235f70db9c09dea5e86c55b9 | 合成HTML设计；非原生验收 |
| review-empty-320x568.png | UI-001/review-empty | 320×568 | 1x | 7577fda62d77804277cde0bd00e1f084c0d99c88d1e901b1781486c39091798b | 合成HTML设计；非原生验收 |
| review-handled-320x568.png | UI-001/review-handled | 320×568 | 1x | 8ae860e4e0ed894c9ac978837e3942359fd6049b18793fa8b26826a75e1f65be | 合成HTML设计；非原生验收 |
| review-inventory-320x568.png | UI-001/review-inventory | 320×568 | 1x | 8b69b212f3d8df84244f65c8277ccc55965408cec9c33ee0cc811a6c294fac7b | 合成HTML设计；非原生验收 |
| review-viewer-320x568.png | UI-001/review-viewer | 320×568 | 1x | b569f42142e61ff2b4dc89371d33e6e810d7585cba918c62b658fd1a2155e35a | 合成HTML设计；非原生验收 |
| review-source-320x568.png | UI-001/review-source | 320×568 | 1x | 7ceb2053fe3573ddfac22cad1e8264aa1a4866ed86f6bf34e7ae5ae0ce899f67 | 合成HTML设计；非原生验收 |
| review-long-320x568.png | UI-001/review-long | 320×568 | 1x | c86d2e78e680af89727b7d309c78bf4d4a0b54b26b1e5572a9da842de8758ca8 | 合成HTML设计；非原生验收 |
| review-error-320x568.png | UI-001/review-error | 320×568 | 1x | 18c4a52702764ac72f0f551ccb42cb773a8325ca4b33c813ea8b3de3df942adb | 合成HTML设计；非原生验收 |
| suggestion-320x568.png | UI-001/suggestion | 320×568 | 1x | b99bdd506b97a6bdd3fa030a926f9ab17c86eec7280993d21219c0cf25fc825f | 合成HTML设计；非原生验收 |
| suggestion-edit-320x568.png | UI-001/suggestion-edit | 320×568 | 1x | d8931014f20143c938dbf39781c70ee88019ba2994ed5e69a9076088301f21f2 | 合成HTML设计；非原生验收 |
| suggestion-deferred-320x568.png | UI-001/suggestion-deferred | 320×568 | 1x | a1d45a9027cfd206d8323786fe3d5b14125a0b8078823247acc64d4840470dfe | 合成HTML设计；非原生验收 |
| suggestion-planned-320x568.png | UI-001/suggestion-planned | 320×568 | 1x | 4ffa146b443bd27bfbd8537b422a8e0d0021de88ab32ea679bc23444f640cbe1 | 合成HTML设计；非原生验收 |
| suggestion-partial-320x568.png | UI-001/suggestion-partial | 320×568 | 1x | 6949671dc72565c68c608064e23c657fab47348fe7a12ee21a0577ccfd13dea7 | 合成HTML设计；非原生验收 |
| suggestion-delete-320x568.png | UI-001/suggestion-delete | 320×568 | 1x | 529e6e790895382a14107fedaaa36e0c989cfdd676f4a1ce7b0b222891a5fd3c | 合成HTML设计；非原生验收 |
| suggestion-record-320x568.png | UI-001/suggestion-record | 320×568 | 1x | 8dd8ab35540647477c9457fde5b2d4825ce2b8d21f6dfba955304152a20d41f8 | 合成HTML设计；非原生验收 |
| suggestion-no-history-320x568.png | UI-001/suggestion-no-history | 320×568 | 1x | 5d77e38fc89049bdad59ca5ec603c268206d39ed616b0c459b76508f0be1c21c | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-320x568.png | UI-001/suggestion-missing-grade | 320×568 | 1x | 33ba5b6b445149efae93a8c4a669d8a6fadd04c64ba673f598751bce02c1be7d | 合成HTML设计；非原生验收 |
| suggestion-loading-320x568.png | UI-001/suggestion-loading | 320×568 | 1x | da2c20638b59e57de0b511400bdbb4494c50c19ca68164deca2bfd90976ccc19 | 合成HTML设计；非原生验收 |
| suggestion-error-320x568.png | UI-001/suggestion-error | 320×568 | 1x | 68f4d8acd4d134ecc4a60571281bf3d342f0ff40ca6ec5e48280fac0d12e07d4 | 合成HTML设计；非原生验收 |
| suggestion-viewer-320x568.png | UI-001/suggestion-viewer | 320×568 | 1x | 6ac9daf687b608454d418385cb3c014324c5ffbce60a8c67afcd4dbb9cf44363 | 合成HTML设计；非原生验收 |
| suggestion-stale-320x568.png | UI-001/suggestion-stale | 320×568 | 1x | b7b2763dc6ded50b96f07fd9f18bb2cbb7765c0fe8d760209f3fefe3118536cf | 合成HTML设计；非原生验收 |
| suggestion-long-320x568.png | UI-001/suggestion-long | 320×568 | 1x | 5a9b85ece17f45012f37f4e56774ca37c7b95b3c621c44eb94664a4487edb19b | 合成HTML设计；非原生验收 |
| suggestion-keyboard-320x568.png | UI-001/suggestion-keyboard | 320×568 | 1x | d671b911581fe655ce4b11f1a342b9867a40bfbbd8c963f009283be9ecae3997 | 合成HTML设计；非原生验收 |
| suggestion-saved-320x568.png | UI-001/suggestion-saved | 320×568 | 1x | 769b238f118682f49b735322f0f62b518d3bed771a2c47a1eb3b20d898599f57 | 合成HTML设计；非原生验收 |
| suggestion-offline-320x568.png | UI-001/suggestion-offline | 320×568 | 1x | 7f9bb9ba58b4cf08d0ae440ae11c519223e1d5bc4a79e448f5f22e8c927152fb | 合成HTML设计；非原生验收 |
| suggestion-saving-320x568.png | UI-001/suggestion-saving | 320×568 | 1x | ef83ab5d5d0a547aec9897a20a8b3453a15d0627c4395d17d893a5c5731390cc | 合成HTML设计；非原生验收 |
| suggestion-approve-error-320x568.png | UI-001/suggestion-approve-error | 320×568 | 1x | 8657411adf263b2d43856588e1cdaba8f74e0bb49adda5b98ee6af047c5d8b03 | 合成HTML设计；非原生验收 |
| review-due-390x844.png | UI-001/review-due | 390×844 | 1x | 4dbac9ac9e58fa5927f14bf8f9a00664501f47283f0b6b6ce2bad0c34722b38f | 合成HTML设计；非原生验收 |
| review-early-390x844.png | UI-001/review-early | 390×844 | 1x | bb05654eec57f59b4730a9da2f1d16b7737fca21366e63b7663ddea1b6b8ffd6 | 合成HTML设计；非原生验收 |
| review-empty-390x844.png | UI-001/review-empty | 390×844 | 1x | 02cb69ffa4585283076bd5cdd8dccd11a06e391c7a0f989477d2400d13df6e12 | 合成HTML设计；非原生验收 |
| review-handled-390x844.png | UI-001/review-handled | 390×844 | 1x | 63da28f6c36328a5f736cdd58a5ca4ea8d2502bc0a90c3b5219c8cfe10d1a6ec | 合成HTML设计；非原生验收 |
| review-inventory-390x844.png | UI-001/review-inventory | 390×844 | 1x | 0c73a2471696d82b9cedbc8a71ed175e501de15669d244c245cf21f6dd383105 | 合成HTML设计；非原生验收 |
| review-viewer-390x844.png | UI-001/review-viewer | 390×844 | 1x | f6ec03a2e91dedd48851745303c84142f625bccde124b8033b731bca52f1f0c8 | 合成HTML设计；非原生验收 |
| review-source-390x844.png | UI-001/review-source | 390×844 | 1x | 4bd746c7a16d883c3bfee0c4bff0064f724bd8b26e2b45349057b8e302c3ed27 | 合成HTML设计；非原生验收 |
| review-long-390x844.png | UI-001/review-long | 390×844 | 1x | 9205ded6b881a29467a148de2f7720ba5abaa6dc7c4a893e4f91481362244e2f | 合成HTML设计；非原生验收 |
| review-error-390x844.png | UI-001/review-error | 390×844 | 1x | e6d35abe26ddb2bfa8f3d4a95e71dd1e34e32a8626d549758374dec181b29e7c | 合成HTML设计；非原生验收 |
| suggestion-390x844.png | UI-001/suggestion | 390×844 | 1x | 2495402ce846f0f9326a5040014ad4616de1ce5ebfa816df5626c4ef8e23e670 | 合成HTML设计；非原生验收 |
| suggestion-edit-390x844.png | UI-001/suggestion-edit | 390×844 | 1x | da329dcdcd17cc0022cf8b62f065a8feb7d74d02e8b4ea5757ef295558f454f3 | 合成HTML设计；非原生验收 |
| suggestion-deferred-390x844.png | UI-001/suggestion-deferred | 390×844 | 1x | 286d185ab301d63aa85eae4b04ca1195641ffd482e0c6288cfb7031efe4bdfe5 | 合成HTML设计；非原生验收 |
| suggestion-planned-390x844.png | UI-001/suggestion-planned | 390×844 | 1x | 3c429931be63375886c0bfee45c4223b9c030b744761bf3e6bca5a7fb982e10e | 合成HTML设计；非原生验收 |
| suggestion-partial-390x844.png | UI-001/suggestion-partial | 390×844 | 1x | 57efb03600a04019d3f19aed3a256532c890de734f2996eb876896df111d270c | 合成HTML设计；非原生验收 |
| suggestion-delete-390x844.png | UI-001/suggestion-delete | 390×844 | 1x | 467a23a2357d12b18257c5690fd7e692b82162f607ff9b2f2b4136b273e798e7 | 合成HTML设计；非原生验收 |
| suggestion-record-390x844.png | UI-001/suggestion-record | 390×844 | 1x | deda58d40f168a1de99685dd989731f30f838abd7e28188886c7a814747adc05 | 合成HTML设计；非原生验收 |
| suggestion-no-history-390x844.png | UI-001/suggestion-no-history | 390×844 | 1x | 32afe72e979cccd6b9d5c0d4ab260197dbc5a479fadeb081c70c930a9ab0757d | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-390x844.png | UI-001/suggestion-missing-grade | 390×844 | 1x | 21deb522e76c3d71958367c95ca949f67e7d7b1a8ec3af43c4a3c0ff532875b3 | 合成HTML设计；非原生验收 |
| suggestion-loading-390x844.png | UI-001/suggestion-loading | 390×844 | 1x | 2826d274af9e12863b911bea8419ff962cacd5f89424cd4f0d0ee0e910e5d244 | 合成HTML设计；非原生验收 |
| suggestion-error-390x844.png | UI-001/suggestion-error | 390×844 | 1x | 23e33f0e0c670596aad7109bd8e7bac879be2168c8b62e497d513ba39175f931 | 合成HTML设计；非原生验收 |
| suggestion-viewer-390x844.png | UI-001/suggestion-viewer | 390×844 | 1x | 77afa7c8d1c9dfca4bfba0a4e7f6dab4e2d114aba12a0c68073af61499cf33d4 | 合成HTML设计；非原生验收 |
| suggestion-stale-390x844.png | UI-001/suggestion-stale | 390×844 | 1x | 33ce7ae7754bd82465aeacb067111d9e483baafd042044ad49325d3f10a329ba | 合成HTML设计；非原生验收 |
| suggestion-long-390x844.png | UI-001/suggestion-long | 390×844 | 1x | 6a088df1ed2ea6943d00667972824a66b13102df263fc0a75288ef974e3b08db | 合成HTML设计；非原生验收 |
| suggestion-keyboard-390x844.png | UI-001/suggestion-keyboard | 390×844 | 1x | 3509335eacfd6318eed47ed2635dbd77327f455f6a17aac4bc2470e5a9b801af | 合成HTML设计；非原生验收 |
| suggestion-saved-390x844.png | UI-001/suggestion-saved | 390×844 | 1x | f1898a5857145fc31a4cec18ff664c1cbf2b33e0e2c057d718e0c7d3b7a9ff4c | 合成HTML设计；非原生验收 |
| suggestion-offline-390x844.png | UI-001/suggestion-offline | 390×844 | 1x | 9bea1c6ed82a83d6dee289949df7476ad99db961714e46032db58e4949e3d526 | 合成HTML设计；非原生验收 |
| suggestion-saving-390x844.png | UI-001/suggestion-saving | 390×844 | 1x | b17ce829749ad92e39c3e00fc73bc009be242ebf6a2d27668462868f2f0f1f03 | 合成HTML设计；非原生验收 |
| suggestion-approve-error-390x844.png | UI-001/suggestion-approve-error | 390×844 | 1x | 89beae2df9f3a8b47a88bc478f7be82f61d4690f56252e0c68fc96e3eb4704c6 | 合成HTML设计；非原生验收 |
| review-due-430x932.png | UI-001/review-due | 430×932 | 1x | d0080a1a3a29a280ebe69be55da8c25600ed32a3ffa65c398e6e114ae790fa0d | 合成HTML设计；非原生验收 |
| review-early-430x932.png | UI-001/review-early | 430×932 | 1x | e2bf879ab0cffea36ade9be731d502db2808e3617b0db93bbc0ef10a3abc5808 | 合成HTML设计；非原生验收 |
| review-empty-430x932.png | UI-001/review-empty | 430×932 | 1x | e2d68c96c64eeaba4507b6b203a8bdc90f6d0bee9b204cfa1f4a106e194f5cb8 | 合成HTML设计；非原生验收 |
| review-handled-430x932.png | UI-001/review-handled | 430×932 | 1x | 0ee27529e4d1613f8eafe57e84530c13686467c05ae4e38cc834ccc266c1a04a | 合成HTML设计；非原生验收 |
| review-inventory-430x932.png | UI-001/review-inventory | 430×932 | 1x | f6b788606c08e11d14daf54d402650aca8d22f7fd4942ce6f006278ecee60285 | 合成HTML设计；非原生验收 |
| review-viewer-430x932.png | UI-001/review-viewer | 430×932 | 1x | 913002f007d030a4e9e706314ad9ac8a3a6a8394dfd63a96708886dc40c2eca2 | 合成HTML设计；非原生验收 |
| review-source-430x932.png | UI-001/review-source | 430×932 | 1x | 806a11a98b406c2e192b0c2e01553554a1ccd2667b4f250420f0c1ced77e7019 | 合成HTML设计；非原生验收 |
| review-long-430x932.png | UI-001/review-long | 430×932 | 1x | 48501ac2f5305d5bf8540dd49212b79a628d1977c8dd7b6cfb5c5fc5d015190e | 合成HTML设计；非原生验收 |
| review-error-430x932.png | UI-001/review-error | 430×932 | 1x | b22fac610f0cf32a4c4551b14ca5720137a27fe50e22ba131f079bf66ed8ed60 | 合成HTML设计；非原生验收 |
| suggestion-430x932.png | UI-001/suggestion | 430×932 | 1x | 50392abdd6c0ee82c91df3adc93ffc26b424eceeb6fc88035e03460d07977b07 | 合成HTML设计；非原生验收 |
| suggestion-edit-430x932.png | UI-001/suggestion-edit | 430×932 | 1x | 76f74ad2e032bf534d3e01a0850d1f8a165e27376afb82aa2406b1f8f9cbc248 | 合成HTML设计；非原生验收 |
| suggestion-deferred-430x932.png | UI-001/suggestion-deferred | 430×932 | 1x | 3ff0a127f016cd85db4254f95e53a348db551e5dfea22828fa9d73338a520682 | 合成HTML设计；非原生验收 |
| suggestion-planned-430x932.png | UI-001/suggestion-planned | 430×932 | 1x | cf084841ccd806861ac8f04684420b1cf4410cc0ca4e0e07d4797e9b266ed051 | 合成HTML设计；非原生验收 |
| suggestion-partial-430x932.png | UI-001/suggestion-partial | 430×932 | 1x | 951b47875928597f85151f0cb32bf64d10c07bbbb3366cab9e03777c866e0a45 | 合成HTML设计；非原生验收 |
| suggestion-delete-430x932.png | UI-001/suggestion-delete | 430×932 | 1x | 309d0ac7faeabac8ade6f63f82bb96498182c9c65a8c5690110538442fe9fc02 | 合成HTML设计；非原生验收 |
| suggestion-record-430x932.png | UI-001/suggestion-record | 430×932 | 1x | 46ff7c816b7dd83eebdd6ae07799e09ed719b93bf9a9f99a8ac221c752da7348 | 合成HTML设计；非原生验收 |
| suggestion-no-history-430x932.png | UI-001/suggestion-no-history | 430×932 | 1x | c948c8e1908f0fb3ec6f63eca079ab49479a73f5432583b5c7f7544d3c41bee5 | 合成HTML设计；非原生验收 |
| suggestion-missing-grade-430x932.png | UI-001/suggestion-missing-grade | 430×932 | 1x | 0d8188a675a99667e3750f51d82c8180c5ef3b548fe7e3b26dcc080617cdf6fe | 合成HTML设计；非原生验收 |
| suggestion-loading-430x932.png | UI-001/suggestion-loading | 430×932 | 1x | d8c8aa08fd028b1389f8573e41816332f2e1669511cacc7d87b94a1380b329b1 | 合成HTML设计；非原生验收 |
| suggestion-error-430x932.png | UI-001/suggestion-error | 430×932 | 1x | 628a2e36f5eac609182fd374a01df8b2d1fee91f7ce0a476fd0499326040218f | 合成HTML设计；非原生验收 |
| suggestion-viewer-430x932.png | UI-001/suggestion-viewer | 430×932 | 1x | 2745624d55e1e64a1538968c5c9f63b39c8f777aeb24f1efda117e5e9529e768 | 合成HTML设计；非原生验收 |
| suggestion-stale-430x932.png | UI-001/suggestion-stale | 430×932 | 1x | d66e56be2831f421524cf337b3b4bc849486441b9ba34e8e0c3d429fdabf38ce | 合成HTML设计；非原生验收 |
| suggestion-long-430x932.png | UI-001/suggestion-long | 430×932 | 1x | d4c0e0e06a94914167205213b687f40b3e1d92258df0802a62b5e8e5d7480bef | 合成HTML设计；非原生验收 |
| suggestion-keyboard-430x932.png | UI-001/suggestion-keyboard | 430×932 | 1x | 3847a041d8b4eee8e3a3cdfdf50cb42951de2160db56dde933ad9d7e333e3005 | 合成HTML设计；非原生验收 |
| suggestion-saved-430x932.png | UI-001/suggestion-saved | 430×932 | 1x | a723bcae6b1d5ff8ef0ab51104fc654115261c6eaf6634d038a05352152b4007 | 合成HTML设计；非原生验收 |
| suggestion-offline-430x932.png | UI-001/suggestion-offline | 430×932 | 1x | 61ca7285e6efdfb102805e029bd77d6a2dbb07d7a2155004f97ad2463757ec74 | 合成HTML设计；非原生验收 |
| suggestion-saving-430x932.png | UI-001/suggestion-saving | 430×932 | 1x | 2d9583c8d23c2dc6c25f3637ca0dbdc9806642c462cdf30de044fda785857b68 | 合成HTML设计；非原生验收 |
| suggestion-approve-error-430x932.png | UI-001/suggestion-approve-error | 430×932 | 1x | 80908fc87bf9945d70a1ea4fba839d0fbdec5f0222370eb6eb6f303d25859ad0 | 合成HTML设计；非原生验收 |

## Gaps and follow-up

- Chrome/155.0.8059.85隔离headless渲染；84张的横向包含、44px控件、8px两列间隔/等宽、正文可滚动空间、底部操作区检查PASS。
- 12条原型点击转移、提交中禁用、Tab循环、Escape等待保护与关闭后焦点恢复PASS；Runtime异常0。
- 原生三视口/真机/读屏/字体/安全区NOT_RUN；业务代码尚未应用此设计，旧实现的自动化不代验本修订。
- 本具体Task Spec01与DREV02已于2026-10-24获批；旧DREV01保持冻结。本次只补批准记录，source/PNG/SHA冻结。

## Integrity checklist

- [x] 自包含HTML和84份PNG及SHA已生成。
- [x] 三视口原型几何与关键交互已执行。
- [x] Task Spec01 / DREV02明确批准（2026-10-24）。
- [ ] 业务组件应用、自动化与原生/真机验收。

