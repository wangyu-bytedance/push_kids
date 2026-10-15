# DOC-002 — 全工程 Markdown 状态与冲突修订（Spec Lite）

- Status: DONE
- Risk: R1
- Owner / Implementer / Reviewer: repository owner / Codex / repository owner
- Date: 2026-10-13
- Spec revision: DOC-SPEC-20261013-02-01
- User confirmation: 产品负责人（用户）于 2026-10-13 回复“删除 旧 Figma 门禁与当前规则冲突”，批准 revision 01 中移除失效 Figma 门禁的限定范围；其他审计事实修订未获批准。
- Approved scope: 仅修订当前治理、模板和 Feature 正文中的失效 Figma 门禁；保留历史审批与原生/真机要求。
- Approved by / Approval date: 产品负责人（用户） / 2026-10-13
- Affected Feature IDs: FEAT-001、002、003、005、006、007、009、010（核对当前文档，不改变产品行为）
- Feature current-state documents: docs/domain/features/；baseline 为本次审计库存中的文件 SHA-256。
- Feature merge owner: Codex

## Scope and acceptance

审计结果见 docs/quality/evidence/MARKDOWN-AUDIT-20261013.md 和 MARKDOWN-INVENTORY-20261013.md。
批准后统一当前治理文档的仓库原生设计门禁，移除当前正文中失效的 Figma 强制要求；历史 Spec/ADR/审批证据保留。
其余 revision 滞后、FEAT-009 当前状态、completed 历史验收口径与候选生命周期问题留在审计报告，需另行批准；不属于本次完成门禁。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: no；不改用户界面。
- Frontend engineering impact: yes；同步治理文本至已批准 GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01，质量预算不降低。
- UI / FDB / FEC / DREV: 复用当前治理来源；无新设计或快照修改。
- Verification: 当前设计政策校验、架构校验、Markdown 链接和生命周期检查；不以这些检查代替原生验收。

## Design views and trade-offs

- Link graph: AGENTS → specs/README + docs/ai → Feature/UI/Architecture → Spec + Evidence + Release。
- Sequence: 盘点 → 比对事实 → 用户批准此 revision → 修订当前正文 → 检查 → 合并状态与引用 → 评估迁移。
- State machine: READY_FOR_REVIEW → APPROVED → IMPLEMENTING → VERIFYING → DONE/completed；未满足验收保留 active。
- Architecture diagram: N/A；无模块、依赖或接口变化。
- Recommended: 定向修订当前规范，历史材料保持可追溯；不采用全仓替换 Figma 或把代码完成一律视为 DONE，以免破坏历史证据及未完成验收。
- Expected files: specs/README.md、docs/ai/*.md、docs/domain/features/*.md、docs/design/frontend/ui/*.md、docs/architecture/ARCHITECTURE.md；按审计证据确定具体变更，迁移时同步引用。

## Required test points and completion gate

1. 当前治理规则与 AGENTS/GOV 不再冲突，历史证据未被重写。
2. 每个修订事实有代码/Spec/证据引用；local 与 release 状态分别记录。
3. 生命周期状态与目录一致，迁移引用可解析。
4. 架构和 current-design-policy 校验实际执行并记录结果。
5. 审计列出的未确定事项保留，不伪造审批/真机/云端证据；完成上述修订后迁移本 Spec。

## Completion evidence — 2026-10-13

- Approved scope complete: specs/README、docs/ai 的三份当前规范、Feature 模板与 FEAT-001/003/005/006/007 正文已同步仓库原生设计证据政策。
- Required test points 1–5: PASS；当前规范残留旧门禁检索无匹配，历史审批/快照未改动；相关 Feature 添加本 Spec 的治理修订引用，其他未确定审计项保留。
- `.venv/bin/python tools/check_architecture.py`: PASS，ARCHITECTURE_VALID checked=3。
- `.venv/bin/python tools/validate_design_evidence.py --check-current-policy`: PASS，DESIGN_EVIDENCE_VALID。
- Markdown 相对链接与 `git diff --check`: 收尾检查见审计报告。
- 业务/原生/真机/云端检查: NOT_RUN，本次仅文档政策同步，无生产代码改动，未声称业务或发布验收通过。
- Lifecycle: 限定批准范围完成，迁移 specs/completed/；其余审计问题需另行批准，不包含在本次 DONE 范围。
