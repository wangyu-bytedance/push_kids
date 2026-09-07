# FEAT-003 — 通知消息通道（Notification message channel）

- Status: `IMPLEMENTED_PENDING_REVIEW`
- Risk: `R3`
- Spec owner: 产品负责人（用户）
- Implementer: Aime（后端 + 小程序授权入口）
- Reviewer: `PENDING（后端、隐私/安全、微信平台）——通过 MR 评审`
- Verifier: `PENDING`
- Created: 2026-09-06
- Last updated: 2026-09-06
- Target release: `PENDING；生产发送还依赖微信订阅消息模板与运行时配置`
- Spec revision: `SPEC-20260906-CHANNEL-02`（前端授权入口；`-01` 为服务端通道，已实现）
- User confirmation: `-01: CONFIRMED 2026-09-06 —「按照这个spec 编写代码，并提交mr」；`
  `-02: 依据 2026-09-06 用户指令「继续做，我需要一个完整的功能」实现，revision 文本待用户确认`
- Additional R2/R3 approval: `CONFIRMED 2026-09-06（与 Spec revision 同一次确认）`
- Affected Feature IDs: `FEAT-003（新增，本 revision 只覆盖通道）；FEAT-002（成员生命周期读契约）`
- Feature current-state documents: 新增 `docs/domain/features/FEAT-003-notification-channel.md`
- Feature baseline revision: `FEAT-003=N/A（全新）；FEAT-002=以实现前最新 revision 为准`
- Feature merge owner: Aime

## Frontend Design Impact and Figma Approval

- Frontend impact: `-01: no；-02: yes`
- Frontend impact reason: `-01` 只交付服务端通道（配置、授权存储、出站队列、投递、重试、终态、调度），
  不改任何界面。`-02` 补上「完整功能」缺的那一半：没有小程序里的授权动作，微信通道在生产环境永远拿不到
  订阅额度，通道只会如实回报 `not_authorized`。因此 `-02` 新增提醒设置页与设置页入口。
- Frontend engineering impact: `-02: yes`
- Affected UI IDs: `UI-011-reminder-settings`（新增，`docs/design/frontend/ui/UI-011-reminder-settings.md`）
- Baseline / Design revision: `FDB-20260906-02` / `DREV-20260906-PKDS-03`（复用 PKDS 2.0，不新增视觉语言）
- Engineering contract: `FEC-20260905-02`
- Figma waiver: `REQUESTED` — 当前 Figma 账号为 Starter/View 且写入限额已触发，无法产出节点级 URL；
  FEAT-001 的 waiver 不覆盖 FEAT-003，节点补录与三视口原生几何证据仍是发布门禁。
- 视口矩阵: 320×568、390×844、430×932；本轮只有 `tools/preview` 近似渲染走查，
  微信开发者工具编译与原生节点几何 `NOT RUN`。

## 0. Executive summary

### Problem

系统此前没有任何对外消息能力：家长必须主动打开小程序，才可能发现有家人正在申请加入、
孩子一小时后有课、或者今天还有复习没做。缺的不是这三条内容，而是一条可依赖的消息通道——
授权、去重、定时、重试、终态、可观测、可收回。

### Intended outcome

一条家庭内可信的尽力而为通道，承载三类消息：

| 类型 | 受众 | 触发时机 | 内容 |
|---|---|---|---|
| `member_application` | 该家庭全部管理员 | 存在待审批加入申请 | 有家人申请加入 + 关系称呼 + 申请码 |
| `schedule_reminder` | 该家庭全部在册成员 | 日程开始前 60 分钟 | 哪个孩子、几点、做什么 |
| `review_digest` | 该家庭全部在册成员 | 每天 19:00（Asia/Shanghai） | 还有哪些孩子、多少条、哪些科目没复习 |

通道对外只承诺一件事：**发出去的一定是真的发过，发不出去的一定被如实标记**。

### Why now

三类消息的业务事实（申请、日程、到期复习）都已经存在且确定性可读，唯一缺口是通道本身。

### 流程偏差（必须记录）

`AGENTS.md` 要求先获批 Spec revision 再进入生产实现。本次通道后端代码在本 revision 之前落地，属于
流程偏差。补救与闭环：本 revision 完整记录已落地事实与证据后提交用户；用户于 2026-09-06 确认本
revision 并要求提交 MR，确认覆盖范围与已实现范围一致（服务端通道，不含前端授权入口）。生产环境
`wechat` 通道仍需先完成 §13 的人工门禁才可启用。

## 1. Facts, decisions, assumptions, questions

### Confirmed facts

- 微信订阅消息需要用户在界面上主动授权；一次性模板的一次授权只能发一条。
- 云托管容器内可直连 `api.weixin.qq.com` 的订阅消息接口，服务本身不保存 AppSecret。
- 待审批申请、日程 occurrence、当日到期复习都已有确定性读路径。

### Decisions

- D1：投递用持久化 outbox（`notification_deliveries`），不用内存队列。进程重启只会重复计算，不会丢消息。
- D2：接收标识（OpenID）用 AES-GCM 应用层加密存储，不落明文、不建索引、不进日志。
- D3：19:00 与「开始前 60 分钟」都按 Asia/Shanghai 业务时间计算，落库存 UTC；时间永不取自客户端。
- D4：没有有效授权就**不入队**，避免产生只能被 skip 的垃圾行；条件恢复后同一条可以 re-arm。
- D5：调度既可进程内定时（`run_notification_scheduler`），也可由带 token 的 `POST /notifications/dispatch`
  由外部 cron 驱动；两条路径共用同一套幂等逻辑。
- D6：成员离开家庭立即切断通道（授权收回、接收标识停用、在途消息作废），且发送前再复核一次成员身份。
- D7：通道不可用时拒绝收下授权（HTTP 404），不制造「开了但永远收不到」的假象。

### Assumptions

- A1：一个成员在一个小程序 AppID 下只有一个接收标识。
- A2：单实例调度足够 MVP 负载；MySQL 上 claim 用 `FOR UPDATE SKIP LOCKED` 已为多实例预留。

### Open questions

- Q1（2026-09-07 已回答）：后台该类目没有长期模板可选，三类都用一次性模板；额度按可累积语义运行，
  家长需要定期补授权，见 `-04`。
- Q2：`review_digest` 是否需要「今天已全部完成」的正向消息？当前实现选择静默。

## 2. Current behavior and evidence

实现前：无通知表、无 provider、无调度、无投递记录。设置页只有家庭/科目/活动。

## 3. Target behavior

### Primary sequence diagram

```mermaid
sequenceDiagram
  participant Cron as Scheduler / cron
  participant Plan as NotificationPlanner
  participant Box as NotificationOutbox
  participant Disp as NotificationsService.dispatch_due
  participant WX as WeChat subscribe API
  Cron->>Disp: sweep()（收回离开成员、清理过期历史）
  Cron->>Plan: plan_all(now)
  Plan->>Box: enqueue / refresh / re-arm / cancel（按 dedupe key）
  Cron->>Disp: dispatch_due(now)
  Disp->>Disp: reclaim_expired + claim(lease) + 成员身份复核
  Disp->>WX: send(receiver, template, data, page)
  WX-->>Disp: errcode
  Disp->>Disp: sent / retry(backoff) / failed，并同步授权额度
```

### Behavior matrix

| 条件 | 结果 | 记录 |
|---|---|---|
| 通道未配置 | 不发送 | `skipped / channel_unavailable`，条件恢复后可 re-arm |
| 成员关掉该类提醒 | 不入队 | 设置页显示为关闭 |
| 无微信授权或额度为 0 | 不入队 | `not_authorized`（历史行），设置页显示待授权 |
| 日程被改时间 | 原 pending 行原地更新 | `refreshed`，不产生第二条提醒 |
| 日程被删除 | pending 行作废 | `cancelled / source_changed` |
| 申请被审批或拒绝 | pending 行作废 | `cancelled / source_changed` |
| 成员被移出家庭 | 立即切断 | 授权 `revoked`、接收标识 `revoked`、在途 `cancelled / member_departed` |
| 发送前才发现成员已离开 | 不发送 | `cancelled / member_departed`（dispatch 计数 `dropped`） |
| 微信瞬时错误 / 网络错误 | 有界退避重试 | `pending` + `available_at`，超次数落 `failed` |
| 用户在微信里拒收 | 永久终态 | `failed / user_refused`，授权置 `rejected`、额度 0 |
| 接收标识无法解密 | 永久终态 | `failed / destination_unreadable`，不打印密文 |
| 一次性额度用尽 | 需要重新授权 | 授权置 `expired`，设置页提示「再存」 |
| 家长再同意一次 | 额度累积 | `remaining_quota += 1`，状态 `accepted` |
| 家长这次弹窗没同意（`reject`） | 已攒额度保留 | 状态与额度不变 |
| 家长在微信里选择不再接收（`ban`/`filter`） | 立即不可送达 | 授权置 `rejected`、额度 0 |
| 当天没有到期复习 | 静默 | 不入队，不发「今天没有」 |

## 4. Scope

### In scope

服务端通道：配置与可用性判定、模板绑定、接收标识加密、成员级偏好、订阅授权与额度、
出站队列与去重/刷新/取消、租约与重试、终态与结果码、离开家庭收回、历史保留窗口、
进程内调度与 cron 入口、成员自服务的读写边界。

### Out of scope / non-goals

- 小程序提醒设置界面与 `wx.requestSubscribeMessage` 授权动作（后续 revision + Design Revision）。
- 短信/邮件/公众号等其他渠道。
- 07:00 早间摘要、AI 生成的通知文案（AI 不参与通知内容）。

### Invariants / must not change

- 通知只读事实，绝不产生学习记录、复习计划或掌握判断。
- 每条消息的受众都在单个家庭内解析；跨家庭受众不可能出现。
- 复习日期仍由 `planning` 的确定性策略产出，通知不改写。
- 不在日志、埋点、仓库中出现 OpenID、密文、模板参数正文或孩子姓名。

### Feature current-state impact

新增 `docs/domain/features/FEAT-003-notification-channel.md`；`FEAT-002` 增补成员离开时的通道收回事实。

## 5. Domain and data design

### Entities

| 表 | 拥有 |
|---|---|
| `notification_preferences` | 成员 × 类型的开关 |
| `notification_destinations` | 成员的加密接收标识、密钥版本、AppID、状态 |
| `notification_subscriptions` | 成员 × 类型的微信授权状态与剩余额度（`-1` 表示长期模板） |
| `notification_deliveries` | 出站消息：dedupe key、payload、计划时间、可用时间、状态机、尝试次数、租约、结果码 |

### State transitions

`pending → sending → sent | failed`；`pending → cancelled`；
`pending/sending → skipped`（可恢复原因下可 re-arm 回 `pending`）；
`sending` 租约过期 → `pending`（未超次数）或 `failed / lease_expired`。

### Schema/data changes

Alembic `20260906_0008_notification_channel`，纯新增四张表与索引；
`Database.expected_cloud_revision = 20260906_0008`；downgrade 只删新增表。

## 6. Interfaces and errors

| 接口 | 语义 | 授权 |
|---|---|---|
| `GET /api/v1/notifications/settings` | 通道可用性、原因、模板 ID、三类偏好与授权状态、最近成功时间 | 家庭成员 |
| `PATCH /api/v1/notifications/preferences` | 改自己的某类开关 | 成员自服务；管理员专属类型需管理员 |
| `POST /api/v1/notifications/subscriptions` | 记录微信授权结果 | 成员自服务；通道不可用返回 404 |
| `GET /api/v1/notifications/deliveries` | 自己最近的投递状态与结果码 | 家庭成员 |
| `POST /api/v1/notifications/dispatch` | 一次 sweep + 计划 + 投递 | 部署侧共享 token（`X-Notification-Trigger`）；未配置则 404 |

## 7. Authorization, security, and privacy

- 所有查询与写入按家庭作用域；后台任务不持家庭作用域，逐行解析该家庭受众。
- 接收标识 AES-GCM 加密、随密钥版本存储、无明文列、无索引；解密失败落 `destination_unreadable`。
- 日志只记录类型、结果码、异常类名与计数，不记录接收人、模板参数与消息正文。
- `dispatch` 入口用 `secrets.compare_digest` 比对；未配置 token 时该路由整体不可用。
- 云环境禁止 `recording` 通道与本地占位接收标识；密钥不足 32 字符时通道自动降级为不可用。

## 8. Architecture and implementation boundaries

- 新增 `push_kids/notifications`：`domain.py`（纯策略）、`templates.py`、`destinations.py`、
  `providers.py`、`outbox.py`、`planner.py`、`service.py`、`scheduler.py`、`router.py`、`schemas.py`。
- 依赖方向单向：`notifications → families / activities / planning`。被读取的领域一律不反向依赖通知，
  依赖图保持无环（`tools/check_architecture.py` 通过，`checked=3`，含 `notifications/domain.py` 纯策略校验）。
- 跨域只读契约：`FamilyService.notification_audience / pending_applications / active_member_ids`、
  `ActivitiesService.occurrences_in_window`、`PlanningService.pending_review_loads`。
- 扩展点：provider 为 `open`（可加渠道，必须实现同一 `SendOutcome` 分类）；
  通知类型为 `open`（新增类型必须提供模板绑定、dedupe key 与受众规则）；
  通知内容生成为 `closed`（不接受模型生成文案）。

## 8bis. `-02` 前端范围与约束

### In scope（`-02`）

- 新增非 Tab 二级页 `pages/notifications/index`（提醒设置）：通道状态、三类开关、授权入口、最近投递记录。
- 新增纯展示策略 `utils/notifications.js`：把服务端的通道/授权/投递状态翻译成家长看得懂的文案。
- 设置页新增「提醒设置」入口（含无学习档案的空态，家人申请提醒在建档前就有意义）。
- 新增部署配置助手 `tools/notification_config.py`：生成密钥、打印模板骨架、把微信已有模板列表
  （`/wxaapi/newtmpl/gettemplate` 返回）离线转成环境变量、按运行时同一套规则校验。

### Out of scope（`-02`）

- 不改任何服务端契约、数据模型、调度或文案生成逻辑。
- 不做通知详情页、不做站内消息中心、不做除微信订阅消息以外的渠道。

### Invariants（`-02`）

- 开关（意愿）与授权（能力）必须分开显示；任一写入失败都不得留下假的「已开启」。
- `wx.requestSubscribeMessage` 必须在用户点击的同一次手势里第一时间调用，其前不得 `await` 网络请求。
- 只有 `accept` 计为授权；`reject / ban / filter` 一律按未授权回传服务端。
- 通道不可用或微信版本过低时不发起授权，也不显示授权入口。
- 前端不自行放行权限：`member_application` 的可见与可改仍由服务端裁决。
- 页面不评价孩子、不预测该学什么；明确声明提醒是尽力而为。

### Acceptance criteria（`-02`）

- AC-101：通道可用且存在未授权类别时，页面报出待授权数量并提供一次最多 3 个模板的授权入口。
- AC-102：微信返回 `reject/ban/filter` 时，页面不显示「已开启」，且服务端收到 `accepted=false`。
- AC-103：偏好写入失败时开关回滚到服务端状态并显示错误。
- AC-104：通道不可用或微信版本过低时不调用授权接口，并给出可行动的说明。
- AC-105：投递记录读取失败只降级该分段，开关与授权仍可用。

## 8ter. `-03` 对齐后台已选用模板的字段语义

用户在小程序后台选用了三个真实模板（新队员加入提醒 / 日程提醒 / 复习通知），它们的槽位比 `-01`
假设的 `headline/detail/child/time/code` 更细：日程提醒要求「时长」「时间」「开始时间」「距离开始时间」，
新队员加入提醒要求「姓名」「申请时间」「温馨提示」，复习通知要求「复习内容」「备注」。微信的规则是
**模板里出现的每个槽位都必须给值**，缺一个就按 `47003` 整条拒发，而一次性订阅下被拒的消息同样吃掉授权额度。

### In scope（`-03`）

- 扩展确定性内容语义：`applicant`、`applied_at`、`duration`、`countdown`、`notified_at`。
- 内容按所属微信字段类型逐字段裁剪（`thing` 20 字、`short_thing` 5 字、`name` 10 字，时间类不裁剪）。
- `ScheduledOccurrence` 带出同日 `duration_minutes`（结束时间不晚于开始时间视为未知）。
- dispatch 在调用微信之前检测「已映射但当次没有内容」的槽位，落 `skipped / template_field_missing`
  并只记录字段名；该结果码可 re-arm。
- `tools/notification_config.py`：按模板正文的中文标签推断映射（「开始时间」优先于泛化的「时间」），
  区分「必须说清的内容」与「模板放得下就填的内容」，并把「映射了这类提醒产不出的语义」判为配置错误。

### Out of scope（`-03`）

- 不改数据库结构、不改调度与去重语义、不改前端交互结构（仅新增一条结果码文案）。
- 不把模板 ID 写进仓库；模板 ID 属于部署环境变量。
- 不申请或替换模板，长期/一次性的选择仍在后台人工决定。

### Invariants（`-03`）

- 时间类槽位只接受真实时间戳，未知时间不得用散文占位，也不得截断时间文本。
- 时长未知时如实写「未设置」，不得凭结束时间缺失就不发提醒，也不得编造时长。
- 语义值仍只来自已存事实与确定性策略，不引入模型生成文案。
- 配错模板的代价必须是「跳过 + 可诊断」，不能是「烧掉家长的一次授权」。

### Acceptance criteria（`-03`）

- AC-201：日程提醒能同时给出主题、时长、时间、开始时间、距离开始时间，且每个值不超过其字段类型上限。
- AC-202：`短_thing` 类字段（距离开始时间）永不超过 5 个字，`即将开始` 用于已到点的情况。
- AC-203：家人申请提醒能给出申请人与申请时间；申请时间未知时该槽位不被填入非时间文本。
- AC-204：已映射槽位缺内容时不调用发送、不消耗额度，落 `skipped / template_field_missing`，
  修正映射后同一条提醒可重新排队发出。
- AC-205：`from-wechat` 对后台这三个模板产出的映射与人工核对结果一致，且 `check` 判定为可用。

## 8quater. `-04` 后台没有长期模板：把一次性额度做成可数、可补的常态

用户在小程序后台确认「选用模板」里**没有长期订阅模板可选**（该类目当前只提供一次性模板）。
这不是配置错误，而是能力边界：三类提醒只能按一次性订阅运行，每条消息都要消耗一次授权额度。
因此本 revision 不再把「换长期模板」当作首选方案，而是把一次性额度做成产品的正常路径：
额度可累积、可数、可补，并且家长的一次「这次不订」不能把之前攒下的额度清零。

### In scope（`-04`）

- `POST /notifications/subscriptions` 新增可选 `decision`（`accept|reject|ban|filter|""`），
  回传 `wx.requestSubscribeMessage` 的原话；服务端据此区分「这次没同意」与「不再接收」。
- 一次性额度语义明确为可累积：每次 `accept` 额度 +1；`reject` 且已有额度时保留额度与 `accepted` 状态；
  `ban` / `filter` / 未给出结论时清零并置 `rejected`。
- 提醒设置页把额度可数化：Hero 显示「提醒余额 N 条」，行内显示「已开启 · 还能发 N 条」，
  仅剩 1 条时改为提醒色，余额 <3 条时把「再存几条提醒」升为主操作。
- 新增补授权路径：已授权状态下也能再次发起授权，按剩余额度最少的类别优先、一次最多 3 个模板；
  成功后报「已存入 N 条提醒」而不是含糊的「已开启」。
- 文档把「一次性订阅」定为正式运行模式：`long_term` 保持 `false`，仅在后台真的出现长期模板时才改。

### Out of scope（`-04`）

- 不改数据库结构、模板字段语义、调度与去重语义。
- 不自动替家长补授权，也不在其他页面弹授权（授权仍必须发生在家长自己的点击手势里）。
- 不用其他渠道（服务号、短信、站内推送）绕过一次性额度限制。
- 不因额度不足而补发历史提醒。

### Invariants（`-04`）

- 界面上的额度数字必须来自服务端的 `remaining_quota`，前端不预测、不乐观加一。
- 家长在微信里选择「不再接收」时必须立即体现为不可送达，不得因为本地还存着数字而显示「已开启」。
- 一次弹窗的拒绝不得销毁此前已经取得的额度。
- 额度耗尽期间的提醒仍然如实落终态并给出原因，不静默、不补发。
- 长期模板（若将来可用）下不得出现任何「攒额度」的说法与入口。

### Acceptance criteria（`-04`）

- AC-301：同一类提醒连续两次 `accept` 后 `remaining_quota == 2`，发出一条后为 1，状态仍是 `accepted`。
- AC-302：`accepted=false, decision="reject"` 不改变已有额度与 `accepted` 状态；
  `decision="ban"` 立即清零并置 `rejected`。
- AC-303：设置页在全部已授权、额度有限时仍提供补授权入口，且补授权顺序为剩余额度最少者优先、最多 3 个模板。
- AC-304：额度为 -1（长期模板）时不出现补授权入口与余额文案。

## 9. Expected file changes

新增上述 `notifications` 包、迁移、四个测试文件；修改 `persistence/models.py`、`platform/config.py`、
`platform/context.py`、`platform/database.py`、`bootstrap/app.py`、`families/service.py`、
`activities/service.py`、`planning/service.py`、`tools/check_architecture.py`、`pyproject.toml`。

`-02`：新增 `apps/miniprogram/pages/notifications/index.{js,json,wxml,wxss}`、
`apps/miniprogram/utils/notifications.js`、`tests/frontend/notifications.test.js`、
`tools/notification_config.py`、`tests/unit/test_notification_config_tool.py`、
`docs/design/frontend/ui/UI-011-reminder-settings.md`；修改 `apps/miniprogram/app.json`、
`apps/miniprogram/pages/settings/index.{js,wxml}`、`docs/design/frontend/FRONTEND-DESIGN.md`、
`docs/domain/BEHAVIOR-CATALOG.md`、`docs/quality/TEST-STRATEGY.md`、`docs/deploy/BACKEND-RELEASE.md`。

## 10. Non-functional requirements

- 通道故障不得影响主 API：配置错误只让通道自报不可用。
- 单次投递批量 50 条，租约 120 秒，重试有界。
- 终态投递记录保留 30 天后清理，在途记录永不被清理。

## 11. Acceptance criteria

- AC-001：授权后，日程开始前 60 分钟，家庭全员各收到一条含孩子姓名、时间、事项的消息。
- AC-002：19:00 后，家庭全员收到当日未复习摘要；当日无到期复习时静默。
- AC-003：有待审批申请时，仅管理员收到消息；申请被处理后未发送的消息作废。
- AC-004：未授权、通道未配置、用户拒收、成员离开四种情况都不产生「已发送」记录。
- AC-005：瞬时故障按退避重试且不重复发送同一条；崩溃留下的租约可回收。

## 12. Verification plan

| 测试点 | 位置 | 结果 |
|---|---|---|
| 纯策略、字段截断、dedupe key、退避、模板解析、AES-GCM | `tests/unit/test_notification_policy.py` | PASS |
| 三类通知端到端、去重刷新取消、开关、额度、调度 token | `tests/integration/test_notification_channel.py` | PASS |
| 重试/退避/拒收/租约回收/密文损坏/通道不可用 | `tests/integration/test_notification_resilience.py` | PASS |
| 离开家庭收回、发送前身份复核、历史保留窗口 | `tests/integration/test_notification_channel_lifecycle.py` | PASS |
| 迁移新增性与 downgrade | `tests/integration/test_notification_migration.py` | PASS |
| 云环境通道配置校验 | `tests/integration/test_cloud_runtime.py` | PASS |
| OpenAPI 契约与身份边界 | `tests/contract/test_api_contract.py` | PASS |

命令证据（2026-09-06）：`uv run ruff check .` PASS；`uv run ruff format --check .` PASS（202 files）；
`uv run mypy apps/api/src` PASS（66 files）；`uv run python tools/check_architecture.py` PASS（checked=3）；
`uv run pytest tests/unit tests/integration tests/contract -q` → 219 passed, 2 skipped；
`npm test` → 91 pass；`npm run lint:miniapp` PASS；`uv run python tools/validate_miniprogram.py`
→ `MINIPROGRAM_VALID pages=13`。真机/微信开发者工具授权验收：`NOT RUN`（依赖后续前端 revision）。

## 13. Rollout, migration, rollback

- 阶段 1（当前）：`PUSH_KIDS_NOTIFICATION_CHANNEL=disabled`，仅迁移上线，通道自报不可用。
- 阶段 2：配置密钥与模板，`recording` 之外只在生产开 `wechat`；先小范围验证。
- 阶段 3：前端授权入口上线后才可能真正发送。
- 回滚：把通道置 `disabled` 即可停止一切发送，数据保留；必要时 downgrade 到 `20260906_0005`。
- 观测：`notification_tick` 计数（queued/cancelled/sent/skipped/retried/failed/dropped/revoked/pruned）。

### 人工门禁

1. 在微信公众平台申请三类订阅消息模板，取得模板 ID 与字段名。
2. 在运行时配置注入 `PUSH_KIDS_NOTIFICATION_SECRET_KEY`（>=32 字符）与
   `PUSH_KIDS_NOTIFICATION_TEMPLATES`；关闭进程内调度时另配 `PUSH_KIDS_NOTIFICATION_TRIGGER_TOKEN`。
3. 上述值只存平台运行时配置，不进仓库、不进聊天。

## 16. Implementation and verification record

### Changed behavior

新增服务端通知通道：三类通知的计划与投递、成员级偏好、微信授权与额度、加密接收标识、持久 outbox
（去重/原地刷新/取消/re-arm）、租约与有界重试、离开家庭收回通道、发送前成员身份复核、终态历史 30 天保留、
进程内调度与带 token 的 cron 入口。既有业务行为未改动。

### Files changed

- 新增：`apps/api/src/push_kids/notifications/{domain,templates,destinations,providers,outbox,planner,service,scheduler,router,schemas}.py`
- 新增：`apps/api/migrations/versions/20260906_0008_notification_channel.py`
- 新增：`tests/unit/test_notification_policy.py`、`tests/integration/test_notification_{channel,resilience,channel_lifecycle,migration}.py`
- 修改：`persistence/models.py`、`platform/{config,context,database}.py`、`bootstrap/app.py`、
  `families/service.py`、`activities/service.py`、`planning/service.py`、`tools/check_architecture.py`、
  `pyproject.toml`（`pycryptodome`）、`tests/{conftest.py,contract/test_api_contract.py,integration/test_cloud_runtime.py}`
- 文档：`docs/architecture/ARCHITECTURE.md`、`docs/domain/BEHAVIOR-CATALOG.md`（`BHV-026`/`BHV-027`）、
  `docs/domain/features/FEAT-003-notification-channel.md`、`docs/quality/TEST-STRATEGY.md`、`docs/deploy/BACKEND-RELEASE.md`

### Evidence（2026-09-06，基于 `origin/main`）

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（200 files）
- `uv run mypy apps/api/src` PASS（66 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 219 passed, 2 skipped（rebase 前）
- `npm test` → 91 pass；`npm run lint:miniapp` PASS；`tools/validate_miniprogram.py` → `MINIPROGRAM_VALID pages=13`
- 全链迁移：`alembic upgrade head` → `20260906_0008 (head)`
- NOT RUN：MySQL 门禁、云托管部署、微信真机授权与真实发送

### `-02` Files changed（前端与配置助手）

- 新增：`apps/miniprogram/pages/notifications/index.{js,json,wxml,wxss}`、`apps/miniprogram/utils/notifications.js`
- 新增：`tools/notification_config.py`、`tests/frontend/notifications.test.js`、`tests/unit/test_notification_config_tool.py`
- 新增：`docs/design/frontend/ui/UI-011-reminder-settings.md`
- 修改：`apps/miniprogram/app.json`、`apps/miniprogram/pages/settings/index.{js,wxml}`、
  `docs/design/frontend/FRONTEND-DESIGN.md`、`docs/domain/BEHAVIOR-CATALOG.md`（`BHV-028`）、
  `docs/quality/TEST-STRATEGY.md`、`docs/deploy/BACKEND-RELEASE.md`、
  `docs/domain/features/FEAT-003-notification-channel.md`

### `-02` Evidence（2026-09-06，本地）

在 `origin/main`（`165c588`）之上 rebase 后重跑：

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（247 files）
- `uv run mypy apps/api/src` PASS（79 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 248 passed, 2 skipped, 2 failed
  （`tests/unit/test_reporting_trends.py`、`tests/contract/test_worker_readiness.py`；两者在 `origin/main`
  上同样失败，属主干既有问题，本分支未修）
- `npm test` → 119 pass（其中 `tests/frontend/notifications.test.js` 11 项）
- `npm run lint:miniapp` PASS；`uv run python tools/validate_miniprogram.py` → `MINIPROGRAM_VALID pages=15`
- `tools/notification_config.py`：`secret` 产出 43 字符密钥；`scaffold` 与 `from-wechat` 的输出都能被
  运行时解析器解析；`from-wechat` 从模板正文解析字段键、按 `type` 判定长期/一次性、对未知类型与
  找不到的模板 ID 返回非 0，并把无内容可填的模板字段警告到 stderr；`check` 对缺 `template_id`、
  未知语义、空配置、短密钥都返回非 0
- 设计走查：`tools/preview`（来自 UI 分支，未提交到本分支）在 320/390/430 渲染「通道可用 · 待授权」与
  「通道不可用 + 微信版本过低」两态并截图人工检查
- NOT RUN：微信开发者工具编译与原生节点几何、真机 `wx.requestSubscribeMessage` 授权、真实送达、
  MySQL 门禁、云托管部署

### `-03` Files changed（模板字段语义）

- `apps/api/src/push_kids/notifications/domain.py`：字段类型上限与逐字段裁剪、`local_datetime_text`、
  `duration_text`、`countdown_text`，三类内容新增申请人/申请时间/时长/距离开始/提醒时间。
- `apps/api/src/push_kids/notifications/templates.py`：语义白名单扩展、`render` 逐字段裁剪、`missing_fields`。
- `apps/api/src/push_kids/notifications/service.py`：发送前检测缺槽位，落 `template_field_missing`。
- `apps/api/src/push_kids/notifications/outbox.py`：`template_field_missing` 列入可 re-arm 结果码。
- `apps/api/src/push_kids/notifications/planner.py`：传入申请时间、开始时间、时长与提醒发出时间。
- `apps/api/src/push_kids/activities/service.py`：`ScheduledOccurrence.duration_minutes`。
- `apps/miniprogram/utils/notifications.js`：新增 `template_field_missing` 的家长可读解释。
- `tools/notification_config.py`：标签驱动的映射推断、必需/可选语义区分、配置错误判定。
- `tests/conftest.py`：测试模板改成与线上模板同形状（字段编号一致，仅模板 ID 为假值）。
- 测试：`tests/unit/test_notification_policy.py`、`tests/unit/test_notification_config_tool.py`、
  `tests/integration/test_notification_channel.py`、`tests/integration/test_notification_resilience.py`、
  `tests/frontend/notifications.test.js`。

### `-03` Evidence（2026-09-06，本地）

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（247 files）
- `uv run mypy apps/api/src` PASS（79 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 251 passed, 2 skipped, 2 failed
  （仍是 `tests/unit/test_reporting_trends.py` 与 `tests/contract/test_worker_readiness.py` 两个主干既有失败）
- `npm test` → 120 pass；`npm run lint:miniapp` PASS；`tools/validate_miniprogram.py` → `pages=15`
- AC-201 ~ AC-204：`tests/unit/test_notification_policy.py`、`tests/integration/test_notification_channel.py`
  （断言 `thing1/thing2/time3/time15/short_thing18` 与 `thing1/time3/thing5`、`thing2/thing4` 的真实槽位）、
  `tests/integration/test_notification_resilience.py::test_template_slot_without_content_is_skipped_before_calling_wechat`
- AC-205：`tests/unit/test_notification_config_tool.py` 用与后台一致的模板正文断言映射；
  另在本地对三个真实模板 ID 跑过 `from-wechat` + `check`，输出 `NOTIFICATION_TEMPLATES_VALID types=3`
- NOT RUN：真实微信送达（仍需云托管环境变量与真机授权）

### `-04` Files changed（一次性额度可累积与补授权）

- `apps/api/src/push_kids/notifications/schemas.py`：`SubscriptionResult.decision`（受限字面量）。
- `apps/api/src/push_kids/notifications/service.py`：`accept` 累积额度、`reject` 保留已攒额度、
  `ban/filter/未知` 清零并置 `rejected`（`_keeps_stored_quota`）。
- `apps/miniprogram/utils/notifications.js`：`quotaLabel`、`topUpTargets`、`reserveOf`，
  `statusOf` 报出剩余条数，`resultsFromWx` 回传微信原话 `decision`。
- `apps/miniprogram/pages/notifications/index.js|wxml`：余额 Hero、补授权主/次操作、行内「再存一条」、
  「已存入 N 条提醒」toast、说明弹窗改写为一次性订阅的真实规则。
- 文档：`docs/deploy/BACKEND-RELEASE.md`、`docs/domain/features/FEAT-003-notification-channel.md`、
  `docs/domain/BEHAVIOR-CATALOG.md`（`BHV-026`/`BHV-028`）、`docs/quality/TEST-STRATEGY.md`、
  `docs/design/frontend/ui/UI-011-reminder-settings.md`。
- 测试：`tests/integration/test_notification_channel.py::test_repeated_grants_stack_one_off_quota_and_a_decline_keeps_it`、
  `tests/frontend/notifications.test.js`（补授权顺序、余额文案、长期模板不攒额度、`decision` 回传）。

### `-04` Evidence（2026-09-07，本地）

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（247 files）
- `uv run mypy apps/api/src` PASS（79 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 252 passed, 2 skipped, 2 failed
  （仍是 `tests/unit/test_reporting_trends.py` 与 `tests/contract/test_worker_readiness.py` 两个主干既有失败）
- `npm test` → 122 pass；`npm run lint:miniapp` PASS；
  `tools/validate_miniprogram.py` → `MINIPROGRAM_VALID pages=15 source_bytes=629122`
- AC-301 / AC-302：`tests/integration/test_notification_channel.py::test_repeated_grants_stack_one_off_quota_and_a_decline_keeps_it`
- AC-303 / AC-304：`tests/frontend/notifications.test.js`
  （`topping up asks again for the types with the least remaining quota`、
  `a long-term template never asks the parent to stockpile messages`）
- 设计走查：新增 `tools/preview/fixtures.js` 的 `notifications` / `notifications-grant` 两态，
  已渲染并截图 320/390/430（`dist/ui-preview/notifications*-{320,390,430}.png`），人工检查无横向溢出
- NOT RUN：微信开发者工具编译、三视口原生节点几何、真机 `wx.requestSubscribeMessage` 与真实送达

### Deviations from approved Spec

`-02` 同样是先实现后确认：用户指令「继续做，我需要一个完整的功能」明确要求补齐能力，但仓库契约要求
可见前端变更先取得 Spec revision + Design Revision + Figma 节点批准。当前 Figma 账号无法产出节点级 URL，
因此 `-02` 记录为 waiver `REQUESTED`，并把原生视口证据列为未跑的发布门禁，不主张已验收。

`-01` 无功能偏差。唯一流程偏差见 §0（实现先于确认，已于 2026-09-06 由用户确认闭环）。

### Residual risks and follow-up

1. 授权入口已实现，但微信开发者工具编译、三视口原生节点几何与真机授权/送达仍 `NOT RUN`，
   因此仍不能声称家长已经能收到微信提醒。
2. 后台没有长期模板可选，三个模板都是**一次性订阅**：额度已做成可累积、可数、可补，但家长仍需定期回
   小程序补授权；额度耗尽期间的提醒只会落 `skipped / not_authorized`，不补发。这是微信能力边界，
   不是可以在代码里绕开的问题。
3. 云端部署、MySQL 门禁未做，公开发布仍被阻断。
4. Figma 节点级 URL 缺失，`-02` 的 waiver 属于请求状态，未获批准前不得进入生产可见发布。

## 18. Revision history

| Revision | 日期 | 变更 |
|---|---|---|
| `SPEC-20260906-CHANNEL-01` | 2026-09-06 | 首版：只覆盖服务端消息通道；记录实现先于确认的流程偏差；前端授权入口另开 revision |
| `SPEC-20260906-CHANNEL-03` | 2026-09-06 | 对齐后台已选用的三个真实模板：新增 `applicant`/`applied_at`/`duration`/`countdown`/`notified_at` 语义、按字段类型逐字段裁剪、槽位缺内容时 `skipped / template_field_missing`（不烧额度、可 re-arm）、`tools/notification_config.py` 改为按模板标签推断映射；三个模板均为一次性订阅，已记入风险 |
| `SPEC-20260907-CHANNEL-04` | 2026-09-07 | 后台无长期模板可选：把一次性额度定为正式运行模式——`decision` 回传区分「这次没订」与「不再接收」、`accept` 累积额度、提醒设置页显示可发条数并提供补授权入口；文档把 `long_term` 固定为 `false` |
| `SPEC-20260906-CHANNEL-02` | 2026-09-06 | 补齐完整功能：小程序提醒设置页与 `wx.requestSubscribeMessage` 授权入口、设置页入口、部署配置助手 `tools/notification_config.py`；新增 `UI-011`；Figma waiver 处于请求状态，原生视口证据未跑 |
