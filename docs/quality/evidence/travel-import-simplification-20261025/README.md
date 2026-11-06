# 旅行导入精简 — 当前源码证据

本文件保留原执行时点的实施/验证与未交付结论；2026-11-01旅行三Spec已由039/0.1.17交付，DONE/completed，用户照片回看/分页/双账号门禁确认PASS。当前生命周期与平台阶段以[成功上传记录](../../../deploy/releases/20261101-client-0.1.17-upload.md)为准；下方VERIFYING/active/未上传仅代表原时点，设备/内容未验及历史FAIL不改为通过。

- Stage: LOCAL_IMPLEMENTED / VERIFYING / NOT_UPLOADED / NOT_DEPLOYED
- Approval: 产品负责人2026-10-25明确回复“批准导入精简 Spec01＋Architecture01＋DREV02，按此实施”，[Spec及范围](../../../../specs/completed/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md)。
- Baseline HEAD: `0576ac30464908154c624effed41df6dfa3110cc`，沿用原checkout及既有未提交BUG-035改动，未提交/推送。
- Current delta: 仅`footprints/{controller,imports}.js`、`index.wxml/index.wxss`及相关测试/取证夹具/文档；此增量无后端/SQL/Schema/依赖或云配置变更。

## Verification

| Point | Actual result | Boundary |
|---|---|---|
| TP01直入相册/防重/取消 | PASS，新增/替换动作回归先红：53/58，5失败；实施后专项58/58，全量349/349 | 非逐字镜像测试 |
| TP02生命周期/AI偏好 | PASS，正常hide/show、family/member/child/unload；取消/失败两种返回时序恢复预览；AI false/true导入均不写preferences | 合成API动作，不代表iPhone |
| TP03上传/编辑/确认/回看回归 | PASS，既有专项随全量通过；首张失败、中途失败1/2、同批跳过已收讫项和稳定key | 正式云确认/新focus仍按BUG-035缺口 |
| TP04 npm test | PASS 349，0 fail/skip | 本地当前前端 |
| TP04 lint:miniapp / validate_miniprogram / architecture | PASS；DAG150，页数/字节以source-native-manifest.json实际记录为准 | 无后端修改，不重复后端/真实MySQL全套 |
| TP05设计 | PASS 15张HTML/交互/current-policy SHA | [批准manifest](../../../design/frontend/snapshots/UI-018/DREV-20261025-TRAVEL-IMPORT-02/APPROVAL.md)，非原生 |
| TP06当前原生矩阵 | PASS，entry/selecting/uploading/upload-error/settings × 320×568/390×844/430×932，共15组 | [source-native-manifest.json](source-native-manifest.json)；原生逻辑窗扣除状态栏/导航栏，screenHeight按精确机型 |
| TP06实际430操作 | PASS，CUA点导入直接系统文件选择器、取消回原页；再选3张合成PNG，在第2张注入一次失败，界面1/3/重试，CUA点重试后3草稿核对 | [失败状态](actual-partial-error.json) / [重试结果](actual-retried.json)，禁云transport；没有六六真实媒体 |
| TP06设置往返 | PASS，生产方法开启/保存/返回、关闭/保存/返回均保持值 | [原生方法结果](native-settings-method.json)，不写成CUA开关点击 |
| TP07只读复核 | PASS，无可执行发现 | 同一代理在实施结束后按code-review技能独立只读阶段执行；非第二名reviewer，[报告](READONLY-REVIEW.md) |

原生节点逐项核对横向边界、触控44px、正文14px、主CTA48px/16px、标题/关闭间距、面板/底部动作边界、短屏导入经正常滚动到导航上方。PNG已逐类抽查；忙态使用批准松绿降透明，继承既有插画/导航。原生矩阵首次通过后为匹配批准忙态颜色再次编译并重采15组，最终绑定SHA取代中间矩阵，不复用BUG-035的42组代验。

复跑：`.venv/bin/python tools/prepare_travel_diary_native.py`建立`/private/tmp/push-kids-travel-diary-native-20261025`禁云副本；官方CLI auto-port9586；CUA选择对应精确机型，`node tools/travel_import_geometry.js 320 9586`（390/430同理）。副本只替换合成transport、移除语音插件、加入既有测试setter/滚动绑定；原生产controller/WXML/WXSS行为不替换。基础库3.16.2、DPR2/3，默认字体；旧tools/travel_diary_geometry.js与旧42组是BUG-035历史状态，不是本revision重放工具。

## Metadata question and open gates

当前选图请求`sizeType:original`，客户端读取大小/格式后上传该临时文件；后端先提取EXIF DateTimeOriginal/OffsetTimeOriginal/GPS，再派生去元数据展示图，GPS走地点反解。三张用户指定JPG重新只读检查均EXIF0；不能判断iPhone相册原件有无这些字段或在哪个转发环节丢失。未用上传时间/下载文件名代填日期。当前HEIC原文件不被支持；未改变既有格式合同。

NOT_RUN：实际iPhone/Android相册原件直传后的EXIF保留率、HEIC兼容、真实软键盘/大字/读屏、完整设备/家长验收。本次未再次上传、编辑或确认六六三张真实草稿；城市大连/日期未知/0正式保持上轮已核验范围。本轮仅合成客户端，不代验云对象/AI地点质量。

Spec保持active/VERIFYING；实际设备与家长验收闭合后才能DONE并迁completed。Feature、BHV、Architecture、UI-001/018、设计索引、测试策略、Spec/索引与本地交付记录同步；当前合同不再要求首次勾选，历史批准源仅加Superseded by。未上传代码包/体验/提审/正式发布。

交付核对：14份受影响Spec/当前文档/证据/交付记录共311个本地链接目标存在；代码和当前合同无冲突。旧设计HTML源及新批准源SHA保持，旧manifest仅加局部Superseded by。`git diff --check`通过。后续只读报告增加的相对链接亦单独核验。
