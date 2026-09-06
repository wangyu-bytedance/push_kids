# FEAT-003 — 通知消息通道

- Feature ID: `FEAT-003`
- Status: `IMPLEMENTING`
- Current-state revision: `FEAT-STATE-20260906-CHANNEL-02-LOCAL`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-06
- Authoritative implementation: `apps/api/src/push_kids/notifications/`、通知持久化模型、
  Alembic `20260906_0008_notification_channel`、`apps/miniprogram/pages/notifications/`、
  `apps/miniprogram/utils/notifications.js`、`tools/notification_config.py`
- Active change Spec: `specs/active/FEAT-003-NOTIFICATION-CHANNEL.md` revisions
  `SPEC-20260906-CHANNEL-01`（服务端通道）+ `SPEC-20260906-CHANNEL-02`（授权入口）
- UI current state: `docs/design/frontend/ui/UI-011-reminder-settings.md`

> 本文只描述当前事实。服务端通道与小程序授权入口都已实现并通过本地全量门禁；**尚未部署到微信
> 云托管，微信开发者工具与真机授权/送达均未验证**，因此不能描述为「家长已经能收到微信提醒」。
> `-01` 已于 2026-09-06 获用户确认；`-02` 依据同日指令「继续做，我需要一个完整的功能」实现，
> revision 文本待确认，代码评审通过 MR 进行。

## Purpose and scope

给家庭提供一条可信的尽力而为消息通道，承载三类消息：家人加入申请（发给管理员）、
日程开始前一小时提醒（发给全家，说明哪个孩子、几点、做什么）、每天 19:00 的未复习摘要（发给全家）。
通道只读事实，不生成学习记录、不判断掌握、不改写复习计划、不使用模型生成文案。

## Current user/system behavior

- 成员级偏好：三类提醒各有独立开关，`member_application` 仅管理员可见可改；其余类型成员可自己改。
- 微信授权：`POST /notifications/subscriptions` 记录 `wx.requestSubscribeMessage` 的结果；
  长期模板额度为无限（`-1`），一次性模板每次授权只够发一条，发完置 `expired` 需重新授权。
- 通道不可用（未配置渠道、缺密钥、缺模板）时，设置接口如实回报 `available=false` 与原因，
  并拒绝收下授权（404），不制造「已开启但收不到」的假象。
- 接收标识（OpenID）AES-GCM 加密存储，带密钥版本，无明文列、无索引；解密失败落
  `failed / destination_unreadable`，日志中不出现接收人、密文与消息正文。
- 计划幂等：每个 tick 重新推导应存在的消息集合；pending 行原地刷新（日程改时间不会发两条），
  不再对应现实的 pending 行作废为 `cancelled / source_changed`。
- 未开启或未授权时**不入队**；因通道不可用/关闭/未授权而 skip 的行，在条件恢复后可 re-arm 重新排队。
- 投递：租约 claim（MySQL 用 `FOR UPDATE SKIP LOCKED`）、有界退避重试、崩溃租约回收，
  终态为 `sent / skipped / failed / cancelled`，每条都有结果码。
- 时间语义：19:00 与「开始前 60 分钟」按 Asia/Shanghai 计算，落库为 UTC；时间永不取自客户端；
  距开始不足一小时的日程仍发一条（发送时间钳到当前）。
- 成员离开家庭立即切断通道：授权 `revoked`、接收标识 `revoked`、在途消息 `cancelled / member_departed`；
  即使没跑清理，发送前的成员身份复核也会挡住该消息（dispatch 计数 `dropped`）。
- 终态投递记录保留 30 天后清理，在途记录永不被清理。
- 调度：进程内 tick（`PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER`）或外部 cron 调
  `POST /notifications/dispatch`（`X-Notification-Trigger` 共享 token，未配置则该路由 404）。
- 小程序入口：「设置 → 提醒设置」（`pages/notifications/index`，非 Tab 二级页；无学习档案的空态也提供入口）。
  页面把「想不想收」（开关）与「能不能收到」（微信授权）分成两件事显示：Hero 报出待授权类别数与
  授权主操作，每行显示状态胶囊与行内「去授权」，最下方按 30 天窗口列出最近投递结果及失败原因。
- 授权动作在用户点击的同一次手势里第一时间调用 `wx.requestSubscribeMessage`，一次最多 3 个模板；
  只有 `accept` 回传 `accepted=true`；通道不可用或微信版本过低时不发起授权，也不显示授权入口；
  偏好写入失败时开关回滚到服务端状态，不留下假的「已开启」。
- 部署配置助手：`tools/notification_config.py secret | scaffold | from-wechat | check`——生成加密密钥、
  打印模板骨架、把微信 `/wxaapi/newtmpl/gettemplate` 的返回转成 `PUSH_KIDS_NOTIFICATION_TEMPLATES`、
  用与运行时相同的解析器校验模板并检查密钥长度；它从不打印既有密钥，也不联网访问微信。
- 尚不存在：早间摘要、其他渠道、通知内的 AI 文案、站内消息中心。

## Current behavior matrix

| Capability | Current status | Evidence |
|---|---|---|
| 三类通知的入队与内容 | implemented locally | `notifications/planner.py`、`tests/integration/test_notification_channel.py` |
| 成员级开关与自服务边界 | implemented locally | `notifications/router.py` + `platform/context.py` |
| 微信授权与额度 | implemented locally | `notifications/service.py::register_subscription` |
| 加密接收标识 | implemented locally | `notifications/destinations.py`、`tests/unit/test_notification_policy.py` |
| 去重/刷新/取消 | implemented locally | `notifications/outbox.py` |
| 重试/租约/终态 | implemented locally | `tests/integration/test_notification_resilience.py` |
| 离开家庭收回通道 | implemented locally | `tests/integration/test_notification_channel_lifecycle.py` |
| 历史保留窗口 | implemented locally | `NotificationsService.prune_history` |
| 微信真实发送 | not verified | 依赖模板申请与云托管配置 |
| 小程序提醒设置与授权入口 | implemented locally | `apps/miniprogram/pages/notifications/`、`tests/frontend/notifications.test.js` |
| 部署配置生成与校验 | implemented locally | `tools/notification_config.py`、`tests/unit/test_notification_config_tool.py` |
| 微信开发者工具 / 真机授权 | not verified | 需要微信开发者工具与真机；三视口原生几何未跑 |

## Verification evidence（2026-09-06，本地）

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（202 files）
- `uv run mypy apps/api/src` PASS（66 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 219 passed, 2 skipped
- `uv run pytest tests/unit tests/integration tests/contract -q` → 223 passed, 2 skipped
- `npm test` → 102 pass；`npm run lint:miniapp` PASS；`tools/validate_miniprogram.py` → `pages=14`
- 设计走查：320/390/430 近似渲染两态截图人工检查
- 微信开发者工具编译、原生节点几何、真机授权与真实发送验收：`NOT RUN`

## Known gaps

1. 生产环境仍未真的发出过一条消息：模板未申请、云托管未配置、真机授权未验证。
2. 模板类型（长期 vs 一次性）未定，影响额度与重复授权体验；一次性模板需要家长反复授权。
3. 云端部署、MySQL 门禁、微信开发者工具三视口原生几何证据未做。
4. `UI-011` 缺 Figma 节点级 URL，waiver 处于请求状态。
