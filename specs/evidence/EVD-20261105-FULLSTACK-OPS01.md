---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: final
owner: Codex
---

# OPS01 批准后测试维护与发布续验

阶段01历史快照：本证据的37/40、材料待批准和320锁屏均为Spec07批准前事实，机器manifest不覆盖。之后批准的v2完整40/40及320补证独立见[阶段02 EVD](EVD-20261105-FIXED40-V2.md)；不能据本页历史措辞推定当前未批准或未补320。

- Evidence ID: EVD-20261105-FULLSTACK-OPS01
- Requirement / acceptance: [OPS Spec01](../completed/OPS-20261105-FULLSTACK-UPDATE.md) R01..R10；用户2026-11-05“批准 OPS Spec01”。
- spec_revision: OPS-SPEC-20261105-FULLSTACK-UPDATE-01
- subject_revision: HEAD0576ac304649＋两行测试afterSHA及原160/168冻结包，见[机器摘要](fullstack-release-20261105-ops01/summary.json)。
- 方法/命令: 新目录保留命令数组/退出码/墙钟、pytest摘要、独立MySQL逐文件结果与源SHA；不覆盖[批准前EVD](EVD-20261105-FULLSTACK-RELEASE.md)。
- result: failed，指整体发布门禁；两项测试修复及回归passed。

## Scope and output

Python988PASS/56条件skip、SDK25PASS、MySQL5.7.44十文件48PASS/0skip、前端359及静态通过。生成源和原40不变，当前完整质量门禁仍37/40 FAIL；三条一次诊断只用于定位，正式写/pending0。工作日24组和归档390/430十四组共38组状态节点/PNG；390确认框AX及实际取消已观察，额外App截图只有下层页面，不算确认框视觉PASS。320归档继续补验时系统锁屏，待用户解锁；设备/内容/新云端未验。

完整范围、预期/实际、历史首败/本轮Green、恢复条件及Owner见[发布续验](../../docs/deploy/releases/20261105-fullstack-update-ops01.md)。原始日志和带条目名称的诊断仅留本机`/private/tmp/push-kids-ops01-20261105/`；仓库仅保存安全计数、静态码和合成原生截图，逐项SHA见同目录manifest，不保存秘密、原儿童材料或模型payload。

## Coding slice

维护分支Baseline→必要两行修正→Green，不人为构造Red。原3秒字节测试在批准前全量/隔离真实失败，旧head在真实MySQL失败；两处测试修改必要性由具体Spec批准。没有用坏夹具当产品Red，没有生产重构，Refactor N/A。SDK真实运输字节/单次请求断言及deadline/queue/cancel专项原样，MySQL降级/数据/check原样；独立进程故障注入验证错误字节/重复调用会失败，不冒称修复前Red。见[Review](REVIEW-20261105-FULLSTACK-RELEASE.md)。

未云交付、未upload/bump、未修改运行配置/生产DB/Git。OPS BLOCKED/active，材料Spec07待批准，不以此EVD豁免质量、原生或人工生产门禁。
