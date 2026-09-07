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
  `template_field_missing` without calling the provider or spending a grant, then re-armable), stacked
  one-off grants (repeat accepts accumulate quota, a per-dialog `reject` keeps quota already granted and
  a `ban`/`filter` zeroes it), the 30-day
  retention window and the dispatch trigger token. Integration template fixtures must keep the field
  shape of the templates actually selected in the WeChat console, so a mapping mistake fails a test
  instead of a real send. Business
  time is injected explicitly; a test that reads wall-clock 19:00 is invalid. Live WeChat send and real
  `wx.requestSubscribeMessage` acceptance remain manual, staged gates.
- Reminder settings screen: page tests must prove that the switch state and the WeChat grant state stay
  separate — a failed preference write rolls the switch back, only an `accept` decision is reported as
  authorized (with WeChat's own `reject`/`ban`/`filter` wording passed through), an unavailable channel
  or an old WeChat client requests nothing, and unreadable delivery
  history degrades only that section. Because the console offers one-off templates only, tests must also
  cover the remaining-quota wording, the top-up path (least remaining quota first, three templates max)
  and that a long-term template never asks the parent to stockpile messages.
  `wx.requestSubscribeMessage` is stubbed; the grant call must be
  asserted to happen before any awaited request so the real client keeps its user gesture.
- Silent renewal: the decision to top up is a pure function over a cached snapshot and must be tested for
  every refusal reason (enough quota, long-term template, unavailable channel, stale snapshot, never
  granted, cooldown, WeChat main switch off) as well as target ordering (emptiest first, three max). The
  plumbing tests must prove that a natural tap both requests the grant and still completes its own
  business request, that a declined dialog starts the cooldown, that a client without
  `wx.requestSubscribeMessage` degrades to doing nothing, and that a failed snapshot refresh never breaks
  the page that asked for it. Real-device dialog timing stays a manual gate.
- Subscription event callback: no test may reach a real WeChat endpoint. Unit covers signature
  verification (wrong token, tampered timestamp/nonce, missing token), JSON and XML parsing, single-object
  and array `List`, unknown status values, ignored event types, oversized bodies and refused
  doctype/entity declarations. Integration must cover URL verification echo, a forged signature (403), a
  deployment without the push token (404), an unreadable or oversized body (400), a popup `reject` keeping
  stored quota, a `change` refusal clearing it, a `ban` clearing it, an `accept` adding no quota, an
  unknown receiver or template changing nothing, a non-zero delivery error code correcting an
  optimistically `sent` row, and a legacy destination without the HMAC index still being matched and
  backfilled. Real event push from the WeChat console stays a manual, staged gate.
- Deployment configuration: `tools/notification_config.py check` must agree with the runtime template
  parser and the 32-character key rule, and must never print the key itself. `from-wechat` converts a
  WeChat `gettemplate` response offline; its output must parse with the runtime parser and it must
  refuse unknown notification types, unknown template ids and error payloads. Its label-driven mapping
  must be asserted against the console template bodies, including that `开始时间` wins over a generic
  `时间` slot.
- MySQL: fresh Alembic migration, schema drift check, identity/family isolation, idempotency, Worker lease and confirmation transaction using `PUSH_KIDS_TEST_MYSQL_URL`.
- Cloud storage/identity: local fakes cover contract branches, but real two-account owner rules, metaid decode and public-ingress rejection are mandatory staging tests.
  Staging status: **PASS (2026-09-06, operator-confirmed)** — two real accounts exercised owner isolation,
  metaid decoding, and public-ingress rejection. This closes this test-strategy gate but does not close the
  separate privacy/deletion, backup/restore, worker-topology, device, or production-release gates.
- Container: build, non-root UID, unprivileged internal port 8000, deployment-config consistency,
  live/ready and graceful termination.

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
```

Optional isolated MySQL gate (required for cloud release):

```bash
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic upgrade head
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic current
PUSH_KIDS_DATABASE_URL='mysql+pymysql://<migration-user>:<password>@<host>/<db>' uv run alembic check
PUSH_KIDS_TEST_MYSQL_URL='mysql+pymysql://<test-user>:<password>@<host>/<isolated-db>' \
  uv run pytest tests/integration/test_mysql_runtime.py -q
```

No live provider call is required for deterministic CI. If `ARK_API_KEY` is present, a separately marked smoke test may run and must not print requests, images, responses or the key.
