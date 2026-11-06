# Cache Spec02 exact task scope

scope: diff_only

Pre-task snapshot is authoritative; unrelated HEAD changes excluded. Include relevant untracked tests. Supplemental staged_analysis assertion reconstructed from unchanged test except approved revision string; not Red evidence.

- apps/api/src/push_kids/agent_processing/pipeline.py
- apps/api/src/push_kids/agent_processing/checkpoints.py
- apps/api/src/push_kids/agent_processing/worker.py
- apps/api/src/push_kids/agent_processing/stage_contracts.py
- apps/api/src/push_kids/learning/service.py
- tests/unit/test_staged_proposal_recovery.py
- tests/unit/test_staged_analysis.py
- tests/integration/test_analysis_checkpoints.py
- tests/integration/test_staged_mysql.py
