# UI-001 设置科目统一列表候选设计

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-03
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/rejected/FEAT-001-SETTINGS-SUBJECT-LIST.md#SPEC-20261012-SETTINGS-SUBJECT-LIST-03
- Superseded by: DREV-20261013-SETTINGS-CONSISTENCY-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-430x932.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-320x568.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-390x844.svg; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-430x932.svg
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-320x568.svg=33de30e096cea6c24d71e4b74863f42f823707784e8c8a702bb94f285e8591de; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-390x844.svg=e22e16fe961b4407fcc19c9418ac23ab529c7d1ebbe90ebeec992d0b206646b9; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/content-430x932.svg=b106ffef1ee5c77e5a31796ade1d0400c98c292083baa501c5cbc51696315cc1; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-320x568.svg=a8ca0ae4b73380dbd0f198369e6a1f312eaeca441d23804d9d7b8004203388cb; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-390x844.svg=68b67fd09cd6ff21f05fd41a5b807fa41e307a62e9c27a9aa2c52a73f071ce89; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/unselected-430x932.svg=7585f384ecd75f45485d093bebd3b43fdb01550e6e06bb0cc36c9125b842a065; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-320x568.svg=08e938740f70d13eb785ab4e4057d194482cb002a7b7e5c7b2e4d5dee54d272b; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-390x844.svg=4df3d94e48c225a54dfebf15ba925e223ed90208e4b4bad96e71c573bc35fb86; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/readonly-430x932.svg=99769ec0db6894405daa4a8d65dff7c6aba8d73a3a3651e90c70aa197adc4af0; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-320x568.svg=3fd4d3aa9e74e835a72a079cf92ba8ee1638470c4241c0c30f04b9e706481e1a; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-390x844.svg=17f978789d101511b385a55a00e401c03ba12d7f972f7c0f2b45873177af713e; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/pending-430x932.svg=b048ec4e70a0446fe4e11316b09b90bb72754c637cc8dd9992d35338e5dc0d7d; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-320x568.svg=3a1365c129578e4fbc9396a12e29f3b14c128cf5b404e48c127b43a1c87bd6ae; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-390x844.svg=37933284d25e5897d96e8ca5a24f00c9363d8c6b451ff25bd9b39bf614f0fdbe; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/long-name-430x932.svg=c036ca0a0b43556bdf3548f08d0c77d3761ffe63b6711eaaf1f8a0a7290be072; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-320x568.svg=dd6fcd2bba568ac5b04e074cf2e3efce6b7885ef2a66f7d3fd9ec6be758a0092; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-390x844.svg=0c57720c83141c6ee253e85fda7680da3aa14b3960aa7e2866fc207c0b823eb2; docs/design/frontend/prototypes/DREV-20261012-SETTINGS-SUBJECT-LIST-03/error-430x932.svg=4bbc64b2139b6657750bb4b7e6ce52489d9b853e6dbc340bd5bc759f03006d24
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING — 等待用户确认具体 Spec + DREV

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| content-320x568.png | content | 320x568 | 1x | 922e4947185470b1184f85afe420c60566eed8c5d5b9a6a73dc671ef030c9c9e | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| content-390x844.png | content | 390x844 | 1x | 59a66ae2643c0681fe72af8c311d9278cc18920173ae0f14d8acb95911edb7d2 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| content-430x932.png | content | 430x932 | 1x | 4c4238c4936a9c6c07537f641a5cebf36194dbec244f343a8011f7a379f30f2f | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-320x568.png | unselected | 320x568 | 1x | 397073c403d54443d65076cf48bb4c7e4b71ab1b44a1e33c64b07e9b4da8ac76 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-390x844.png | unselected | 390x844 | 1x | 22cfdf831284468bb9932cf5666821e6416d9af989320a2943488cab92c5c8c4 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| unselected-430x932.png | unselected | 430x932 | 1x | 721709013f897b619c83405a6a76f197711e0889d456845584ab4daaae62e8ec | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-320x568.png | readonly | 320x568 | 1x | dd0badc74e0028379d73acdbfc21f9cbc0399a764974715fe481070a2fbe8248 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-390x844.png | readonly | 390x844 | 1x | 880e96068c15102578819413988ba0d5130c163430937f9f5447adadd0af75d9 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| readonly-430x932.png | readonly | 430x932 | 1x | 5a3bf07d3a6a913d1b0947f2963e33dd8f2d9bd89dda9ed9139bd58b0a36f4ad | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-320x568.png | pending | 320x568 | 1x | 110130c0395b82d5f4324447e6b22595cd06e5b49d228d38148c48a708be048e | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-390x844.png | pending | 390x844 | 1x | a0797ad1ae38ccb6b9cd21b28aef774e1245c5eefbc7aa63cec2530d09b5a0ad | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| pending-430x932.png | pending | 430x932 | 1x | 2cef3c62b65e20674bf6e240e3f90bb5b78c13d6e97c58362209e768c8bc6a54 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-320x568.png | long-name | 320x568 | 1x | 7886db4224ce26080dfebb5b7df956c749f9e2564313728a880c759a82c376b5 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-390x844.png | long-name | 390x844 | 1x | fde9f7ade5a965fb05d870219028ccd6c280994e482972d56dc25d34162a42e4 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| long-name-430x932.png | long-name | 430x932 | 1x | 7ba4a5f2d0537560e3aa6f3e0fc71d312137e0be1f7839278ca072c478f450e7 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-320x568.png | error | 320x568 | 1x | 5c09cfa66cd13f4d820f4a2fe6ed17f2e3f40838b4237f36d494ea9706630691 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-390x844.png | error | 390x844 | 1x | b61023b35cbcbd65e470b3c54e84ce790e42a97dab2fd10eb419ba73d38def50 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |
| error-430x932.png | error | 430x932 | 1x | 703b6e0d8860f1970b1cee9c43641739bbe143a8a761f722ebd9681397fea0e6 | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |

原生节点矩形、交互、iOS/Android NOT_RUN。此处为设计候选图，未修改生产代码。
