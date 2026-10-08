# UI-001 — 复习条目科目组卡候选设计证据

- Status: AWAITING_EXPORT
- UI ID: UI-001
- Design Revision: DREV-20261007-REVIEW-GROUP-CARDS-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Task Spec path and revision: specs/active/FEAT-001-REVIEW-INVENTORY-GROUPED-CARDS.md#SPEC-20261007-REVIEW-GROUP-CARDS-04
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261007-REVIEW-GROUP-CARDS-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261007-REVIEW-GROUP-CARDS-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261007-REVIEW-GROUP-CARDS-01/index.html=368234b7d915c1c3be2bdb2692307fc8ae37de4f0a3e1bf6e01f116a15b03457
- Prototype generated/updated at: 2026-10-07
- Approved by: 产品负责人（用户）确认交互与布局方向；完整设计证据待验收
- Approved at: 2026-10-07（方向确认）
- Approval evidence: 本会话消息“好的 按照这个方式修改代码 然后部署前端”；对应 SPEC-20261007-REVIEW-GROUP-CARDS-04 与 DREV-20261007-REVIEW-GROUP-CARDS-01
- Superseded by: N/A

## Scope

复习条目页使用用户提供的“今日复习安排”科目卡片布局，并按后续反馈支持逐科折叠：暖白组卡、松绿左缘、科目字标、组头本页项数与箭头、展开后组内分隔和每项尾部“…”操作。首科默认展开，其他科默认收起，各组可独立开合。“…”就近展开非模态下拉菜单，不再使用底部调整面板；删除保留独立确认。时间筛选两列，科目/次数筛选三列等宽；“指定次数”不是预置4次，只有输入确认后才显示所选值。按当前游标页分组，保留原API/筛选/调整语义。示例内容为合成，不含真实孩子数据。原型里的按钮仅演示视觉和导航；不发送网络请求或写数据。

## Previous exports (stale; do not approve against these)

| File | State | CSS viewport | Scale | SHA-256 |
|---|---|---|---|---|
| actions-320x568.png | actions | 320x568 | 1x | ccf12e88a7777686d7351b08f28184a3838788eea1f3257d9c276d8f4c5a56f0 |
| actions-390x844.png | actions | 390x844 | 1x | f1933efffb265e2d791c29efcf4a707ce99d43f46c912029ee43812bee9afd57 |
| actions-430x932.png | actions | 430x932 | 1x | 302d509415e2f3ea2dc770f4fa317ef839b2c4f8aeea84898b65959df393e80f |
| count-320x568.png | count | 320x568 | 1x | f66f29671d6ab5af43edf2cddf0608f1464b8621490ea4a1477d0cc686384b81 |
| count-390x844.png | count | 390x844 | 1x | 879bc629988ce15e91b41279ee6154835836b38843e1b5e92474b37de61b4a7c |
| count-430x932.png | count | 430x932 | 1x | a805a693bf762ab98220590ca9f15897ce86be4aa002846bdba4202536963309 |
| empty-320x568.png | empty | 320x568 | 1x | dfe8f838692c6b8a78f90be3df0b3ba5a86d72b16a129b508ea6c5ae153b03ef |
| empty-390x844.png | empty | 390x844 | 1x | beb87115b0fe704bf35c08f9e305a245603660344599155b4ac2088450a65126 |
| empty-430x932.png | empty | 430x932 | 1x | 4f7216d49f4e7374216e1e32a6d133c3953dac377a9a48925f5db409b80f255d |
| long-320x568.png | long | 320x568 | 1x | ee24d1bbba67a0e81598c196622c2cd850ed8dabc0c389a055aac15c3336903d |
| long-390x844.png | long | 390x844 | 1x | 7526ae0d4356be40e1cdc28bee1ce67f05f4d4bdec9286c52a07ee20c35ff653 |
| long-430x932.png | long | 430x932 | 1x | dd909787a06554e562d0ff83432035bbea832c3c2cfbaaa3ac226cb64a6297b5 |
| readonly-320x568.png | readonly | 320x568 | 1x | b7d6132cb5681436dfa6ee308f99a6a3c8105f2cf722ede910690ec26ff35ffa |
| readonly-390x844.png | readonly | 390x844 | 1x | 81a0c310cc589d3eb7014d2d01c3d3fb5005d20836a42394cd47b714177ea364 |
| readonly-430x932.png | readonly | 430x932 | 1x | 7ff1c2c13576a58ec0213fa9f6e1432aac27d843817955bbe66f64b4c53d2577 |
| subject-320x568.png | subject | 320x568 | 1x | a1243749b8a2087e13be247ade744d5cf8290a47b59f320a57fe95c43a1a6eda |
| subject-390x844.png | subject | 390x844 | 1x | 3221e21fb2afd79cc82316221d264420c55377f92332a8db4f9124df22c993bf |
| subject-430x932.png | subject | 430x932 | 1x | 5e9b3d540df9bdb26ce79084d7bfb95e78eafe6bdf15cd9958b3be4aa9ce9788 |
| time-320x568.png | time | 320x568 | 1x | 52bdd1e1e1f0aed431d5dbf5457d4f7536f989428a682ae436922c97db017778 |
| time-390x844.png | time | 390x844 | 1x | cb1ba8a8834a3ece6196460be2809af607d8aba3f905ae4b06260fe86318903f |
| time-430x932.png | time | 430x932 | 1x | 4e9dca29647d02e8e4ba7a475ac9c25f6e08ea67cc3caf8090f69221c9c7cebb |

## Verification evidence

- STALE：下表24张PNG是更早版本的截图；“…”下拉菜单和筛选等宽/动态次数修订后未重新导出，不能作为当前设计视觉或几何证据。新矩阵需10状态×3视口。
- PASS：本次自包含HTML内脚本通过Node语法检查；无浏览器DOM模拟检查确认未输入时显示“指定次数”、输入7后才显示7次、非法值不提交、科目筛选仍在。
- NOT_RUN：本次菜单和筛选的三视口截图、可见按钮几何、页面溢出与真实点击交互复验。浏览器工具的本地 `file://` 访问被安全策略拒绝，不能以其他浏览器入口绕过。
- NOT_RUN：微信小程序新版原生节点几何、iOS和Android；本地开发者工具已打开，但当前是今日页，不将其截图称为目标页新版验收。

## Approval gate

产品负责人已确认本版交互与布局方向。当前缺少与源码一致的三视口截图和原生几何证据；这些证据补齐并验收前，不能把本清单标记为完整的发布设计证据。
