# DREV-20261021-HERO-ARC-REMOVAL-01 — 背景细弧线清理

- Status: APPROVED
- Approved by: 用户，2026-10-21
- Approval evidence: 展示Spec01/DREV01及对比后，用户要求“还有很多其他的背景 有类似的问题 一起修复掉”；当前方案本就覆盖全部共享卡片，按同一方案实施，无额外视觉变化。
- Task Spec: [BUG-SPEC-20261021-HERO-ARC-01](../../../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md)
- Baseline: FDB-20260913-04 APPROVED
- Engineering contract: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected UI: UI-001、UI-009、UI-011
- Direction: 保留现有暖白纸面、浅绿受光与原有插画，去掉卡片右下角类似头发丝的细弧线。

## 可见改动

共享 `.pk-hero::after` 的圆形细描边在卡片边界被裁成弧线。候选仅删除这条装饰规则及对应注释；
没有重绘 PNG。所有引用共享类的页面一起生效：今日正常/引导、记录、日程、报表、设置四张卡、
家庭与成员邀请卡、提醒设置正常/中性卡。保留原文案、布局、按钮、表单、图表、授权与图片失败回退。

## 可编辑来源与导出

- `render.cjs` 从当前 WXML/WXSS 和既有 synthetic fixtures 生成自包含 HTML，仅在候选副本删除规则，未修改生产源码。
- `*-320x568.html`、`*-390x844.html`、`*-430x932.html` 是可直接打开和编辑的设计源，图片均内嵌。
- 每个状态导出 320×568、390×844、430×932 竖屏 PNG，DPR 1；设置额外导出滚到最后一张卡的视口。
- [对比预览](comparison.html) / [对比图片](comparison.png) 展示今日卡片修改前后。
- 三份候选清单：`snapshots/UI-001/`、`snapshots/UI-009/`、`snapshots/UI-011/` 下本 DREV 的 `APPROVAL.md`。
- 各 HTML 与 PNG 的 SHA-256 记入对应清单。既有获批设计源/清单不变。

## 验证边界

`render-audit.json` 保存所有候选的弧线伪元素、修改前后 hero 位置/尺寸、图片解码、运行错误与远程请求检查。
这些是设计期 HTML 辅助证据。批准后仍须运行生产前端回归、静态及设计检查，并采集原生三视口截图，
核对卡片与现有控件几何、长内容与可访问性，完成 iOS/Android 真机视觉验收；HTML 不能代替原生验收。
资源预算沿用 1.5 MiB，触控目标沿用至少 44px；本方案不新增运行时资产、依赖、请求、交互或日志。

## 批准与状态

用户已批准 BUG-SPEC-20261021-HERO-ARC-01 与本 DREV 的全局共享方案；实现与验收状态以任务Spec和质量证据为准。
批准不代表上传、体验、审核或正式发布。完成验收前 Spec 保留 active。获批HTML/PNG保持不可变。
