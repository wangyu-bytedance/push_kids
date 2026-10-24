# UI-001 — 今日学习空区与风格统一

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261024-TODAY-LEARNING-03
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md#SPEC-20261024-TODAY-CARD-VISIBILITY-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/index.html=282bc58dad29ac22e19338a2c9112848d4af73189f25a0ca98b1b209db53ea39
- Prototype generated/updated at: 2026-10-24
- Approved by: 用户
- Approved at: 2026-10-24
- Approval evidence: call_ac391833df284fc7b0afcb71c55abec7，用户回复「批准，按此实现」，明确批准Spec01和DREV03。
- Superseded by: N/A

## Approved scope

空区整体隐藏；有实际建议/待学时显示具体标题及元信息，沿用今日页分区/复习卡字阶与胶囊按钮。生成/失败/删除恢复保留必要状态与入口。DREV02弹层仍沿用已批准源，不改业务资格、权限、请求或正式记录。批准冻结时尚未修改生产组件；实现证据独立记录。

21态 × 320×568、390×844、430×932 = 63张PNG，1x/DPR1。proposal-long滚动至今日学习分区，其他顶部。只使用合成资料；原生/真机NOT_RUN。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| recent-new-320x568.png | UI-001/recent-new | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| warming-up-320x568.png | UI-001/warming-up | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| no-history-320x568.png | UI-001/no-history | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| missing-grade-320x568.png | UI-001/missing-grade | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| no-subject-320x568.png | UI-001/no-subject | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| disabled-320x568.png | UI-001/disabled | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| inactive-320x568.png | UI-001/inactive | 320×568 | 1x | 488c0dda80d98f3bca6759d21aa0a142f450e69a53f9059d394d786651202b05 | 合成设计，非原生验收 |
| eligible-empty-320x568.png | UI-001/eligible-empty | 320×568 | 1x | e507486bf530390a21b274a5f232672359e14df837312ec4bb07f97fca131cd2 | 合成设计，非原生验收 |
| viewer-empty-320x568.png | UI-001/viewer-empty | 320×568 | 1x | 0e07d049cd032a566f04a95249db1a3aac25a185ca9b6370ab85a87e44fe9b1d | 合成设计，非原生验收 |
| unknown-empty-320x568.png | UI-001/unknown-empty | 320×568 | 1x | 72860453d3a4e09f3c35fb0a411bf6a3d1be836576239a0f788620ea2aa0ed90 | 合成设计，非原生验收 |
| proposal-320x568.png | UI-001/proposal | 320×568 | 1x | d2b1f5710d2e984e0b8146235c72590b08267ef186905baea45c8f7841be2f81 | 合成设计，非原生验收 |
| proposal-long-320x568.png | UI-001/proposal-long | 320×568 | 1x | f32645812be5e88568287a45d1db9075e1d0ea006f05fb5d5630e965ea1ce935 | 合成设计，非原生验收 |
| task-320x568.png | UI-001/task | 320×568 | 1x | 8486ebac6f3e851d3706aedbc6155be9f4994c6856fb00cc317a71f03b77f474 | 合成设计，非原生验收 |
| partial-320x568.png | UI-001/partial | 320×568 | 1x | ea66e9bc560938d7576470e590aeafbedf28c2a4f79b58cc9154c9a327fdba56 | 合成设计，非原生验收 |
| viewer-task-320x568.png | UI-001/viewer-task | 320×568 | 1x | 650d930fff18f799a197d9dd0f24499865008ed5e2996a130ba51cd38c22b298 | 合成设计，非原生验收 |
| task-feature-off-320x568.png | UI-001/task-feature-off | 320×568 | 1x | 8486ebac6f3e851d3706aedbc6155be9f4994c6856fb00cc317a71f03b77f474 | 合成设计，非原生验收 |
| generating-320x568.png | UI-001/generating | 320×568 | 1x | a6cd1c26478e6311336857c56b5894f4f670b8ba0acd34756de43c97a9d7307f | 合成设计，非原生验收 |
| generation-error-320x568.png | UI-001/generation-error | 320×568 | 1x | 3afd0f807358ba38d176288e8419704cb48917712fd26bf89ecb23998a848ded | 合成设计，非原生验收 |
| stale-320x568.png | UI-001/stale | 320×568 | 1x | 2fe85cdaf58c67b9d99b0cebe7f0534803bd876c706f72a03cbf94414b394223 | 合成设计，非原生验收 |
| recover-after-remove-320x568.png | UI-001/recover-after-remove | 320×568 | 1x | 1281c8a5fbf6e6e075b17cba2abeb9994a1cb55fb7b796f31ebdd951a1cba7e0 | 合成设计，非原生验收 |
| network-error-320x568.png | UI-001/network-error | 320×568 | 1x | 4a15b53387d766e54a3169b95f02e89af1468873d4e89679dd5cb405d67158c8 | 合成设计，非原生验收 |
| recent-new-390x844.png | UI-001/recent-new | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| warming-up-390x844.png | UI-001/warming-up | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| no-history-390x844.png | UI-001/no-history | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| missing-grade-390x844.png | UI-001/missing-grade | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| no-subject-390x844.png | UI-001/no-subject | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| disabled-390x844.png | UI-001/disabled | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| inactive-390x844.png | UI-001/inactive | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| eligible-empty-390x844.png | UI-001/eligible-empty | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| viewer-empty-390x844.png | UI-001/viewer-empty | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| unknown-empty-390x844.png | UI-001/unknown-empty | 390×844 | 1x | 74e4db773372b74bc0b103f45a38bb016eb67f4537db44676e2cb162cadb9d4b | 合成设计，非原生验收 |
| proposal-390x844.png | UI-001/proposal | 390×844 | 1x | 5a4a3578749b90322dca13686db64ee2cbea7874b100b07504e2907f5d76f8c3 | 合成设计，非原生验收 |
| proposal-long-390x844.png | UI-001/proposal-long | 390×844 | 1x | 659a2b69199b0e9a8a6a5bbd3cef7c461238a7152d3ef6f974a9e4501592be02 | 合成设计，非原生验收 |
| task-390x844.png | UI-001/task | 390×844 | 1x | a03a89ef28608106ef1c0cd9b41a7b495cce0da7356095f805a1b92d97dff5a5 | 合成设计，非原生验收 |
| partial-390x844.png | UI-001/partial | 390×844 | 1x | f9ceebbe3f1efbdda960754b0e12b647d1a736aa382f84c2dbd7ff1b8c8fcb98 | 合成设计，非原生验收 |
| viewer-task-390x844.png | UI-001/viewer-task | 390×844 | 1x | 378b3dcdbdc4c33b81b4a94b53f52e9d45d15d8a19b7ad385fdf793ac508e9ab | 合成设计，非原生验收 |
| task-feature-off-390x844.png | UI-001/task-feature-off | 390×844 | 1x | a03a89ef28608106ef1c0cd9b41a7b495cce0da7356095f805a1b92d97dff5a5 | 合成设计，非原生验收 |
| generating-390x844.png | UI-001/generating | 390×844 | 1x | c0a09ebeeb361a286a1403f8f7eb749e8c2413f69b29a89510547082634e18c1 | 合成设计，非原生验收 |
| generation-error-390x844.png | UI-001/generation-error | 390×844 | 1x | 10e97098814e2918f9a8345889b3a900b85b23966d977ac0d97daede7c5c9db3 | 合成设计，非原生验收 |
| stale-390x844.png | UI-001/stale | 390×844 | 1x | a32d34bc74426105c114dec2cbba25604d4caa78914732e836ac51ea3333750c | 合成设计，非原生验收 |
| recover-after-remove-390x844.png | UI-001/recover-after-remove | 390×844 | 1x | a0caf794bc7f34ded383e9d8c07086bf5101d4f4d3e2d384b5ea37bb49e1f362 | 合成设计，非原生验收 |
| network-error-390x844.png | UI-001/network-error | 390×844 | 1x | 3c02b256021a978d489d9b208a8f6ccd422400feb1bed5e1c11fd12a72b94f83 | 合成设计，非原生验收 |
| recent-new-430x932.png | UI-001/recent-new | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| warming-up-430x932.png | UI-001/warming-up | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| no-history-430x932.png | UI-001/no-history | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| missing-grade-430x932.png | UI-001/missing-grade | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| no-subject-430x932.png | UI-001/no-subject | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| disabled-430x932.png | UI-001/disabled | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| inactive-430x932.png | UI-001/inactive | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| eligible-empty-430x932.png | UI-001/eligible-empty | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| viewer-empty-430x932.png | UI-001/viewer-empty | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| unknown-empty-430x932.png | UI-001/unknown-empty | 430×932 | 1x | 0841ab7f422f987a87ef9a972f189d906ebf09f380f8f8c479b0ffe60a9a20aa | 合成设计，非原生验收 |
| proposal-430x932.png | UI-001/proposal | 430×932 | 1x | 9392737bdc96d86604f3a1eb12eb1d76132c74da061e45b421b494b9f8aef2f6 | 合成设计，非原生验收 |
| proposal-long-430x932.png | UI-001/proposal-long | 430×932 | 1x | 7d35c0ef660d932369fa16f0c8c4e1a86c6751ad2ac249a87fc39473ddbac778 | 合成设计，非原生验收 |
| task-430x932.png | UI-001/task | 430×932 | 1x | 354a860ce176bf711f5cf63eb5618b3674997d27e344a12561fe3622653fd5f7 | 合成设计，非原生验收 |
| partial-430x932.png | UI-001/partial | 430×932 | 1x | 3aeac70e06bc1ef697436ffe0ab659b771f5cc5833e7d30bf04a213a127f49a8 | 合成设计，非原生验收 |
| viewer-task-430x932.png | UI-001/viewer-task | 430×932 | 1x | 1f372bc3670336445dabdec77218292253bc903b2668266027d374c5b8664d0b | 合成设计，非原生验收 |
| task-feature-off-430x932.png | UI-001/task-feature-off | 430×932 | 1x | 354a860ce176bf711f5cf63eb5618b3674997d27e344a12561fe3622653fd5f7 | 合成设计，非原生验收 |
| generating-430x932.png | UI-001/generating | 430×932 | 1x | 133dd9675292eb224334a84a97e7aa1c50c16b0092416f5760114eeec054ec38 | 合成设计，非原生验收 |
| generation-error-430x932.png | UI-001/generation-error | 430×932 | 1x | d498ae4543bbea948c5edb783062ad4c5786f778f4d4e9f870345ea119a3663d | 合成设计，非原生验收 |
| stale-430x932.png | UI-001/stale | 430×932 | 1x | 1e37d21064655bc258c7d24f46a52ff3653805913722e4a5890d583d51ca3ebe | 合成设计，非原生验收 |
| recover-after-remove-430x932.png | UI-001/recover-after-remove | 430×932 | 1x | 639fe89e5c445c1d40fb58ea1e08fbb9ca77b60b2bc32984855a84b0472c74e5 | 合成设计，非原生验收 |
| network-error-430x932.png | UI-001/network-error | 430×932 | 1x | d84b356c85b1bc635f45c47442c4d4704a543f251a4ebd2fdce0d6891267a811 | 合成设计，非原生验收 |

## Verification

63张布局检查通过；10种空态无分区、无额外间距；分区字体与复习安排一致，具体标题16px，正文≥14px，所有操作≥44px且横向包含。8个入口跳至已批准DREV02相应弹层；Runtime异常0。详细报告见prototype目录render-report.json和TODAY-CARD-DESIGN-20261024.md。

此清单尚未批准。批准后HTML/PNG/SHA冻结；旧DREV01/02目前不新增Superseded by。
