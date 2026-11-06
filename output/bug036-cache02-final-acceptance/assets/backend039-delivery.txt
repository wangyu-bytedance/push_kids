# 2026-10-31 — BUG-035兼容后端交付（当日发布证据）

以下状态限定2026-10-31记录时。最新2026-11-01只读确认039 normal/100%/1、PUBLIC关闭，
038未在最新列表；本人登录、039微信健康与42组原生通过，用户已确认正向focus/分页/双真实家庭非owner门禁，
0.1.17官方上传1,191,019字节并bump成功。后续以[上传记录](20261101-client-0.1.17-upload.md)为准，
不继续执行下方已过时的0%灰度、登录或上传前验收门禁。

- Actual stage: `BACKEND_039_NORMAL_0_PERCENT / DIRECTED_SMOKE_PENDING / FRONTEND_PREVIEW_ONLY / UPLOAD_BLOCKED`。
- Current evidence: 用户“批准测试维护 Spec01”后，仅维护原集成测试，精确核验`t/merge/review0`身份、重试复用与清理。[测试Spec01](../../../specs/completed/OPS-20261031-RELEASE-STAGE-CACHE-TEST-MAINTENANCE.md)已DONE归档，测试不进入生产payload；[Review01](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/review01.md)0确认发现。下述为批准后最终事实，早期失败保留在[历史续接](20261031-client-release-resume.md)及原始日志。
- Authorization: 用户于2026-10-31本对话明确“后端也已经授权”；前端上传授权为此前“当前效果OK 上传前端准备发布”。
- Scope: 已批准BUG-035的`footprints/reads.py`、`router.py`；在已部署038源码上增加有界照片焦点和双向分页合同。当前其他agent_processing改动不进入本候选。
- Commit: `0576ac30464908154c624effed41df6dfa3110cc`及已记录的两份工作区文件。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`；服务`flask-ik19`；端口8000；GRAY。
- Frozen payload: `dist/client-release-20261031-0.1.17/backend-compatibility-candidate`；154份payload，1523469字节；准备manifest SHA-256 `50a2ea9846fdfe9da13a5ae5b1b7f3ddd0e312d7f72b1961d5c2531060469c62`。本次重新逐项核对摘要，无多余文件。
- Current control plane: 039于2026-10-31 19:15:02创建，19:18:08达到normal；当次实例查询039 **0% / 1副本**、038 **100% / 1副本**。19:57[再次只读核对](../../quality/evidence/client-release-20261031/backend-authorized/cloud-control-pre-upload02.json)两版本仍normal，流量分别0%/100%，未重查实例数。PUBLIC关闭及实际MINIAPP/OA见本轮[完整控制平面](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/cloud-control-flask-ik19-039.json)；本次未改入口配置或切流。037未在列表中，不称为当前可用回退版本。
- Schema: `20261024_0025`不变；管理员严格只读核验PASS。19:24独立使用平台配置中的039实际应用账号，经既有批准数据库入口完成`verify_cloud_schema()`、`check_ready()`和无DDL权限校验，均PASS；这与管理员检查分别留证。早期内部地址OperationalError保留为历史环境失败。无迁移/生产数据写入，新增备份门禁NOT_APPLICABLE。
- Runtime configuration: [038/039配置只读对比](../../quality/evidence/client-release-20261031/backend-authorized/cloud-runtime-parity.json)显示MYSQL、Ark与HMAC配置存在且一致，只保存比较结果。平台当前资源为0.25 CPU / 0.5 GiB / min0 / max5，与后端手册0.5 CPU / 1 GiB / min1 / max1基线不同；本次未调整资源，该差异留待管理员后续发布复核，不将其记为基线一致。

## 当前检查与上传通道

| 检查 | 结果 |
|---|---|
| 精确冻结payload与源清单/秘密扫描 | PASS；154后端/168前端SHA匹配，后端只有两份批准差异，未混入BUG-036 |
| 原staged实库测试 | 修订前FAIL_BASELINE；批准后两轮均2 PASS，最终Ruff/format PASS |
| 精确候选完整后端 | PASS；最终789 passed / 46条件skip；实库另验，不隐去skip |
| 独立MySQL5.7 | PASS；10模块各自独立utf8mb4库；公平复习13 PASS / 1 SQLite参数skip |
| 五万照片规模 | PASS；最终5项，原500ms/响应/内存/查询预算不变；首次0.521s失败保留 |
| 候选Ruff/format/mypy | PASS；本日同150份精确源已运行，SHA未变；测试修订另验Ruff/format |
| 生产Schema | PASS_ADMIN_STRICT；0025，实际应用账号独立核验见下项 |
| 容器/dry-run | PASS；源与镜像匹配，UID10001、端口8000、live/ready200、SIGTERM0；本地test/SQLite，不能代云smoke |
| 实际039应用账号Schema复验 | PASS_RUNTIME_READONLY；19:24使用039平台实际账号，经既有批准入口通过Schema0025、数据库ready和无DDL权限检查；不代真实AppID定向HTTP |
| 部署 | PASS_DELIVERY；官方CLI提交exit0，039 normal / 0% / 1；没有全量切流 |
| 真实微信live/ready | PASS_EXISTING_SERVICE_ONLY；部署前200/89ms与200/88ms，既有路由；039定向检查NOT_RUN |
| 官方微信登录/preview | PASS；HTTP V2登录与preview独立通过，0.1.17编译1,191,019字节；此前CLI成功与本代理CLI缓存EPERM分别保留，没有upload/bump，基准仍0.1.16 |
| 前端完整/静态/设计/架构 | PASS；349项、17页、4 policies/151 modules；批准设计资产不变 |
| 入口原生 | PASS_LOCAL_NATIVE_PARTIAL；320×568独立Page和记录Tab内嵌各7态，14组节点/PNG；390/430、完整动作/设备/可访问性未验 |
| 039定向focus/前后分页、双账号/非owner | NOT_RUN；旧0.1.16验收不覆盖新focus合同 |
| upload/体验/审核/正式发布 | NOT_RUN |

完整最终测试与逐项skip在[第二轮](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/round02/)；
部署[确认](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/deployment-confirmation.json)、
[提交](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/deploy-submission.json)及normal查询分别保存。
实际账号[当前探针](../../quality/evidence/client-release-20261031/backend-authorized/cloud-readonly-flask-ik19-039.json)通过；[较早内部地址探针](../../quality/evidence/client-release-20261031/backend-authorized/test-maintenance01/runtime039-schema.json)仍保留OperationalError，不覆盖历史结果。两者没有输出或保存秘密。
官方HTTP V2 [preview回执](../../quality/evidence/client-release-20261031/backend-authorized/http-preview-attempt02.json)校验PNG签名与168份源，首次二进制响应解析失败另行保留。
原生[双宿主源码与输出摘要](../../quality/evidence/client-release-20261031/native-approved-source.json)仅绑定禁云合成副本。

部署前038实际CRUD账号与部署后039实际CRUD账号均有独立Schema/数据库ready/无DDL只读PASS；039 normal和这些数据库检查不能代真实微信定向健康或云业务smoke。
在完成新版本定向验证前保持0%，不上传依赖focus合同的前端。旧CLI EPERM及实库/格式/规模失败均保留为历史。

## 后续人工门禁与恢复条件

```text
【需要人工操作】配置039灰度测试账号
原因：039当前0%流量，定向业务验证需要管理员在云控制台配置测试用户；按既有发布手册保留平台人工门禁。
操作入口：https://cloud.weixin.qq.com/cloudrun/service/flask-ik19
导航路径：prod-d2g14rwoycac6b45d → 云托管 → flask-ik19 → 版本/流量管理 → flask-ik19-039 → 灰度测试用户
需要填写/选择：
- 在平台内选两个不同家庭的真实微信测试账号定向039，身份信息只在平台配置。
- 039普通流量0%、038保持100%，PUBLIC关闭，端口8000与Schema0025不变。
完成标志：039 normal，测试用户规则保存成功，普通流量比例未变。
完成后回复：已完成配置039灰度测试账号
```

依据[发布手册人工约定](../README.md)、[后端§7](../BACKEND-RELEASE.md#7-灰度验收与全量)和[前端§2](../FRONTEND-RELEASE.md)，管理员在
[服务控制台](https://cloud.weixin.qq.com/cloudrun/service/flask-ik19)将两个独立家庭测试微信账号定向039；
在平台内完成身份配置，聊天只回复完成状态。039普通流量保持0%、038保持100%，PUBLIC保持关闭。
成功标志为039测试用户规则保存且版本normal；随后核验真实AppID定向live/ready200、
focus照片精确打开/前后分页/旧cursor，以及跨家庭/非owner拒绝和灰度指标。
039应用账号Schema已有独立只读PASS；真实AppID定向039健康/focus/分页仍需独立执行，不能用数据库ready或038健康冒充。

入口390×844、430×932须在微信开发者工具真实切换模拟器尺寸，并为独立/内嵌两宿主各采7态节点/PNG：
empty、drafts、legacy、loading、error、viewer、archived。源码绑定、44px触控、无横溢和完整动作按原Spec验，
不得伪造systemInfo或使用HTML替代。当前桌面工具没有可用模拟器尺寸控件，此步骤需操作者协助；
实际设备/软键盘/读屏/大字按原矩阵记录，不把320或历史15/42组当作当前全验收。
已准备[参数化原生采集器与操作说明](../../quality/evidence/client-release-20261031/native-current-matrix.md)，支持两宿主、三个真实尺寸及指定automation端口。语法检查PASS；390预检在仍为320的真实模拟器上按预期停止，未生成390验收证据、未调用夹具或云业务。原320证据与原采集器保持不变。
所有适用上传门禁完成后，继续同冻结前端官方upload；仅成功才bump。全量、体验、提审、正式发布保留独立管理员门禁。

## 生命周期与后续条件

测试维护Spec DONE/completed；无运行时产物，全部TP已完成。BUG-035后端已由039交付、客户端未上传，
继续VERIFYING/active；导入精简、入口精简仅客户端增量，成功上传前继续VERIFYING/active。
同步FEAT-001/012、Behavior、Architecture、UI-001/018、设计索引、测试策略、三份旅行Spec及索引；
逐项删除旧“待批准/测试FAIL/后端未创建”的当前结论，历史正文注明时间范围。
当前正文已同步039实际应用账号PASS，并修正此前“仍未核验”的冲突；039定向与原生/设备验收缺口继续保留。未修改产品/API/架构合同或批准设计资产。
19:27阶段的路径、引用、源SHA和Spec计数见[原闭合检查](../../quality/evidence/client-release-20261031/approved-delivery-closure.json)。
当时19份文档/691本地链接、106 completed/13 active/13 rejected索引及154/168冻结源核对PASS；
架构4 policies/151 modules、current-policy设计和`git diff --check`均实际复验PASS，
见[最终静态检查](../../quality/evidence/client-release-20261031/approved-delivery-static-checks.json)。
本次运行账号正文纠正和采集器参数化的最新结果分别在[当前静态检查](../../quality/evidence/client-release-20261031/upload-preflight-static02.json)、[当前闭合核对](../../quality/evidence/client-release-20261031/upload-preflight-closure02.json)与[原生只读预检](../../quality/evidence/client-release-20261031/native-current-matrix-preflight.json)。本次没有修改生产源或覆盖旧证据；390/430、定向微信和双账号仍按未执行记录。
无Git提交/推送、生产数据或Schema修改；批准设计源/快照不变。
