# Behavior catalog — FEAT-001

| ID | Behavior | Owner | Verification |
|---|---|---|---|
| `BHV-001` | Parent creates children and learning/activity subjects | children | API integration tests |
| `BHV-002` | Parent uploads one or more photos or manually enters learning with occurrence time | learning | contract/integration tests |
| `BHV-003` | Analysis runs asynchronously and yields editable proposal or actionable failure | agent_processing | worker tests |
| `BHV-004` | Only parent confirmation creates formal learning/knowledge/review data | learning + knowledge + planning | transaction tests |
| `BHV-005` | Repeated knowledge reuses identity and keeps every occurrence | knowledge | dedup unit/integration tests |
| `BHV-006` | Review schedule follows deterministic memory-curve policy | planning | policy unit tests |
| `BHV-007` | Historical backfill produces a current check, not past Todo debt | planning | backfill unit test |
| `BHV-008` | Daily Todo is grouped under a time budget and accepts four feedback types | planning | service tests |
| `BHV-009` | Activity schedules suggest practice and show last practice without mandatory review | activities | integration tests |
| `BHV-010` | Dashboard/report/calendar summarize confirmed evidence only | reporting | reporting tests |
| `BHV-011` | Every resource is isolated by family scope | platform | cross-family tests |
| `BHV-012` | Cloud requests derive family scope from a bound WeChat actor and reject client family authorization | platform | cloud identity + real two-account tests |
| `BHV-013` | Cloud images use server-issued private upload paths and are claimed only after uploader/path/content validation | media + learning | adapter tests + real storage E2E |
