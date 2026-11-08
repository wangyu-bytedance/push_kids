---
created: "2026-11-07"
updated: "2026-11-07"
type: evidence
status: recorded
owner: Codex
---

# DREV09 本地交付与 Review

本页保留原执行时点的结果。后续 0.1.19 上传及补充原生验证见[发布证据](../client-release-20261108/README.md)。

以下保留 DREV09 当次证据。当前页头及两档本地 Review 步骤见 [DESIGN-004 实现证据](../design004-20261107/README.md)。

- Evidence ID: `EVD-20261107-DESIGN003-LOCAL-01`
- Requirement: [DESIGN-003 Spec01](../../completed/DESIGN-003-THEME-VISUAL-REFINEMENT.md) TP-01..07；[DREV09批准清单](../../../docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-09/APPROVAL.md)；沿用[DESIGN-002 Spec08](../../completed/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)。
- Subject: HEAD `925a8a49ea972f365e17ed1504575ac49deef65a` 加未提交实现，[源码清单](source-manifest.json)绑定最终前端、测试和验证工具；设计源/导出另有冻结SHA。
- Scope: `IMPLEMENTED_LOCAL / VERIFYING / NOT_UPLOADED`。只改记录/报表呈现、主题语义材质、验证工具及文档。BHV-046、Architecture01、API、身份、数据和上传路径不变。

## 本地 Review

在微信开发者工具中打开或导入仓库的 `apps/miniprogram` 项目，点 **编译**。手动操作模拟器不需要打开服务端口。选择 320×568、390×844、430×932 三种尺寸，从 **设置 → 底部「界面风格」** 切换六个主题。每个主题重点检查：

1. **报表**：「一点一滴，看得见」在标准字号下完整一行，孩子入口在下一行；放大字体时可换行。
2. **记录**：五新主题横幅完整显示，类型菜单能展开、切换旅行日记、点外面关闭；长孩子名和上传中不遮挡菜单。原始风格无新增横幅。
3. **上传入口**：原始相机插画保留；新主题显示对应颜色的相机图标，不再嵌套横幅。选图后确认原照片预览、移除、忙态与错误仍可区分。
4. **今日 / 设置**：今日复习卡点「其他反馈」，检查内层反馈框；对照深海夜色的错误、输入、选中与弹层边界，以及切换主题后已填草稿是否保留。

[批准设计预览](../../../docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-09/index.html)可并排对照。它是设计稿，视觉和操作以本地小程序为准。对准备发布的源码，原生自动验证使用下述合成数据副本，不调用生产业务。

## 已执行的验证

| TP | 方法与结果 |
|---|---|
| 03 媒体角色 | `node --test tests/frontend/theme-media.test.js`；[Red](red-media.log)中成长花园错误返回整张横幅，修复后[合同通过](green-media.log)。原始相机资源仍保留，其他五主题使用既有相机图标。真实图像状态的原生验收另记。 |
| 05 共享业务与主题 | `npm test`，同仓库[基线](baseline-frontend.log)368 PASS，最终[结果](frontend.log)369 PASS、0 FAIL、0 SKIP。包含主题状态、组件生命周期、保存草稿和上传相关回归。 |
| 07 静态与资源 | `npm run lint:miniapp`、`validate_miniprogram.py`、`check_themes.js --baseline=e221d8d61bc164dc27b2309e62f04d3bcf4360ba`、`check_architecture.py`、当前设计政策及DREV09批准清单均通过；命令/退出码见[检查明细](checks.json)。两个JS验证工具语法、Python验证工具Ruff/format通过；初次局部Ruff因参数表达式过长失败，折行后通过。 |
| 07 资源与再生 | [六主题合同](contracts.json)：主题插画141,499字节、总源码1,322,435字节，保留各主题文字色对与载荷结果。[首屏资源再生](generation.json)前后SHA一致；5份DREV09原始设计源与164个导出SHA全部一致。无新依赖/插画/字体。 |

## 原生、设备与发布边界

首轮最终候选[原生启动](native-start.log)返回246，服务端口关闭。随后用本机端口[成功启动官方自动化](native-recovery.log)，原生 API 确认模拟器实际尺寸为 390×844。隔离副本使用合成数据，69 份页面与组件的 WXML/WXSS 和本轮源码一致；原生补测使用独立目录，保留 Spec08 的历史证据。

- [390×844 专项采集日志](native-focus-390.log)：记录页连续三次遇到自动化响应超时或对象无法克隆，完成 0 组节点与截图配对。报表和其余状态未运行。
- [独立截图探测](native/390/visual-probes.json)：原始记录页有一张可读截图；请求成长花园后，逻辑层报告已切换，但画面仍显示原始风格，不能算成长花园通过。报表探测未返回可验证的页面。截图单独保留以便排查，不计入矩阵。

后续恢复按[当前测试策略](../../../docs/quality/TEST-STRATEGY.md)选 390×844 和 430×932，并写入独立目录。以下为原三档矩阵的历史执行计划：

```bash
uv run python tools/prepare_theme_native.py /private/tmp/push-kids-themes-review-20261107
node tools/theme_native.js 320 9631 --refinement --project=/private/tmp/push-kids-themes-review-20261107 --output=specs/evidence/design003-20261107/native
```

先通过官方 CLI `auto` 打开该合成项目和自动化端口，再在模拟器分别选择 320、390、430 对应的实际尺寸。完整矩阵为 17 路由×6×3 + 8 共享态×6×3 + 7 补充态×6×3 = 576 组。320/430 未执行；物理设备、读屏、大字、键盘、完整原生业务操作、点击稳定性及用户 Review 待验。无后端或迁移 diff，后端业务和实库测试不适用。没有上传、体验、提审或正式发布。[发布记录](../../../docs/deploy/releases/20261107-theme-refinement-local.md)。
