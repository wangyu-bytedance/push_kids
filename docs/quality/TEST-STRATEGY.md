# Test strategy — FEAT-001

## Required layers

- Unit: review intervals, feedback transitions, backfill, normalization and Todo grouping.
- Integration: SQLite transactions, family isolation, submission confirmation, activity records and reports.
- Contract: HTTP request/response shape, job lifecycle, upload validation and stable errors.
- Provider: deterministic adapter restricted to test/e2e plus Ark response-shape parser fixtures; live Ark smoke is secret-gated.
- Mini program: request client, formatters, state reducers and structural validator.
- Visual/runtime: WeChat DevTools compile plus 320×568、390×844、430×932 captures for changed states. Record renderer, base library, DPR, font scale and source revision.
- Native geometry: ordinary page roots must not move horizontally; seven-day, three-range, four-budget and seven-weekday controls must all be visible. Circular controls have a width/height difference of at most 1px and regular touch targets are at least 44px. `overflow-x:hidden` and HTML screenshots do not satisfy this gate.
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
