# FEAT-001 — 家庭学习持续跟进系统 MVP

- Status: `CURRENT`
- Revision: `FEAT-STATE-20260906-PKDS-04-AI-INCREMENT`
- Last verified: 2026-09-06（AI 增量后端本地 212 passed / 2 MySQL skipped，前端 109 passed，架构与小程序校验通过；Ark strict JSON Schema live smoke 因本机未配置 Key 为 NOT_RUN；确认页新分区仍受设计门禁阻塞）
- Source Spec: `specs/completed/FEAT-001-PUSH-KIDS-FINAL-SPEC.md` revision `SPEC-20260831-08`
- Latest applied Spec: `specs/active/FEAT-001-SUBJECT-GROUPED-INCREMENTAL-AI.md` revision `SPEC-AI-INCREMENT-20260906-03`（backend only）
- Previous applied Spec: `specs/active/BUG-013-MULTI-SUBJECT-AND-PARENT-FLOW.md` revision `BUG-SPEC-20260906-16`
- Current visible contract: `docs/design/frontend/prototypes/DREV-20260906-PKDS-01/FRONTEND-SPEC.md`
- Intermediate design artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`

## Purpose and current behavior

家长记录小学阶段孩子真实学过的内容。照片或文字创建异步分析任务；AI 只生成可编辑草稿，
家长确认后才写入学习记录、知识点出现历史和复习计划。系统只安排已经学过的知识，不预测
下一课，不自动批改或判断掌握。活动只进入日程、练习记录和温和提醒，不进入记忆曲线。

原生微信小程序有五个 Tab：今日、日程、记录、报表、设置，共 12 个已注册页面。视觉与交互合同
是 PKDS-1.0（`DREV-20260906-PKDS-01`）。HTML DREV-03 与 UX-03/UX-04 保留为评审过程的阶段性
产物，不参与运行。

## Current invariants

- 复习待办每项返回结构化来源：`source_submission_id`、`source_occurred_on`、`review_round`
  （= `step + 1`）、`interval_days`（= 到期日减去最近一次复习反馈日期，无反馈则减去首次学习
  日期，两者都缺为 `null`）。中文文案由前端拼装，后端不返回渲染句子；缺来源的历史数据返回
  `null` 且仍出现在待办中。照片按写入时分配的 `sort_order` 稳定排序（详情、分析取图一致）。
  正式知识点保存机器识别的 `confidence` 与 `evidence`（仅识别可靠度与出处，不表示掌握程度），
  首次确认写入后不被后续确认覆盖；本次修订之前的历史数据没有这两个字段。科目区分系统预设
  （`语文/数学/英语` 且 `kind=learning`，`is_custom=false`）与家长自建（`is_custom=true`）。
- 历史回看已在本地实现：记录页同页切换新增/历史，已确认/待处理/全部共用分页入口；
  详情由独立的只读页面 `pages/record-detail/` 承载（已入档只读态与待处理态），确认页只承载
  可编辑草稿；两者共用同一份只读 mixin 与模板，展示正式总结、本次知识、原始材料和关联知识
  截至现在的复习反馈。今日和报表可带日期/科目跳入；到期项回到今日反馈。浏览不写学习、
  知识、Review 或 Feedback。
- 历史列表每页 20 条、最多 50 条，稳定游标排序；已确认按学习日期，其他按提交日期。
  无 view 参数的旧 history 接口保留兼容；新 UI 不再依赖 100 条待处理草稿接口。
- 原图每次经家庭/孩子/提交/媒体关联验证；viewer 允许读取，被移除成员拒绝新读取。
  云端签发最长 60 秒 GET 链接，本地下载每次带身份；临时文件退出清理。真实云端双账号 owner
  隔离与 metaid 解码已于 2026-09-06 由用户确认验收通过；合法域名和设备矩阵仍按各自发布门禁记录。
  搜索文字经编码请求头传输，不进入访问日志 URL；预览签发在单进程内限制为每成员每分钟 120 次
  （一次展开九图并逐张查看原图不再被自身限流打断）。云环境客户端直接使用签发的 HTTPS 地址渲染，
  本地环境保留带身份的容器下载。

- 所有查询与写入在 API 边界按家庭隔离；跨家庭资源返回 404。
- 云环境由微信入口 actor 的 HMAC binding 解析家庭，拒绝客户端 `X-Family-ID`；本地/测试
  仍保留显式开发身份。
- 运行时只允许 Ark；确定性 Provider 仅允许显式 `test/e2e` 环境，运行库没有种子/示例数据。
- 未确认草稿不能改变正式学习、知识、复习、Todo 或报表。
- 学习确认只接受服务端解析为 `learning` 的科目；新 activity 提案、已有 activity ID 或同名
  活动均返回 400，草稿保留且不写正式数据。家长显式选择已有 learning 科目时以该科目分类为准。
- 一份提交可以产生多条学习记录，每个科目一条：`learning_records.submission_id` 从唯一约束改为
  普通索引（Alembic `20260906_0004`）。科目身份由 `agent_processing/subject_routing.py` 的确定性
  路由决定，不采信模型字面：拆分 `、，,；;／/｜|＋+&＆·・.。：:` 与空格、去掉 `以及/和/与/及/跟`
  连接词与 `自定义/综合/混合/其他/未知/多科目/跨科目/多学科/合并` 等 stopword，再按家庭已配置科目
  别名匹配（`英文`→`英语`、`math`→`数学`）。因此不再创建 `数学、语文` 这类合成科目。
- 目录里没有的科目名标记为未列出，必须家长在确认时显式同意新增；缺同意时确认返回
  `409 consent_required`，草稿保留、不写任何正式数据，也不自动建科目。
- 确认支持 `groups[]`（每组 = 一个科目 + 该科目的知识点位置 + 可选摘要）。索引以客户端看到的
  知识点位置为权威，服务端只在每个科目桶内去重，避免全局去重造成索引移位。缺 `groups` 的旧客户端
  仍走单科目路径；`ConfirmationResult` 保留 `record_id`/`subject_id` 并新增 `records[]`。
- 活动从既有活动记录入口保存。历史 activity Review 保留但退出 Todo、带练、AI Todo 候选、
  手动/匹配反馈和复习统计；原有活动记录、日程、练习频次与建议不变，历史学习记录不重写。
- AI 输入包含本次图片/完整文字、实际发生时间、已填写年级、最多30个学习科目、分科目均衡
  选取的最多30条已确认历史、最多100个已有知识身份/计划状态、目标上海自然日内最多200个已确认
  条目，以及确认当天最多50个 active 且已到期/逾期的 learning Review 候选；历史发生日提交不带
  今日 Review 候选，未来未到期 Review 也不作为可完成候选。
  每科学习历史先取最近20条、按家长文字词面相关性排序后最多10条；知识先取最近30个，再按
  词面相关性排序，最终跨科目轮流取样。照片相关性由模型阅读，未声称语义检索。
  历史/知识出现必须不晚于本次学习；不推断教材、单元、掌握程度或下一课。
- 部署规则在 `agent_processing/prompt.py` 以 `subject-grouped-incremental-20260906-03` 版本化，不读取
  个人SKILL目录。Ark 必须按当前 active learning subjects 返回固定键的 strict JSON Schema，条目明确
  为 `new_learning` 或 `review`；Markdown fence、额外科目/字段和非法引用不再由正则修补。Provider
  失败后只携带脱敏校验代码最多重生成两次；最终非法输出终态为 `analysis_output_invalid`，不保存原文。
  服务端再校验证据、历史/知识/Review引用并精确过滤同发生日重复项；语义正确性仍须家长核对。
- 批内相同图片字节只传一次，证据保持原照片编号；最近100个同家庭同孩子的待确认/已确认
  提交内，相同文字+图片字节摘要触发重复材料提示并清空自动Todo匹配。摘要保存在草稿JSON的
  服务端元数据，不进模型/日志。无摘要旧记录、重新压缩/裁剪图片不保证识别；新学习事件仍可确认。
- AI可关联候选已有知识ID，服务端校验并统一名称/类别，确认页可取消关联；确认再次检查身份
  与科目/名称/类别。同份记录重复知识只产生一次出现；多次学习仍保留各次发生时间和记录。
- 上传材料中的复习内容必须引用同科目的当日到期/逾期 Todo，不能同时作为新学习条目。家长确认后
  只写一条 `ReviewFeedback(complete)` 并按确定性策略推进已有 Review，不创建 LearningRecord、
  KnowledgeOccurrence 或新 Review；纯复习确认返回空 `records[]` 和 `updated_reviews[]`。混合确认同一
  事务处理新学与复习。step/due/active/确认日变化时返回 `409 review_state_changed` 并保持草稿，
  不再静默忽略；未来或已结束 Review 不会提前推进。
- AI排队、分析中、失败或待确认均可人工确认，人工表单不自动匹配Todo；保存时才取消未完成Job，
  复用同一正式记录事务，来源标记人工录入。Worker成功/失败回写均校验状态、attempt和lease，
  丢弃人工确认、取消或新租约后的迟到结果；不把取消结果复活用于旧任务。
- Review 日期只来自 1/3/7/14/30/60 天确定性策略；历史补录只安排当前检查。
- `daily_budget_minutes` 只把全部到期内容分为“建议完成/有余力再做”，不改变到期日；家长端不展示或编辑该内部默认值。
- 固定活动提醒的星期、开始和结束时间是设置、日程和今日的同一事实源。
- 设置只固定展示数学、语文、英语；其他学习科目与课外活动必须由家长从目录或自定义名称显式添加。课外活动默认空，取消添加或提醒编辑不产生补偿写入。
- 今日在成功且全部为空时提供记录学习和添加日程入口；单栏空文案居中。日程七天、报表三档、基础科目和活动七星期不依赖横向滚动。
- 单次照片学习记录支持 1–9 张：相机单张、相册多选或反复追加；全部图片只创建一个 Job。
- 云环境图片使用后端 ticket + `wx.cloud.uploadFile` + uploader metadata claim；不经过
  `callContainer` 请求体或容器持久化磁盘。取消记录会同步尝试删除已 claim 文件；失败清理目前依赖
  当前 Worker 拓扑；相关决策只引用 `ADR-001 / TD-001`。
- 照片批次在创建 Job 前中断时仍可从服务端状态继续分析或取消；待确认草稿也可删除。
- Worker 普通循环异常以 1/2/4/8/16/30 秒退避自动继续，健康轮询后重置；清理故障单独隔离，
  最多每 60 秒尝试一次，不阻塞分析。任务准备/Provider 普通失败沿用最多三次尝试；数据库写回
  故障保留持久化状态，通过新 Session 和原 5 分钟过期租约恢复，避免伪造任务结果。
- Worker attempt 现记录媒体查询、对象存储 materialize、上下文构建、Provider 和写回的脱敏阶段边界
  与耗时；只记录 Job ID、attempt、对象数、stage 和异常类型，不记录儿童内容、对象路径、模型输入输出
  或异常原文。云端 INFO 路由与 Ark Key 启动门禁已随 `flask-ik19-008` 灰度部署；真实日志确认
  图片读取、Ark 调用和 proposal 校验成功，但 MySQL 秒级 lease 与内存微秒值比较误判导致写回跳过。
  revision 15 已在 claim 后重载持久化 lease，并将达到最大次数的过期任务终态化；
  `flask-ik19-009` 已达到 `normal`，真实新图片已完成 Ark 与写回并进入待家长确认。
- `SPEC-AI-OUTPUT-20260906-01` 的后端已实现并以 `flask-ik19-011` 灰度部署：新 AI 提案使用
  `hanzi/word/poem/arithmetic/concept/activity/other` 受控展示类别，AI summary 上限为 120 字，
  Submission read API 从原子知识点确定性派生有序 `display_groups`；旧提案按 category/name 兼容。
  该投影不参与授权、确认或正式知识写入。新列表前端仍受 `DREV-20260906-AI-02` 设计门禁阻塞。
- 启用 Worker 时，尚未启动、异常退避、停止或后台 Task 已结束均使 `/health/ready` 返回
  `503 worker_unavailable`；健康轮询恢复后为 200，正常分析不按耗时判死。明确禁用 Worker
  的开发/测试配置保留原 readiness；`/health/live` 保持进程存活语义。退避可被 stop 唤醒。
- ReviewFeedback 与 CalendarEvent 创建都使用 family-scoped 幂等请求记录，网络重试不双推进或双建。
- 活动建议按请求的历史目标日和目标周计算，不使用“当前周”污染历史结果。
- `occurred_at` 与 `created_at` 分开保存；日历显示按 Asia/Shanghai 展开。
- 数据库时间列统一先转 UTC 再保存，读取后带 UTC 时区；历史无时区值遵循既有 UTC 约定。
  学习、活动、历史与任务时间不再因 SQLite/MySQL 丢失时区而让客户端误读当地时间。
- 零照片且无 Job 的草稿明确为等待上传，可在原草稿补传或取消；补传复用原批次 key 和照片
  槽号，失败后不重复占用上传票名额。已 claim 但响应丢失时，以服务端 media_count 恢复。
- 兼容提交接口仍先筛选 queued/analyzing/pending_confirmation/failed，再每页 100 条查询；
  新记录页改用 history 的 20 条游标分页及独立待处理总数，轮询保留当前页；已确认历史不轮询。
- Ark 接收完整已接受文字，不再静默截断到 2000 字；输出逐点校验直接证据、图片索引、
  上下文和 Todo 引用。家长可看到证据、低置信度和不确定项，手动新增知识点仍可确认。
- 已结束 Review 的新反馈返回 409，不再重新激活；同一已成功幂等请求允许回放原结果。

## Current contracts

| Responsibility | Current implementation |
|---|---|
| API composition | `apps/api/src/push_kids/bootstrap/app.py`, `/api/v1`, `/health/live`, `/health/ready` |
| learning profiles/subjects | `children` module; profile creation is backend-only in the product UI |
| submission lifecycle | `learning` module with local multipart or cloud ticket/claim multi-media finalize |
| provider/jobs | `agent_processing`; Ark + test-only deterministic adapter |
| deterministic review | pure `planning/domain.py` |
| schedule/activity | `activities`; CalendarEvent CRUD + ActivitySchedule projection, plus read-only TravelArrangement calendar projection and cross-source conflict metadata |
| dashboard/report | `reporting`; today aggregation and 7/30/100-day ranges |
| persistence/media | SQLAlchemy + Alembic；MySQL/cloud storage in cloud, SQLite/local media in dev/test |
| native UI | `apps/miniprogram`; callContainer + cloud upload transport, UI-001 DREV-20260830-03 |

## Runtime data state

The local runtime database was reset after archiving all prototype databases under
`data/archive/20260830-pre-native/`. `data/push_kids.db` is schema-only and passes
`tools/audit_database.py --require-empty`. Real profiles are configured explicitly with
`tools/configure_local_profile.py`; the command never creates learning records.

## Verification evidence

| Gate | Result on 2026-08-31 |
|---|---|
| Python unit/integration/contract | 38 passed, 1 optional MySQL test skipped in default suite |
| Isolated MySQL 8 | baseline migration/current/check passed；cloud identity/job/idempotency/confirmation 1 passed |
| Live HTTP E2E | 1 passed; worker, SQLite, history, multi-photo, confirmation, review and reports |
| Mini Program tests | 24 passed |
| Ruff / Mypy | passed; 40 source files typed |
| Container | 2026-09-05 image build passed；UID 10001；internal port 8000；`/health/live` and `/health/ready` passed；graceful stop passed |
| Cloud staging | `flask-ik19-003` normal；managed MySQL at `20260903_0001`；least-privilege runtime account；DB WAN closed；service PUBLIC closed |
| Real callContainer | domainless live/ready 200 after PUBLIC closure；unbound actor returns expected 403 |
| Architecture validator | `ARCHITECTURE_VALID checked=2` |
| Mini Program validator | 7 pages, 5 exact tabs, source package under budget |
| Runtime DB audit | integrity/FK/family checks passed; all business tables empty |
| WeChat DevTools CLI | project opened successfully; real preview/upload not run without registered AppID |
| Live Ark | `NOT_RUN`: no `ARK_API_KEY`; the four supplied Desktop paths no longer exist |

2026-09-05 BUG-005/006 本地增量验证：后端 unit/integration/contract **66 passed, 2 skipped**
（未配置隔离 MySQL）；前端测试 **28 passed**；Mypy、架构校验及小程序校验通过。
本次八个代码/测试文件 Ruff check 通过；全仓 Ruff check/format 在并行新增
`families/domain.py:1` 有 import/空行格式问题。独立只读复审 **PASS**；详细命令和修复前后
证据见对应 Spec。上述历史云端证据不代表本次修复已重新部署或完成云端验收。

BUG-007 后续本地验证：后端 **80 passed, 2 skipped**（隔离 MySQL 未配置），前端 **34 passed**；
Ruff check/format、Mypy（47 source files）、ESLint、架构和小程序校验通过，独立第二轮复审 PASS。
此前并行家庭模块的格式问题在最新全仓检查中已消失。真实 Ark/云上传和受影响页面视口仍未验收。

## Current limitations / release blockers

BUG-010 本地实现已通过微信开发者工具 registered AppID preview 编译，最终预览包 175,099 bytes；
执行时 macOS 锁屏导致 CUA 与三视口原生截图仍未运行，不能据此声称布局完成视觉验收或云端已更新。

- Real Cloud Hosting actor binding, two-account isolation, owner-only object rules, metaid decode and public-ingress
  rejection passed operator-confirmed staging acceptance on 2026-09-06. This is no longer a release blocker.
- Current cloud Worker topology is documented here only as a runtime fact; its decision is referenced as
  `ADR-001 / TD-001`.
- Database credential rotation, least-privilege account and cloud Alembic execution are complete. Backup/restore
  remains a release gate; the previously shared password is revoked and must not be reused.
- Registered AppID, HTTPS legal domains, privacy declaration, iOS/Android real-device verification and
  preview/upload remain mandatory before an experience or public build.
- 小程序尚未留存最低基础库设置证据，也未对 `callContainer`、`uploadFile`、`chooseMedia` 做能力门禁；
  媒体权限失败、安全错误分类和上传取消恢复按 `BUG-SPEC-20260905-02` 待批准实施。
- Live Doubao image analysis remains unverified until a rotated secret and accessible test images are supplied.
- BUG-005/006 的故障注入及分类回归目前仅在本地隔离环境验证，未重新部署或执行真实云端/MySQL
  故障恢复验收。取消中的 Provider 失败竞争（CR-004）已在BUG-009本地修复；媒体路径清理
  （CR-005）仍属独立问题。
- Figma Starter waiver remains scoped to FEAT-001 and expires before public production release.
- BUG-010 的受控 Figma waiver 同样在公开生产前失效；三视口、字体放大、键盘和 iOS/Android 实机证据仍待补齐。

## Change references

- 2026-09-06 — 云端验收状态更新：用户确认 `BHV-019` 原生/云端验收与 `BHV-020` 真实双参与者
  owner/metaid 测试通过；测试策略要求的真实双账号 owner 规则、metaid 解码和公网拒绝标记为 PASS。
  该证据只关闭对应 staging 安全测试，不关闭隐私/删除、备份恢复或真机视口门禁；Worker 状态只见
  `ADR-001 / TD-001`。

- 2026-09-06 — `FEAT-007 / SPEC-20260906-TRAVEL-02 / DREV-20260906-TRAVEL-01`：设置新增按孩子维护的
  每周出行安排；出行只进入日程，不进入今日、Todo、报表或活动练习。日程对 CalendarEvent、
  ActivitySchedule 与 TravelArrangement 的明确时段统一采用半开区间检测，并为冲突双方返回结构化
  对象与重叠分钟数。自动化已通过，原生三视口和 iOS/Android 仍为 `NOT_RUN`，本轮未部署。

- 2026-09-06 — `BUG-013 / BUG-SPEC-20260906-16`：多科目照片一次确认后按科目分别入档（迁移
  `20260906_0004` 把 `learning_records.submission_id` 的唯一约束降为普通索引，Alembic head 由
  `20260905_0003` 升至 `20260906_0004`，downgrade 遇到多记录数据会显式报错而不是丢数据）；
  新增确定性科目路由与 `consent_required` 同意闸门；待确认草稿可在记录详情页就地确认；
  活动图标按语义派生；报表指标可点；今日默认折叠复习与学习；云环境照片预览改用签发 HTTPS 地址、
  预览限额提至 120/min。API 全部新增字段可选、旧客户端不变。自动化证据：后端 171 passed / 2 skipped，
  ruff check + format（172 files）、mypy（55 files）、`ARCHITECTURE_VALID checked=2`，前端 78 passed、
  ESLint 通过、`validate_miniprogram.py pages=12 source_bytes=533311`、图标生成器幂等。
  三视口原生几何、真机与真实 Ark 多科目语义准确率仍为 `NOT_RUN`，本轮未部署；历史上已落库的
  合成科目名不做自动回改。

- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01`（FEAT-005）改变了本 Feature 的孩子上下文前提：一个家庭
  可以同时保留多个在用学习档案，孩子选择由小程序共享 `utils/child-context.js` 统一解析并在选中档案
  失效时回落；已归档档案的学习/科目/活动新增返回 409，但看板、报表、历史与原图仍可读。
  开通家庭不再必须创建孩子。孩子档案生命周期的权威现状见
  `docs/domain/features/FEAT-005-multi-child-profiles.md`；Alembic head 升至 `20260906_0005`（FEAT-005 的迁移在 review 合并时重链到 BUG-013 的
  `20260906_0004` 之后）。

- 2026-09-06 — `SPEC-20260906-PKDS-01`：小程序全部页面改为 PKDS-1.0 视觉与交互合同，新增只读
  记录详情页并把"可编辑草稿"与"只读记录"拆成两个路由；后端字段级新增 Todo 溯源、媒体稳定
  排序、知识点识别把握程度与证据、科目自定义标记，使界面上"为什么出现、来自哪张照片、
  这条草稿有多可靠、这个科目是谁加的"都能被解释而不是被猜测。新字段全部可空、历史数据允许
  `null`、界面缺字段时隐藏对应展示而不显示占位，因此对旧数据和旧客户端向后兼容。
  Alembic head 由 `20260905_0002` 升至 `20260905_0003`（含 downgrade 与回填测试）。
  自动化证据：后端 131 passed / 2 skipped，ruff / mypy / architecture check 通过，前端 59 passed、
  ESLint 通过、`validate_miniprogram.py pages=12`。三视口原生几何、字体放大、键盘态与真机
  弱网仍为 `NOT_RUN`，因此仍不满足公开发布门禁，本轮也未部署。

- `SPEC-HISTORY-20260905-01 / DREV-20260905-HISTORY-01`: 历史列表、复用只读详情、原始材料读取、
  复习反馈回看和今日/报表联通。本地后端 119 passed / 2 MySQL skipped；前端 58 passed；
  Ruff/Mypy/ESLint/架构/包体检查通过；DevTools preview 编译通过。原生三视口、云端双账号预览和部署未完成。

- `SPEC-20260831-08`: native five-Tab conversion, real local services, no runtime mock data,
  context-aware Doubao proposal, unified schedule and strict E2E/database validation.
- `DREV-20260830-03`: accepted HTML interaction artifact and source of the native conversion.
- `BUG-002`: developer-owned API URL and unambiguous backend-configured profile copy.
- `BUG-003 / BUG-SPEC-20260905-01`: keep UID 10001 and move the CloudBase/Docker internal port from 80
  to 8000 after the real cloud runtime rejected the privileged bind.
- `CLOUD-SPEC-20260903-03`: WeChat Cloud Hosting callContainer, trusted actor binding, MySQL/Alembic,
  private object-storage ticket/claim and single-instance staging Worker.
- `WX-API-BASELINE-20260905-01 / BUG-SPEC-20260905-02`: current `wx.*` inventory, minimum base-library
  recommendation and proposed compatibility/permission/error/upload recovery hardening; implementation pending approval.
- `BUG-005 / BUG-SPEC-20260905-03`: Worker 循环恢复、清理隔离、任务准备异常保护和执行器 readiness。
- `BUG-006 / BUG-SPEC-20260905-04`: 服务端活动分类边界，以及历史活动 Review 的读写和统计隔离。
- `BUG-007 / BUG-SPEC-20260905-05`: 六项 P2 修复（CR-010–015），上传恢复、UTC 时间、模型证据、
  完整文字、待处理分页和复习终态；前端增量 `DREV-20260905-P2-01`，真机验证仍待完成。
- `BUG-008/009 / BUG-SPEC-20260905-06/07`: AI上下文、重复材料/知识/Todo、保留复习进度、人工兜底
  和迟到结果保护；UI增量 `DREV-20260905-AI-01`。本次仅本地修改，验证与未运行项见BUG-009。
- `BUG-010 / BUG-SPEC-20260905-11 / DREV-20260905-UX-03`: 原生控件几何、设置目录、今日空态、
  拍照对齐、家庭详情、邀请申请及100天30项分页；本地实现与390 CUA完成，其他视口证据待补齐。
- `BUG-011 + BUG-012 / BUG-SPEC-20260905-14`: 安全阶段日志云端 INFO 路由、Worker 生命周期事件、
  Ark Key `SecretStr` 与 cloud+ark 启动门禁；本地回归通过，冻结白名单目录已灰度部署为
  `flask-ik19-008` 并达到 `normal`。尚未用新图片证明对象存储、Ark 与写回全链路成功；本 revision
  没有修改重试、租约、数据或 Worker 架构。
- `BUG-011 / BUG-SPEC-20260906-15`: 修复 MySQL `DATETIME` 精度导致的 lease 假冲突，并阻止过期
  running 任务突破 max_attempts；本地回归通过，灰度版本 `flask-ik19-009` 已达到 `normal`，
  新图片端到端 smoke 已进入待家长确认。
- `2026-09-06 release 010`: 远端前端样式基线与 BUG-011/BUG-012 本地修复已在 commit `72970f3`
  合并并推送；最小白名单后端版本 `flask-ik19-010` 已达到 `normal`。开发者工具五个主 Tab、
  320/390/430 视口和云数据加载通过且 0 console error；真机双账号、前端上传和全量切流仍为门禁。
  证据见[发布记录](../../deploy/releases/20260906-010.md)。
- BUG-010 后续截图回归：目录/星期/日历/FAB与报表切换条已继续修正，最新58项前端测试通过；390视觉与320部分复查。详见[回归证据](../../design/frontend/ui/BUG-010-20260905-layout-followup.md)，整体仍未完成真机矩阵或部署。
