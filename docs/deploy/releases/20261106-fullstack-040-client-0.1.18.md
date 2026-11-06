# 2026-11-06 全栈交付：040 / 0.1.18

- 实际阶段：`BACKEND_040_NORMAL_100_PERCENT / SCHEMA_0027 / CLIENT_0.1.18_UPLOADED`。
- 用户批准：`批准 OPS Spec01`、`批准固定40材料 Spec07`；本次确认`已完成数据库发布前备份，窗口确认`，并明确要求`不用配置 直接发布`。
- HEAD：`0576ac30464908154c624effed41df6dfa3110cc`＋既有已批准工作区修改；无 Git 提交或推送。
- 来源：`dist/fullstack-release-20261105/`，freeze manifest SHA-256 `c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`。后端160份、1,607,791源字节；客户端168份、1,244,228源字节，上传前逐项SHA一致。
- [版本证据](../../../specs/evidence/EVD-20261106-FULLSTACK-DELIVERY.md)、[安全产物目录](../../../specs/evidence/fullstack-release-20261106/summary.json)。11/05各阶段、失败和manifest保持原版本。

## 数据库与后端

发布前备份、隔离恢复路径与30分钟受控窗口由用户在聊天确认，代理没有独立取得备份ID或进行恢复演练。窗口内真实执行MySQL `20261024_0025 → 20261105_0026 → 20261105_0027`，新增两个默认false的workday列和近期学科索引。迁移包独立于运行包；没有业务数据修订。

Alembic upgrade/current/check、管理员strict schema、17个队列/提前复习触发器集合均PASS。两张投影different/missing/unexpected均0。平台实际040运行账号通过DBready、0027启动校验及无DDL权限检查，没有给运行账号扩权。[生产迁移](../../../specs/evidence/fullstack-release-20261106/production-migration.json)、[投影](../../../specs/evidence/fullstack-release-20261106/production-projections.json)、[实际040账号](../../../specs/evidence/fullstack-release-20261106/runtime-schema-post040.json)。早期私有脚本post输出曾硬编码039标签，不作为040身份依据；本证据使用修正后的版本绑定重查。

官方CLI从冻结白名单创建040，备注`ops01-20261106-c96b30d-0027`；先观察normal/0%/1实例。灰度URL规则SDK调用两次返回`ServiceNotExist`，没有改变流量；用户随后明确跳过测试账号、直接发布。助手执行全量前的前置读取已显示040 normal/100%，因此前置断言停止，未重复发起切流mutation；实际切流操作者/确切时间未由审计日志独立确认。上传后再次读取仍为040 normal/100%/1。

镜像标识为`flask-ik19-040-20261106065032`，SDK只提供镜像tag，未取得registry digest，不将源SHA称为镜像digest。端口8000。18项服务与原039运行配置一致；System One沿默认true，Pro/Lite默认模型分别为`doubao-seed-2-1-pro-260628` / `doubao-seed-2-1-lite-260915`。保留既有0.25CPU/0.5GiB/min0/max5，未擅改为手册资源建议。开放类型实际为`MINIAPP + OA`，`PUBLIC`不在其中；不能写成仅MINIAPP。[最终状态](../../../specs/evidence/fullstack-release-20261106/post-upload-cloud-state.json)。

实际开发者微信身份经`wx.cloud.callContainer`访问040默认流量，live/ready、bootstrap、children、calendar、schedule、report七路GET全部200；最后一轮各请求约130–477ms。首次schedule探针误用`date`参数得到422，修正为公开合同`day`后200；保留原探针，不能把夹具错误归为后端失败。此次只读smoke不证明AI生成、正式确认、取消、重试或恢复已在线验收，也不是线上成功率统计。[首次](../../../specs/evidence/fullstack-release-20261106/wechat-smoke-040.json)、[修正后](../../../specs/evidence/fullstack-release-20261106/wechat-smoke-040-corrected.json)。

## 客户端

官方登录PASS；冻结生产客户端preview 1,200,319字节。按版本工具0.1.17→0.1.18计算，官方upload成功，回执文件时间为2026-11-06 09:31:29 CST；包体1,200,417字节，成功后bump为0.1.18。说明：`优化学习内容生成与人工核对，支持工作日安排，精简档案归档提示`。[回执](../../../specs/evidence/fullstack-release-20261106/client-delivery.json)、[官方日志](../../../specs/evidence/fullstack-release-20261106/frontend-upload.log)。

上传包保持真实AppID、`useCloud=true`、prod环境、flask-ik19和`urlCheck=true`。私有本地测试项目未上传。开发上传不等于体验版、审核或正式发布，后续平台操作仍由管理员完成。

后续接口设置：冻结包的旅行日记在家长点击“地图选点”时调用`wx.chooseLocation`，app.json已声明该项。管理员正在准备后台接口申请；开通/审批结果尚未核验。其余截图中的定位、直播、音视频通话、NFC、红包及微信运动接口未被该包调用，不建议批量开通。申请材料使用已保存的原生演示场景截图，不称为系统地图选点成功证明；本次重新截图的官方RPC超时，生产代码未改。

本次不改身份、绑定、家庭成员/角色/邀请、租户边界、媒体owner或相关平台配置；新增双账号门禁为`NOT_APPLICABLE`，沿用已确认安全基线。0027当前实际运行账号、真实微信读取和工作日主路径另行验证，不用既有安全证据抵扣。

## 测试与生成质量

| 检查 | 实际结果及范围 |
|---|---|
| 冻结源码与必需自动检查 | 相同160/168源；11/05批准两行测试维护后的Python988PASS/56条件SKIP、SDK25PASS、隔离MySQL5.7.44十文件48PASS/0SKIP、前端359及静态PASS沿用精确源码证据；本次未重复整套 |
| fixed40 v2 | 获批材料Spec07后唯一完整单轮40/40＝100%；三科各15/15，empty/pending/formal均0，约527.8秒。原v1 37/40 FAIL、旧45次对照保持，不改阈值或分母 |
| 原生状态矩阵 | 工作日48＋备注减法24＋归档21＝93组节点/PNG；沿用11/05已绑定源码证据 |
| 原生确认框 | 本次320/390 CUA实际视觉及取消补齐，430原记录保持。截图RPC下层图不当作modal视觉；本次320/390视觉为CUA会话观察，没有另存modal PNG |
| 原生工作日主路径 | 生产Pages/API utils的165份私有副本逐字节一致；真实HTTP到隔离SQLite合成家庭。实际保存辅导课18:10–19:10、回填、日程摘要、来源跳转；新建工作日日程20:10–20:40、保存及编辑回填均由CUA AX观察PASS |
| 本地联调边界 | 仅私有config/插件/project设置用于本地HTTP，WechatSI插件省略，urlCheck/lazy placeholder关闭，生产包不变；不证明真实设备或语音能力。多次自动化连接/截图超时、旧路由夹具失败保留；重启工具后使用实际原生操作完成，不将脚本重跑成功当稳定性指标 |
| 家长内容 / 线上成功率 | `PENDING / NOT_MEASURED`；System One无疑点不等于质量通过，固定40也不是线上统计 |
| 真机 / 大字体 / 读屏 | `NOT_RUN`，在体验版继续；不因开发DONE改成PASS |

System One只在Pro形成有效产物后辅助验收，疑点、不可用或超预算都保留产物并进入既有人工核对；只有家长确认才建立正式学习与确定性复习。该产品合同未因发布而改变。

## 恢复与待验

0027后039不是可用回滚目标。恢复使用理解0027及workday语义的本冻结代码/新兼容镜像或前向修复；必要时按管理员确认的备份恢复路径处理。System One开关关闭只关闭辅助验收，不回退Schema或工作日逻辑。未执行生产恢复演练。

备份保留要求仍是最新3份。发布后访问备份控制台被浏览器站点安全策略拦截，未能列出、核对或删除任何备份，数量记`NOT_RUN`；未绕过限制，需要管理员在控制台核对保留列表。用户的发布前备份完成确认保持，不能写成已核验保留数量。

11份匹配实现/关联交付Spec设DONE并迁completed，验收缺项独立保留。旧10/13候选OPS仍BLOCKED/active：040交付继承缓存功能，不能伪称旧34/40失败候选已部署；CLOUD-002、DOC-003仍待具体批准。当前120 completed、3 active、19 rejected，共142。Feature001/003/005、Behavior、Architecture、UI001/015、测试策略、发布入口及Spec索引同步当前正文；批准设计快照、阶段manifest及历史结果/版本保持，历史可变Markdown仅迁移归档链接，不追改测试结论。文档与源码冲突/链接/状态数量检查见新证据目录的closure结果。
