# 每日任务设计候选审批清单

- Status: APPROVED
- Task Spec: SPEC-20261012-DAILY-TASKS-01
- Design Revision: DREV-20261012-DAILY-TASKS-01
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02
- Approver / Date / Message: 产品负责人（用户） / 2026-10-12 / 「好的按照这个方案实现前后端代码。」

- UI ID: UI-001
- Design Revision: DREV-20261012-DAILY-TASKS-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-010-DAILY-TASKS.md / SPEC-20261012-DAILY-TASKS-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261012-DAILY-TASKS-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261012-DAILY-TASKS-01/design.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261012-DAILY-TASKS-01/design.html=5a166972fb9d75227db5ce7bee7675485a55eeb84c81bf6f5832cac83c1aa89f
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-12
- Approval evidence: 本聊天消息「好的按照这个方案实现前后端代码。」
- Export engine: Google Chrome / Playwright，2026-10-12
- Viewports: 320×568、390×844、430×932；device scale factor 1。
- States: settings、today、completed、empty、form-error。
- 限制：设置长页需滚动；窄屏首屏错误提示在折线下方，本候选仅为设计预览，原生键盘、控件几何和真机验收 NOT_RUN。
- 本设计为受影响区块的增量稿，已有 Hero 与其他设置卡片沿用获批基线。
- External design dependency: none

| File | SHA-256 |
|---|---|
| docs/design/frontend/prototypes/DREV-20261012-DAILY-TASKS-01/design.html | 5a166972fb9d75227db5ce7bee7675485a55eeb84c81bf6f5832cac83c1aa89f |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/completed-320x568.png | c20b8d70cb87f0a804dfa5288f6ec07239c72f23d2aa10516bfa451178f872a4 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/completed-390x844.png | 18069db474fc3a7e84ab18c32070b3230c33d21bc1895c56c8bc4770584b331c |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/completed-430x932.png | 525cfe2a27a4ac194f91774fe44af2135b09dd96c5623c0c53f5fa7c6435c113 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/empty-320x568.png | 79b9783a114ab34f03638ade32e178bbe09b43cf449a6f4110e3c76f5edad765 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/empty-390x844.png | c4ad714f943d257d347043288879d34a20d6918b5cbbb8b0ea6a90b42798aa1b |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/empty-430x932.png | 98654e9267dfecdeccb64bc743fdeb35b80f977673dabc08a076bad71a48dffa |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/form-error-320x568.png | f1db7a3e9ba032d6b2ee3d755a3860b45edb2c0d04bdcac39e024e62ea2382c4 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/form-error-390x844.png | b695f1672cf6693d912985f8e00737c24f4d0d7a6a79d428ef1df19a1a483819 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/form-error-430x932.png | 83f434afc739c983e5db991ee1d543e7e894ac6b95591892bfef519450833f7a |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/settings-320x568.png | f1db7a3e9ba032d6b2ee3d755a3860b45edb2c0d04bdcac39e024e62ea2382c4 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/settings-390x844.png | 2230435bc52cc9e470dedba581787868aa9a40eb22bc3b77f9c076719d8505cb |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/settings-430x932.png | a0d6905c40ffd30b5812baee2efa7e9cb8354cf52ab7ca4558938b14dd5fa749 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/today-320x568.png | 09c0bc0af089788266570261b707ee76bfcadc0971a2bc2f8d9299923601e375 |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/today-390x844.png | 190a8a3c42a2b06c6de118dfd40eaefe2b6525d510d2c29c5355c646c65520da |
| docs/design/frontend/snapshots/UI-001/DREV-20261012-DAILY-TASKS-01/today-430x932.png | 29c8dcf18c2f359b5cff783316be1de4a8873a46218a03149f9c0660aaa51ada |

## Export manifest

| File | State | CSS viewport | Scale | SHA-256 |
|---|---|---|---|---|
| completed-320x568.png | completed | 320×568 | 1x | c20b8d70cb87f0a804dfa5288f6ec07239c72f23d2aa10516bfa451178f872a4 |
| completed-390x844.png | completed | 390×844 | 1x | 18069db474fc3a7e84ab18c32070b3230c33d21bc1895c56c8bc4770584b331c |
| completed-430x932.png | completed | 430×932 | 1x | 525cfe2a27a4ac194f91774fe44af2135b09dd96c5623c0c53f5fa7c6435c113 |
| empty-320x568.png | empty | 320×568 | 1x | 79b9783a114ab34f03638ade32e178bbe09b43cf449a6f4110e3c76f5edad765 |
| empty-390x844.png | empty | 390×844 | 1x | c4ad714f943d257d347043288879d34a20d6918b5cbbb8b0ea6a90b42798aa1b |
| empty-430x932.png | empty | 430×932 | 1x | 98654e9267dfecdeccb64bc743fdeb35b80f977673dabc08a076bad71a48dffa |
| form-error-320x568.png | form-error | 320×568 | 1x | f1db7a3e9ba032d6b2ee3d755a3860b45edb2c0d04bdcac39e024e62ea2382c4 |
| form-error-390x844.png | form-error | 390×844 | 1x | b695f1672cf6693d912985f8e00737c24f4d0d7a6a79d428ef1df19a1a483819 |
| form-error-430x932.png | form-error | 430×932 | 1x | 83f434afc739c983e5db991ee1d543e7e894ac6b95591892bfef519450833f7a |
| settings-320x568.png | settings | 320×568 | 1x | f1db7a3e9ba032d6b2ee3d755a3860b45edb2c0d04bdcac39e024e62ea2382c4 |
| settings-390x844.png | settings | 390×844 | 1x | 2230435bc52cc9e470dedba581787868aa9a40eb22bc3b77f9c076719d8505cb |
| settings-430x932.png | settings | 430×932 | 1x | a0d6905c40ffd30b5812baee2efa7e9cb8354cf52ab7ca4558938b14dd5fa749 |
| today-320x568.png | today | 320×568 | 1x | 09c0bc0af089788266570261b707ee76bfcadc0971a2bc2f8d9299923601e375 |
| today-390x844.png | today | 390×844 | 1x | 190a8a3c42a2b06c6de118dfd40eaefe2b6525d510d2c29c5355c646c65520da |
| today-430x932.png | today | 430×932 | 1x | 29c8dcf18c2f359b5cff783316be1de4a8873a46218a03149f9c0660aaa51ada |

