# 2026-10-16 — BUG-029复习科目保序后端发布

- Status: `GRAY_IMMUTABLE_031_NORMAL / DIRECTED_SMOKE_PENDING / NOT_FULL_RELEASED`
- Authorized: 用户明确要求“修改代码 然后提交git 并部署”；BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01及额外SPEC-20261016-RELEASE-LINT-01均明确批准。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`，服务`flask-ik19`，端口8000；仅MINIAPP，PUBLIC关闭。
- Scope: 只部署PlanningService保序修复；小程序无改动，无新上传/体验/审核/正式发布。
- Git/source: baseline `8b933dae762f6dbdb1bb9c2286155106b0a5fdc6`；bug提交 `1b1e9645bfe4fbd88f76109d13f135d5a4a46307`，lint单独提交`374b9ba`。冻结时工作区clean；后续仅记录验收文档，发布源码不变。
- Rollback: 2026-10-16平台只读核对`flask-ik19-030`为normal，service normal/PUBLIC关闭；保留030，不删除旧版本。

## 变更与门禁

后端相对上一发布源码4672628原无差异；本轮只在planning/service.py调整日计划session组装。无SQL、model、Alembic、依赖、镜像基础或运行配置变化；五个设计lint脚本只用于开发且不进入白名单。

| 检查 | 实际状态 |
|---|---|
| 全量本地测试 | PASS，后端518 passed/19 optional skipped，前端244/244；Ruff/format/Mypy/ESLint/架构/设计/小程序检查通过，详见[质量证据](../../quality/evidence/REVIEW-SUBJECT-ORDER-20261016.md) |
| 设计工具清理 | PASS，5脚本新旧168个输出哈希一致，批准设计资产无改动；[chore证据](../../quality/evidence/RELEASE-LINT-20261016.md) |
| Alembic before/after | 本地唯一head及生产只读current均为20261012_0019；MySQL 5.7.18-cynos-2.1.14-log；未迁移 |
| 本次新建备份 | NOT_APPLICABLE，BACKEND-RELEASE §4.2：无Schema/数据迁移 |
| 运行配置/通知配置人工门禁 | NOT_APPLICABLE，未改环境变量、身份、实例、入口、存储或通知通道 |
| 两真实账号/图片owner本轮复验 | NOT_APPLICABLE，无身份/角色/租户边界/图片访问变更；本地family/sibling隔离回归PASS |
| 本轮隔离MySQL空库迁移/可选MySQL测试 | PASS，MySQL5.7.44 utf8mb4_unicode_ci全新空库upgrade head/current=0019/check无差异；4文件mysql专项18 passed/7 deselected（8.14s）；初次默认字符集失败已在重建库后解决 |
| 白名单候选 | PASS，107文件/1239653字节，4个根文件+API Python，逐字节等于1b1e964；manifest SHA-256 `a752ba7bd8a1849a6f58d116aff89006a3cd14175fb0db7dcc3d06b75f8d0476`；docs/tests/tools/小程序/秘密排除 |
| 本地Docker构建/UID/8000/SIGTERM/health | PASS，冻结目录构建；UID10001、8000、live/ready 200，SIGTERM退出0/OOM false；同一镜像连接隔离MySQL，通过HTTP完成语文首项后3次重读保序/计数/plan_id均正确 |
| wxcloud dry run / GRAY创建 | PASS，CLI2.3.3；打包128项（含目录）无禁止路径。预演临时ZIP已通过重新生成同哈希目录移除。确认表核对目标AppID/env/service、GRAY、Dockerfile、`.`、8000和唯一备注后输入yes；031于22:53:10创建，22:56:03达到normal，副本1；服务normal/PUBLIC关闭 |
| 新候选真实AppID健康与业务smoke/共存/指标 | NOT_RUN：031流量0%，无定向参数/白名单命中证据，需控制台配置定向测试后验收。031运行日志API返回TopicNotExist，无法读取，不将旧030或本地镜像检查当新云候选smoke |
| 后端全量 | NOT_RUN，保留BACKEND-RELEASE §7人工切流门禁 |

## 既有生产基线与恢复

本轮在灰度创建前及031 normal后，分别通过真实开发者工具AppID调用wx.cloud.callContainer，当前生产030的13个读取路由（live、ready、me、children、subjects、activity-schedules、travel-arrangements、daily-tasks、daily-tasks-today、dashboard、report、review-inventory、schedule）全部200，返回形状检查通过。中途自动化连接断开，重启项目auto9420后恢复并成功重跑。只证明当前承载流量的030仍可用；未写业务反馈，不能证明0%流量031已完成定向smoke。

Docker旧后端进程残留、无engine socket；本轮重启后恢复29.1.2引擎，未清理用户文件/镜像/卷。历史空间错误不是本次最终失败。隔离MySQL初次使用镜像默认排序规则触发历史0003中文SQL collation失败，清理本次容器后按项目utf8mb4_unicode_ci重建空库，base→0019及current/check全部通过。

最终冻结目录`dist/release-20261016-bug029-1b1e964`；本地镜像`push-kids:bug029-1b1e964`，镜像ID `sha256:39395a18e9f4580b922ec96812ea3cbf057d4e25d35806cfc62f6202045a8b14`。容器验证只在本次专用网络/空库中使用合成家庭，随机测试密码仅进程内传递，结束删除本次应用/MySQL容器、临时卷和网络；生产无迁移/业务写入。

已通过CLI同源只读API在内存逐字段比较031与030：EnvParams、CPU/内存、实例上下限、端口、入口、MountWxToken等无差异，未输出秘密值；031备注为`push-kids-20261016-bug029-1b1e964`，Dockerfile/BuildDir/8000正确。当前030 FlowRatio=100、031=0，无定向URL参数。031构建日志23531字节的内存扫描可见API COPY，未见禁止的仓库根上传路径或build-failure标志；原始日志未入仓库/聊天，CLI完成上传后自动删除临时ZIP，因此未声称拿到了实际上传ZIP摘要。

平台版本031已normal；发布单仍`running`，CreateVersion完成进入灰度流程，GrayRelease人工阶段未完成，FULL阶段notInvolve。不能把CLI“部署完成”解释成已全量发布。全量前须在[服务控制台](https://cloud.weixin.qq.com/cloudrun/service/flask-ik19)为031配置测试用户定向命中；在小程序测试完成复习后保序、live/ready及相关读取，观察至少2分钟和错误/延迟/Job指标，再由发布负责人按BACKEND-RELEASE §7确认切流。回滚030，Schema保持0019；不在聊天粘贴OpenID或任何秘密。

## 文档与生命周期

已同步FEAT-001、BHV-006、Architecture与UI-001相关正文及引用，明确031 normal但0%及030仍100%；BUG Spec保留`specs/active/BUG-029-REVIEW-SUBJECT-ORDER.md`，VERIFYING。Lint chore四项门禁通过，DONE并迁移completed。逐项核对实际diff与相关当前正文无冲突；定向smoke/指标/共存/全量待发布负责人完成后只读核验，再决定BUG Spec的DONE迁移。代码完成或版本normal不等同完整验收完成。
