# 当前旅行入口 — 剩余原生矩阵采集

2026-11-01续接已按本采集器完成真实390×844/430×932两宿主各7态共28组PASS；
加既有320两宿主14组，共42组原生节点/PNG。实际机型选择、生产源/截图SHA核对见
[完整矩阵](../client-release-20261101/native-matrix-resumed.json)，本地动作和微信039健康见
[当前报告](../../../deploy/releases/20261101-client-upload-attempt.md)。下方NOT_RUN均限定2026-10-31预检当时，
原预检与采集器保持，不重复覆盖证据；随后用户已确认正向云照片/双账号门禁，
0.1.17成功上传并bump，当前平台状态见[上传报告](../../../deploy/releases/20261101-client-0.1.17-upload.md)，设备验收独立开放。

批准范围：入口精简Spec01 / Architecture01 / DREV01；两宿主各7态，真实320×568、390×844、430×932。当前320两宿主14组证据及生产源绑定在[native-approved-source.json](native-approved-source.json)，保持原文件和摘要。

[参数化采集器](native-current-matrix-collector.js)由本机既有双宿主采集器复制，原文件未改；只增加宿主、宽度和端口参数，映射精确screenHeight、更新输出名与边界、拒绝覆盖已有证据，并在调用夹具前验证原生尺寸。原字体、触控、滚动可达、三等列与历史manual断言及合成禁云守卫保持。

本轮实际执行：`node --check` PASS。以`standalone 390 9592`连接成功，但当前原生模拟器仍为320×568，尺寸守卫停止并输出`switch the native simulator to 390x844 before collection`。没有生成390验收文件、改变页面夹具或调用云业务。390/430采集仍NOT_RUN。

19:57[原生只读预检](native-current-matrix-preflight.json)确认离线守卫、实际宽320/screenHeight568、DPR2和基础库3.16.2；预检未调用夹具或云业务。[静态检查](upload-preflight-static02.json)记录采集器语法结果；旧320摘要重新核对见[闭合核对](upload-preflight-closure02.json)。

采集只允许已准备的`/private/tmp/push-kids-travel-diary-native-20261025`合成离线项目：`useCloud=false`、`familyId=synthetic`。生产项目或不符实际尺寸立即拒绝；不得mock systemInfo、注入尺寸或用HTML代替。监听端口目前9592，如重启需以官方automation实际端口为准。

操作者在微信开发者工具的合成离线项目中先切换模拟器至390×844，再由代理执行：

```bash
node docs/quality/evidence/client-release-20261031/native-current-matrix-collector.js standalone 390 9592
node docs/quality/evidence/client-release-20261031/native-current-matrix-collector.js embedded 390 9592
```

两宿主采集完成后，真实切换至430×932，再执行：

```bash
node docs/quality/evidence/client-release-20261031/native-current-matrix-collector.js standalone 430 9592
node docs/quality/evidence/client-release-20261031/native-current-matrix-collector.js embedded 430 9592
```

输出分别为`native-approved-390-{standalone,embedded}`、`native-approved-430-{standalone,embedded}`，每组包含empty/drafts/legacy/loading/error/viewer/archived的节点JSON和PNG、SHA-256及实际SDK/视口。每态errors须为空；字体≥14px、普通触控≥44px、主CTA≥48px、无横向越界、滚动后CTA可达及原三等列规则沿用既有误差阈值。采集结果仅证明当前源的合成原生布局，不代完整动作、设备/可访问性、039定向云或双真实账号验收。

2026-10-31预检当时前端未上传/基准0.1.16；当前0.1.17已上传/bump，039照片回看/双账号门禁由用户确认。
旧灰度0%步骤已过期，后续体验/审核按[当前上传报告](../../../deploy/releases/20261101-client-0.1.17-upload.md)继续。
