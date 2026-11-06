# BUG-036 current-session09/13 evidence

该目录与原07/08证据分开。当前生产源码本地`staged-20261031-09`/旧对照`child-aware-history-agent-20261031-13`；批准Spec01/Architecture01/Prompt04及新证据前提实验范围保持，未部署。

- [09EVD](../../EVD-20261031-BUG036-PROMPT09.md)：完整检查、内容/输出失败、并发通知差异和清理。
- [同30源当前会话报告](../../../../dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.md) / [结构结果](../../../../dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.json)：08current-session20输出/12内容PASS/11完整PASS；09为26/12/10，原13无提案12恢复，原PASS18/25回退；各早期运行独立保留。
- [18源/测试快照SHA](source-manifest-prompt09.json)：匹配实际生成hash；`.py.txt`为证据，不是第二套运行代码。
- [独立Review03](reviews/group_1-review03-audit.md) / [独立新证据前提审查](reviews/group_1-evidence-premise-audit.md)：各71pass/0新增确认缺陷，实际内容由当前会话评判。
- [新证据前提审查HTML](reviews/evidence-premise-report.html) / [Markdown](reviews/evidence-premise-report.md)：0个已确认新增代码/提示合同缺陷；这不改变实际内容验收FAIL。
- [08首失败](checks/full-suite-review03.txt) / [就绪隔离8pass](checks/worker-readiness-review03-recheck.txt) / [08全量复验](checks/full-suite-review03-isolated.txt) / [09全量832pass/46skip](checks/full-suite-prompt09.txt)：失败和复验分别保留。
- [通知审计差异](notification-audit-difference.json)：09为60/61表相同，通知38→37，时间/终态和保留期清理路径可查，但具体删除者未确认。
- [新清理](cleanup-round02-round03.json)：144files/32335675bytes已删除，私有原图/身份/DTO根目录不存在，68safe files已查已知身份和密钥。旧cleanup不追认新轮次。
- [产物manifest](retained-manifest.json)保留原审查快照，评測/closure最终manifest另外记录。

生成进程无DB连接/Worker/checkpoint，业务POST、草稿、Job、上传和正式知识写入均0。这里只存源码、测试、安全摘要和校验结果，不存原图、身份或原始模型响应。内容验收FAIL与全表审计PARTIAL不因本地合成检查变成PASS。Spec仍VERIFYING/active，正式确认、发布40条、云部署和原生/真机未在本轮执行。
