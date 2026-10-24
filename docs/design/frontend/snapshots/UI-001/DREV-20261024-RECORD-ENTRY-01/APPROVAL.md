# UI-001 / UI-018 — DREV-20261024-RECORD-ENTRY-01

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261024-RECORD-ENTRY-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md#BUG-SPEC-20261024-RECORD-ENTRY-05
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-RECORD-ENTRY-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-RECORD-ENTRY-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-RECORD-ENTRY-01/index.html=c8c626ce7f9d0becf63817e21cc75f39eee235aa4790ec026d834d1bb3122987
- Prototype generated/updated at: 2026-10-24
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-24
- Approval evidence: 本聊天在Spec05及当前交互稿收尾后用户回复「可以」，唯一对应Spec05 + 本DREV01；本地实施/验证获批，上传/发布另行授权。
- Superseded by: [DREV-20261024-FOOTPRINTS-MINIMAL-01](../../../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)仅覆盖旅行重复身份标题、次要入口与设置内容/高度，Spec01+DREV01于2026-10-24获批；其余记录入口/孩子/范围/导入合同继续有效。旧源与导出冻结。

合成内容；仅设计验证，未修改业务源码，不代表原生/真机或生产实施验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| travel-320x568.png | UI-001/travel | 320×568 | 1x | 55c63ac09249da47e2e7b36219be2cf04e02ca19271bbfd61928e48eada02356 | HTML设计，非原生验收 |
| learning-320x568.png | UI-001/learning | 320×568 | 1x | 20689e786282fb9ea69c94c9a8f72a4ebeb4a442a98e33337a794505cface91f | HTML设计，非原生验收 |
| long-320x568.png | UI-001/long | 320×568 | 1x | 6b8acf7f146d74fca8e82bbb2bc5ea750bd3bc0f919657c2055e68a741b8aeb2 | HTML设计，非原生验收 |
| single-320x568.png | UI-001/single | 320×568 | 1x | 18f63cfec98589f9eb7d335720345853967bbf6f1856b757a139b849e7f7cb92 | HTML设计，非原生验收 |
| types-320x568.png | UI-001/types | 320×568 | 1x | 1db34fce1382f319c7b6ebdd1eff1c1b8c366712faa6ced2f855e3e2e6c28fa2 | HTML设计，非原生验收 |
| learning-types-320x568.png | UI-001/learning-types | 320×568 | 1x | 4899b1a173da59887f045da6fb1a9d6f84bcbd8a8e7e9d29f02a8f6618a6a7f6 | HTML设计，非原生验收 |
| long-types-320x568.png | UI-001/long-types | 320×568 | 1x | e61aeba4f989c0f14285ea29b357c8e05775e90d6b3ac052507fcdf856e4c3d1 | HTML设计，非原生验收 |
| today-320x568.png | UI-001/today | 320×568 | 1x | eaa328ada09e306f517992af68d722f6c1425793fd93435047d5462e8f66833a | HTML设计，非原生验收 |
| from-learning-320x568.png | UI-001/from-learning | 320×568 | 1x | 20689e786282fb9ea69c94c9a8f72a4ebeb4a442a98e33337a794505cface91f | HTML设计，非原生验收 |
| travel-bottom-320x568.png | UI-001/travel-bottom | 320×568 | 1x | 403d25db5a3de3d2dda7d6146f57d658d56191729da3a85ce5fbde9d934cfa3a | HTML设计，非原生验收 |
| travel-390x844.png | UI-001/travel | 390×844 | 1x | a6139019213ab375a0a10724a041ceb1c6d2a7cb38977da5a6ad3f80e4019672 | HTML设计，非原生验收 |
| learning-390x844.png | UI-001/learning | 390×844 | 1x | c0f715718679bb609331c13f1f6a9dea0fa350fb58750547ba7c342fc3571f72 | HTML设计，非原生验收 |
| long-390x844.png | UI-001/long | 390×844 | 1x | 3dcb9b3627997c36965bb000b5f32ec2cdd288914e7c0df68b9c8fb5f166143b | HTML设计，非原生验收 |
| single-390x844.png | UI-001/single | 390×844 | 1x | e0c1c6cbd849ca6d5a939237c54a2a72d7426e167d90c684e32b07851c14cd7f | HTML设计，非原生验收 |
| types-390x844.png | UI-001/types | 390×844 | 1x | e32abe99dbb11e14cee4c5d4cf6712bf207f456eb229bf1134738f35c8a4d586 | HTML设计，非原生验收 |
| learning-types-390x844.png | UI-001/learning-types | 390×844 | 1x | 4f206d7e22ec1efadf60d35d1448bf7e579c263ce4f952d30c5d65ffc44990ca | HTML设计，非原生验收 |
| long-types-390x844.png | UI-001/long-types | 390×844 | 1x | af695b3bd682ac6d2e1dd5bb16fbbe89f17b8d41785e8479eb54925b242bd6b7 | HTML设计，非原生验收 |
| today-390x844.png | UI-001/today | 390×844 | 1x | 2d1bc617b315c8689dec5d7743904f39f04a5fab7830a22995c6dc703687f8aa | HTML设计，非原生验收 |
| from-learning-390x844.png | UI-001/from-learning | 390×844 | 1x | 4ca7be62464798ebec09846188ca38b0b409fc2a61ac91458931aa7cce202e75 | HTML设计，非原生验收 |
| travel-bottom-390x844.png | UI-001/travel-bottom | 390×844 | 1x | a6139019213ab375a0a10724a041ceb1c6d2a7cb38977da5a6ad3f80e4019672 | HTML设计，非原生验收 |
| travel-430x932.png | UI-001/travel | 430×932 | 1x | ba74ee95a88f3341f37f802464108fe2ea508eabdaf2fa590394149cbe8b8298 | HTML设计，非原生验收 |
| learning-430x932.png | UI-001/learning | 430×932 | 1x | c972e01031b3a3416d6394bef9d376bc7c6476350b453b4d7351e22721093ca7 | HTML设计，非原生验收 |
| long-430x932.png | UI-001/long | 430×932 | 1x | 4093994cdd25b6b2cbea31b09ad4e1a6ba788e7815a60b4789afa8b7a67b68ec | HTML设计，非原生验收 |
| single-430x932.png | UI-001/single | 430×932 | 1x | 4e05ebc78693b1c5dee16d7c35ade85d139475e606faacadf3cf38be8fcdac94 | HTML设计，非原生验收 |
| types-430x932.png | UI-001/types | 430×932 | 1x | 3cd9682f92b83fce36113d811b523da7ab3bbce4fdc88bef9bd46a31f8c8ccb2 | HTML设计，非原生验收 |
| learning-types-430x932.png | UI-001/learning-types | 430×932 | 1x | a6dd86f4d6e0f333cb4351934e7dc7b8b18b28334fb097988c89ba25269a9764 | HTML设计，非原生验收 |
| long-types-430x932.png | UI-001/long-types | 430×932 | 1x | d07e9f39fe94a82ae0a0b102e7c2df585bbd0dafa19100ccb6b00dd08ff92a32 | HTML设计，非原生验收 |
| today-430x932.png | UI-001/today | 430×932 | 1x | 01d80f951b2ce34113176f202005dc3815cc7eb8d0342f79c814fa1e361aaee9 | HTML设计，非原生验收 |
| from-learning-430x932.png | UI-001/from-learning | 430×932 | 1x | 724bb32cb0845e575aef5a5f23ea5f751a94e7cc81c954a5659ce180ab9f75d6 | HTML设计，非原生验收 |
| travel-bottom-430x932.png | UI-001/travel-bottom | 430×932 | 1x | ba74ee95a88f3341f37f802464108fe2ea508eabdaf2fa590394149cbe8b8298 | HTML设计，非原生验收 |
