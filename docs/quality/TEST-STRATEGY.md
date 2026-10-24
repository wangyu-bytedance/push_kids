# Test strategy — FEAT-001

2026-10-24标题约束增量：已批准Title Limit Spec01/Architecture01/DREV04。新生成/PATCH标题统一trim后1–20码点、无内部换行；覆盖0/1/20/21/120、非BMP与绕过验证的provider实例、版本/JSON/任务/正式事实零写入，及旧120字完整读取/审批/记录/删除/主动精简。前端覆盖计数、无效零PATCH、失败保留及不同操作幂等键、reset/hide后排队焦点失效。先红后绿：后端11失败/9通过，前端4失败；现专项后端52、前端18，全量后端780通过/40个MySQL环境相关跳过、前端332通过。三视口各13态原生共39态和独立复核通过，含20字标题两行、14px计数/错误、21/空/旧120/非BMP、错误/保存及旧标题实际滚动；[绑定证据](evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)明确真机/键盘/大字体/读屏未验，Spec留VERIFYING。下方120字用例仅为旧数据兼容，不再代表新生成/编辑有效上限。

2026-10-24今日卡片显隐增量：已批准Card Visibility Spec01/DREV03。前端测试覆盖所有无资格/eligible空态、可写/只读、Task优先和开关关闭、生成/失败/失效/删除恢复、显示投影零写入、隐藏仍自动提示、请求失败保留及重置。原生要求21卡片态×320×568/390×844/430×932，节点与截图共同核对空区零节点/额外间距、邻接分区字体家族/字阶/字重/行高/字距一致、长标题完整、全宽胶囊及44px触控；另回归6个既有DREV02弹层态。当前327项前端和三视口81组原生通过（63卡片＋18弹层）；320初次取证脚本未计既有44px触控下限，改采实际bar/section矩形后全部重跑通过，首次失败留证；源码绑定、实际结果和设备/可访问性缺口见[本轮证据](evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)。设计63张和旧弹层45组不能代验新卡片。

2026-10-24建议弹层精简增量：针对等待中的重复确认/关闭、失败保留和同幂等键重试运行前端专项；标题/元信息、全宽确认、等宽编辑/换项、独立暂缓、44px关闭和8px间隔须由320×568、390×844、430×932原生节点和截图共同验证。覆盖普通与历史长标题、旧120字兼容、实际滚动或全内容可见、等待、失败、编辑及邻接待学状态；新生成/编辑有效上限由上方DREV04改为20码点。合成副本只增加测试setter和标题滚动取证绑定，禁止业务写入；45组取证及源码/工具版本说明见[实现证据](evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)。默认字体模拟器不代替系统大字体、读屏、实际键盘或真机。

2026-10-24今日学习增量专项：按两份批准Spec04执行`test_today_learning_policy`、`test_empty_day_early_review`、`test_learning_suggestions`、`test_today_learning_migrations`、`test_today_learning_reads`及`today-learning.test.js`。迁移固定0022→0024，避免独立0025改变旧库夹具；SQLite10k/50k验证有界上下文、槽索引和实际SQL数量，自动提示普通命令≤15条领域SQL（身份认证固定查询另计），/current≤8。MySQL5.7须实际引擎验证，MySQL8不可替代。78张设计PNG与合成原生矩形各有用途，均不能代替键盘、读屏、真实设备或内容/主体适用验收。精确本轮结果和未执行原因以[证据](evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)为准，默认关闭且未部署。

2026-10-23 BUG-031门禁：`tests/performance/test_footprints_reads.py`显式参数化SQLite与真实MySQL5.7，各执行单到访/1000到访的50k分布；MySQL未配置仍skip，发布必须单独运行且无skip。每例创建独立临时库，从冻结迁移链升head；解释实际预览SQL及绑定参数，检查每分支实际key=ix_footprint_photo_visit、type=ref/range，外层PRIMARY/eq_ref和无DEPENDENT，而非possible_keys字符串。保留500ms/16MiB/查询数/响应预算，验证精确前四、deleted/跨家庭排除及下一页；Decimal按FastAPI真实编码测响应大小。最终冻结源码31项专项/规模结果与首次失败均见[证据](evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md)，不替代云端owner/真机/全球底图验收。

2026-10-20 永久词条替代增量：测试单项完整覆盖的严格AI合同、跨科目人工标注合成语义样本、原分析流水线可选阶段失败降级，以及服务端覆盖快照与确认事务。验证编辑/篡改不生效、实际历史守恒、旧材料与Review重建不恢复、当前/未来自动行移出不补题、既有人工预约消费一次、仅所选词条删除、并发幂等、持久游标与租约重试/取消。SQLite和真实MySQL5.7分别执行迁移与行为门禁，10k/50k双状态目录检查真实ORM计划、查询数和响应预算；自引用SET NULL需显式反向索引覆盖批量清理，MySQL回退先移除自表外键再删除其索引。真实模型样本通过只代表该样本集。具体DREV已批准并实现，新筛选/分页/迟到响应/只读/共享内嵌和几何审计反例已测试；完整三视口原生截图与iOS/Android验收仍独立记录，自动化不抵扣。实际命令、结果和缺失项见[本轮证据](evidence/AUTO-SUPERSEDED-REVIEW-20261020.md)。

2026-10-18 FEAT-012增量：合成照片不得含儿童内容；测试覆盖独立EXIF字段与解码10s超时、未知时间、确认幂等/版本/候选、原件24h/草稿168h、权限/归档/冻结、真实清理编排、worker确认竞态、有界画廊/草稿与镜头跟随。50k照片含单大到访及1000到访两种分布，核对SQL计划、查询数和响应预算；真实MySQL5.7门禁单列，未配置只能skip。解锁后24态×3隔离原生节点/PNG/SHA通过，见[原生范围](evidence/child-footprints-20261018/native/README.md)；不抵扣27态缺失7态、完整插件包、真机相册/海外地图、真实AI分层和私有云owner验收。HTML或mock不替代这些门禁。命令/当前结果见[实现证据](evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md)。

## Required layers

- Unit: review intervals, feedback transitions, backfill, normalization and Todo grouping.
- Integration: SQLite transactions, family isolation, submission confirmation, activity records and reports.
- Contract: HTTP request/response shape, job lifecycle, upload validation and stable errors.
- Provider: deterministic adapter restricted to test/e2e plus Ark response-shape parser fixtures; live Ark smoke is secret-gated.
- Ark context transport: unit fixtures must cover default-on session reuse, explicit stateless rollback,
  ten-minute expiry, reverse best-effort cleanup, strict Schema in both modes, no explicit `caching`, safe
  cached-token telemetry and zero response-ID reuse/logging. A real latency comparison uses paired samples with
  alternating mode order and reports only duration, turn count and cached-token aggregate; compare samples with
  the same turn count and do not treat a single run as conclusive.
- Analysis Agent resilience/privacy: fixtures must prove that 20 unmatched candidates fit in one batch tool round
  plus a final round under the eight-turn cap; the last turn rejects tools and a deadline derived from the persisted
  five-minute lease minus the writeback reserve does not call the provider after expiry. SDK retries must be zero.
  Invalid tool JSON/shape/type/range/subject must execute no query and receive a safe same-loop correction. Log
  capture must assert generation/batch counters while excluding child text, subject, keywords, raw output and
  dynamic schema paths. Integration must drive retryable output/transport/budget failures
  to exactly three durable Job attempts, capability/input failures to one, and retain SQL uncertainty, cancellation,
  late-result and readiness behavior.
- Analysis proposal quality: deterministic tests must prove configured/analysis subject separation, unconfigured
  preset recognition, same-loop correction for empty proposals and model-authored runtime claims, three-attempt
  durable exhaustion, non-empty guarded writeback, and dry-run/idempotent/tenant-scoped legacy repair. Release also
  requires the fixed deidentified 40-case live Ark gate: 12 Chinese, 12 mathematics, 12 English and 4 multi-subject
  cases, at least 30 rendered images, scheduled in a deterministic Chinese/mathematics/English round-robin with one
  multi-subject case after every three rounds. Every failure remains in the end-to-end denominator and at least 38/40
  must pass. Subject-semantic rates exclude only the exact infrastructure terminal code `analysis_failed`; output,
  schema, subject, evidence, empty-proposal and all other failures stay in each affected subject denominator. Every
  subject denominator must be non-zero and at least 90%, with zero empty/remaining pending and zero formal writes.
  Reports may contain only case IDs, static codes, attempt counts and aggregates. Missing `ARK_API_KEY` is NOT_RUN
  and cannot be represented as 95% success.
- Staged analysis (`BUG-028`): provider tests cover transport/HTTP/auth/incomplete/schema categories, absolute
  deadlines and process concurrency. Durable tests cover validated cache reuse, poison-cache rejection,
  full candidate/source coverage, manual confirmation/cancel/TTL/deletion, and late-result guards. MySQL 5.7
  specifically overlaps checkpoint save with manual confirmation and checks recovery/indexes. Live tools default
  to the staged factory; the original 40-case gate is supplemented by 24 reproducible multi-photo cases repeated
  three times. Source/subject checks are automated; neither these nor historical name overlap constitute independent
  human semantic truth. Historical replay reads one authorized family in a read-only transaction, excludes
  knowledge created after the submission, omits unversioned present-day Todo state, cleans temporary images and
  reports only case aliases/metrics. Interrupted/failed runs remain in evidence and cannot be silently replaced.
- Mini program: request client, formatters, state reducers and structural validator.
- Design evidence: repository-local editable SVG/self-contained HTML, required viewport/state PNGs,
  dimensions, SHA-256 values and approval identity are checked offline; historical external-tool records
  do not satisfy or block the current gate.
- Visual/runtime: WeChat DevTools compile plus 320×568、390×844、430×932 captures for changed states. Record renderer, base library, DPR, font scale and source revision.
- Native geometry: ordinary page roots must not move horizontally; seven-day, three-range, four-budget and seven-weekday controls must all be visible. Circular controls have a width/height difference of at most 1px and regular touch targets are at least 44px. `overflow-x:hidden` and HTML screenshots do not satisfy this gate.
- Review-inventory native geometry regression: after changing selectors or row actions, collect `boundingClientRect` results from the WeChat Mini Program renderer for 320×568, 390×844 and 430×932. Check the time view's two equal 44px segments with an 8px gap, the subject/count views' single full-width trigger and opened option list, a long title, and an open ellipsis menu. Each option and group toggle is at least 44px high; every control remains inside its content row without overlap; the ellipsis is 44×44px (±1px) and has at least 8px clearance from adjacent text. A partial-row check applies only to multi-column selectors that contain one. Run the geometry audit on captured rectangles and inspect native screenshots for text wrapping. CSS inspection, self-contained HTML and screenshots alone are insufficient to mark this gate passed.
  In DevTools, start the local automation endpoint with the installed WeChat CLI (`/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /absolute/path/to/push_kids/apps/miniprogram --auto-port 9420 --trust-project` on macOS), select each simulator viewport, then run `node tools/review_inventory_geometry.js capture <time|subject|count> <320|390|430> <output.json> [--open-menu] [--open-filter]` for every view/viewport pair. The capture contains only numeric rectangles and excludes child text/IDs; store screenshots containing child content only in the approved local test location, never in the repository. `node tools/review_inventory_geometry.js audit <capture.json>...` rechecks retained numeric evidence.
- Interaction state: adding a subject/activity writes only after explicit confirmation; cancelling a catalog or reminder editor performs zero writes. Member self-removal is checked in both UI state and service integration tests.
- Notification channel: no test may reach a real WeChat endpoint. Unit covers notification policy,
  per-field-type clamping (`thing` 20, `short_thing` 5, timestamps never truncated), dedupe keys, retry
  backoff, template parsing and AES-GCM receiver encryption; integration
  drives the whole channel through the `recording` sender and a scripted sender, and must cover queueing
  conditions, in-place refresh, cancellation, member switches, grant quota, bounded retry, refusal, lease
  recovery, an undecryptable receiver, an unavailable channel, revocation on leaving the family,
  membership re-check at send time, a mapped template slot with no content (skipped as
  `template_field_missing` without calling the provider or spending a grant, then re-armable), the 30-day
  retention window and the dispatch trigger token. Integration template fixtures must keep the field
  shape of the templates actually selected in the WeChat console, so a mapping mistake fails a test
  instead of a real send. Business
  time is injected explicitly; a test that reads wall-clock 19:00 is invalid. Live WeChat send and real
  `wx.requestSubscribeMessage` acceptance remain manual, staged gates.
- Reminder settings screen: page tests must prove that the switch state and the WeChat grant state stay
  separate — a failed preference write rolls the switch back, only an `accept` decision is reported as
  authorized, an unavailable channel or an old WeChat client requests nothing, and unreadable delivery
  history degrades only that section. `wx.requestSubscribeMessage` is stubbed; the grant call must be
  asserted to happen before any awaited request so the real client keeps its user gesture.
- Deployment configuration: `tools/notification_config.py check` must agree with the runtime template
  parser and the 32-character key rule, and must never print the key itself. `from-wechat` converts a
  WeChat `gettemplate` response offline; its output must parse with the runtime parser and it must
  refuse unknown notification types, unknown template ids and error payloads. Its label-driven mapping
  must be asserted against the console template bodies, including that `开始时间` wins over a generic
  `时间` slot.
- MySQL: fresh Alembic migration, schema drift check, identity/family isolation, idempotency, Worker lease and confirmation transaction using `PUSH_KIDS_TEST_MYSQL_URL`.
- MySQL 5.7 read-path compatibility (`ARC-015`, `BUG-SPEC-20260912-MYSQL57-01`): the production engine is
  WeChat Cloud Hosting CynosDB MySQL `5.7.18`, which has no window functions. Any release that changes SQL
  MUST run the affected Today/Todo/Report/history/list paths against a **real MySQL 5.7 server** via
  `PUSH_KIDS_TEST_MYSQL_URL` and confirm they return the existing contracts with indexed plans. This gate is
  **blocking for backend cloud release**; SQLite compilation and MySQL 8 `EXPLAIN` evidence cannot substitute.
  Captured runtime SQL must contain no `OVER (` window projection or `WITH ... AS` dependency.
- Cloud storage/identity: local fakes cover contract branches, but real two-account owner rules, metaid decode and public-ingress rejection are mandatory staging tests.
  Staging status: **PASS (2026-09-06, operator-confirmed)** — two real accounts exercised owner isolation,
  metaid decoding, and public-ingress rejection. This closes this test-strategy gate but does not close the
  separate privacy/deletion, backup/restore, worker-topology, device, or production-release gates.
- Container: build, non-root UID, unprivileged internal port 8000, deployment-config consistency,
  live/ready and graceful termination.
- Bounded reads (`TEST-PERF-READ-001..005`): keep scale fixtures separate from the fast correctness
  suite; record runtime, hardware and dialect. Query-count tests prove O(1) list projection, while
  scale tests assert item/byte/memory bounds and aggregate conservation. SQLite `EXPLAIN QUERY PLAN`
  and isolated MySQL `EXPLAIN` cover dominant History/Todo/Report/list paths. Middleware tests assert
  route-template-only duration/size events and absence of concrete IDs, query/search/cursor values or
  child content. Timing comparisons use identical fixtures/environments; skipped MySQL or staged
  checks remain explicit release risks.

## Gates

```bash
uv run pytest --cov=push_kids --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run mypy apps/api/src
npm test
npm run lint:miniapp
uv run python tools/check_architecture.py
uv run python tools/validate_design_evidence.py --check-current-policy
uv run python tools/validate_miniprogram.py
uv run python tools/audit_database.py data/push_kids.db --require-empty
uv run pytest tests/performance/test_read_paths.py -q
```

Isolated MySQL gate (blocking for backend cloud release — must be a real MySQL 5.7 server per `ARC-015`):

```bash
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic upgrade head
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic current
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic check
PUSH_KIDS_TEST_MYSQL_URL='mysql+pymysql://<test-user>:<password>@<host>/<isolated-db>' \
  uv run pytest tests/integration/test_mysql_runtime.py -q
```

No live provider call is required for deterministic CI. If `ARK_API_KEY` is present, a separately marked smoke test may run and must not print requests, images, responses or the key.

FEAT-013 grade gate: `test_grade_policy.py`, `test_grade_confirmation.py`,
`test_grade_confirmation_migration.py`, `test_grade_confirmation_reads.py` and frontend
`grade-confirmation.test.js` cover school-year boundaries, first confirmation, shared retries/conflicts,
manual intent/version, archive/unknown/terminal/permission boundaries, rollback, App sessions,
restoration at a safe host, stale in-flight bootstrap synchronization, report-filter exclusion and
manual conflict recovery requiring a fresh choice without losing drafts. `test_grade_confirmation_mysql.py` requires disposable `grade_*` MySQL5.7
runtime/migration databases through the existing test URL variables; never point it at production.
Both engines exercise 50k archived rows plus five active children, a single limited query, actual index
plans and 8KiB response budget. Historical-schema migration fixtures seed their frozen column list,
not current ORM defaults. `tools/prepare_grade_confirmation_native.py` creates an offline synthetic
copy and `tools/grade_confirmation_geometry.js` collects native rectangles/screenshots. The 2026-10-24
run covers 17 presentation states at all three viewports, profile controls, native picker opening/cancel
and a CUA-scrolled short-screen error. Layout fixtures do not prove actual
foreground/picker semantics, accessibility focus or iOS/Android. Subsequent reviewed lifecycle/conflict
repairs have automated evidence but no native end-to-end acceptance. Independent read-only review passed.
Actual results and unexecuted gates:
[2026-10-24 evidence](evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md).

FEAT-013 dialog simplification: approved `SPEC-20261024-GRADE-DIALOG-SIMPLIFICATION-01 / DREV02`
removes explanatory text and uses side-by-side later/confirm actions. Reuse the existing grade/profile/session
tests; update the old long-copy assertion without weakening the retained-choice/same-payload retry checks.
The native capture tool now writes to `evidence/grade-dialog-simplification-20261024/native/`, preserving
the original DREV01 evidence. Audit all three exact viewports for text/field clearance, 12px action gap,
approved flex allocation (including each button's padding), full-row containment, 44px targets and latest
fact without an editable picker. Long name, saving, error, conflict/latest and actual picker/retry/later
paths need fresh evidence; HTML and prior geometry are not substitutes. Final 327/53 automated checks,
51 fresh native states and actual picker/retry/later at each viewport passed. Computed button text contrast
is at least 4.5, including saving; the platform disabled-style override was fixed and all 51 states recaptured.
Unexecuted real-device/accessibility/full-business-native gates and distinct source stages are recorded in
[this change's evidence](evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md).

FEAT-011 renewal gate: `test_notification_renewal_policy.py`, `test_notification_renewal.py`,
`test_notification_renewal_migration.py`, `test_notification_renewal_reads.py` and frontend
`notification-renewal.test.js` / `notifications.test.js` cover actor receipts, transaction rollback,
per-type cooldown, original-event registration, identity changes and synchronous native wiring.
`test_notification_renewal_mysql.py` additionally requires disposable MySQL5.7 runtime and migration
databases via `PUSH_KIDS_TEST_MYSQL_URL` / `PUSH_KIDS_TEST_MYSQL_MIGRATION_URL`; never target production.
Its migration, concurrent sessions and 50k receipt/attempt reads passed locally on2026-10-17.
The ordinary suite skips it without explicit configuration; the separate run is recorded independently.
Native geometry uses `tools/notification_renewal_geometry.js` in a verified useCloud=false copy with
synthetic states. It cannot prove real authorization, remembered choices, accessibility focus or delivery.
See `docs/quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md` for actual coverage and
remaining device gates. The SQLite whole-schema Alembic check exposes four historical learning-record
index differences; the five new tables match metadata, and actual MySQL5.7 whole-schema check passes.

The BUG-027 release quality gate is stricter than ordinary CI and is run explicitly in a controlled secret-bearing
environment. It is blocking for release even though ordinary deterministic CI remains secret-free:

```bash
PYTHONPATH=apps/api/src uv run python tools/evaluate_analysis_quality.py \
  --cases tests/fixtures/analysis_quality/cases.json --report <private-temp-report>
```

For a controlled latency A/B, run at least two paired samples (three or more for a release decision):

```bash
PYTHONPATH=apps/api/src uv run python tools/benchmark_ark_context_reuse.py --runs 3
```

The benchmark alternates mode order and prints only mode, duration, generation count and cached-token aggregate.
It does not prove a speedup when the two modes take different generation counts.
