# Regression and Reviewer Evaluation Cases

Owner：项目维护者。用[REG模板](REGRESSION-TEMPLATE.md)关联[ISS](../issues/README.md)，
记录重放契约/版本/证据索引。实际测试和夹具仍在既有 `tests/`，新EVD在
`specs/evidence/`；历史证据保留原路径，不新建第二套测试/事故/发布事实源。

## Verification targets

| kind | 证明目标 | active所需证据 |
|---|---|---|
| behavior | 原缺陷不再发生 | test_path、精确命令、bad/fixed revision、真实Red与Green EVD |
| reviewer | 审查器识别问题/避免有害误报 | 不可变reviewer_fixture、bad_revision、已确认标签/标准及reviewer_evidence |
| both | 两者 | 以上两组分别满足 |

审查器夹具是脱敏快照或固定base/target的清单，不能仅指向变化中的工作树。
标注期望根因/位置/严重性、禁止误报、模型/提示/规则/工具版本、预算及评估者。
产品在坏版本失败与审查器在坏版本识别成功是不同结果，不能互相替代。
预期标签需人工核实，不能让被测模型自行生成并批准自己的答案。

## Run and lifecycle

1. 安全隔离坏版本复现诚实Red；环境故障不算复现，不在生产故意破坏。
2. 修复版本运行Green及相邻行为；不同版本/阶段分别留EVD，不覆盖首败。
3. Discovery/Review选择相关案例进入Spec测试点；模型/提示/REVIEW/工具变化时
   重放适用reviewer正负例，记录漏报、误报、有害修复、轮数、时间/费用和窗口。
4. CI/定时回放只有实际配置才算接入；本轮未新增CI/定时配置，缺口与
   命令/Owner/预算以[测试策略](../TEST-STRATEGY.md)为准。

状态：draft尚缺执行证据；active满足契约并纳入相关验证；quarantined注明原因、
Owner和期限且不计通过；retired注明不再适用的契约/替代案例及决定依据。
不能因失败退役，不无限续期隔离；机器校验只查结构，不证明实际执行或标签正确。

## Current cases

[终态缓存与明确重试REG](REG-20261101-FINAL-REFUSAL-CACHE-RETRY.md)为active behavior，实际预期Red/最终Green及坏/好源码清单由缓存Spec02 EVD绑定；首轮测试源未单独快照的限制诚实保留。SQLite与独占MySQL并发/事务证据，不作为模型内容或发布验收。

[知识生成机制REG](REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md)为active behavior案例，有版本绑定的真实Red/Green并已纳入BUG-036 required点。安全源码/测试快照和独立审查来源由EVD关联；真实素材内容通过率独立记录。

内容Spec03的12/15增量在同一机制REG补充正式来源局部纠正和实际SDK运输字节回归，
关联两项新增ISS与独立11/12快照。166专项/896全量PASS不能代替固定30+3语义验收。
