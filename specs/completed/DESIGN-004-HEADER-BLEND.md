# DESIGN-004 — 六主题页头统一 (Spec Lite)

- Status: DONE
- Risk: R1，现有页头的可逆呈现变更
- Owner / Reviewer: 产品负责人（用户）
- Implementer: Codex
- Date: 2026-11-07
- Spec revision: DESIGN-004-SPEC-01
- User confirmation: 产品负责人，2026-11-07，直接回复本 Spec 与 DREV 的设计确认请求「好的 在多个风格进行落地」。批准按六主题落实到本地供 Review。
- Affected Feature IDs: FEAT-001 的全局六主题呈现。FEAT-002 家庭流程、FEAT-003 提醒和 FEAT-006 清理是共享样式宿主。
- Feature current-state: [FEAT-001](../../docs/domain/features/FEAT-001-push-kids-mvp.md) 的 `FEAT-STATE-20261107-THEMES-03`，[FEAT-002](../../docs/domain/features/FEAT-002-family-collaboration.md)、[FEAT-003](../../docs/domain/features/FEAT-003-notification-channel.md)、[FEAT-006](../../docs/domain/features/FEAT-006-data-cleanup-and-family-reset.md)。
- Feature/UI merge owner: Codex，验证后更新 FEAT-001 全局呈现及相应 UI 的已实现事实和证据。

## 设计和工程影响

- Frontend design / engineering impact: YES。共享装饰层、标题可读性、响应式几何、缺图、长文案和记录弹层。
- UI IDs: [UI-001](../../docs/design/frontend/ui/UI-001-parent-miniapp.md)、[UI-009](../../docs/design/frontend/ui/UI-009-family-members.md)、[UI-010](../../docs/design/frontend/ui/UI-010-family-access.md)、[UI-011](../../docs/design/frontend/ui/UI-011-reminder-settings.md)、[UI-016](../../docs/design/frontend/ui/UI-016-data-cleanup.md)。
- Frontend baseline: `FDB-20261107-05` / `FEC-20261107-AGENT-DEVICE-MATRIX-03`，六主题、390×844 与 430×932。
- Prior Design Revisions: DREV06（主题风格）、DREV08（入口）、DREV09（标题、记录比例、上传装饰及边框）。本修订接管重叠的页头材料与布局。
- Approved Design Revision: `DREV-20261107-HEADER-BLEND-01`。[可编辑设计](../../docs/design/frontend/prototypes/DREV-20261107-HEADER-BLEND-01/index.html)与[快照清单](../../docs/design/frontend/snapshots/UI-001/DREV-20261107-HEADER-BLEND-01/APPROVAL.md)绑定 SHA-256。
- Required exports: 六主题 × 两视口 × 18 场景。覆盖 13 个实际路由、创建/邀请码与清理列表/确认分支，以及缺图、大字长标题、记录菜单。
- Task Spec / Design approval: `DESIGN-004-SPEC-01` + `DREV-20261107-HEADER-BLEND-01`。工程偏差 NONE。
- 工程检查覆盖共享组件/状态、无障碍、文字与几何、图像资源和原生兼容。预算沿用 FEC，正文对比至少 4.5:1，常规触区至少 44px，内容包含误差最多 1px。现有表单、图表、数据/隐私、观测和运动的行为合同继续适用，本提案只改变静态装饰。

## 1. 问题和目标

用户本地 Review 的两张成长花园截图显示，报表页像一个圆角卡片，今日页则显示矩形图片。代码中，报表和日程头部带 `.pk-hero`，继承圆角、边框和卡片容器样式；今日等普通页头没有该类。两种页头都使用有实色边缘的 JPEG，视觉上会和页面底色形成分界。记录另用独立的 `widthFix` 层保存完整比例。

统一页头为页面的一部分。它与内容共享底色，插画四边渐入当前主题底色，保留主体和各图自然比例。五个主页面的标题叠在图上，详情、表单等子页在素底放置标题以便换行，插画接在文字下方。原始风格用干净的底色和原有局部小插画。图片失败时标题与控件落回页面语义前景色。

## 2. 范围与影响

- 五个 Tab 页头，以及现有主题页头宿主中的课外活动、学习详情、草稿确认、家庭引导/加入/申请、提醒设置和删除配置。页面卡片、应用导航和系统顶栏沿用各自视觉角色。
- 记录的上传入口、报表的标题字号与首行规则、已有下拉/返回、主题偏好、表单、授权及业务合同继续由已批准的 Spec 维护。
- UI-001 负责共享页头合同。家庭、提醒和清理 UI 按各自实际宿主记录应用。行为目录 BHV-046、架构 Architecture01、测试及发布记录按最终 diff 核对，批准历史快照保持版本绑定。

## 3. 设计视图和取舍

`现有页面主题适配器 → registry 的颜色/本地插画 → theme-header 的画面层 → 页面原有标题、选择器和弹层`。

- 时序：沿用主题切换和原有图片加载回调。成功显示插画，失败退回同色素底；再次应用主题沿用现有失败重置。
- 状态：`原始/无图 → 素底`，`插画可用 → 融合页头`，`图片失败 → 素底`。记录菜单的开关与页头图状态独立。
- 架构图：N/A，沿用已有 registry、适配器和共享样式依赖，没有新生产模块或反向依赖。

| 方案 | 取舍 | 决定 |
|---|---|---|
| 共享页头装饰层，渐变使用主题底色 | 适配全部宿主与缺图，复用现有 JPEG，需验证原生叠层与前景对比度 | 推荐 |
| 各页统一圆角图片卡片 | 形状一致，仍有明确的独立卡片边界 | 备选 |
| 每个主题重新制作透明头图 | 能定制过渡，增加资源加工和包体成本 | 备选 |

## 4. 实施范围

| 位置 | 变更 |
|---|---|
| `apps/miniprogram/styles/theme.wxss` | 统一页头画面层，固定插画自然比例，增加底色融合和缺图前景色，前景与菜单独立叠放 |
| `apps/miniprogram/presentation/theme/header-art.wxml`、现有 13 个宿主的 WXML 和三页 WXSS | 15 处挂载同一画面层，清理报表/日程页头的卡片外观和记录页专用布局。现有主题语义角色足够，无需修改 registry 或生成 token |
| 验证、Feature/UI/架构/发布记录 | 采集最终差异对应的证据，核对与当前事实一致 |

## 5. 验收与测试

| 点位 | 验收 | 证据 |
|---|---|---|
| TP-01 | 六主题两视口的实际宿主都用同一页头规则，插画边缘渐入页面并保留主体 | 设计 216 组 PASS，390×844 和 430×932 原生各 108 组 PASS |
| TP-02 | 原始及缺图态保留可读标题、正文和控件。常规对比 ≥4.5:1，长标题和大字能换行，标准报表标题仍一行 | 设计最低抽样 4.74:1；两档缺图、长标题换行与报表单行 PASS；系统大字和其他辅助功能 NOT_RUN |
| TP-03 | 记录类型菜单和孩子入口可达，打开菜单无裁切，常规触区 ≥44px，记录头图保持原比例 | 两档原生节点及各六主题菜单开合、点外关闭和双向切换 PASS |
| TP-04 | 本地资源与源码符合预算，保留主题偏好，无新增联网或业务请求 | 前端 370 项、适用静态与两档主题偏好动作通过，官方上传包体 1,254,694 字节 |

## 6. 当前阶段和下一步

Chromium 设计校验 PASS，六主题两视口共 216 张截图。通过画面几何、图片自然比例、报表标题单行、长标题换行和菜单层级检查。标题/副文案区域最低抽样对比为 4.74:1。两份 DREV 清单均通过对应状态与哈希校验，DREV09 仍按原视口矩阵核验。[本轮快照](../../docs/design/frontend/snapshots/UI-001/DREV-20261107-HEADER-BLEND-01/APPROVAL.md)记录导出尺寸与哈希。

已核对 Feature、行为目录、架构、各宿主 UI、测试策略和发布文档。用户随后要求“发布前端”，匹配源码于 2026-11-08 随 0.1.19 开发版上传，按 GOV-002 归档为 `DONE / specs/completed/`。真机、系统辅助功能和用户 Review 待验，完整验收为 PARTIAL。[原生及源码证据](../evidence/client-release-20261108/README.md) · [发布记录](../../docs/deploy/releases/20261108-client-0.1.19-upload.md)
