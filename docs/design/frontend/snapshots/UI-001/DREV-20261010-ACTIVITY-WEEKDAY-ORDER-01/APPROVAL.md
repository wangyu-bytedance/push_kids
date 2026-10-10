# 活动星期排序 — 候选设计 manifest

- Status: APPROVED
- Task Spec: SPEC-20261010-ACTIVITY-WEEKDAY-ORDER-02
- Design Revision: DREV-20261010-ACTIVITY-WEEKDAY-ORDER-01
- Baseline: FDB-20260913-04
- Engineering contract: FEC-20261007-NATIVE-GEOMETRY-02
- Owner: 产品负责人（用户）
- Approval: 产品负责人（用户），2026-10-10，本会话“按照这个方案实现”；原UI不变，只排序。
- Scope: 设置页课外活动列表顺序；示意为滚动到该区块的局部视图，不授权改变现有样式、图标或布局。
- Editable source: docs/design/frontend/prototypes/DREV-20261010-ACTIVITY-WEEKDAY-ORDER-01/activity-order.svg
- Source SHA-256: 450a440a0d428f2edf3c30d919e04dc5d1c31985b0cd08307dfb1ca18be58c7e
- Draft correction: 2026-10-10用户要求原UI不变，并指出钢琴/围棋排序错误；仅修正未批准候选设计的顺序，禁止改变现有WXML/WXSS。
- 空/错态导出为独立可编辑SVG。原有全页状态、权限、图标及恢复文案沿用既有UI-001；本示意只表达内容顺序和无内容状态，不作为现有文案替换指令。
- Native evidence: NOT_RUN；这些SVG仅用于设计批准，不代替微信原生三视口截图或节点矩形验收。
- Approval immutability: 获批后仅允许添加 Superseded by 指针；后续视觉变更另立revision。

| Export | Viewport | State | SHA-256 |
|---|---|---|---|
| content-320x568.svg | 320×568 | content | c4b5226fb12ea79017d55e18c10444e35c9d2bbb0567124eb94bb0873e216910 |
| empty-320x568.svg | 320×568 | empty | 7b537ae1aa45899289a8e305fb4d1891499c316d0ecd568322e5267c8d7c721c |
| error-320x568.svg | 320×568 | error | 186a4e5d4240d33af257ed49a57563bf538162b167e4f4bbc0b93ebb0376391d |
| content-390x844.svg | 390×844 | content | 450a440a0d428f2edf3c30d919e04dc5d1c31985b0cd08307dfb1ca18be58c7e |
| empty-390x844.svg | 390×844 | empty | 70e04f2097dba55d7389de057e848c1e5b25fb2c706d519558bb8cdd42aca125 |
| error-390x844.svg | 390×844 | error | 1f63575a3a05f80b7c680f815147e510928be9363a26444bce058451c0477169 |
| content-430x932.svg | 430×932 | content | c8ef1efdab269e814d3ee2b36a7ec213a1323805a29c682538b1450a0a311661 |
| empty-430x932.svg | 430×932 | empty | 608af1e10ed4fe97fc38dd12f5431e6350b3f9ad700092fbc5202ea3716cab9a |
| error-430x932.svg | 430×932 | error | feaa967ad56cdafd16a3d985023ad579f71a4d2d871308e9962ecc88c5313b08 |

内容示例：游泳（周一）→围棋（周三09:00）→钢琴（首时段周三19:00）→舞蹈（周日）→绘画（未设置）→篮球（时间不固定）。同星期按首时段开始时间升序，同星期同时间保持原始列表顺序。
