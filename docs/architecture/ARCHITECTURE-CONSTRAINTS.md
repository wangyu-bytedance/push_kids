# Architecture constraints — aligned with `ARCH-LOCAL-DESIGN-EVIDENCE-20260913-01`

These constraints originated in `ARCH-20260830-01`; the enforceable rules below remain active under the current
architecture revision. Historical `FDB`/`FEC`/`DREV-20260830-*` references are frontend design revisions, not
architecture-revision pointers.

Approved frontend extension `ARCH-20261106-MINIAPP-THEMES-01` (DESIGN-002 Spec08): `presentation/theme` owns bounded compiled theme registration, local display state and explicit lifecycle adapters. It must not import pages, API or business utilities; pages/components depend toward the presentation domain. Registry values generate first-paint tokens and all theme checks. No global Page/Component replacement, business reload on switching, remote theme injection or duplicated business controllers. `node tools/check_themes.js` enforces the frontend boundary/schema/resource contract alongside the existing architecture checker. Existing server constraints remain unchanged.

- `ARC-001`: planning and normalization policies MUST be framework/database/network independent. Enforced by `tools/check_architecture.py` and unit tests.
- `ARC-002`: routers MUST only validate/map transport and call services; no review scheduling or provider calls in routers.
- `ARC-003`: module imports MUST remain acyclic; deep imports into another domain's persistence internals are forbidden.
- `ARC-004`: every business read/write MUST filter by trusted `family_id`; client-supplied resource IDs alone never authorize access.
- `ARC-005`: external files and model output MUST be validated for type, size, shape, enum and length before persistence or rendering.
- `ARC-006`: review dates MUST be created by `planning/domain.py`; model-proposed dates are ignored.
- `ARC-007`: submission confirmation MUST atomically create formal record, occurrences and review items, and mark the submission confirmed.
- `ARC-008`: retryable submission/job creation MUST use idempotency or duplicate detection; a running/succeeded job cannot be leased twice. Define scope, duplicate response, concurrent duplicates and recovery at meaningful side-effect checkpoints. Sequential/concurrent retry and interruption tests MUST verify durable final state and absence of forbidden duplicate effects; a key alone does not prove crash safety.
- `ARC-009`: job states are `queued`, `running`, `succeeded`, `failed`, `cancelled`; retries are bounded and errors omit secrets/raw child content.
- `ARC-010`: secrets MUST come from environment variables. `.env`, media and local databases are ignored by Git.
- `ARC-011`: public production deployment requires both (a) verified WeChat identity with public ingress rejecting
  client `X-Family-ID`, and (b) an approved privacy/deletion policy and operational flow. Gate (a) passed controlled
  staging on 2026-09-06 with two real accounts, owner isolation, metaid decoding and public-ingress rejection;
  gate (b) remains open, so public production is still blocked.
- `ARC-012`: no new global `common`, `utils`, `helpers` or service-locator module without an owned semantic contract.
- `ARC-013`: schema and public API changes require a Spec compatibility note and forward-safe migration plan.
- `ARC-014 — Bounded read paths`: every collection or embedded-list API MUST declare a stable total
  order, default/max page size, continuation/end semantics, snapshot behavior and compatibility. A
  router limit is insufficient when service work is still unbounded. Counts and reports aggregate at
  the database-owner boundary and materialize only O(page-size/bucket-count) rows; list projections
  use O(1) queries in page size. Growing tenant queries require tenant-leading composite indexes,
  SQLite/MySQL plan evidence, comparable latency/memory/response budgets and safe route-template
  observability. Exceptions require an approved measured Spec with an owner and expiry.
- `ARC-015 — Database dialect and version compatibility`: runtime SQL owned by services MUST execute on the
  production engine, WeChat Cloud Hosting CynosDB MySQL `5.7.18` (InnoDB, `utf8mb4`), and on local/test SQLite.
  Window functions (`OVER (...)`), CTEs (`WITH ... AS`), functional indexes, enforced `CHECK` constraints and
  other MySQL-8-only features are forbidden until an independently approved migration Spec raises the baseline.
  Every release that changes SQL MUST prove the affected paths on a real MySQL 5.7 server; SQLite compilation or
  MySQL 8 evidence cannot substitute. Enforced by `tests/integration/test_mysql_runtime.py`, the read-path
  performance/plan tests, and the Database support matrix in `ARCHITECTURE.md`.
- `ARC-016 — Repository-native frontend design evidence`: user-visible frontend work MUST use an approved
  Task Spec revision and Design Revision backed by a repository-local editable SVG or self-contained HTML
  source, required viewport/state exports and a matching SHA-256 approval manifest. Figma, external design
  URLs, node IDs and tool-availability waivers are not required. Repository previews do not replace native
  Mini Program geometry, interaction, accessibility or three-viewport evidence.

## AI Native maintainability constraints

- `ARC-004 — Acyclic module graph`: production, test, and runtime-registration dependencies MUST remain a DAG; `tools/check_architecture.py` is the primary enforcement and new cross-module edges require focused tests.
- `ARC-005 — Purpose/domain decomposition`: code MUST be organized by coherent product capability and responsibility before technical layer; interfaces MUST NOT accumulate domain policy.
- `ARC-006 — Common code extraction has semantic ownership`: shared code requires an owner, stable contract, compatible change axis, declared consumers, allowed dependencies, and contract tests; syntax similarity alone is insufficient.
- `ARC-007 — Public boundaries preserve module positioning`: cross-capability access MUST use an owning service/contract and MUST NOT deep-import persistence tables or private implementation files.
- `ARC-008 — Architecture decisions are reasoned and recorded`: boundary, deployment, data-owner, or extension changes MUST record chosen design, rejected alternatives, trade-offs, maintainability impact, and revisit conditions in an approved Spec/ADR.
- `ARC-009 — Extensibility is explicit and bounded`: every variation axis MUST be classified open/closed/deferred; open points define registration, compatibility, isolation, resource, security, observability, test, deprecation, and removal rules.
- `ARC-013 — Architecture confirmation before coding`: before initial production coding or a change to modules, shared abstractions, dependency direction, deployment topology, or extension points, the owner MUST approve the exact architecture/Spec revision.

## TDD-supporting state and data constraints

Governance revision: `ARCH-GOV-20261028-TDD-CODING-REVIEW-01`, approved under
[GOV-003 Spec01](../../specs/completed/GOV-003-TDD-CODING-REVIEW-INCREMENTAL-MERGE.md).
Runtime architecture and existing bounded-read, MySQL and frontend constraints remain unchanged.
Earlier duplicated IDs are qualified by their section/title; new rules use unoccupied IDs.

### ARC-017 — Mutable state ownership

- **Rule**: Independent actors MUST isolate mutable state when shared authority is unnecessary.
  Required shared state MUST have one explicit logical write authority enforced by the owning
  service/command, actor/queue, or database transaction/version protocol. Retries and recovery
  MUST preserve that authority; multiple physical instances may use the same protocol.
- **Why**: Correct ownership/lifecycle before choosing serialization; locks must not conceal
  unrelated actors sharing buffers, competing independent rules, or duplicate responsibility.
- **Allowed**: Per-request/per-worker state, immutable shared values, existing owner service with
  atomic/versioned commands. No new actor/queue/framework is required by this rule.
- **Enforcement**: State/owner map and Review; changed paths require Spec-selected repeated,
  concurrent and interruption/recovery tests. `tools/check_architecture.py` checks dependencies,
  not the semantic correctness of mutable-state ownership.
- **Exception/Owner**: An approved Spec/ADR states scope, invariant-preserving protocol, project
  owner, verification and expiry/revisit condition; otherwise no unowned shared state is allowed.

### ARC-018 — Validated domain states

- **Rule**: Model data shapes and domain terms before branching. Parse external input once per
  trust boundary into validated Schema/value objects; constructors and transitions preserve
  invariants. Keep planning policy pure. Internal validated values do not replace authorization
  or validation at a new trust boundary.
- **Forbidden**: Unchecked casts/suppressed errors as fixes, repeated raw parsing throughout
  policy, or ambiguous boolean/null combinations encoding illegal states.
- **Enforcement**: Existing Pydantic/transport contracts and mypy as applicable; changed paths
  need invalid-input/transition tests and domain-term Review. These are required verification
  responsibilities, not a claim that every existing path has been re-audited.
- **Exception/Owner**: An approved Spec/ADR records the project owner, reason, evidence and
  expiry/revisit condition before relaxing a constraint.

Exceptions require an approved Spec/ADR with owner, reason and expiry. There is no active external-design-tool evidence exception.
