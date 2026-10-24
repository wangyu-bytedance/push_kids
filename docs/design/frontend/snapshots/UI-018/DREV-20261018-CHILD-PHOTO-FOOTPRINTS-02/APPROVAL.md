# UI-018 — DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02 候选设计清单

- Status: APPROVED
- UI ID: UI-018
- Design Revision: DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md#SPEC-20261018-FOOTPRINTS-UI-COPY-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/index.html=8c35c870ec78b8fc0da535e1f50e3d3104ada55949bee92a18e796101da5d986
- Prototype generated/updated at: 2026-10-18
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-23
- Approval evidence: 用户审阅精简候选及标题入口方案后要求“完成这个功能的代码编写”，批准既定文案清单；入口另见SPEC-20261023-RECORD-TYPE-SWITCHER-01。源与导出哈希保持不变。
- Superseded by: [UI-018当前状态](../../../ui/UI-018-child-photo-footprints.md)及[2026-10-23实现证据](../../../../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)接管实施/验证状态；下方生成阶段“待批准/NOT_RUN”为历史语境，批准以本清单2026-10-23头部为准。入口由DREV-20261024-RECORD-ENTRY-01接管；[DREV-20261024-FOOTPRINTS-MINIMAL-01](../../../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)于2026-10-24获批，覆盖重复身份标题、次要入口及设置长文/高度，其余DREV02合同继续有效。冻结源与导出不变。

## Candidate scope

27个HTML状态，全部覆盖320×568、390×844、430×932。
合计81张手机PNG，另附1张桌面评审工作台。
照片、孩子、时间、地点均为虚构示例，照片用内嵌SVG插画占位。
地图仅为坐标点位示意，无真实底图、行政边界、道路、定位或地理检索服务。
完整候选交互和限制见FRONTEND-SPEC.md。批准后源与清单冻结，只能添加Superseded by。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| records-320x568.png | UI-018/records | 320×568 | 1x | 8539b4833188bb977800324b82c5fa7ae5885aae7cf6110eb323655d1645e62b | HTML设计；非原生验收 |
| records-390x844.png | UI-018/records | 390×844 | 1x | 37af3466fe2d33df8aba75e47fe186ba7ce32482da0dadfa51599fea9bb2dbf1 | HTML设计；非原生验收 |
| records-430x932.png | UI-018/records | 430×932 | 1x | 70ae393a4afdbaccc3f243d67e05a5d343a269a98dfb6d603cad734702a96762 | HTML设计；非原生验收 |
| timeline-320x568.png | UI-018/timeline | 320×568 | 1x | 5fbb11bb33c52ea65661336b8de87c2f7b8753aa4af2baf6bd1e23ac622c506e | HTML设计；非原生验收 |
| timeline-390x844.png | UI-018/timeline | 390×844 | 1x | 9cfb649070aa59143e2f0bedb8e791ab6bdb9b8a69cc570d7aac38de09ac6102 | HTML设计；非原生验收 |
| timeline-430x932.png | UI-018/timeline | 430×932 | 1x | 8bbaae2e3c02551f23bd452f6c5e2161ba6cb995d886bdf31c09ed5c094278cb | HTML设计；非原生验收 |
| empty-320x568.png | UI-018/empty | 320×568 | 1x | 4e1246714dff7bcafe31ba8737540b8809ce0da2fa0a01de09576c1d9ebd71fc | HTML设计；非原生验收 |
| empty-390x844.png | UI-018/empty | 390×844 | 1x | 71b5f5a64428b28388177f96290fa92c0074d0e0e16ffc15a402033c3a4511fb | HTML设计；非原生验收 |
| empty-430x932.png | UI-018/empty | 430×932 | 1x | 2668a1dd07ff97cc5938f45398440f90c890901a500b44fde827304e9bca2fce | HTML设计；非原生验收 |
| import-320x568.png | UI-018/import | 320×568 | 1x | c09512abd109409d0ecb5e2838dec7b39b195c1e239e042967210a126eb4aed4 | HTML设计；非原生验收 |
| import-390x844.png | UI-018/import | 390×844 | 1x | f9dcf5e7b37275884e8847b7213f11e6200488c46ff7006b8a8b42cef140ee25 | HTML设计；非原生验收 |
| import-430x932.png | UI-018/import | 430×932 | 1x | 1f697d84dfb1f1d538e614f1ddf61bb557df57889490ffda2ea4b35c40e6c3a6 | HTML设计；非原生验收 |
| consent-320x568.png | UI-018/consent | 320×568 | 1x | c6df47bbb85f83f6fe6a221ab8ecbb60c58a3c33492504b662e5ea42d8dbe81d | HTML设计；非原生验收 |
| consent-390x844.png | UI-018/consent | 390×844 | 1x | 7565651cefe44e531b3941e5989b2cc57b3bf64041bc5a45271a0b3b5aeedae8 | HTML设计；非原生验收 |
| consent-430x932.png | UI-018/consent | 430×932 | 1x | 39fd9354089c4de55f7b9f352fe8187d67d91f3d1d374041863488d6b7c74db9 | HTML设计；非原生验收 |
| importing-320x568.png | UI-018/importing | 320×568 | 1x | 7212b57fbe143de634f3ce8a8fc3ae811492dcf8d23809e8c42973d88cae813a | HTML设计；非原生验收 |
| importing-390x844.png | UI-018/importing | 390×844 | 1x | bfb783f9bfe0628d56f70c02e1d0aa5cb3ba2d768f195c305e03fe9a8c821597 | HTML设计；非原生验收 |
| importing-430x932.png | UI-018/importing | 430×932 | 1x | 053bbfc11fa5da211e6284a52b131688b011f5b34e4cafeba0f88b0f111379d0 | HTML设计；非原生验收 |
| review-320x568.png | UI-018/review | 320×568 | 1x | f2f474aa5f346ded80fbfc07af09bb03ca5ab0484ccdb0becd6ed076aee01cf0 | HTML设计；非原生验收 |
| review-390x844.png | UI-018/review | 390×844 | 1x | c2147becfc7711e170e37edf1e95cd4bd52ebfb8bd6e48d6becaef1931044f92 | HTML设计；非原生验收 |
| review-430x932.png | UI-018/review | 430×932 | 1x | 3fd8dd3af61f49543a830750cdb2c43387f403b59d7a8e704ac0cf41c85e35a0 | HTML设计；非原生验收 |
| batch-320x568.png | UI-018/batch | 320×568 | 1x | e572f55bc1bee1429a1752d588cd74252abc5aac16c1b3d4eeca54e920150fbf | HTML设计；非原生验收 |
| batch-390x844.png | UI-018/batch | 390×844 | 1x | 7a9a5f2ba8ac639c3f68288fb0967ee9d19dc07f5ecca268d03ea63ec806231b | HTML设计；非原生验收 |
| batch-430x932.png | UI-018/batch | 430×932 | 1x | 9e206e7f523a041c5f0425fdfd06aa12229e8acac5ff05a4a75bf3549d855c6e | HTML设计；非原生验收 |
| confirm-320x568.png | UI-018/confirm | 320×568 | 1x | 5e475ca98d2603b30313edf8684523d7eb27b0dd083d58a8eebf9f40c6bfca14 | HTML设计；非原生验收 |
| confirm-390x844.png | UI-018/confirm | 390×844 | 1x | d8c768d6af16470ca44e9f05d75283ee8a2165cc82d0a49960f63ffe2af3ce0f | HTML设计；非原生验收 |
| confirm-430x932.png | UI-018/confirm | 430×932 | 1x | c294b8fcf160b0019a824d56a2b61cc70a6ec99e7e572f7146ee0fe43cd77ca4 | HTML设计；非原生验收 |
| saved-320x568.png | UI-018/saved | 320×568 | 1x | 77276ac73b809312bafc3cfca344d904ed9d8a7097c99bced548f8424ea7e234 | HTML设计；非原生验收 |
| saved-390x844.png | UI-018/saved | 390×844 | 1x | af55e72192eae274583dcab17aad93ce0e787400cf0b3a9a3278a61ba3bc14f5 | HTML设计；非原生验收 |
| saved-430x932.png | UI-018/saved | 430×932 | 1x | 0fc7a379bff4ac52cf7069d4c17b084487011e02adff410effe026b1bd012a2b | HTML设计；非原生验收 |
| playback-320x568.png | UI-018/playback | 320×568 | 1x | ab93091fb785b5e7bdb9dd850b735a89f6d44a69e75c1d44917553e8df8ed2c4 | HTML设计；非原生验收 |
| playback-390x844.png | UI-018/playback | 390×844 | 1x | acf00f2ed67e3ff6c9caa5564bf56b0fca32ac7debedb7b1d02d5386343364d2 | HTML设计；非原生验收 |
| playback-430x932.png | UI-018/playback | 430×932 | 1x | 84e795acfe2129800fed4805bb209cf798befae316707b126cb1ff95e7be64ac | HTML设计；非原生验收 |
| paused-320x568.png | UI-018/paused | 320×568 | 1x | 2866b090c8bdb56e1d9ad1cf20bf5aff4e48fbacc8bf142b9a56851d8da5bf22 | HTML设计；非原生验收 |
| paused-390x844.png | UI-018/paused | 390×844 | 1x | 791468749c76f8c0558073121cf820452bfa2d88b04a56961d8c4f959dce4b6a | HTML设计；非原生验收 |
| paused-430x932.png | UI-018/paused | 430×932 | 1x | 4481a88d1ab75fed7e2d1edf97e46560419d60ff2a1719c9686f9038e2cc2252 | HTML设计；非原生验收 |
| lit-320x568.png | UI-018/lit | 320×568 | 1x | b2dd3109e5b8e7419125531b560264778468584a2f2c0afe5da97ed7fd90ab13 | HTML设计；非原生验收 |
| lit-390x844.png | UI-018/lit | 390×844 | 1x | 778d5135e3e280bfa6b7216672e6eaa6818bcae20bba14da5933727e33b56894 | HTML设计；非原生验收 |
| lit-430x932.png | UI-018/lit | 430×932 | 1x | ccd2a5ffaa379c1b794e3e9a9fc472bccd134102c66fd1c6405e6b03766cbfea | HTML设计；非原生验收 |
| world-320x568.png | UI-018/world | 320×568 | 1x | 78174868d0f2d767bbe4855a6fa04d7033d9617314792810b437bb45ae388df4 | HTML设计；非原生验收 |
| world-390x844.png | UI-018/world | 390×844 | 1x | 868e78d3a062304055c1cab37c038d5cc803e1e2ffd1a60931f187fb716c359b | HTML设计；非原生验收 |
| world-430x932.png | UI-018/world | 430×932 | 1x | c94b833f6542844a84c7ab0ac8868f5a02ed9c97652e62fdb40398673a69f223 | HTML设计；非原生验收 |
| place-320x568.png | UI-018/place | 320×568 | 1x | 7871f055e1b505b2cfdc90f7345edde2309855a7dddfebd66654c42c50c1e205 | HTML设计；非原生验收 |
| place-390x844.png | UI-018/place | 390×844 | 1x | 5c3c87c4fbd87430b0d03567235599c86c09a0ce90cbc70c312ed0824a3ac724 | HTML设计；非原生验收 |
| place-430x932.png | UI-018/place | 430×932 | 1x | 02e269ddba61e651222d17051edd1351cbf1cc0a042d3356b8baa2c2ee1f4e26 | HTML设计；非原生验收 |
| failed-320x568.png | UI-018/failed | 320×568 | 1x | 5196940dc40b733111b9dbbb7c927fa64a4c3be266e299502d2ff496304cf8ec | HTML设计；非原生验收 |
| failed-390x844.png | UI-018/failed | 390×844 | 1x | b227a8813ec2a0fb99a7ee8358caa370112115f32f8d960926d1bcdf8c6a7035 | HTML设计；非原生验收 |
| failed-430x932.png | UI-018/failed | 430×932 | 1x | eb37679e0cc83464a8fac4a51d6e4db9a49a759e41643f65f66e4077236b13c0 | HTML设计；非原生验收 |
| unknown-320x568.png | UI-018/unknown | 320×568 | 1x | fdbe0c4391a8d87c631ee5ad1ceaa8484aa62c26107adb6cfecfad8d56d7ba3e | HTML设计；非原生验收 |
| unknown-390x844.png | UI-018/unknown | 390×844 | 1x | a103f834cdfed9e6ff48ccc1bf53162baf4ead0002cadc67466daece2da968fa | HTML设计；非原生验收 |
| unknown-430x932.png | UI-018/unknown | 430×932 | 1x | 3fd8dd3af61f49543a830750cdb2c43387f403b59d7a8e704ac0cf41c85e35a0 | HTML设计；非原生验收 |
| denied-320x568.png | UI-018/denied | 320×568 | 1x | d4ce16f359eb9f226e9ce46d30605cb3907e3e5191b28444d59ed72e4f62e686 | HTML设计；非原生验收 |
| denied-390x844.png | UI-018/denied | 390×844 | 1x | ceb1c190177015c589dfdcee50fe7cb3eb91afd707f56e17facbe63542793455 | HTML设计；非原生验收 |
| denied-430x932.png | UI-018/denied | 430×932 | 1x | 17e9a49abbb59a8a46d1625e9691325583bcbd300f10cdce52ee07e1729b0f53 | HTML设计；非原生验收 |
| viewer-320x568.png | UI-018/viewer | 320×568 | 1x | 80b1abb0fb8c72f7601b6ef688f8c4309a1b534d89c2b7dacf9d9dfff03929a3 | HTML设计；非原生验收 |
| viewer-390x844.png | UI-018/viewer | 390×844 | 1x | 39d615ade910083e910f167bd693ef2cf899174cee2d0be277d6242748fe1fb4 | HTML设计；非原生验收 |
| viewer-430x932.png | UI-018/viewer | 430×932 | 1x | 9c1167464085fed1cee3592f70bbf73f379a159facdc3e7da01998e7e9cb3dea | HTML设计；非原生验收 |
| map-error-320x568.png | UI-018/map-error | 320×568 | 1x | 04a80e837848e51b570fb5d8b6bfeb29808d965cf79eb5696babcfd0f1fedfd4 | HTML设计；非原生验收 |
| map-error-390x844.png | UI-018/map-error | 390×844 | 1x | 0b89d3e9069545f796d2ea2fe33b4e846e2a188708e356efdd5ef0adf227d70a | HTML设计；非原生验收 |
| map-error-430x932.png | UI-018/map-error | 430×932 | 1x | 29a6845c7823893f4d1261aa900962efe06459c41f62dcc9881dfc4ef27f7730 | HTML设计；非原生验收 |
| ai-settings-320x568.png | UI-018/ai-settings | 320×568 | 1x | 7ae3fd04e4f6522bfbb45ef9a2abeec7d3f34d800d53d8126762fcc17ea1161c | HTML设计；非原生验收 |
| ai-settings-390x844.png | UI-018/ai-settings | 390×844 | 1x | b31026117b9082963f4fb4f5a2f5dd647a38eb36e77b06831d2b4fcefdb52c59 | HTML设计；非原生验收 |
| ai-settings-430x932.png | UI-018/ai-settings | 430×932 | 1x | cd45a7dcad3fc9e8bee1b8d84f0ffce31b38ac4e90062dd39331b6c8c268ff81 | HTML设计；非原生验收 |
| archived-320x568.png | UI-018/archived | 320×568 | 1x | 5b0d68e1cef71a6a171ff5f402d1a0a50f41c79513490a7ae85f4ff8494355dd | HTML设计；非原生验收 |
| archived-390x844.png | UI-018/archived | 390×844 | 1x | 2c90ebc81bc0d3cbef134aeff9a484ed45e4e33fcafb6e4badfe47912fbb444f | HTML设计；非原生验收 |
| archived-430x932.png | UI-018/archived | 430×932 | 1x | 539b843dcdfec213e9f6c2361a8812a8e539fde46079c3fc8489400f7fb8f0e0 | HTML设计；非原生验收 |
| photo-edit-320x568.png | UI-018/photo-edit | 320×568 | 1x | 37ba54e1f701fb5c925882faebc9c929db6c36fdb79e645fb845837475f0efa8 | HTML设计；非原生验收 |
| photo-edit-390x844.png | UI-018/photo-edit | 390×844 | 1x | 9e3e22d1c83c4b8bddb59bd239dc2ac5592bb0470dbde501ba7134884514c5e2 | HTML设计；非原生验收 |
| photo-edit-430x932.png | UI-018/photo-edit | 430×932 | 1x | 98eaa65e93213f4570340d7a39b14a5b5cb2b6f0a723b32ebeb6186cd5d2c712 | HTML设计；非原生验收 |
| photo-delete-320x568.png | UI-018/photo-delete | 320×568 | 1x | 5f32eb0b7f6b089bfde46411ffe1c66f8d6ab1c19e569119e64de4727cd59497 | HTML设计；非原生验收 |
| photo-delete-390x844.png | UI-018/photo-delete | 390×844 | 1x | a01ce254122c31dc78017ee3458893b1377dcfff87d89ac7a63ec401fe153914 | HTML设计；非原生验收 |
| photo-delete-430x932.png | UI-018/photo-delete | 430×932 | 1x | bba18121e580eb88e19d09ca5e35db34679a0fa43b5d9c1e955159fdc0aea2bb | HTML设计；非原生验收 |
| expired-320x568.png | UI-018/expired | 320×568 | 1x | e646942303b06929e91220aab30eec24010995c3a75b4fa33fa89c99c393fdba | HTML设计；非原生验收 |
| expired-390x844.png | UI-018/expired | 390×844 | 1x | b853064a6b22e9a01c4fde664e5c105954144b8ed678d95333214e6ceeaf7be2 | HTML设计；非原生验收 |
| expired-430x932.png | UI-018/expired | 430×932 | 1x | 79ca39c7ae7789b55f81796019de62a4eb7d926ffb202ccfabdb8ba3324cafd4 | HTML设计；非原生验收 |
| draft-delete-320x568.png | UI-018/draft-delete | 320×568 | 1x | b456b3cfc9fa31a9fc8e9bcb5878528413622932ddc38f68186197c8a0bfb75b | HTML设计；非原生验收 |
| draft-delete-390x844.png | UI-018/draft-delete | 390×844 | 1x | 3df1e35e47a9a5c705b38a82ad4a2e040805d02fccef843566a9131a1d41b458 | HTML设计；非原生验收 |
| draft-delete-430x932.png | UI-018/draft-delete | 430×932 | 1x | d2aaa784a463d1fd7ca546f5a9e0cc973d7d8569bdce2f25700de0a927e293d4 | HTML设计；非原生验收 |
| photo-320x568.png | UI-018/photo | 320×568 | 1x | 6233fe634a9af9e711799471d8ce2528d97fb19f304dcd304a3589770663f8db | HTML设计；非原生验收 |
| photo-390x844.png | UI-018/photo | 390×844 | 1x | 7f63a30ab3e31ded6ad2cd6976b20e492a7181ef7d6bbc97dfd7dda9cab03370 | HTML设计；非原生验收 |
| photo-430x932.png | UI-018/photo | 430×932 | 1x | 6648aeb2fdb817388dc8b70d2ccd754bfd8acd36ab2d72bdaf35d1e2d16c1cd8 | HTML设计；非原生验收 |
| desktop-1600x1040.png | review workbench | 1600×1040 | 1x | 976a37660c87b2c44c189980519f0680388b35576b6d31e92542f533fc86798f | 桌面评审工作台，非额外小程序视口 |

## Verification and gaps

- 浏览器静态导出、无页面JS错误、按钮/文本输入44px、水平边界检查：PASS。
- 示例导入/同意/核对/确认/时间线/回放/暂停/拖动/世界视图：PASS。
- 聚合展开/地点详情、单张修改/全选4张/确认：PASS。
- R3/R4分批追加、AI开启/沿用/关闭、刷新继续、到访日重算、逐张删除、归档收尾与7天边界演示：PASS。
- 主动删除单张草稿、重置后恢复初始示例且不会重新保存已重置内容：PASS。
- 以上仅为隔离HTML设计验证；不证明微信原生节点/地图覆盖层/真机选图/AI/后端可用。
- 本次文案Spec与DREV待批准；主功能Spec04仍VERIFYING，原设计DREV01冻结。
- 原生三视口、字体放大、读屏、iOS/Android、照片与地图服务：NOT_RUN。
