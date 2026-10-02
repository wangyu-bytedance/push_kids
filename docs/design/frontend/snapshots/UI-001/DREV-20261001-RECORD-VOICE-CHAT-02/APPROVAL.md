# UI-001 — DREV-20261001-RECORD-VOICE-CHAT-02 Approval Snapshot

- Status: `SUPERSEDED_UNAPPROVED`
- UI ID: `UI-001`
- Design Revision: `DREV-20261001-RECORD-VOICE-CHAT-02`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/active/FEAT-001-VOICE-INPUT.md#SPEC-20261001-VOICE-INPUT-02`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-CHAT-02/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-CHAT-02/record-voice-chat.html`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-CHAT-02/record-voice-chat.html=be9d0bf4574b8f1ee7b6641d97d2f5f8edb4cacac9bc69585ae774ec81f5baa6`
- Prototype generated/updated at: `2026-10-01`
- Approved by: `pending explicit product-owner approval`
- Approved at: `pending explicit product-owner approval`
- Approval evidence: `pending explicit approval of SPEC-20261001-VOICE-INPUT-02 + DREV-20261001-RECORD-VOICE-CHAT-02`
- Superseded by: `DREV-20261001-RECORD-VOICE-INLINE-03`

## Approval identity

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-02 + DREV-20261001-RECORD-VOICE-CHAT-02`

## Candidate scope

- Surfaces/flows: 记录页“学习内容”的文字/语音模式切换；按住录音、松开转文字、上滑取消。
- States: `text`、`voice_ready`、`holding`、`appended` 有候选快照；授权、取消预备、识别中、错误和超长由 Frontend Spec 定义。
- Viewports: `320×568`、`390×844`、`430×932`，四个关键状态各一组候选。
- Interaction behavior: 模仿微信聊天输入习惯，但松开后只追加可编辑文字，不发送或保存语音消息。
- Copy/semantics: 不显示常驻录音状态卡，不增加停止按钮或撤回按钮；失败不丢照片、文字和时间。
- Privacy behavior: 音频不上传业务后端、不保存、不回放；临时路径、识别全文和插件响应不写日志或本地存储。
- Permitted implementation-only deviations: 原生字体 fallback、真实中文自然换行、微信系统隐私/授权弹窗外观。
- Explicitly not approved: 语音消息、后端 ASR、音频持久化、自动提交、自动确认、录音分析或学习评价。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `record-voice-text-320x568.png` | Record / text idle | 320×568 | 1x | `311c58cb989974df531aec648ba6c40bc3f66b1e2750f33db53bbb4d46b380c2` | narrow phone |
| `record-voice-text-390x844.png` | Record / text idle | 390×844 | 1x | `d414436a5b962480816bf1d2f090b1172ae28545e5c9293d13f0923beb6fc6c7` | reference viewport |
| `record-voice-text-430x932.png` | Record / text idle | 430×932 | 1x | `79475f1147d16015d0178509640a8dbbcc637af275594ce470532c7ea1f2ae8b` | wide phone |
| `record-voice-voice-320x568.png` | Record / voice ready | 320×568 | 1x | `ad5185281a0c4d65828f1049a635e814cfd5a3bf2202ae1ed5d5c189894fb2d4` | narrow phone; hold button visible |
| `record-voice-voice-390x844.png` | Record / voice ready | 390×844 | 1x | `cf38d28f769df25edccfa87f0a92aa8916153f70d18c62ed08d909bd9628ee3e` | reference viewport |
| `record-voice-voice-430x932.png` | Record / voice ready | 430×932 | 1x | `b734bb1f73a9baeccd2de06d1346dce6afc14b0c2c97eca3bf5b8f31495ce7b3` | wide phone |
| `record-voice-holding-320x568.png` | Record / holding | 320×568 | 1x | `9faab5f7994e8afa531dcae31404593c143dd278dc57ef6a3db2d5d50827da1a` | narrow phone; overlay visible |
| `record-voice-holding-390x844.png` | Record / holding | 390×844 | 1x | `0e1bfe7f5c23366aac14eeefe2197980c3cb5e88d9b114c3bb1a242a57254ddc` | reference viewport |
| `record-voice-holding-430x932.png` | Record / holding | 430×932 | 1x | `878de05529e085ad0c046f431331f738b05fa97291e4adf33c32bc806366c8c4` | wide phone |
| `record-voice-appended-320x568.png` | Record / transcript appended | 320×568 | 1x | `096cd3354729a37d8b063f9e16960a5069888f9d45da6ffd96bb8ec387161f3c` | review toast visible |
| `record-voice-appended-390x844.png` | Record / transcript appended | 390×844 | 1x | `09b3c2569b0c1bfae20b7ad7badaa1dbbc6ac2e4fa55a9f675f86134cc3cda80` | reference viewport |
| `record-voice-appended-430x932.png` | Record / transcript appended | 430×932 | 1x | `64017d34295ac869b64b83f3c7971c11327e4c3402b62b93cbfadd295ac4a06b` | wide phone |

## Gaps and follow-up

- States not represented: `requesting_permission`、`cancel_armed`、`recognizing`、`no_speech/error`、`overflow_review`；须由实现测试和原生验收覆盖。
- Manual assumptions: 候选中的文字和照片槽为无身份示意，不是识别准确率或真实数据证据。
- Native runtime evidence: `NOT_RUN — 当前仅为待批准设计；仓库导出不能替代微信开发者工具原生手势、节点几何、iOS/Android、真实授权、60 秒自动停止和大字体证据。`
- Commercial assumption: WechatSI 公开文档列出接口额度但未给出货币价格或 SLA；目标 AppID 的插件条款仍需在实施前核验。

## Integrity checklist

- [x] Editable source exists, is repository-local, and its SHA-256 matches.
- [x] Every listed export exists and its SHA-256 matches.
- [x] Required baseline viewports and four key states are represented; other states are explicitly listed.
- [ ] Product owner approved the named Task Spec revision and Design Revision.
- [ ] Manifest frozen after approval; any visible divergence creates a new Design Revision.
