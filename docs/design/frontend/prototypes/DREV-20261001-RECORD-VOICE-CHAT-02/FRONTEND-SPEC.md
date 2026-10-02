# DREV-20261001-RECORD-VOICE-CHAT-02 — 微信聊天式语音输入

- Status: SUPERSEDED_UNAPPROVED
- Superseded by: `DREV-20261001-RECORD-VOICE-INLINE-03`（用户要求麦克风直接放入输入框并缩短输入框）
- Related Spec: `SPEC-20261001-VOICE-INPUT-02`
- Affected UI: `UI-001 / pages/records/index`
- Supersedes candidate: `DREV-20261001-RECORD-VOICE-INPUT-01`（未批准；用户反馈交互过于复杂）
- Baseline: `FDB-20260913-04`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`

## Interaction direction

保留记录页现有暖纸底和松绿视觉，不增加状态卡、开始/停止按钮或独立录音页。借用微信聊天的模式切换和
按住说话肌肉记忆：麦克风图标在“文字输入 / 语音输入”之间切换；按住开始，松开结束并转成文字，上滑
取消。与微信语音消息的关键差别是：松开后不会发送音频，只把转写结果追加进可编辑文字。

## Primary interaction

1. 学习内容输入框左侧显示 44px 麦克风切换键；默认仍是键盘和多行文字输入。
2. 点击麦克风后，文字区域原位变为大触控按钮“按住说话”；切换键变为键盘图标。
3. 按住按钮开始录音，页面中央出现轻量浮层：`松开，转成文字`；上滑时切换为
   `松开，取消本次`。不显示常驻计时卡或额外操作按钮。
4. 松开后结束录音并显示 `正在转成文字…`；禁止重复按住，但照片、时间和原文字均保留。
5. 成功后自动回到文字模式，把结果以一个换行追加到现有文字，并用短暂 toast 提示
   `已转成文字，请检查`。家长直接在输入框内编辑、删除或提交，不再增加“撤回本次”操作。
6. 录音达到 60 秒时自动结束并转写；上滑取消、无语音或失败均不修改原文字。

## Permission edge

首次按住触发系统隐私或麦克风授权时，系统弹窗会打断触摸手势。授权成功后页面停留在语音模式并显示
`已允许麦克风，请按住说话`，不会在手指已经离开后自动开始录音。拒绝时显示一次性提示并允许打开设置；
文字输入始终可切回、可使用。

## State model

| State | Main surface | Gesture/action | Preservation |
|---|---|---|---|
| text_idle | 多行文字框 + 麦克风切换键 | 编辑文字 / 切到语音 | 全部表单不变 |
| voice_ready | 原位按钮“按住说话” + 键盘切换键 | 长按开始 / 切回文字 | 已有文字隐藏但保留 |
| requesting_permission | 微信系统授权界面 | 同意/拒绝 | 不自动开录、不改文字 |
| holding | 轻量浮层“松开，转成文字” | 松开完成 / 上滑 | 原文字保留 |
| cancel_armed | 浮层“松开，取消本次” | 松开取消 / 下滑恢复 | 原文字保留 |
| recognizing | 原位按钮“正在转成文字…” | 等待；不可重复录音 | 原文字保留 |
| text_appended | 回到文字框，短暂 toast | 编辑或提交 | 仅追加转写文字 |
| no_speech/error | 回到 voice_ready，短暂错误提示 | 重试或切回文字 | 原文字不变 |
| overflow_review | 回到文字模式，待加入文字独立可编辑 | 缩短后加入 / 放弃 | 不截断、不改原文字 |

页面 hide/unload、切换孩子、失去写权限或开始保存时终止本次录音，并用 generation token 丢弃迟到结果。

## Gesture thresholds and feedback

- `touchstart` 进入录音；`touchend` 正常结束；`touchcancel` 直接取消。
- 手指相对起点向上移动至少 80rpx 后进入取消预备态；向下回到阈值内可恢复。
- 按住反馈在 100ms 内出现；使用触感反馈时必须遵循平台设置，不能作为唯一反馈。
- 录音浮层使用文案、麦克风图标和状态色共同表达，不依赖波形或颜色。
- 单次最长 60 秒；最后 10 秒只显示简洁倒计时，避免全程增加视觉负担。

## Accessibility and fallback

- 麦克风切换键 accessible name：`切换到语音输入`；键盘键：`切换到文字输入`。
- 大按钮 accessible name：`按住录音，松开转成文字，上滑取消`。
- 所有触控目标不小于 44px；普通文字不小于 14px。
- 对无法完成长按手势的用户，手动文字输入仍是完整一级路径；本次不额外引入第二套点击录音流程。
- `prefers-reduced-motion` 或平台减少动态设置下，浮层仅做透明度切换。

## Submission and privacy semantics

- 转写结果只是既有 `text` 草稿；无照片走 `source=manual`，有照片仍走既有照片批次。
- 松开不是提交，toast 不是确认；家长仍须点击“提交整理”，后续仍须确认 AI 草稿。
- 原始音频不上传业务后端、不保存、不回放；临时路径和插件响应不写日志、本地存储或分析事件。

## Responsive matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / text、voice_ready、holding、appended | 切换键、大触控按钮、取消提示和底部提交区无横向溢出 |
| 390×844 / 同上 | 主视觉对照；已有文字与语音模式切换位置稳定 |
| 430×932 / 同上 | 最大内容宽度不变，不扩成桌面工具栏 |
| representative iOS/Android | 首次授权、已授权、上滑阈值、触摸取消、60 秒结束、通话中断、前后台切换 |
| large text / keyboard | 文案换行不遮挡手势区；返回文字模式后光标和输入键盘可恢复 |

## Alternatives and trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 微信式模式切换 + 按住说话 | 熟悉、一步结束、不增加常驻状态 UI | 长按对部分用户不友好；首次授权需要再按一次 | selected per user feedback |
| 点击开始 / 点击停止 + 状态卡 | 状态最明确、运动障碍更友好 | 操作和页面元素过多 | superseded |
| 松开即保存学习记录 | 步骤最少 | 误识别直接写入，违反家长确认原则 | rejected |
| 松开发送语音消息 | 完全复刻微信 | 需要音频存储、播放、后端识别和新数据模型 | rejected |

## Approval boundary

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-02 + DREV-20261001-RECORD-VOICE-CHAT-02`

本修订批准的是微信式手势和“语音转可编辑文字”，不是语音消息。它不批准保存/上传/回放音频、自动提交、
自动确认或后端 ASR。
