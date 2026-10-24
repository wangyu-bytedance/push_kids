# FEAT-003 — 通知消息通道

- 2026-10-20本地排期兼容：复习摘要重新计算的未复习量排除永久已替代知识，保留既有人工预约的一次例外。无额外替代通知，不改变模板/授权/投递规则；见[替代状态证据](../../quality/evidence/AUTO-SUPERSEDED-REVIEW-20261020.md)，未部署。

- Design governance revision: `DOC-SPEC-20261013-02-01`；[门禁同步记录](../../../specs/completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md)，仅修订设计证据政策，不改变实现/发布状态。

- Feature ID: `FEAT-003`
- Status: `BACKEND_035_DEPLOYED / RENEWAL_CLIENT_LOCAL / VERIFYING`
- Current-state revision: `FEAT-STATE-20261024-NOTIFICATION-SCHEMA-0022 / AUTO-RENEWAL-VERIFYING-02`
- Owner: 产品负责人（用户）
- Last verified: 2026-10-24（生产0020–0022迁移/结构核验；真实通知收件证据仍为10-17，不冒称本轮重测）
- Authoritative implementation: `apps/api/src/push_kids/notifications/`、通知持久化模型、
  Alembic `20260906_0008_notification_channel` + `20260907_0009_notification_deletion_scope`、`apps/miniprogram/pages/notifications/`、
  `apps/miniprogram/utils/notifications.js`、`apps/miniprogram/utils/notification-renewal.js`、`tools/notification_config.py`
- Applied Spec: `specs/completed/FEAT-003-NOTIFICATION-CHANNEL.md` revisions
  `SPEC-20260906-CHANNEL-01`（服务端通道）+ `SPEC-20260906-CHANNEL-02`（授权入口）
  + `SPEC-20260906-CHANNEL-03`（对齐后台已选用模板的字段语义）+
  `BUG-SPEC-20260907-22`（永久删除与冻结边界）；只读运行事实及隔离诊断工具见
  `specs/completed/OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS.md`及
  `specs/completed/OPS-20261017-NOTIFICATION-GRAY-DEBUG-DEPLOYMENT.md`及
  `specs/completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md`（获批-01/-02/-03；032/033及任务已清理；必要权限缺口由-04修复，-05真实日程投递成功后诊断闭环）
  平台单接口配置修复见`specs/completed/OPS-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX.md`，DONE，仅代表配置验收。
  单条真实日程投递见`specs/completed/OPS-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE.md`，DONE；微信返回成功，用户已明确确认收到0F58提醒。
- UI current state: `docs/design/frontend/ui/UI-011-reminder-settings.md`

> 本文只描述当前事实。2026-10-17 只读核验时，`flask-ik19-031` 正常承载 100% 流量，通知通道为
> wechat，三类模板及加密配置存在；修复前当前账号日程提醒与复习摘要均开启、accepted、额度各为1。
> 修复前最近10条投递均为failed/transport_error，运行日志对应30次HTTPError。
> 获批-02/-03分别部署032/033（normal/0%），固定HTTP空请求均实测502/HTTPError；033细化解析未提取到有效白名单位置数字码，HTTPS条件对照为URLError、无HTTP响应。
> 032/033均已删除，关联灰度管理任务已停止；031仍normal/100%、受保护配置不变。
> 修复前prod截图确认总开关开启但接口权限列表为空；用户批准-04后添加唯一`/cgi-bin/message/subscribe/send`路径，新截图确认配置完成。
> 获批-05创建唯一临时日程0F58（19:05—19:10 CST），原调度产生的当前账号记录于18:49:19 CST达到sent/ok，授权额度1→0并expired；随后仅该日程DELETE 204，查询匹配数0。
> 用户随后于2026-10-17明确回复“已收到”（call_5b80efd7f9504c4ca286e2df7e031c75），该账号本次日程提醒从发送到实际微信收件已验证；其他成员及其他通知类型本轮未逐一验收。
> 最终官方只读复核031仍normal/100%、PUBLIC关闭、原版本及受保护配置不变。不能回溯断言旧30次均为502或完全排除其他历史原因。
> 真机授权操作及三视口 UI 验收仍未补齐；服务端 accepted 记录不替代这些验收。
> `-01` 已于 2026-09-06 获用户确认；`-02` 依据同日指令「继续做，我需要一个完整的功能」实现，
> revision 文本待确认，代码评审通过 MR 进行。

## Purpose and scope

2026-10-24当前部署阶段：[OPS Spec04](../../../specs/active/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md)按用户指定同库顺序完成生产0022/current/check与结构/队列核验，续订五表存在。035部署后用户100%接管并删除034，旧实例0；通知秘密与18项原配置均保留，coverage=false。真实微信GET通知设置/renewal均200，完整客户端本地已打开。未重新申请授权、补发历史失败通知或创建测试消息，真实续订/各类收件仍待用户验收；全量前定向检查未执行。上述031叙述限定10-17的历史观察，当前见[发布记录](../../deploy/releases/20261023-fullstack-test-deployment.md)。

给家庭提供一条可信的尽力而为消息通道，承载三类消息：家人加入申请（发给管理员）、
日程开始前一小时提醒（发给全家，说明哪个孩子、几点、做什么）、每天 19:00 的未复习摘要（发给全家）。
通道只读事实，不生成学习记录、不判断掌握、不改写复习计划、不使用模型生成文案。

## Current user/system behavior

本地视觉增量 `FEAT-VISUAL-20261021-HERO-ARC-01`：提醒状态卡随共享样式删除细弧线，通道、授权和发送行为不变。
[Spec01](../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md) / DREV-20261021-HERO-ARC-REMOVAL-01已批准；
验证范围见[质量证据](../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)，未部署/上传。

- 成员级偏好：三类提醒各有独立开关，`member_application` 仅管理员可见可改；其余类型成员可自己改。
- 微信授权：新本地客户端先预备`grant-attempts`，在点击同步链调用微信，再按原事件ID幂等登记真实结果；只有accept增加额度。旧`POST /notifications/subscriptions`仍兼容，旧格式本身没有事件去重。
  长期额度为`-1`，一次性每次同意增加1次，发完置`expired`。本地自动补充能力见[FEAT-011](FEAT-011-notification-auto-renewal.md)，未部署。
- 通道不可用（未配置渠道、缺密钥、缺模板）时，设置接口如实回报 `available=false` 与原因，
  并拒绝收下授权（404），不制造「已开启但收不到」的假象。
- 接收标识（OpenID）AES-GCM 加密存储，带密钥版本，无明文列、无索引；解密失败落
  `failed / destination_unreadable`，日志中不出现接收人、密文与消息正文。
- 计划幂等：每个 tick 重新推导应存在的消息集合；pending 行原地刷新（日程改时间不会发两条），
  不再对应现实的 pending 行作废为 `cancelled / source_changed`。
- 未开启或未授权时**不入队**；因通道不可用/关闭/未授权/模板槽位缺内容而 skip 的行，条件恢复后可 re-arm 重新排队。
- 模板字段语义（对齐后台已选用的三个模板）：`headline`（主题）、`detail`（可行动说明）、`child`、
  `applicant`（申请人关系）、`time`（日程开始时间）、`notified_at`（提醒发出时间）、`applied_at`（申请时间）、
  `duration`（时长，无结束时间时为「未设置」）、`countdown`（距开始多久，≤5 字）、`code`（申请码）。
  每个值按所属微信字段类型的上限裁剪（`thing` 20 字、`short_thing` 5 字，时间类不裁剪）。
- 模板配错时不烧额度：若某个已映射槽位当次没有内容，dispatch 在调用微信之前就落
  `skipped / template_field_missing` 并只记录字段名（不记内容），修正映射后同一条提醒可重新排队。
- 投递：租约 claim（单实例 MySQL 5.7 使用有界、排序的普通 `FOR UPDATE`，不使用 8.0 才支持的
  `SKIP LOCKED`）、有界退避重试、崩溃租约回收，
  终态为 `sent / skipped / failed / cancelled`，每条都有结果码。
- 时间语义：19:00 与「开始前 60 分钟」按 Asia/Shanghai 计算，落库为 UTC；时间永不取自客户端；
  距开始不足一小时的日程仍发一条（发送时间钳到当前）。
- 成员离开家庭立即切断通道：授权 `revoked`、接收标识 `revoked`、在途消息 `cancelled / member_departed`；
  即使没跑清理，发送前的成员身份复核也会挡住该消息（dispatch 计数 `dropped`）。
- 日程提醒与复习摘要通过 `notification_delivery_children` 保存完整 child ownership。永久删除孩子时删除所有
  引用该孩子的 delivery（多孩子摘要整条删除），但保留家庭级偏好、授权与接收标识；永久删除家庭时清空全部通知数据。
  对 migration 前无 child link 的旧日程/复习 delivery 采用隐私优先清理。
- 删除请求冻结 family/child 后，planner 数据源、outbox 入队与 dispatch 发送前都会在同一数据库事务中锁定复核
  active/deleting 状态；因此删除接受后不会重新入队或调用渠道发送。若发送先持锁完成，删除请求在其后才被接受。
- 终态投递记录保留 30 天后清理，在途记录永不被清理。
- 调度：进程内 tick（`PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER`）或外部 cron 调
  `POST /notifications/dispatch`（`X-Notification-Trigger` 共享 token，未配置则该路由 404）。
- 小程序入口：「设置 → 提醒设置」（非Tab二级页；无学习档案也有入口）。本地页面分别显示想不想收、是否自动补充、当前额度和真实投递；逐类显示次数、冷却或停止/待确认，提供“手动补充次数”或“去微信调整”，下方保留30天投递历史。
- 授权动作在用户点击的同一次手势里第一时间调用 `wx.requestSubscribeMessage`，一次最多 3 个模板；
  只有 `accept` 回传 `accepted=true`；通道不可用或微信版本过低时不发起授权，也不显示授权入口；
  偏好写入失败时开关回滚到服务端状态，不留下假的「已开启」。
- 部署配置助手：`tools/notification_config.py secret | scaffold | from-wechat | check`——生成加密密钥、
  打印模板骨架、把微信 `/wxaapi/newtmpl/gettemplate` 的返回转成 `PUSH_KIDS_NOTIFICATION_TEMPLATES`、
  用与运行时相同的解析器校验模板并检查密钥长度；它从不打印既有密钥，也不联网访问微信。
- 尚不存在：早间摘要、其他渠道、通知内的 AI 文案、站内消息中心。

### Local renewal integration (not deployed)

用户2026-10-17批准`SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01`及架构/DREV。notifications新增本人选择CAS、逐类型当前模板证明与冷却、60秒授权租约及事件去重；读取planning公开完成游标，不反向依赖。失败仅恢复原事件；未决结果不从getSetting猜额度。默认unseen，首次显式开启；明确关闭停止。新增`20261017_0020`五表迁移仅本地/隔离MySQL5.7验证，线上Schema及031未改。维护扫描失效离开成员选择和租约；家庭删除清理新增本域表，孩子receipt由planning清理，游标不回退。

本次代码及文档核对、自动化和缺失验收见[实现证据](../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)。原有云端单条收件不是本次续期验收；真机和独立评审待补，Spec active/VERIFYING。

## Current behavior matrix

| Capability | Current status | Evidence |
|---|---|---|
| 三类通知的入队与内容 | implemented locally | `notifications/planner.py`、`tests/integration/test_notification_channel.py` |
| 模板字段语义与逐字段裁剪 | implemented locally | `notifications/domain.py`、`notifications/templates.py`、`tests/unit/test_notification_policy.py` |
| 槽位缺内容时跳过而非被微信拒发 | implemented locally | `notifications/service.py`、`tests/integration/test_notification_resilience.py` |
| 成员级开关与自服务边界 | implemented locally | `notifications/router.py` + `platform/context.py` |
| 微信授权与额度 | 本次日程成功后正常消耗1次授权；真机授权操作待补 | 日程额度1→0/expired，复习额度仅有测试前历史核验；[2026-10-17证据](../../quality/evidence/NOTIFICATION-HTTP-DIAGNOSIS-20261017.md) |
| 加密接收标识 | implemented locally | `notifications/destinations.py`、`tests/unit/test_notification_policy.py` |
| 去重/刷新/取消 | implemented locally | `notifications/outbox.py` |
| 重试/租约/终态 | implemented locally | `tests/integration/test_notification_resilience.py` |
| 离开家庭收回通道 | implemented locally | `tests/integration/test_notification_channel_lifecycle.py` |
| 永久删除通知清理与冻结并发边界 | deployed, live flow pending | `tests/integration/test_data_deletion.py`、`tests/integration/test_notification_channel.py`、`flask-ik19-015` |
| 历史保留窗口 | implemented locally | `NotificationsService.prune_history` |
| 微信真实发送 | -05单条当前账号日程提醒sent/ok，用户确认微信已收到；其他成员/类型待验收 | 0F58，2026-10-17 18:49:19 CST发送，用户随后确认收件；旧10条失败不重置，不能把单次成功推广到所有通知 |
| 小程序提醒设置与授权入口 | development version uploaded | `apps/miniprogram/pages/notifications/`、`tests/frontend/notifications.test.js`、版本 `0.1.4` |
| 部署配置生成与校验 | implemented locally | `tools/notification_config.py`、`tests/unit/test_notification_config_tool.py` |
| 微信开发者工具 / 真机授权 | not verified | 需要微信开发者工具与真机；三视口原生几何未跑 |

## Verification evidence（2026-09-07，本地）

通知删除专项回归：

- `PYTHONPATH=. uv run pytest tests/integration/test_data_deletion.py tests/integration/test_notification_channel.py tests/integration/test_notification_channel_lifecycle.py tests/integration/test_notification_migration.py -q` → 24 passed，包含 claim 后 purge 先提交的 child/family 确定性交错。
- `PYTHONPATH=. uv run pytest tests/unit tests/integration tests/contract -q` → 264 passed, 2 skipped。
- `uv run ruff check .`、`uv run ruff format --check .`、`uv run mypy apps/api/src`、`uv run python tools/check_architecture.py` 均 PASS。
- `npm test` → 124 passed；Mini Program lint PASS；validator → 15 pages / 628174 bytes。
- fresh SQLite `upgrade head/current` PASS（`20260907_0009`）；生产 MySQL 已从 `20260906_0007` 升级到
  `20260907_0009 (head)`，`alembic check` PASS（`No new upgrade operations detected`）。
- 云托管灰度版本 `flask-ik19-015` 于 2026-09-07 11:03:02 达到 `normal`；小程序开发版本 `0.1.4`
  已通过开发者工具预览并上传（575557 bytes）。

## Verification evidence（2026-09-19，MySQL 5.7 兼容修复）

- 隔离 MySQL 5.7.44 从空库升级到 `20260913_0014`，`current/check` PASS；完整 MySQL 专项 4 passed。
- 修复前两个 Worker 用例因 `SKIP LOCKED` SQL 1064 失败，修复后分析、通知与删除 Worker 均能完成领取；
  生产源码中无 `skip_locked`。
- 完整后端 362 passed / 4 skipped，完整前端 170 passed；Ruff、format、Mypy、ESLint、架构、设计证据、
  小程序静态与性能读路径均 PASS。
- 冻结白名单容器使用 CRUD-only MySQL 账号，DDL 被拒绝；UID 10001，live/ready 200，SIGTERM exit 0。

此前通知通道基线在 `origin/main`（`165c588`）之上的证据：

- `uv run ruff check .` PASS；`uv run ruff format --check .` PASS（247 files）
- `uv run mypy apps/api/src` PASS（79 files）
- `uv run python tools/check_architecture.py` PASS（`ARCHITECTURE_VALID checked=3`）
- Alembic 单一 head：`20260906_0008`（迁移链 `…0006 → 0007 → 0008`）
- `uv run pytest tests/unit tests/integration tests/contract -q` → 248 passed, 2 skipped, **2 failed**：
  `tests/unit/test_reporting_trends.py`（等长分桶顺序）与 `tests/contract/test_worker_readiness.py`（就绪 503）
  在 `origin/main` 上以相同方式失败，与通知通道无关，未在本分支修复
- `npm test` → 119 pass；`npm run lint:miniapp` PASS；`tools/validate_miniprogram.py` → `pages=15`
- 设计走查：320/390/430 近似渲染两态截图人工检查
- 微信开发者工具编译、原生节点几何、真机授权与真实发送验收：`NOT RUN`

## Known gaps

1. 修复前核验的最近10条投递均失败；-04补齐必要权限后，-05单条日程提醒已sent/ok，用户已确认微信收到。
   provider 把 HTTPError 统一记为 transport_error，只保留异常类名，旧日志无法恢复 HTTP 状态与平台码。
   [Spec-02](../../../specs/completed/OPS-20261017-NOTIFICATION-GRAY-DEBUG-DEPLOYMENT.md)已明确获批，env -i清空进程环境的032已部署、取码并清理。
   获批[Spec-03](../../../specs/completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md)的033扩展数字字段/固定分类后，HTTP仍502且未分类，HTTPS对照URLError。
   033及管理任务已清理。修复前截图确认必要发送路径权限缺失；用户按已批准
   [单接口修复Spec-04](../../../specs/completed/OPS-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX.md)添加精确路径后，截图及官方只读版本核验通过；-05补齐当前账号单次微信成功受理证据，诊断及测试Spec已DONE。
   仍未取得旧30次HTTP状态/平台代理内部数字码；本次单账号日程收件成功不替代全成员、三类模板、真机授权操作/原生视口与长期可靠性验收。
2. 后台已选用的三个模板（新队员加入提醒 / 日程提醒 / 复习通知）都是**一次性订阅**：每条提醒消耗一次授权，
   日程与复习提醒会退化成「每次都要家长再点一次」；若能选到同题材长期模板应替换并把 `long_term` 设为 `true`。
3. 云端版本与 MySQL migration 已发布；本轮真实 AppID 的 `wx.cloud.callContainer` 读取通知设置与投递记录均200。
   两账号删除/通知完整链路、微信开发者工具三视口原生几何证据仍未补齐。
4. `UI-011` 的仓库原生可编辑 SVG/HTML 设计源文件和审批 manifest 仍为 PENDING；按 `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01` 补齐设计证据。

## Change References

- 2026-10-17 — `OPS-SPEC-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE-05`：用户批准家庭范围，唯一临时日程201，当前账号投递sent/ok、额度1→0/expired，测试日程停用204并确认不再列出；031及配置不变。无业务代码/部署/全局dispatch或旧失败重置；用户随后明确确认微信“已收到”，本次发送及收件闭环。
- 2026-10-17 — `OPS-SPEC-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX-04`：管理员添加唯一订阅消息路径，截图确认开关保持开启，官方只读复核031 normal/100%、PUBLIC关闭、无新版本；未重新部署或补发，真实送达仍未验收。
- 2026-10-17 — `OPS-SPEC-20261017-NOTIFICATION-HTTP-DIAGNOSIS-01`：核验通知配置、当前账号订阅与失败历史，
  新增独立且不加载业务数据的单次空请求诊断工具；21项专项测试及断网容器检查通过。
  后续获批-02/-03以GRAY创建032/033（0%），HTTP均502；033未提取到有效数字码、HTTPS对照URLError；两个临时版本及关联任务均已清理，031始终100%、配置不变。
  用户后续修复前截图确认总开关已开但接口权限为空，之后按-04补齐单路径；未改业务发送代码、授权记录、重试或UI，真实送达仍待验证，见
  [证据](../../quality/evidence/NOTIFICATION-HTTP-DIAGNOSIS-20261017.md)及[诊断发布记录](../../deploy/releases/20261017-notification-diagnosis.md)。
- 2026-09-19 — `BUG-024 / BUG-SPEC-20260919-MYSQL57-WORKER-01 /
  ARCH-20260919-MYSQL57-WORKER-01`：将通知租约领取从 MySQL 8 专属 `SKIP LOCKED` 收敛为生产 5.7
  与当前单实例兼容的普通事务行锁；状态、去重、退避、授权与发送合同不变。MySQL 5.7 专项 4 passed；
  云端发布状态见 release 021。
- 2026-09-07 — `BUG-016 / BUG-SPEC-20260907-22 / d38065a / flask-ik19-015 / 小程序 0.1.4`：补齐 delivery-child ownership、family/child 通知 purge、legacy 隐私优先清理，以及删除冻结后的入队/发送锁定复核；生产 migration 与开发版本发布完成，真实授权/送达仍待体验验收。
