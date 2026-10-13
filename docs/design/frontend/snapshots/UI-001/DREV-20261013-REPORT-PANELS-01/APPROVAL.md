# UI-001 — DREV-20261013-REPORT-PANELS-01 Approval Snapshot

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261013-REPORT-PANELS-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-001-REPORT-PANELS-REFINEMENT.md#SPEC-20261013-REPORT-PANELS-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261013-REPORT-PANELS-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261013-REPORT-PANELS-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261013-REPORT-PANELS-01/index.html=659c5aef1fa87ed2e2f6e82b1efa7c46dc71e3a6707650ac78f6dfc9fca6398a
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-13
- Approval evidence: 用户审阅效果图后回复“可以 这个方案可行”，批准 SPEC-20261013-REPORT-PANELS-01 + DREV-20261013-REPORT-PANELS-01；同时明确不影响并行每个card背景优化。
- Superseded by: N/A

## Approved scope

报表历史与编辑计划内部布局、独立展开/首尾收起、日期分隔行、筛选与明确的调整入口。外层card背景/材质/装饰交由并行任务，本任务沿用统一pk-card样式。数据、API与领域政策保持原合同。截图为合成示例；HTML提示交互不调用真实API。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| both-320x568.png | both | 320x568 | 1x | e037fe01bdf5dc2da37aebf71eb389b87720d3b26c0486c895a27350a0880880 | 合成数据，浏览器设计导出 |
| both-390x844.png | both | 390x844 | 1x | 404409f75d73def7e9d3d9d289000d0992cbedb1c9bd56ac4d1d336841668b11 | 合成数据，浏览器设计导出 |
| both-430x932.png | both | 430x932 | 1x | dc2232d805ad2dfc55b93244701d6b7dccf3566c3887ba7826dceb83f304270f | 合成数据，浏览器设计导出 |
| collapsed-320x568.png | collapsed | 320x568 | 1x | f9249a7e4647dac7e4da08dca6d349f67be10c67d6676634b6fe85e463cb6c5a | 合成数据，浏览器设计导出 |
| collapsed-390x844.png | collapsed | 390x844 | 1x | d3fbdca58cf137d73fc11861793846976c73e81fd2ffdcc7addb830876f6d639 | 合成数据，浏览器设计导出 |
| collapsed-430x932.png | collapsed | 430x932 | 1x | 324d0f2325737018a62afbf24361ea37e2a020bf8ffb24eb9b77d193516dcaef | 合成数据，浏览器设计导出 |
| history-320x568.png | history | 320x568 | 1x | e037fe01bdf5dc2da37aebf71eb389b87720d3b26c0486c895a27350a0880880 | 合成数据，浏览器设计导出 |
| history-390x844.png | history | 390x844 | 1x | 404409f75d73def7e9d3d9d289000d0992cbedb1c9bd56ac4d1d336841668b11 | 合成数据，浏览器设计导出 |
| history-430x932.png | history | 430x932 | 1x | 2f26bee3b6064b5769b20032fb74e8b36746edc331440c26d5b380761f8ff53a | 合成数据，浏览器设计导出 |
| menu-320x568.png | menu | 320x568 | 1x | 0e80ff7f3dedbd626c38ac193f3c5635dc31628bd411de36037ce472e0abcd7f | 合成数据，浏览器设计导出 |
| menu-390x844.png | menu | 390x844 | 1x | c0a971c5e6fed6647bacc4882a6d6eede61a593f882b79dcc959cd0db8f1311d | 合成数据，浏览器设计导出 |
| menu-430x932.png | menu | 430x932 | 1x | 29195bfcf46114d7e7175581b026c48589991abd752ee317ea6bf0a48bfc7125 | 合成数据，浏览器设计导出 |
| plan-320x568.png | plan | 320x568 | 1x | 7f9ab9e0e1e761d5d36e527a4baa7d59b775eedc82ef419e2e95e6744363b594 | 合成数据，浏览器设计导出 |
| plan-390x844.png | plan | 390x844 | 1x | 27941f0def47fe6d43b0b332126488a8d46c1d76b027a005ea53a3897aa12312 | 合成数据，浏览器设计导出 |
| plan-430x932.png | plan | 430x932 | 1x | 03efc4990ad6b8e8215b4b04c8eae35d1a29e6b50fea12179e1bd2d266ad8644 | 合成数据，浏览器设计导出 |

## Supplemental full-page and overview hashes

- both-320x568-full.png: 8450a6323a8bae9d68f026e27c373accec5d753c19648ac1aec80b411baf4533
- both-390x844-full.png: fa67713165056aa120b35d4a681b0cc9c64595a7aa5b2e0746550608e9ebebba
- both-430x932-full.png: aef01b9cef747af7a5271bc2b4dd9a852b011222af927e97ee6daa608a20e6da
- collapsed-320x568-full.png: 30ce261655c94e6d454d7e1eb3b743ce390c20968297730ebaa3e71ff4e924c0
- collapsed-390x844-full.png: d3fbdca58cf137d73fc11861793846976c73e81fd2ffdcc7addb830876f6d639
- collapsed-430x932-full.png: 324d0f2325737018a62afbf24361ea37e2a020bf8ffb24eb9b77d193516dcaef
- history-320x568-full.png: 195c8cf2a5acdd616e95ace19dab9ae45f750c26de4f5f04f5d11539897ef39e
- history-390x844-full.png: 7a90305899360b6e7924ff3e8c57c795f54168b682233f5d30a2f3c09b774464
- history-430x932-full.png: 2a46743237e6edcb64d02d5e2d71d27a8ae5ad3cad614b09060512ddeb93c03f
- menu-320x568-full.png: 515c9a0e0fa740e589af493c4f564955336da2bf68df6b2ea87dd932f5a841b0
- menu-390x844-full.png: b1c784e7549c3f0f14b4f55ecb548764bf19b53d4627fc6db271cc7927011cb5
- menu-430x932-full.png: ccf785e8a52ea8457ab4f4e4583ed7e112cb695b9532e45071acb49eff9f7dec
- plan-320x568-full.png: a1ff1421d1858f4e665b87f14eff190e0aa8682e6a1189257cc7d8277eaebb0b
- plan-390x844-full.png: f5c4f7170758515b98effb825fbca508443ce1d80030ec6c7e7a718cf9c44f33
- plan-430x932-full.png: afd6a835d979a27cb918c7a1a1d49626b99d604d1bed7d63f85e0830457fb49a
- proposal-overview.png: b73a985afd898b9f8b20f65929b72cb85d600f9f780c6fadfed7a05b599e1260

## Verification and gaps at approval

15组浏览器视口/状态无横向溢出；3档首尾收起与aria-expanded演示检查通过。批准时原生实施与真机未运行；实施证据另行记录，不改写本批准清单。批准后只允许更新Superseded by。
