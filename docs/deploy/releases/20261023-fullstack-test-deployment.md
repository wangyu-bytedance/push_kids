# 2026-10-23 — 完整服务端与客户端本地测试交付

- Status: BACKEND_035_100_PERCENT / SCHEMA_0022_VERIFIED / LOCAL_CLIENT_READY / USER_ACCEPTANCE_PENDING。用户指定同库升级顺序已执行；035 normal/100%/1实例，用户已删除034，旧实例0，coverage=false。真实微信18项GET全部200，本地完整客户端已重开并进入旅行日记。
- Scope: 用户明确选择当前全部代码，含通知续订、旅行日记、AI永久替代复习词条及已批准入口/文案。
- Task: [运维Spec04执行记录](../../../specs/active/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md)。原Spec02完整范围/备份批准保留；用户在同库并发风险说明后明确要求直接升级当前push_kids库（call_98faa5ae52df44ce902b9b30645c9670），取代停旧消费者前提。不新增业务代码或迁移设计；Spec03临时维护提案撤回并移至rejected，不再等待其批准。人工接管/删除及真实产品验收保持独立。
- Git基线：`82ca52775bc948f2a963a8f4ed614322d8859de8`；完整未提交业务差异纳入冻结范围，无提交/推送。
- Backend target: `wx5d2e0014690bf285 / prod-d2g14rwoycac6b45d / flask-ik19 / 8000`。
- Before: 发布准备初始031 normal/100%，随后用户发布配置版034并删除031；迁移前034 normal/100%/1实例、coverage=false、公网关闭。MySQL5.7.18-cynos / Schema0019；After：10:55升级0022，035 normal，用户随后切到100%并删除034，真实微信健康/读取smoke通过；前端仅本地打开，未上传。

## 实际门禁

| 检查 | 结果 |
|---|---|
| 完整unit/integration/contract | BUG-031后重跑671 passed / 35 skipped / 86 warnings，92.98s；skip为未注入MySQL的普通套件，另执行专项 |
| 前端 | 275/275，ESLint PASS |
| Ruff / format / mypy | BUG-031后PASS，628 Python文件格式、130类型源；reads.py既有未注解提示不抵扣覆盖 |
| architecture / design policy / miniapp | PASS，DAG130；pages17/source_bytes1163980（非上传包体） |
| 真实本地MySQL5.7 | 最终冻结迁移包/源码：5.7.44；base→0019→0022/current/check通过，27专项＋4规模=31 passed，无skip，临时库清理 |
| 真实足迹50k读取预算 | 首候选FAIL2.255s，获批BUG-031修复后，最终MySQL1/1000到访0.3935/0.1724s、峰值<6MiB，SQLite0.0326/0.1040s；实际索引/主键、无DEPENDENT、顺序/隔离/删除/分页及原查询/响应预算PASS。首次并行修复回归另有0.543s及过窄ref断言失败，保留结果摘要，不放宽500ms |
| 真实覆盖语义 | 1 passed，仅固定人工标注合成样本；不外推所有真实输入 |
| 真实Ark40例 | PASS40/40，三科语义各15/15，operational_failures=0、formal_write_count=0；staged-20261020-04 / doubao-seed-2-1-pro-260628。BUG-031仅改reads.py，模型模块与此执行时源逐项相同，未重发40次调用 |
| 最终运行包 | `dist/release-20261023-full-bug031-01`：134文件/1406788字节；逐项SHA、当前源一致性、本机已有秘密值扫描PASS；无manifest外文件 |
| 运行包manifest SHA256 | `001c2e0be2b6f0518b74248e2e2fc2dd54c8ddf100df3fc908732d3e7d67432e` |
| 独立冻结迁移包 | `dist/migration-20261023-full-bug031-01`：157文件/1528565字节，含完整Alembic链/env.py、运行源码及queue v1/v2；迁移实测从该目录执行。测试生成pycache已清理，无manifest外文件；后续runner设置PYTHONDONTWRITEBYTECODE=1 |
| 迁移包manifest SHA256 | `39aba303a370e8156fd61b730bb183d0367d8aba39b325bf47d12b0aa0eea31e` |
| cloud dry-run | 新冻结包PASS；CLI ZIP440173字节，SHA`d414b7456e16352aa7340971638ee2e617b293460b43232deeb1d2e90adc415c`；已移出发布目录，不代表部署成功 |
| 本地容器构建/运行 | PASS，2026-10-24从相同冻结目录标准构建成功（依赖层缓存）；Dockerfile/lock未改。镜像`sha256:ec384a3c9c4699aa1cba3b0398498ae6bee7cba82ccb5863bcce91f62b181045`，130份Python源与manifest一致。隔离网络/只读文件系统/合成SQLite，UID10001、8000 live/ready均200、SIGTERM 0.414秒退出0/OOM=false；构建代理未持久化，镜像config/history已有秘密扫描PASS。此前Docker Hub/公共PyPI超时不改写为成功；见[持久证据](../../quality/evidence/fullstack-release-20261024/container.json) |
| CLI本地完整客户端 | 启动证据PASS；2026-10-24重新islogin/auto成功，HTTP61088/自动化9465；真实AppID/完整插件、useCloud=true、正确env/service，无fixture注入或上传。旧031 live/ready均200，不代验新后端。随后维护排空时用官方close关闭本任务项目以停止本地请求，后端验证后重开 |

2026-10-23临时测试日志在恢复会话后已不存在；其实际结果与独立复核摘要保留在本记录，不宣称可重新访问原日志或2026-10-24重跑。2026-10-24补充的安全容器结果已持久化在仓库。拒绝直接回显潜在敏感原始日志的自动审批后，改为进程内只提取白名单统计与固定错误类别；未输出秘密，未绕过审批拒绝。

初始失败候选`dist/release-20261023-full-82ca527`（134文件/1406603字节，manifest`53e43f069d6bee53596aa5e92295b6e6093c8cf0547ed2f30aefdf19b73dd2c4`）保留供追溯，禁止部署；其dry-run/构建不当作最终候选通过。独立review确认BUG-031合同等价且31项及291文件SHA通过；前次OPS四项finding已被性能修复、停净旧消费者、前置灰度验收与独立迁移包解决。2026-10-24容器门禁通过，BUG-031设DONE并迁至completed，人工运维门禁仍开放。详见[BUG-031证据](../../quality/evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md)。

2026-10-24只读复核：服务normal，031 normal/100%/1实例，其他列出的旧版本0%/0实例。入口实际返回MINIAPP和OA，PUBLIC仍关闭；此前“仅MINIAPP”是目标约束，不是此次完整入口列表。管理员配置门禁须核对OA与目标入口合同的差异，不自动扩大或关闭入口。没有创建版本或变更流量。

## 2026-10-24 备份确认后的维护预检

用户已确认数据库备份成功并允许维护排空切换，Spec02设APPROVED。官方CLI只读复核031仍100%/1实例，未实际停净；数据库仍0019。分析running=0、删除running=0、通知sending=0，分析/删除queued=0；innodb_trx所见其他活动事务=0，统计受账号可见权限约束，仅为一次观察，不能代替阻止新请求/消费者停净证据。两个冻结包291项SHA/当前源再次匹配。

基础配置中尚无`PUSH_KIDS_COVERAGE_ENABLED`，不能将缺失当作false；新二进制默认true。需由管理员先在服务设置中预设false，保留其他环境变量/通知秘密和现有资源，核对MINIAPP/PUBLIC/OA入口合同。官方CLI现有命令未提供可确认的暂停/停止消费者命令；不以删除服务、0%流量、min=0或猜测控制面接口代替停止。

控制台页面读取被浏览器site-safety策略拒绝，未通过其他浏览器/间接接口绕过该页面限制。备份成功按用户确认记录，不宣称已独立读取备份或验证隔离恢复。须由管理员确认隔离恢复、定向灰度与停止能力，再排空并暂停全部旧实例/后台消费者及自动拉起；若无这些能力则保持旧服务，不能先停服或先迁移。仅在CLI副本数、任务和事务复核满足后，才从冻结迁移包执行0019→0022。见[历史安全预检摘要](../../quality/evidence/fullstack-release-20261024/maintenance-precheck.json)；随后配置已生效，当前见下段。

用户随后报告“操作已完成，旧实例为0、coverage=false已设置”。10:26:11和10:27:01 CST官方接口复核完整8版本清单仍031 normal/100%/1实例，其他0，基础和运行版本的17项配置均未含该开关；任务/事务所见仍0、Schema仍0019。报告与读数尚不一致，已请管理员核对AppID/目标环境/服务和配置提交生效状态。当前不执行DDL或新部署，不重复索取方案批准。为减少本地请求，已通过官方DevTools CLI `close --project apps/miniprogram`关闭本任务项目；源码/配置未改，后端验证后重新打开。冻结包SHA再次通过。详见[复核摘要](../../quality/evidence/fullstack-release-20261024/maintenance-recheck.json)。

## 数据库、启用及回滚

配置历史：10:34:07 CST基础配置和034已核验coverage=false；034 normal/100%/1实例，031 normal/0%/1实例，两者镜像相同，数据库0019、在途任务/可见其他事务0。10:35用户删除031已核验。当时按Spec02等待旧消费者停净；该顺序后来被用户明确同库升级指令取代，实际迁移见下节。[配置证据](../../quality/evidence/fullstack-release-20261024/configuration-confirmed.json)保留原时间边界，不作为迁移后的状态。受保护控制台未代操作或绕过。

迁移链0019→0020（通知五表）→0021（足迹五表）→0022（永久状态字段/索引、覆盖两表和queue v2）。旧031严格要求0019且忽略永久状态，不满足免备份兼容条件。备份、隔离恢复路径与迁移窗口必须由管理员确认；不能将旧031的存在写成0022的可用回滚点。

coverage=false不能阻止旧分析/删除worker、通知scheduler或HTTP请求写入。用户在该风险解释后明确指定先同库迁移再启动新版，由其删除034；Spec04据此记录维护窗口，无写入隔离或零停机保证，不再要求先停旧实例。未清lease或删除任务；旧版重启可能因严格0019校验失败。新版接管后仍观察至少2分钟，不把这种临时共存当作兼容性通过。

代理提交的新灰度保持coverage=false，并请求定向测试配置；用户在该请求等待期间先完成100%接管/034删除。全量前定向验收NOT_RUN，不因接管后成功而追认通过。接管后的真实微信18项GET及绑定状态通过，真实写入/私有照片与两个账号隔离仍NOT_RUN。coverage继续false；开启需独立配置灰度/验收/人工全量。关开关不恢复已替代状态；不自动downgrade或删数据；若必要，恢复备份/旧版须管理员在隔离核对窗口内写入后另行批准。

地图Key未配置；人工路径保留，不能将地图检索、EXIF真机保留率、真实全球底图/照片私有对象、AI地点效果写成已验收。用户本地测试不替代这些产品门禁。

## 当前交付阶段

10:35:45 CST复核用户“31版本已经删除”：完整8版本清单已无031，034 normal/100%/1实例，其余0；基础配置/034 coverage=false保持生效。数据库0019，在途任务及可见其他事务仍0。用户随后确认没有暂停入口；不再要求查找该入口。公开检索查到通用[CloudBase Run停止实例API](https://cloud.tencent.com/document/product/1243/130558)，但未验证其适用于当前微信控制台或足以防止自动拉起，未调用、未据此绕过受保护页面。

### 用户指定的直接升级与035部署

用户明确要求“老的数据库已经备份……直接修改……然后拉起新版本服务，我来删除老版本”，并在`call_98faa5ae52df44ce902b9b30645c9670`确认“直接升级当前push_kids库”。原Spec02业务范围和备份批准保留；此具体指令取代停净前提。未批准/实施的[Spec03维护桥接](../../../specs/rejected/OPS-20261024-SPEC03-MAINTENANCE-PROPOSAL.md)撤回归档，不新增临时程序、数据库或云服务。

10:53复核完整8版本：034 normal/100%/1实例，coverage=false；当前库0019，分析/删除queued/running、通知sending、账号可见其他事务均0。291项冻结SHA/当前源/已有秘密扫描及镜像130源匹配通过。首次runner在`alembic current`连接检查因会话初始化URL转义报1064，未进入upgrade，库仍0019，见[首次失败摘要](../../quality/evidence/fullstack-release-20261024/database-upgrade.json)。修正一次性runner参数、不改冻结源码后，10:55:17–10:55:25 CST执行冻结Alembic current→upgrade0022→current→check全部PASS；55预期表无缺失、4永久状态列存在、8个queue v2触发器齐全/v1已移除、派生队列差异/多余项均0、superseded=0。见[实际迁移证据](../../quality/evidence/fullstack-release-20261024/database-upgrade-attempt02.json)。未清库或写生产合成记录，备份恢复未执行。

10:55:52 CST从最终冻结包通过官方CLI提交GRAY，版本`flask-ik19-035`，备注`full-20261024-bug031-ops04-01`，端口8000、Dockerfile、工作目录`.`，未传环境参数或noConfirm。10:58:58核验normal/1实例/0%，18项配置与基础配置/034逐项一致、coverage=false，CPU0.25/0.5GiB/min0/max5保持，入口OA/MINIAPP、PUBLIC关闭。云构建镜像digest=`sha256:4aec5f680599624d07477d12729c8ab930b5c4453a0d2a9256b3ee1a1d16428f`，API源COPY/冻结无dev依赖安装/推送成功；与本地arm64镜像digest区分，见[云构建摘要](../../quality/evidence/fullstack-release-20261024/backend-035-build.json)。CLI用户日志查询TopicNotExist未解决，不等于部署失败或运行错误数0。

请求用户配置035定向测试后，03:00官方读数已变为035 normal/100%/1实例、034 0%；用户随后明确回复“34已删除，35流量100%”。03:01完整8版本清单核验034不存在、其他旧版本实例0、035 100%；代理没有切流/删除。全量前定向检查未执行，真实链路检查在接管后完成：live、ready、me、通知设置/续订、足迹偏好、孩子、科目、每日任务/今日、首页、复习清单、报表、足迹草稿/到访/统计/地图/回放18项均200，当前账号bound。只返回状态/响应形状，无生产合成写入或儿童内容日志，见[微信smoke](../../quality/evidence/fullstack-release-20261024/cloud-smoke-035.json)。03:02复核035仍normal/100%/1实例、旧实例0、Schema0022、在途/排队任务与可见其他事务0。[版本配置证据](../../quality/evidence/fullstack-release-20261024/backend-035.json)随最终观察更新。
本地完整客户端已通过官方CLI auto9465重开（HTTP61088），真实AppID/完整语音插件/useCloud/env/service正确；实际记录Tab标题菜单→旅行日记timeline组件加载无错、有可用孩子，无fixture注入/源码改动，见[当前本地入口](../../quality/evidence/fullstack-release-20261024/client-local-entry.json)。现在停留旅行日记供用户测试；未选择或上传照片、未提交学习/旅行记录、未申请订阅授权或发送通知。
本任务后端目标为按门禁到达可测试版本；用户要求客户端本地部署，因此不推进小程序版本号或上传。

11:01:16–11:03:33 CST四次完整控制面快照跨136.753秒，035均normal/100%/1实例、旧实例均0；11:02/11:03库0022及在途/排队/可见其他事务0。[接管观察](../../quality/evidence/fullstack-release-20261024/handoff-observation.json)记录实际样本与限制：非连续事件流，应用日志仍TopicNotExist，不能宣称完整错误率/p95通过。现已到达后端全量及客户端本地可测试状态，用户写入/真实素材与产品验收仍开放。

文档同步以实际Schema/云版本状态为准；Feature001/003/011/012、Behavior核对、Architecture、UI-018、主Spec、索引及发布/质量证据同步当前0022/035/本地打开事实。业务源码、API/UI合同、设计快照、FEC与测试策略本轮未改；全量前定向检查和真实产品验收未冒称通过。原Spec02批准保留，OPS Spec04在active/VERIFYING等待用户业务验收，Spec03撤回至rejected；产品Specs继续active/VERIFYING，BUG-031保持completed/DONE。后端100%接管与前端本地测试均不代表小程序已上传、体验、审核或正式发布。
