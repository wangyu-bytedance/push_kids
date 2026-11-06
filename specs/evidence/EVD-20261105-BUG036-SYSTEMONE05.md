# BUG-036 System One Spec05 — 本地实现与验证

- 批准：`BUG-SPEC-20261105-SYSTEM-ONE-05 / ARCH-20261105-SYSTEM-ONE-05 / QUALITY-20261105-SYSTEM-ONE-01`，用户2026-11-05“可以，检测标准是，你用这套流程 跑一些全量的case 查看生成时间，效果”。
- 状态：VERIFYING / active；本地实现，默认关闭，没有部署、生产迁移、业务写入或Git提交。家长内容review PENDING。
- 基线：Git HEAD `0576ac30464908154c624effed41df6dfa3110cc`，工作区已有并行未提交内容。[329份基线SHA](bug036-systemone05-20261105/baseline-manifest.json)绑定实施前快照；不把其他任务的改动归到本Spec。
- 真实同源90次对照已完整结束，零harness错误；成功率/速度/已确认内容门禁FAIL，家长完整review仍PENDING。失败未被诊断重跑或最佳轮次替换。

## 实现范围

`SystemOneDecisionProvider`只拥有受信Ark专用API、beta头、响应验证与网络上限。`decision_contracts`拥有判定/回退DTO，`decision_workflow`是每次attempt独立的分类、Q1–Q7和关系账本；原`StagedArkProvider`保留Pro提取/整合/纠正。共享`request_limits`维持两个进程请求槽，未增加模型并发。

分类并行提取；按实际学科有界加载最新40个normal知识，稳定`created_at DESC,id DESC`并使用提交创建时点。每两科最多80条一个批次，实际学科最多20/800条，索引补召回仍最多20查询/100不同结果，可信总目录900。新索引迁移0027接在并行工作日0026之后，启动Schema guard同步0027。MySQL5.7分支显式使用新复合索引，避免优化器选旧subject_id索引并对科目库存filesort；SQLite不加hint。均为本地事实，云Schema未由此改变。

质量审查对完整产物及原图/原文字生成是非问题；失败标准映射固定纠正要求。关系按双方事实分类，等价/完整覆盖对应概率至少0.95，confidence只验证有限范围，不能另加未批准的0.95门槛。两类模型的修复/消歧共用一次逻辑机会；Pro回退使用严格列表DTO、每片最多24题，仍受33核心调用与45/30秒网络上限约束。

父确认等价沿旧契约observed；新版本覆盖快照绑定内容与Review版本，确认时重查，记录发生日observed后再supersede，同日已复习不再次计数。过期关系跳过；旧草稿/人工路径保留原义。接口路径、可编辑条目与前端交互保持，server-owned coverage元数据增加可选decision_revision与review_state_version。

临时结果仍18键/64KiB每键/512KiB每Job/24h。新路径reuse纯由已验证匹配推导，不单独占缓存键；classify加入终态/明确retry的固定清理合同。match uncertain不读写可复用缓存。默认`PUSH_KIDS_SYSTEM_ONE_ENABLED=false`，专用模型默认`doubao-seed-2-1-lite-260915`；关闭后沿旧分支。

## Red、Baseline及修复

| 证据 | 实际结果 |
|---|---|
| [Provider Red](bug036-systemone05-20261105/provider-red.txt) / [Green](bug036-systemone05-20261105/provider-green.txt) | 9 FAIL/1 PASS → 35 PASS，真实HTTPX MockTransport验证专用协议和错误分流 |
| [Workflow Red](bug036-systemone05-20261105/workflow-red.txt) / [Green](bug036-systemone05-20261105/workflow-green.txt) | 2 FAIL → 33 PASS；接入及uncertain缓存合同 |
| 同日确认首次测试 | 3 PASS/1 FAIL，已复习日的review_count从1多记成2；改为同日跳过重复observed，确认专项通过。未伪称首次全绿 |
| [冻结candidate01修复阶段Baseline](bug036-systemone05-20261105/repair-baseline.txt) / [Green](bug036-systemone05-20261105/repair-green.txt) | 旧stage输出预算未登记disambiguate/decision_fallback，2个实际KeyError；修后14 PASS。最早名为repair-red的运行因加载时序已读到修改后模块，实际2 PASS，不能当Red，保留而不冒称首败 |
| 关系探针 | 选项概率0.9614但confidence0.8895，额外双阈值导致错误拒绝；修回批准的选项概率≥0.95，未按holdout调低阈值或改标签 |
| [classify purge Red](bug036-systemone05-20261105/classify-purge-red.txt) | 明确retry原清理漏新classify键，1 FAIL；加入固定集合并核验跨提交/家庭和事务回滚 |
| [18键上限 Red](bug036-systemone05-20261105/maximum-keys-red.txt) | 9图+文字+两组+一次纠正+历史复用需19键，1 FAIL；不再缓存纯推导reuse，仍用原18键上限 |
| [MySQL查询计划Red](bug036-systemone05-20261105/mysql57-plan-red-gate.txt) / [Green](bug036-systemone05-20261105/mysql57-gate.txt) | 五万项20科结果/11查询正确，但一个UNION分支实际选旧subject_id索引并filesort，1 FAIL/12 PASS；加MySQL专用hint后13 PASS。最早相同计划失败另存first；second的零结果失败由夹具微秒在DATETIME(0)四舍五入导致，夹具改用已持久化的整秒形状，未改业务时点规则 |

## 固定40及关系40

原`tools/evaluate_analysis_quality.py`的fixture、顺序、评分、worker重试和清理均保持。第一次完整执行36/40＝90%，语文12/14、数学13/14、英语14/15，FAIL；没有空待确认/遗留pending/正式写。失败为zh-03整合超时、math-07提取超时（均3attempt），zh-07及multi-04纠正后质量拒绝（各1attempt）。[原始安全评分](bug036-systemone05-20261105/fixed40-report.json)保留全部失败。

诊断重放zh-07成功12.746秒；multi-04仍失败48.576秒，Q6发现遗漏后纠正的来源/账本约束没有通过。诊断重放不替换完整40的分母或得分。完整40没有历史数据；其后关系/回退和临时键保护修正按增量专项验证，不声称该旧波次是所有后续代码的同SHA全量运行。

预先标注的合成关系40对，最终37/40；自动关联17个均与标签一致（本集合precision17/17），20个正例识别17个，recall85%，低于90%目标。漏识别eq03/eq07/co07，未降低阈值补分。最初诊断波次包含12个KeyError，错误返回None不算正确拒绝；诊断与修后数据分别保留。此集合由本执行会话预标注，不冒称第三方/家长独立验收。

## 真实同源对照

固定18条沿用Spec04私有只读快照；15条材料可用，每条新旧各3轮（每路径45次），3条已取消照片原图不可用单列，不当模型失败。每对进程交错启动，旧源为实施前快照，新源为冻结candidate03；每路径单Job、进程2请求槽，两个路径可并行外呼，不能拿这些并发条件当线上SLA。

私有数据按提交创建时间过滤历史，无后来的知识或当前无版本Todo。历史名称/证据缺版本，真实Review历史快照不可重建，故真实回放不评估正式确认与覆盖事务；这些由合成数据库事务测试单列。没有重新下载材料，没有业务POST、生产Job、草稿或正式写；未重跑本轮生产全表指纹，不借Spec04的审计宣布当前全库不变。

[完整脱敏指标](bug036-systemone05-20261105/paired03-report.json)含90行、三轮、单图/多图/人工分层、全部终态与成功子集、实际已返回用量。源码冻结校验保持true，无harness错误；15/18来源可回放，3条已取消且原图不可用不计模型失败。生成计时不含下载及Python启动；同机还运行本地测试，没有CPU/网络隔离，本集合不是生产SLA。

| 指标（每路径45次） | 旧流程实施前快照 | System One candidate03 | 判定 |
|---|---:|---:|---|
| 首attempt产出（含内部纠正） | 36/45＝80% | 36/45＝80% | 新路径低于90%目标 |
| 最多3attempt最终产出 | 43/45＝95.56% | 37/45＝82.22% | 新路径低于95%，较旧路径少6次产出 |
| 无已记录纠正/消歧/回退的单attempt产出 | 32/45 | 31/45 | 单列，不冒称首轮无需修复 |
| 全部终态p50 | 34.782秒 | 26.640秒 | 降23.41%，低于25%改善目标；仍高于15秒 |
| 全部终态p95（nearest-rank） | 77.964秒 | 61.361秒 | 降21.30%，低于25%改善目标；仍高于60秒 |
| 全部终态最大值 | 149.194秒 | 131.053秒 | 三图整合超时仍可拖长 |
| 仅成功子集p50 / p95 | 34.761 / 77.964秒（43项） | 25.215 / 61.052秒（37项） | 不能用筛成功子集替代全部请求 |
| 已完成Provider响应 | 253 | 287 | 不含未返回响应的完整外呼数 |
| 已返回input / output tokens | 1,367,309 / 66,074 | 1,675,799 / 43,416 | 非完整计费；System One output=0不等于免费 |

| 轮次 | 旧最终产出 | 新最终产出 | 新p50 / p95 |
|---|---:|---:|---:|
| 1 | 14/15 | 13/15 | 24.062 / 61.361秒 |
| 2 | 15/15 | 12/15 | 26.862 / 75.058秒 |
| 3 | 14/15 | 12/15 | 28.300 / 131.053秒 |

双方均成功的36对中，新路径33对更快，单对改善比例的中位数27.45%；这是条件子集，不能覆盖新路径8次无产出。人工15次新14次产出、p50 14.266秒；单图24次新21次、p50 28.811秒；多图6次新2次、p50 60.443秒。新路径8次失败：7次纠正后quality终态，1次三attempt merge超时；失败样本/轮次为real07-r1、real17-r1、real06-r2/r3、real10-r2/r3、real14-r2/r3。completed fallback观测0/45，不把未返回请求当完整成本记录。

内容复核确认3份输出存在来源命名问题：real10-r1补全不可见标题末字，real18-r1/r2将首句当作篇名；均被内置检查放过。real18-r3已使用中性描述，不误标为同类FAIL。曾在中间更新将其误计为第4次，已明确更正并修复结果表；不改模型结果或其他分数。real07三轮拆合也不一致，粒度留家长核对。其余产物不因此被标人工PASS；零来源虚构目标已FAIL，完整匿名Q1–Q7评分仍PENDING。

主轮固定为第1轮15行，另列第2/3轮全部结果；没有挑选每条最佳结果。[本机45份真实生成结果表](/Users/bytedance/.codex/visualizations/2026/11/05/01a1a9e5-f205-7ed2-98c2-4537082f530b/system-one-review/生成结果表.html)和[固定40结果表](/Users/bytedance/.codex/visualizations/2026/11/05/01a1a9e5-f205-7ed2-98c2-4537082f530b/system-one-review/固定40结果表.md)只含生成结果与指标，不附原始输入/证据/图片/身份。完整产物继续只在私有目录，不入仓库。

候选01在发现修复stage错误后中止；候选02为协议校正诊断，未作为最终配对统计。冻结candidate03内存回放不调用生产语义purge或SQL；后续classify清理/reuse省键及MySQL索引hint增量以真实DB专项单独覆盖，生成标准及外呼保持。[最终25文件源码与测试清单](bug036-systemone05-20261105/final-source-manifest.json)及[冻结源](bug036-systemone05-20261105/final-source.zip)明确列出三份差异，不把真实波次冒称最终源码同SHA。成功的响应数及已返回token可统计；超时供应商未返回用量不能当0费用或完整外呼计数。

## TP与剩余门禁

| 范围 | 结果/边界 |
|---|---|
| TP01 专用协议 | PASS：真实合成HTTP200约0.613秒；真实图片单判断约0.796秒；不代表整单耗时 |
| TP02 分类 | 已接并行辅助，不以分类丢科；完整40多科仍有失败，非全部内容PASS |
| TP03 最近历史 | PASS：SQLite100项边界/scope/2查询；独占MySQL5.7.44五万项、20科800精确结果、同刻排序/未来/非normal及11查询，每分支实际新索引ref/range、无库存filesort。外层最多80项排序允许 |
| TP04 关系 | 单元边界PASS；合成holdout precision目标达本集合、recall目标FAIL |
| TP05 质量 | 来源失败一次纠正后终止、旧来源/纠正保护专项PASS；原40和真实内容分别评估，内置审查不代表人工质量PASS |
| TP06 恢复 | PASS：uncertain/cache/明确retry/回滚及新classify清理；独占MySQL相关8项checkpoint/并发/锁序/回滚/跨scope专项通过，不代表全部可选MySQL套件已执行 |
| TP07 确认 | 新版本正常/过期/同日/重复保护及旧人工/确认/事务专项；没有生产确认或新增真机验收 |
| TP08 预算 | 两provider共用2槽；每请求128题、900pair/33调用、9图/上传大小、文本保守96KiB、关系片90KiB；MySQL迟到写/明确retry相关8项已通过，极限形状/全部9图token估算仍PARTIAL |
| TP09 固定40 | FAIL：36/40，不用诊断成功覆盖失败 |
| TP10 真实效果 | 90次完整执行；新首attempt80%、最终82.22%、p50 26.640/p95 61.361秒，成功率/速度FAIL；已确认3份命名内容FAIL，完整家长review PENDING；只交付生成结果表 |
| TP11 兼容 | 最终全量943 PASS/57条件skip，隔离MySQL13 PASS及共享两槽专项13 PASS分别记录；无前端代码变更，设备N/A |

首次全量933 PASS/2 FAIL/52 skip：新迁移head漏同步启动guard已修；worker readiness一次StaleDataError/等待超时，单独重放PASS，未改并行调度代码。第二次全量938 PASS/52 skip。[第三次全量](bug036-systemone05-20261105/final-full-suite.txt)943 PASS/52 skip（135.63秒）；[共享两槽专项](bug036-systemone05-20261105/shared-slots.txt)13 PASS。[缓存最终专项](bug036-systemone05-20261105/cache-final-green.txt)33 PASS，历史失败不删除。起初Docker daemon不可用，启动已有Docker Desktop后使用本机已有5.7镜像创建独立容器；[MySQL最终记录](bug036-systemone05-20261105/mysql57-summary.json)13 PASS，容器及其数据卷已删除。没有连接生产作写测试，也不把相关13项代替其余可选MySQL检查。

原真实30+补充3原始私有材料已在旧任务清理，NOT_RUN，旧FAIL不重标。独立上下文代码Review NOT_RUN；当前指令未授权多Agent，未自行委派。发布、人工内容review与性能目标未通过前均不启用新路径。

新增MySQL测试和查询hint后的[最终全量](bug036-systemone05-20261105/final-full-suite-with-mysql-gates.txt)：943 PASS/57条件skip，162.08秒，进程exit0；新增5项在默认无URL命令中skip，已在独立5.7.44容器实跑，与既有8项合计13 PASS。其余44项默认skip不冒称执行。Ruff check、format（953文件）、mypy（156源文件）、架构DAG（5 policies/156 modules）、前端359、设计policy和小程序静态检查实际PASS；mypy保留默认不检查无类型函数体的配置限制，无前端原生新验收。

之后仅新增6个新快照HTTP确认用例（正常、父编辑、注入、人工、Review过期、历史补录），未再改生产源；[路由与相邻专项](bug036-systemone05-20261105/confirmation-route-final.txt)26 PASS。确认前正式occurrence/feedback为0，只有正常/补录在确认后记录发生日observed再替代，其他路径保留旧项；不把这6例倒算进此前全量943。最终源码清单包含这6例测试。完整家长内容review和独立代码Review仍未执行。

## 后续优化建议（未静默实施新规则）

1. 标题/书名独立核对逐字来源；缺字保留中性名称，不由常识补全。Q1整项概率未可靠拦住命名问题，需继续保留家长review。
2. 粒度/重复判断定位到具体条目对与失败标准，纠正建议保留实际失败项。当前全局should_merge指向全部条目，多标准合并后变成泛化建议，Pro可能原样返回并被再次拒绝；先改定位/反馈，不降低来源或关系阈值凑产出。
3. Pro提取/整合仍是主要耗时，复杂三图在merge重复超时；优先验证有界局部patch纠正和精简重复输出，维持来源账本、两个请求槽与原超时预算。真实三轮未达到速度目标，不能只凭亚秒Lite探针放行。
4. 关系40有3个正例漏识别，先核对事实表达和有界消歧，不放宽0.95阈值；标签疑义须先由独立人员确认并版本化，不能评后改标签补分。

这些建议若改变质量标准、修复协议或架构，须形成具体后续修订再实施；本轮不以临时规则重跑挑分。默认开关保持false。

## 文档与生命周期闭合

Feature、Behavior Catalog、Architecture、UI current-state、Spec/索引、测试策略/证据、ISS/REG及本地发布边界已按实际diff核对正文；共用match缓存修复对关闭分支同样生效，旧源对照不等于修后关闭分支或云039。没有改动批准设计资产。原云版本/Schema与本地0027、模型门禁FAIL、家长PENDING及未执行项分别保留，无已知代码/当前文档冲突。[闭合清单](bug036-systemone05-20261105/documentation-closure.json)绑定15份文档、25文件源码一致与本地链接检查；`git diff --check`通过。

没有匹配的云交付，Spec最终为`VERIFYING`，位置仍`specs/active/BUG-036-SYSTEM-ONE-GENERATION.md`，不迁DONE。独立Review、完整家长内容评分、原30+3材料重放、九图极限资源和其余可选MySQL/本轮全库Schema drift检查未完成；不以本次自动化或模型产出将其改为PASS。
