# DREV-20261001-RECORD-VOICE-INPUT-01 — 记录页语音输入

- Status: SUPERSEDED_UNAPPROVED
- Superseded by: `DREV-20261001-RECORD-VOICE-CHAT-02`（用户反馈交互过于复杂）
- Related Spec: `SPEC-20261001-VOICE-INPUT-01`
- Affected UI: `UI-001 / pages/records/index`
- Baseline: `FDB-20260913-04`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- External design dependency: none

## Interaction direction

这是 Operate 型表单增量。视觉方向保持“暖纸底、松绿主操作、低装饰”：语音只是“学习内容”的辅助
输入，不成为独立记录模式、独立页面或聊天入口。家长始终看得到照片、已有文字和最终提交后果；录音与
转写状态使用清楚的时间和动作，不使用装饰性波形、评分、情绪判断或自动提交。

## Information hierarchy

```text
学习内容                              [麦克风] 语音输入
┌────────────────────────────────────────────┐
│ 可补充照片里不明显的内容……                │
│                                            │
│                                      0/4000│
└────────────────────────────────────────────┘

录音或转写时，在同一字段下方出现状态面板；页面底部原提交按钮保留位置，
但在过程结束前禁用并说明原因。
```

入口是次级操作，触控区不小于 88rpx；“提交整理”仍是页面唯一主操作。

## Primary interaction

1. 家长点击“语音输入”。仅此时请求隐私同意与 `scope.record` 麦克风权限。
2. 授权成功后开始录音，最长 60 秒。已有文字保留、暂时只读，页面显示 `正在听 00:18 / 01:00`。
3. 家长点击“停止并转成文字”，进入 `正在转成文字…`；点击“取消”则放弃本次音频，不改变原文字。
4. 转写成功后，把去除首尾空白的结果以一个换行追加到原文字，不覆盖家长内容；显示
   `已转成文字，请核对` 和临时的 `撤回本次`。
5. 家长继续编辑或直接提交。任何语音结果都不会自动提交、自动确认或直接成为正式学习记录。

## State model

| State | Visible behavior | Primary/secondary actions | Form preservation |
|---|---|---|---|
| idle | 字段标题右侧显示“语音输入” | 开始录音 | 照片、时间、文字不变 |
| requesting_permission | 微信隐私/麦克风授权界面 | 平台允许/拒绝 | 表单不变，禁止重复触发 |
| recording | 显示计时、60 秒上限；文字只读 | 停止并转成文字 / 取消 | 原文字持续可见 |
| recognizing | 显示静态进度文案，不伪造百分比 | 可取消并忽略迟到结果 | 原文字不变 |
| appended | 结果追加进文字；显示核对提示 | 撤回本次 / 继续编辑 | 只修改 `text` 草稿 |
| no_speech | “没有听清，可以再试一次” | 重新录音 / 收起 | 原文字不变 |
| permission_denied | 说明麦克风权限用途 | 去设置 / 继续手动填写 | 原文字不变 |
| dependency_error | “语音暂时不可用，可继续手动填写” | 重试 / 收起 | 原文字不变 |
| overflow_review | 结果与已有文字合并会超过 4000 字 | 编辑待加入文字 / 取消 | 不静默截断，不改原文字 |
| saving | 沿用现有保存状态 | 不允许开始录音 | 现有保存合同不变 |

页面隐藏、卸载、切换孩子或失去写权限时，正在录音/转写的本次结果必须取消并使迟到回调失效；不会把
临时音频路径、识别全文或插件响应写入日志、本地存储或分析事件。

## Copy and accessibility

- 空闲入口：`语音输入`；accessible name：`使用语音填写学习内容`。
- 录音状态：`正在听 00:18 / 01:00`；操作：`停止并转成文字`、`取消`。
- 转写状态：`正在转成文字…`；不显示无法证明的百分比或剩余秒数。
- 成功：`已转成文字，请核对`；操作：`撤回本次`。
- 权限拒绝：`需要麦克风权限才能使用语音输入`；操作：`去设置`、`继续手动填写`。
- 服务失败：`语音暂时不可用，可继续手动填写`；操作：`重试`。
- 麦克风、停止、取消等图标必须来自现有生成图标体系；图标不能单独承担含义。
- 状态不只靠颜色；录音状态同时使用文字、时间与停止动作表达。
- 所有普通触控目标至少 88rpx，正文至少 14px；录音计时使用 tabular numerals。

## Submission and source semantics

- 语音转写结果最终只是现有 `text` 表单值。
- 无照片但有转写文字时继续走既有 `source=manual`；有照片时继续走既有照片批次并携带 `input_text`。
- 历史来源仍只表示照片/文字材料事实，不新增“语音”筛选或数据库 source。
- 原始音频不上传、不保存、不回放；插件返回的临时文件路径不进入业务状态。
- AI 仍只接收家长可见、可编辑的最终文字；家长确认前零正式学习写入。

## Responsive matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / idle、recording、appended | 语音入口、计时、停止/取消和固定提交区都不横向溢出；键盘关闭后仍可完整滚动到历史 |
| 390×844 / idle、recording、appended | 主视觉对照；字段、状态面板与底部 CTA 的层级清楚 |
| 430×932 / idle、recording、appended | 最大内容宽度不变，不拉伸为桌面布局 |
| representative iOS/Android | 首次授权、已授权、拒绝后去设置、60 秒自动停止、微信通话中断、后台切换、弱网失败 |
| large text / keyboard | 长文案自然换行；输入键盘不会遮住字段核对与提交返回路径 |

## Design alternatives

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 字段标题右侧入口 + 原位状态面板 | 不新增模式；上下文和草稿始终可见；复用现有表单 | 字段区会临时增高 | selected |
| 按住说话 | 操作步数少 | 容易误触/滑动取消；无障碍与中断恢复较差 | rejected |
| 独立录音底部弹层 | 空间充足 | 遮挡表单、形成第二条流程、离开已有文字上下文 | rejected |
| 上传音频后由后端 ASR | 可控、可替换供应商 | 新增音频存储、清理、密钥、API、费用与隐私范围 | deferred |

## Approval boundary

需要产品负责人明确批准：

`SPEC-20261001-VOICE-INPUT-01 + DREV-20261001-RECORD-VOICE-INPUT-01`

本修订只批准客户端语音转文字后进入现有 `text` 草稿；不批准保存/上传/回放音频、后端 ASR、语音历史
来源、自动提交、自动确认、录音分析或学习评价。可接受的实现差异仅限原生字体 fallback、真实中文自然
换行和微信系统授权弹窗外观。

候选快照：
`docs/design/frontend/snapshots/UI-001/DREV-20261001-RECORD-VOICE-INPUT-01/APPROVAL.md`。
