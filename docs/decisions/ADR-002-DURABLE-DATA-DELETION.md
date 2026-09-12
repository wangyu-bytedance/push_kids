# ADR-002: Durable cross-domain data deletion

- Status: ACCEPTED
- Date: 2026-09-06
- Decision owners: 产品负责人（用户）
- Technical area: data lifecycle, privacy, modular boundaries, background work
- Related Spec: `specs/completed/FEAT-006-DATA-CLEANUP-AND-FAMILY-RESET.md` revision `SPEC-20260906-DATA-CLEANUP-01`
- Related ADRs: `ADR-001-WECHAT-CLOUD-HOSTING-MYSQL.md`
- Supersedes: N/A

## 1. Decision

We will implement permanent child/family deletion as a durable, idempotent `data_management` application workflow.
The accepting transaction revalidates the trusted family and role, freezes the target against new writes and persists a
deletion request. A worker then removes private media and calls narrow purge contracts owned by each domain, verifies no
target residue, and only then marks the request succeeded. Family deletion additionally requires the requester to be the
only active family member and clears the surviving actor binding to `unbound`. Completed minimal tombstones are retained
for 30 days for status/idempotency and then removed.

This decision becomes `ACCEPTED` only together with explicit approval of `SPEC-20260906-DATA-CLEANUP-01`.

## 2. Context

### Problem

Child/family data spans relational rows and private object storage. A synchronous ORM cascade cannot atomically cover both,
and existing foreign keys do not form a complete database cascade graph. Reporting success after deleting only one side can
leave private media or rows behind; allowing writes during cleanup can create data after the purge inventory is taken.

### Decision drivers

1. Never delete outside the verified family/target and never report success with residue.
2. Survive process restarts, dependency failures and duplicate client requests.
3. Preserve domain data ownership and an acyclic module graph.
4. Minimize retained identity/content after completion.
5. Keep existing archive/restore and old family-create clients compatible.

### Current facts

- `Child` has only an `active` archive flag; no physical delete path exists.
- Family/child data is distributed across families, children, learning, knowledge, planning, activities, calendar, jobs and media.
- Cloud media deletion is an external side effect and cannot share a transaction with MySQL.
- The application already runs a durable analysis worker pattern and requires idempotent background jobs with terminal states.
- Family roles have no separate immutable owner role; manager is the highest authority.

### Assumptions

- The user intends permanent deletion, not another soft-delete state; approval of the related Spec validates this.
- Deletion may complete asynchronously while the UI shows a recoverable pending state.
- A 30-day minimal tombstone balances client retry/status recovery with data minimization; a future approved privacy policy may revise it.

### Constraints

- Server-derived WeChat actor/family context is authoritative; client IDs never authorize.
- Routers delegate; domain modules do not directly mutate another domain's tables.
- No child names, raw OpenID, media paths, confirmation strings or raw payloads enter logs/tombstones.
- Physical purge is irreversible; rollback can stop new acceptance but cannot restore purged user data.

## 3. Options considered

### Option A — Durable orchestration with freeze and owned purge contracts (chosen)

- Description: add one cross-domain application owner, persistent lifecycle and target freeze; domains expose narrow purge operations.
- Benefits: restart-safe, explicit order/ownership, testable residue and fault behavior, compatible with external media.
- Costs: new schema, worker lifecycle, write-gate coverage and operational monitoring.
- Risks: missing one writer or owned table; controlled by exhaustive inventory, freeze tests and residue verification.
- Reversibility: acceptance can be disabled; accepted/purging requests must continue to terminal state.
- Evidence/experiment: SQLite/MySQL concurrency, fault injection, real private-storage cleanup and restart tests required by the Spec.

### Option B — Synchronous request with manual delete order

- Description: delete objects and rows inside one HTTP request.
- Benefits: smaller UI/API surface and immediate response on small local fixtures.
- Costs: request timeouts and no durable progress/retry after process failure.
- Risks: DB/object-store partial completion; unsafe success/retry ambiguity.
- Reversibility: poor once either side commits.
- Evidence/experiment: rejected by the existing non-transactional storage boundary.

### Option C — ORM/database cascade or reuse archive

- Description: cascade from Family/Child, or only set the existing archive flag.
- Benefits: little application code; archive is recoverable.
- Costs: current schema lacks a complete cascade chain and archive retains all private data.
- Risks: false deletion promise, orphan rows/media, invisible coupling to FK layout.
- Reversibility: archive is reversible but does not meet the requested contract; cascade is irreversible.
- Evidence/experiment: current model inventory shows plain `family_id` columns and external media objects.

### Option D — Retain current state

- Consequences: users cannot clean mistaken/stale families or exercise the requested data removal right; public deletion gate remains unresolved.
- When this would be preferable: only if product intent changes to archive-only and visible wording no longer promises deletion.

## 4. Rationale

Option A is the only candidate that can make the success claim depend on both database and object-store residue checks while
remaining restart- and retry-safe. A top-level application orchestrator is justified because deletion is one coherent use case
with consumers across several stable domain owners; placing it in families, children, routers or generic utilities would either
create dependency cycles or erase ownership. The sole-active-member guard compensates for the current absence of an owner/consent
model and prevents one manager from erasing other active members' shared family.

## 5. Consequences

### Positive

- Deletion has explicit authorization, lifecycle, retry, terminal state and verification semantics.
- Archive remains a clear recoverable alternative rather than being overloaded.
- Each domain remains authoritative for its own data and can test its purge contract.
- Client retries and worker restarts cannot create a second effect.

### Negative / accepted debt

- Every target writer must learn the authoritative freeze guard; missing one is a release blocker.
- A new worker/request schema and operational stuck-request handling are required.
- Physical deletion cannot offer restore after purge begins.
- Family deletion with active co-members is intentionally unavailable until a consent/owner model is designed.

### Operational

- Deployment: migration → backend/worker → staging verification → Mini Program.
- Monitoring: safe counts/age/retry/exhaustion/residue mismatch by request ID and type.
- On-call/runbook: pause new acceptance, inspect safe request state, retry idempotently; never edit purge scope by hand.
- Cost: bounded extra worker/database operations and object-store delete calls; no new third-party dependency.

### Security/privacy

- Authorization is verified again at acceptance; target ownership comes from server persistence.
- Ordinary target content/audit is purged. For 30 days the tombstone retains only request ID, requesting actor binding reference,
  target type, terminal state, timestamps and keyed fingerprints—never original target IDs/names or raw OpenID.
- Product analytics remain disabled; logs use safe state/error codes and correlation IDs only.

### Compatibility/migration

- Existing archive/restore and `POST /families` payloads with optional child remain supported.
- Old clients do not know the new endpoints and remain unaffected except that writes to a deleting target receive safe 409.
- Rollback keeps status reads and workers until every accepted request is terminal.

## 6. Guardrails

- Architecture rules created/changed: `data_management` is the sole orchestration owner; domains expose contracts and never import it.
- Automated enforcement: import DAG checker; contract tests; exhaustive model/table inventory test; writer-freeze mutation matrix.
- Tests: permissions/tenant, idempotency, double lease, late writes, restart/faults, residue, migration up/down and real storage.
- Metrics/alerts: nonterminal age, exhausted requests, retry count and residue mismatch; no user content labels.
- Forbidden usage: router/table deletion, client-computed scope, raw object path from request, synchronous false success, cascade without residue proof.

## 7. Rollout and rollback

- Rollout sequence: approve Spec/DREV/ADR; implement migration and worker; deploy API/worker; run isolated MySQL and real storage tests; publish UI.
- Feature flag/traffic control: endpoint availability is the server gate; no speculative long-lived product flag unless rollout requires it.
- Migration: forward-safe request/freeze state; no data backfill.
- Success signals: all accepted test requests terminal, zero residue mismatch, zero cross-tenant effects, no sensitive log output.
- Abort signals: authorization discrepancy, stuck/exhausted request, residue mismatch, old client regression or object-store uncertainty.
- Rollback or restore: stop new requests and revert UI/API exposure, but keep compatible schema/status/worker for accepted requests. Purged data is not restorable.

## 8. Revisit conditions

Revisit this decision when:

- product introduces account deletion/export, family ownership transfer or multi-party deletion consent;
- a complete database-enforced ownership/cascade graph and transactional media layer materially change the failure model;
- the approved privacy/legal policy requires a tombstone retention other than 30 days;
- cleanup volume or latency exceeds the worker SLO defined during implementation.

Owner for revisit: product and architecture owner.

## 9. Validation after adoption

| Hypothesis | Metric/evidence | Target | Review date | Result |
|---|---|---|---|---|
| success implies no target residue | exhaustive DB + object-store verification | 100% for test/staging fixtures | before release | pending |
| retries remain one effect | API/worker idempotency and restart tests | zero duplicate effects | before release | pending |
| freeze prevents late data | concurrent mutation matrix | zero accepted writes after freeze | before release | pending |
| other families remain unchanged | cross-tenant snapshots | byte/row-equivalent unaffected fixture | before release | pending |
| tombstone is minimal and expires | schema/log inspection + expiry job test | no prohibited fields; removed after 30 days | before release | pending |

## 10. Approval

- Approved by: 产品负责人（用户）
- Approval date: 2026-09-06
- Dissent/concerns retained: none；用户明确批准相关 Spec、ADR 和 scoped Figma waiver。
