# 2026-10-31 historical Knowledge cleanup

- Scope: production data repair only; no backend image, Mini Program upload, Schema migration or configuration change.
- Spec: `SPEC-20261031-HISTORICAL-KNOWLEDGE-CLEANUP-01`
- Backup: operator confirmed successful production backup and recovery path before apply.
- Pre-apply digest: `cdeff9d569eb22cec2b6b786a9b4d52838878fe7297d86b49de6c781a3964310`.
- Apply result: 15 canonical renames and 30 permanent supersession links committed in one transaction.
- Conservation: Knowledge 243, occurrences 243, learning records 112, feedback 455 before and after.
- Post-check: 213 normal / 30 superseded; all 30 linked; 15/15 canonical rows indexed; approved-cluster dry-run is empty; 9 vague rows intentionally unresolved.
- Deployment state: cleanup runtime support and the paired prompt/review increment were cloud-delivered as immutable gray backend `flask-ik19-038` (`normal` at 2026-10-31 11:40:08 +08:00). The cleanup data apply itself preceded deployment and is not repeated. Traffic/candidate smoke remains NOT_RUN; this operation does not claim an experience version, review or formal publication.
- Recovery: use the operator-confirmed pre-apply backup if semantic rollback is required; do not ad-hoc reverse supersession.
