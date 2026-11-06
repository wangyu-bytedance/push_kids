# BUG-036 内容Spec03 — 冻结12真实来源最终验收

结果FAIL：没有修复全部未通过样本。固定30全部保留，每份一次完整attempt；补充3和边界10各自独立分母。模型doubao-seed-2-1-pro-260628，2case/2request，270秒总预算，原45/30秒阶段上限保持。无业务/Job/checkpoint写入。

| 组 | 分母 | 产出 | C1–C6内容通过 | 严格提案通过 | 正确补材料拒绝 |
|---|---:|---:|---:|---:|---:|
| final | 30 | 20 | 10 | 9 | 1 |
| supplemental | 3 | 2 | 1 | 0 | 0 |
| boundaries | 10 | 7 | 8 | 6 | 1 |

原30：9PASS、10FAIL、9NO_PROPOSAL、1NEEDS_PARENT_VERIFICATION、1NEEDS_MORE_MATERIAL。case18知识项通过但摘要失败。原六PASS现3/6，case18/24/25回退。补充原PASS亦有摘要合同回退。内部review passed不计内容验收。

边界严格通过7/10＝6份提案PASS＋1份预期补材料拒绝；C1–C6的8包含该正确拒绝及1份仅摘要失败。严格提案通过与完整边界通过分别计数。

11/14诊断8份仅2份产出，未授予内容PASS；历史失败不覆盖、不拼接进最终分母。
早期case07/08/10/16/17私有来源笔记有误，已逐份以高分辨率原图复核纠正，最终判断为执行会话直接对照，没有外部judge。安全JSON保留来源SHA与计数。

## final逐条判断

| case | 判定 | 合同码 | 实际原因 |
|---|---|---|---|
| case01 | PASS | — | 明确对象集合、技能及摘要一致。 |
| case02 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case03 | NO_PROPOSAL | — | 局部纠正两次结构尝试均改动受保护证据，在复审/历史前拒绝。 |
| case04 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case05 | FAIL | C1, C4 | 目标名称保留填括号操作，缺实际减法不等式限制。 |
| case06 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case07 | FAIL | C5 | 同技能完整书写集合按版面容器拆为重复目标；完整名称可在上限内。 |
| case08 | PASS | — | 具名作品及直接教学证据一致。 |
| case09 | NO_PROPOSAL | — | group覆盖校验两次失败，可读材料未到最终核验。 |
| case10 | PASS | — | 原图重新核对后，完整书写对象与摘要一致。 |
| case11 | NEEDS_MORE_MATERIAL | — | 只有笼统活动标题，缺规则/范围；正确拒绝虚构目标。 |
| case12 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case13 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case14 | PASS | — | 具体计数及有限数列规则一致，未从插图扩大学科。 |
| case15 | NO_PROPOSAL | — | merge provider_timeout，无最终提案。 |
| case16 | FAIL | C3, C4, C5 | 同混合运算规则按应用题容器重复拆分，名称缺具体量关系。 |
| case17 | FAIL | C3, C5 | 已有两步运算规则之外，另以故事容器重复命名同规则。 |
| case18 | FAIL | OUTPUT_SUMMARY_SCOPE | 知识项读写子集正确；摘要把全部认读集合扩成全部书写。 |
| case19 | FAIL | C4 | 名称只说差值递增，缺材料中明确的差值/增量规则。 |
| case20 | NEEDS_PARENT_VERIFICATION | C2 | 叠加标记/改动无法支持高置信具体分点/段数，需家长核对。 |
| case21 | NO_PROPOSAL | — | reuse理由超80字符，末端校验拒绝；质量首审通过不等于最终产出。 |
| case22 | PASS | — | 完整对象集合及独立语法结构、摘要一致。 |
| case23 | FAIL | C1, C4 | 词义目标缺完整具体词组；语法名称仍以填空/作答容器为主。 |
| case24 | FAIL | C2 | 把普通手写词认作描红；原PASS回退。 |
| case25 | FAIL | C2, C4 | 旋转原图字母遗漏两项且错误判为线条/重复；不确定性未补回全集。 |
| case26 | PASS | — | 完整词表与独立问答/介绍结构一致，数词具体范围规则可恢复。 |
| case27 | PASS | — | 具名作品及完整词表一致，无插图数学规则扩展。 |
| case28 | PASS | — | 原图对象逐一复核，纠正旧字形并保持完整集合。 |
| case29 | PASS | — | 具体语法条件及全部来源场景一致。 |
| case30 | FAIL | C2 | 明确手写汉字仍识成另一字并保持high，缺相应歧义说明。 |

## supplemental逐条判断

| case | 判定 | 合同码 | 实际原因 |
|---|---|---|---|
| failed01 | FAIL | OUTPUT_SUMMARY_QUANTITY | 两作品知识项正确；摘要使用数量词，违反批准输出合同。 |
| failed02 | NO_PROPOSAL | — | 两次结构纠正改变受保护成员/目标，确定性拒绝。 |
| failed03 | FAIL | C2, OUTPUT_UNCERTAINTY_ALIAS | 韵母归类错误及备注升为教学仍存在；不确定性泄漏素材alias。 |

## boundaries逐条判断

| case | 判定 | 合同码 | 实际原因 |
|---|---|---|---|
| holdout01 | FAIL | OUTPUT_SUMMARY_QUANTITY | 完整目标正确；摘要写数量，违反批准合同。 |
| holdout02 | PASS | — | 跨科目具体目标和对象集合一致。 |
| holdout03 | NO_PROPOSAL | — | 已知书写对象因无关听力材料缺失被整体丢弃。 |
| holdout04 | PASS | — | 可变差值规则明确，未复用固定步长旧身份。 |
| holdout05 | PASS | — | 听写未错误复用仅认读的历史身份。 |
| holdout06 | PASS_EXPECTED_REJECTION | — | 缺具体单元内容，正确拒绝虚构。 |
| holdout07 | PASS | — | 明确字母方向及对象集合保持。 |
| holdout08 | PASS | — | 认读集合保持，家长备注未升为教学。 |
| holdout09 | NO_PROPOSAL | — | 长词表提取及合并名称/证据超限，未形成完整有界分组。 |
| holdout10 | PASS | — | 认读全集和书写子集分别保持，摘要未扩张。 |

## 资源与数据库

| 组 | 进程peak RSS bytes | 成功请求最大body bytes | 最大文本payload bytes |
|---|---:|---:|---:|
| diagnostic | 186777600 | 2397643 | 57928 |
| final | 172425216 | 3610637 | 44048 |
| supplemental | 161120256 | 1865345 | 62673 |
| boundaries | 151388160 | 18226 | 2094 |

诊断11请求字节为pre-SDK估计；最终12、补充、边界是HTTPX运输body长度。成功请求token/耗时/字节逐项见JSON；失败请求费用和完整资源未知。峰值仅这批进程，不是最大9图实时SDK/云资源验收，资源PARTIAL。Provider调用计数包含同一语义纠正位置的DTO结构尝试，未新增语义循环。

READ ONLY Cynos5.7前后61表：51/61指纹一致，10表变化，PARTIAL；外部写入来源未证明。agent_jobs/analysis_stage_results等未变；零测试写入不能替代全表一致。审计JSON另有`schema`版本元数据0025，不是第62张表，不计入表分母。

| 变化表 | before rows | after rows |
|---|---:|---:|
| children | 2 | 2 |
| daily_review_plan_items | 637 | 637 |
| daily_task_completions | 1 | 2 |
| review_early_slots | 258 | 261 |
| review_feedback | 467 | 468 |
| review_feedback_requests | 395 | 396 |
| review_items | 264 | 264 |
| review_member_completion_progress | 3 | 3 |
| review_member_completion_receipts | 56 | 57 |
| review_queue_entries | 264 | 264 |

11文件live/snapshot及11/12不可变manifest checks逐项SHA一致，全部运行中生产源SHA未变。896PASS/52条件SKIP/108warnings，115.03秒的[本轮日志](candidate12/backend-all.txt)独立保存；163/893历史结果未改标。

无部署、存量数据修订、自动确认或Git提交；Spec VERIFYING/active。MySQL并发、真实Worker/父母确认、云smoke/云资源、原生/真机NOT_RUN。准确65536字节存储边界、未限长SHA与慢文件I/O取消仍未覆盖。批准的一次最终30+3/边界预算已执行；保留失败，不追加随机整轮或改变标准。

[安全JSON](evaluation-12.json) · [12 EVD](../EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)
