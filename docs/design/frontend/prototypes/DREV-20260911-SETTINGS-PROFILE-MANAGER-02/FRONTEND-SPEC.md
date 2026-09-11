# DREV-20260911-SETTINGS-PROFILE-MANAGER-02 — 学习档案面板视觉降噪

- Status: APPROVED
- Related Spec: `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01`
- Affected UI: `UI-001 / pages/settings/index / child sheet`
- Baseline: `FDB-20260906-03`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260906-04`
- Figma anchor under requested FEAT-001 waiver: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Visual direction

温暖纸张感、平面分隔、内容优先、操作克制：姓名与年级建立清楚层级，状态以小号文字表达，次要编辑
收为透明线性图标，新增回到列表动作，不再用连续米色色块和大虚线框制造视觉噪音。

## Proposed composition

```text
学习档案                                             ○ ×

┌────────────────────────────────────────────────────┐
│  旺   旺仔                                   ✎     │
│       一年级 · 当前使用                            │
├────────────────────────────────────────────────────┤
│  六   六六                                   ✎     │
│       学前-中班                                    │
├────────────────────────────────────────────────────┤
│  ＋   新建学习档案                              ›  │
└────────────────────────────────────────────────────┘

已归档
┌────────────────────────────────────────────────────┐
│  满   满满                                      恢复 › │
│       二年级                                       │
└────────────────────────────────────────────────────┘
```

## Component decisions

- 档案主体：姓名 15px/500，年级 12–13px muted；不再把 `姓名 · 年级` 放成一条粗文本。
- 当前状态：跟随年级显示“当前使用”，使用文字而非只靠绿色；删除右侧状态 pill，给姓名留宽度。
- 编辑：显示既有 `ico-pen-mute` 16–18px；外层透明 88×88rpx，`catchtap="editChild"`，无底色、边框或圆角块。
- 切换：档案主体仍是整行，pressed 时使用既有 `primary-wash`；编辑点击不触发行切换。
- 新增：并入在用档案 rowlist 尾部，使用 tinted 72rpx 加号 mark + “新建学习档案” + chevron；不再使用虚线 CTA。
- 归档：保留独立“已归档”标题和列表，恢复仍是轻量文字 + chevron，不与编辑图标混淆。
- viewer：只显示档案信息和切换；铅笔、新增、归档管理均不渲染。
- limit：新增行不渲染，列表下显示既有 `childLimitHint`。

## Responsive and accessibility matrix

| State | 320×568 | 390×844 | 430×932 |
|---|---|---|---|
| one/many active | name/grade shrink and truncate before 88rpx edit target | balanced reference | max sheet width retained |
| viewer | no empty action column | rows remain switchable | same hierarchy |
| limit | help wraps below list | one/two-line reason | no stretch |
| archived | vertical sheet scroll; restore stays in row | section separation | no excess whitespace |

- 触控目标：档案行与编辑图标点击区均 ≥88rpx。
- accessible names：行“切换到{name}”；图标“编辑{name}的档案”；新增“新建学习档案”。
- 当前状态同时由文字表达；不以颜色作为唯一线索。

## Approval boundary

批准即授权：只重做学习档案面板的信息排版和控件外观；保留 DREV-01 的入口、功能、权限、路由和状态机。
请明确批准：

- `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01`
- `DREV-20260911-SETTINGS-PROFILE-MANAGER-02`
- 本修订沿用 FEAT-001 scoped Figma waiver，且该 waiver 在公开生产发布前到期

Approval evidence: 用户于 2026-09-11 回复“落地”。批准快照：
`docs/design/frontend/snapshots/UI-001/DREV-20260911-SETTINGS-PROFILE-MANAGER-02/APPROVAL.md`。

## Local implementation evidence

- 实现：姓名/年级两级信息、次级“当前使用”、透明 88rpx 铅笔点击区、列表内“新建学习档案”；旧块状
  “编辑”、状态 pill 和独立虚线新增框已删除。
- 自动化：focused frontend 32 passed；全量 frontend 140 passed；ESLint、小程序静态
  `pages=15 source_bytes=630368`、架构 `checked=3`、图标生成幂等与 diff check 通过。
- 预览：真实 AppID local preview 575988 bytes，未上传；sheet/viewer/limit 的 320/390/430 HTML fixture
  共 9 个已生成。PNG 因缺少 Playwright Chromium executable 未运行；受影响原生面板、字体放大及
  代表性 iOS/Android 仍为 `NOT_RUN`。
