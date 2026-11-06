---
created: "2026-11-01"
updated: "2026-11-01"
type: evidence
status: completed
owner: TRAE
---

# BUG-036 固定40失败归因与成功率修复设计证据

- Evidence ID: `EVD-20261101-BUG036-FIXED40-DIAGNOSIS-01`。
- Requirement: 当前会话用户“排查不通过的原因 并修复，要求成功率达标”；诊断后拟定[成功率修复Spec04](../completed/BUG-036-FIXED40-SUCCESS-REPAIR.md)。
- spec_revision: `BUG-SPEC-20261101-KNOWLEDGE-SUCCESS-04`，READY_FOR_REVIEW，尚未批准/实施；本EVD是诊断Baseline，不是实现Green。
- subject_revision: 原发布10/13六条诊断；已批准内容12/15原40完整隔离复测，两个版本独立。
- result: failed，12/15完整复测33/40（82.5%）/各科60%、86.7%、86.7%；10/13六条诊断已完成，原34/40 FAIL保持。诊断完成不等于修复完成。
- 受阻发布候选仍为10/13，本轮未装入12/15、未创建灰度版本、未改变流量或Git状态。

## 1. 方法、对象与不变条件

冻结153份源码/工具/fixture；其中六份agent_processing源与内容Spec03的candidate12不可变清单SHA一致。原40fixture与评分工具没有编辑。源指纹与完整报告在[诊断证据目录](../../docs/quality/evidence/bug036-fixed40-diagnosis-20261101/manifest.json)绑定，完整复测结束后才导出六份文件，逐项SHA/字节保留。

私有诊断目录：`/private/tmp/push-kids-quality40-diagnosis-20261101`；外部观察脚本只包装阶段生成和pipeline异常，记录case短编号、DTO计数、静态科目分类和问题码，不改业务源、Prompt、评分或重试。原素材均为fixture合成数据，临时PNG用TemporaryDirectory随过程清理，不上传到仓库。

10/13六条：每条一次完整pipeline attempt、同模型/45与30秒阶段上限/270秒总上限，2026-11-01 22:16:32–22:17:37 CST；无数据库、历史返回空、无checkpoint或业务API连接。不能冒称原Worker三次尝试的逐阶段重放，不能与原40拼接。

12/15完整40：原`evaluate_analysis_quality.py`、原固定跨科目顺序、原Worker及临时SQLite、原三次Job恢复、原评分方法；Provider只从既有`.env`读key，不回显。生产数据库URL没有用于连接，媒体强制local、通知与可选coverage关闭。原40阈值≥38/40、各科≥90%、empty/pending/formal0保持。

## 2. 原六条单次诊断

| case | 已观察链路 | 结果与含义 |
|---|---|---|
| zh-05 | extract 0项/needs_context=true → group/m1 coverage | 单材料未进入merge；材料未给短文和实际时间词 |
| zh-07 | extract/merge有语文 → review0/review1 exercise_not_knowledge | 排序技能被两轮当作纯指令，规则边界问题 |
| zh-09 | extract/merge语文 → review通过 → match | 本次科目检查通过；原40失败不改标，随机性确认 |
| multi-01 | extract含zh/math且needs_context=true → group/t coverage | 已有数学候选仍整单阻断；不是没有识别数学 |
| multi-02 | extract/merge math/en → review vague_name → correction只剩en、数学indeterminate_object | 最终subject.mismatch；拒绝/省略发生在命名与范围阶段 |
| multi-04 | extract三科 → merge三项indeterminate_object → review通过 → empty_proposal coverage | 缺少字词对象与已声明数学规则一并丢弃；原空保护生效但三次重试会空转 |

以上只记录安全类别，没有保留名称、basis、证据或原模型响应。归因以阶段事实及原fixture为边界，不能解释每个原始attempt中的模型内部推理。

## 3. 假设核验

| 假设 | 结论 | 证据及限制 |
|---|---|---|
| 未配置英语或系统科目目录导致失败 | REJECTED，原六条此次诊断 | extract与merge识别英语；multi-02实际在review/correction丢数学，不是英语许可问题 |
| 单来源needs_context被构组早退，丢弃其他可辨目标 | CONFIRMED | zh-05、multi-01 group/m1或t；静态`len(group)<2`早退与运行事件对应 |
| 纯指令/具体技能/缺对象边界不一致导致省略与复审失败 | CONFIRMED | zh-07 exercise_not_knowledge、multi-02 vague_name后省略、multi-04全部省略；需要新的明确行为合同 |
| 再跑同版本自然通过即可证明修复 | REJECTED | zh-09从旧FAIL变成此次单次通过，源码不变；原FAIL仍保留 |
| 所有失败都只是fixture材料不足，代码无需修复 | REJECTED | multi-01已有独立数学候选却早退；部分材料不足真实存在，但不能解释整单阻断 |
| 新内容12/15已修复原40全部失败 | REJECTED，本次完整复测 | 最终33/40、各科均低于90%；七条输出失败、零终态基础设施失败，不能由本次单轮推断长期平均 |

## 4. 12/15完整40结果

实际2026-11-01 22:16:32–22:25:37 CST完成，exit1；[原评分报告](../../docs/quality/evidence/bug036-fixed40-diagnosis-20261101/full12-report.json)及[安全阶段记录](../../docs/quality/evidence/bug036-fixed40-diagnosis-20261101/full12-diagnostics.json)保留。

| 指标 | 实际结果 | 原门槛 |
|---|---|---|
| 整体 | 33/40，82.5%，FAIL | 至少38/40，95% |
| 语文 | 9/15，60%，FAIL | ≥90% |
| 数学 | 13/15，86.7%，FAIL | ≥90% |
| 英语 | 13/15，86.7%，FAIL | ≥90% |
| 终态基础设施失败 | 0 | 保留原输出/科目失败分母 |
| 空/剩余待确认/正式写入 | 0 / 0 / 0 | 均为0 |

| case | attempts | 实际失败阶段 |
|---|---:|---|
| multi-01 | 3 | 首次extract为non_learning/0项，merge为空，review通过后empty_proposal；后续attempt复用成功缓存，无新的生成调用 |
| zh-04 | 1 | 首审exercise_not_knowledge，纠正后复审vague_name，quality终态 |
| zh-05 | 3 | extract 0项/needs_context=true，单图group/m1 coverage；后续复用提取 |
| zh-07 | 3 | 同上；与10/13诊断的quality失败是两个独立路径 |
| zh-09 | 3 | 同上；10/13诊断PASS不替换此FAIL |
| en-12 | 1 | 两次review均vague_name，quality终态 |
| multi-04 | 3 | extract 0项/needs_context=true，单文字group/t coverage；后续复用提取 |

七条均为`analysis_output_invalid`且保留分母。multi-02本次科目检查通过，原10/13失败仍保留；新旧失败并集八条进入Spec04回归。最新33/40低于旧单轮34/40，但未做配对统计，不把差异归因为新版本长期效果。

math-03出现一次match provider_timeout后按原Job政策恢复，最终通过，不能忽略该请求，也不能将中途超时冒称最终基础设施失败。原六条诊断与完整40开始时间相同，最初65秒并行，不做耗时或资源因果比较；未量峰值RSS/完整请求费用，不补写资源PASS。

## 5. 修复准备与门禁

Spec04推荐澄清明确学科技能与具体对象边界、单来源未解上下文进入原merge、审查后空提案终态，保留来源安全、原两页group、候选/证据账本、局部纠正、历史、缓存和资源边界。不是只改Prompt取新随机结果；未实施。

原fixture、旧FAIL、整体95%/每科90%阈值和失败分母不改；正确拒绝不计提案PASS。新指纹后跑一次完整原40，若失败保留失败。真实30+3内容FAIL、资源/READ ONLY审计PARTIAL、云定向smoke/容器/发布门禁独立，不由原40替代。

批准后按Spec04实施、诚实Red/Green、专项/全量和独立Review；新发布包需单独批准对应源revision，不能复用只批准10/13的发布manifest。

## 6. 文档与生命周期

本轮形成新Spec、EVD及索引入口，生产源和测试文件没有编辑。Spec04处于READY_FOR_REVIEW/`specs/active/`；原父/缓存/内容三Spec仍VERIFYING，OPS发布仍BLOCKED。本轮没有云交付，不能DONE或归档。

最终导出六份安全文件及SHA清单，fixture/评分工具不变校验通过。实际闭合核对153份源码变化0、六份证据SHA/字节变化0、三个任务完整文档的相对链接缺失0、109completed/15active/13rejected、八个READY_FOR_REVIEW；秘密/原图匹配0，`git diff --check`通过。
[代码/文档核对矩阵](../../docs/quality/evidence/bug036-fixed40-diagnosis-20261101/document-closure.md)明确当前Behavior/Architecture/UI合同不变、Feature/Test/ISS/发布跟踪和索引已同步，未发现本任务当前正文与代码冲突；
[闭合机器记录](../../docs/quality/evidence/bug036-fixed40-diagnosis-20261101/closure-checks.json)保留实际数量与时间。未经执行的Ruff/后端/设备/云检查不引用历史PASS冒充本次；本轮没有代码变更，不重复产品测试套件。
