# 2026-11-05 — OPS Spec01批准后续验

本报告为材料Spec07批准前的阶段01记录，以下待批准/320锁屏/37FAIL均绑定该时点；机器目录保持不可变。之后用户已批准Spec07，v2单轮40/40及解锁后320补证见[阶段02](20261105-fixed40-v2-verification.md)。当前发布仍受适用原生及生产门禁约束，不能把本历史报告当最新质量门禁。

- Stage: `LOCAL_TEST_REPAIRED / QUALITY_GATE_BLOCKED / NOT_UPLOADED`。
- Approval: 用户本聊天“批准 OPS Spec01”，对应[OPS-SPEC-20261105-FULLSTACK-UPDATE-01](../../../specs/completed/OPS-20261105-FULLSTACK-UPDATE.md)和Architecture01。
- Source: HEAD `0576ac30464908154c624effed41df6dfa3110cc`＋既有dirty工作区；本轮仅两行测试变更。前后快照及SHA、命令摘要见[新EVD](../../../specs/evidence/EVD-20261105-FULLSTACK-OPS01.md)和[机器摘要](../../../specs/evidence/fullstack-release-20261105-ops01/summary.json)。
- Frozen runtime: 160后端、168客户端与原冻结清单保持一致，manifest SHA `c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`；本轮不重写原清单/首败。原打包/preview/容器及云只读事实见[批准前记录](20261105-fullstack-update-preparation.md)。
- Delivery: 没有生产DB/配置写入、部署、切流、upload或bump；沿用最近只读确认039 normal/Schema0025/客户端上传基准0.1.17，本轮未重新查询云平台，不能冒称最新平台快照或0027已部署。

## 测试维护及真实结果

`test_stage_provider.py`仅真实SDK运输字节测试的绝对预算3→30秒，仍精确检查请求/图片字节和一次请求。专门deadline、queue、取消及生产预算均未改。`test_supersession_mysql.py`仅head预期0025→明确0027，降级保护、数据守恒、重升级和`command.check`均保持。Refactor N/A：两处局部断言合同已清楚，无必要新抽象。

| 检查 | 批准后本轮结果 |
|---|---|
| SDK整文件 | 25PASS/1warning，pytest9.35秒；原失败不覆盖 |
| Python全量 | **988PASS/56条件SKIP/0FAIL**，128warnings，pytest193.68秒；launcher墙钟253.92秒分别记录 |
| MySQL5.7.44 | **10文件48PASS/0FAIL/0SKIP**，同一Runner、每文件独立迁移库；原FAIL文件13PASS。新库及0025→0027两路径upgrade/current/check均PASS，临时容器销毁；不覆盖默认56skip所有可选项 |
| 前端/静态 | 359PASS/0skip、ESLint、Ruff/format968、mypy156、DAG5策略156模块、设计policy、小程序17页和diff通过 |
| 独立Review | 两行增量0新增已确认代码问题；独立SDK25PASS，偏移运输字节和重复请求两种进程内故障注入均被原断言拒绝；不冒称生产修改Red。完整发布仍BLOCK |

批准前Python987/1FAIL、隔离SDK FAIL、MySQL各轮harness错误及旧head断言FAIL保持原EVD；本轮测试源不同，不能把本次PASS追认旧测试。两个测试ISS本地resolved，发布和线上观察独立，不写closed。

## 生成失败诊断

生产、模型参数、Prompt、原40材料/顺序/评分/阈值未变。没有再跑原40择优；当前完整门禁仍**37/40＝92.5% FAIL，数学86.7%/英语80%**。43/45仍为先前15真实材料×3轮的独立结果，不代表当前门禁、线上率或家长内容合格率。

仅原三个失败各诊断一次，在临时SQLite驱动原Worker，最后取消草稿；正式写0、pending0。只导出有界阶段计数、科目及静态码，原输入、图片和模型payload不入仓库。

| 原失败 | 此次一次诊断 | 可支持的结论 |
|---|---|---|
| multi-02：Pro review1 vague_name | 17.383秒形成两科产物，review0通过 | 失败本次未复现，不能据此证明原复审是误报或问题已修复 |
| en-08：Pro review1 unsupported_by_evidence | 13.633秒形成英语产物，review0通过 | 同上，不能用复跑PASS替换原FAIL |
| multi-04：subject.mismatch | 29.633秒形成语文/数学两科，英语以indeterminate_object省略；局部纠正后Pro通过 | 当前原材料仅给英语主题，按批准规则不能猜具体词表；原三科期望与材料冲突，见[ISS](../../quality/issues/ISS-20261105-FIXED40-SUBJECT-TRUTH.md) |

原门禁临时产物已清理，不能补称观察到原multi-04也有同样具体省略。诊断只解释此次可见链路。System One在有效原产物后辅助验收，不能恢复发生在此前的原Pro终态拒绝；本轮未改这条生产边界。

推荐[材料Spec07](../../../specs/completed/BUG-036-FIXED40-MATERIAL-ALIGNMENT.md)：另建v2，只补该三科样本的具体英语词汇，原40/FAIL保持；95%/90%和生产均不变。批准前不修改。v2完整单轮仍须真实过门禁；修正材料不等于提高了生产成功率。若需改Pro终态/转人工策略或Prompt，必须另有具体生产修订，不能用本OPS静默扩大。

## 原生及剩余发布门禁

官方auto重新连接后恢复；320/390/430工作日备注减法8态×3共24组节点/PNG完成并观察，新增短状态/已知内容保留、两处编辑备注删除、保存/触控和边界检查有效。BUG033在同一只读合成项目补390/430各7态节点/PNG，共38组状态证据；原生产WXML/WXSS相同，JS只有既有测试setter，网络写入拒绝。390确认框由CUA实际观察AX标题/正文/取消和归档按钮，点击取消后确认框节点移除；额外App.captureScreenshot只拍到下层页面，不能作为确认框PNG通过证据。确认框视觉/全交互仍PARTIAL，不当作真实儿童/云端验收。

继续切换归档320时Mac锁屏，CUA明确无法自动解锁，已向用户请求本机解锁；没有尝试获取密码或绕过。既有320节点保持，当前320归档PNG/相应交互及设备、大字/读屏、父工作日完整动作等未验项如实保留。新证据不能把整个R06改PASS。

生产仍未进入备份/迁移/灰度/切流/upload门禁。039严格0025、不能在0027上ready的兼容约束不变；未来进入生产前须按手册完成备份、受控窗口、理解workday字段的恢复方案、真实微信smoke及人工流量确认。

## 文档及生命周期

Feature001/005、UI001/015、测试策略、ISS、Spec/EVD/Review、索引和发布入口同步；Architecture/Behavior/API合同无变动，核对后不制造无事实变化的revision，批准设计快照不改。OPS01测试维护完成但整体未云交付，故`BLOCKED/active`；材料Spec07为`READY_FOR_REVIEW/active`，其余本地功能仍VERIFYING，未新增DONE。尚未验证内容质量、全部原生/设备及新云交付；不把本地测试通过写成已更新版本。
