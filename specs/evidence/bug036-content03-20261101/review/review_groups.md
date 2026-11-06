# BUG-036 Content03 independent review groups

SKILL_ROOT: `/Users/bytedance/.trae-cn/skills/bits-code-guard`
REPO_ROOT: `/Users/bytedance/Documents/push_kids`
WORK_DIR: `/Users/bytedance/Documents/push_kids/specs/evidence/bug036-content03-20261101/review`

Scope: the approved Content03 patch against the retained approval baseline.
The HEAD inventory includes unrelated and earlier work and is discovery only.
Authoritative scope: `../manifest.json` and `../content03.diff`.
Python files have no additional language-specific rule.

## Group 1: source, evidence and correction contracts

Read pipeline.py, stage_contracts.py, prompt.py and related staged tests.
Check original-source visibility, formal evidence ownership, source coverage,
correction isolation, summary and reuse contracts, empty candidates, and
independent test expectations. Review all seven dimensions and repository policy.

## Group 2: provider, budgets and recovery

Read stage_provider.py, failures.py, telemetry.py and provider tests.
Share pipeline.py/stage_contracts.py as boundary context, and read the existing
checkpoint/worker contracts without including earlier changes in this patch.
Check byte limits, bounded image reads, cancellation, source integrity, static
diagnostics, cache revisions and terminal review reuse, and test effectiveness.

Each group reports confirmed findings and limitations, per-file necessity and
placement, and relevant document status. Reviewers do not modify production code,
tests or current-state documentation. Reports belong to this directory.
