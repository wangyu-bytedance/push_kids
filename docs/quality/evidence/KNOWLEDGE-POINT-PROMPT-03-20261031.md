# SPEC-20261031-KNOWLEDGE-POINT-PROMPT-03 evidence

- Subject revision: `staged-20261031-06` / `child-aware-history-agent-20261031-10`
- Scope: source, read-only production-history replay and immutable backend gray delivery.
- Formal production writes during replay: `0` by tool contract (repeatable-read/read-only snapshot; model proposals are not confirmed).

## Verification

| Check | Result |
|---|---|
| Focused unit + confirmation/history/supersession integration | PASS — 75 tests |
| Ruff check and format check on changed Python files | PASS |
| Historical text-only replay | PARTIAL — 3/4 attempts produced one evidence-backed point and completed history lookup; 1/4 failed safely with `coverage` and produced no proposal |
| Historical lexical comparison | All 3 successful attempts differed lexically from the old confirmed name; comparison evidence only, not independent semantic correctness proof |
| Historical image replay | NOT_RUN — private media download helper could not obtain media in this local environment |
| Child with >100 historical items | NOT_RUN — replay tool stopped at its explicit `history_snapshot_cap`; production lookup remains independently bounded |
| Cloud delivery | PASS — immutable `flask-ik19-038` reached `normal` at 2026-10-31 11:40:08 +08:00; service normal, PUBLIC closed, Schema unchanged at `20261024_0025` |
| Directed 038 live/ready and business smoke | NOT_RUN — traffic split is not exposed by CLI and no directed gray traffic or cutover was performed |

Raw aggregate-only replay reports are retained in `specs/evidence/knowledge-point-prompt-03-historical-replay*.json`; they contain aliases, counts, hashes and failure codes, not child material text.

## Observed outcome

Historical equivalence now requires the same subject, core target, compatible scope and review action. Related, prerequisite, broader/narrower and successor knowledge are explicitly non-equivalent. A deterministic regression proves that two generated variants resolving to one historical Knowledge ID become one history proposal while preserving evidence from both sources. Parent confirmation remains the only path that writes a reviewed-today fact.
