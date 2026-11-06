# BUG-036 内容Spec03 — 冻结12版本验收

- Evidence revision: `EVD-20261101-BUG036-CONTENT03-ACCEPTANCE-02`。
- Approval: Product owner，2026-11-01，“批准 BUG-036 内容 Spec03（含 Architecture03、Prompt05）”。
- Scope: [内容Spec03](../completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)，Architecture03、Prompt05；仅本地实施、隔离测试、固定来源零写入回放和文档同步。
- Frozen candidate: `staged-20261101-12` / `child-aware-history-agent-20261101-15`。
- [12源码清单](bug036-content03-20261101/candidate12/manifest.json)保留11文件及批准10/13基线；[增量](bug036-content03-20261101/candidate12/review-increment.diff) SHA-256 `f4b83b64318427e0d45515e8ec463f97b5b904c782fac2ea657ca64efabc4a63`。
- 11/14的163专项/893全量、原始Red和合成资源探针属于[先前机制EVD](EVD-20261101-BUG036-CONTENT03-IMPLEMENTATION.md)，没有覆盖或改标为12结果。

## 独立审查与修复

两个新上下文分组按`REVIEW-20261028-01`和bits-code-guard审查完整批准差异，逐文件核对必要性、位置、测试及相关正文。

| finding | 真实问题和影响 | 修复及证据 |
|---|---|---|
| `BUG036-C03-G1-001`，P1 / MAJOR | 正式证据已把候选来源改为另一素材，局部纠正仍把旧候选来源并入授权范围，可能改动另一素材的已审查目标 | item只由正式evidence确定来源；omission保留候选lineage。新用例验证允许修正原素材账本，但禁止另一素材目标漂移，历史查询前拒绝 |
| `BUG036-C03-G2-001`，P2 / MINOR | pre-SDK字典字节统计不等于实际HTTP body；独立探针1013≠912 | HTTPX请求event hook只记录已序列化body长度，不存内容；真实SDK+本地MockTransport含中文/图片的新用例验证精确相等 |

[首轮Group1](bug036-content03-20261101/review/group_1-audit.md)、[Group2](bug036-content03-20261101/review/group/group_2-audit.md)保留各自结果；85/24直接用例调用不是独立pytest全量。
新增修复前2FAIL/1PASS：越界纠正未抛异常、1179≠1070运输字节；修复后166专项PASS/1warning，8.54秒。
其中一次中间运行165PASS/1FAIL来自revision断言未同步，保留事实，不能当作新产品Red。
[第二轮独立跨组/增量审查](bug036-content03-20261101/review/round2-audit.md)确认两finding均fixed，0新确认代码问题；
142直接单测调用与19独立探针覆盖受影响范围、实际body计数、取消/关闭/槽恢复，不能冒称重新执行全套pytest。
正文闭合、真实内容及资源未验仍独立。

诊断规则细化仍在已批准Prompt05内：素材账本引用最终数组从i0起算，不能用c编号；审查逐字核对实际证据再报告错误；重复字母按对象集合去重；同声母配套音节/词语/短句不按容器机械拆分。没有增加调用、延长30/45秒、移除review或写case答案表。

## 11版本诊断组（独立，不替换最终验收）

同原来源选择8份，每份一次完整attempt，2case/2request、原模型与参数。保留原始失败。

| source | 产出 | 实际阶段 / 原因 |
|---|---|---|
| case02 | 否 | merge / provider_timeout |
| case03 | 是 | 3个新提案；产出不计内容PASS |
| case09 | 否 | review1 / quality；同成员分合反转及证据误读 |
| case13 | 否 | merge / provider_timeout |
| case18 | 否 | merge / validation；素材账本用i1起算后改成c编号 |
| case25 | 否 | review1 / quality；旋转字母集合判断不一致 |
| failed02 | 是 | 13个新提案；仍有字词/标题及边缘对象核对问题，不计内容PASS |
| failed03 | 否 | merge / validation；摘要超长、账本编号错误；输出中的术语/备注问题仍保留 |

诊断进程peak RSS186,777,600字节；真实请求已使用SDK，但11统计为pre-SDK估计值，不能当运输字节PASS。2/8产出不代表2/8内容通过，也不是最终30的分母。

## 12版本自动化与内容状态

命令前缀`UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync`。

| 检查 | 实际结果 |
|---|---|
| 5份staged/provider/checkpoint专项 | 166PASS/1warning，8.54秒 |
| 完整backend | 896PASS/52条件SKIP/108warnings，115.03秒 |
| 本任务agent_processing及5份测试/fixture Ruff / format | PASS，28文件已格式化 |
| 全库Ruff | PASS；范围外并行维护已消除先前错误，不归因于本修复 |
| 全库format | PASS，865文件；先前失败时点仍保留 |
| mypy | PASS，151源；既有untyped note |
| architecture | PASS，4policies/151modules，无环 |
| git diff --check | PASS |
| 原30完整attempt | FAIL：20产出、10 C1–C6内容PASS、9严格PASS、10FAIL、9NO_PROPOSAL、1待家长核对、1正确补材料拒绝 |
| 补充3 / 10边界 | FAIL：补充2产出/1内容PASS/0严格PASS；边界7/10严格通过（6提案PASS＋1预期拒绝），另1摘要FAIL/2NO_PROPOSAL |
| READ ONLY61表after | PARTIAL：51/61指纹一致，10表变化，外部写入归因未证明；schema0025元数据另计并保持 |
| 私有来源与输出清理 / 文档闭合 | PASS：244文件/17目录/52,081,821字节已移除，私有材料0；11源与不可变清单SHA一致，本任务87处本地引用存在，当前正文与代码核对无冲突 |

完整成功条件仍为29份充分材料内容及输出合同PASS、case11正确补材料拒绝，补充3另计；原6PASS无回退。
当前会话已直接查看33份/74原图及原30中4份含文字素材，并逐份对照实际最终输出判断C1–C6和摘要/不确定性合同。早期case07/08/10/16/17私有阅读笔记有误，最终重新查看高分辨率原图后纠正；来源和模型输出没有修改。内部review passed不是验收。

## 固定来源最终内容结论

[逐条安全报告](bug036-content03-20261101/evaluation-12.md)和[安全JSON](bug036-content03-20261101/evaluation-12.json)保留全部43份最终判断、8份独立诊断的产出状态、来源SHA及成功请求计数，不含儿童图像、完整提案、原模型响应或身份。
原30严格PASS为case01/08/10/14/22/26/27/28/29；case18知识项内容通过，但摘要扩大书写范围，严格FAIL。case11正确缺材料拒绝仍在30分母，不能计生成PASS。
原六PASS仅case01/08/10保持；case18摘要、case24描红误读、case25遗漏字母回退。补充failed01知识项正确但摘要使用数量词，failed02受保护范围漂移被拒绝，failed03韵母归类/备注教学/素材alias仍失败。

原30无提案包含6份merge provider_timeout（02/04/06/12/13/15）、03局部证据漂移、09提取group覆盖失败、21reuse理由超80字符。
其余失败保留名称缺具体规则/对象、按容器重复拆分、字形误读、高置信几何无法核对及输出合同问题。边界03把可用书写对象随无关听力缺失整体丢弃，09长词表仍超限，01摘要数量失败。没有修复全部样本，没有补跑随机整轮或降低标准。

## 资源与零写入核验

同模型、2case/2request、每源一次完整attempt及270秒总预算，45/30秒阶段和缓存02政策保持。原30、补充、边界进程peak RSS分别172,425,216 / 161,120,256 / 151,388,160字节；成功请求最大运输body分别3,610,637 / 1,865,345 / 18,226字节。文本payload最大44,048 / 62,673 / 2,094字节。逐阶段token/耗时/字节见安全JSON。失败请求的完整费用/字节未知，真实最大9图SDK/云峰值NOT_RUN，资源PARTIAL。quality_corrections是Provider请求次数；同一语义纠正位置允许两个DTO结构尝试，case03不代表新增两轮语义纠正。

READ ONLY Cynos5.7 after实际2026-11-01 18:45:10，61表中51一致；children、daily_review_plan_items、daily_task_completions、review_early_slots、review_feedback、review_feedback_requests、review_items、review_member_completion_progress、review_member_completion_receipts、review_queue_entries变化。各行数及前后SHA见JSON；agent_jobs、analysis_stage_results、正式learning记录等保持。审计对象附带schema0025元数据且保持，不是第62张表。测试Runner无DB/checkpoint连接写入、无业务POST；并发外部写入来源未证明，不能宣称全库未变。

## 文档与私有材料闭合

完成本地源码/快照/验收manifest逐项SHA核对，11份live与冻结12一致；11/12历史快照及Red/Green未改写。33份/74图在清理前再次逐图SHA/字节核对PASS，[来源指纹](bug036-content03-20261101/source-integrity.json)仅留短编号/hash/计数。70份任务证据在清理前扫描，无原身份/完整原文字/图片数据/凭据匹配；[隐私审计](bug036-content03-20261101/privacy-audit.json)记录真实范围。

[清理记录](bug036-content03-20261101/cleanup.json)：仅移除本任务私有目录244文件、17目录及52,081,821字节，原图、身份、历史上下文、stage输出与临时脚本均已清理，任务目录不存在、私有材料剩余0；其他会话材料和`.env`未触碰。[闭合检查](bug036-content03-20261101/closure-checks.json)核对18份受影响文档范围和87处本任务本地引用，缺失0；actual Spec目录109completed/14active/13rejected与索引一致。

已同步Feature、BHV-032、Architecture、UI无变更事实、Test、Prompt、父Spec、ISS/REG、索引与本地发布记录；[代码/文档核对矩阵](bug036-content03-20261101/document-closure.md)保留机制PASS、内容FAIL、资源/审计PARTIAL、条件NOT_RUN及未云交付状态，未发现本任务当前代码与正文冲突。[本轮896PASS日志](bug036-content03-20261101/candidate12/backend-all.txt)独立留存，不改写893历史证据。Spec仍VERIFYING/active，验收失败及云交付缺项未追认为DONE。

[最终闭合清单](bug036-content03-20261101/final-closure.json)在清理和矩阵补齐后再次验证：19文档范围、101处任务本地引用缺失0，11live/snapshot及全部manifest SHA一致；全部验收分母一致、私有目录不存在。保留初轮18/87检查，不改写历史数量；最后`git diff --check`通过。

## 生命周期与未验边界

Spec仍VERIFYING，位于`specs/active/`，无对应12/15云交付。本轮无部署、生产Job/reset、业务POST、数据库/checkpoint写入、自动确认或Git提交。
MySQL并发、真实Worker/父母确认、定向云smoke、原生/真机和发布门禁本轮NOT_RUN；公开API、Schema和UI无修改，不据后台测试补记设备验收。[本地发布记录](../../docs/deploy/releases/20261101-knowledge-content03-local.md)明确区分本增量和10/13另任务准备包。
先前Review记录的未限长SHA读取、同步文件I/O取消，以及精确65536字节与既有存储65535边缘不由本轮合成/真实回放追认为已覆盖。
