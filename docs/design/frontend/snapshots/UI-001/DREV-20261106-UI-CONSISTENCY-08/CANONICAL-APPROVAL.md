# DREV-20261106-UI-CONSISTENCY-08 — canonical approval index

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261106-UI-CONSISTENCY-08
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md / DESIGN-002-SPEC-08
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-08/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-08/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-08/index.html=1fa17ef66978d6c1a83e59b6d83517cc7d7e08cbea7d9206dc0756e3fb7a324b
- Approved by: 用户
- Approved at: 2026-11-06
- Approval evidence: 当前会话“好的 按照以上方案落地”，批准Spec08 / Architecture01 / DREV08并沿用DREV06五主题全界面方向。

本文件仅将冻结JSON源/导出清单及其后续批准转写为校验器所需字段；不修改原APPROVAL、manifest、设计源或截图，不追改早期等待评审状态。所有原source/export SHA逐项核验相同。
原始manifest SHA-256：`f10280f232920ee562d145ce101c47054448194d64452ad4aa8d41c3e5183c7d`。未带viewport的总览/拼版使用实际图片画布尺寸及1x；手机状态继续使用原viewport。

## Export manifest

| File | State | Viewport | Scale | SHA-256 |
|---|---|---|---|---|
| browser-915x904.png | all / browser-915x904 | 915x904 | 1x | bcbe6941c5abd3411cb729adf01ff69815d5b0cd923e1917c8b6828ea6dcaa80 |
| garden-closed-320x568.png | garden / settings-closed | 320x568 | 1x | 0b554f9b3b621c3251941420b884f118b399c9a6ee4eb952d19df93302023c9b |
| garden-closed-390x844.png | garden / settings-closed | 390x844 | 1x | 362edfe7a267eb40030968d6a382ad6fb7c441ae925babd037e73d0732e6f1a2 |
| garden-closed-430x932.png | garden / settings-closed | 430x932 | 1x | b08845031af6b784f715ecbed0271e993ecd04bad1748e87419681b5a00b5163 |
| garden-picker-320x568.png | garden / settings-picker | 320x568 | 1x | fd5c1993d33451d3f5d3f9c69fd63f41405d813728af89f56a34d93346dd39c8 |
| garden-picker-390x844.png | garden / settings-picker | 390x844 | 1x | 1950c9531f0e94a55d0ecbdf3ec3d6f77ddb87069baa8ea671774619ae07d2ab |
| garden-picker-430x932.png | garden / settings-picker | 430x932 | 1x | 60d53e8f801c2cedb4398af27ac5b7be9f82caa2cbb54dfdad68ecff4b6425a1 |
| garden-storage-error-320x568.png | garden / settings-storage-error | 320x568 | 1x | de100d823bee2f1af2a1e192fb64455339d215ab9db97b8b16ab625f4d5a0ff6 |
| garden-storage-error-390x844.png | garden / settings-storage-error | 390x844 | 1x | 9b27bd80be28a35ac531f74f9b998a8356a42055e512e945f73115a52828a3a1 |
| garden-storage-error-430x932.png | garden / settings-storage-error | 430x932 | 1x | e95db5ef8c9cc7c1f73b6d53666696857cedb57ebbf1d8199330440a603f0abf |
| midnight-closed-320x568.png | midnight / settings-closed | 320x568 | 1x | 68d92b3946607484c0619e487e00d5c444546c98a0acac060c2fe8816702a4c4 |
| midnight-closed-390x844.png | midnight / settings-closed | 390x844 | 1x | 47917fa4d6f113caf3527651185de397126e8c2eaae2f0792dc56b3e82b7a1b2 |
| midnight-closed-430x932.png | midnight / settings-closed | 430x932 | 1x | 78629959ce7bbf04b96ab849a0bbff18c82d2491e4cdbab14c51670ca0e0ec01 |
| midnight-picker-320x568.png | midnight / settings-picker | 320x568 | 1x | 4ffd8724234b6e40c3938f2c23afd8c7c0e86202cc34e7999d8d843bc04e7a0a |
| midnight-picker-390x844.png | midnight / settings-picker | 390x844 | 1x | 4388fe2d54e096da9e767fb3721dd1eab40ad249dece53f8ae65533e1bba3432 |
| midnight-picker-430x932.png | midnight / settings-picker | 430x932 | 1x | e618ebf0aa9fa2156ec8ba4da3573d74d0d09e72d4e45d97eacc5865382664fc |
| midnight-storage-error-320x568.png | midnight / settings-storage-error | 320x568 | 1x | 766649550c4b11f50770c360f6f525dc3c9583b595397700e36cc11fd0f957c3 |
| midnight-storage-error-390x844.png | midnight / settings-storage-error | 390x844 | 1x | 07a389b405a0350ede947bfd8bfb6e7fa7159e34d8a04ac7cdeca258d4b8a327 |
| midnight-storage-error-430x932.png | midnight / settings-storage-error | 430x932 | 1x | 0329817a8a8f2d12a12329e0b471c81e9b26f4dadaeedfc4d095b47a4b47df67 |
| ocean-closed-320x568.png | ocean / settings-closed | 320x568 | 1x | fd5e50f147cf3497ddd58848e32a9879cb2bc9fa6e2fe2814b34c94b246f2422 |
| ocean-closed-390x844.png | ocean / settings-closed | 390x844 | 1x | 4b43cb7879845824aaa86d3c3235fc9686613f8839d8c08df8837885d362d33a |
| ocean-closed-430x932.png | ocean / settings-closed | 430x932 | 1x | ef5fa3c7a18ac4e97dd5c2d99a6fdefc29c8405d321ad0210b641fbe1878e7f9 |
| ocean-picker-320x568.png | ocean / settings-picker | 320x568 | 1x | 1d0653ace4d6cc7ebad40f52930b06d022dad447de0461461b59abeed2b64d71 |
| ocean-picker-390x844.png | ocean / settings-picker | 390x844 | 1x | a453fa20f70f1a10791d1652ac6595ea1582e06327059ea7f99d2beab04ac187 |
| ocean-picker-430x932.png | ocean / settings-picker | 430x932 | 1x | f0ccbc2e31fe66fa0aa3c8f818c79ca5199005eaa5a23e082230ebd7bb6bce5d |
| ocean-storage-error-320x568.png | ocean / settings-storage-error | 320x568 | 1x | 14f51e94e6a50efcc77b9b6b59b7e67c388983025db5b989cdc9425c087a2133 |
| ocean-storage-error-390x844.png | ocean / settings-storage-error | 390x844 | 1x | f847f5a1e9b0db61a6b2aeb48a7f6c0e4888bed46436fe48e18f64682ecc544f |
| ocean-storage-error-430x932.png | ocean / settings-storage-error | 430x932 | 1x | 5095c3fdf1c5be07069bb0c249a6500cb5b8ba202a206d46cfbf9d4d4c90728c |
| original-closed-320x568.png | original / settings-closed | 320x568 | 1x | a0ef91edfb054de175cd1a2ab4aa54937c632a2bc168a34a06cc487125b731cf |
| original-closed-390x844.png | original / settings-closed | 390x844 | 1x | 2c094056d1fc5ab8db0e2e54c0c837e9fabf2f990cfbe6522e7cf034cf74fdee |
| original-closed-430x932.png | original / settings-closed | 430x932 | 1x | 62f3392355d3d0e975c47098f5006b531a4191f7b29ceb9382de791551c67766 |
| original-picker-320x568.png | original / settings-picker | 320x568 | 1x | 1fb3c6915abea1232afbbc465de6187c3d0fe01d239a84c842c06351d9030a7f |
| original-picker-390x844.png | original / settings-picker | 390x844 | 1x | 15b15c6d267d82a0c9696bf851f95cf31876afa28185d3947ccae6ce879d19dc |
| original-picker-430x932.png | original / settings-picker | 430x932 | 1x | 9f9a4f6f887a9203afa9220e14984631e87252841ebba49b6b0c141ba170bd62 |
| original-storage-error-320x568.png | original / settings-storage-error | 320x568 | 1x | 6aacf4e88e1f5a3c7a673daf22d1affce9ab209561f12afd131b76ede1ace3ea |
| original-storage-error-390x844.png | original / settings-storage-error | 390x844 | 1x | 2cfed83e194249daa91c0ae80904571d94dbb2619afbbc1da23381408b55ec77 |
| original-storage-error-430x932.png | original / settings-storage-error | 430x932 | 1x | c44d250a462b909f4ea4c867473691cfbaa950f0eca52f7c0bcf53dfee3ed955 |
| overview.png | all / overview | 1770x1434 | 1x | 8215f4cdfe08d8db5ec8b45c718f8f241b81fb1620acb928fd427ba0ab8ea75f |
| space-closed-320x568.png | space / settings-closed | 320x568 | 1x | 188b59232124b488faea070270cbbd3078aff317b626787a1e1d79dc53b7d1ec |
| space-closed-390x844.png | space / settings-closed | 390x844 | 1x | 5e9351ca51befb7e9c4235baeba390ba8b5d0841169c4d68e4ed47e2c1a66aa0 |
| space-closed-430x932.png | space / settings-closed | 430x932 | 1x | 56c96a07257b673bb84d705b6c885d657d06090ed88232ba5e90d02d18bf3eea |
| space-picker-320x568.png | space / settings-picker | 320x568 | 1x | bbdcf179e3debdc513e2eae4bb0550a9b6a9b7222b35a4041be284640a6af82c |
| space-picker-390x844.png | space / settings-picker | 390x844 | 1x | 1594128d655993321b4406e429331e2b4b794bd2c755936b999bfc4d980e9c31 |
| space-picker-430x932.png | space / settings-picker | 430x932 | 1x | ed04b26a256cf387d7e29204ed7e71fb4e20e74564823f074a213b0945616f6e |
| space-storage-error-320x568.png | space / settings-storage-error | 320x568 | 1x | e7a68e4af8d41edaf930dc9822b3c8b4a0379f09de1d322f5e3c0f87b9fc779a |
| space-storage-error-390x844.png | space / settings-storage-error | 390x844 | 1x | 23849978130cfb640ad78d990364a4dcc85b88b16ff9258a9e8dbbd44038c59f |
| space-storage-error-430x932.png | space / settings-storage-error | 430x932 | 1x | d815cc5e2e35df3c723dd71f623edf7aa76cf7ebf446bb4181680875dcdfe646 |
| tech-closed-320x568.png | tech / settings-closed | 320x568 | 1x | a999a9582a048db8efca1985b5809d91ee89427c7fcf6cc1aff6eeba1861fc52 |
| tech-closed-390x844.png | tech / settings-closed | 390x844 | 1x | 8b5d2d4bd9219c22a803165b77cb789980f2dc2da4df18c0cfab5f0921befa3d |
| tech-closed-430x932.png | tech / settings-closed | 430x932 | 1x | d6aa9c611beb0d21025d7781bf4b7f58454bc90a342f849a8923dba1c4a85541 |
| tech-picker-320x568.png | tech / settings-picker | 320x568 | 1x | 20843043e91341bd5f7733a385b4e9f22fc954589dfbbfc42fd4cac16d798de5 |
| tech-picker-390x844.png | tech / settings-picker | 390x844 | 1x | ffc1f8015c7f28cc64fb67de40f745324ba76cc15604d8cc7b13dd3ad777e3d1 |
| tech-picker-430x932.png | tech / settings-picker | 430x932 | 1x | 416db403a5f11a1df59ec084fc394c955dd83aebe57451a4788c41216afa617e |
| tech-storage-error-320x568.png | tech / settings-storage-error | 320x568 | 1x | a100514653f0915be7d1fb08b9ebe2e7eca1a9936fcf33cb6dbbea8c3ff3fe3d |
| tech-storage-error-390x844.png | tech / settings-storage-error | 390x844 | 1x | 12df7bc716a4d73963c3208c94dd8c48171cd03b8f7bf0c658f8ebb760dd3741 |
| tech-storage-error-430x932.png | tech / settings-storage-error | 430x932 | 1x | 40acc55d49c4c4ad8a90bcef50ac0ea1546806d2c5d13ebc5bb2156a171fb5c0 |
