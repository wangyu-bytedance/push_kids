# 2026-10-17 通知 HTTP 隔离诊断发布记录

- Status：DIAGNOSTICS_AND_TASKS_CLEANED / REQUIRED_OPENAPI_PERMISSION_CONFIGURED / SINGLE_SCHEDULE_DELIVERY_SENT_OK / TEST_EVENT_DISABLED / DEVICE_RECEIPT_CONFIRMED。
- Specs：[诊断-01](../../../specs/completed/OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS.md)、[灰度-02](../../../specs/completed/OPS-20261017-NOTIFICATION-GRAY-DEBUG-DEPLOYMENT.md)、[细化-03](../../../specs/completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md)、[单条验收-05](../../../specs/completed/OPS-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE.md)，均获用户明确批准并完成；权限配置另由-04批准。
- Source：8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a + 未提交诊断工具、测试、Spec及事实文档；业务源码未改。
- Target：wx5d2e0014690bf285 / prod-d2g14rwoycac6b45d / flask-ik19 / 8000。
- Production：031始终normal/100%；本轮没有流量写操作，PUBLIC关闭。
- Schema before/after：未查询或修改生产Schema；探针无数据库/业务依赖，不借历史migration证据声称本次通过。
- Frontend：未构建、上传、设体验版、提审或正式发布。

## 历史-02发布物与本地门禁

- -02白名单目录/private/tmp/push-kids-notification-probe-20261017-02，仅Dockerfile/probe.py/manifest.json。
- ZIP2495 bytes，SHA-256 619717eb41aee87c524c7ce0afbff51990131073dc75340ba66bffd79feb544b。
- probe.py与-01逐字节相同；CMD用env -i清空环境，平台继承例外由-02单独明确批准。
- 本地镜像sha256:a14fcd45a99a76e833cdd3a56eeb7770e8796be00ad86ef99bf042359dba6abf。
- 本次专项21 passed/1 warning、Ruff check/format、架构、白名单/哈希/秘密格式扫描通过。
- 断网只读非root容器：PID1仅两个Python标志，虚构变量清除，健康4次200、未知404、日志1条，SIGTERM exit0，测试容器已清理。
- -01既有完整后端539/19 skipped、前端244及静态门禁不冒充-02重跑结果，详见[完整证据](../../quality/evidence/NOTIFICATION-HTTP-DIAGNOSIS-20261017.md)。
- 磁盘不足曾令Docker EOF；清理可再生mypy及约2GiB旧npm缓存、重启卡住Docker后通过容器验收；未清空Docker数据。
- Schema/新备份/双账号业务及UI验收N/A；依赖声明/锁未改，依赖安装NOT_RUN。

## 历史-02云端阶段（已结束）

1. 16:35:40 CST官方上传HTTP200，flask-ik19.zip / 1792226140，字节数/本地摘要与冻结记录一致。
2. SubmitServerRelease，package/GRAY，任务2383541；创建flask-ik19-032，备注OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS-02。
3. 032达到normal/0%，CPU0.25/Mem0.5/min0/max5、8000端口，包标识与继承环境摘要核验一致。
4. 官方API查得1个Running实例，未额外请求启动。平台运行状态不等于业务验收。
5. tcbr/2022-02-17/SearchClsLog读得1条安全日志：HTTP502、platform_errcode=null、HTTPError、reason=http_error。
6. 16:39 CST仅删除032（不删服务/镜像）；随后确认032消失、原020—026与031均保留。
7. 每阶段核对031 normal/100%、冻结配置摘要一致、服务changedServiceFields=[]；未改入口、资源、变量或权限。

未保存原始响应/日志、签名URL、业务变量值、OpenID或消息正文。远端包未重新下载验哈希，云构建镜像摘要未单独查询。
无业务请求、真实通知、dispatch、历史失败行/授权额度写入；业务smoke及成功送达NOT_RUN，无业务切流或回滚。
032清理完成；031继续承载业务，020—026保留。

## -03发布物、实际云端结果和最终清理

- 用户批准-03后修改独立工具及测试；业务源码与Schema未改。新冻结目录/private/tmp/push-kids-notification-probe-20261017-03，仅三文件。
- ZIP3729 bytes，SHA-256 cdcf4b484ac398d9e6839016c392ab0a92c8b739e8f4ba9b75b193c32931a7f1。
- probe.py SHA-256 83d89a097d13f0aa5d7a7b1713de97ce331a6b4370e1f2ab819eb4f348b01fb1；Dockerfile仍为env -i隔离启动。
- 本地镜像sha256:d57cabaa8153fcccb28776bf2b5920348b08d3cf142efb8add3a2d9949e3070b；不冒充云构建镜像摘要。
- 本次专项63 passed/1 warning，完整后端581 passed/19 skipped/62 warnings，npm244 passed；Ruff check/format529、Mypy103、架构、miniapp lint/validator及设计政策通过。
- 断网/只读/非root/env -i容器健康、一次断网日志、SIGTERM exit0及测试容器清理通过；19项可选MySQL跳过理由见完整证据。
- 16:52:35 CST上传HTTP200，flask-ik19.zip/1792227155；第一次提交ResourceInUse，无新版本。
- 核实旧032已删除而管理任务2383541仍running；仅取消该诊断任务，确认stopped，031与配置未变。随后同一上传包重提一次成功：任务2383674。
- 033达到normal/0%，8000、CPU0.25/Mem0.5/min0/max5，包标识/继承环境摘要匹配；不改服务环境或流量。
- 云内HTTP空请求：502/HTTPError/json_object，无批准位置有效数字码、category=unclassified。
- 条件HTTPS空请求执行一次：URLError/transport_unavailable，无HTTP响应或可归因错误码。只取得两条安全探针日志，没有第三次请求或真实消息。
- 033窄窗口日志21条未触及100条上限，固定网关错误格式计数均0；不据此排除权限/白名单/代理或上游原因。
- 16:58 CST删除仅033，复核其不存在；随后只取消已删除033的仍running管理任务2383674，确认stopped。
- 最终020—026与031全部保留，032/033均不存在，031 normal/100%，PUBLIC关闭，changedServiceFields=[]、031冻结摘要不变。
- 依赖安装NOT_RUN（声明/锁未改），Schema/新增备份及前端门禁N/A；真实通知、成功送达及生产Schema读取NOT_RUN。

## 结论与剩余门禁

已复现HTTPError，实测502；现有provider将该异常记为transport_error，最多三次后failed。
旧30次没有状态码，不能断言全为502。033细化解析仍未得到有效数字码或类别，HTTPS对照为URLError，不能断言DNS/TLS或某一种网络原因。
调试包已部署、取码并清理，关联灰度任务也已停止。
用户提供的prod修复前截图确认总开关开启、微信令牌权限列表为空，缺少`/cgi-bin/message/subscribe/send`必要权限。
官方前提与源码路径已核对，见[截图证据](../../quality/evidence/NOTIFICATION-HTTP-DIAGNOSIS-20261017.md#管理员只读截图证据)。
管理员按获批-04补齐唯一精确路径后，新截图显示该项且总开关仍开；配置后官方只读API确认031 normal/100%、PUBLIC关闭、无新版本，服务字段/031受保护摘要不变。
配置缺口已修复并验收；独立获批-05又取得原031当前账号单条日程提醒sent/ok及测试日程清理证据，说明该次发送已被微信成功受理。
用户随后明确确认微信已收到该条0F58，当前账号本次日程发送到收件验证完成；其他成员/通知类型未逐一验收，不能断言所有旧失败均为502、完全归因或已排除其他历史问题。

历史package detail阻塞和“需要人工创建诊断版本”已由获批-02解决，该人工创建门禁失效。
不再要求操作者重复创建032/033。-03已明确获批并执行，不存在待批准的-03包；不继续盲目发布同样探针。
控制台访问仍受站点安全门禁限制，不用替代浏览器/CDP/WebShell绕过。

## 人工核查门禁

本配置门禁已完成，无需重复操作。修复前截图显示路径缺失，修复后截图显示唯一精确路径及开启开关；来源与SHA-256见质量证据。
原要求查看033历史平台代理数字码的检查仍未取得，但不再阻塞识别已确认的配置缺口。
用户2026-10-17明确批准[Spec-04](../../../specs/completed/OPS-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX.md)及架构（call_2314cfc8076f40f88ec0cb8d595c6134），随后在[云调用控制台](https://cloud.weixin.qq.com/cloudrun/openapi)完成单路径配置；没有要求第二次审批。
配置前后官方只读复核：031 normal/100%、PUBLIC关闭，仅原020—026与031；配置后status比较changedServiceFields=[]、productionConfigUnchanged=true，诊断版本不存在、其任务stopped。
-04配置阶段未发包、重启、切流、主动发送或补发，也未改历史失败/授权；后续真实单条验收以独立获批-05为准，见下节。

## -05单条真实日程验收（无新增部署）

- 2026-10-17用户明确批准Spec-05及家庭范围（call_5c6ba23a5eed4910bb493dabb8aa6dd2），允许当前家庭3名成员中符合订阅条件者接收并正常消耗授权。
- 官方开发者工具CLI恢复本机连接；创建前只读bootstrap及4个接口均通过，当前账号日程额度1/accepted、通道可用，目标环境及家庭/档案一致，唯一合成标识可识别且旧匹配0。
- 仅1次POST创建“通知测试0F58”（19:05—19:10 CST，非重复，201），当日日程匹配1；由原调度自然处理，不调用全局dispatch。
- 第1轮30秒有界观察匹配当前账号唯一schedule_reminder：sent/ok，scheduled_at=2026-10-17T10:49:18Z，sent_at=2026-10-17T10:49:19Z（18:49:19 CST）。额度1→0，订阅expired，未伪造再次授权或补偿额度。
- 终态后仅停用本次event_id，DELETE 204；再查当日日程ID/合成名称匹配0。为软停用，不承诺物理删除审计或撤回在途通知；未查询全部家庭成员结果。
- 最终官方status确认031 normal/100%、productionConfigUnchanged=true、changedServiceFields=[]，原版本保留、033不存在、其GRAY任务仍stopped；PUBLIC关闭。无部署、重启、流量/权限/配置/Schema/偏好变更或旧失败补发。
- 本轮不改生产源码/测试/依赖，完整Python/npm/构建/迁移/备份及前端发布门禁N/A，未以旧-03结果冒充重跑。用户于2026-10-17在call_5b80efd7f9504c4ca286e2df7e031c75明确确认“已收到”0F58；精确手机收件时间未采集。
- 这是一条日程及当前账号一次成功受理证据，不能推广为全家庭、全部模板或长期可靠性；后续日程发送需要重新取得一次性授权。

## 文档闭环

已同步FEAT-003、运维说明、完整证据、-01/-02/-03与Spec索引；单接口配置修改及验收由获批-04涵盖，不扩大原诊断Spec范围。
核对本次diff与通知Behavior/Architecture/UI合同无新增冲突，批准设计快照未改。
-01/-02/-03原部署/安全诊断/清理检查通过，必要权限缺口经-04修复，-05补齐原链路单条成功与临时日程清理证据；诊断Spec复核完成条件后DONE迁至specs/completed/，保留旧30次精确状态/内部码无法回溯的限制。
-04配置与-05单条运行验收均DONE于specs/completed/；索引及引用同步。当前账号本次实际微信收件已由用户确认，其他成员/类型验收缺口保留在Feature中，不要求重做配置或重复发送。
