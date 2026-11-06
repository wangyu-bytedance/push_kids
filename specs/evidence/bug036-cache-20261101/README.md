# BUG-036 缓存增量安全证据

权威结论见[EVD](../EVD-20261101-BUG036-CACHE02.md)，获批Spec02当前local10/13、VERIFYING/active，未云交付。

- `source-manifest.json`：实际9份最终代码/测试、8份实施前生产/测试快照SHA及不变prompt哈希；`snapshot_paths`定位`.py.txt`惰性副本，文件内容与原源码逐字节一致。
- `baseline-manifest.json`：实施前19份选择范围清单；文档当时状态仅历史证据，不成为当前正文。
- `red.log`：真实实施前12预期FAIL/47PASS；首轮测试源未单独冻结，不能把最终测试副本冒充首轮。基线55stdout未单独导出，实际工具结果/EVD保留。
- `focused-final.log`、`backend-full-final.log`、`mysql-*`：真实116专项、857全量/52默认条件skip、独占MySQL5.7 8PASS和迁移/Schema/销毁；首败、网络、fixture修正与旧版本断言失败原样分类留证。
- `ruff-task-final.log`、`mypy-final.log`、`architecture-final.log`：声明范围内通过；`ruff-final.log`和`format-with-parallel-artifact.log`保留最新共享工作树范围外FAIL，旧结果不追认新对象。
- [独立审查](review/report.html)：0确认代码缺陷，Cross发现1项P2文档证据计数错误，已修正；原报告与[处置](review/disposition.md)保留发现、scope/hash和核验。`review/doc-source-manifest.json`为审查时文档版本；最终修正快照见`documentation-closure-final.json`，不倒改Review原hash或将曾导出的初步0发现汇总冒充最终结果。

本目录只有脱敏报告、固定类别及源码/合成测试。没有儿童图片、原模型payload、真实身份、凭据或数据库URL；图片/配置不作为回放夹具。快照不是生产模块或新测试harness，不应直接import或被pytest收集。复现旧版只能在隔离副本按路径还原选定`.txt`和测试源，明确标记为新事后replay；不操作生产缓存。
