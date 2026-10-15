# DOC-003 — 以当前代码校正工程文档（Spec Lite）

- Status: READY_FOR_REVIEW
- Risk: R1；仅文档事实修正，不修改业务代码、测试、数据或部署。
- Owner / Implementer / Reviewer: 产品负责人（用户） / Codex / 产品负责人（用户）
- Date: 2026-10-13
- Spec revision: `DOC-SPEC-20261013-03-01`
- User confirmation: pending；请求消息“以当前代码为准，修改错误的docs”确定工作目标，具体修订范围如下，按 AGENTS Requirement workflow 第3条待确认。
- Affected Feature IDs: FEAT-001、002、003、005、006、007、009、010；无已实现代码的候选功能不得写成已实现。
- Feature current-state documents: `docs/domain/features/`；当前基线为文件实际内容与 git HEAD `ca41351`，保留已有文档工作区变更。
- Feature merge owner: Codex

## 1. Problem and outcome

工程当前文档存在旧实现描述、漏记能力、旧 revision 与发布状态矛盾。以当前工作区生产代码证明本地行为/接口/架构，以已有可追溯发布与验收记录证明外部状态；不通过改文档批准现有代码的审批缺口。

已确认的更正点：

| 文档 | 错误/缺口 | 权威证据与目标 |
|---|---|---|
| README.md | 必做/可选分组、后台首次建档、最终交付 Spec 作为本轮来源，遗漏每日任务/逐日时段 | planning/selection.py、children/families 路由、原生设置/建档页面；改为实际当前流程，历史最终 Spec 仅为历史基线。 |
| ARCHITECTURE.md | revision 滞后；当前选择描述仍按 due/最久/ID，旧 head 与新 head 在当前正文并存 | planning/selection.py 的 daily-plan-fair-v2、公平选择和预算；platform/database.py 与 migrations；当前正文唯一表达现状，旧批准引用归历史。 |
| FEAT-001、UI-001、FEAT-010 | 当前段落未上传与0.1.14上传并存，元数据旧版本，Tab 职责漏每日任务 | 当前 pages/components、发布记录20261013 §8；区分开发上传、后端未部署、体验/正式与验收。 |
| FEAT-007、UI-017 | 出行仍只有统一开始/结束时间，漏逐日 time_slots | travel/schemas.py、activities/weekly_slots.py、settings/index.js；记录统一/逐日、0–6星期、单日单段、同日结束晚于开始及兼容能力合同。 |
| FEAT-009 当前状态缺失 | 有代码无独立当前事实文档 | activities/travel schema/router/service、settings 状态；新增本地状态文档，保留 Spec 中设计审批 PENDING 与原生/真机未验收，不冒称功能已批准完成。 |
| specs/README.md | “当前最终变更记录”指向旧最终 Spec | 改为 Feature/UI 当前入口，旧 Spec 保留为历史基线。 |
| 20261013-fullstack-diff.md | 首段不上传/未纳入报表、下一步重新询问纳入/修复Ruff/上传，与已记录提交和上传结果矛盾 | 本报告自身§5/6/8与314150f/898aa4b/ca41351；合并为已执行事实及剩余后端门禁，不重跑发布操作。 |
| 审计报告/清单 | 初始审计问题与后续修复、上传、归档状态混杂 | 更新明确的关闭/保留结论和内容指纹，保留首次审计证据。 |

## 2. Scope and non-goals

读取全部当前文档，对照其所指生产模块核对事实；修正能被代码或实际证据证明的错误，补齐缺失当前状态。历史 Spec/ADR/release 记录保留当时事实，仅修复错误引用或显式区分历史与当前。不能仅因代码实现就批量宣布 DONE、取消候选、补造审批、重写已批准设计 manifest、改变强制工程规则来迎合代码。未经证实的云端状态标为 unknown/pending。

## 3. Frontend Design Impact and Repository-native Approval

- Frontend impact / engineering impact: no / no；仅记录已有实现与证据，不修改界面、工具链、质量预算或审批合同。
- UI IDs: UI-001、009、010、011、014、015、016、017，按实际事实差异选择修订。
- FDB / FEC / DREV / new exports: N/A；本任务无新设计，不为原有审批缺口补造批准。

## 4. Design views and trade-offs

- Link/call graph: 当前文档 → 所引用生产代码/测试 → 实际实现事实；发布记录/审批/验收证据 → 外部状态；两类事实 → Feature/UI/Architecture/Behavior → 索引/Spec。
- Sequence diagram: N/A；无应用调用顺序变化。修订工作顺序为读代码 → 标定冲突 → 确认本revision → 修正文档 → 检查 → 记录证据 → 归档。
- State machine: READY_FOR_REVIEW → APPROVED → IMPLEMENTING → VERIFYING → DONE/completed；不能证实的事实保留明确未知项。
- Architecture diagram: N/A；无模块边界、依赖或扩展点变化。
- Trade-off: 定向重写当前正文并保留历史引用，避免全仓词语替换破坏历史事实；源码只证明实现，不证明生产部署和设备验收。

## 5. Expected file changes

- modify: README.md、specs/README.md、docs/architecture/ARCHITECTURE.md、docs/domain/BEHAVIOR-CATALOG.md、受影响Feature/UI当前文档、20261013-fullstack-diff.md、Markdown审计报告和清单。
- add: docs/domain/features/FEAT-009-weekday-specific-times.md、本任务验证记录（可合并审计报告）。
- move: 仅本 Spec 在自身完成门禁通过后迁移 completed；其他任务按实际批准验收证据判断，不自动迁移。
- retain: 历史审批、Spec、ADR、设计源文件/导出/hash、其他用户改动、所有生产代码。

## 6. Acceptance and required test points

| Test point | Required result |
|---|---|
| TP-001 当前事实核对 | 每处修改有生产文件/函数或发布证据引用；旧正文冲突被替换，历史明确标记。 |
| TP-002 状态可信度 | local/自动化/原生/真机/开发上传/体验/审核/正式区分；未验证不得声称通过，其他Spec审批缺口保留。 |
| TP-003 文档完整性 | 相对Markdown链接有效；修订编号、Feature/Behavior/UI与索引一致；无过期当前重复正文。 |
| TP-004 架构/设计政策 | `.venv/bin/python tools/check_architecture.py` 与 `tools/validate_design_evidence.py --check-current-policy` 实际运行并记录。 |
| TP-005 范围与生命周期 | `git diff --check`；无本任务生产代码或批准快照修改；本Spec完成后DONE并迁移，清单刷新。 |

业务测试、云端、原生和真机检查不作为本纯文档任务必跑项；如引用历史结果须写明证据来源和范围，不声称本次执行。审批后的事实核对若暴露代码缺陷，只记录，不改代码或放宽验收。

## 7. Verification and completion

- Verification: NOT_RUN；目前仅完成读取与范围准备，尚未执行文档事实修订。
- Completion gate: 上述TP全部记录结果、当前文档合并并引用本Spec、diff审查、迁移与引用修复。
