# DREV-20261001-RECORD-VOICE-INLINE-03 — 输入框内嵌语音

- Status: APPROVED / LOCAL_IMPLEMENTATION_VERIFIED
- Related Spec: `SPEC-20261001-VOICE-INPUT-03`
- Affected UI: `UI-001 / pages/records/index`
- Supersedes candidate: `DREV-20261001-RECORD-VOICE-CHAT-02`（未批准；麦克风被放在输入框外）
- Baseline: `FDB-20260913-04`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Approval: 产品负责人（用户）于 2026-10-01 在明确批准请求后要求先实现并充分测试；后续交互调整需新 DREV

## Interaction direction

把文字和语音收敛到同一个紧凑输入框：输入框默认约 92px 高，右下角内嵌 44px 麦克风触控区；点击输入区
继续键入，直接按住麦克风录音。没有外置按钮、输入模式切换、开始/停止按钮或常驻录音卡。

## Primary interaction

1. 输入框提示 `写下今天学了什么…`；底部左侧显示字数，右下角显示麦克风。
2. 家长直接按住麦克风开始录音。输入框原位进入浅绿色录音态，显示 `松开，转成文字`；手指上滑
   80rpx 后显示 `松开，取消本次`。
3. 松开后原位显示 `正在转成文字…`，避免重复触发。
4. 成功后文字追加到输入框，显示短暂 toast `已转成文字，请检查`；家长可直接编辑或提交。
5. 取消、无语音、失败或中断均不改变原文字；单次最长 60 秒。

## State model

| State | Input field | Action/result |
|---|---|---|
| idle | 紧凑多行文字框，右下角内嵌麦克风 | 点击文字输入；按住麦克风录音 |
| requesting_permission | 微信系统授权界面 | 首次授权完成后等待新的按住手势，不自动录音 |
| holding | 原位浅绿覆盖层“松开，转成文字” | 松开转写；上滑进入取消预备 |
| cancel_armed | 原位浅红覆盖层“松开，取消本次” | 松开取消；下滑回阈值内恢复 |
| recognizing | 原位“正在转成文字…” | 不允许再次录音或提交 |
| appended | 回到文字框并追加结果 | 直接编辑；短暂 toast 后消失 |
| no_speech/error | 回到原输入框，显示短暂错误提示 | 原文字不变，可重试或手动输入 |
| overflow_review | 原文字不变，待加入文字独立可编辑 | 缩短后加入或放弃，不截断 |

页面 hide/unload、切换孩子、失去写权限或开始保存时取消本次，并让迟到回调失效。

## Permission edge

首次长按可能被微信隐私/麦克风弹窗打断。授权完成后只提示 `已允许麦克风，请重新按住`，不会在手指
已经离开后自动录音。拒绝时可去设置，但键盘输入始终可用。

## Accessibility and geometry

- 输入框视觉高度：92px；内容增长后最高 160px，再内部滚动。
- 麦克风视觉圆面 36px，完整触控范围 44×44px，距输入框右/下内边缘各 6px。
- 麦克风 accessible name：`按住录音，松开转成文字，上滑取消`。
- 计数区域避开麦克风触控区；文字右/下 padding 保证内容不会压到按钮。
- 录音状态用文案、图标和底色共同表达；减少动态时仅切换透明度。
- 无法完成长按的用户仍可完整使用手动文字输入。

## Submission and privacy semantics

- 松开只是生成可编辑文字，不是提交、确认或发送语音消息。
- 转写结果仍是既有 `text` 草稿；无照片走 manual，有照片仍走既有 photo batch。
- 原始音频不上传业务后端、不保存、不回放；临时路径、转写正文和插件响应不写日志或本地存储。

## Responsive matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / idle、holding、appended | 内嵌按钮、文案、计数和底部提交区无横向溢出或相互遮挡 |
| 390×844 / 同上 | 主视觉对照；输入框与页面其他字段对齐 |
| 430×932 / 同上 | 最大内容宽度不变；按钮仍贴输入框内侧 |
| iOS/Android | 首次授权、长按/松开、上滑阈值、touchcancel、60秒、通话和前后台中断 |
| keyboard/large text | 键盘不遮挡输入区；长文增长到上限后内部滚动；文案可换行 |

## Alternatives and trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 输入框内嵌麦克风，直接长按 | 最少结构、无需切模式、符合本次反馈 | 图标需留足 44px 热区；需防文字遮挡 | selected |
| 输入框外麦克风 + 语音模式 | 接近微信旧式切换 | 多一个模式、占一列空间 | superseded |
| 点击开始/停止 | 对长按困难用户友好 | 操作和状态元素更多 | rejected for this revision |

## Approval boundary

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-03 + DREV-20261001-RECORD-VOICE-INLINE-03`

本修订只批准输入框内嵌语音转文字，不批准保存/上传/回放音频、自动提交、自动确认或后端 ASR。
