# UI-001 — 复习条目清单式改版候选设计证据

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261010-REVIEW-INVENTORY-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-001-REVIEW-INVENTORY-REDESIGN.md#SPEC-20261010-REVIEW-INVENTORY-REDESIGN-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-320x568.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-390x844.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-430x932.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-320x568.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-390x844.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-430x932.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-320x568.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-390x844.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-430x932.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-320x568.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-390x844.svg; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-430x932.svg
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-320x568.svg=13ae6eaa2358e39a8b573e489071eac10af61007d169a3ffe8ebe1c715ffec06; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-390x844.svg=12c4771f68eb8a8f77208c90780d8bf4e7bcc932d66fdc58fdb449b3ae55fa48; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/actions-430x932.svg=4f7843ba423cb7126477d216ad2b6fc661579e6232726fee4214d5b854d490df; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-320x568.svg=4d716f81e57364c1c8906370c75519fe007909d8fcf5f03c783c2cd50632fd7a; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-390x844.svg=0e305512378cf1f8b4e075083c3643de4b52549f5de92021051f1c4ea307ad1c; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/count-430x932.svg=a100a207cb055564d76f5c2ceabe1f0e816d83d6c44c4c3b5a3e884482d6548c; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-320x568.svg=696b93aa64c17ae9222e8e95099fd27a8921bf4ad9726b7ba30f06217b4c41aa; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-390x844.svg=2ff322648e4070f3d5c78895b02fb67a683645c67b78ca6d69693d5b6bd79b3d; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/subject-430x932.svg=3f3ee00ebd37b72a4cacf0367676e5f547befbff5ca72f12a63b451a03aac504; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-320x568.svg=348bd30f3eb4f5550b603c124eb943d1452759c2c872ffe101af6f2c031556da; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-390x844.svg=acd79b359724c52a2ff72f29ecc6c59bd410f7d162d901e6cb1c4a788bfdd6f7; docs/design/frontend/prototypes/DREV-20261010-REVIEW-INVENTORY-02/time-430x932.svg=cd94e2d57b31817106d47d389ec2a6d4288f7171f2020ef22c959e8b11d3c306
- Prototype generated/updated at: 2026-10-10
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-10
- Approval evidence: 用户审阅效果图及 SPEC-20261010-REVIEW-INVENTORY-REDESIGN-01 后回复“好的按照这个方案实现”
- Superseded by: N/A

## Scope

这版复用纸芽基线，批准“原生导航 + 单层筛选 + 同科清单 + 就近菜单”的可见方向。全部截图使用合成示例，不含真实儿童记录；不代表小程序已经修改或发布。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| actions-320x568.png | actions | 320x568 | 1x | 89858b9d132606225240f9eed6f7d4ae81e13506c8f211b347256e126dee02fc | 合成数据、静态效果图 |
| actions-390x844.png | actions | 390x844 | 1x | e9a9f2b1b8c87e04e240b9f5732d11eb06086b3c4d11b90d15a719b30ac8e5d0 | 合成数据、静态效果图 |
| actions-430x932.png | actions | 430x932 | 1x | ac968c3baa90e70ff8e5563302df9c8d3dbef53a86cbe4c04fbdaa21a3ac7ada | 合成数据、静态效果图 |
| count-320x568.png | count | 320x568 | 1x | e3a49624e7bc6f033d61ee152a55a06f50037704cd86dbdd150d563f43553f3e | 合成数据、静态效果图 |
| count-390x844.png | count | 390x844 | 1x | 29469c56e78899fea6b3746517e49b51f6725c5c83fc2a5323302a69aa8adfa4 | 合成数据、静态效果图 |
| count-430x932.png | count | 430x932 | 1x | b3edc0903e89f13bd022c54c35e944f24f667f1fddd767aca4a003dab5312994 | 合成数据、静态效果图 |
| subject-320x568.png | subject | 320x568 | 1x | 31c63fd5a4d3c72343f77726cfef22a07467d6cfe85a2b618ff3e7163a93434d | 合成数据、静态效果图 |
| subject-390x844.png | subject | 390x844 | 1x | 1b8b29ee951492d205e865aa552dc3fbefc2f848d8fe99db2a9163993170961c | 合成数据、静态效果图 |
| subject-430x932.png | subject | 430x932 | 1x | c49407f898a75e821d86492fd550a967569d674db8bb9a015023a8384026388f | 合成数据、静态效果图 |
| time-320x568.png | time | 320x568 | 1x | fc4ed90b43c745671084c77f5a4b77295d57630e87562068dacc95a554934e2a | 合成数据、静态效果图 |
| time-390x844.png | time | 390x844 | 1x | 0d0d3a427461eb5821086216dc64f192934f2627bbd7d30aab9770392555526d | 合成数据、静态效果图 |
| time-430x932.png | time | 430x932 | 1x | 1f08dea184cd1dbb0039344b75829904f12c21a30925b4427bed6d28964e69b4 | 合成数据、静态效果图 |

## Gaps and follow-up

- 科目/次数选择器展开、空/只读/错误/冲突/删除确认等风险状态在实施验收中补齐。
- PNG是SVG静态导出；微信原生节点几何、字体放大、iOS/Android真机与实际接口响应均尚未运行。
- 旧 DREV-20261007-REVIEW-GROUP-CARDS-01 清单保持原状态；本候选不改写其批准或证据。

## Integrity checklist

- [x] 每个可编辑SVG位于仓库内且SHA-256匹配。
- [x] 12张PNG对应4状态×3视口，尺寸和SHA-256匹配。
- [x] 用户确认本 Spec revision 与 Design Revision。
- [ ] 审阅后补齐实施所需状态与原生验证。
