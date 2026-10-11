# 2026-10-11 报表折叠区前端发布候选

## 冻结范围

- Source Git commit：`b2f0aa28e66ce16666fbed50944ad5918085de38`；发布检查开始时工作区干净。
- Scope：本次目标为 `SPEC-20261011-REPORT-DISCLOSURES-01` / `DREV-20261011-REPORT-DISCLOSURES-01`，报表在“科目学习记录”和“课外活动投入”之间新增默认折叠的“历史记录”“编辑计划”。相对上次已上传 `0.1.12` 的源码 `3705578c`，候选包还累计包含此前已批准但未上传的复习条目改版、今日删除入口、精确原图展示、语音输入和课外活动排序等小程序改动；不是只含报表改动。
- 本次无后端代码、API、数据库 Schema 改动；不创建后端版本，也不迁移数据库。
- AppID：`wx5d2e0014690bf285`；云环境：`prod-d2g14rwoycac6b45d`；服务：`flask-ik19`。
- 当前仓库版本基准 `0.1.12`；候选上传版本 `0.1.13`，尚未占用或推进版本基准。
- 若后续上传需回退前端，回退目标为已上传的 `0.1.12`；本次数据库保持原状，生产 Schema revision 未重新读取。
- 候选说明：`报表新增历史记录与编辑计划，优化复习条目、语音输入和活动排序`。

## 已执行检查

- `npm install`：PASS。
- `npm test`：PASS，219 passed / 0 failed。
- `npm run lint:miniapp`、`npm run check:miniapp`、`npm run check:design-evidence`、`python3 tools/check_architecture.py`：PASS。
- 配置核对：`useCloud=true`，目标环境及服务匹配，真实 AppID，`urlCheck=true`。
- 小程序源码包 133 文件、724195 字节；文件名与内容模式扫描未发现 `.env`、数据库、私钥、凭据模式或儿童照片。开发者工具预览编译 PASS，候选包体 687111 字节（671.0 KB）；预览产物保存在忽略目录 `dist/local-preview/`。
- 微信开发者工具 `islogin`：PASS。真实 AppID `wx.cloud.callContainer` 的 `/health/live` 与 `/health/ready` 均返回 HTTP 200。
- 2026-10-11 只读查询：云托管服务 `normal`、PUBLIC 关闭；版本 `flask-ik19-026` 和 `flask-ik19-028` 均列为 `normal`。CLI 列表不含流量比例或 028 的源码身份。
- 后续用户在本会话确认当前线上流量使用 `flask-ik19-028`。同一真实 AppID 小程序链路只读调用 `GET /api/v1/children/{child_id}/review-inventory` 和 `/subjects` 均返回 HTTP 200，响应均含预期 `items` 数组；仅记录状态与响应形状，未输出孩子 ID 或数据。此证据验证当前路由支持前端调用；028 源码身份和控制台流量比例未由 CLI 独立读取。
- 本次实现的三视口、四种展开状态的原生几何及前端行为证据见 `docs/quality/evidence/REPORT-DISCLOSURES-20261011.md`。

## 上传前待确认

- **后端流量兼容性：PASS（用户控制台确认 + 当前业务路由只读 smoke）。** 旧 `flask-ik19-026` 不含编辑计划所用接口，但用户已确认线上使用 028，且当前小程序链路的两个目标 GET 接口均为 200。CLI 不提供流量比例，因此该比例来自用户确认，不声称由 CLI 独立验证。
- **两个真实微信账号的家庭隔离与图片 owner 复测：NOT_APPLICABLE。** 以已上传 `0.1.12` 的源码 `3705578c` 对比完整候选包：未改 `app.js`、`utils/api.js`、`pages/family-*` 或后端身份/家庭/媒体授权边界，也未改存储规则或平台身份配置。新增界面读取既有 `currentMember.role` 控制删除/排期按钮可见性，材料组件筛选并呈现对应照片；两者均复用服务端原有权限及私有媒体接口，不修改角色策略、图片 owner 判定或跨家庭访问合同。相关前端状态测试及云端只读业务路由已验证，按 `SPEC-20261011-RISK-BASED-RELEASE-GATES-01` 复用 2026-09-06 双账号安全基线，不把未复测记为通过。其余累计改动以本次前端全套自动化、设计/原生几何和预览编译证据覆盖；真机能力留待体验版。
- **iOS/Android 真机交互：NOT_RUN。** 本次 Spec 仍为 `VERIFYING`，体验版阶段需验收。

风险分级门禁修订 `SPEC-20261011-RISK-BASED-RELEASE-GATES-01` 已由用户 2026-10-11 回复“批准，上传”批准；本次双账号复测不触发，后端兼容性已通过。当前仍停在**开发预览成功、开发版本未上传**；上传前将复核版本与工作区，成功后另记平台状态并推进版本基准。
