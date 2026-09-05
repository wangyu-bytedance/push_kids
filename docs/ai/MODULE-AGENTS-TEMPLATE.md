# [Module Name] Agent Instructions

> 将本文件复制为目标模块目录下的 `AGENTS.md`。只写相对仓库根规则的增量，不复制根 `AGENTS.md`。
>
> `AGENTS.override.md` 仅用于明确的临时覆盖；必须说明原因、Owner 和删除日期。

## 1. Scope

- Applies to: `[relative paths]`
- Module purpose: `[one sentence]`
- Owner: `[team/person]`
- Public entry points: `[paths/APIs/events]`
- Source-of-truth docs: `[module architecture/behavior/runbook links]`

## 2. Local commands

```bash
# Focused tests
[TODO: exact command]

# Module lint/type/build
[TODO: exact command]

# Integration/contract tests
[TODO: exact command]
```

These commands refine the repository-level commands; they do not waive required
root validation.

## 3. Boundary and ownership

This module owns:

- `[business capability/data/contract]`

This module does not own:

- `[responsibilities delegated elsewhere]`

Allowed dependencies:

- `[module/public API]`

Forbidden dependencies:

- `[internal paths/tables/framework layers]`

Other modules MUST interact through:

- `[public interface/event/query]`

## 4. Local invariants

- `[INV-ID: invariant that must remain true]`
- `[authorization/tenant/data/state invariant]`

Before changing one of these invariants, update the relevant Spec and behavior
catalog entry and obtain `[required owner]` approval.

## 5. Local conventions

- Entry/handler pattern: `[TODO]`
- Error model: `[TODO]`
- Transaction owner: `[TODO]`
- Async/idempotency pattern: `[TODO]`
- Test fixture/factory pattern: `[TODO]`
- Generated files and source command: `[TODO or N/A]`

Only include rules that differ from or concretize root guidance.

## 6. High-risk files/areas

| Path/area | Risk | Required review/evidence |
|---|---|---|
| `[TODO]` | `[auth/money/migration/etc.]` | `[owner + tests]` |

## 7. Review rules

- `[module-specific failure to flag]`
- Safe path/exception: `[how to do it correctly]`
- `[domain-specific compatibility rule]`

Formatting and naming rules already enforced by CI SHOULD NOT be repeated here.

## 8. Temporary exceptions

| Exception | Reason | Authority | Owner | Removal condition/deadline |
|---|---|---|---|---|
| None |  |  |  |  |

If this is an `AGENTS.override.md`, it MUST include at least one active
exception and MUST be deleted when the removal condition is met.
