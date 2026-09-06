# Architecture constraints — aligned with `ARCH-20260906-TRAVEL-01`

These constraints originated in `ARCH-20260830-01`; the enforceable rules below remain active under the current
architecture revision. Historical `FDB`/`FEC`/`DREV-20260830-*` references are frontend design revisions, not
architecture-revision pointers.

- `ARC-001`: planning and normalization policies MUST be framework/database/network independent. Enforced by `tools/check_architecture.py` and unit tests.
- `ARC-002`: routers MUST only validate/map transport and call services; no review scheduling or provider calls in routers.
- `ARC-003`: module imports MUST remain acyclic; deep imports into another domain's persistence internals are forbidden.
- `ARC-004`: every business read/write MUST filter by trusted `family_id`; client-supplied resource IDs alone never authorize access.
- `ARC-005`: external files and model output MUST be validated for type, size, shape, enum and length before persistence or rendering.
- `ARC-006`: review dates MUST be created by `planning/domain.py`; model-proposed dates are ignored.
- `ARC-007`: submission confirmation MUST atomically create formal record, occurrences and review items, and mark the submission confirmed.
- `ARC-008`: retryable submission/job creation MUST use idempotency or duplicate detection; a running/succeeded job cannot be leased twice.
- `ARC-009`: job states are `queued`, `running`, `succeeded`, `failed`, `cancelled`; retries are bounded and errors omit secrets/raw child content.
- `ARC-010`: secrets MUST come from environment variables. `.env`, media and local databases are ignored by Git.
- `ARC-011`: public production deployment requires both (a) verified WeChat identity with public ingress rejecting
  client `X-Family-ID`, and (b) an approved privacy/deletion policy and operational flow. Gate (a) passed controlled
  staging on 2026-09-06 with two real accounts, owner isolation, metaid decoding and public-ingress rejection;
  gate (b) remains open, so public production is still blocked.
- `ARC-012`: no new global `common`, `utils`, `helpers` or service-locator module without an owned semantic contract.
- `ARC-013`: schema and public API changes require a Spec compatibility note and forward-safe migration plan.

## AI Native maintainability constraints

- `ARC-004 — Acyclic module graph`: production, test, and runtime-registration dependencies MUST remain a DAG; `tools/check_architecture.py` is the primary enforcement and new cross-module edges require focused tests.
- `ARC-005 — Purpose/domain decomposition`: code MUST be organized by coherent product capability and responsibility before technical layer; interfaces MUST NOT accumulate domain policy.
- `ARC-006 — Common code extraction has semantic ownership`: shared code requires an owner, stable contract, compatible change axis, declared consumers, allowed dependencies, and contract tests; syntax similarity alone is insufficient.
- `ARC-007 — Public boundaries preserve module positioning`: cross-capability access MUST use an owning service/contract and MUST NOT deep-import persistence tables or private implementation files.
- `ARC-008 — Architecture decisions are reasoned and recorded`: boundary, deployment, data-owner, or extension changes MUST record chosen design, rejected alternatives, trade-offs, maintainability impact, and revisit conditions in an approved Spec/ADR.
- `ARC-009 — Extensibility is explicit and bounded`: every variation axis MUST be classified open/closed/deferred; open points define registration, compatibility, isolation, resource, security, observability, test, deprecation, and removal rules.
- `ARC-013 — Architecture confirmation before coding`: before initial production coding or a change to modules, shared abstractions, dependency direction, deployment topology, or extension points, the owner MUST approve the exact architecture/Spec revision.

Exceptions require an approved Spec/ADR with owner, reason and expiry. The only active exception is the FEAT-001 Figma evidence waiver documented in `ARCHITECTURE.md`.
