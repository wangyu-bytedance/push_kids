# Test strategy — FEAT-001

## Required layers

- Unit: review intervals, feedback transitions, backfill, normalization and Todo grouping.
- Integration: SQLite transactions, family isolation, submission confirmation, activity records and reports.
- Contract: HTTP request/response shape, job lifecycle, upload validation and stable errors.
- Provider: deterministic adapter restricted to test/e2e plus Ark response-shape parser fixtures; live Ark smoke is secret-gated.
- Mini program: request client, formatters, state reducers and structural validator.
- Visual/runtime: WeChat DevTools compile and screenshots when CLI supports the local environment.
- MySQL: fresh Alembic migration, schema drift check, identity/family isolation, idempotency, Worker lease and confirmation transaction using `PUSH_KIDS_TEST_MYSQL_URL`.
- Cloud storage/identity: local fakes cover contract branches, but real two-account owner rules, metaid decode and public-ingress rejection are mandatory staging tests.
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
