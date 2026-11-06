---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: verified
owner: "Product owner / Codex"
---

# System One辅助验收 — 当前版本实测与本地验证

- Evidence ID: EVD-20261105-BUG036-SYSTEMONE06
- Requirement / acceptance: [Spec06](../completed/BUG-036-SYSTEM-ONE-ACCEPTANCE.md)，TP01–TP11。
- spec_revision: `BUG-SPEC-20261105-SYSTEM-ONE-06 / ARCH-20261105-SYSTEM-ONE-06`
- subject_revision: candidate02，156生产文件manifest SHA `349320d7078dbb059386cf3975b1f4c7bd3b6f56efd852fa3bf34f79d470883c`；唯一最终格式修正保持AST逐文件相同，见下文。
- result: passed
- Evidence scope: 本地流程/产物保持与本轮生成率目标；检查器命名漏检、家长内容PENDING及原生/云缺项独立保留，不代表完整质量或发布验收通过。
- 方法/命令：`uv run python /private/tmp/push-kids-systemone06-20261105/paired_generation_final.py`；验收既有产物另运行replay_acceptance.py；自动测试见下表。
- 环境：macOS arm64、本地Python3.12.11/uv、SQLite测试；真实Ark只读材料调用。未改生产配置/数据库、未创建真实Job/草稿/缓存/正式事实，未Git提交/推送或部署。

安全工件：[最终源码/测试manifest](bug036-systemone06-20261105/source-manifest.json)、[本轮18路径变更](bug036-systemone06-20261105/change-manifest.json)、[最终代码zip](bug036-systemone06-20261105/final-source.zip)、[生成冻结口径](bug036-systemone06-20261105/generation-freeze-manifest.json)、[回放脚本](bug036-systemone06-20261105/replay-harness.zip)。最终代码zip SHA `32d2e0f6088e3ebbe8df5eef2f3aaf0a49e88106b3d220cd36540766b592a42d`，源码manifest SHA `d2212bad7224cf78ae24d8050f085b684425542843739e81cda0b0cb70d969e3`。不含环境文件、凭据、原材料或模型原始响应。

## 当前版本和冻结口径

原Pro `staged-20261101-13 / child-aware-history-agent-20261101-16`保持，Lite只作辅助验收。打开/关闭验收均从同一冻结目录导入156源文件，在同一进程交替启动两分支，共用原2请求槽。15份可用材料×3轮×2分支＝90次，每Job上限3attempt，只按既有failure disposition重试，原18缓存键/64KiB单键/512KiB总量、20工具/100历史项和270秒attempt上限保持。不修改预标标准，不增加重试或通过省略条目制造成功率。

每attempt单列generation_succeeded、acceptance_started、acceptance_returned、facts_preserved、failure_phase；有效生成后因验收丢产物另计。最终产出、首轮成功、验收返回/意见、耗时及人工内容质量分开。3份已取消提交原图404单列材料不可执行，不进入本次15材料的生成分母，也不被宣称为恢复成功。

真实回放使用此前已授权只读获取的材料和family/child/as-of过滤历史。历史证据为当前未版本化快照，历史Todo与精确重复材料上下文不可重建，没有伪造；实际Worker接线、重复材料/人工确认/事务与迟到保护由集成测试分别验证。该小样本三轮不等于独立45份材料，不宣称统计非劣效或线上成功率。

耗时为此只读回放内的Pro生成、同进程排队、实际attempt和验收墙钟时间；图片先已下载，不计生产Job队列、材料远程下载或attempt之间available_at等待间隔，不能当作线上从提交到草稿的用户延迟。

私有原始材料/输出仅存`/private/tmp/push-kids-systemone06-20261105`及既有私有来源目录，目录mode700；仓库只保存脱敏数值、源/脚本/材料指纹和测试证据。面向用户仅提供生成结果与核对意见，无原始输入或图片。

candidate02冻结后Ruff发现一个101字符行。最终将一个f-string分为相邻的两个f-string；AST dump对156文件逐项相同，无运行语义或提示文本变化。冻结验收模块SHA `bb55797bc71563b5d8b5dbe94f57b3ae4874379315dc729c2b8c278d7ef3c40b`，最终SHA `33b037292c828e5b8bf3f4ba82b63f59806e39d1b632b0281edbb69427b4ce5d`；不重写冻结manifest或冒称两字节源完全相同。最终测试绑定工作树，真实回放绑定冻结candidate02及机械等价证据。

## Red / Green、首败与中止记录

| 阶段/记录 | 实际结果和解释 |
|---|---|
| red-worker.txt | 旧Worker三种验收结果均未调用checker，3个诚实行为FAIL；不是语法/依赖失败。 |
| green-worker.txt | 初始接线与原Worker/分阶段专项88PASS；不覆盖随后新增事务边界测试。 |
| 集成文件同名collection ERROR、初次mypy | 单元/集成都叫test_proposal_acceptance.py导致收集失败，后者改为test_worker_acceptance.py；补 evidence 列表类型。不是行为Red。 |
| focused-final / transaction-fix-green | 事务事件与取消/lease/deleting三项真实FAIL；rollback过期ORM访问隐式开读事务。第一次只替换scope/checkpoint遗漏Runner参数，仍三项FAIL；核对共同前提后完整替换五处标量访问。 |
| transaction-fix-green02.txt | 52PASS，事务与迟到保护修复。 |
| worker-final.txt | 新手工确认测试编辑插入位置错误NameError，1FAIL/6PASS；修复测试组织，不算产品Red或隐藏故障。 |
| focused-final03.txt | 64PASS，包含阈值/家庭/attempt/耗尽租约/手工确认及实际归档。 |
| red-target-hints.txt | 同目标多标准未汇聚，四目标低分退化为通用提示，真实FAIL。修复按目标合并，内部findings保留。 |
| red-response.txt | 原HTTP全量缓冲超大响应后才validation，预期容量拒绝测试真实FAIL。修复64KiB流式停止。 |
| focused-final04.txt | 77PASS，包含以上全部新增边界。 |
| [最终REG](bug036-systemone06-20261105/reg-final.txt) | 89PASS/13.55秒，绑定工作树格式修正后的当前源，含旧覆盖/迁移兼容和Worker相邻回归。 |
| paired01 | harness局部变量round覆盖内置函数，首个LLM已调用后记录抛TypeError，无可用完整指标；保留错误日志，不计最终分母。 |
| paired02 | candidate01试跑因事务边界缺陷发现后主动中止，STOPPED状态及所有部分行保留，不选择性复用成功结果。 |
| paired03 | 独立新目录、最终candidate02完整90次，COMPLETED 90；开启43/45、关闭42/45，无harness错误，所有失败和attempt保留。 |

## 自动检查与独立Review

| 命令/范围 | 当前结果 |
|---|---|
| `uv run pytest tests/unit tests/integration tests/contract -q` 首轮02 | 961PASS/56SKIP/1FAIL，SDK运输字节测试3秒local_deadline；单项重跑1PASS。保留首败，不当稳定PASS。 |
| 同全量03（新增边界后） | 985PASS/56SKIP/1FAIL，同SDK测试deadline；只跑该文件25PASS，字节测试2.15秒。不改变超时或删除测试。 |
| 同全量04（最终工作树） | 988PASS/56SKIP，322.09秒；既有128项deprecation warnings。此前两次SDK deadline失败仍保留，单次通过不证明该3秒测试时间稳定。 |
| `uv run ruff check .` / `uv run ruff format --check .` | 最终03 PASS / 956 files formatted；02的E501首败保留，唯一码行格式修正AST相同。 |
| `uv run mypy apps/api/src` | 最终03 PASS，156 files；既有未类型化函数注解note保留。 |
| `npm test` | 359PASS/0FAIL；无前端源码变更，不能替代原生/设备。 |
| `tools/check_architecture.py` | 最终02 ARCHITECTURE_VALID，5 policies/156 modules，runtime/lazy DAG。 |
| `tools/validate_design_evidence.py --check-current-policy` | DESIGN_EVIDENCE_VALID，无新设计/前端实现。 |
| `tools/validate_miniprogram.py` | MINIPROGRAM_VALID，17 pages/1,244,228 bytes；不代表原生交互验收。 |
| 隔离MySQL5.7旧覆盖/迁移/缓存事务 | MySQL5.7.44升级head成功，`tests/integration/test_system_one_mysql.py tests/integration/test_staged_mysql.py` 12PASS/27.09秒；utf8mb4独占容器已删除，0生产访问。与默认56条件SKIP分开，其余MySQL仍未跑，不冒充全MySQL通过。 |
| 原生/真机新动态提示兼容TP11 | NOT_RUN；无前端源码/布局变化，本轮未启动原生合成页面。公开API可读、编辑及确认由Worker/learning集成验证；不以Node/static代验。 |
| 独立只读代码/文档Review | candidate02及最终AST等价格式修正PASS，0未解决已确认代码/文档问题；独立59PASS/3.30秒，第三轮文档复核PASS。未独立跑全量/MySQL/原生/真实模型。整理报告见[独立Review](REVIEW-20261105-BUG036-SYSTEMONE06.md)。另一次collect-only在SDK导入文件读取阶段主动中止130，未执行测试，无通过/失败声明。 |

独立Reviewer先按REVIEW/`code-review` Skill读取批准稿与基线，再复核生产/测试18项diff；156冻结源与工作树逐项核对（格式修正前），规范化18路径audit SHA `981ca0dff4bf60ccded9b54804ae4fa365857da667b31d060c3bd3f757e428ee`。三条稳定finding：R2-CR-001事务边界MAJOR，R2-CR-002归档术语MINOR，R2-CR-003同目标合并MINOR；前后代码、测试与根因分别见三个ISS及当前[REG](../../docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md)。最终文档与真实90/58回放数字复核均在第三轮完成。

第三轮最终文档增量复核：Reviewer独立验证156文件AST相同、唯一f-string拆行且最终SHA正确；核对21个Markdown路径变化（含Spec05移入/移出）、全部相对Markdown目标存在，目录12/109/19与索引一致。D-01残留旧05启闭分支措辞、缓存ISS元数据/README的Review状态已修正；D-02 REG阈值勘误明确source/scope/summary/coverage为0.95，subject/granularity/action/separate为0.90。另明确退役的仅为Spec05覆盖版本字段新生产者，原Pro legacy coverage路径保持。均只修复事实表述，不改代码、阈值或批准范围；最终90/58数字已逐项独立重算，与私有来源/安全工件全等，未发现数值偏差或新问题，没有启动第四轮全面审查。

| 本轮生产/测试路径（相对apps/api/src/push_kids，测试为仓库相对） | 动作 | 独立审查必要性/放置结论 |
|---|---|---|
| agent_processing/context.py | modify | necessary/correct，移除退役时间上下文 |
| agent_processing/contracts.py | modify | necessary/correct，恢复100历史上限，旧覆盖版本只读兼容 |
| agent_processing/decision_contracts.py | modify | necessary/correct，保留答案校验，删除退役DTO |
| agent_processing/decision_workflow.py | delete | necessary/correct，删除第二条生成权威路径 |
| agent_processing/history_search.py | modify | necessary/correct，清退近期池查询，保留原有界搜索 |
| agent_processing/pipeline.py | modify | necessary/correct，原Pro生成，保留uncertain缓存修复 |
| agent_processing/proposal_acceptance.py | add | necessary/correct，固定验收/静态提示/降级，无正式副作用 |
| agent_processing/runner.py | modify | necessary/correct，移除分类/近期池注入 |
| agent_processing/stage_provider.py | modify | necessary/correct，只暴露验收能力，不改Pro指纹 |
| agent_processing/system_one_provider.py | modify | necessary/correct，64KiB流式预算和释放 |
| agent_processing/worker.py | modify | necessary/correct，事务外外呼及原子写回/迟到保护 |
| platform/config.py | modify | necessary/correct，按批准Spec默认开启辅助验收 |
| tests/integration/test_system_one_history.py | delete | necessary/correct，仅覆盖退役路径 |
| tests/integration/test_system_one_mysql.py | modify | necessary/correct，删近期池测试，保留迁移/旧确认 |
| tests/integration/test_worker_acceptance.py | add | necessary/correct，真实Worker、人工及事务竞争 |
| tests/unit/test_proposal_acceptance.py | add | necessary/correct，事实/阈值/降级/合并与预算 |
| tests/unit/test_system_one_provider.py | modify | necessary/correct，协议、流式截流、两槽与开关 |
| tests/unit/test_system_one_workflow.py | modify | necessary/correct，原Pro路由和缓存回归 |

没有不必要、放置错误或另可安全删除的本轮文件。未触碰learning旧确认分支、迁移0027或并行工作日前端。文档变化均为受影响事实层/Spec/ISS/REG与发布边界；历史冻结证据不重写。Reviewer未修改文件、没有授予发布/合并权限。

## 真实回放与人工内容验收

TP07旧43份＋已知命名问题3份＋原标合成12份使用实际新accept_proposal完成58次，均在90次生成之后运行，0 Pro调用/0业务写入。58/58返回、58/58学习事实保留，无unavailable/skipped。旧43份为35未报问题/8建议核对，43/43全部保留；不能当作当前43/45生成率或内容合格率。

3份已知命名问题中2份未报问题，1份仅因其他标准提示核对；命中预先指定命名/摘要来源问题为0/3（任意疑点触发1/3）。因此检查器在此回归集仍漏命名错误，不能用总体触发疑点冒称命名检出。12合成为5未报问题/7核对，二分类和预标定位均11/12，误报1份；这12个标签与原测试保持一致，仅为回归，不能当独立真实准确率。不调阈值/标签或挑最好轮替换。旧Discovery已知漏报继续保留，本轮没有启用诊断题名校准。

TP08实测：

| 指标 | 新版本：验收开启 | 同期：验收关闭 |
|---|---:|---:|
| 材料/执行 | 同15份×3轮＝45 | 同15份×3轮＝45 |
| 首轮生成产出 | 43/45＝95.6% | 42/45＝93.3% |
| 最终产出 | **43/45＝95.6%** | **42/45＝93.3%** |
| 实际attempt总数 | 47 | 45 |
| 有效原生成后被验收丢弃 | **0/43** | 0/42（disabled） |
| 学习事实完全保留 | 43/43 | 42/42 |
| 验收意见 | 28未报问题、15建议核对 | 42 disabled |
| 总墙钟p50 / p95（秒，所有45次） | 23.107 / 84.793 | 22.740 / 65.436 |
| 验收自身p50 / p95（秒，成功产物） | 0.833 / 1.714 | 0 / 0 |

本轮观测达到新最终产出率≥同期关闭分支的样本目标；不宣称新增验收使Pro质量/成功率有因果改善或统计非劣效。首轮与最终相同，重试没有恢复这两次失败；不是通过增加attempt改善结果。43成功产物验收后仍43份可确认；15建议核对不算生成失败，28未报问题也不算内容PASS。

全部5个最终失败均为原Pro的`review/review1 quality`，验收未调用：开启real17第2轮、real10第3轮，各先一次validation可重试，第二attempt复审拒绝；关闭real10第2轮、real06第2轮、real07第3轮，各1attempt复审拒绝。原来源/语义安全校验保持，没有把未形成产物的失败改为“正常无条目”。

安全数值：[完整90行](bug036-systemone06-20261105/generation-rows.json)、[统计](bug036-systemone06-20261105/generation-metrics.json)、[58验收回验](bug036-systemone06-20261105/acceptance-summary.json)。原始产物/判定/材料仅私有目录。用户[生成结果表](/Users/bytedance/.codex/visualizations/2026/11/05/01a1a9e5-f205-7ed2-98c2-4537082f530b/system-one-new-version/新版本生成结果表.html)含45新版本＋可切换45同期对照，展示生成摘要、条目/复习方法及核对提示，不含原始输入、图片或家庭/孩子/提交内部ID。HTML结构90行/两分支各45、0img、内部ID未泄露及脚本语法检查PASS；未浏览器视觉验收，不代验原生小程序。

TP09家长生成质量PENDING，由用户review本表；命名/范围/完整性等内容不能因本次产出率或no_finding自动通过。质量校准/独立holdout改进属后续另行冻结问题集的工作，不在本轮按回归集调题补分。

## 文档、兼容与交付

FEAT-001、BHV-032/032a、Architecture、UI-001和测试策略替换Spec05过时当前正文，发布说明区分本地/云端，Spec/README/STATUS修复状态及目录。Spec06为VERIFYING/active，无匹配云交付；Spec05未交付实验按获批替代清退，CANCELLED/rejected，不追认旧FAIL通过。历史EVD仍描述其当时版本，不重写冻结证据。

仅评估家庭只读旧草稿计数0，未获全库清零证据，保留旧覆盖元数据确认兼容及0027迁移链；Owner agent_processing/learning维护者，2026-11-12复查，须获授权全租户旧草稿清零及兼容测试才移除。实际归档按既有FEAT-005/BHV-025允许已有任务收尾，Spec06误称已记录术语勘误与独立Review，不新增生命周期行为。

最终代码/文档冲突核对已按Feature、Behavior、Architecture、UI、Spec、测试、发布/兼容与ISS/REG逐项完成；旧05当前路径措辞和Review元数据残留已替换，历史FAIL不改标。当前21份存在的Markdown文件（含Review整理及迁移目的文件；旧路径删除另计）的678个本地目标均存在，目录active12/completed109/rejected19与索引一致，`git diff --check`通过，见[链接检查](bug036-systemone06-20261105/document-links.json)。该检查只证明路径存在，不以此代替语义Review。真实内容、原生/设备、未跑可选MySQL与云观察仍不因自动检查变PASS。本任务没有部署授权，也未到发布人工门禁。
