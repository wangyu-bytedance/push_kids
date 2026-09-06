# 微信小程序平台 API 基线与改造清单

- Status: `CURRENT_AUDIT / IMPLEMENTATION_PENDING_APPROVAL`
- Revision: `WX-API-BASELINE-20260905-01`
- Applies to: `apps/miniprogram`
- Related Feature/UI: `FEAT-001` / `UI-001`
- Related engineering contract: `FEC-20260830-01`
- Proposed implementation Spec: `BUG-SPEC-20260905-02`
- Last audited: 2026-09-05（静态代码与官方 API 文档；真机兼容矩阵未执行）

本文只收录当前产品实际使用或近期改造需要使用的微信小程序 API。官方
[小程序 API 总索引](https://developers.weixin.qq.com/miniprogram/dev/api/) 是参数、最低基础库、
平台支持、废弃状态和回调语义的权威来源；不能用博客示例或开发者工具单次成功替代官方契约。
云托管调用与身份边界仍以
[`docs/operations/WECHAT-CLOUD-HOSTING.md`](../../operations/WECHAT-CLOUD-HOSTING.md) 为准。

## 1. 版本与兼容策略

- 项目发布最低基础库建议固定为 `2.23.0`。原因是当前发布路径依赖
  `wx.cloud.callContainer`，并使用 GET、POST、PATCH、DELETE；较旧基础库不能作为受支持运行时。
- 微信公众平台的“基础库最低版本”和微信开发者工具的调试基础库都要显式设置并记录。仓库中的
  `project.config.json` 只解决开发工具可复现性，不能替代公众平台的最低版本设置。
- 同时用当前稳定基础库和最低基础库 `2.23.0` 验证，至少覆盖代表性 iOS、Android 真机。
- 新增或替换任何 `wx.*` API 前，必须在官方页面确认最低版本、低版本行为、Promise/Callback
  支持、插件/桌面/鸿蒙差异、隐私要求和废弃状态。
- 即使设置了最低基础库，关键入口仍需做能力检测；不支持时提供明确升级提示和仍可用的文字录入，
  不得静默回退到公网 API。

## 2. 当前 API 清单

| API/能力 | 当前位置 | 当前用途 | 必须保持的约束 |
|---|---|---|---|
| `wx.cloud.init` | `app.js` | 初始化生产云环境 | `onLaunch` 全局一次；失败不能切公网 |
| `wx.cloud.callContainer` | `utils/api.js` | 业务 JSON 请求 | env/path/method/service 正确；检查 HTTP 状态与业务错误 |
| `wx.cloud.uploadFile` | `utils/cloud-media.js` | 图片直传私有云存储 | 只用服务端签发路径；不持久化 fileID；进度可观察 |
| `wx.request` / `wx.uploadFile` | `utils/api.js` | 本地开发回退 | 生产 `useCloud=true` 时不可触达；不能成为云失败降级路径 |
| `wx.chooseMedia` | `pages/records/index.js` | 相机单拍、相册多选 | 只选图片、最多 9 张；取消与权限/能力失败分开处理 |
| `wx.getImageInfo` | `utils/cloud-media.js` | 获取图片声明格式 | 只作客户端提示；服务端仍验证魔数、格式和大小 |
| `wx.getFileInfo` | `utils/cloud-media.js` | 获取大小 | 目前可用但与 `chooseMedia.tempFiles[].size` 重复 |
| `wx.getStorageSync` / `wx.setStorageSync` | `app.js` | 当前孩子选择 | 只能保存非敏感偏好；不得保存身份、fileID、图片或正文 |
| `wx.navigateTo` / `wx.navigateBack` / `wx.switchTab` | 页面代码 | 页面与 Tab 路由 | 参数来自受控 ID；失败不得造成重复写入 |
| `wx.showToast` / `wx.showModal` | 页面代码 | 轻提示与确认 | Toast 只作补充；关键失败需持久错误和重试入口 |

暂不需要引入定位、通讯录、蓝牙、剪贴板、支付、分享、广告、扫码或本地持久文件 API。新增这些能力
必须先有已批准的 Feature/Design/Privacy 范围，不能因为总索引提供了 API 就直接接入。

## 3. 当前需要改造的代码

### P0 — 体验版验收前必须完成

1. **运行时能力门禁**
   - `app.js` 检查 `wx.cloud`、`wx.cloud.callContainer` 和 `wx.cloud.uploadFile`。
   - `records/index.js` 检查 `wx.chooseMedia`；不支持时保留文字录入并提示升级微信。
   - 公众平台最低基础库设为 `2.23.0`，仓库记录对应开发工具调试版本。

2. **媒体权限与失败恢复**
   - 为 `wx.chooseMedia` 增加 `fail` 处理，区分用户主动取消、能力不可用和相机/相册权限失败。
   - 权限失败提供可行动说明；不得把取消显示成错误，也不得阻断手动文字记录。
   - 保持用户已经填写的文字、时间和已选照片，不因可恢复失败清空表单。

3. **网络错误契约**
   - `utils/api.js` 保留安全的错误类别、HTTP 状态、平台错误码和非敏感 request ID，页面不接触原始
     Header 或包含身份信息的错误对象。
   - 为 `callContainer` 设置不超过平台上限的显式 timeout。
   - 自动重试仅用于安全读取，或携带稳定幂等键的写请求；次数有限并带退避。401/403、输入错误和
     状态冲突不得自动重试。
   - 页面载入失败继续显示持久错误和“点此重试”；表单提交失败不能只依靠可能被截断的 Toast。

### P1 — 公开发布前完成

4. **上传取消与中断恢复**
   - 封装并保留 `UploadTask`，允许用户取消正在进行的上传，防止重复点击。
   - 取消后保持服务端草稿/ticket 状态可恢复；orphan 清理的 Worker 架构决策只引用
     `ADR-001 / TD-001`。
   - 覆盖前后台切换、弱网、单图成功多图中断、重复继续和取消竞态。

5. **版本更新处理**
   - 评估接入 `wx.getUpdateManager`，在新版本已就绪时提示重启，降低旧客户端继续调用新服务契约的
     风险。它不能替代 API 向后兼容和灰度发布。

### P2 — 可随上述改造顺带清理

6. **复用媒体选择结果**
   - 页面保留 `{tempFilePath, size, fileType}`，优先使用 `tempFiles[].size`，删除无必要的第二次
     `wx.getFileInfo` 调用。
   - `wx.getImageInfo` 只用于格式提示；安全判断继续由服务端完成。

7. **统一交互反馈适配器**
   - 集中处理短成功 Toast、持久错误和确认对话框的选择规则，但不要引入新的通用 UI 框架。
   - 成功图标 Toast 文案保持短小；长错误进入页面状态或 Modal，不依赖 Toast 完整展示。

## 4. 明确不需要改造的部分

- `callContainer` 的 env、path、method、`X-WX-SERVICE` 结构正确，无需改成公网 `wx.request`。
- 微信身份无需客户端 `wx.login` 后自行传 OpenID；服务端继续使用专用链路注入的 `X-WX-*`。
- 图片继续走 `wx.cloud.uploadFile`，无需 base64 或 multipart 经过 `callContainer`。
- `selectedChildId` 是安全显示偏好，可以继续存储；不得扩大为本地授权状态。
- 导航 API、Modal 删除确认和当前 9 图上限没有发现需要更换 API 的问题。

## 5. 验证矩阵

| Test point | Required evidence |
|---|---|
| `TP-API-001` | 最低基础库下 `wx.cloud`、callContainer、uploadFile、chooseMedia 能力检测与升级提示 |
| `TP-API-002` | 当前稳定基础库主流程不回归，云失败不切公网 |
| `TP-API-003` | 相机/相册取消、拒绝、系统设置恢复和文字录入 fallback |
| `TP-API-004` | 200/4xx/5xx、timeout、断网、冷启动错误分类与有界重试 |
| `TP-API-005` | 1/9 图进度、中断、恢复、取消、重复点击和 orphan 清理 |
| `TP-API-006` | Storage、日志、错误、埋点不含 OpenID、fileID、图片和儿童正文 |
| `TP-API-007` | `npm test`、`npm run lint:miniapp`、`tools/validate_miniprogram.py` |
| `TP-API-008` | iOS、Android、DevTools 在 320×568、390×844、430×932 的相关状态证据 |

以上改造会影响兼容提示、权限失败、表单错误和上传取消等可见状态。开始编码前必须批准
`BUG-SPEC-20260905-02`；如新增可见布局或交互超出现有设计契约，还需批准对应 Design Revision。
