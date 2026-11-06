# UI-018 — DREV-20261025-TRAVEL-IMPORT-02 Approval Snapshot

- Status: APPROVED
- UI ID: UI-018
- Design Revision: DREV-20261025-TRAVEL-IMPORT-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: specs/active/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md#SPEC-20261025-TRAVEL-IMPORT-SIMPLIFICATION-01
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261025-TRAVEL-IMPORT-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261025-TRAVEL-IMPORT-02/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261025-TRAVEL-IMPORT-02/index.html=4761538253e21b85f4ac255b36576cfb3e1620c40589367931350427a641e918
- Prototype generated/updated at: 2026-10-25 Asia/Shanghai
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-25
- Approval evidence: request_user_input_async/call_b44b8ace4cbe466886ae287d8a6e6051回复：“批准导入精简 Spec01＋Architecture01＋DREV02，按此实施”
- Superseded by: DREV-20261031-TRAVEL-ENTRY-CLEANUP-01（仅零草稿兜底与空态新建手动到访入口；直接相册、选择忙态、上传/失败及设置等原批准范围继续有效）

## Approved scope

导入精简Spec01/Architecture01/DREV02已获产品负责人明确批准。删除截图整块中间面板，直接系统相册；AI开关使用已有设置。5态×320/390/430共15张，沿用暖纸松绿与14px/44px/48px预算。截图仅HTML合成状态，没有真实照片或系统相册。旧批准DREV01源保持冻结。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| entry-320x568.png | VP-320/entry | 320×568 | 1x | ea7596743bad147758d852ef669a839ea722f88a74f1625a71366c4e4ab21a5c | Synthetic HTML design; not native |
| selecting-320x568.png | VP-320/selecting | 320×568 | 1x | 5943210078e3e13b3443879f7b3d3f93b567d8e98ba30b7e7f63c6bbfb503009 | Synthetic HTML design; not native |
| uploading-320x568.png | VP-320/uploading | 320×568 | 1x | f3a795c4d0eaa27440b7dc350ead37d82747b5cfae6b3595ff0105c9c4a3ebfa | Synthetic HTML design; not native |
| upload-error-320x568.png | VP-320/upload-error | 320×568 | 1x | cd9cb789e25608ace824028c739d385257f0f9aa381dc307ca7b3d1f3a15ee5d | Synthetic HTML design; not native |
| settings-320x568.png | VP-320/settings | 320×568 | 1x | be9c23506430d9a02e8eb6cdff3824e00948a8d724d02e2cb4992a21240ba590 | Synthetic HTML design; not native |
| entry-390x844.png | VP-390/entry | 390×844 | 1x | b050134e9f774551b20d1d0b04169d7f3c1729c0e5ffae5f31a0b6733c150710 | Synthetic HTML design; not native |
| selecting-390x844.png | VP-390/selecting | 390×844 | 1x | 73a0e88d9c90ae4c24b779da6552d72c40a1f3e4dc3ca016afaa5c87d08447d5 | Synthetic HTML design; not native |
| uploading-390x844.png | VP-390/uploading | 390×844 | 1x | 57d3aca0d1080abf0c47e31b406fbbea63a2513937dbbacb8502a745d96579ec | Synthetic HTML design; not native |
| upload-error-390x844.png | VP-390/upload-error | 390×844 | 1x | 296b104c6733a9920ba149a0b22541a2712c73645549607610193d45951fa3d8 | Synthetic HTML design; not native |
| settings-390x844.png | VP-390/settings | 390×844 | 1x | 39c51de4a6dc3858207f545a041facbd6b0bb8332bd06ea3396bf575256ae363 | Synthetic HTML design; not native |
| entry-430x932.png | VP-430/entry | 430×932 | 1x | 91f32188511b373bd0eef905a47181ad9ff70fdad616ec2163e84ee9d1a7f6b0 | Synthetic HTML design; not native |
| selecting-430x932.png | VP-430/selecting | 430×932 | 1x | 8ee98176bba5cb7df5920a5ca9e2c555cef4cd871c863c260ee44daa01f29bed | Synthetic HTML design; not native |
| uploading-430x932.png | VP-430/uploading | 430×932 | 1x | f9b6f6d6356cdf7db86e3b9b250e6a58bee278c95d23d5538e08daa5cedad766 | Synthetic HTML design; not native |
| upload-error-430x932.png | VP-430/upload-error | 430×932 | 1x | 03935088534c33775244448ef03febe56c54ffe05cba2cf62e500b40999c7778 | Synthetic HTML design; not native |
| settings-430x932.png | VP-430/settings | 430×932 | 1x | 2731b31be3f34e38a335cc82b1e2d7d82940922c229e8226410d47526b17a662 | Synthetic HTML design; not native |

## Gaps and follow-up

- HTML尺寸、触控/主CTA、横向边界、删字和演示点击通过；320短屏主操作滚动到导航上方后取证，scrollTop见render-audit.json。
- 系统相册、生产代码、原生三视口/实际动作与真机均NOT_RUN，待具体revision批准后执行。
- 已批准设计不代表代码已实施或发布；生产实现与原生证据在Task Spec记录。
