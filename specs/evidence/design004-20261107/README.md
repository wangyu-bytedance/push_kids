# 六主题页头本地验证与 Review

本页保留原执行时点的结果。后续 0.1.19 上传及补充原生验证见[发布证据](../client-release-20261108/README.md)。

- 证据 `EVD-20261107-DESIGN004-LOCAL-01` 绑定获批的 [DESIGN-004 Spec01](../../completed/DESIGN-004-HEADER-BLEND.md) 和 [DREV-20261107-HEADER-BLEND-01](../../../docs/design/frontend/snapshots/UI-001/DREV-20261107-HEADER-BLEND-01/APPROVAL.md)。
- 阶段为 `IMPLEMENTED_LOCAL / VERIFYING / USER_REVIEW_PENDING / NOT_UPLOADED`。设计批准导出和当前源码的原生证据分别记录。

## 本地 Review

1. 在微信开发者工具打开仓库的 [apps/miniprogram](../../../apps/miniprogram) 项目，点击 **编译**。
2. 进入 **设置 → 底部「界面风格」**，选择并应用原始风格、成长花园、星际探索、深海夜色、海洋或科技。
3. 建议先在成长花园来回切换 **今日 ↔ 报表**，对照之前两张截图。两页插画应自然融入背景，报表标题保持一行。到 **记录** 点「学习记录」，切到旅行日记再切回，确认菜单正常开合。
4. 对照原始风格的素底与局部小插画，以及深海夜色的标题和菜单。打开提醒设置或删除配置，可以看到子页标题排在插画上方。

| 390×844 原生样例 |  |
|---|---|
| 原始风格 | [日程](native/390/original--calendar.png) |
| 成长花园 | [今日](native/390/garden--today.png) · [报表](native/390/garden--reports.png) |
| 星际探索 | [今日](native/390/space--today.png) · [报表缺图](native/390/space--image-failure.png) |
| 深海夜色 | [今日](native/390/midnight--today.png) · [记录菜单](native/390/midnight--record-menu.png) |
| 海洋 | [今日](native/390/ocean--today.png) |
| 科技 | [今日](native/390/tech--today.png) |

[批准的交互对照稿](../../../docs/design/frontend/prototypes/DREV-20261107-HEADER-BLEND-01/index.html)用来对照设计。最终呈现以微信开发者工具或手机为准。

## 测试记录

| 点位 | 实际执行 |
|---|---|
| TP-01 设计 | Chromium 两视口、六主题、18 场景共 216 张导出。批准清单绑定尺寸、状态和哈希。 |
| TP-01 原生 | 390×844、基础库 3.17.4，共 108/108 组节点和截图。13 个路由覆盖 15 处共用挂载，另测缺图、长标题、记录菜单。零几何、截图或导航失败。成长花园横幅自然呈现为 390×152 逻辑像素。[原生矩阵](native/390/matrix-headers.json) |
| TP-02 字体和回退 | 设计对比度抽样最低 4.74:1。390×844 原生验证 24px 报表标题单行、子页长标题换行、原始无横幅及合成缺图回退。放大系统字体、读屏和键盘在待补范围。 |
| TP-03 实点 | 在 390×844 的原生记录页用官方自动化依次点击标题、菜单外部、标题、旅行日记、标题、学习记录，六主题均观察到预期状态。矩阵检查页头控件触区、菜单范围和头图比例。[操作状态](native/390/header-record-actions.json) · [实点日志](native-actions-390.log) |
| TP-04 自动化 | [旧行为基线](baseline-frontend.log) 369 项通过。[页头回归 Red](red-header.log) 在旧家庭引导页复现缺少共用插画层，[定向 Green](green-header.log) 通过。最终 [npm test](frontend.log) 370 PASS、0 FAIL、0 SKIP，覆盖主题切换/偏好恢复与既有共享业务。 |
| TP-04 静态及预算 | ESLint、小程序静态、架构、设计政策及两份批准 DREV、六主题合同和 diff 空白检查通过。设计证据校验器另有 13 项单测通过。17 路由总源码 1,320,202 字节，较 DESIGN-003 本地源码减少 2,233 字节。主题插画 141,499 字节沿用；无新资源、依赖或接口。[检查日志](static.log) · [主题合同](contracts.json) |

本次原生取证用离线合成副本，通过本地配置、合成状态和测试生命周期提供数据。101 份 WXML、WXSS 与本地资产逐文件匹配生产源码。边界读数来自 `wx.createSelectorQuery`，样式另用开发者工具 `Element.getStyles`，避免旧探针合并读取时的桥接序列化错误。合成缺图态验证回退呈现。逐图 SHA 和副本清单绑定当前证据。[证据绑定](source-manifest.json) · [副本清单](native/390/source-sha256.json)

收尾核对了 Feature、BHV-046、Architecture01、五份 UI、Spec、测试策略与发布记录。相对 DESIGN-003，18 份生产变更均为 WXML 或 WXSS，040 的 160 份后端发布源码 SHA 全匹配。当前文档区分已实施页头、前序 DREV09 视觉范围和最近一次实际上传。

## 待补和恢复

- 430×932 原生矩阵和实点为 NOT_RUN。取证时模拟器实际是 390×844，桌面处于锁屏。切到 iPhone 14 Pro Max 后，按下方命令重放。原生 runner 要求实际 API 尺寸和请求尺寸一致。
- iOS / Android 真机、系统大字、读屏、键盘为 NOT_RUN。用户本地 Review 待执行。后端和数据库迁移门禁不适用本次页头差异。
- 无官方包体或上传回执。前端云端当前为 0.1.18 开发上传，DESIGN-004 留在 active，状态 VERIFYING。[本地交付记录](../../../docs/deploy/releases/20261107-theme-refinement-local.md)

```bash
uv run python tools/prepare_theme_native.py /private/tmp/push-kids-header-blend-native-20261107
# 用微信开发者工具 CLI auto 打开该隔离项目并指定 9641 为自动化端口
# 在模拟器选择实际 430×932 尺寸后执行
node tools/theme_native.js 430 9641 --header-blend --project=/private/tmp/push-kids-header-blend-native-20261107 --output=specs/evidence/design004-20261107/native
node tools/theme_native.js 430 9641 --header-actions --project=/private/tmp/push-kids-header-blend-native-20261107 --output=specs/evidence/design004-20261107/native
```
