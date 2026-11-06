# Historical Knowledge cleanup — 2026-10-31

- Spec: `SPEC-20261031-HISTORICAL-KNOWLEDGE-CLEANUP-01`
- Approved by: product owner, 2026-10-31 reply `批准`
- Backup gate: PASS — operator replied `备份完成 你可以进行操作了` before production apply; backup identity remains in the platform record.
- Approved pre-apply digest: `cdeff9d569eb22cec2b6b786a9b4d52838878fe7297d86b49de6c781a3964310`

## Verification

| Check | Result |
|---|---|
| Focused maintenance + supersession integration | PASS — 21 tests |
| Full unit/integration/contract gate immediately before apply | PASS — 793 passed, 46 skipped |
| Ruff changed files | PASS |
| Mypy maintenance module | PASS |
| Architecture DAG | PASS — 4 policies, 151 modules |
| Production dry-run before apply | PASS — exact approved digest; 15 clusters / 15 renames / 30 supersessions / 9 unresolved |
| Production apply | PASS — one transaction committed after backup confirmation |
| Post-apply approved-cluster dry-run | PASS — 0 remaining clusters |
| Canonical/search-index check | PASS — 15 normal canonical targets and all 15 indexed |
| Supersession linkage | PASS — 30 superseded rows, all 30 linked |
| Formal fact conservation | PASS — Knowledge 243, occurrences 243, learning records 112, feedback 455 before and after |

The first complete gate run had two failures: the approved Review stage made an old checkpoint-count assertion stale, and one worker-readiness timing test returned 503 once. The checkpoint test was corrected to assert the persisted Review checkpoint; targeted tests passed, the readiness case passed in isolation, and the complete gate then passed 793/46.

Nine vague rows remain unchanged because stored evidence is insufficient to name a concrete knowledge target without guessing. Three proposed groups were also excluded because their rows belong to different children; family/child/subject scope was not relaxed.

No schema migration, deployment, deletion, occurrence reassignment, feedback rewrite, mastery decision or reviewed-today event was performed.
