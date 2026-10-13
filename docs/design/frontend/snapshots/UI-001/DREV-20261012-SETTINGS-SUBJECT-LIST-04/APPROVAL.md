# UI-001 设置科目统一列表候选设计

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-04
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/rejected/FEAT-001-SETTINGS-SUBJECT-LIST.md#SPEC-20261012-SETTINGS-SUBJECT-LIST-04
- Superseded by: DREV-20261013-SETTINGS-CONSISTENCY-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-430x932.svg
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-320x568.svg=ced1df9e18e63031d3e77345d765fbac4b837cb14ee66c4cdc5f547266cdcd79; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-390x844.svg=fa753cea25af49b6fb95610f60c61b2f772dfbca235be1c6a16a1e4eea988a54; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/content-430x932.svg=12480d5244ae7f63aabf5c1dd85fd1106dbfd448a50b437a52816d9fbfe3748c; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-320x568.svg=95462fcb19d52e09e6af6e2aaf89b63ab9743da78aa0f3ef8eb7a7bce3b5b806; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-390x844.svg=9f3cd23df7e5a8bb2c6a3026734d558007d17ebdc4566b213c70e5788def4312; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/unselected-430x932.svg=d455b91ca4e4092fe8fbff77c507082787b30d8f346c4e2ae94bb380f5703d7d; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-320x568.svg=cbe4c64b4e803239903ed3b5a93ad24c1839a5bad6a8b1df115751fa16386377; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-390x844.svg=8db43e26a0af39eb651eba2db1c18f95f831356d0ffbf74a8a11224575ea26a3; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/readonly-430x932.svg=bc1a47b13d678718604568c459a958b2c8473c9cbf8aabd756af699b570323e7; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-320x568.svg=b8e564310bbc98f146f827ef7f7be258a628546c1738a42a23bb122ce5201f40; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-390x844.svg=09b5eb42d3a2f7c8f8efd2f1207f49958bb6465082b1dfae3cef904e7e60069e; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/pending-430x932.svg=3cd2fe9b16eca7c69e7cbf5b1f639ce447b713babe62fdffb95e36711c827639; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-320x568.svg=03f284b5b639dc8c795ea5f9fc4237d3d004aeec1267e51b4532be0b87e6c87e; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-390x844.svg=51908ce627ac3ac95a811186b44e284464505ad3388240058ae45b6167e4c3e6; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/long-name-430x932.svg=083ef480c2fcd9b5e93c5cd6634326e0b8a4bab0225faa153d84debd9ae17ec7; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-320x568.svg=b8bfb505420833a2735161ec44f2b4d6e53c93c0b78b06781c6561e3d7a6cb71; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-390x844.svg=58cbc4f65f6377f456fac28df7712ee441d17553bb92bd6eb245ff019d017523; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-04/error-430x932.svg=6c9cdc2005ef5ddfdf4022321d2e949ef4a9da55441d6236039fc6f42ef48e76
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING — 等待用户确认具体 Spec + DREV

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| content-320x568.png | content | 320x568 | 1x | 1e6ac2df6ecc9e53c14432a4b7d48b37b69035127c84e168928699fe4de9fdb3 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| content-390x844.png | content | 390x844 | 1x | 750aa35ef16209c9b85a39515ab23cc466bf75bbc1a66345f8a503c6e29c41a7 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| content-430x932.png | content | 430x932 | 1x | 842bdfb76b54acbf5f524ae50e6858a274d83e85ff8aa9983c263f17adbd478b | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-320x568.png | unselected | 320x568 | 1x | 663199a5fd71a18a04012933b7e763260717e1846f981c0b83708f3bbde674e6 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-390x844.png | unselected | 390x844 | 1x | 7febf5361d9ffce5b4cb5688969018fec983418542f07be2f7de31e3da8addd1 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-430x932.png | unselected | 430x932 | 1x | e4c85d38cc923cb317d025e9a80e81717566e99f88dc50d288a77a56a8f7bbdf | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-320x568.png | readonly | 320x568 | 1x | 45f076fffe920bad3297aa3039ad5f8a4ebaee7959dc420eda967bb3ce7ef67a | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-390x844.png | readonly | 390x844 | 1x | eb6d1c7a423b4fecac1cb2705aab46d6667671c8aaea8dfc9ac321fc7ae7f271 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-430x932.png | readonly | 430x932 | 1x | 95ae1961f68d330921df179ee7967dac51d39ab794f45e9b960ba0c874cfb0a6 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-320x568.png | pending | 320x568 | 1x | 6c191f93497da95d9ac00b4776a17adffbbb94b2a173e5864734b775254a4cb9 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-390x844.png | pending | 390x844 | 1x | f9c472e3e5fc2b91d84e4e4dd9c86e36b1ddf50d58ff73230f486c3ee0080bbc | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-430x932.png | pending | 430x932 | 1x | ff1c6afd00f9ef5a386fbffc9f36440da8c96c8ec197c3b186bc2460a1a64407 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-320x568.png | long-name | 320x568 | 1x | 8d8d18f9515c65a2b7939ee803e46b0a534ff6f18aae8ac8fc4b5269a8e80e8f | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-390x844.png | long-name | 390x844 | 1x | d7eeeb3ce98c20007dc515df9b483ee43cec7e7e0c85c3e085f482462744b55d | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-430x932.png | long-name | 430x932 | 1x | 87a1ea3e4b47861513d2869f353f03ec52c0659f62fef2cac2802e2cd4c3f816 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-320x568.png | error | 320x568 | 1x | 06064c763ff08cef8bed97e0e91e03f829cd649fb0ea97ef5ea72f94525bc6b1 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-390x844.png | error | 390x844 | 1x | 33486cf7516d1869be8dd8c5decdbc41ca3400c5ee2493ad415a08dea3462a6e | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-430x932.png | error | 430x932 | 1x | 6173ffca3f0ef8d181e8ab59ceee2fa5d6ed9cbc75864028f2447d7ad80a4ada | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |

原生节点矩形、交互、iOS/Android NOT_RUN。此处为设计候选图，未修改生产代码。
