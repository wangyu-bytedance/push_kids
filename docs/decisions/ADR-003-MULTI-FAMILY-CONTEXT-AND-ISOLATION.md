# ADR-003: 多家庭上下文、兼容迁移与隔离门禁

- Status: PROPOSED
- Date: 2026-09-11
- Decision owners: 产品负责人（用户）
- Technical area: identity / tenancy / persistence / Mini Program context
- Related Spec: `specs/active/FEAT-002-MULTI-FAMILY-CHILD-TENANT-ISOLATION.md` revision `SPEC-20260911-MULTI-FAMILY-06`
- Related ADRs: `ADR-001-WECHAT-CLOUD-HOSTING-MYSQL.md`
- Supersedes: N/A

## 1. Decision

We will model a trusted WeChat actor as having multiple family-scoped memberships, resolve every business request from
trusted actor plus an untrusted `X-Selected-Family-ID`, and keep child selection subordinate to the verified family.
The existing single-family data remains in place. S1–S4 may run behind a staging-only feature flag, but public enablement
and the phrase “database-enforced complete isolation” require S5 composite constraints and S6 migration/cloud evidence.
An editor/viewer may explicitly leave one selected family; managers must first hand off and be demoted. Member WeChat
avatars/nicknames are deferred as a low-priority, separately specified feature; this decision adds no member profile data.

## 2. Context

### Problem

Current `wechat_actor_bindings.family_id` and the unique active actor projection allow only one active family per actor.
The product needs a parent to access, for example, both their own household and a grandparent household without splitting
families, moving children, or introducing child-level roles.

### Decision drivers

1. Cross-family confidentiality and write integrity.
2. Compatibility with existing one-family/multi-child data and current clients.
3. Reuse of current family roles and UI-015 child profile behavior.
4. Reversible rollout across SQLite development and Cloud Hosting MySQL.

### Current facts

- `Family 1:N Child` is already the persisted model.
- `FamilyMember` currently has global `UNIQUE(active_actor_binding_id)`.
- Client state has one global `selectedChildId` and no selected-family header.
- Most child-owned rows carry family and child IDs, but composite FK coverage is incomplete.
- Current self-removal is rejected and current member rows have only relationship/role, with no user name/avatar fields.

### Assumptions

- The gateway continues to provide the trusted WeChat actor identity validated by ADR-001.
- MySQL and SQLite retain their documented multiple-NULL behavior for the proposed active projection; migration tests
  must prove parity before cutover.

### Constraints

- Client family and child IDs never authorize access.
- Existing child IDs, historical records, `occurred_at`, and `created_at` must not be rewritten.
- Leaving a family ends only that membership and never deletes family learning data.
- OpenID/metaid are authentication identifiers, not profile-display sources.
- No public enablement without real multi-account/multi-family cloud evidence.

## 3. Options considered

### Option A — Shared database with verified family context and composite constraints

- Description: actor+family memberships, explicit selected-family context, family-first queries, staged composite FK rollout.
- Benefits: compatible with the modular monolith and existing data; DB can reject mismatched family-child-parent chains.
- Costs: S5 touches all child-owned domains and needs a controlled MySQL migration.
- Risks: partial rollout could be overstated as complete isolation; public gate prevents that.
- Reversibility: additive expand and feature flag are reversible before contract migration.

### Option B — Application filtering only

- Description: add family selection and rely on service/repository filters.
- Benefits: delivers staging UI sooner.
- Costs: one missed filter can create a cross-tenant write; database cannot prove consistency.
- Risks: unacceptable as the final R3 public boundary.
- Reversibility: usable only as a temporary staging phase.

### Option C — One database/schema per family

- Description: physically separate tenant storage.
- Benefits: stronger physical isolation.
- Costs: disproportionate provisioning, migrations, pooling, backup, and worker complexity for current scale.
- Risks: operational failures and cross-schema orchestration become the dominant risk.
- Reversibility: expensive.

### Option D — Retain one actor/one family

- Consequences: cannot satisfy the stated user journey.
- When this would be preferable: only if multi-family access is removed from product scope.

## 4. Rationale

Option A keeps the established family tenant boundary and family-wide role model while adding only the missing actor-to-
family cardinality. Separating staging usability from public enablement permits incremental verification without weakening
the final isolation claim. Options B and C respectively under-enforce security or over-expand operations.

## 5. Consequences

### Positive

- Existing families, children, records, and roles remain stable.
- The server owns authorization; selection remains an untrusted preference.
- Composite constraints make wrong-family chains fail even if application code regresses.

### Negative / accepted debt

- During the compatibility window, singular and multi-family bootstrap contracts coexist.
- S5 is a broad migration and cannot be reduced to a UI-only release.

### Operational

- Deployment: audit → expand → backfill → validate → staging flag → S5/S6 → public enablement → contract.
- Monitoring: count selection-required, upgrade-required, denied/revoked membership, discarded stale response and
  migration inconsistency events without logging family/child names or raw identifiers.
- On-call/runbook: disable the multi-family flag on any leak, wrong role, stale render, invalid composite row, or DB parity failure.
- Cost: extra membership/context queries and migration indexes; bootstrap must avoid loading family content.

### Security/privacy

Only minimal family/child labels are returned by actor-only bootstrap. Logs exclude selector values, names, raw OpenID,
media IDs and model payloads. Cache and idempotency namespaces include verified family scope. Member rows retain the
current relationship label and first-character avatar; this decision does not collect or store WeChat profile data.

### Compatibility/migration

The current singular contract remains only for actors with exactly one active family. A legacy client facing multiple
families receives `client_upgrade_required`, never an arbitrary fallback. Compatibility lasts at least 30 days and two
formal Mini Program releases, and ends only with usage evidence.

## 6. Guardrails

- Architecture rules created/changed: `FamilyContext` is immutable and verified; role is never actor-global.
- Automated enforcement: actor+family active uniqueness, S5 composite FK/unique checks, dependency/architecture checks.
- Tests: endpoint × foreign family/child/resource matrix, SQLite/MySQL invalid insert, files/jobs, client race and migration rehearsal.
- Metrics/alerts: safe aggregate counters only; no tenant or child names in telemetry.
- Forbidden usage: authorizing from selector, `wechat_actor_bindings.family_id`, last UI selection, or an ID-only child lookup.
- Forbidden usage: auto-demoting a manager during leave or deriving display data from OpenID/metaid.

## 7. Rollout and rollback

- Rollout sequence: S1 characterization; S2 expand/context; S3 UI behind flag; S4 matrix; S5 constraints; S6 cloud evidence/document merge.
- Feature flag/traffic control: allowlisted staging actors only until S5/S6 pass.
- Migration: preserve IDs and content; stop on any ambiguous ownership instead of guessing.
- Success signals: all automated matrices pass plus native three-viewport and real multi-account cloud evidence.
- Abort signals: any cross-family read/write, wrong-family role, stale render, orphan scope, or SQLite/MySQL mismatch.
- Rollback or restore: disable selection, retain schema and memberships, keep multi-family legacy clients at upgrade gate;
  never delete memberships or choose the old binding projection.

## 8. Revisit conditions

Revisit this decision when cross-family aggregation, child migration, child-specific grants, physical tenant storage, or
the deferred member avatar/nickname capability becomes an approved product requirement. The member profile capability
requires its own privacy, storage and lifecycle Spec rather than an amendment during implementation.

Owner for revisit: 产品负责人（用户）

## 9. Validation after adoption

| Hypothesis | Metric/evidence | Target | Review date | Result |
|---|---|---|---|---|
| Existing data migrates without reassignment | sanitized migration rehearsal | zero rewritten child/family IDs | before S2 cutover | pending |
| Context prevents tenant crossover | API/file/job matrix | zero leak/write | before staging flag | pending |
| DB rejects mismatched chains | SQLite/MySQL constraint suite | all invalid inserts rejected | before public enablement | pending |
| UI never renders stale family data | native race/state suite | zero stale frames/responses | before public enablement | pending |
| Leaving affects one membership only | role/scope/history integration suite | editor/viewer allowed, manager denied, other families/history unchanged | before staging flag | pending |

## 10. Approval

- Approved by: pending
- Approval date: pending
- Dissent/concerns retained: pending
