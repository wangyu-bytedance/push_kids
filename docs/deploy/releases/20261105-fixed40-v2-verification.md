# 固定40材料Spec07批准后的独立验收

本报告为阶段02的材料/模型验收快照；该阶段机器manifest保持不变，最终独立窄核PASS、0新增确认问题。随后第二次解锁的48组工作日截图和430确认框视觉/取消另见[阶段03](20261105-fullstack-native-followup.md)，下文原生45组/锁屏均为阶段02时点。

本阶段按用户2026-11-05“批准固定40材料 Spec07”执行。生产源码、Prompt、评分、阈值及重试不变；只新增版本化材料，原40及其37/40 FAIL保留。该结果不能称为生产代码改进或线上成功率100%。

## 完整单轮结果

| 对象 | 结果 |
|---|---|
| v2固定材料、原Worker/Pro生成＋System One辅助验收 | **40/40，100%，PASS** |
| 语文 / 数学 / 英语 | 各15/15，100% |
| 整体/每科门槛 | 原95%/90%，不变 |
| 运行错误 / 空提案 / 剩余pending / 正式写入 | 全部0 |
| 完整40运行次数 | 1；不按诊断复跑替换评分 |
| 总墙钟 | 约527.8秒，8分48秒；OS秒级进程起点至报告mtime，不是逐条模型延迟 |
| 家长内容验收 | PENDING，自动科目评分不能替代 |

命令：`uv run python tools/evaluate_analysis_quality.py --provider staged --cases tests/fixtures/analysis_quality/cases-20261105-v2.json --report <private>/fixed40-v2.json`，退出0。管线`staged-20261101-13`、生成模型`doubao-seed-2-1-pro-260628`；运行后读取同一配置确认System One开关true、模型`doubao-seed-2-1-lite-260915`。Lite只辅助验收，本轮未导出逐条验收意见分布，40/40不是Lite内容合格率。完整[安全报告](../../../specs/evidence/fullstack-release-20261105-ops01-v2/quality-report.json)保留全部40分母；原版本37/40不回写。

## 材料与生成效果边界

v2仅multi-04.material补充三个明确英语词汇。40唯一ID/原顺序、36单科＋4多科、30图＋10文及每科预期分母15全部保持。原文件SHA `9bdaec483fa9f6cc65e7a46c3656e70f2304efd42ecab3fe362864afa8fd829f`不变。原160后端白名单和168客户端文件、评分器/管线/Worker/合同与迁移仍与冻结源SHA一致；[逐项验证](../../../specs/evidence/fullstack-release-20261105-ops01-v2/fixture-verification.json)独立记录。

另执行一次multi-04 v2输出样本，沿用同一Worker、隔离SQLite，21.071秒/1attempt/三科产物，零正式写/pending。仅为家长提供条目结果表并核对三个词汇，没有把它当第41个门禁样本或覆盖完整40结果。命名中英语仅出现所给三个词汇；内容合格仍由家长review。原三个失败case的一次诊断与旧37/40仍见[上一阶段](20261105-fullstack-update-ops01.md)。

## 原生与发布状态

用户回复“开启了”后，320归档7态节点/PNG已补，三视口归档21组，加工作日备注减法24组，共45组状态节点/PNG。320联系表与有未完成状态整图已视觉查看；合成离线fixture、真实WXML/WXSS且拒绝云写，不冒称真实业务或设备验收。390确认框AX和实际取消沿用上一阶段证据；额外App截图只有下层，不能算modal视觉PASS。320再次尝试未观察到确认框，后续CUA返回noWindowsAvailable，重取app明确提示Mac再次锁屏；已请求再次解锁。确认框视觉、工作日完整入口动作、iOS/Android、大字/读屏/焦点等仍PARTIAL/NOT_RUN。

Python988PASS/56条件skip、SDK25PASS、隔离MySQL5.7.44十文件48PASS/0skip、前端359及静态PASS是相同源码的上一阶段实测，不为材料数据变更重复运行整套。MySQL两条迁移路径PASS，不把48项称为默认56skip全覆盖。对应[不可变阶段摘要](../../../specs/evidence/fullstack-release-20261105-ops01/summary.json)及原失败日志均保留。

未修改生产DB/运行配置、未迁移/部署/上传/bump/切流、未Git提交推送。云端039/Schema0025/客户端0.1.17为先前已确认阶段，本增量未重新查询。039不兼容0027，后续必须先完成适用原生门禁，再由管理员确认备份、受控窗口及0027兼容恢复方案；尚未进入该生产人工动作。

## 文档与生命周期闭合

已按实际diff同步Feature001/005、UI001/015、测试策略、ISS、OPS与Spec07、发布入口及Spec索引。Architecture/Behavior Catalog/API/批准DREV/FEC无行为变动；生产逐项SHA不变，没有新增边界或扩展点，不伪造新版架构设计。原OPS阶段EVD/机器manifest保持当时快照，新阶段另存[EVD](../../../specs/evidence/EVD-20261105-FIXED40-V2.md)，历史文档的待批准/锁屏均限定为原阶段。

Spec07本地材料实施和自动验证完成，内容review独立PENDING，未有匹配OPS云交付，仍VERIFYING于`specs/active/`。OPS01因适用原生缺项和后续生产门禁保持BLOCKED/active；本轮40/40只解除质量自动门禁，不把其余验收改PASS。当前active14＝VERIFYING10＋READY_FOR_REVIEW2＋BLOCKED2，completed109、rejected19，共142。
