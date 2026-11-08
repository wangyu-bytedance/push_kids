# EVD — 2026-11-08 前端 0.1.19 开发版上传

上传候选包含 187 个文件，基于 `925a8a49ea972f365e17ed1504575ac49deef65a` 与已批准的前端差异。官方 CLI 上传成功，本地版本记录已推进到 0.1.19。体验、提审、正式发布待后续平台门禁。[发布记录](../../../docs/deploy/releases/20261108-client-0.1.19-upload.md) · [源清单](source-manifest.json) · [上传前校验](pre-upload-integrity.json)

| 检查 | 实际结果 |
|---|---|
| `npm install`、`npm test` | 依赖安装成功，370 PASS，零失败及跳过 |
| `npm run lint:miniapp`、`uv run python tools/validate_miniprogram.py` | PASS |
| `uv run python tools/check_architecture.py` | PASS，五项策略、156 个模块 |
| `uv run python tools/validate_design_evidence.py --check-current-policy` | PASS。DREV06、DREV08 使用 canonical 清单，DREV09、HEADER-BLEND 使用批准清单，四份校验通过 |
| `node tools/check_themes.js` | PASS。颜色、主题状态字节与离线资源检查见[输出](theme-contracts.json) |
| `git diff --check` | PASS |
| 微信开发者工具 `islogin`、`preview`、`upload` | 登录有效，预览 1,254,609 字节，上传 1,254,694 字节。[预览结果](preview-info.json) · [上传结果](upload-info.json) |
| `npm run --silent release:version:bump`、`npm run --silent release:version` | 上传成功后版本推进，当前为 0.1.19 |
| 生产兼容性 | 160 个冻结后端源文件与 040 一致。云状态 normal/100%/1，小程序容器七路 GET 均为 200，零业务写入。[运行状态](cloud-state.json) · [只读 smoke](cloud-smoke.json) |

## 原生证据

官方 CLI 启动 `auto`，通过 `wx` 窗口信息确认实际尺寸。将节点采集项目的生产 WXML、WXSS、插画等 101 个文件与冻结上传候选逐一核对。页头矩阵用 `node tools/theme_native.js <width> <port> --header-blend`，真实点击另用 `--header-actions`，主题动作另用 `--actions`。每档各有 108 组节点和 PNG，覆盖实际 13 路由、缺图、长标题、子页分支及菜单。两档各有六组记录菜单点击及六组设置页主题状态验证。主题状态验证使用原生页面方法，包含取消、应用、草稿保留、偏好恢复和零业务请求。

- 390×844 采用与上传候选哈希相符的 11/07 原生节点及截图。[矩阵](../design004-20261107/native/390/matrix-headers.json) · [主题动作](native/390/actions.json) · [生产文件哈希](native/390/source-sha256.json)
- 430×932 本次采集，108 组通过。[矩阵](native/430/matrix-headers.json) · [记录菜单](native/430/header-record-actions.json) · [主题动作](native/430/actions.json) · [执行日志](native-430.log)
- 430×932 的组合照片入口探针首次遇到序列化及超时，结果保留为失败。重开自动化后，针对页面自身采集节点，每种主题采集缺图、旅行、照片入口、上传中和上传失败五种状态，共 30 组通过。[首次日志](native-refinement-430.log) · [恢复日志](native-refinement-recovered-430.log) · [恢复矩阵](native/refinement-recovered/430/matrix-refine-media-failure,refine-travel,refine-photos,refine-uploading,refine-upload-error.json)

完整独立验收为 PARTIAL。全局 300 组、其余照片和共享组件状态、真机、系统读屏/大字、业务端到端及独立 Review 仍按各 Spec 留待补验。历史 DREV 的三档设计导出及原生历史结果保留各自的验证范围。备份保留检查为 NOT_RUN，站点策略拦截后实际数量由管理员核对。

## 文档归档

发布后逐项核对 Feature、BHV-046、Architecture01、设计基线、八份受影响的 UI 现状、测试策略和发布文档，按上传候选更新交付与验收状态。三份 Spec 归档 DONE，后续验收留在各自记录。复核了 187 个生产源文件哈希、246 张原生截图哈希、95 个版本和归档链接，以及四份批准设计清单。
