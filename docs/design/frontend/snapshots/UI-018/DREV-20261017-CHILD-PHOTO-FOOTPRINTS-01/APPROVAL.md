# UI-018 — DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01 设计批准快照

- Status: APPROVED
- UI ID: UI-018
- Design Revision: DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md#SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01/index.html=58982a8241094d1fbc6da97b6eb7d16a7f4bb046a7538b76c6c67eba893c896e
- Prototype generated/updated at: 2026-10-17
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-17
- Approval evidence: Q19 request_user_input_async / call_68a44a48d02740b6befbef52d0b390d9 / item 0；用户“认可，评审收敛”。问题明确对应Spec04 / Architecture03 / DREV01，仅确认需求共识与交互稿，生产实施另行批准。原话与范围记录：docs/research/child-footprints/20261017-grill-review.md#q19-整体确认记录。
- Superseded by:; [DREV-20261024-FOOTPRINTS-TIMELINE-01](../../../prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md) covers ordinary button/view-control pills and timeline thumbnail time labels only; other flows/layout remain in their approved scope.

## Approved scope

27个HTML状态，全部覆盖320×568、390×844、430×932。
合计81张手机PNG，另附1张桌面评审工作台。
照片、孩子、时间、地点均为虚构示例，照片用内嵌SVG插画占位。
地图仅为坐标点位示意，无真实底图、行政边界、道路、定位或地理检索服务。
交互范围：记录入口、导入/核对/家长确认、时间线/跟随回放/地点点亮、主要区域优先与全球、AI设置、固定7天草稿、分批继续、归档收尾、逐张纠正/删除及照片翻页；完整语义与限制见FRONTEND-SPEC.md。
Permitted implementation-only deviations: none。
Explicitly not approved: Task Spec04或Architecture03的生产实施；真实地图/EXIF/AI/原生运行效果；真实儿童素材或第三方处理实验；数据迁移、部署、上传、体验、审核或正式发布。
本次登记用户批准后，源、PNG和清单冻结；后续仅可添加Superseded by，设计变化需新DREV。Task Spec保持READY_FOR_REVIEW。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| records-320x568.png | UI-018/records | 320×568 | 1x | 645e4e729662263fdff24b6331e6daf89b349ef33907c8dfe0ac21085dcd7df8 | HTML设计；非原生验收 |
| records-390x844.png | UI-018/records | 390×844 | 1x | c851f5394df4846cc95108752ff37e5813fc601b0c70eacdb1dcdd4bd07e63ef | HTML设计；非原生验收 |
| records-430x932.png | UI-018/records | 430×932 | 1x | 2e4d4e5ea0c621ccb06730e91b7fd8fd6a0e9ce4a1b2adf9611e9b5479c2198e | HTML设计；非原生验收 |
| timeline-320x568.png | UI-018/timeline | 320×568 | 1x | bf559a4a88097ef64e9942c661f70de5dfefcc23427ee20398f8248f2752b978 | HTML设计；非原生验收 |
| timeline-390x844.png | UI-018/timeline | 390×844 | 1x | b978a3e46d6e1708959e334fcc58a14bcf41e12fd29577e90262a46782d9f2a6 | HTML设计；非原生验收 |
| timeline-430x932.png | UI-018/timeline | 430×932 | 1x | 307538732941f581acedf91f1247fedd0ce7b033e07daf494c0d27c5ed69bbcf | HTML设计；非原生验收 |
| empty-320x568.png | UI-018/empty | 320×568 | 1x | ee9221d04d7ab3d1861ebf67d5ca0f7f0e268415651ad61513dfed5ea5c91bdb | HTML设计；非原生验收 |
| empty-390x844.png | UI-018/empty | 390×844 | 1x | c2ace78aa4ee9b02697a9179e72da0d6522c452bf34e33b89a983cb76d7aefbe | HTML设计；非原生验收 |
| empty-430x932.png | UI-018/empty | 430×932 | 1x | 2434dc34a035471505db7fd9e9a4f8f8ac02fa800b62e4424f8ae82a90bb301a | HTML设计；非原生验收 |
| import-320x568.png | UI-018/import | 320×568 | 1x | 257325fc68cd1338fc3491c7b1c2b6c17c25ecf31d9732062704cbad535a883c | HTML设计；非原生验收 |
| import-390x844.png | UI-018/import | 390×844 | 1x | b99ca4480ade5e13028bbff20d8bd0a1c1325a1c15196a75635d5e8a64a03612 | HTML设计；非原生验收 |
| import-430x932.png | UI-018/import | 430×932 | 1x | ae587931e2f03910021efb6f83b38635cd1991a1ea14433283da7f338637f536 | HTML设计；非原生验收 |
| consent-320x568.png | UI-018/consent | 320×568 | 1x | 9a6679b9cfe2bc081645cfcd842af2f220ceb0cf4a72e51176d4477b4c08c48a | HTML设计；非原生验收 |
| consent-390x844.png | UI-018/consent | 390×844 | 1x | c557c8b2ad8c7b967a574b35ecfddaa0aa4548ae38eb84bece408fe8c36307d9 | HTML设计；非原生验收 |
| consent-430x932.png | UI-018/consent | 430×932 | 1x | e3483b8c746fc2591729d12b319ed49d72a54af8b2ed76c7a19cc873f81a3271 | HTML设计；非原生验收 |
| importing-320x568.png | UI-018/importing | 320×568 | 1x | 33fbbd700be168b3d97e7a3fad7f05c2a24368f647dd9b96f07daa29d98709d8 | HTML设计；非原生验收 |
| importing-390x844.png | UI-018/importing | 390×844 | 1x | 20b8e350eb73be88c4600a48c2771f8e646e5bfc3dd067e53f65485a38a8e2ea | HTML设计；非原生验收 |
| importing-430x932.png | UI-018/importing | 430×932 | 1x | 150aa5df96ea2988f514ac1a5d6e864447f370d2d71757c022e42d5bc15f6b8d | HTML设计；非原生验收 |
| review-320x568.png | UI-018/review | 320×568 | 1x | 52dd80ca746a659d334de19de16b199f55f2a7ab314c0a8861d9da9de77827c6 | HTML设计；非原生验收 |
| review-390x844.png | UI-018/review | 390×844 | 1x | 35253d462d04f5a36553ee69384199ef919e4834b1ceeeba835793c006308772 | HTML设计；非原生验收 |
| review-430x932.png | UI-018/review | 430×932 | 1x | 7446be8ad67a534d77bcd29dc4567f506faaeb9104ee6f7c6db653366da7fe54 | HTML设计；非原生验收 |
| batch-320x568.png | UI-018/batch | 320×568 | 1x | 2e17ab5e68df88a824ff01b8c9f0e7770d1fb6ca0c169fa777c800647547f61b | HTML设计；非原生验收 |
| batch-390x844.png | UI-018/batch | 390×844 | 1x | 9c7a5046559a54fe76ef64ec0cd4a420692f054c258f2163733cfe4a5c02459a | HTML设计；非原生验收 |
| batch-430x932.png | UI-018/batch | 430×932 | 1x | a902e1340ac71d064c7b8620e33de888d15691d8732ef92520810f982ef421cb | HTML设计；非原生验收 |
| confirm-320x568.png | UI-018/confirm | 320×568 | 1x | 0bb00143f0a444756008b6b716667167504a30fcc6c332d2b1ba6cdcc1b8b5b3 | HTML设计；非原生验收 |
| confirm-390x844.png | UI-018/confirm | 390×844 | 1x | 209e4714f2e1fc71e9f89db40e928fd43ed4e79194cc01d109cabb43c2d98395 | HTML设计；非原生验收 |
| confirm-430x932.png | UI-018/confirm | 430×932 | 1x | e8ece261e68bbf686a41c5a1fce364469f2e50b5fa08b9bc1014974654951f79 | HTML设计；非原生验收 |
| saved-320x568.png | UI-018/saved | 320×568 | 1x | 30c0784fdfa91acbf6da63d5790ab256e24db729ca55bd79807003b24440ac1d | HTML设计；非原生验收 |
| saved-390x844.png | UI-018/saved | 390×844 | 1x | 51ccaa0c1bb9feb381edb88fa28103bdf5fca15cd32ef0e7d6a3c532f3cc0566 | HTML设计；非原生验收 |
| saved-430x932.png | UI-018/saved | 430×932 | 1x | 610c7c0743e4e6b7a22599b500c344601cba64aa47b079f47a3aad302ca6ea9e | HTML设计；非原生验收 |
| playback-320x568.png | UI-018/playback | 320×568 | 1x | c5c4cb02706f177500445e67218b0c5555d212beb5988e9af568d81c82cb1ffa | HTML设计；非原生验收 |
| playback-390x844.png | UI-018/playback | 390×844 | 1x | 26832bc7cfe297187892890ec2019bac8df120a28fcf16b850895e96f3f28b7d | HTML设计；非原生验收 |
| playback-430x932.png | UI-018/playback | 430×932 | 1x | d17e40cc3c48600a677dd72838e8671b36f05a0acc93fd6955df37d8721afb91 | HTML设计；非原生验收 |
| paused-320x568.png | UI-018/paused | 320×568 | 1x | 0f7aed7df1b747f652779de04a0c2abcb6836f4455ad2d12feb4742de953605f | HTML设计；非原生验收 |
| paused-390x844.png | UI-018/paused | 390×844 | 1x | 30620525c275c0bdd03e16811534696b3d21d15d191c708dca7e526384c8fc73 | HTML设计；非原生验收 |
| paused-430x932.png | UI-018/paused | 430×932 | 1x | 1a1e2e2369a01db310990fd210fae0b8c95af0eafc9d53991e4e225d435712b1 | HTML设计；非原生验收 |
| lit-320x568.png | UI-018/lit | 320×568 | 1x | 6e3fad6d0853cfa9aa4916f59528183435c87ae586a52cd34f6c251c3e918d51 | HTML设计；非原生验收 |
| lit-390x844.png | UI-018/lit | 390×844 | 1x | 31cd0098774b3e5c128bd172c0e7a116073c5ebb3b0014b64a4667b0127164c7 | HTML设计；非原生验收 |
| lit-430x932.png | UI-018/lit | 430×932 | 1x | 19ab3bc3980e67822f6ed18c4d05b3d0ca9ef3b924f1bc9b6c39d432499695ff | HTML设计；非原生验收 |
| world-320x568.png | UI-018/world | 320×568 | 1x | c5a28bd31a0fb09147e0d5eb36a6c21d7c99d09e89152ef5dfa51dba5c8291ec | HTML设计；非原生验收 |
| world-390x844.png | UI-018/world | 390×844 | 1x | e8b533cb6e786babc7d20e3a976e8bd001ecfabc8698c7e5e90d5b780c3f7031 | HTML设计；非原生验收 |
| world-430x932.png | UI-018/world | 430×932 | 1x | 4a4b9712dae19c39c2fc86b33ec9f25af72ceeaaedecf7f00493642e98a3e75e | HTML设计；非原生验收 |
| place-320x568.png | UI-018/place | 320×568 | 1x | 7871f055e1b505b2cfdc90f7345edde2309855a7dddfebd66654c42c50c1e205 | HTML设计；非原生验收 |
| place-390x844.png | UI-018/place | 390×844 | 1x | aa456977d00b310cdd747220693ec47df9d009bd4e8f8a97043a32b0040511d8 | HTML设计；非原生验收 |
| place-430x932.png | UI-018/place | 430×932 | 1x | c25fe112732676e71421ce3ee8e580413a3ada1ccadc42ecfe8c6b6a18deaace | HTML设计；非原生验收 |
| failed-320x568.png | UI-018/failed | 320×568 | 1x | 095962c1c0512c18c54f273756b51a74c13e7fb061b2e5be311cca382a1cf97c | HTML设计；非原生验收 |
| failed-390x844.png | UI-018/failed | 390×844 | 1x | edea2b4f55957177d4f1716ab7fd3012cbb22e6dd68a645603272fb2eddc2b32 | HTML设计；非原生验收 |
| failed-430x932.png | UI-018/failed | 430×932 | 1x | 6658cacc90a88bffffc4f06e20df4df14b81ae78380a8064de7064fafcddf7de | HTML设计；非原生验收 |
| unknown-320x568.png | UI-018/unknown | 320×568 | 1x | 52dd80ca746a659d334de19de16b199f55f2a7ab314c0a8861d9da9de77827c6 | HTML设计；非原生验收 |
| unknown-390x844.png | UI-018/unknown | 390×844 | 1x | 35253d462d04f5a36553ee69384199ef919e4834b1ceeeba835793c006308772 | HTML设计；非原生验收 |
| unknown-430x932.png | UI-018/unknown | 430×932 | 1x | 7446be8ad67a534d77bcd29dc4567f506faaeb9104ee6f7c6db653366da7fe54 | HTML设计；非原生验收 |
| denied-320x568.png | UI-018/denied | 320×568 | 1x | 3cbfa4529813ae43b1ff9625f72ef389307c6135453dde2bcc366c84132527f6 | HTML设计；非原生验收 |
| denied-390x844.png | UI-018/denied | 390×844 | 1x | 99dfa1ae9912a28c402d6b8963ad6c8b1b4ba5a0af3db4c1971be0e304604d7b | HTML设计；非原生验收 |
| denied-430x932.png | UI-018/denied | 430×932 | 1x | 5ed2e6e36827b52e2551c1b66e529eadbcf49244efd9b7149390de360a4bedd6 | HTML设计；非原生验收 |
| viewer-320x568.png | UI-018/viewer | 320×568 | 1x | 80d8e5382e565b4b55f14a1a0f69c6d579e8b7d7e8e35b1a02e033c527c65a1c | HTML设计；非原生验收 |
| viewer-390x844.png | UI-018/viewer | 390×844 | 1x | 1ee058dda401aa32fb1d5544c13468e91f6805ade4f2cf19a1934dbfe37bcc2f | HTML设计；非原生验收 |
| viewer-430x932.png | UI-018/viewer | 430×932 | 1x | d64a771c796dbd3c383d9caa8ff45ca35890bb8fb354fdf1e92b016cda892737 | HTML设计；非原生验收 |
| map-error-320x568.png | UI-018/map-error | 320×568 | 1x | ec089adb6f2d8351cc14397147432e053719da96c088dd9849d87c22a8ce9f70 | HTML设计；非原生验收 |
| map-error-390x844.png | UI-018/map-error | 390×844 | 1x | d109396fd0b02dcff1b8077da0502274291b808d29240fe573aba49c3a95a8e4 | HTML设计；非原生验收 |
| map-error-430x932.png | UI-018/map-error | 430×932 | 1x | 1102791d1ecb4fc28ae5bb5f860251f7eb6711cd1b48853a36bc7181f105c697 | HTML设计；非原生验收 |
| ai-settings-320x568.png | UI-018/ai-settings | 320×568 | 1x | fc918203b80822a99b529b7286934f4a0b1468b030c56300e634462d94a496ad | HTML设计；非原生验收 |
| ai-settings-390x844.png | UI-018/ai-settings | 390×844 | 1x | c684c604d0dd05433f410d25cfbbd80ebc58440739fed165ac241c2601eec278 | HTML设计；非原生验收 |
| ai-settings-430x932.png | UI-018/ai-settings | 430×932 | 1x | bf2faedc387ed1d24e04fb6fde8125f975c90e93a129c3875d11c7402f36fdc7 | HTML设计；非原生验收 |
| archived-320x568.png | UI-018/archived | 320×568 | 1x | 39041c93a60ae147478db1511c8adf976d678f41a12ab77a515078125ef4f853 | HTML设计；非原生验收 |
| archived-390x844.png | UI-018/archived | 390×844 | 1x | 8fca8e2b6591565942d9fabbe4bc5d642f3ce004049ed167b8f42bcc61cafb96 | HTML设计；非原生验收 |
| archived-430x932.png | UI-018/archived | 430×932 | 1x | 3a03bde4da050993047d59e6db31df4f23ba1a7a950b2869476a5de28b8ff065 | HTML设计；非原生验收 |
| photo-edit-320x568.png | UI-018/photo-edit | 320×568 | 1x | 1aaad1a32f98aea0d4d531a6894d896eb2c1228db7a7f5a87d25f2829d7e9a3b | HTML设计；非原生验收 |
| photo-edit-390x844.png | UI-018/photo-edit | 390×844 | 1x | 073f7f40fd9023858b2c608f88bb82592abbb4a6f717c724146d882ceb49d03d | HTML设计；非原生验收 |
| photo-edit-430x932.png | UI-018/photo-edit | 430×932 | 1x | dd08326aab6c43a1bfd1061ab139f95d303932839e6d762e35cde5c9b83013fc | HTML设计；非原生验收 |
| photo-delete-320x568.png | UI-018/photo-delete | 320×568 | 1x | 71f3216d01bdae59e43588681b2748e8b85bf6a9d62be894ce459cfae155149e | HTML设计；非原生验收 |
| photo-delete-390x844.png | UI-018/photo-delete | 390×844 | 1x | 252f3d462e02703408cee4ff09b3a290a974167c8d275559a2c3a478f2caf616 | HTML设计；非原生验收 |
| photo-delete-430x932.png | UI-018/photo-delete | 430×932 | 1x | b19c762e84174e0634867d92066a5b985abefee06dfc2d4acc9063e86d258974 | HTML设计；非原生验收 |
| expired-320x568.png | UI-018/expired | 320×568 | 1x | 1831b25b17ec43659c10f8edd4a92021b8ee349d77bcbd9f0604dc2234d35e98 | HTML设计；非原生验收 |
| expired-390x844.png | UI-018/expired | 390×844 | 1x | a68e54bbd170525f63332eb53e5356750926003f4ab6081e6224bc5a1df05fe5 | HTML设计；非原生验收 |
| expired-430x932.png | UI-018/expired | 430×932 | 1x | 188455f9bb7a72f0681d98fc1389cad620aa10d7246cdfb8a1643b4362b332e6 | HTML设计；非原生验收 |
| draft-delete-320x568.png | UI-018/draft-delete | 320×568 | 1x | e702219e5b5b176172863b1056dd359a470f5756e5fd22d13126d317ba0a5574 | HTML设计；非原生验收 |
| draft-delete-390x844.png | UI-018/draft-delete | 390×844 | 1x | ba26c632c9eab984576bda6bda25a2449e39e47d6d544b5bb33b9274fd6b12a3 | HTML设计；非原生验收 |
| draft-delete-430x932.png | UI-018/draft-delete | 430×932 | 1x | 2ddef7ee308a6aa8dae4e4d5b56b2e489c7b7460b6866aeaec7e9f69d2f8ec67 | HTML设计；非原生验收 |
| photo-320x568.png | UI-018/photo | 320×568 | 1x | 184a22a0d4a8b8a0b46291796ffefc616f539d38e05340285f91c1f28f65e4c5 | HTML设计；非原生验收 |
| photo-390x844.png | UI-018/photo | 390×844 | 1x | 42084b991a08f149ec44e18a3e667a29c328796fe93c35592252d3b5ea97cee2 | HTML设计；非原生验收 |
| photo-430x932.png | UI-018/photo | 430×932 | 1x | 8892c4170463006d366b1a1571a70afbd111aa9cfce15990c00df2c05668e573 | HTML设计；非原生验收 |
| desktop-1600x1040.png | review workbench | 1600×1040 | 1x | 57cbcb911ad34428d52f8c78bb23cbfa14fa0cd57679f7e7c75b29800a2ccaaa | 桌面评审工作台，非额外小程序视口 |

## Verification and gaps

- 浏览器静态导出、无页面JS错误、按钮/文本输入44px、水平边界检查：PASS。
- 示例导入/同意/核对/确认/时间线/回放/暂停/拖动/世界视图：PASS。
- 聚合展开/地点详情、单张修改/全选4张/确认、同地同日照片前后翻页：PASS。
- R3/R4分批追加、AI开启/沿用/关闭、刷新继续、到访日重算、逐张删除、归档收尾与7天边界演示：PASS。
- 主动删除单张草稿、重置后恢复初始示例且不会重新保存已重置内容：PASS。
- 以上仅为隔离HTML设计验证；不证明微信原生节点/地图覆盖层/真机选图/AI/后端可用。
- 需求grill review已由Q19完成；DREV获设计批准，Task Spec/Architecture生产实施批准尚未取得。
- 原生三视口、字体放大、读屏、iOS/Android、照片与地图服务：NOT_RUN。
