# CROSS-DOC-001 — 文档证据计数修正

- Severity / origin: P2 / MINOR，文档收尾新增错误；0确认代码缺陷。
- Independent source: [最终Cross报告](cross.md)、[原发现](cross.jsonl)。
- Actual evidence: [ruff-with-evidence.log](../ruff-with-evidence.log)有10项证据副本I001、7项范围外E501，共17项。EVD原记“多出16项证据路径错误”错误，现已按该日志修正。
- Disposition: fixed，2026-11-01，获授权文档收尾/TRAE；修正EVD、Spec TP-C08、证据README和最终HTML/JSON汇总。原Cross发现不删除、不改为false_positive。
- Verification: 从实际日志分别统计`I001`与`E501`并核对10+7=17；最终源码清单仍与工作区9文件相同，文档链接和最终快照重验。仅文档/报告变化，不重新运行生产行为测试或声称独立重新审查。
- Review result: 1 confirmed P2 documentation finding, fixed; 0 unresolved findings, 0 confirmed code defects。先前读取到的0发现报告属于审查尚未终结时的初步输出，已由最终报告替换。
- Spec lifecycle: 两份BUG-036仍`VERIFYING/active`；全库静态缺项、内容FAIL、未部署等原边界保持。
