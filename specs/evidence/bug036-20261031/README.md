# BUG-036 本地验证证据索引

当前本地源码为09/13；[09EVD](../EVD-20261031-BUG036-PROMPT09.md)记录832/46、独立增量71pass/0确认缺陷、固定30条26输出/12内容PASS/10完整PASS、六边界5/6及通知38→37并发差异。当前会话[报告](../../../dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.md)与[审查/快照索引](current-session/retained-manifest.json)分别保留两份08和09结果；原07/08以下证据是历史版本，不能作为09结果。

当前会话[源/测试快照](current-session/source-manifest-prompt09.json)、[通知审计差异](current-session/notification-audit-difference.json)和[新清理](current-session/cleanup-round02-round03.json)独立留存：144files/32335675bytes已清理、两临时目录不存在，未修改生产数据。全表指纹相同仍PARTIAL，不能以清理完成改成PASS。

批准：`BUG-SPEC-20261031-KNOWLEDGE-GENERATION-01` / `ARCH-20261031-KNOWLEDGE-GENERATION-01` / `KNOWLEDGE-PROMPT-20261031-04`。用户原话“批准”，直接回应前一具体Spec01/Prompt04批准请求。范围为本地实施及零业务写入验证，云部署和生产数据修订不在此范围。

- [implementation EVD](../EVD-20261031-BUG036-IMPLEMENTATION.md)：诚实Red/Baseline/Green、容量/历史/失败机制、检查与限制。
- [批准时完整SHA索引](approval-baseline-manifest.json)；[实际安全源码/测试快照索引](snapshot-manifest.json)：approval、Review01、Review02、当前08分别保留`.py.txt`，避免变成第二套生产模块。
- [Review01流程](reviews/group/group_1-audit.md) / [运行时](reviews/group/group_2-audit.md)：原5项发现不覆盖。
- [Review02流程](reviews/group/group_1-review02-audit.md) / [运行时](reviews/group/group_2-review02-audit.md) / [跨组核验](reviews/group/cross-review-audit.md)：独立只读执行，最终无新确认发现。
- [Review03提示差异](reviews/review03/audit.md) / [可浏览报告](reviews/review03/report.html)：两文件08提示细化，当前续接上下文直接审查，不能冒称第三组独立审查。
- [07完整后端](reviews/full-suite-review02.txt) / [08完整后端](reviews/review03/full-suite.txt)：分别832pass/46条件skip，后者120.51秒。
- [固定30首轮07](../../../dist/knowledge-generation-evaluation-20261031-prompt04/revision07/evaluation-30.md)：13严格通过，内容FAIL；08末轮另列，不替换首败。
- [末轮08安全留存](evaluations/revision08/evaluation-30.md) / [首轮07安全留存](evaluations/revision07/evaluation-30.md)：08为25输出/9严格PASS，原PASS18/25回退；[两轮汇总](../../../dist/knowledge-generation-evaluation-20261031-prompt04/evaluation.md)区分机制与内容失败。
- [实际清理](cleanup.json)：173文件/56717611字节，原图、身份和原阶段已清理；秘密/身份扫描及产物manifest通过，其他任务未触碰。
- [机制ISS](../../../docs/quality/issues/ISS-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md) / [active REG](../../../docs/quality/regressions/REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md) / [内容ISS](../../../docs/quality/issues/ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md)。

这里没有儿童图、身份、原模型阶段或密钥。原私有业务数据的安全摘要和SHA在评测报告中；版本报告导出时清理尚待执行，后续实际完成结果由独立cleanup证据追加，不重写不可变评测。历史审查中的私有路径只说明当时运行位置，当前安全留存路径由本索引替代。云交付、原生/真机、发布40-case和正式确认未在此执行。
