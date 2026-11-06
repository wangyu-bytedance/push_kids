# 测试维护 Spec01 — 测试结果

用户2026-10-31明确“批准测试维护 Spec01”，批准对象为`SPEC-20261031-RELEASE-STAGE-CACHE-TEST-01`。
仅维护`tests/integration/test_staged_mysql.py::test_mysql_stage_recovery_and_indexes`；
没有新增顶层测试，也没有修改生产代码或发布payload。

范围：matching首次失败后恰有`t/merge/review0`，且所有行绑定本family/child/submission/job；
Job与submission回到queued。重试只再次执行matching，extract/merge/review各调用一次，
最终pending_confirmation并清空临时缓存。既有锁顺序、MySQL5.7索引计划和确认边界保持。

缺陷分析：未发现可证实生产缺陷。旧数量断言2不符合已批准review阶段的持久化合同，原失败日志保留在
[`../mysql57-isolated-staged_mysql.log`](../mysql57-isolated-staged_mysql.log)，没有改期望去接受错误输出。

生成/维护：原一个测试入口增加精确身份、失败状态和调用次数断言；另一个原锁顺序用例保持不变。

| 验证轮次 | 命令与结果 | 处理 |
|---|---|---|
| 第1轮 | 精确冻结后端＋独立utf8mb4 MySQL5.7，pytest指定文件：2 PASS；Ruff PASS，format FAIL | 仅修正断言换行；保留第一轮日志 |
| 第2轮 | 同合同重新建独立临时库：2 PASS；Ruff/format PASS，154后端/168前端SHA审计PASS | all-pass复核；scope、断言和成功清理保持 |

精确运行命令为受控runner执行`pytest -o pythonpath=. tests/integration/test_staged_mysql.py -q -rs`；
临时数据库URL只通过进程环境注入，未使用生产数据或真实模型。
详细证据：[第一轮](focused-staged-mysql-green.json)、[第二轮](round02/focused-staged-mysql-green.json)、
[第二轮格式](round02/changed-test-format.json)、[源码绑定](round02/test-source.json)。

七步流程：准备、Python上下文、精确范围、缺陷分析、两轮验证已完成；覆盖率按规则SKIPPED
（用户未要求覆盖率/无CI卡口/EXEC_SOURCE为空）；执行来源与测试遥测flush单独记录。
第7步已实际执行`utree flush`测试遥测，exit0，报告duration为3.8分钟；此处记录会话执行结果，
不把未保存的原始stdout伪造为日志附件。执行来源为空，未触发覆盖率上报分支。

TP02..04最终：精确候选完整789 PASS / 46条件skip；10模块各自独立utf8mb4 MySQL5.7全部PASS，
公平复习13 PASS / 1 SQLite参数skip，足迹五万规模5 PASS。完整日志与逐项skip解释均在
[第二轮](round02/)；154后端/168前端SHA与秘密扫描PASS。新上下文
[Review01](review01.md)确认0发现。最终文档/路径/冻结源核对见[闭合检查](../../approved-delivery-closure.json)。

生命周期：[Spec01](../../../../../../specs/completed/OPS-20261031-RELEASE-STAGE-CACHE-TEST-MAINTENANCE.md)
已DONE归档。本Spec不含运行时变更；测试不进入154份生产payload。
精确兼容候选由[039正常部署](cloud-control-flask-ik19-039.json)交付，当前0%/1副本，038保持100%/1副本，PUBLIC关闭。
[部署前真实微信健康](cloud-health-before.json)live/ready200不能归属039；
[较早039内部地址探针](runtime039-schema.json)保留本地OperationalError。19:24[独立实际账号复验](../cloud-readonly-flask-ik19-039.json)从平台读取039实际应用账号，经既有批准数据库入口完成Schema0025、数据库ready及无DDL权限检查，结果PASS_RUNTIME_READONLY；没有借管理员账号或输出秘密。数据库ready不代039真实微信HTTP/业务smoke。
未完成定向039主路径、适用双账号或完整原生门禁，不以测试PASS自动推进前端上传/全量。
