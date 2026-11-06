# 2026-10-25 最新客户端 0.1.16 开发版本上传

- Stage: DEVELOPMENT_VERSION_0.1.16_UPLOADED / EXPERIENCE_PENDING / NOT_SUBMITTED_FOR_REVIEW / NOT_OFFICIALLY_PUBLISHED。
- Authorization: 用户本会话要求「服务端已经是最新的了？客户端也发布」。这是已批准实现的交付操作，没有增加产品/API/测试行为或设计修订；没有提交或推送。
- Source: 冻结时HEAD为 `0576ac30464908154c624effed41df6dfa3110cc`（add travel，2026-10-25 09:29:05 +0800）。发布核对开始时是26714b9＋已批准BUG-034增量，期间工作区由外部操作提交；代理未提交/推送。当前提交与冻结/上传168份文件一致；相对上次0.1.15源码5837d59共63份路径有变化，包含旅行日记、学习/复习、通知续订和年级确认。BUG-033归档候选未实施，未打入包。
- Frozen input: `dist/client-release-20261025-0.1.16/project`，168份跟踪源码/资源、1221792源码字节。SHA-256 manifest：`72f5552cc5c4af3a0bb3bd4960bf9dc3c1c4a3261379d0b10ffca5f2e0ef0b49`。上传后逐项复核当前源/冻结源一致，配置为真实AppID、useCloud=true、目标环境/服务匹配、urlCheck=true；仅跟踪assets图片，无本次几何注入、儿童图片或已知秘密模式。
- Target: `wx5d2e0014690bf285 / prod-d2g14rwoycac6b45d / flask-ik19`。
- Backend: 037 normal、服务normal、公网关闭；150份Python、pyproject和uv.lock与已部署冻结02全部一致，无额外源码，manifest SHA `4c12f38271ec8659e4b7b472bd8d62992c8754260d5b0210aed0079ce36eda23`。包含CRUD启动修复；无需重建服务端。Schema保持0025，无新迁移或流量操作。
- Version: 工具从0.1.15计算0.1.16，成功上传后才bump基准至0.1.16；未复用旧号。
- Description: 新增旅行日记与照片时间线，统一按钮样式，优化学习记录、复习与年级确认。
- CLI result: preview成功1178893字节；从冻结目录upload退出0并显示upload成功，上传包体 **1178991字节**。CLI不能读取体验/审核/线上状态，因此不推断这些后续状态。

## 本轮检查与门禁

| 检查 | 结果 |
|---|---|
| npm install --ignore-scripts --offline --no-audit --no-fund | PASS，既有依赖up to date |
| npm test | 335 tests /335 pass /0 fail /0 skip，1361.384416ms |
| npm run lint:miniapp / npm run check:miniapp | PASS；17页、1221792源码字节 |
| check_architecture / current-policy design validator | PASS；4 policies /150 modules；批准设计源/导出不变 |
| 真实微信callContainer live / ready | 200 /200，142ms /98ms；只记录固定状态，未读取业务内容 |
| 本次新增媒体权限路径双账号门禁 | PASS_OPERATOR_CONFIRMED：用户2026-10-25在call_fa3043ef407b4441aca5087686394298回复「已按上述范围验证通过」；两不同家庭真实账号，A可看自己照片，B不能读取A到访列表/照片详情/缩略图。代理未代做，不扩张到移除/撤权/全部对象生命周期 |
| BUG-034三尺寸原生 | 复用同一当前源码的54组节点/PNG，源码摘要未变；其余功能各自原生/设备缺口不由这54组代验 |
| 后端pytest/MySQL | NOT_RUN，本轮未改后端，冻结源码150份与已部署验证包一致 |
| iOS/Android完整体验、读屏/大字体、实际订阅授权、全球地图/AI内容 | NOT_RUN；保留各产品Spec的验收缺口 |

[上传与检查结果](../../quality/evidence/client-release-20261025/upload.json)、[源码清单](../../quality/evidence/client-release-20261025/source-manifest.json)、[服务端健康](../../quality/evidence/client-release-20261025/backend-health.json)。旧发布记录按日期保留，不改写为当时已上传。

## 后续平台阶段与回退

按[前端发布手册§4](../FRONTEND-RELEASE.md)由管理员选择0.1.16为体验版并配置体验成员；完成适用真机/主路径验收，再核对资质隐私、提交审核，审核通过后人工正式发布。本轮没有自动操作这些平台阶段，也未开启默认关闭的提前复习/学习建议或覆盖功能。

上一已上传候选为0.1.15；后台当前正式版本未独立读取，不能把该候选称为已上线回退点。回退客户端按后台已验收版本操作；后端继续037/0025，035不能在0025重启，不执行数据库downgrade。

## 历史文档与生命周期（当次执行口径）

同步Feature/UI/Behavior/Architecture/设计索引/测试/发布与Spec索引的当前上传阶段及用户验收来源；领域合同、批准设计源/导出、生产源码均不改。BUG-034及其他未完成产品验收的Spec保留active/VERIFYING，不把上传成功改成DONE。体验版、提审和正式发布等待管理员完成相应门禁。

## 2026-10-26 开发完成归档

按用户明确批准的[云端交付完成规则](../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)，本记录已交付范围对应的41份Spec已标开发DONE并迁completed，具体见[状态索引](../../../specs/STATUS.md)。原验收结果和发布阶段保留，未执行检查不改为PASS；本轮没有新部署/上传。BUG-035和旅行导入精简是此后本地增量，继续active。
