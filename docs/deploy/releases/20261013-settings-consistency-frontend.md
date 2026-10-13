# 2026-10-13 设置统一前端发布

- Source commit: 5837d59（设置科目列表、每日任务背景与候选/编辑半屏及设计/测试证据）。
- Target version: 0.1.15，版本工具从已上传基准0.1.14计算，禁止复用。
- AppID: wx5d2e0014690bf285；useCloud=true；urlCheck=true。
- Cloud env / service: prod-d2g14rwoycac6b45d / flask-ik19。
- Backend / Schema: 既有flask-ik19-030 / 20261012_0019，本次不变，无数据库或后端部署。
- 当前状态：CLI upload成功，0.1.15已上传为开发版本；包体1027271字节（1003.2KB）。未设置体验版、未提交审核、未发布正式版。版本基准已推进0.1.15。
- 发布说明：统一设置科目与每日任务样式，新增每日任务背景与快捷候选。

## 自动检查与阶段判定

239项npm test、lint:miniapp、check:miniapp、架构、批准设计清单、git diff --check均PASS。
CLI islogin={login:true}，preview成功；包体1027271字节（1003.2KB），低于1.5MiB。
已有node_modules及lock无依赖变更，npm install未重复执行。客户端配置核对及秘密/数据库/私钥文件扫描无匹配。
此次不改可信身份、家庭成员/角色/绑定、租户授权、媒体owner或存储规则，双账号安全重验NOT_APPLICABLE；复用既有安全基线。
430×932原生八态几何PASS；320/390原生、完整截图、iOS/Android键盘读屏及真机NOT_RUN，记录于SETTINGS-CONSISTENCY-20261013.md，留待体验验收。
后端兼容与健康smoke：实际wx.cloud.callContainer读取live/ready/me/children/subjects/activity-schedules/travel-arrangements/daily-tasks/daily-tasks-today/dashboard/report/review-inventory/schedule共13项均200；返回任务数组与今日/首页任务结构符合预期。首次连接因CLI重启IDE断开，恢复auto连接后完整重测PASS。源码5837d59之外的并行文档治理未纳入本次提交。

## 后续阶段与回退

开发上传成功后由管理员选为体验版、验收变更主路径，再提交审核，审核通过后人工发布；不能将上传记为正式上线。
前端回退目标：此前0.1.14；后端保持030与Schema0019。本次任务Spec保留VERIFYING，剩余原生/真机验收不伪记DONE。
