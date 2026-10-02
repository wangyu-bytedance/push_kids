# UI-001 — DREV-20261001-RECORD-VOICE-INPUT-01 Approval Snapshot

- Status: `SUPERSEDED_UNAPPROVED`
- UI ID: `UI-001`
- Design Revision: `DREV-20261001-RECORD-VOICE-INPUT-01`
- Frontend baseline revision: `FDB-20260913-04`
- Frontend engineering revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Task Spec path and revision: `specs/active/FEAT-001-VOICE-INPUT.md#SPEC-20261001-VOICE-INPUT-01`
- Frontend spec path: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INPUT-01/FRONTEND-SPEC.md`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INPUT-01/record-voice-input.html`
- Editable source SHA-256: `docs/design/frontend/prototypes/DREV-20261001-RECORD-VOICE-INPUT-01/record-voice-input.html=e95cb2129ba3ce75ef3fd85ac7a38e72522d3c28328dd98786cb2b6b072a1ea5`
- Prototype generated/updated at: `2026-10-01`
- Approved by: `pending explicit product-owner approval`
- Approved at: `pending explicit product-owner approval`
- Approval evidence: `pending explicit approval of SPEC-20261001-VOICE-INPUT-01 + DREV-20261001-RECORD-VOICE-INPUT-01`
- Superseded by: `DREV-20261001-RECORD-VOICE-CHAT-02`

## Approval identity

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-01 + DREV-20261001-RECORD-VOICE-INPUT-01`

## Candidate scope

- Surfaces/flows: 记录页“学习内容”字段；客户端录音、转写、追加与撤回。
- States: `idle`、`recording`、`appended` 有候选快照；授权、转写中、无语音、权限拒绝、依赖失败、超长审阅和保存状态由 Frontend Spec 定义。
- Viewports: `320×568`、`390×844`、`430×932`，三个关键状态各一组候选。
- Interaction behavior: 点击开始、点击停止；最长 60 秒；转写结果只追加到现有草稿并由家长核对；失败不丢照片、文字和时间。
- Copy/semantics: 语音是现有文字输入的辅助方式，不是独立记录来源；不会自动提交、自动确认或评价孩子。
- Privacy behavior: 音频不上传业务后端、不保存、不回放；临时路径、识别全文和插件原始响应不写日志或本地存储。
- Permitted implementation-only deviations: 原生字体 fallback、真实中文自然换行、微信系统隐私/授权弹窗外观。
- Explicitly not approved: 后端 ASR、保存/上传音频、语音历史来源、自动提交、自动确认、录音分析或学习评价。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| `record-voice-idle-320x568.png` | Record / idle | 320×568 | 1x | `bedd0f9011cb12741d16d3b7f4de97d92afefe29626acfe5c4ca0d37e8733844` | narrow phone; voice entry visible |
| `record-voice-idle-390x844.png` | Record / idle | 390×844 | 1x | `4e892eef89415337c7ebda2780e34536fc6b806ba45aab132867da24a2f67b8c` | reference viewport |
| `record-voice-idle-430x932.png` | Record / idle | 430×932 | 1x | `1f49bd4d2ec7f9cb99fcede9302e13d4c05e31ba47ac339b1afe0e2e26e3d1ed` | wide phone |
| `record-voice-recording-320x568.png` | Record / recording | 320×568 | 1x | `fed2b75f593d5589d2c5f99ab0db95d2f59816e5b1b86b5c507175d10923d75b` | state panel scrolled into view |
| `record-voice-recording-390x844.png` | Record / recording | 390×844 | 1x | `fa5f91cd9ece32240cca289373405d91e647cd2566e873301854ba296aa8c773` | reference viewport |
| `record-voice-recording-430x932.png` | Record / recording | 430×932 | 1x | `83e6b4d36627922e202b62fc6ddcb582951ef423d42b9ebc6bdf2c04f6f2627d` | wide phone |
| `record-voice-appended-320x568.png` | Record / transcript appended | 320×568 | 1x | `37c2c4fd0f3fb4c66cf0e42f41e0550392a3e867f4ad9457d36b2117bd063aa2` | review notice and undo visible |
| `record-voice-appended-390x844.png` | Record / transcript appended | 390×844 | 1x | `a62a67fb898115d6bf7ea85999f553f28c190db52a71d342b52f12a1a5ac0222` | reference viewport |
| `record-voice-appended-430x932.png` | Record / transcript appended | 430×932 | 1x | `905165122edef2305564c92481fd2a3c2b1a6545eb97ddcde8ff60651fbf821b` | wide phone |

## Gaps and follow-up

- States not represented: `requesting_permission`、`recognizing`、`no_speech`、`permission_denied`、`dependency_error`、`overflow_review`、`saving`；须由实现测试和原生验收覆盖。
- Manual assumptions: 候选中的学习文字和照片槽为无身份示意内容，不是识别准确率或真实数据证据。
- Native runtime evidence: `NOT_RUN — 当前仅为待批准设计；仓库导出不能替代微信开发者工具原生节点几何、iOS/Android、真实授权、60 秒自动停止、前后台中断和大字体证据。`
- Commercial assumption: WechatSI 公开文档列出接口额度但未给出货币价格或 SLA；目标小程序 AppID 的插件添加页条款需在实施前核验。

## Integrity checklist

- [x] Editable source exists, is repository-local, and its SHA-256 matches.
- [x] Every listed export exists and its SHA-256 matches.
- [x] Required baseline viewports and three key states are represented; other states are explicitly listed.
- [ ] Product owner approved the named Task Spec revision and Design Revision.
- [ ] Manifest frozen after approval; any visible divergence creates a new Design Revision.
