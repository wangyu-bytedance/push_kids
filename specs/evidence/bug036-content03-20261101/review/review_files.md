# 待评审文件列表

scope: diff_only

diff_direction: approved baseline 10/13 → Content03 candidate 11/14

The initial HEAD inventory is in diff_files.md and is not the review patch.
Approved scope and complete hashes: ../manifest.json; patch: ../content03.diff.
Include relevant new tests even though the default script filters test paths.

- apps/api/src/push_kids/agent_processing/pipeline.py
- apps/api/src/push_kids/agent_processing/stage_contracts.py
- apps/api/src/push_kids/agent_processing/prompt.py
- apps/api/src/push_kids/agent_processing/stage_provider.py
- apps/api/src/push_kids/agent_processing/failures.py
- apps/api/src/push_kids/agent_processing/telemetry.py
- tests/staged_analysis_fakes.py
- tests/unit/test_staged_analysis.py
- tests/unit/test_staged_proposal_recovery.py
- tests/unit/test_stage_provider.py
- tests/unit/test_provider_evidence.py

Context includes approved Spec/Prompt, Feature, Behavior, Architecture, Test
policy and existing checkpoint integration tests. Earlier cache/worker/learning
and parallel frontend changes are not Content03 implementation changes.
