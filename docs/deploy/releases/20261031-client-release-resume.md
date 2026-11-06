# 2026-10-31 — 前端0.1.17发布续接（批准测试维护前的历史记录）

本报告全部检查与状态限定于“批准测试维护 Spec01”之前；当前事实由
[批准后最终交付](20261031-travel-diary-backend-compatibility.md)取代：测试维护完成、039 normal/0%已部署，
320两宿主各七态通过，前端仍未upload。下方FAIL和未部署为当时事实，保留原始失败及恢复过程，不作为当前门禁结论。

- Actual stage: `PREVIEW_COMPILED / UPLOAD_BLOCKED / BACKEND_NOT_DEPLOYED`。
- Authorization: 用户本轮“前端发布和部署”；沿用此前“当前效果OK 上传前端准备发布”和“后端也已经授权”的既有范围。
- Commit: `0576ac30464908154c624effed41df6dfa3110cc`＋已记录工作区差异；本轮没有修改生产源或测试、没有Git提交/推送。
- Target: `wx5d2e0014690bf285 / prod-d2g14rwoycac6b45d / flask-ik19`。
- Frontend: 原冻结168份文件与当前源码一致，manifest SHA-256 `04c6668a20a0f99622c78424b4d7c5ba07aadc1fd515f20a494e0e4cfcbb2adb`。
- Version: 工具基准仍0.1.16，候选0.1.17；未调用upload或bump。
- Preview: 官方CLI成功，编译包体 **1,191,019字节**；[原始包体信息](../../quality/evidence/client-release-20261031/preview-resume-info.json)。
- Backend: 原038＋仅BUG-035的reads/router两份批准源，154份payload；manifest SHA-256 `50a2ea9846fdfe9da13a5ae5b1b7f3ddd0e312d7f72b1961d5c2531060469c62`。未混入在改的BUG-036。
- Schema: 受控管理员严格只读检查PASS，`20261024_0025`；无迁移/生产数据写入，新增备份门禁NOT_APPLICABLE。

## 已执行检查

| 检查 | 结果与范围 |
|---|---|
| npm依赖、完整前端、ESLint、小程序/设计/架构 | PASS；349前端、17页、4 policies/151 modules；本轮重新执行 |
| 精确候选完整后端 | PASS；修正隔离目录后789 passed /46 conditional skips；实库另验 |
| 独立MySQL5.7模块 | 足迹1、Schema权限6、年级4、通知2、复习调度2、运行合同7、知识替代13、今日学习1均PASS；公平复习13 PASS/1 SQLite参数skip |
| staged恢复MySQL | **FAIL**；1 PASS/1 FAIL，旧缓存数量断言2，实际extract/merge/review0为3 |
| 候选Ruff/format/mypy | 复用本日相同150份精确候选已运行PASS；源码SHA未变 |
| Docker | PASS；精确候选150份源与镜像匹配，UID10001、8000、live/ready 200、SIGTERM exit0；本地test/SQLite，不代云smoke |
| 五万照片SQLite/MySQL规模 | PASS复测；5项通过，仍使用0.5s/原查询、内存与响应预算；首次并行运行失败保留 |
| 云部署dry-run | PASS；未创建云版本 |
| 官方CLI登录/编译预览 | PASS；login=true，preview1191019字节；旧EPERM已解除 |
| 入口320×568原生 | PASS_LOCAL_NATIVE_PARTIAL；内嵌宿主七态节点/PNG；390/430、独立宿主/完整动作、设备/可访问性NOT_RUN |
| 真实微信callContainer | NOT_VERIFIED；冻结项目9587自动化调用及后续简单探针超时，未返回可用HTTP状态；不将超时等同于服务故障 |
| 实际云运行CRUD账号Schema | NOT_RUN；本地.env只有管理员配置，.env.runtime为本地SQLite；未借管理员身份冒充应用账号 |
| 部署/upload/体验/审核/正式发布 | NOT_RUN |

完整日志与逐项结果在[候选验证目录](../../quality/evidence/client-release-20261031/backend-authorized/)。
前端本轮命令输出见[完整检查日志](../../quality/evidence/client-release-20261031/frontend-resume-checks.log)，原工具执行记录为`1ae41f8a10736dddeb5818229e3d2ac4`，结果全部退出0。
本轮原生证据在[七态节点/截图](../../quality/evidence/client-release-20261031/native-resume-attempt02/)；
只使用禁云合成数据，未自动确认真实照片。

## 失败与恢复过程

首次同时向全套实库测试注入一个未迁移、默认latin1临时库，导致16 FAIL/10 ERROR；
年级库前缀保护、缺alembic_version、字符集和重复fixture均明确命中。补齐隔离目录的冻结前端文件，
SQLite全套789/46通过；实库改为每模块独立utf8mb4库并迁移，原失败日志保留，生产数据库未使用。
唯一仍在实库失败的staged恢复测试与已批准Spec03 quality-review合同冲突，不能通过删除review或跳过测试解决。

原生首轮把连续的既有segmented tabs误作为新增8px分列按钮，七态断言FAIL；源码diff确认该控件未变，
按本次受影响的导入/草稿/历史入口范围复核，第二轮七态均PASS。两轮节点/截图分别保留。
既有tabs宽度相等、44px高、14px字、无重叠；不把零间距记为8px通过。
桌面工具仅提供菜单树，没有截图/可用模拟器尺寸控件；因此不能完成390/430和完整桌面动作验收。

dry-run生成`.temp-runkit-1793442798257.zip`，后续白名单审计准确FAIL；
移到`/private/tmp`后154份payload无缺失、无摘要改变、无未知文件，审计PASS。
不得连同dry-run ZIP再次上传。

五万照片规模首次1 FAIL/4 PASS：并行迁移时单项timeline0.521s超过0.5s。
无并行迁移复测仍用原阈值，5项PASS，结果见`footprints-scale-mysql57-attempt02.json`；未调低门禁。

## 发布阻断与具体后续

1. [测试维护Spec01](../../../specs/completed/OPS-20261031-RELEASE-STAGE-CACHE-TEST-MAINTENANCE.md)
   当时待批准；后续已批准并完成，仅修订一个已有集成测试，精确断言三阶段身份/复用/清理，不改生产流程。
2. 所有适用自动门禁通过后创建兼容后端GRAY；必须核验真实运行账号、定向live/ready、
   focus/前后分页和适用双账号/非owner路径。此前0.1.16账号验收不覆盖新focus合同。
3. 入口390×844/430×932、独立Page/内嵌主路径与适用原生矩阵仍需补齐；本轮320证据不代全矩阵。
4. 上述条件满足后从同一冻结源upload；仅成功才bump。体验版、提审、正式发布按项目人工门禁。

本轮查询最新仍`flask-ik19-038 normal`，未新部署/切流；旧037未出现在版本列表，不能称其为本轮可用回退点。
实际流量以控制台为准；本任务未独立证明038响应了真实业务请求。客户端上一已上传候选为0.1.16，
当前体验/线上版本未读取，不将它称为已上线回退版本。

## 文档与生命周期

同步Feature、Behavior、Architecture、UI、设计索引、测试策略、原准备报告和Spec索引中本次受影响的
登录/preview/验证事实；旧EPERM与局部测试保留为历史。批准设计源/快照不变。
BUG-035、导入精简、入口精简仍VERIFYING于`specs/active/`；新测试维护Spec为READY_FOR_REVIEW于active。
未取得对应云交付，不满足DONE归档；代码/当前文档核对没有发现新的运行合同偏差，已发现的旧测试
与quality-review合同不一致公开保留，不用文档消除失败。
本轮受影响17份文档链接/Spec计数与源冻结审计通过，`git diff --check`通过；
具体见[闭合检查](../../quality/evidence/client-release-20261031/resume-closure-check.json)。
