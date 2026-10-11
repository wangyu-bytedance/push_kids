# 2026-10-11 报表折叠区前端发布候选

## 冻结范围

- Source Git commit：`b2f0aa28e66ce16666fbed50944ad5918085de38`；发布检查开始时工作区干净。
- Scope：`SPEC-20261011-REPORT-DISCLOSURES-01` / `DREV-20261011-REPORT-DISCLOSURES-01`，报表在“科目学习记录”和“课外活动投入”之间新增默认折叠的“历史记录”“编辑计划”。
- 本次无后端代码、API、数据库 Schema 改动；不创建后端版本，也不迁移数据库。
- AppID：`wx5d2e0014690bf285`；云环境：`prod-d2g14rwoycac6b45d`；服务：`flask-ik19`。
- 当前仓库版本基准 `0.1.12`；候选上传版本 `0.1.13`，尚未占用或推进版本基准。
- 若后续上传需回退前端，回退目标为已上传的 `0.1.12`；本次数据库保持原状，生产 Schema revision 未重新读取。
- 候选说明：`报表新增可折叠的历史记录和编辑计划入口，便于查看记录与调整复习安排`。

## 已执行检查

- `npm install`：PASS。
- `npm test`：PASS，219 passed / 0 failed。
- `npm run lint:miniapp`、`npm run check:miniapp`、`npm run check:design-evidence`、`python3 tools/check_architecture.py`：PASS。
- 配置核对：`useCloud=true`，目标环境及服务匹配，真实 AppID，`urlCheck=true`。
- 小程序源码包 133 文件、724195 字节；文件名与内容模式扫描未发现 `.env`、数据库、私钥、凭据模式或儿童照片。开发者工具预览编译 PASS，候选包体 687111 字节（671.0 KB）；预览产物保存在忽略目录 `dist/local-preview/`。
- 微信开发者工具 `islogin`：PASS。真实 AppID `wx.cloud.callContainer` 的 `/health/live` 与 `/health/ready` 均返回 HTTP 200。
- 2026-10-11 只读查询：云托管服务 `normal`、PUBLIC 关闭；版本 `flask-ik19-026` 和 `flask-ik19-028` 均列为 `normal`。CLI 列表不含流量比例或 028 的源码身份。
- 本次实现的三视口、四种展开状态的原生几何及前端行为证据见 `docs/quality/evidence/REPORT-DISCLOSURES-20261011.md`。

## 上传前待确认

- **后端流量兼容性：NOT_RUN。** 旧 `flask-ik19-026` 不含编辑计划所用的复习目录接口。需在云托管控制台确认 026 已无流量，所有承载流量的版本均支持该接口，并核对 028 的来源与灰度稳定性。服务/版本 `normal` 及一次成功业务请求不能替代流量核对。
- **两个真实微信账号的家庭隔离、图片 owner 与主业务流程 smoke：NOT_RUN。** 2026-09-06 有历史双账号部分验收，但发生在此后多个后端版本变化之前；不据此声称本次已通过。
- **iOS/Android 真机交互：NOT_RUN。** 本次 Spec 仍为 `VERIFYING`，体验版阶段需验收。

按 `docs/deploy/FRONTEND-RELEASE.md` §2，“任一项失败都停止上传”；上述必需项尚未取得当前证据，因此本次停在**开发预览成功、开发版本未上传**。未设置体验版、未提审、未正式发布，也未运行 `release:version:bump`。取得上传前证据后，重新核对候选版本和工作区，再执行上传。
