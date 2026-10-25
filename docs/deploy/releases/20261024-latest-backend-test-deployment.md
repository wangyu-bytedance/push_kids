# 2026-10-24 最新后端部署与本地客户端测试

- Current stage: `SCHEMA_0025_VERIFIED / BACKEND_037_NORMAL_100_PERCENT / WECHAT_READ_SMOKE_PASS / LOCAL_USER_TEST_READY`
- Scope: [已批准OPS Spec01](../../../specs/active/OPS-20261024-LATEST-BACKEND-TEST-DEPLOYMENT.md)；用户要求检查全部代码、部署最新服务端、完整客户端本地测试。
- Commit: `26714b997465fd2d1d9199f45ed931bd85c39405`。检查开始时为82ca527+已暂存增量，期间用户另一个操作提交全部增量；代理没有提交/推送。冻结01时工作区干净；冻结02另包含已批准CRUD readiness单文件生产修复，source diff及两包SHA见下方，测试/文档不混入运行包。
- Target: `wx5d2e0014690bf285 / prod-d2g14rwoycac6b45d / flask-ik19 / 8000`。
- Actual production: 22:35:45–22:35:51 CST生产0022→`20261024_0025`迁移与admin结构/投影核验通过。036因CRUD readiness缺陷deploy_failed/0%；获批修复后的037于22:55:57 normal，22:56:57官方观察已由用户调至100%/1实例，035为0%/1实例，036仍失败。035不能在0025上重启，不是回滚目标。MINIAPP/OA入口、PUBLIC关闭，18项配置继承035/基础配置，资源0.25CPU/0.5GiB/min0/max5。代理未切流。

## 全仓检查与发布准备

自动化覆盖全部后端和客户端；人工路径核对重点为035冻结源码与最新代码的差异，包括年级并发确认、知识计时、建议审批/实际记录隔离、Job租约/清理、提前复习投影/反馈、迁移和家庭授权。不是逐行形式化证明。历史测试夹具和CR-002启动检查均经具体批准修复、验证；037已接管且真实微信20项GET通过，用户业务/设备/内容门禁继续独立记录。

| 检查 | 本轮实际结果 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest tests/unit tests/integration tests/contract -q -p no:cacheprovider` | 780 passed / 40 skipped / 108 warnings，110.34s；skip为未注入MySQL环境，后续实库验证单列 |
| `npm test` | 332 passed / 0 failed / 0 skipped |
| Ruff / format | PASS，733文件已格式化；使用--no-cache |
| mypy | PASS，150源码；既有untyped-body提示1条，不代表该函数体已完整检查 |
| ESLint / DAG / design / miniapp | PASS；150模块、17页面、1221025源码字节 |
| `git diff --check HEAD` | PASS；执行时工作区已经用户提交而干净，不冒称提交前所有冻结证据空白均已修正 |
| SQLite规模专项 | 11 passed，32.29s；today_learning_reads、grade_confirmation_reads、review_inventory_scale、read_paths |
| 真实MySQL5.7.44 | 空库base→0025/current/check PASS；全部32个实际用例有通过证据，历史失败和修复后13项/年级4项复测均保留，SQLite迁移另4 passed。独立冻结包0022→0025/旧年级与旧计划守恒/9触发器/结构PASS；10k/50k新查询实际结果、查询数和500ms预算PASS，详见[实库证据](../../quality/evidence/latest-backend-release-20261024/mysql-frozen-migration-and-scale.json) |
| 本地镜像 | 冻结源码150份SHA一致；UID10001；无网络/只读容器live200/ready200；SIGTERM4.854s、exit0；开启本地测试worker |
| CLI dry-run | PASS，退出0；只打包，不创建版本/切流 |
| 微信开发者工具登录/打开 | PASS，`login:true`，IDE HTTP61088；完整真实AppID项目CLI open成功，运行useCloud/env/service匹配，当前today；未上传 |
| 云端新版本/新Schema/真实smoke | Schema0025/admin严格trigger与CRUD默认校验PASS；037 normal/100%/1实例，真实微信20项GET全部200；036旧失败保留。全量前定向smoke NOT_RUN，用户先行100%后执行读取smoke，不倒写为全量前通过 |
| 真机/键盘/读屏/新建议真实内容及用户业务 | NOT_RUN；不以自动化、容器或平台normal替代 |

本地现有依赖可用，未重复uv sync/npm install；容器构建使用冻结uv.lock和无dev依赖安装。首次离线网络模式构建因缓存不命中而无法下载uv；默认网络模式复用已有依赖层成功，失败日志保留。

## CR-001：历史迁移测试夹具与最新年级事实冲突

- Priority / gate: 原`P1 BLOCK`，现`RESOLVED`（测试修订经批准并验证）。
- Location: `tests/integration/test_supersession_mysql.py:192`。
- Actual: 该文件12 passed / 1 failed。最新app夹具升head0025、child由新API建立年级确认；测试却直接downgrade0021，先被0025的`Cannot discard shared grade confirmation facts`正确拒绝，未到预期0022永久状态保护。
- Original impact: 原测试无法证明其0022历史迁移合同；后续最新API跨历史Schema同样不可靠。该历史失败已按下述修订解除，仍保留失败记录。
- Resolution: 用户明确批准[测试隔离Spec01](../../../specs/completed/BUG-MYSQL-SUPERSESSION-MIGRATION-ISOLATION.md)，退出只读评审阶段后仅改该用例及必要导入。独立历史库/固定0022/冻结列种子验证拒绝后revision/事实/queue守恒、清理合成依赖后降级/重升；全文件13 passed、年级4 passed、SQLite迁移4 passed。原失败保留，当前门禁解除；生产保护未改，Spec已DONE迁completed。

首次MySQL runner另有初始化错误：URL.set(database=None)保留了未创建的today_learning_test库，报1049，尚未进入业务用例。补齐本地占位库后该用例1 passed；失败与重跑证据均保留，不写成生产代码修复。整个runner只创建/删除任务独占本地容器和合成库，从未连接生产。

## 冻结与配置

| 产物 | 文件/字节 | manifest SHA256 |
|---|---|---|
| `dist/release-20261024-latest-0025-01` | 154 / 1512935 | `abbafd997450213e26c467823de89223bb47e5f6105af5f9b352d109ea4b240c` |
| `dist/migration-20261024-latest-0025-01` | 182 / 1647519 | `8ff4d5fd9e508613cda6ae4397d60789db85a8168d92dd89d5e3331ce58339bc` |

两包白名单、每项SHA、当前源和本地已知秘密扫描通过。运行镜像ID `sha256:232e71e9cbb2c1687f04dfdf73951f645e5b443fcd8b5ba42065e15c623c9523`，仅本地构建，不是云端镜像摘要。

CLI dry-run在冻结目录额外留下`.temp-runkit-1792848084600.zip`，因此随后完整性复核首次拒绝未知文件；仅删除本次CLI生成的该临时ZIP后，两包白名单/逐项SHA/当前源重新通过，manifest未改。不允许把该ZIP作为实际发布输入。MySQL槽查询计划使用ix_early_slots系列索引，无槽表ALL扫描；部分相关子查询有filesort，实际计划完整保留，不宣称全部索引天然避免排序。

保持现有云配置；coverage沿用false，empty_day_early_review及learning_suggestions默认false。没有开启内容未验收的建议、地图Key或其他新能力。年级确认无开关，需0025后端。客户端版本号/包未修改、未上传、未设置体验、未提审或正式发布。

## 备份、维护窗口与恢复

2026-10-24用户在call_41ffceeca8634b69bb95f48b14bfd817明确批准OPS Spec01并确认「已完成本次数据库备份并确认恢复路径」。该门禁按管理员确认为满足，不要求重复确认；代理未独立读取备份/执行恢复。

0023新增槽和安全默认字段/触发器；0024新增8表并初始化知识计时；0025新增children两列和索引。035严格要求0022，0025迁移后不能作为可重启回滚目标。用户已批准同库迁移→新GRAY的短维护窗口，不能称零停机或兼容滚动；失败时停止放量，优先修复向前，不自动downgrade、清库或恢复备份。

测试隔离与CR-002修复Spec均已获批并验证，修复冻结02创建037且接管；数据库本次备份/OPS维护窗口批准仍保留，修复过程中只读复核0025，未重复迁移。

生产预检首次脚本误用不存在的footprint_import_jobs表，1146且未执行DDL；改为真实footprint_photos.job_state。随后核实覆盖队列23条queued、0 running；服务基础配置和唯一运行035均coverage=false，新旧worker在claim前返回，迁移不涉及该表，因此保留停用队列、不清lease/任务，要求其他任务与事务为0继续。两次预检失败证据保留，不冒充生产代码失败或清空队列。

## 文档与生命周期

本轮同步OPS批准与备份、两项获批修订、Spec索引、FEAT-001/004/005/006/013、Behavior、Architecture、UI-001/015阶段与测试策略，按实际diff核对无业务/API/UI合同变化；启动权限检查合同已合并正文与发布必需门禁，批准设计快照不变。历史测试隔离Spec已DONE并迁completed；OPS与CRUD修复Spec留active/VERIFYING，部署/自动化/读取smoke通过，等待用户本地业务验收，恢复条件为反馈实际测试结果。其他产品Spec的设备/内容缺口保持独立。

## 生产迁移与灰度记录

[迁移证据](../../quality/evidence/latest-backend-release-20261024/production-upgrade.json)：MySQL5.7.18-cynos，0025唯一head、alembic check无新操作，运行时Schema校验通过；旧年级摘要守恒、未产生grade确认事实，全部孩子有input clock。queue v2的8触发器及early slots的9触发器齐全，两个派生投影mismatch/extra均0。未写合成孩子/学习，停用覆盖队列保留。

CLI确认表AppID/env/service/GRAY/Dockerfile/./8000/唯一备注均正确后输入yes。上传解压日志仅冻结apps/api/src、pyproject、uv.lock及发布配置/manifest，未见.env/.venv/仓库dist。CLI出现已知TopicNotExist日志订阅错误，创建进度以官方控制面复核，不因此重建版本或重复迁移。22:37:30镜像推送成功，CLI构建输出摘要`sha256:6b8abcef7f02bec648dfaeba8ba39ee7ce8416cf7eac54553d9ee818c5d79892`；云端tag为`flask-ik19-036-20261024223617`。22:41:15只读控制面确认deploy_failed，停止本地CLI监听，未删除云版本。

## CR-002：CRUD账号触发器元数据不可见导致启动拒绝（已修复并通过云端读取smoke）

原`P1 BLOCK`，现`FIXED / CLOUD_READ_SMOKE_PASS`；位置`platform/database.py::verify_cloud_schema`，lifespan与ready均调用。管理员可见9个early触发器，但036实际CRUD账号同库只读探针可见0，原样冻结代码抛出「数据库提前复习投影触发器不完整」。首次本地访问内网endpoint不可达；经现有管理endpoint、同一应用账号复测成功连接0025并复现。证据[runtime-account-schema-attempt02.json](../../quality/evidence/latest-backend-release-20261024/runtime-account-schema-attempt02.json)。036健康探针connection refused仅是未监听的现象，不能单凭该报错判定端口或OOM；037同端口/资源正常并通过live/ready。

MySQL5.7要求TRIGGER权限才显示元数据，运行账户CRUD-only的约定不应因此扩权。用户在call_f5deed23a40b43f2b50e7ec67901bf90明确批准[具体Spec01/Architecture01](../../../specs/active/BUG-CRUD-SCHEMA-READINESS.md)，已仅修改Database.verify_cloud_schema：默认检查revision/必需表字段索引，显式verify_triggers=True供发布账号严格核验；新增只读发布工具和权限回归。未给应用扩权、未改migration/领域/客户端、未重复0025迁移。036失败证据保留；新包02的037已normal/100%，真实微信20项GET通过；用户写入/设备验收未执行。

自动审批曾拒绝独立“读取并持久化未知云端构建/进程日志摘要”探针，理由是未知日志可能含敏感运行信息；该命令未执行，也未绕行。改用只读控制面固定配置字段与同库应用账号固定Schema探针完成定位，后者已获自动审批执行；没有未知日志内容落盘，本次无需用户额外授权日志读取。

## 修复冻结02与037

基线仍为26714b9，加已批准CRUD readiness修复；未提交生产diff SHA256 `d3799f092594c7e31a356a8e822c8c9d3d3803fbe15f3a6085633b78088238b0`，只有platform/database.py进入新运行包。新工具只在迁移/核验包；旧01与036保持不变。

| 产物02 | 文件/字节 | manifest SHA256 |
|---|---|---|
| release-20261024-latest-0025-02 | 154 / 1513300 | `4c12f38271ec8659e4b7b472bd8d62992c8754260d5b0210aed0079ce36eda23` |
| migration-20261024-latest-0025-02 | 183 / 1648727 | `4b89bf485feef9d9e9b78034fc2d3a1d85b002bd635f2341c4dd1d0d2da8c9a7` |

本轮后端780 passed/46条件MySQL skipped/108 warnings/111.11s；MySQL5.7权限6、年级4、今日1、永久13、计划2共26 passed，空库base/head/current/check通过。最小权限实测CREATE/ALTER/TRIGGER拒绝、无trigger元数据仍能运行；错revision/表/列/索引拒绝、admin严格模式缺trigger拒绝，工具错误输出无秘密。

首轮相关今日MySQL用例立即claim失败（attempt04）；独立合成DATETIME .700000落库真实round至下一秒，生产Worker按周期重试而测试要求立即领取。按本已批准T03相关回归，只为该测试增加最多2秒轮询，不改业务/时钟/唯一提示或审批/正式事实断言，attempt05全部26项通过。原失败与真实精度probe均保留。前端未改，沿用本轮先前332 passed；SQLite性能/新SQL无变化，不机械重跑。Ruff/format740、mypy150、DAG150与diff通过。

本地镜像02 SHA `sha256:c1762e8a7e6b13fece636cfe09ba24eeec738f4fa01c2ff90accb2b2d7cef07d`，150份源码匹配，UID10001、live/ready200、SIGTERM4.808秒/exit0。两包白名单/秘密/源码检查和CLI dry-run通过；只清理本次生成`.temp-runkit-1792853493004.zip`后重新校验白名单。生产仅current/check和冻结严格工具只读核验：admin9 trigger PASS、实际CRUD可见0但默认校验PASS，23 queued覆盖任务保留。

以唯一备注`latest-20261024-crud01-26714b9-02`提交GRAY/8000/Dockerfile/.；确认表正确后yes，使用--detach不读取未知云日志。037于22:55:57 normal/0%；请求管理员定向时，用户在call_e70f1ec5975643a7be0a1580e08e766b回复「比例已经调到100%」，22:56:57官方API确认037 normal/100%/1、035 0%/1。全量前定向smoke未执行，不能追记为通过。

22:57:23完整真实AppID本地客户端经wx.cloud.callContainer读取20项全部200，耗时60–227ms，含live/ready、me、年级候选、续订/通知、孩子/科目、每日任务、今日/报表/复习目录、当前建议及足迹5项。只保存状态/耗时/形状和配置匹配布尔值，不保存孩子内容或OpenID；未代替家长确认/上传/通知/合成业务写入。新年级和建议读取接口为最新代码证据，不能由035历史smoke替代。见[037 smoke](../../quality/evidence/latest-backend-release-20261024/cloud-smoke-037.json)。前端未上传/体验/审核/正式发布，当前仍完整本地客户端供用户测试。

22:56:57–23:00:57控制面观察跨度239.699秒，037始终normal/100%/1，035 0%/1与036失败0%/1保留，未擅自删除/重启。23:01:43真实微信末次live200（2735ms）、ready200（108ms）；观察是离散采样，不代表完整时段持续指标或无瞬时错误。见[接管观察](../../quality/evidence/latest-backend-release-20261024/handoff-observation-037.json)。

23:01:48同库只读聚合复核：agent/deletion/footprint/suggestion queued或running均0，notification sending0，coverage running0、暂停queued23保留，其他事务0、Schema0025。见[接管后任务](../../quality/evidence/latest-backend-release-20261024/post-handoff-jobs-037.json)；不将单次计数当作完整queue age/5xx/429监控。最终DAG150、git diff --check及本轮20份Markdown的261个本地链接检查通过。业务/UI合同与代码无冲突；启动权限合同已更新，用户测试尚未代验。
