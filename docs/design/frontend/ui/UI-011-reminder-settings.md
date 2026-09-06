# UI-011 — 提醒设置与微信授权入口

- Status: `CURRENT_LOCAL / PREVIEW_ONLY / NATIVE_MATRIX_PENDING`
- Related Feature: `FEAT-003`
- Related Spec: `SPEC-20260906-CHANNEL-02`
- Baseline: `FDB-20260906-02`（PKDS 2.0「纸 · 芽」，未新增视觉语言）
- Engineering contract: `FEC-20260905-02`
- Design revision: `DREV-20260906-PKDS-03`（屏 G9；仅复用既有 tokens/atoms/图标集）
- Interactive artifact: `N/A` — 本轮未产出独立原型，走查用 `tools/preview` 近似渲染
- Snapshot manifest: `PENDING`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `N/A` — 当前账号为 Starter/View，MCP 写入限额已触发；节点补录仍是发布门禁

> 本文只描述当前本地事实。页面已实现并通过前端单测与结构校验，**微信开发者工具编译、三视口原生
> 节点几何、真机 `wx.requestSubscribeMessage` 授权与真实送达均为 `NOT RUN`**，因此不能描述为已验收。

## Information architecture

入口位于「设置 → 提醒设置」，非 Tab 二级页 `pages/notifications/index`。家庭还没有学习档案时，
设置页空态里同样提供该入口——家人加入申请的提醒在建档之前就有意义。

页面自上而下三段：**通道状态（能不能收到）→ 三类提醒开关（想不想收）→ 最近的提醒（实际收到了什么）**。
这个顺序来自一条硬约束：开关代表意愿，授权代表能力，两者必须分开显示，否则家长会把「开关是开的」
误当成「一定会收到」。

## Review states

| State | Visible contract |
|---|---|
| 通道可用 · 有待授权 | 绿色 Hero 报出待授权类别数与主操作「在微信里开启提醒」；对应行显示 `待微信授权` + 行内「去授权」 |
| 通道可用 · 全部就绪 | Hero 改为「提醒已就绪」并显示最近一条发出时间；一次性模板额外说明一次授权只够一条 |
| 通道不可用 | Hero 降级为中性卡片，说明服务端给出的原因，并明确「不影响记录和复习」；所有行显示 `暂不可用`，不出现授权按钮 |
| 微信版本过低 | 追加中性提示条；点击授权只弹「更新微信」说明，不调用不存在的接口 |
| 单类关闭 | 行显示 `已关闭` 且不催授权 |
| 拒收 / 额度用完 / 授权被收回 | 分别显示 `微信里已拒收`（危险色）、`上一条已用完`、`需要重新开启`，都提供再授权入口 |
| 最近的提醒 | 每条显示标题、内容、类别、时间、状态胶囊；非成功结果附一句可据此行动的原因 |
| 投递记录读取失败 | 只降级这一段为提示条，开关与授权照常可用 |
| 偏好写入失败 | 开关拨回服务端真实状态并显示错误，不留下假的「已开启」 |

## Interaction and safety contract

- 授权必须在用户点击的同一次手势里第一时间调用 `wx.requestSubscribeMessage`，其前不得 `await`
  任何网络请求；一次最多带 3 个模板（微信上限）。
- 只有 `accept` 计为授权；`reject / ban / filter` 一律按未授权回传服务端，界面不做乐观解释。
- 通道不可用时不发起授权，也不显示授权入口——服务端会以 404 拒绝收下无法消费的授权。
- `member_application` 行标注「仅管理员」；非管理员的可见性与可改性由服务端决定，前端不自行放行。
- 页面文案不评价孩子、不预测该学什么，只复述「哪个孩子、几点、做什么」和「还有哪些没复习」。
- 页面明确声明提醒是尽力而为，重要安排以小程序内日程为准。
- loading / empty / error / 401 / 403 / 并发变更遵循 `FEC-20260830-01`；下拉刷新重新读取设置与记录。

## Visual and responsive contract

沿用 PKDS 2.0：暖纸背景、低饱和青绿、既有 `pk-card / pk-hero / rowlist / pill / pk-notice` 原子与
既有图标集（`ico-family` / `ico-clock` / `ico-book`），不新增品牌色、字体、图像或第三方资源。
状态既用文字也用色彩表达，不只依赖颜色。评审矩阵为 320×568、390×844、430×932。

## Approval status

- 用户指令（2026-09-06）：「继续做，我需要一个完整的功能」——据此实现授权入口，`SPEC-20260906-CHANNEL-02` 待评审确认。
- 已完成：`node --test tests/frontend/notifications.test.js`（11 项）、`npm test`、`npm run lint:miniapp`、
  `tools/validate_miniprogram.py`（`pages=14`）、320/390/430 近似渲染走查。
- 待完成（发布门禁）：微信开发者工具编译与三视口原生节点几何证据、真机授权与真实送达、
  Figma 节点补录或新的 waiver、快照 manifest。

## Change references

- `specs/active/FEAT-003-NOTIFICATION-CHANNEL.md` revision `SPEC-20260906-CHANNEL-02`
- `docs/domain/features/FEAT-003-notification-channel.md`
- `docs/domain/BEHAVIOR-CATALOG.md` `BHV-027`
