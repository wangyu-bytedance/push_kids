---
created: "2026-11-06"
updated: "2026-11-06"
type: evidence
status: final
owner: Codex
---

# 040 / 0.1.18 版本绑定交付证据

- Evidence ID: `EVD-20261106-FULLSTACK-DELIVERY`
- Requirement / acceptance: [OPS Spec01](../completed/OPS-20261105-FULLSTACK-UPDATE.md) R01–R09；[材料Spec07](../completed/BUG-036-FIXED40-MATERIAL-ALIGNMENT.md) Q01–Q05；相关产品Spec的交付与原生主路径。
- spec_revision: `OPS-SPEC-20261105-FULLSTACK-UPDATE-01` / `BUG036-SPEC-20261105-FIXED40-MATERIAL-07`。
- subject_revision: HEAD`0576ac30464908154c624effed41df6dfa3110cc`＋批准差异，冻结manifest SHA`c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`。
- result: `passed`，仅指记录的生产迁移、040交付、只读smoke、原生主路径和0.1.18官方上传；完整验收`PARTIAL`。
- 结果、首次失败、命令和限制：[发布报告](../../docs/deploy/releases/20261106-fullstack-040-client-0.1.18.md)；[安全manifest入口](fullstack-release-20261106/summary.json)。

## Scope and output

生产迁移0025→0027/current/check/strict17触发器及双投影一致PASS；实际040CRUD无DDL/DBready/schemaPASS。040先normal0%，用户要求跳过灰度账号直接发布；助手全量前读取已是100%，没有重复切流mutation。真实微信七路GET200；仅首次错误探针参数422，正确合同重验200。线上AI生成/正式写入NOT_RUN，生产业务写0，DDL实际执行。

原生320/390确认框视觉和取消补齐；工作日两处真实HTTP保存、回填、摘要和来源跳转通过。165份生产副本匹配，私有三文件改动明确列出；不能冒称完整生产配置/语音/真机验收。连接、未编译、旧路由和截图RPC首败均保留安全日志；CUA实际AX确认最终状态，新modal截图无磁盘产物。

官方`islogin/preview/upload`完成，0.1.18上传包1,200,417字节、版本bump成功。尚未选体验版、提审或正式发布。备份保留列表因浏览器站点安全策略拦截NOT_RUN；不泄露或索取秘密。

相同源码11/05全量988/56skip、MySQL48/0skip、前端359与fixed40 v2单轮40/40证据沿用；没有新生产源码或测试变更，只更新发布版本基准及真实事实。原v1/旧30/45内容失败保持，家长内容PENDING、线上成功率NOT_MEASURED、设备/可访问性NOT_RUN。

## 方法与命令

```text
私有受控runner：Alembic upgrade head / current / check；verify_cloud_schema(verify_triggers=True)
私有runtime runner：官方SDK读取040配置，内存传入实际CRUD身份，DBready/schema/SHOW GRANTS只读
wxcloud run:deploy <frozen backend> -e prod-d2g14rwoycac6b45d -s flask-ik19 --containerPort 8000 --dockerfile Dockerfile --targetDir . --releaseType GRAY --remark ops01-20261106-c96b30d-0027 --override --detach
official DescribeCloudBaseRunServer / DescribeServiceBaseConfig / DescribeCloudBaseRunServerVersion
真实wx.cloud.callContainer：live/ready/me/children/calendar/schedule?day/report
official devtools auto + CUA原生操作 → 隔离FastAPI/SQLite，合成家庭
cli islogin --project <frozen client> --port 41292 --lang zh
cli preview --project <frozen client> --port 41292 --info-output <private receipt> --lang zh
npm run --silent release:version:next
cli upload --project <frozen client> --port 41292 --version 0.1.18 --desc <报告所列说明> --info-output <private receipt> --lang zh
npm run --silent release:version:bump
```

受控私有日志不复制凭证、环境变量或儿童原图/原始内容。仓库仅保留已选安全输出。

## Coding slice

N/A：本轮未实施生产代码；批准的两项测试维护、材料修订、Red/Baseline/Green及原质量评测见11/05独立EVD。发布状态不是代码设计或内容质量证据。独立reviewer只读复核生命周期映射和范围：旧10/13发布候选不能借040归档DONE；11份对应范围交付后归档，3份仍active。
