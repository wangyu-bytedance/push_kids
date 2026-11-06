# 中国工作日日程实施与验收证据

Evidence revision: WORKDAY-EVD-20261105-02；绑定[Spec02/Architecture02](../../../../specs/completed/FEAT-001-CHINA-WORKDAY-SCHEDULES.md)、`DREV-20261105-WORKDAY-02`。
基线HEAD `0576ac30464908154c624effed41df6dfa3110cc`加既有工作区。用户“完成这个方案的落地”批准Spec/架构，具体设计的HTML源与60张导出生成后获“批准此设计并继续前端实施”；批准前未实现界面。

`source-sha256.json`绑定本轮生产/测试/工具对象，`artifact-sha256.json`绑定设计/证据/文档；均为当前工作区快照，不是Git提交或发布allowlist。批准设计源SHA保持`b3bde16a5013c1325cdb1f1bb90a2f5bdef1c778985f58f4c948621b24677ee9`。不含密钥、真实儿童资料、图片或模型payload。

| 检查 | 结果 | 保留文件/说明 |
|---|---|---|
| 后端/前端Red | 6/9与6/6预期失败 | [后端Red](../../../../specs/evidence/EVD-20261105-WORKDAY-RED-01.md)、[前端Red](../../../../specs/evidence/EVD-20261105-WORKDAY-FRONTEND-RED-01.md)；原首败留会话，不伪造缺失原始日志 |
| 最终后端专项 | 16PASS，6.91s，19warnings | `logs/focused-final.log`，全年独立日期期望、API、迁移/重启、planner入队 |
| 完整Python | 最终919PASS/52SKIP，145.32s，126warnings | `logs/python-final.log`；未配置隔离MySQL。新增旧fingerprint/停用活动回归及增强window断言后已重跑全量；此前917PASS日志`python-01.log`独立保留 |
| 完整前端 | 359PASS，0FAIL，1687.26ms | `logs/frontend-final.log`，含新增工作日10项；实际Page VM与API/wx边界替身 |
| Ruff / format / mypy | PASS / 930 files / 152 sources | `logs/ruff-final.log`、`format-final.log`、`mypy-final.log`；mypy保留无注解函数提示 |
| 架构 / 设计 / 小程序 / ESLint | PASS | `logs/*-final.log`，5 policies/152 modules；17页、source_bytes1245796（小于1.5MiB源预算，未测上传包） |
| SQLite0025→0026 | PASS | 专项两例：默认false、原旧行、禁止丢失true行的降级、本地启动后重启保持 |
| 全库Alembic check | FAIL（既有漂移） | `logs/migration.log`；四个learning_records单列索引。`alembic-baseline-comparison.json`显示旧0025与新0026完全相同、工作日表无新增漂移；复现脚本保留为`alembic-comparison-script.txt`，不修范围外Schema |
| 原生三视口节点 | 48组PASS | `native/`，320×568/390×844/430×932×设置/日程×8状态。检查实际窗口、横向边界、新模式/picker/保存热区44px、规则14px及保存可见；不代表所有控件和可访问性通过 |
| 原生PNG / 视觉 / 真机 | PARTIAL / NOT_RUN | RPC截图超时，完整本地PNG缺失；390实际工作日编辑表单经CUA截图观察（会话内），不能代替三尺寸截图齐套。iOS/Android、读屏、大字、键盘、最低基础库NOT_RUN |
| 年度维护演练 | PASS_LOCAL | [runbook](../../../operations/CHINA-WORKDAY-CALENDAR.md)与专项验证2027缺覆盖安全态，未运行云端演练 |
| 独立Review / 云交付 | NOT_RUN | 作者自查不计R2；本增量没有后端部署、云DDL、客户端preview/上传/体验/审核/正式发布 |

原生环境为微信开发者工具Stable2.01.2510290、基础库3.17.4。`tools/prepare_workday_native.py`创建`/private/tmp/push-kids-workday-native-20261105`合成副本，禁用云传输、拒绝全部写入；生产WXML/WXSS原样，副本JS仅加fixture hook/API替身。`native-source-sha256.json`绑定准备时生产源，`native-summary.json`校验当前源一致及48组结果。合成背景可能保留“未建档”文案，不作为真实业务端到端通过证据。

收尾新增可见性回归：已停用活动科目不应触发覆盖警告；真实API首先1FAIL（0.43s），给原有bounded查询补同family/child科目join与active过滤后通过。见[独立保留的增量Red](../../../../specs/evidence/EVD-20261105-WORKDAY-HIDDEN-ACTIVITY-RED-01.md)及最终专项16项，增量后完整Python重跑919PASS；旧917首轮结果独立保留。查询仍最多两次limit1，范围内年份零警告查询，不引入额外列表下载。

`attempt01/`保留最初截图失败及不足的节点checker结果（未绑定selector，不能用于44px通过结论）；`attempt02/`保留修正checker后的320保存按钮小于44px失败及当时390结果。之后只在批准下限内补min-height/width44px与规则14px；最终`native/`48组全部通过。没有覆盖或删除首败。最终48组未重复调用已知超时的截图RPC，因此各JSON的screenshot_status为NOT_RUN。

其他首败：初次Alembic配置路径错误、迁移合成Subject缺color、首次mypy空值类型错误均已修复/改正；前端最初全量出现warning变量插入位置错误和旧空态文案断言不匹配，修正后359PASS（`logs/frontend-01/02/03.log`保留）。最后误用不存在的`npm run lint`是命令准备失败，正确`npm run lint:miniapp`实际PASS，不计产品Red。Today覆盖测试改为验证不宣称可靠空日；独立学习引导仍可出现，不把它误判为活动空态。

文档冲突核对：Feature001/003及索引、Behavior009a、Architecture、UI001、Test strategy、Spec/状态索引、年度runbook及本地发布记录已合并实际行为，替换原“未实施/未批准”正文；Feature001中落后的“当前038/0.1.16”改为引用已记录039/0.1.17，未重新查询生产。批准设计源/导出未修改；历史测试和发布结果不改标。缺失独立Review、原生完整截图/设备、隔离MySQL及全库Schema检查仍阻断发布结论。

Spec最终VERIFYING，继续active。开发DONE须本Spec两端对应实现分别有匹配云交付；本地通过不满足归档条件。
