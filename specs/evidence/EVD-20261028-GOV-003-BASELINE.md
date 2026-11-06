---
created: "2026-10-28"
updated: "2026-10-28"
type: evidence
status: recorded
owner: Codex
---

# EVD-20261028-GOV-003 — 增量治理合并与保护验证

- Evidence ID: EVD-20261028-GOV-003-BASELINE
- Requirement: [GOV-003 Spec01](../completed/GOV-003-TDD-CODING-REVIEW-INCREMENTAL-MERGE.md)，TP-001..006。
- spec_revision: GOV-SPEC-20261028-TDD-CODING-REVIEW-MERGE-01
- subject_revision: UNCOMMITTED+base0576ac30464908154c624effed41df6dfa3110cc+policy-sha256:30923ae7c39cf0949c99276081294e4602d2477909dd51a12ecb0958151c738c
- 方法/命令: 本文命令表的实际执行、原始SHA清单对照、局部diff/文档自复核及最终339处本地链接、127份Spec索引/归档和16文件对象摘要核对。
- result: passed
- Owner: Codex；人工批准人为产品负责人（用户），2026-10-28“批准Spec01，按方案合并”。

## 范围、环境和对象绑定

Python3.12.11、Nodev22.22.0、uv0.9.18，本机现有依赖，日期按Asia/Shanghai。
未同步/安装新依赖；uv命令均设`UV_CACHE_DIR=/tmp/push-kids-skill-uv-cache`并用
`--offline --no-sync`。开始时已有182项dirty状态，未reset/stash/提交/推送。

本证据只说明批准范围内的治理就绪、保护检查与本地既有门禁结果。它不验证新产品
行为、真实TDD收益、审查器召回/误报、设备或云端交付。最后结果只对下表16份规则/
索引内容有效，Spec状态记录与本EVD不参与该hash，避免自引用；它们另查批准、结果
和链接/索引一致性。16文件改变时对此新版本须重新验证，不能追改旧版本绑定。

摘要算法：按仓库相对路径排序，对每个文件拼接`path + NUL + sha256 + LF`，再取
UTF-8字节SHA-256。完整未提交对象包含这些新增文件，不是仅取git diff。

| 规则/索引文件 | SHA-256 |
|---|---|
| `AGENTS.md` | d3c253a41ba14b8ef2760db8dc030c645c45cedd68aba85f8c9cd3103b4edfe6 |
| `REVIEW.md` | 90f4fbbf4841d98976adb3edc6b36781fa991a7ac450a8a5d8d1fe929ce6d7c6 |
| `docs/ai/CODING-CONSTRAINTS.md` | 68c1af282c70882f264a6cd126098b05a462288683b7bd45506bd00665b154d4 |
| `docs/ai/DEVELOPMENT-PROTOCOL.md` | 7e4bd884e066956dd60a9f2d34ae3821e952016b9bb5002b3e5fa02c9e53f47a |
| `docs/ai/MAINTENANCE-PLAYBOOK.md` | a4021155af1096b18db62000b1c9f52c11a632aae1e416c33aa25c245834cc54 |
| `docs/architecture/ARCHITECTURE-CONSTRAINTS.md` | 6867c3be669fe15cb2ad40781bff1a7b2134b31a834dce248910bc5799c23c79 |
| `docs/quality/TEST-STRATEGY.md` | a8484ff292dc7f7b910bd6f76acd5bd770a94b4e2828b62c4bb4b723a0938273 |
| `docs/quality/issues/DOC-AMBIGUITY-TEMPLATE.md` | 96a7f13f6e243f1bfcab5466926ea5275f3e60b3404f99adb716a165e779a38c |
| `docs/quality/issues/ISSUE-TEMPLATE.md` | 5e5aeee23ade040a35bb8c8cef9f11436191255863a8e967f6206feb9a2c5973 |
| `docs/quality/issues/README.md` | 5d061cf3a1196e046c2882d995dc8ffdb51a1990554f048e65004b5118cb1e9e |
| `docs/quality/regressions/README.md` | b22b92882abe62b2bcbff646f22ff6c0a5c87572960d03b3ac906d085c4c4ee8 |
| `docs/quality/regressions/REGRESSION-TEMPLATE.md` | 5371014e845576342f36f39ca16efc3b9fb883152f6cf4c2c10c76733cb7f2b8 |
| `specs/README.md` | bc12bd6ce274af7bcba6a6fa5b483d4cc52e2360a89b747cf7024e0bdde70add |
| `specs/STATUS.md` | 2e6c11155fe09e6e7add574a9711bbf825a670715f1d052b6571b2b07a19ccf2 |
| `specs/_templates/REVIEW-REPORT.md` | 09c57318bb7612655a2cd191d573303ac827350b44537d7f0b905fd53765b548 |
| `specs/evidence/EVIDENCE-TEMPLATE.md` | 7339c54affa08c2808a89a2fa390353e281ca93aa7dcb5635655fdd07e0774dd |

## 实际命令和结果

| TP / command | 合并前 | 合并后实际结果与限制 |
|---|---|---|
| TP-001 / 原有4584文件逐项SHA对照，只允许9份既有治理/索引文件变化 | 已冻结完整清单 | PASS：最终4575份保护文件无变，原有文件删除0；133份Spec/模板、1959份前端设计文件保持；新增9文档及修改9文档精确符合范围；原先已删除路径无恢复 |
| TP-002 / 局部diff和Skill逐项人工对照 | Gate E先改实现后写测试 | 已替换旧顺序；Red/Baseline、必要Refactor、恢复/前提检查及规则Owner齐备；ARC-014/015保持，新增017/018 |
| TP-003 / 前端Review章节逐字比较及规则/模板自复核 | 原章节存在 | PASS：原章节字节相同；现有五维、FEC、微信平台/读取/发布规则保持；原云交付规则原句相同；339处本地链接无缺失 |
| TP-004 / `uv run --offline --no-sync python tools/check_architecture.py` | PASS | PASS：4 policies / 150 modules，runtime/lazy DAG |
| TP-004 / `uv run --offline --no-sync python tools/validate_design_evidence.py --check-current-policy` | PASS | PASS：DESIGN_EVIDENCE_VALID |
| TP-004 / `uv run --offline --no-sync python tools/validate_miniprogram.py` | PASS | PASS：17 pages / 1234867 source bytes |
| TP-004 / `npm test` | 349 PASS | 349 passed / 0 failed / 0 skipped；合并后实际重跑 |
| TP-005 / `git diff --check`及归档/对象核对 | PASS | PASS；归档后103 completed / 11 active / 13 rejected合计127份均在索引，无旧active副本，16规则/索引文件hash与绑定对象一致 |
| TP-005 / Skill `validate_ai_native.py . --format json` | FAIL：174 ERROR / 101 WARN | FAIL：165 ERROR / 98 WARN；按level/code/path/message集合比较新增0、消除12；不报告全仓通过 |
| TP-006 / 工具/接入状态、阶段/效果语义审查 | 未有真实任务试用 | 新质量工具/CRAP/定量重复/变异/reviewer回放及CI/定时均未由本次接入；没有编造运行/覆盖/收益 |

完整原始输出留在受控临时位置：
`/tmp/push-kids-skill-20261028-baseline.json`、
`/tmp/push-kids-skill-20261028-validation-baseline.json`、
`/tmp/push-kids-gov003-validation-after.json`、
`/tmp/push-kids-gov003-after-frontend-tests.log`及
`/tmp/push-kids-gov003-policy-snapshot.json`。临时产物可能清理，核心结果/对象摘要
已写入本证据；不将临时日志可用性当作长期可重放保证。

保护集摘要为`62f78688795d98d3fadf4fafbe3ce4c9d97026d78655dcab12f90c4356adb5d6`，
使用同一排序算法；集合为开始时4584个存在文件减去本轮允许修改的9文件。
当前版本可从Git列出的存在文件中排除本轮全部18个变更/新增文档重算4575集合。

## R1文档自复核和逐文件必要性

这是同一上下文R1自复核，不冒称独立Reviewer；未来R2/R3规则仍要求独立上下文。
确认过的一处位置文字问题：REVIEW敏感路径表的笼统`migrations/`改为实际
`apps/api/migrations/`，已用仓库文件列表核对；无未解决的本次范围内确认缺陷。

| 文件 | 动作/主要变化 | 必要性/理由 | 位置/冗余 |
|---|---|---|---|
| AGENTS | modify；加载协议/编码/Review/ISS/REG入口 | necessary；新会话能发现规则 | correct；细则留权威文档 |
| DEVELOPMENT-PROTOCOL | modify；替换Gate E、Review/前提/交接流程 | necessary；去除相反顺序，执行新规则 | correct；保留前端/云交付正文 |
| CODING-CONSTRAINTS | modify；Work/Right/Practice、单决策、类型/根因 | necessary；落实编码要求 | correct；TDD流程引用协议 |
| MAINTENANCE-PLAYBOOK | modify；工作区保护与ISS/REG观察 | necessary；闭环及知识保存 | correct；无周期任务创建 |
| ARCHITECTURE-CONSTRAINTS | modify；017/018及008中断恢复 | necessary；状态/边界可测试要求 | correct；无改生产边界或新编号冲突 |
| TEST-STRATEGY | modify；行为证据、工具状态/预算及试用 | necessary；避免虚报工具和质量收益 | correct；既有专项逐行保留 |
| REVIEW | add；项目失效定义/敏感范围/七类核对/收敛 | necessary；缺少仓库审查入口 | correct；不是第二份任务报告 |
| REVIEW-REPORT模板 | modify；文档表/稳定ID/阶段证据 | necessary；审查有实际输出载体 | correct；前端章节和原清单完整保留 |
| issues/README | add；检索/生命周期/关闭约束 | necessary；模板接入流程 | correct；链接既有事实源 |
| ISSUE-TEMPLATE | add；根因/漏检/回归/关闭字段 | necessary；人工/AI问题记录格式 | correct；无伪造历史实例 |
| DOC-AMBIGUITY-TEMPLATE | add；旧新来源/方案/答复/应用/复验 | necessary；裁决可评审可追溯 | correct；复用同一ISS |
| regressions/README | add；行为/审查器契约及活跃条件 | necessary；明确何时算回归覆盖 | correct；无测试搬迁 |
| REGRESSION-TEMPLATE | add；版本/实际命令/正负例及证据 | necessary；可重放契约 | correct；未建虚假active案例 |
| EVIDENCE-TEMPLATE | add；Spec/对象/阶段/结果绑定 | necessary；新证据版本规则 | correct；历史证据原位引用 |
| specs/README | modify；治理入口和当前数量 | necessary；新任务可发现 | correct；只更新本轮索引 |
| specs/STATUS | modify；增加GOV-003及当前计数 | necessary；归档索引一致 | correct；旧结果明确为历史 |
| GOV-003 Spec | add/move；批准、范围、结果和DONE归档 | necessary；已批任务闭环 | correct；仅移动本任务Spec |
| 本EVD | add；对象、实际结果和自复核 | necessary；保留证据/缺口 | correct；不新建平行发布台账 |

必要文件为上表全部18个；questionable/unnecessary/misplaced均无确认项；
无生产代码删除/回退建议。可删除的只是本轮临时日志/工作材料，仍按引用和清理
授权核对，不主动删除。正确性结论仅限规则/文档保护及实际检查，不覆盖产品收益。

## 受影响文档联合核对

| 文档/范围 | 本次核对的契约及证据 | 结论/动作 |
|---|---|---|
| AGENTS、开发/编码/维护协议 | 新入口、阶段顺序、两次前提失败、权限/交付口径；局部diff与Spec01 | aligned；冲突旧流程已替换 |
| 架构约束 | 008恢复、017/018状态模型；原014/015/016及维护性条款保持 | aligned；无运行架构改动，Architecture正文不改 |
| TEST-STRATEGY、Review规则/模板、ISS/REG/EVD | 真实命令/未配置、逐文件/文档表、版本和关闭条件 | aligned；不宣称平台门禁已接入 |
| Feature索引、Behavior/Architecture、UI/FDB/FEC及设计源/快照 | 本次无产品diff，相关现有约束保留；保护SHA和设计/架构检查 | aligned于“本次合同未变”；不重新证明所有历史实现/验收 |
| 发布README及GOV-002 | 本次无发布；开发DONE、验收、上传/体验/审核/正式发布仍分开 | aligned；不改发布文档或批准历史 |
| 原有任务Spec | SHA保护、状态和存放位置保持 | aligned于无改写承诺；历史内容缺口未验证/未修复 |
| Spec目录/本任务/EVD引用 | 本任务DONE、127份完整索引、339处本地链接、16文件对象hash核对 | aligned；归档后无缺失/新增校验发现 |

未发现本范围需要额外人工裁决的语义歧义；已有完成规则以用户GOV-002和本次
明确Spec01批准为据，没有推定或追认产品/设计批准。新读者可从AGENTS进入协议、
规则、真实命令和模板，理解如何实施及如何审查；产品当前事实继续从Feature/UI读。

## 剩余缺口和未执行项

- 通用validator仍失败：164条TASK_SPEC_FEATURE_LINK、98条COMPLETED_SPEC_FEATURE_MERGE
  警告及1条REQUIRED_DIR（`specs/deliveries`）；项目沿用现有开发/验收/发布状态索引，
  Spec01明确不新增DLV平行台账，也不改历史Spec凑绿。Owner为项目维护者，后续若做
  历史治理需单独Spec及复核原批准；本次只能报告无新增，不能声称全仓AI Native通过。
- 编码切片：N/A；本次只有文档，不制造Red或产品改动。真实TDD/Review效果NOT_RUN，
  后续已批准任务采集阶段/发现/误报/轮数/投入和发布后结果，当前无足够样本。
- 后端全套、实库MySQL、Ark、容器/原生/真机、云端/上传：NOT_RUN，本次无对应变更；
  历史通过不冒充本轮执行。没有额外授权或人工门禁等待。

最终结论：TP-001..006在本轮声明的治理范围内通过，开发DONE已归档；passed不覆盖
全仓通用validator、真实TDD/Review效果或产品验收。规范内容以后变化时另建新EVD，
保留本运行和失败基线；不修改本对象版本去追认后续改动。
