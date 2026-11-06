# 2026-10-31 knowledge prompt backend gray deployment

- Scope: knowledge-point extraction/consolidation quality review, one bounded correction, strict historical semantic equivalence and same-Knowledge identity collapse. Historical cleanup production data repair is recorded separately.
- Specs: `SPEC-20261031-KNOWLEDGE-POINT-PROMPT-03` and `SPEC-20261031-HISTORICAL-KNOWLEDGE-CLEANUP-01`.
- Target: AppID `wx5d2e0014690bf285`; environment `prod-d2g14rwoycac6b45d`; service `flask-ik19`; container port `8000`.
- Release package: frozen deployed-037 source plus only five approved `agent_processing` files. Manifest lists 154 payload files plus the manifest itself; `release-manifest.json` SHA-256 `80278f7c3a218ca27d995f4523809f9208063278d2d7492ec237a1ecc7290b8b`.
- Source revisions: staged `staged-20261031-06`; legacy parity `child-aware-history-agent-20261031-10`.

## Verification before upload

| Gate | Result |
|---|---|
| Current-worktree complete server suite | PASS — 793 passed, 46 skipped |
| Exact frozen package complete server suite | PASS — 793 passed, 46 skipped; an earlier run had one isolated readiness timeout which passed 3/3 in isolation and on the complete rerun |
| Exact package Ruff check / format | PASS |
| Exact package Mypy | PASS — 150 source files; one existing untyped-body note |
| Production Schema strict read-only check | PASS — `20261024_0025` |
| Local image | PASS — UID 10001; live/ready healthy; SIGTERM exit 0 |
| `wxcloud deploy --dryRun` | PASS |

No Schema migration or production database write was performed by this code deployment. The separately approved historical cleanup had already completed after the operator-confirmed backup.

## Cloud result

- Confirmation table was checked for the intended AppID/environment/service, GRAY release, `Dockerfile`, target `.`, port `8000` and unique remark `knowledge-prompt-20261031-spec03-01` before entering `yes`; `--noConfirm` was not used.
- Immutable version: `flask-ik19-038`; created `2026-10-31 11:37:07 +08:00`; reached `normal` at `11:40:08 +08:00`.
- Cloud image digest reported by the build: `sha256:ae264d28cedc70c60f89889abdbe3189c3220de21327bd6b62f903c89d23d180`.
- Service `flask-ik19` is `normal`; PUBLIC access remains closed.
- The CLI repeatedly returned `ResourceNotFound.TopicNotExist` for log subscription and did not exit after the deployment reached `normal`. The local wait was interrupted only after independent `version:list` confirmed `038 normal`; authoritative deployment state is the control-plane query.
- Traffic percentage: NOT_RUN/unknown. CLI 2.3.3 does not expose the version split, and no traffic change was requested or performed. This record does not claim that 038 has served production requests or replaced 037.
- Real AppID `wx.cloud.callContainer` live/ready and business smoke against 038: NOT_RUN because the new version has no confirmed directed traffic and PUBLIC is closed.
- Full cutover: NOT_RUN; remains a release-owner manual gate after directed smoke and metrics review.
- Rollback target: `flask-ik19-037`; Schema remains `20261024_0025` and no destructive downgrade is required.
- Mini Program: no upload, experience, review or formal-release action in this deployment.

Cloud delivery establishes development completion under `GOV-SPEC-20261026-CLOUD-DELIVERY-DONE-01`; it does not change the NOT_RUN acceptance and traffic stages above.

## Later read-only verification and local BUG-036

The above traffic-unknown statement records the deployment-time evidence. The later original30-source evaluation observed038normal/100% and PUBLICclosed through a read-only control-plane query; no traffic change or directed business smoke was performed by that evaluation. See the [original evaluation](../../../dist/knowledge-generation-evaluation-20261031-30/evaluation-30.md). This observation does not retroactively pass the deployment's business-smoke gates.

BUG-036 subsequently implements local `staged-20261031-09` / `child-aware-history-agent-20261031-13` with bounded recovery and stronger rules. Its [current evidence](../../../specs/evidence/EVD-20261031-BUG036-PROMPT09.md) records26/30proposals,12/30content passes and10/30complete passes, remaining failures and no test business writes. It invokes remoteDoubao directly with local new code;038is still the old06/10delivery. No BUG-036 deployment, migration, cutover or client upload is claimed. The Spec remainsVERIFYING/active; future release must run its actual playbook and gates.
