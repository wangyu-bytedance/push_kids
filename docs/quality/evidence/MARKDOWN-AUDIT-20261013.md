# 全工程 Markdown 状态与冲突审计 — 2026-10-13

- Audit type: governance / documentation consistency
- Mode: read-only audit + 用户明确授权的 AGENTS 收尾规则增强
- Auditor: Codex
- Overall health: AMBER
- Remediation update 2026-10-13: MD-001/MD-002 已按用户明确指令关闭；下表保留首次审计问题及证据位置，行号可能因修订变化。其他审计项未执行修订。
- Scope: 排除 .git、.venv、node_modules 与运行缓存的工程 Markdown；逐文件库存见 [完整清单](MARKDOWN-INVENTORY-20261013.md)。全量文本盘点不等于逐条业务行为或云端运行验收。
- 工作区已有其他任务的生产代码、设计脚本、Feature/UI 和发布记录改动；本次保留，不提交、不迁移生产、不修改批准快照。

## 1. 已证实的冲突

| ID | 严重程度 | 证据 | 冲突与处理建议 |
|---|---|---|---|
| MD-001 | MAJOR | specs/README.md Mandatory workflow 8–9 与 Frontend design gate；docs/ai/DEVELOPMENT-PROTOCOL.md:111–114、230、261–263；CODING-CONSTRAINTS.md:277、290；MAINTENANCE-PLAYBOOK.md:35、70、154 | 仍要求 Figma/node/waiver；与 AGENTS、已 DONE 的 GOV-001 及当前 Architecture 仓库原生设计政策冲突。批准 DOC-002 后统一当前规范，保留历史证据。 |
| MD-002 | MAJOR | FEAT-001:384–385；FEAT-005:128–143；FEAT-006:68、83；FEAT-003:134；FEAT-007:49–54 | 当前 Feature 正文把补 Figma 节点列为公开发布门禁；GOV 已取消该依赖。替换为仓库原生设计证据要求；原生三视口/真机门禁继续保留。历史 Change References 中的旧 waiver 不应批量删除。 |
| MD-003 | MINOR | FEAT-001:34、UI-001:35、ARCHITECTURE:7 | revision 仍为 10 月 6 日，而正文已加入 10 月 12–13 日任务/背景/报表内容。当前事实并非全部遗漏，但版本标识不能代表完整正文；确认修订后统一更新并保留变更引用。 |
| MD-004 | MAJOR | specs/active/FEAT-009-WEEKDAY-SPECIFIC-TIMES.md:3、40–50；activities/router.py 与 weekly_slots.py；Feature 目录 | FEAT-009 已有代码和局部测试事实，却无独立 Feature 当前状态文档；Spec 同时记录 Approved Design Revision PENDING 和前端已实现。需补本地事实文档并核查批准范围，补设计审批，不能伪称已验收。 |
| MD-005 | MINOR | completed/FEAT-001-PUSH-KIDS-MVP.md、FEAT-001-PUSH-KIDS-FINAL-SPEC.md、DESIGN-001-HTML-REDESIGN.md；BUG-010 V4 | 历史 completed 使用 COMPLETED、DONE_WITH_EXTERNAL_RELEASE_GATES、STAGE_COMPLETE 和中文状态字段，且文件名含 DRAFT。不能仅靠正则判断为未完成；建议规范顶层生命周期，另列阶段/发布状态，历史验收说明保留。 |
| MD-006 | NEEDS_VERIFICATION | completed/BUG-010-NATIVE-LAYOUT-AND-PARENT-FLOWS.md、BUG-015-REPORT-METRIC-TRENDS.md 等状态注释；active 10 月前端 Spec；AGENTS 原生验收规则 | 历史 DONE 把原生/真机列为独立发布门禁，新 active 则因相同缺口停在 VERIFYING。这是完成口径差异，需逐份按当时批准合同和现行政策确定；不能无证据批量迁移或追溯宣布违规。 |
| MD-007 | MINOR | specs/README.md Purpose 中“FEAT-001 当前实现的最终变更记录”为 FINAL-SPEC；当前 10 月 active Spec | “最终变更记录”表述已过时；该文件是历史基线，当前 Feature/UI 才是现状来源。修订索引说明避免将历史 Spec 当当前实现。 |
| MD-008 | MINOR | DOC-001-DATA-LIFECYCLE-DOCUMENTATION.md、CLOUD-002、BUG-004、FEAT-008 的 READY_FOR_REVIEW；FEAT-002-MULTI-FAMILY 的 DRAFT | 长期未批准候选与当前代码并存，不代表全部可完成或取消。需要 Owner 决定保留、被后续 Spec 替代或拒绝；不能根据日期替用户取消。 |

## 2. 状态与位置检查

审计时已有 active 27 份、completed 50 份、rejected 10 份。active 顶层状态：VERIFYING 17、READY_FOR_REVIEW 6、DRAFT 3、IMPLEMENTING 1。没有 active 明写 DONE/REJECTED 的直接目录错误。库存同时记录中英文状态，避免把中文字段误报为缺失。

- 10 月前端 VERIFYING 多明确缺原生全状态、真机或用户验收，保留 active 有依据；已经上传也不等于满足完成门禁。
- FEAT-009 的 IMPLEMENTING 和未批准设计存在需要核查的范围问题；不自动改为 DONE。
- completed 的非标准历史状态与门禁口径列为复核项，不擅自迁移历史记录。
- rejected 的取消/拒绝理由应保留；未发现仅因目录位置就需要恢复实施的证据。
- 本次新增 DOC-002 是 READY_FOR_REVIEW，留 active 正确；这是待批准修订，不代表已实施所有文档纠正。

## 3. 代码与当前文档抽查

| 当前事实 | 代码/文档证据 | 结论 |
|---|---|---|
| 每日任务已本地接入 | bootstrap/app.py daily_tasks 路由；ARCHITECTURE 模块表；BHV-035；FEAT-010；FEAT-001 与 UI-001 增量 | 基本同步，明确尚待 MySQL/完整真机与发布验收；revision 滞后另见 MD-003。 |
| 身份与家庭边界 | platform/context.py request_context/self_service_context；Architecture:72、274；FEAT-001:143 | 云端 actor 绑定与本地 X-Family-ID 分别记录；AGENTS 的 MVP 描述应结合这些模式阅读，不能推断云端仍信任客户端 family。 |
| 报表/计划面板 | 当前生产文件 diff、FEAT-001 首段、REPORT-PANELS Spec 和证据 | 文档记录本地实现，发布候选尚待冻结；历史测试结果不作为本审计新执行结果。 |
| 发布状态 | 20261013-fullstack-diff.md 首段 PREPARING/NOT_DEPLOYED，末段用户补充授权与下一步 | 报告中旧“待决定纳入报表”与末段“已授权纳入”并存，过程信息应归一为当前决定。授权上传不等于已上传或正式发布；线上源码/Schema 仍未证实。 |

## 4. 检查与证据边界

| 检查 | 本次结果 |
|---|---|
| 全量 Markdown 文本读取、分类、SHA-256、顶层状态与 Markdown 本地链接检查 | 已执行；清单包含全部工程文件；相对 Markdown 链接未发现缺失目标。代码块反引号中的路径、锚点和外部 URL 不在该链接检查的保证范围。 |
| uv run python tools/check_architecture.py | 未成功启动：uv 缓存目录 sandbox 权限不足。 |
| uv run python tools/validate_design_evidence.py --check-current-policy | 未成功启动：同上。 |
| .venv/bin/python tools/check_architecture.py | PASS：ARCHITECTURE_VALID checked=3。 |
| .venv/bin/python tools/validate_design_evidence.py --check-current-policy | PASS：DESIGN_EVIDENCE_VALID。只证明该工具覆盖的政策/证据结构，不证明所有治理正文、原生或真机验收通过。 |
| 业务测试 / Ruff / MyPy / 微信原生验收 / 云端检查 | NOT_RUN：本次仅文档审计与指令增强，无生产代码修改；现有其他任务的检查报告保持历史证据性质。 |

## 5. 已执行与待批准动作

已按用户明确要求修改 AGENTS.md，新增每次代码修改后的文档正文/状态/revision/迁移/引用/代码冲突核对与完成回复要求。

用户随后明确要求“删除 旧 Figma 门禁与当前规则冲突”，批准 [DOC-002 revision 01](../../../specs/completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md) 中的限定门禁修订。已同步 specs/README、docs/ai 三份规范、Feature 模板与 FEAT-001/003/005/006/007 当前正文；MD-001/002 关闭。原生/真机要求和历史审批保留，业务实现/发布状态不变。DOC-002 限定范围完成，设为 DONE 并迁移 completed；其他事实纠正仍需另行批准。

本次修订再次执行架构和 current-design-policy 校验均 PASS；全工程相对 Markdown 链接、Spec 迁移位置与 `git diff --check` 均 PASS；当前 specs/README、docs/ai、Feature 模板的 Figma/FIGMA/figma/node-specific 检索无匹配。全量库存同步为修订后的内容指纹，不改批准快照。业务/原生/云端测试 NOT_RUN，原因是仅改文档政策。
