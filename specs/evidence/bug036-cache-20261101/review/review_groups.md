# Cache Spec02 independent review groups

Group 1 — Pipeline result and cache policy
- pipeline.py, stage_contracts.py, test_staged_proposal_recovery.py, test_staged_analysis.py
- Check final refusal reads/writes, intermediate recovery, original validation/deadline/budgets.

Group 2 — Retry and worker persistence
- checkpoints.py, worker.py, learning/service.py, test_analysis_checkpoints.py, test_staged_mysql.py
- Check family/child/job/submission lock order, state re-read, semantic whitelist, rollback,
  late lease/SQL protections, missing-job repair and no formal writes.
- stage_contracts.py shared as the revision boundary; pipeline.py may be read for direct failure inputs.

All reviewers: exact task.diff and source-manifest.json, REVIEW.md and approved Spec02.
Do not review unrelated pending changes or treat old content failures as cache regressions.
Documentation review will run after final current-fact updates, against this same code snapshot.
