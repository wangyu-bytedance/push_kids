# 2026-11-01 — 前端0.1.17提交续接（用户补齐门禁前的历史证据）

本报告正文限定用户回复“已完成039照片回看与双账号验收”之前；随后0.1.17已于16:15:08官方上传成功，
包体1,191,019字节并bump，三Spec DONE/completed。当前以[成功上传记录](20261101-client-0.1.17-upload.md)为准；
下方未上传/待账号验收是历史状态，不再要求重复执行已确认门禁。

- Actual stage: `BACKEND_039_NORMAL_100_PERCENT / LOGIN_AND_PREVIEW_PASS / NATIVE_THREE_VIEWPORTS_PASS / UPLOAD_BLOCKED_BUSINESS_ACCOUNT_SMOKE / NOT_UPLOADED`。
- Authorization: 用户本轮“后端已经部署完成，前端提交”，继续授权当前已批准前端开发版本上传；无需再次申请上传授权。未执行Git提交/推送、提审或正式发布。
- Baseline: `0576ac30464908154c624effed41df6dfa3110cc`＋已有工作区修改，生产前端与冻结包未改变。
- Target: AppID `wx5d2e0014690bf285`，环境`prod-d2g14rwoycac6b45d`，服务`flask-ik19`。
- Frontend: `dist/client-release-20261031-0.1.17/project`；168份源逐项SHA与当前源码、已验证manifest一致，manifest SHA-256 `04c6668a20a0f99622c78424b4d7c5ba07aadc1fd515f20a494e0e4cfcbb2adb`。
- Version: 工具计算候选`0.1.17`；基准仍`0.1.16`，未调用upload/bump。用户“我已登录微信开发者工具，请继续操作”后恢复本轮验证，无新增生产代码。
- Description prepared: 精简旅行日记入口，优化照片导入与核对恢复，修复照片精确回看。

## 当前结果

| 检查 | 结果和范围 |
|---|---|
| 云端控制平面 | PASS；2026-11-01 15:31 Asia/Shanghai只读确认039 normal、100%流量、1副本，PUBLIC关闭，入口MINIAPP/OA；038已不在本次列表中，不继续称其为当前可用回退版本 |
| 前端冻结范围 | PASS；168份源码/冻结副本逐项匹配，无本次生产改动；0.1.17由工具计算 |
| 架构/设计/小程序/diff | PASS；4 policies/151 modules、DESIGN_EVIDENCE_VALID、17页/1233761源字节、git diff --check |
| 完整前端/ESLint/依赖 | 复用2026-10-31同168份精确源码已运行349 PASS及ESLint/依赖证据；无新变化，不重复套件，不描述为本轮重跑 |
| 本轮官方preview | PASS；官方CLI fresh preview exit0，编译1,191,019字节；不是上传回执 |
| 当前官方CLI登录 | PASS；初次仍false，随后本人登录状态生效，官方两次login:true；早期false/code10保留 |
| 原生automation启动 | PASS；合成项目及真实AppID冻结云客户端分别官方auto成功；DevTools重启后改用当前28158端口恢复，没有绕过认证 |
| 当前桌面状态 | PASS_AUTHENTICATED；正确官方工具实例，真实选择iPhone12/13 Pro与iPhone14 Pro Max；不是mock systemInfo |
| 真实微信039健康/身份 | PASS；live200/170ms、ready200/79ms，复测123/109ms；me200、bound，两个孩子visits200；039是当时唯一100%版本，控制平面与请求分别留证 |
| 新focus运输合同 | PASS_PARTIAL；37字符focus被422拒绝，合法未知visit/focus404，证明新参数校验可达；当前账号无confirmed visit/photo，正向focus与前后分页NOT_RUN |
| 双真实账号/非owner | NOT_RUN；只执行一个真实微信账号，旧0.1.16双账号基线不覆盖新focus |
| 三视口/双宿主原生布局 | PASS；既有320×568双宿主14组＋新390×844与430×932两宿主各7态共28组，合计42组节点/PNG；源SHA与截图SHA匹配 |
| 原生动作 | PASS_LOCAL_NATIVE_SCOPE；独立/内嵌三模式和草稿面板真实方法通过，内嵌CUA切视图/打开核对，两个宿主真实系统选图取消恢复；返回学习后实际setField/hasText通过；完整真机/键盘/读屏/大字NOT_RUN |
| 前端upload/bump/体验/审核/正式发布 | NOT_RUN |

当前[续接证据](../../quality/evidence/client-release-20261101/resumed-preflight.json)、
[原生矩阵摘要](../../quality/evidence/client-release-20261101/native-matrix-resumed.json)与
[当前云端查询](../../quality/evidence/client-release-20261101/cloud-state-resumed.json)保存本轮结果；
真实微信[首次健康](../../quality/evidence/client-release-20261101/cloud-smoke-resumed01.json)/
[focus验证及无正式照片](../../quality/evidence/client-release-20261101/cloud-smoke-resumed02.json)、
[真实原生动作](../../quality/evidence/client-release-20261101/resumed-ui-actions.json)与
[新preview包体](../../quality/evidence/client-release-20261101/preview-resumed-info.json)分别留证。
本次[官方预览二维码](../../quality/evidence/client-release-20261101/preview-resumed-qr.png)供有预览权限的测试账号验证；
若平台提示过期，从同一冻结项目重新preview即可，二维码不是开发版本上传或体验版。
初次[认证失败](../../quality/evidence/client-release-20261101/preflight.json)仍是历史，未覆盖。
原源码、测试、preview及实际应用账号Schema0025/数据库ready/无DDL权限PASS见
[此前兼容交付](20261031-travel-diary-backend-compatibility.md)。无Schema、运行配置、切流或业务数据写入。
本轮100%为用户完成后只读观测，不冒称代理实施切流。旧038控制平面与0%观测保留原日期，不当作当前状态。

## 当前上传门禁与生命周期

```text
【需要人工操作】完成039照片回看与双账号验收
原因：新focus读路径触发前端发布§2的主路径与家庭/图片owner门禁；当前已登录账号没有正式到访照片，且只有一个真实账号证据。
操作入口：微信开发者工具中dist/client-release-20261031-0.1.17/project的预览二维码；https://mp.weixin.qq.com/
导航路径：当前预览 → 记录 → 旅行日记 → 有已确认照片的到访 → 照片回看；第二测试家庭重复权限验证
需要填写/选择：
- 使用两个不同家庭、具有预览权限的真实微信测试账号；身份/儿童照片只在微信平台和小程序内操作。
- 用既有已确认到访照片验证点击照片与回看一致，深于第一页仍能定位，前后页和返回列表可用。
- 两个家庭不能读取彼此的照片/到访；非owner私有图片访问被拒绝。
完成标志：039目标主路径及双账号/非owner检查通过，无越权或错误照片定位。
完成后回复：已完成039照片回看与双账号验收
```

当前门禁直接来自[前端发布§2](../FRONTEND-RELEASE.md)：涉及图片owner/私有访问的变更需两个真实账号验收，
且必须验证本次主路径和目标后端兼容；未完成时停止上传。用户上传授权继续有效，不再申请部署/上传授权。
本轮不制造或确认儿童正式照片来填补测试数据；管理员可在官方工具内选有既有正式照片的测试账号继续，
聊天只回验收状态。自动化、预览及原生矩阵可独立完成的工作均已完成。
验收后继续同168份冻结源upload，仅成功才bump；若源码变化先重新冻结核验。平台体验/提审/正式发布保持独立门禁。

BUG-035后端已交付、客户端尚未上传；旅行导入/入口精简也尚未客户端云交付，
三份Spec仍VERIFYING于`specs/active/`。测试维护仍DONE/completed，BUG-036独立任务未混入包。
本轮未修改生产源码/测试/设计资产；同步Feature、Behavior、Architecture、UI、Spec/索引及发布记录
的已登录、fresh preview、039微信健康、42组原生、动作和剩余账号/主路径事实。
初次probe误判学习handler、官方工具并行重启端口失败保留原结果；只修订临时探针，不改产品。
最终当前文档引用、源SHA/原生摘要与生命周期核对见[续接闭合](../../quality/evidence/client-release-20261101/resumed-closure.json)；
三项旅行Spec位置保持active/VERIFYING，已实现后端与尚未上传客户端按两端分别记录。
