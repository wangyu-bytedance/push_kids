# UI-001 — 公平排期候选设计证据

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261007-FAIR-REVIEW-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Task Spec path and revision: specs/active/FEAT-001-FAIR-DAILY-REVIEW.md#SPEC-20261007-FAIR-REVIEW-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261007-FAIR-REVIEW-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261007-FAIR-REVIEW-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261007-FAIR-REVIEW-01/index.html=99e920e60756e27798a2f5c1602516a7b49d39d5b12778ca30f32bf86baeae22
- Prototype generated/updated at: 2026-10-07
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-07
- Approval evidence: 本会话“生成代码，然后测试后提交部署服务端”，批准删除两段说明后的SPEC-20261007-FAIR-REVIEW-01及DREV-20261007-FAIR-REVIEW-01
- Superseded by: N/A

## Scope

今日说明与条目日期/安排状态的增量设计。全部为合成示例，不是真实孩子的计划或产品截图。
沿用现有导航、反馈、筛选和调整菜单；本设计不会修改这些组件。

2026-10-07用户反馈“这些信息不需要”：删除今日排期规则说明与等待总数；未批准候选稿内同步更新。

## Export manifest

| File | State | CSS viewport | Scale | SHA-256 |
|---|---|---|---|---|
| clear-320x568.png | clear | 320x568 | 1x | ea91a820f98765cbeb5b435f3ac850359bce26b7948f959bf42ba11013eaa858 |
| clear-390x844.png | clear | 390x844 | 1x | 224ce3fb65ae63ddeb2159f7bde7cde719fb281539ddab5058d3c06b45211fb3 |
| clear-430x932.png | clear | 430x932 | 1x | 899dbb566269dbc7d61a37a5eb03e31455f10cf3be10a1d674a6bae78df21100 |
| completed-320x568.png | completed | 320x568 | 1x | 99f0d936b923076075c6d8b2dc0de23c180876a818f1db2b14b19897cc5df216 |
| completed-390x844.png | completed | 390x844 | 1x | c42d0988b5947c740c0cd413deab5a476a0977d9e6f0974fd8c7ca34ecb0eaeb |
| completed-430x932.png | completed | 430x932 | 1x | ecd65f60a1cf4a9d8e16132cb0c7e32894b10075fffd6b0acddeb13ccb874d73 |
| deferred-320x568.png | deferred | 320x568 | 1x | 79be529f7d38e648ab91ca64021144c81adebf5e2f94b0f0325690fbbd2b413d |
| deferred-390x844.png | deferred | 390x844 | 1x | 5a880c1163428460f0d4f41e656f47b12cc6b4cee103ae99a19d56e3baf6ef18 |
| deferred-430x932.png | deferred | 430x932 | 1x | edd70eb5fe2418b936461627b2466a41e921231681b88692e773be1820de2e2f |
| future-320x568.png | future | 320x568 | 1x | 547e6d956cb2744227a7c4793c84f40ce0dc04e661c7351d0ed27fb16398e5ad |
| future-390x844.png | future | 390x844 | 1x | 988bc50d71a548d94d62f9de45b0357c1ef44321d5a5ee4e942c3b4f8cf99036 |
| future-430x932.png | future | 430x932 | 1x | 21f7a24ab842e037cce8a5d2d3eb38110513f043d990b06d634df5997de45570 |
| legacy-320x568.png | legacy | 320x568 | 1x | 0a27ded7ab8c4cd5fb51f26bba0dfe0714a4db30dcf9356cee6d2b65a8d04e6e |
| legacy-390x844.png | legacy | 390x844 | 1x | fbf24a844a5a68c5787c37e5a79d4395319cd2c21a683db1472a78d05e5c3fa0 |
| legacy-430x932.png | legacy | 430x932 | 1x | 56d91a4e133e86b15d64c122dec3536854d2075d3ae46cd24d406929c2120894 |
| limited-320x568.png | limited | 320x568 | 1x | 1fbf61141565bd3676872c486c1bb19517e77b482d8de5cf112bc93a27538d7d |
| limited-390x844.png | limited | 390x844 | 1x | b837350b9a48e05f92d6f4c7b0671959d7b6bf7262a6cf9e6df9bc09bc5664ba |
| limited-430x932.png | limited | 430x932 | 1x | efc31661c1f6fdad5544c5054ec44fa4dd59f75bce0ba72e2c5b107351bd9827 |
| long-320x568.png | long | 320x568 | 1x | 54f8c18c4f72dfad9f6bfa96eb236f67a19f306e85337f6699866833e44730db |
| long-390x844.png | long | 390x844 | 1x | ef936c603f2a9dd71ed4d2b2e371bcd44c883b49ce3b4c277f95b5005882f798 |
| long-430x932.png | long | 430x932 | 1x | 4731e310266c775a50d3dd15cdc1571018c2e45c4c3b744613128b6115dcb642 |
| reserved-320x568.png | reserved | 320x568 | 1x | fb3b209cbd3dba259e3351f0d589c01cfcf193130aa582ae482495222186a7d8 |
| reserved-390x844.png | reserved | 390x844 | 1x | e6da1e5773fe8036cd7dd3b670b8d03aedaba71158921896fd39d6d8ce29cae4 |
| reserved-430x932.png | reserved | 430x932 | 1x | d3a769c9efabc8b65ebc46aef4506052b505b12716168b56356db3cdf2f4ad33 |
| reviewed-320x568.png | reviewed | 320x568 | 1x | 92d9b67b22da2773a167c50c7a47331c3a05c6caa333267ed8f9058f1f09bb17 |
| reviewed-390x844.png | reviewed | 390x844 | 1x | 715b52a76622d2cbc72b8b9bb8f13c66ef13a3093ef60b5360970c7ab532d3bc |
| reviewed-430x932.png | reviewed | 430x932 | 1x | 69bbb469a771256a34cde7c4bc68bf14537336869a9097ac3e68f80e50fe0b91 |
| scheduled-320x568.png | scheduled | 320x568 | 1x | 29f5cc5b277419612f585ebfac6a00211c50fe3ac9d25a7d28bb7078864a5f50 |
| scheduled-390x844.png | scheduled | 390x844 | 1x | 03b368de2cdab5282d02719032205043a592191655fc8df4138d1452efe355fb |
| scheduled-430x932.png | scheduled | 430x932 | 1x | 1574430f72953f5a44733259cb8a6ae65afe4171ef6f044e4af402fc31a1b3df |
| today-320x568.png | today | 320x568 | 1x | ea91a820f98765cbeb5b435f3ac850359bce26b7948f959bf42ba11013eaa858 |
| today-390x844.png | today | 390x844 | 1x | 224ce3fb65ae63ddeb2159f7bde7cde719fb281539ddab5058d3c06b45211fb3 |
| today-430x932.png | today | 430x932 | 1x | 899dbb566269dbc7d61a37a5eb03e31455f10cf3be10a1d674a6bae78df21100 |
| ungenerated-320x568.png | ungenerated | 320x568 | 1x | 3c4b30c81ce1943caa7049335fdf73af60b22732b6c3ed97edb3b418ec9bbe7f |
| ungenerated-390x844.png | ungenerated | 390x844 | 1x | 1db7db5cbc34f80707b5658e8843105dfb7441ab7c25d82928924c3a6e3ac6cc |
| ungenerated-430x932.png | ungenerated | 430x932 | 1x | c95574be421a1c53a568c32f6bae1bf9e13164905e6d8ff6d1b6e0e38538e80d |
| waiting-320x568.png | waiting | 320x568 | 1x | 01ad9655c9935a5bfb24d89e24ae596e92d27e0cceb544fa84be90a69bb6e3c5 |
| waiting-390x844.png | waiting | 390x844 | 1x | d956369a919ef1e2b5352847675c74e37e9c7236a518eb8b5f8744ed02de4680 |
| waiting-430x932.png | waiting | 430x932 | 1x | 1cfd32db6ae881c88a1d45bd2fca96c3a02d5ff1e5ba0cf144827201f5919e65 |

## Verification evidence

- PASS：Playwright Chromium渲染13状态×3视口，共39张PNG；DPR=1。
- PASS：全部状态无脚本错误；根无横向溢出；正文≥14px，新增示例按钮≥44px。
- PASS：人工查看320px今日和390px条目样图；数字单位换行已修正并重导出。
- 结构证据：design-checks.json；HTML设计检查不能代替原生节点几何。
- NOT_RUN：原生小程序实现/三视口/iOS/Android；尚未批准具体修订，不作生产实现。
- 初次sandbox启动Chromium因MachPort权限失败；随后经权限审核允许启动后成功渲染。

## Approval gate

等待用户同时确认SPEC-20261007-FAIR-REVIEW-01与DREV-20261007-FAIR-REVIEW-01。
批准后冻结本源与导出hash；可见设计变化需新DREV。
