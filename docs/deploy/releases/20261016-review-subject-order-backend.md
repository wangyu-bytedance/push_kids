# 2026-10-16 — BUG-029复习科目保序后端发布

- Status: `PREPARING / LOCAL_CHECKS_PASSED / DOCKER_GATE_PENDING / NOT_DEPLOYED`
- Authorized: 用户明确要求“修改代码 然后提交git 并部署”；BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01及额外SPEC-20261016-RELEASE-LINT-01均明确批准。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`，服务`flask-ik19`，端口8000；仅MINIAPP，PUBLIC关闭。
- Scope: 只部署PlanningService保序修复；小程序无改动，无新上传/体验/审核/正式发布。
- Git/source: baseline `8b933dae762f6dbdb1bb9c2286155106b0a5fdc6`；提交与最终冻结SHA待写入。
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
| 本轮隔离MySQL空库迁移/可选MySQL测试 | NOT_RUN，未配置隔离MySQL URL；无SQL/Schema变更，不把生产只读current当迁移证据 |
| 白名单候选 | PASS，预提交107文件/1239653字节，4个根文件+API Python；manifest SHA-256 `a752ba7bd8a1849a6f58d116aff89006a3cd14175fb0db7dcc3d06b75f8d0476`；正式冻结后补commit逐字节核对 |
| 本地Docker构建/UID/8000/SIGTERM/health | NOT_RUN：Docker引擎套接字不存在；启动/恢复中，不能越过必需容器门禁 |
| wxcloud dry run / GRAY创建 | NOT_RUN，须先通过容器与冻结门禁；CLI已核实2.3.3 |
| 新候选真实AppID健康与业务smoke/共存/指标 | NOT_RUN，尚无新候选版本；不伪装成新版本通过 |
| 后端全量 | NOT_RUN，保留BACKEND-RELEASE §7人工切流门禁 |

## 既有生产基线与恢复

本轮通过真实开发者工具AppID调用wx.cloud.callContainer，旧生产030的13个读取路由（live、ready、me、children、subjects、activity-schedules、travel-arrangements、daily-tasks、daily-tasks-today、dashboard、report、review-inventory、schedule）全部200，返回形状检查通过。仅证明发布前服务可用；未写业务反馈，不能证明新保序修复已上线。

Docker诊断发现旧后端进程残留、无engine socket；历史10月13日日志含no space left on device，10月16日本机可用约3.1GiB。本轮只尝试启动/可逆重启，不清理用户文件/镜像/卷。恢复Docker后须从最终提交重新核对冻结目录，完成容器门禁再用GRAY创建不可变版本，记录平台normal及新候选smoke。若引擎仍不可用，停止上传并交付已验证Git提交，等待环境恢复。

## 文档与生命周期

已同步FEAT-001、BHV-006、Architecture与UI-001相关正文及引用，保留本地实现和旧发布状态；BUG Spec暂留`specs/active/BUG-029-REVIEW-SUBJECT-ORDER.md`，VERIFYING。Lint chore四项门禁通过，DONE并迁移completed。最终部署结果与提交后续补入本报告，不将代码完成等同验收完成。
