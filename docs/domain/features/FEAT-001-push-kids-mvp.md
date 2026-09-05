# FEAT-001 — 家庭学习持续跟进系统 MVP

- Status: `CURRENT`
- Revision: `FEAT-STATE-20260905-07`
- Last verified: 2026-09-05（本地、非 root 8000 应用容器；真实微信云新版本 pending）
- Source Spec: `specs/completed/FEAT-001-PUSH-KIDS-FINAL-SPEC.md` revision `SPEC-20260831-08`
- Intermediate design artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`

## Purpose and current behavior

家长记录小学阶段孩子真实学过的内容。照片或文字创建异步分析任务；AI 只生成可编辑草稿，
家长确认后才写入学习记录、知识点出现历史和复习计划。系统只安排已经学过的知识，不预测
下一课，不自动批改或判断掌握。活动只进入日程、练习记录和温和提醒，不进入记忆曲线。

原生微信小程序有五个 Tab：今日、日程、记录、报表、设置。HTML DREV-03 保留为评审过程的
阶段性产物，不参与运行。

## Current invariants

- 所有查询与写入在 API 边界按家庭隔离；跨家庭资源返回 404。
- 云环境由微信入口 actor 的 HMAC binding 解析家庭，拒绝客户端 `X-Family-ID`；本地/测试
  仍保留显式开发身份。
- 运行时只允许 Ark；确定性 Provider 仅允许显式 `test/e2e` 环境，运行库没有种子/示例数据。
- 未确认草稿不能改变正式学习、知识、复习、Todo 或报表。
- AI 输入包含本次图片/文字、已有科目、最近 20 条已确认学习和当前 Todo 候选；近期上下文
  只能消歧，不能冒充本次图片证据。
- Review 日期只来自 1/3/7/14/30/60 天确定性策略；历史补录只安排当前检查。
- `daily_budget_minutes` 只把全部到期内容分为“建议完成/有余力再做”，不改变到期日。
- 固定活动提醒的星期、开始和结束时间是设置、日程和今日的同一事实源。
- 单次照片学习记录支持 1–9 张：相机单张、相册多选或反复追加；全部图片只创建一个 Job。
- 云环境图片使用后端 ticket + `wx.cloud.uploadFile` + uploader metadata claim；不经过
  `callContainer` 请求体或容器持久化磁盘。取消记录会删除已 claim 文件，失败由 Worker 重试。
- 照片批次在创建 Job 前中断时仍可从服务端状态继续分析或取消；待确认草稿也可删除。
- ReviewFeedback 与 CalendarEvent 创建都使用 family-scoped 幂等请求记录，网络重试不双推进或双建。
- 活动建议按请求的历史目标日和目标周计算，不使用“当前周”污染历史结果。
- `occurred_at` 与 `created_at` 分开保存；日历显示按 Asia/Shanghai 展开。

## Current contracts

| Responsibility | Current implementation |
|---|---|
| API composition | `apps/api/src/push_kids/bootstrap/app.py`, `/api/v1`, `/health/live`, `/health/ready` |
| learning profiles/subjects | `children` module; profile creation is backend-only in the product UI |
| submission lifecycle | `learning` module with local multipart or cloud ticket/claim multi-media finalize |
| provider/jobs | `agent_processing`; Ark + test-only deterministic adapter |
| deterministic review | pure `planning/domain.py` |
| schedule/activity | `activities`; CalendarEvent CRUD + ActivitySchedule projection |
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
| Architecture validator | `ARCHITECTURE_VALID checked=2` |
| Mini Program validator | 7 pages, 5 exact tabs, source package under budget |
| Runtime DB audit | integrity/FK/family checks passed; all business tables empty |
| WeChat DevTools CLI | project opened successfully; real preview/upload not run without registered AppID |
| Live Ark | `NOT_RUN`: no `ARK_API_KEY`; the four supplied Desktop paths no longer exist |

## Current limitations / release blockers

- Real Cloud Hosting actor headers, two-account isolation, owner-only object rules and metaid decode remain
  unverified. Public ingress must be disabled before real data.
- The first Push Kids cloud version failed because UID 10001 could not bind privileged port 80. BUG-003
  moves all internal deployment-port declarations to 8000; a new immutable CloudBase version smoke remains
  required before this fix is considered verified in the real cloud runtime.
- Cloud staging must remain one instance while the Worker is in-process. Multi-instance requires a separate
  Worker/queue and a new approved revision.
- Database credential rotation, least-privilege account, backup/restore and cloud Alembic execution remain
  deployment gates. A password previously shared in chat is treated as compromised and must not be used.
- Registered AppID, HTTPS legal domains, privacy declaration, iOS/Android real-device verification and
  preview/upload remain mandatory before an experience or public build.
- Live Doubao image analysis remains unverified until a rotated secret and accessible test images are supplied.
- Figma Starter waiver remains scoped to FEAT-001 and expires before public production release.

## Change references

- `SPEC-20260831-08`: native five-Tab conversion, real local services, no runtime mock data,
  context-aware Doubao proposal, unified schedule and strict E2E/database validation.
- `DREV-20260830-03`: accepted HTML interaction artifact and source of the native conversion.
- `BUG-002`: developer-owned API URL and unambiguous backend-configured profile copy.
- `BUG-003 / BUG-SPEC-20260905-01`: keep UID 10001 and move the CloudBase/Docker internal port from 80
  to 8000 after the real cloud runtime rejected the privileged bind.
- `CLOUD-SPEC-20260903-03`: WeChat Cloud Hosting callContainer, trusted actor binding, MySQL/Alembic,
  private object-storage ticket/claim and single-instance staging Worker.
