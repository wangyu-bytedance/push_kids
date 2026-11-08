# DESIGN-005 Spec01 本地验证

用户于 2026-11-08 批准 DESIGN-005-SPEC-01 与 DREV-20261108-CHILD-SWITCH-01。批准的 HTML 源和 252 张导出按原 SHA-256 冻结。此处为生产 WXML/WXSS 的模拟器与静态证据。[Spec](../../active/DESIGN-005-CHILD-SWITCH-HEADER.md) · [批准清单](../../../docs/design/frontend/snapshots/UI-001/DREV-20261108-CHILD-SWITCH-01/APPROVAL.md)

## 原生验证

使用微信开发者工具在隔离项目内运行，生产 WXML/WXSS 原样保留，加载与请求接入合成数据。模拟器用 `wx.getWindowInfo()` 确认逻辑尺寸，用原生节点与 PNG 证明布局。源文件哈希和逐图哈希均复算。[核验汇总](verification.json)

| 视口 | 六主题 × 15 个场景 | 证据 |
|---|---:|---|
| 320×568 | 90 PASS | [矩阵](native/320/matrix-child-heading.json) · [源清单](native/320/source-sha256.json) |
| 390×844 | 90 PASS | [主矩阵 89 组](native/390/matrix-child-heading.json) · [自动化桥超时后单组补跑](native/390/matrix-child-heading-original-today.json) · [源清单](native/390/source-sha256.json) |
| 430×932 | 90 PASS | [矩阵](native/430/matrix-child-heading.json) · [源清单](native/430/source-sha256.json) |

15 个场景覆盖今日、日程、学习记录、旅行日记、报表、设置、独立足迹、无档案、单档案、长昵称、记录类型菜单、学习记录保存中、报表缺图、日程隐藏装饰及只读设置。每个场景检查标题和孩子切换的同行与右缘、适用的 44px 触区、标准报表单行、背景显隐或记录菜单的相对层级。

- 三档原始风格日程和报表各有 11 个节点在背景显隐前后完全相同。人工查看了原始两页和深海夜色记录菜单。[日程](native/430/original--calendar.png) · [报表](native/430/original--reports.png) · [记录菜单](native/430/midnight--record-menu.png)
- 三档今日、日程、报表和设置各 24 组实际点击通过。覆盖打开、取消不变更及选择第二个档案。390 并行时一次选中点击未生效，单独复跑 24 组通过。[320 孩子弹层](native/320/child-sheet-actions.json) · [390 孩子弹层](native/390/child-sheet-actions.json) · [430 孩子弹层](native/430/child-sheet-actions.json)
- 430 档六主题记录菜单打开、外部关闭和双向切换通过。六组风格操作同步页面、组件和本机偏好，保留草稿且零业务请求。[记录菜单动作](native/430/header-record-actions.json) · [风格动作](native/430/actions.json)
- 320 与 390 档六主题菜单开合和双向切换通过，切到旅行时原生组件内只出现嵌入式足迹，没有第二个标题入口。[320 记录菜单与嵌入检查](native/320/header-record-actions.json) · [390 记录菜单与嵌入检查](native/390/header-record-actions.json)
- 390 档原始风格学习记录的系统 picker 实际打开、取消、滚动到第二项并确认通过，合成加载刷新档案。旅行分支和独立足迹只完成对应布局与记录宿主检查，系统 picker 完整选择流程未验收。[选择前](picker-390/learning-open.png) · [取消状态](picker-390/learning-cancel.json) · [滚动后的选择](picker-390/learning-selected.png) · [确认状态](picker-390/learning-selected.json)
- 中间布局在 430 档记录和旅行各六个主题测得切换入口与外层行相差 22px。修正标题行结构后，当前矩阵通过。[修正前矩阵](baseline/matrix-child-heading.json) · [修正前记录节点](baseline/original--records.json)

## 自动化与资源

- `npm test` 370 PASS，`npm run lint:miniapp`、`node --check tools/theme_native.js` 和 `uv run python tools/validate_miniprogram.py` PASS。[前端测试](frontend-tests.log)
- `node tools/check_themes.js` 六主题合同 PASS。现有主题资源 141,499 字节，主题图片没有新增或替换。前端源码 1,320,312 字节，较 0.1.19 冻结源增加 110 字节。[主题报告](theme-contracts.json) · [上次上传源清单](../client-release-20261108/source-manifest.json)
- `uv run python tools/check_architecture.py` 五条策略、156 模块 PASS。`uv run python tools/validate_design_evidence.py --check-current-policy` 及本设计批准清单的独立校验 PASS。
- 系统大字、读屏、iOS/Android 真机和用户 Review 为 NOT_RUN。后端测试与部署在本次纯前端呈现改动之外。

## 现状和交付

已核对并同步 UI-001、UI-018、FEAT-001、FEAT-012、行为目录、架构、测试策略与发布手册。当前文档区分 0.1.19 已上传范围和本地标题行增量。原设计快照只加局部接管指针，部署状态和版本基准沿用已有记录。自动化发布的官方 API 或 SDK 优先规则同步到 AGENTS.md 和发布手册。

本地 Spec 位于 `active/`，状态 VERIFYING。匹配源码取得微信开发上传回执后按 GOV-002 归档 DONE，验收记录独立保留。
