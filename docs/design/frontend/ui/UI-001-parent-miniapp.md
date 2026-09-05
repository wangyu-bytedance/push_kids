# UI-001 — 家长端微信小程序

- Status: `CURRENT`
- Related Feature: `FEAT-001`
- Baseline: `FDB-20260830-01`
- Engineering contract: `FEC-20260830-01`
- Design revision: `DREV-20260830-03`
- Current-state revision: `UI-STATE-20260903-02`
- Last verified: 2026-09-03（自动化；真实 DevTools/设备 pending）
- Intermediate artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`
- Figma waiver anchor: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Current information architecture

原生微信小程序面向家长，采用五个一级 Tab。所有页头只保留当前上下文与统一的紧凑孩子
切换器，不重复显示 Tab 已表达的大标题。

| Tab | Current responsibility |
|---|---|
| 今日 | 可折叠的今日复习、今日学习、今日活动；待确认/失败提示 |
| 日程 | 周日期轨、当天时间线、过去日程灰显、FAB 新建、编辑/删除日程 |
| 记录 | 照片/文字、实际发生时间、1–9 张同批照片、异步任务与确认入口 |
| 报表 | 7/30/100 天概览、复习紧迫度、复习活跃度、科目记录 |
| 设置 | 即时保存复习预算、在学科目、常见活动、固定星期与完整时间段 |

深层页面只有草稿确认与活动练习记录。产品 UI 不创建学习档案、不编辑服务地址、不展示账号
占位；这些由后台配置或后续微信身份版本负责。

## State and interaction contract

- 每个远程页面有 loading、empty、content 和可重试 error；不会用示例卡片填空。
- AI 状态使用真实命名阶段，不显示虚构完成百分比；失败保留提交并可重试。
- 图片可单张拍摄、相册一次多选和多次追加，统一 9 张上限；一次提交只创建一个分析任务。
- Job 创建前中断的多图批次显示“继续分析/取消”，不会无限轮询或形成不可恢复草稿。
- AI 草稿可编辑；“确认”是创建正式记录、知识和复习项的唯一入口。
- 今日从同一个 Dashboard 读取复习、已确认学习和日程。三栏独立折叠，不使用只计算复习的
  “今日总体进度”卡。
- 每日复习预算点击即 PATCH，失败回滚；它只改变 required/optional 分组。
- ActivitySchedule 是设置、今日和日程的统一来源；固定安排必须有开始/结束时间。
- 今日还消费不与固定日程重复的柔性活动建议；活动提醒可直接移除。
- Todo 的“带练提示”只提交当前所选且已确认的 Review IDs。
- 日程卡点击编辑；重复日程 MVP 修改整个系列。结束时间早于当前时刻后统一灰显。
- 报表范围切换会重新请求 7/30/100 天数据；100 天按最多 30 天一屏横向浏览。
- 紧迫度同时显示数字/勾与颜色，活跃度同时保留次数语义，颜色不是唯一信息。
- 孩子切换器和折叠箭头都使用 CSS 矢量 chevron，不使用字体字形 `⌄`。

## Visual system

方向是暖纸色背景、墨绿色主色、克制分隔线和低阴影。信息依靠排版和留白建立层级，不采用
儿童游戏化、排行榜、玻璃拟态或企业 BI 密集卡片。底部半屏层使用统一 handle、标题、关闭和
主操作；日程新增使用右下角浮动加号。

## Responsive and accessibility

目标竖屏视口为 320×568、390×844、430×932。触控目标不小于 44px；长内容垂直滚动；
只有日程日期和报表时间页允许显式横向滚动。关键状态有文字语义，表单保留输入，错误不只
依靠 Toast。图片不进入本地存储或日志。云环境 JSON 统一走 `wx.cloud.callContainer`，图片按
服务端 ticket 使用 `wx.cloud.uploadFile` 后 claim；页面不持久化 fileID 或 OpenID。

## Implementation and current evidence

| Contract | Path/evidence | Result |
|---|---|---|
| shell/tokens | `apps/miniprogram/app.*` | five exact tabs |
| pages | `apps/miniprogram/pages` | 7 pages validated |
| API/config | `utils/api.js`, `utils/cloud-media.js`, `config.js` | cloud env/service + callContainer + server-issued upload path；local fallback retained |
| JS behavior | `tests/frontend` | 24 passed |
| static package | `tools/validate_miniprogram.py` | valid; no WXML method calls |
| lint | ESLint | passed |
| WeChat DevTools | local CLI open | opened; registered AppID preview not run |

The accepted HTML version remains a design-history artifact. It is not loaded by the Mini Program and does
not provide runtime data.

## Known deviation / release gate

Cloud transport and upload wrappers have automated coverage, but real `callContainer`、storage owner rule、
camera authorization、weak-network resume and iOS/Android evidence are not claimed. They are mandatory before
the experience build is accepted.

## Change references

- 2026-08-31 — `DREV-20260830-03 / SPEC-20260831-08`: native conversion of the accepted HTML,
  five Tab IA, unified schedule, contextual reports, multi-photo batch and backend-configured profiles.
- 2026-08-30 — `BUG-002`: removed parent-editable API URL and ambiguous child create/save copy.
- 2026-09-03 — `CLOUD-SPEC-20260903-03`: switched the non-visible network/media infrastructure to
  callContainer and private cloud direct upload without changing the approved visual design.
