# UI-018 / UI-001 — DREV-20261024-FOOTPRINTS-TIMELINE-01

- Status: APPROVED
- UI ID: UI-018
- Design Revision: DREV-20261024-FOOTPRINTS-TIMELINE-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md#BUG-SPEC-20261024-FOOTPRINTS-CONTROLS-TIMELINE-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/index.html=e1f468a9eff823de181bd563a6814fe9207004fc86571b0bc4c4c605cd45e47c
- Prototype generated/updated at: 2026-10-24
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-24
- Approval evidence: 本会话call_a4e6de3e6be5408fb860b26f20a09323回复「批准 Spec01＋Architecture01＋DREV01，按此实施」。源、42张PNG和本清单自此冻结；实施证据单独记录。
- Superseded by: N/A

42张合成HTML设计候选；人物/日期/插画均非业务数据。旧批准设计保持不可变。原生、真机与生产实现未执行。
本机已安装Playwright但缺其自带Chromium，首次launch未进入渲染；改用现有Chrome隔离会话后完成42张导出、三视口DOM预算/等列/倒序及切换/回放/预览/设置/换窗口交互检查，无页面错误、零网络请求。HTML不替代微信节点几何与设备验收。
走查390主界面、320长名及390设置；确认遍历各自日期的照片详情，manual不展示伪照片。源/PNG均以本清单最终SHA为准；详细机器结果见[render-audit.json](render-audit.json)。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| overview-320x568.png | UI-018/overview | 320×568 | 1x | f3f38551d1f58d6e2b2ec787e939e0d3320462d85d1de6d5239d24d10d50017c | HTML候选，非原生 |
| preview_failed-320x568.png | UI-018/preview_failed | 320×568 | 1x | ef78592c132ccea11d74dec0eafb9f5c0413835dcb004ec457d935d6b659821b | HTML候选，非原生 |
| empty-320x568.png | UI-018/empty | 320×568 | 1x | bd82fe20bb815464aff444313d3ae8173491786bdc45e2ac1f4424da5f80c550 | HTML候选，非原生 |
| loading-320x568.png | UI-018/loading | 320×568 | 1x | f5d8c2a8f442853e1ca4035e3298fa57c8b5f6578cb7d2f3175e38c82f47a89a | HTML候选，非原生 |
| error-320x568.png | UI-018/error | 320×568 | 1x | e8c655d976f870dc687d53fdbbea13af191be4cca42a90acfb4424c54489a3c0 | HTML候选，非原生 |
| viewer-320x568.png | UI-018/viewer | 320×568 | 1x | 990d17bfd87d6fec7b322f7920dfe884142922de1fd79d4532f2fdc23fc013c0 | HTML候选，非原生 |
| long-320x568.png | UI-018/long | 320×568 | 1x | 3dd1c707726835683bbd83d3e365bea988ae370bfc091cfd818ef5c0303b9004 | HTML候选，非原生 |
| playback-320x568.png | UI-018/playback | 320×568 | 1x | 4088006dda77d5c6eac52a29bb210b3b52cd19cdf77661e77c32ab44d2251dca | HTML候选，非原生 |
| lit-320x568.png | UI-018/lit | 320×568 | 1x | 4ffbb9eac9dcce8fbc1f64b1e9f5d9e2cc4b9ecd64d87fb3d5c5a021c83223a7 | HTML候选，非原生 |
| settings-320x568.png | UI-018/settings | 320×568 | 1x | b8803d2438813c21a0bda5eecba257e26ec3cae548a6f733fcccb8c6133b68ab | HTML候选，非原生 |
| saving-320x568.png | UI-018/saving | 320×568 | 1x | ef39bb64e00ea79916ab3f69acddb984d29877d69ddb9dd08c831488c3066016 | HTML候选，非原生 |
| photo-320x568.png | UI-018/photo | 320×568 | 1x | df9be374ed12dc7c49609d6ce1544dbce60bfa69b490ab2d1958204466e9ca9a | HTML候选，非原生 |
| older_window-320x568.png | UI-018/older_window | 320×568 | 1x | 107f7cd3bc9920d1330b52267ce2e5ae1af3b961746b2d5f718566339b1f07f8 | HTML候选，非原生 |
| standalone-320x568.png | UI-018/standalone | 320×568 | 1x | d39e7ee9cc725ecfbaddb8f2ca345c32ff13055877160b55a4948766cab6c650 | HTML候选，非原生 |
| overview-390x844.png | UI-018/overview | 390×844 | 1x | a09d88c35580f977272c656d3a00bc7955e078c97097664694230bfb6b5bb6fa | HTML候选，非原生 |
| preview_failed-390x844.png | UI-018/preview_failed | 390×844 | 1x | 4b1204fd74ef6efa048820b9470604b9fdcadc7e2d24ed5c48dfff9c0eda6e10 | HTML候选，非原生 |
| empty-390x844.png | UI-018/empty | 390×844 | 1x | a8f57c7eb73ae8b5d6f7222c47222424e4e8b2adb2e47dc4255616c21929d3eb | HTML候选，非原生 |
| loading-390x844.png | UI-018/loading | 390×844 | 1x | 978cdc4236e6ab310f6a85b5ecd022d3278a93cfae2669917a28b2aef61ab159 | HTML候选，非原生 |
| error-390x844.png | UI-018/error | 390×844 | 1x | 25c614acc6690f2d3ad11d74bf80409f5488f1b5fd08a2e521865defc9c21b75 | HTML候选，非原生 |
| viewer-390x844.png | UI-018/viewer | 390×844 | 1x | 17f1432fd967d1ebfdaf28ca82a31ecca388a273f782ac0e0ee61e98f3c0ff31 | HTML候选，非原生 |
| long-390x844.png | UI-018/long | 390×844 | 1x | e708e6b6d58c507e9afcf87a6344165524016827874caac4677af8eba7bdca45 | HTML候选，非原生 |
| playback-390x844.png | UI-018/playback | 390×844 | 1x | c66c352bbb380e2ca7d287b7d4b2a8febc0b757a20d741fcd55feedee085cca0 | HTML候选，非原生 |
| lit-390x844.png | UI-018/lit | 390×844 | 1x | c022039674927ae5c535d8cda6b08b39e2801c8df5e9ab5089dd8b582489028a | HTML候选，非原生 |
| settings-390x844.png | UI-018/settings | 390×844 | 1x | c54bf4b046c9f1d27c808cb45fd966374efd74fbe66ac28a305091486b706947 | HTML候选，非原生 |
| saving-390x844.png | UI-018/saving | 390×844 | 1x | 2c9857dd149e6fa9ede4e8a62326e195e6570c11a403444e4616adcbcd3a0879 | HTML候选，非原生 |
| photo-390x844.png | UI-018/photo | 390×844 | 1x | 1486620e4d8d50aefacb9699428e538312e7a03655b18aea472dae2a4cedf036 | HTML候选，非原生 |
| older_window-390x844.png | UI-018/older_window | 390×844 | 1x | baeb9046c09bd00f9e27c25b2e47024acac3f7b936f7d89cc4a4a0f396927c93 | HTML候选，非原生 |
| standalone-390x844.png | UI-018/standalone | 390×844 | 1x | a37e0511fbb5abe22183f5bb3c426f8693c1756cf4b45225093b72628f42ac42 | HTML候选，非原生 |
| overview-430x932.png | UI-018/overview | 430×932 | 1x | 227d3245871fd69508eccceb6a4f3a0843c49e24e14a5c8d98ac18b6b1f837bb | HTML候选，非原生 |
| preview_failed-430x932.png | UI-018/preview_failed | 430×932 | 1x | d183e3a7289b680d62d1bcd9ca7248f25e9f74cf33ab3d2e697837bbd4242ebc | HTML候选，非原生 |
| empty-430x932.png | UI-018/empty | 430×932 | 1x | 7e21dd0bc7082326425b00a172dec9fa9d8648d696e01278d01542572d287e54 | HTML候选，非原生 |
| loading-430x932.png | UI-018/loading | 430×932 | 1x | f019a0b8ffe39bdd338a5442a3eff3baee3102caad36e3c02d152fc27016dbeb | HTML候选，非原生 |
| error-430x932.png | UI-018/error | 430×932 | 1x | 1b7a92e3885a1a04ea7a4d7a52a0610e3fed86efb7fa309bdf5ded2ac759aa7b | HTML候选，非原生 |
| viewer-430x932.png | UI-018/viewer | 430×932 | 1x | a97c6af6bf140051939b22e5e481965a88a9507b15ef711820dc2988a68730c1 | HTML候选，非原生 |
| long-430x932.png | UI-018/long | 430×932 | 1x | 73107d4133710f4bbd44a77418fd4ccee5cadcce647a469f05c09c27c56087d0 | HTML候选，非原生 |
| playback-430x932.png | UI-018/playback | 430×932 | 1x | b691cfad59303c9cf9f13094792281187eecf03e26efa2952e02496feecca760 | HTML候选，非原生 |
| lit-430x932.png | UI-018/lit | 430×932 | 1x | 04cb643e74b1c18927b2a93b49911b2355a85bf54df22726a94bcb6d783596f2 | HTML候选，非原生 |
| settings-430x932.png | UI-018/settings | 430×932 | 1x | ed1575ca14ff6bb960e2389c4b0a5f1fa430e908e582fb99eab4e15a4be3a960 | HTML候选，非原生 |
| saving-430x932.png | UI-018/saving | 430×932 | 1x | fb53cf26f9bb22f3b548f61654542cfe4b2e16d178a76b2bc46fc9d3a74d004d | HTML候选，非原生 |
| photo-430x932.png | UI-018/photo | 430×932 | 1x | 0c4c65d3d575a58b4a2b9194f46c1c00cce5a9692e8fe4bc182527739e0f25a3 | HTML候选，非原生 |
| older_window-430x932.png | UI-018/older_window | 430×932 | 1x | fcb83e580528cd7b29470f71ec454396e7901ce2ce26f5d4391da29dfcd50824 | HTML候选，非原生 |
| standalone-430x932.png | UI-018/standalone | 430×932 | 1x | 4c07af983cde89dd4befa5e590cb084fed38591d65bb20e1c7cc17f7afcfe7e8 | HTML候选，非原生 |
