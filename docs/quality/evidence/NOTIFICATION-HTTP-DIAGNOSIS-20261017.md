# 通知 HTTP 失败诊断证据 — 2026-10-17

- Specs：[诊断-01](../../../specs/completed/OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS.md)、[灰度-02](../../../specs/completed/OPS-20261017-NOTIFICATION-GRAY-DEBUG-DEPLOYMENT.md)、[细化-03](../../../specs/completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md)、[单条验收-05](../../../specs/completed/OPS-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE.md)，均已明确获批并完成；权限增量由-04批准。
- Architectures：ARCH-20261017-ISOLATED-NOTIFICATION-PROBE-01、ARCH-20261017-NOTIFICATION-GRAY-PROBE-02、ARCH-20261017-NOTIFICATION-502-DETAIL-03。
- Scope：修复前当前账号10条失败及对应日志、无收件人隔离探针；后续-05明确批准家庭范围的单条临时日程，结果只核验当前账号，不推广为全体家庭统计。
- Source：8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a + 未提交诊断工具、测试、Spec与事实文档；业务源码未改。
- Current state：032/033及其灰度任务已清理；必要发送路径权限按获批-04补齐。获批-05唯一临时日程0F58经原调度使当前账号达到sent/ok（18:49:19 CST），额度1→0/expired，测试日程已停用204并核验消失；用户随后确认微信已收到。最终031 normal/100%、PUBLIC关闭、原版本及受保护配置不变。

## 当前已验证事实

| 项目 | 结果 |
|---|---|
| 真实AppID的callContainer只读GET通知settings、deliveries | 均200 |
| 修复前当前账号日程/复习提醒 | enabled=true、subscription_status=accepted、remaining_quota=1 |
| 修复前最近10条投递 | 6日程+4复习，全部failed/transport_error，sent_at为空；后续-05仅有界匹配本次唯一测试，不重置旧失败 |
| 031配置 | wechat渠道、密钥长度校验满足、三类模板存在；不记录值、模板ID或接收人 |
| 原业务日志，10月13日至17日 | 30条notification_send_transport_error，异常类全部HTTPError，对应最多3次尝试；最近09:04:55 CST |
| 032隔离探针 | HTTP502、platform_errcode=null、HTTPError、reason=http_error；1条安全探针日志 |
| 033细化探针 | HTTP502/json_object，无有效白名单位置数字码，unclassified；HTTPS URLError，无HTTP响应；安全日志2条 |
| 探针请求 | 固定http://api.weixin.qq.com/cgi-bin/message/subscribe/send，POST {}，无身份/模板/正文，每进程一次 |
| 032运行 | normal/0%，1个Running实例；未额外调用StartVersionInstance |
| 清理复核 | 16:39 CST官方API确认032不存在；原020—026及031全部保留，031 normal/100% |
| 最终资源复核 | 16:58 CST033不存在，管理任务2383674 stopped；旧032任务2383541也已stopped；全部原版本保留 |
| 配置比较 | 服务各字段按语义摘要核对，changedServiceFields=[]；031冻结配置摘要相同；PUBLIC关闭 |
| 管理员修复前截图 | prod云调用总开关开启，微信令牌权限列表为空；必要发送路径未配置 |
| 管理员修复后截图 | 唯一精确路径/cgi-bin/message/subscribe/send已列出，总开关仍开启 |
| 配置后官方只读复核 | 031 normal/100%、PUBLIC关闭，仅020—026与031，无新版本 |
| -05真实日程提醒 | 0F58，创建201/匹配1；当前账号sent/ok，sent_at=2026-10-17T10:49:19Z，额度1→0/expired |
| -05实际微信收件 | 用户2026-10-17在call_5b80efd7f9504c4ca286e2df7e031c75明确答复“已收到”，与唯一0F58测试对应；未采集精确收件时间 |
| -05清理和最终复核 | 仅本次日程DELETE 204，当日匹配0；031 normal/100%，productionConfigUnchanged=true，changedServiceFields=[]，原版本保留、033及任务仍已清理 |

HTTP502是新探针的实测值。旧30条日志只有异常类，不能宣称旧30次每次都是502。
-01至-04无真实通知或授权额度写入；后续-05只用既有family-scoped API创建/停用1条测试日程，成功投递正常消耗授权。全程不调用全局dispatch、不直连数据库、不重置旧失败或伪造额度。

## 结论与未确认项

现有provider捕获HTTPError（URLError子类），统一返回retry/transport_error；最多三次尝试后落failed。
隔离程序不加载业务代码、接收人或模板，同一路径仍收到502，复现HTTPError这一失败类型。
502表明本次微信HTTP调用链返回网关错误；探针阶段没有得到更深数字码。
032仅提取顶层整数errcode，null表示“未提取到”，不表示响应没有其他错误字段或平台没有返回错误。
未取得85107；管理员修复前截图已独立确认接口权限为空，不依赖该错误码推断。-01至-03本身不授权改权限；后续-04明确批准的单接口权限现已配置，仍不允许重置失败记录。
后续033已扩展六处数字字段及精确格式归类，HTTP仍502且unclassified；条件HTTPS对照为URLError，未得到HTTP响应。
不能由URLError断言DNS、TLS或某一种具体连接原因。21条同版本可读日志的固定格式计数均0，也不能证明平台配置正确或没有代理错误。
管理员前后截图确认必要权限缺口并按-04修复；-05又验证相同生产provider下的单条日程提醒sent/ok，用户随后确认微信已收到。必要配置阻断已消除，当前账号本次日程发送及收件闭环；不能声称历史所有失败均已完全归因，其他成员/类型仍需分别验收。

官方[TCloudBase订阅消息示例](https://github.com/TCloudBase/wxcloudrun-wxapp-subscribe)要求开放接口服务及
/cgi-bin/message/subscribe/send白名单。结合修复前空列表截图，确认此前存在必要接口权限缺口；新截图确认该路径现已配置。
服务端accepted与额度1本身不等于微信已接受发送；本次证据是原provider写入sent/ok及授权消耗，加上用户针对唯一0F58明确确认微信收件，不是配置状态推断。

## -05单条真实日程投递验收

- 审批：2026-10-17，call_5c6ba23a5eed4910bb493dabb8aa6dd2，用户明确回复“批准 Spec-05，允许家庭范围测试”；批准既有家庭3名成员中符合订阅条件者接收，不伪称仅本人。
- 本机开发者工具连接断开时未发送创建请求；官方CLI恢复后，首次账号上下文未同步被守卫拦截，仍无业务写入。通过既有只读bootstrap同步身份后继续同一测试标识/幂等key，未创建第二条记录。
- 执行前me/members/children/settings均200；bound、写权限、目标AppID/env/service、当前所选档案及家庭上下文一致；成员3，当前账号日程额度1，accepted，channel可用，完整唯一标识可见，旧日程/投递匹配0。
- 合成日程名仅“通知测试0F58”，2026-10-17 19:05—19:10 CST，kind=other、repeat_weekly=false。仅1次POST创建201，随后当日日程精确匹配1；幂等key及本次event_id仅在临时恢复状态中，不记录身份或原始响应。
- 由既有调度自然处理；第1轮（间隔30秒）匹配当前账号唯一schedule_reminder，state=sent、result_code=ok、scheduled_at=2026-10-17T10:49:18Z、sent_at=2026-10-17T10:49:19Z（18:49:19 CST）。当前账号日程remaining_quota由1变0、subscription_status=expired，未伪造或恢复授权。
- 既有031使用WeChatSubscribeSender；该结果代表微信发送接口返回成功业务码。本次API不暴露其他家庭成员投递结果，未声称其发送数量或成功。用户随后于2026-10-17在call_5b80efd7f9504c4ca286e2df7e031c75针对“通知测试0F58”答复“已收到”，该次手机实际收件验证通过；未采集精确收件时间，不把服务端sent_at当成手机收件时间。
- 终态后仅对本次event_id执行DELETE，返回204；再查该档案当日日程，ID/合成名匹配数0。该操作为active=false软停用，不物理抹除审计，不保证撤回已入队或在途通知。
- 最终官方只读status：031 normal/100%、productionConfigUnchanged=true、changedServiceFields=[]、onlyApprovedServiceChanges=true、existingVersionsPreserved=true、033不存在、其GRAY任务2383674仍stopped。PUBLIC关闭由本轮创建前官方preflight及未变配置交叉核验。
- 未改生产代码、测试、依赖、Schema、权限、偏好、流量或版本；未调用全局dispatch、重发旧通知或新建第二条测试。完整Python/npm/容器回归本轮N/A，未重跑，旧-03结果保持历史归属。
- 文档闭环覆盖FEAT-003、FEAT-001临时日程验收、运维说明、证据、发布记录、Spec/索引；Behavior/Architecture/UI合同及批准快照未变。最终文档链接/diff检查结果见Spec-05 S-006。
- -01/-02/-03经复核原诊断执行/清理门禁通过，必要权限缺口已确认、-04修复后由-05补齐原链路成功受理及用户实际收件证据，诊断任务DONE归档。旧30次精确状态/平台代理内部码不可回溯的限制保留，不以其未知为由宣称所有旧失败已完全解释；单次收件成功不推广为全成员/类型或长期可靠性保证。

## 管理员只读截图证据

- 用户于2026-10-17在本会话提供`codex-clipboard-54bcc71c-2aa2-4197-bbbb-160a11f1581e.png`。
- SHA-256：`442f03999a500e3a76404d014f76ff7bd0fb6ee5c021992f6d0f15da6bf6f0e1`；仅记录去敏配置事实，未复制图片至仓库。
- 画面为环境prod、服务管理/云调用；总开关为绿色开启，接口表显示暂无API接口。
- 代码固定发送路径与官方前提已交叉核对；此处没有从截图推断平台数字码或过去权限状态。
- [单接口修复Spec-04](../../../specs/completed/OPS-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX.md)已于2026-10-17获用户明确批准（call_2314cfc8076f40f88ec0cb8d595c6134）。用户随后完成配置，提供`codex-clipboard-444b0e3b-5527-4e65-a1a2-eeabda462b5a.png`，画面显示唯一精确发送路径及绿色开启开关。
- 修复后截图SHA-256：`280a7ff5267554272dd88c437f2498e6a6769a43c4688b3fa53d0efe9174b4f0`；仅记录去敏事实，未复制图片至仓库。
- -04配置前后官方只读preflight通过：031 normal/100%、PUBLIC关闭，仅020—026与031，无新版本；-04阶段本代理未重新部署或发送通知，真实单条测试由后续独立获批-05执行。
- 配置后status在内存比较冻结基线：changedServiceFields=[]、productionConfigUnchanged=true、所有原版本保留、033不存在且任务2383674 stopped；不输出配置值。
- -04结束时-01/-02/-03因修复后验证缺失保持BLOCKED；现已由后续获批-05取得原业务链路sent/ok，达到诊断闭环门禁后DONE归档。未取得的旧平台代理内部码仍如实列为限制。
- -04配置阶段没有新增代码、测试或依赖变更，未重跑Python/npm回归；下述581/19 skipped等属于先前-03工具变更的实际执行证据，不能冒充-04/-05重跑。配置阶段文档闭环检查结果在配置Spec中单列。
- 配置Spec已通过F-001至F-005，DONE并移至completed；-04阶段9份文档54个本地链接存在、无尾随空白、git diff --check通过。后续-05最终检查11份文档76个本地链接全部存在、无尾随空白、diff及Spec迁移检查通过；通知相关Feature/Behavior/Architecture/UI及发布合同无本轮新增冲突。

## -02实际发布与清理

- 用户批准：2026-10-17“批准-02，按该方案部署并排查（推荐）”，审批问题call_facaedb2b45c480ebfa2134f1423fe05。
- 16:35:40 CST官方上传HTTP200；PackageName=flask-ik19.zip，PackageVersion=1792226140。
- SubmitServerRelease：package/GRAY、8000、Dockerfile=Dockerfile、BuildDir=.；任务2383541。
- 新版本flask-ik19-032，备注OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS-02。
- 032达到normal/0%，包标识匹配，CPU0.25/Mem0.5/min0/max5；继承环境与服务基线的内存摘要匹配。
- 平台版本配置临时继承既有环境；env -i后探针仅接收两个Python标志，未读取或输出业务变量值。
- tcbr/2022-02-17/SearchClsLog取得1条安全结果。CLS Content需解析嵌套结构；提取器只输出数字码/固定枚举，原始日志不落盘。
- 16:39 CST调用DeleteCloudRunVersions，只选032，IsDeleteServer=false、IsDeleteImage=false；随后确认032已消失。
- 取码前后及清理后均确认031 normal/100%、原版本保留、入口与环境等受保护配置不变。
- 未重新下载远端包验哈希；本地摘要+上传200+版本包标识匹配不能写成远端字节哈希验证。

## -02冻结发布物与本次检查

- 目录：/private/tmp/push-kids-notification-probe-20261017-02，仅Dockerfile/probe.py/manifest.json。
- ZIP：/private/tmp/push-kids-notification-probe-20261017-02.zip，2495 bytes。
- ZIP SHA-256：619717eb41aee87c524c7ce0afbff51990131073dc75340ba66bffd79feb544b。
- Dockerfile SHA-256：be52b22809e9a710d45ab25c0a5cbe83b871d5170be4a6b1a82d4f5db3b41588。
- probe.py SHA-256：861dd521bc4db233bf0c14681d4a329f57a1dacba05160e97582c7dbd331c798，冻结时与当时仓库源码及-01逐字节相同；当前工具已依获批-03更新，不能再宣称当前源码与-02相同。
- 本地镜像：sha256:a14fcd45a99a76e833cdd3a56eeb7770e8796be00ad86ef99bf042359dba6abf；不等同于云构建镜像摘要。
- CMD：/usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 /usr/local/bin/python /app/probe.py。

| 检查 | -02本次实际结果 |
|---|---|
| 白名单、manifest/ZIP逐文件哈希、源码一致性、秘密格式扫描 | PASS |
| .venv/bin/pytest tests/unit/test_notification_gateway_probe.py -q | 21 passed/1 warning，0.03s；已有Starlette弃用警告 |
| 专项Ruff check、format --check --no-cache | PASS，2文件 |
| tools/check_architecture.py | PASS，ARCHITECTURE_VALID checked=3 |
| Docker构建，network=none | PASS，python:3.12-slim，UID10001 |
| 断网/只读/cap-drop容器，注入虚构变量 | PASS，PID1初始环境仅两个Python标志，虚构变量清除，/app只有probe.py |
| live/ready各两次、未知路径、探针日志计数 | 4次200、404、日志1条；健康不重发 |
| SIGTERM、本地测试容器清理 | exit0、非OOM，仅本轮测试容器已删除 |
| 云版本/日志/清理/配置不变量 | PASS，实测502，无整数errcode；更深根因未确认 |
| 全仓后端、npm、Mypy、前端静态门禁 | -02未重跑；probe源码未改，既有-01结果见下，不能冒充本次执行 |
| Schema/新MySQL空库/迁移/新增备份/双账号业务验收 | N/A，无业务/数据库依赖或数据写入 |
| 原生三视口/真机授权/前端上传提审 | N/A，无前端变化；不替代既有未验收项 |
| uv sync/npm install | NOT_RUN，依赖声明和锁未改，使用现有依赖 |

宿主Docker曾EOF且重启超时；安全分类检查发现后台no space left on device，宿主仅约125MiB空闲。
删除可再生.mypy_cache约36MB及322个旧npm内容缓存约2GiB后，空闲约2.2GiB，Docker29.1.2恢复并通过上表验收。
只停止和重启已核实路径的卡住Docker进程；没有清空已有Docker镜像、容器、卷或业务文件。

## -01历史检查和阻塞经过

- 专项21 passed；完整Python539 passed/19 skipped/62 warnings，跳过项为未配置隔离MySQL或依赖MySQL隔离级别的用例。
- Ruff/format通过（525文件），Mypy通过（103文件），npm244 passed，miniapp lint、架构、设计证据政策与validator通过（16页/1070913源字节）。
- 原2400字节ZIP SHA-256 fd3eb342ed9a32a3b9b4698840cdc65f2a36cc3cca2aff2c83906439d2fc68ea；原冻结目录与包未改。
- 原Dockerfile SHA-256 2e59abd2c8fae7836c10b350675cfac7f3aebec8c9e738e4e41b814ee195531e；原本地镜像sha256:5c5b87f838d3b27637e8fd8dd618c692e2657ac6ffadd9d4c3c79aac2bcdc215，断网健康与exit0通过。
- 旧CreateCloudBaseRunServerVersion反复拒绝InvalidParameter/package detail param is missing；按官方cloudapi补AccessType=4仍未创建版本。
- 11:17:26及16:20:36 CST原包再次上传均HTTP200，包版本1792207046及1792225235；这些上传没有启动探针。
- 16:07复核为原8个版本、30条HTTPError、探针日志0；当时具体状态码确实未知。
- 腾讯云[公开接口更新记录](https://cloud.tencent.com/document/product/876/34816)列出2026-03-02移除旧创建接口；不能由此推定本次内部参数报错原因。
- 明确批准-02继承例外后，官方现有GRAY链路创建032；旧“无新版本/等待人工创建”已不是当前状态。
- 旧tcb/2018日志API返回TopicNotExist，tcbr/2022可用。OpenAccessTypes按集合比较，避免顺序变化误判。

## 文档与生命周期

已合并FEAT-003、运维说明、发布记录及Spec索引的部署/502/清理事实，替换过期当前正文。
核对本轮diff：无业务API、Schema、授权、重试、通知状态或UI合同变化；通知Behavior、Architecture、UI-011、FDB/FEC及批准快照不改。
部署取码与清理完成；后续截图确认必要权限缺口，-04完成单路径修复，-05补齐当前账号单次sent/ok、测试日程清理及用户确认手机收件证据。-01/-02/-03及-05已DONE归档；不推广为全部成员或全部通知类型通过。
8份相关文档的本地链接及git diff --check通过；无本轮通知合同冲突。
[细化诊断-03](../../../specs/completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md)已获批并执行、取码与清理，见下节；后续配置和单条验收及其边界见上节。

## -03批准、本地验收和最终云端结果

用户于2026-10-17回复“批准-03，继续细化排查（推荐）”，问题call_c72df312de1446299ccfe9fc496ad2e6。
在实现前记录APPROVED；仅修改独立诊断工具和测试，未改业务应用。
新增固定位置32位数字码、精确错误格式静态归类；仅HTTP502且unclassified时再发一次同路径HTTPS空请求。
原文在进程内存处理后丢弃；输出只保留批准的数字/固定枚举。

| 检查 | 本次结果 |
|---|---|
| 专项pytest | 63 passed/1 warning，0.11s；保留原21项并扩展字段/格式/隐私/条件对照 |
| 完整后端pytest | 581 passed/19 skipped/62 warnings，47.16s；19项为可选隔离MySQL/隔离级别依赖 |
| npm test | 244 passed/0 skipped |
| 全仓Ruff check/format | PASS，529文件format检查 |
| Mypy | PASS，103 source files，缓存放临时目录 |
| 架构/miniapp lint/validator/设计证据政策 | PASS；ARCHITECTURE_VALID checked=3；16页/1070913源字节；DESIGN_EVIDENCE_VALID |
| 白名单/ZIP摘要/逐文件manifest/秘密格式扫描 | PASS；源码与冻结probe.py逐字节相同 |
| 断网只读非root容器 | PASS；UID10001、PID1仅两个Python标志、虚构变量清除、/app只有probe.py |
| 健康/日志/SIGTERM/本地清理 | 4次200、未知404、断网日志1条、exit0/非OOM；测试容器已删除 |
| uv sync/npm install | NOT_RUN，未改依赖声明/锁，使用已有依赖 |
| Schema/迁移/新增备份/双账号业务/原生视口/前端发布门禁 | N/A，独立诊断无对应业务变更，不替代原有验收 |
| 真实通知/成功送达/生产Schema读取 | NOT_RUN，本轮明确不执行；不得声称已修复 |

- 新冻结目录/private/tmp/push-kids-notification-probe-20261017-03；仅Dockerfile/probe.py/manifest.json，旧-01/-02包未改。
- ZIP3729 bytes；SHA-256 cdcf4b484ac398d9e6839016c392ab0a92c8b739e8f4ba9b75b193c32931a7f1。
- probe.py SHA-256 83d89a097d13f0aa5d7a7b1713de97ce331a6b4370e1f2ab819eb4f348b01fb1。
- Dockerfile SHA-256 be52b22809e9a710d45ab25c0a5cbe83b871d5170be4a6b1a82d4f5db3b41588，与-02启动隔离合同相同。
- 本地镜像sha256:d57cabaa8153fcccb28776bf2b5920348b08d3cf142efb8add3a2d9949e3070b，不冒充云构建摘要。
- 官方上传HTTP200，flask-ik19.zip/1792227155；首个SubmitServerRelease返回ResourceInUse，无新-03版本。
- 只读确认旧032版本虽已删除，其GRAY管理任务2383541仍running；仅取消该已删除诊断版本的任务，确认stopped，前后031及配置不变。
- 确认本次版本不存在后，同一上传包重提一次成功；任务2383674，033由creating达到normal/0%，包标识及继承摘要相符。
- 033云内HTTP：502/HTTPError/json_object，error_codes=[]、platform_errcode=null、category=unclassified。
- 按条件执行HTTPS一次：URLError/transport_unavailable，无HTTP响应、数字码或可归因类别；不是成功调用微信接口。
- 同版本窄窗口CLS返回21条、未触及100条上限，只在内存扫描既定网关错误格式并输出类别计数；上游拒连/超时/白名单/令牌均0，不将未命中当作排除证据。
- 16:58 CST仅删除033（IsDeleteServer=false、IsDeleteImage=false），随后确认原版本保留、033不存在。
- 为避免再次遗留发布占用，在确认033已删除后仅取消其仍running的GRAY管理任务2383674，最终状态stopped；没有取消业务版本任务。
- 最终031 normal/100%、PUBLIC关闭、全部原版本保留、changedServiceFields=[]、031冻结摘要不变。
- 调试执行与资源清理已完成；-04完成单路径权限配置及只读版本核验，后续-05补齐当前账号单条sent/ok、临时日程停用和用户确认微信收件证据；旧平台代理码及全成员/类型未代验，无待批准的额外诊断包。
