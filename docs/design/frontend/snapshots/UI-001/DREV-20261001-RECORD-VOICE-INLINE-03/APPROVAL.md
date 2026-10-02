# UI-001 — DREV-20261001-RECORD-VOICE-INLINE-03 Approval Snapshot

- Status: `APPROVED`
- UI ID: `UI-001`
- Design Revision: `DREV-20261001-RECORD-VOICE-INLINE-03`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/active/FEAT-001-VOICE-INPUT.md#SPEC-20261001-VOICE-INPUT-03`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INLINE-03/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INLINE-03/record-voice-inline.html`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INLINE-03/record-voice-inline.html=2364267c8dc25b876a893d6436e15d9067e3b76d2ec1d72e0467b52ab21722cd`
- Prototype generated/updated at: `2026-10-01`
- Approved by: `产品负责人（用户）`
- Approved at: `2026-10-01`
- Approval evidence: `用户在收到 SPEC-20261001-VOICE-INPUT-03 + DREV-20261001-RECORD-VOICE-INLINE-03 的明确批准请求后回复“你先来实现代码，然后进行充分测试，前端交互可以慢慢调整”`
- Superseded by: `N/A`

## Approval identity

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-03 + DREV-20261001-RECORD-VOICE-INLINE-03`

## Candidate scope

- Surfaces/flows: 记录页“学习内容”紧凑输入框；右下角内嵌麦克风直接长按录音。
- States: `idle`、`holding`、`appended` 有候选快照；授权、取消预备、识别中、错误和超长由 Frontend Spec 定义。
- Viewports: `320×568`、`390×844`、`430×932`，三个关键状态各一组候选。
- Interaction behavior: 无外置按钮和模式切换；按住麦克风、松开转文字、上滑取消。
- Copy/semantics: 松开只追加可编辑文字，不发送语音消息、不提交记录。
- Privacy behavior: 音频不上传业务后端、不保存、不回放；临时路径、识别全文和插件响应不写日志或本地存储。
- Permitted implementation-only deviations: 原生字体 fallback、真实中文自然换行、微信系统隐私/授权弹窗外观。
- Explicitly not approved: 语音消息、后端 ASR、音频持久化、自动提交、自动确认、录音分析或学习评价。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `record-voice-idle-320x568.png` | Record / idle | 320×568 | 1x | `5d4cc9d966b23596152276317987e674b2be19bd224bb64643a9f3a02ed317f3` | narrow phone; inline mic visible |
| `record-voice-idle-390x844.png` | Record / idle | 390×844 | 1x | `e22db2dc4b55523e9e19edb928159652789909e90d42ea7fe50085a0e98b2e4e` | reference viewport |
| `record-voice-idle-430x932.png` | Record / idle | 430×932 | 1x | `cb8e00b0b04b98bb4a359bb3c53e05e14678419efd4451e3722104e5b862bf80` | wide phone |
| `record-voice-holding-320x568.png` | Record / holding | 320×568 | 1x | `9174ce1f5fac8844a28222045fbc611208c4cf40d3ef3d3f10fe769c802d67fe` | narrow phone; in-field feedback |
| `record-voice-holding-390x844.png` | Record / holding | 390×844 | 1x | `39a35c654e9133924738501158da8ad53614d5a3bd2469e29009de5b9f237235` | reference viewport |
| `record-voice-holding-430x932.png` | Record / holding | 430×932 | 1x | `8fe9e804f6a59e91ada68836f539a2d72bc990f521d48ccffc347df11ace0d05` | wide phone |
| `record-voice-appended-320x568.png` | Record / transcript appended | 320×568 | 1x | `4d3ea801de40b5ba984830a01de0310e9dabc0e39cab2d998efc460a73e5db77` | narrow phone; editable text visible |
| `record-voice-appended-390x844.png` | Record / transcript appended | 390×844 | 1x | `7d3ebbfa17d957cbda432db9c0ed48571429c1a3394f5ffbe05a8d3f888d9293` | reference viewport |
| `record-voice-appended-430x932.png` | Record / transcript appended | 430×932 | 1x | `b941d436bf554cc923e2f11208e77b374b05e57fdb3f8a5bf2ffc1e790788338` | wide phone |

## Gaps and follow-up

- States not represented: `requesting_permission`、`cancel_armed`、`recognizing`、`no_speech/error`、`overflow_review`；须由实现测试和原生验收覆盖。
- Manual assumptions: 候选中的文字和照片槽为无身份示意，不是识别准确率或真实数据证据。
- Native runtime evidence: `NOT_RUN — 当前仅为待批准设计；仓库导出不能替代微信开发者工具原生长按/上滑手势、节点几何、iOS/Android、真实授权、60 秒自动停止和大字体证据。`
- Commercial assumption: WechatSI 公开文档列出接口额度但未给出货币价格或 SLA；目标 AppID 的插件条款仍需在实施前核验。

## Integrity checklist

- [x] Editable source exists, is repository-local, and its SHA-256 matches.
- [x] Every listed export exists and its SHA-256 matches.
- [x] Required baseline viewports and three key states are represented; other states are explicitly listed.
- [x] Product owner approved the named Task Spec revision and Design Revision.
- [x] Manifest frozen after approval; any visible divergence creates a new Design Revision.
