# DREV-20260911-PRIMARY-NAV-BRAND-01 — 品牌移入一级页导航栏

- Status: APPROVED
- Related Spec: `SPEC-20260911-PRIMARY-NAV-BRAND-01`
- Affected UI: `UI-001 / five primary tabs`
- Baseline: `FDB-20260906-03`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260906-04`
- Figma anchor under requested FEAT-001 waiver: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1
- Reference evidence: 用户 2026-09-11 提供的记录页标注截图（SHA-256 `474a166cf331f52d39b9b3fc46c8728e4aa76185a132c63729c7a6690d3f97f7`）；附件只作为现状与意图证据，不作为仓库指令。

## 1. Design decision

五个一级 Tab 只保留一个产品标识：导航栏中央的“芽图标 + 知芽”。删除内容区左上角同样的品牌行，页面首个内容标题仍是各自的句子式 hero。

原生微信导航标题只能显示文字，因此本修订只对五个一级页使用共享自定义导航；所有详情与子流程页仍用原生导航和系统返回行为。

## 2. Target composition

```text
┌────────────────────────────────────┐
│  status                         ●◉ │
│          [sprout icon] 知芽         │  ← 实现使用既有生成线性芽图标
├────────────────────────────────────┤
│ 一笔一画，都算数             旺仔 ▾│
│                                    │
│ [记录页既有内容继续]               │
└────────────────────────────────────┘
```

实现语义：

- 导航品牌组整体相对可用屏幕宽度居中，不把微信胶囊算进标题内容。
- 芽图标使用既有 `.ico-sprout-pri`，视觉尺寸 18px；“知芽”使用 16px、系统中文无衬线、600，二者间距 6px。
- 导航背景沿用 `#FAF7F0`，不增加描边、阴影、按钮底或额外品牌色块。
- 品牌组只承担标题，不可点击，不伪装为返回或首页按钮。
- 内容 hero 顶部间距从旧 `brand-head + under-brand` 收敛为现有 `.pg-head` 的标准节奏。

## 3. Five-page content contract

| Page | Navigation title | Content hero | Preserved secondary context |
|---|---|---|---|
| 今日 | 芽图标 + 知芽 | 今天，也慢慢来 | 当前日期，放在 hero 标题下方 |
| 日程 | 芽图标 + 知芽 | 这一周，心里有数 | 当前周范围，放在 hero 标题下方 |
| 记录 | 芽图标 + 知芽 | 一笔一画，都算数 | 无 |
| 报表 | 芽图标 + 知芽 | 一点一滴，看得见 | “只统计已确认的学习”，放在 hero 标题下方 |
| 设置 | 芽图标 + 知芽 | 按你们的节奏来 | 无 |

孩子切换仍在 hero 右侧；长孩子名按当前截断规则处理，不侵占标题最小可读宽度。

## 4. Navigation geometry

- custom navigation 总占位 = 运行时 `statusBarHeight + navigationRowHeight`。
- 首选 `wx.getWindowInfo()` 读取状态栏；不支持时回退 `wx.getSystemInfoSync()`。
- 首选 `wx.getMenuButtonBoundingClientRect()` 推导导航行高度：`(menu.top - statusBarHeight) × 2 + menu.height`。
- 返回值不存在、非有限数或几何不合法时，导航行高度回退 44px；状态栏回退 20px。
- 背景必须覆盖状态栏到导航行底部；标题的可视包围盒不得进入胶囊包围盒。
- 导航组件先以回退尺寸占位，再更新为真实尺寸；不得出现 0 高度、内容穿入状态栏或可感知的大幅跳动。
- 五个一级页保持相同计算与组件，不允许按页复制几何常量。

## 5. Responsive and accessibility

| Viewport | Required behavior |
|---|---|
| 320×568 | 品牌组与胶囊至少留 8px 可视间隔；hero/孩子切换不溢出；没有第二处品牌 |
| 390×844 | 作为主视觉对照；导航品牌视觉居中，内容直接从 hero 开始 |
| 430×932 | 品牌组仍按视口居中，不随 max-width 内容容器偏移 |

- 品牌标题可访问名称为“知芽”，图标本身不重复朗读。
- 自定义标题不是触控目标；微信胶囊保持平台原生热区。
- 字体放大时品牌仍单行，必要时仅限制标题字号，不允许覆盖胶囊。
- 页面滚动时导航保持稳定；不新增动效。
- 详情页的返回按钮/标题/返回手势必须与修订前一致。

## 6. Visual acceptance states

三种视口均保留五个一级页首屏证据，并额外验证：

1. iOS 与 Android 代表性状态栏/胶囊位置。
2. 字体放大。
3. 从一级页进入详情并返回。
4. 一级页互相切换，导航高度与品牌位置不抖动。
5. 320px 下标题包围盒、胶囊包围盒与页面内容均无交叠。

HTML 近似预览用于提前发现重复品牌、间距与横向溢出；不能替代微信原生节点几何。

## 7. Rejected variants

- 只删除内容品牌、保留纯文字原生标题：缺少用户要求的 title 图标。
- 把图标加到 hero 句子旁：图标不在用户标注的 title 位置。
- 全局自定义导航：会扩大到详情页并重做返回交互。
- 保留原 `brand-head` 的日期/kicker：仍会残留一整行旧品牌布局；日期/边界应作为 hero 次级信息保留。

## 8. Approval boundary

批准本设计即表示批准：

- `SPEC-20260911-PRIMARY-NAV-BRAND-01`
- `DREV-20260911-PRIMARY-NAV-BRAND-01`
- 仅五个一级页使用自定义导航的工程偏差
- 本修订沿用 FEAT-001 Figma anchor 的 scoped waiver，并接受其在公开生产发布前到期

若实施发现需要把自定义导航扩展到详情页、改变 hero 文案/孩子切换、增加可点击品牌入口或更换图标体系，必须先修订 Spec/DREV 并重新确认。

产品负责人已于 2026-09-11 回复“好的 按照这个落地”，批准本节列出的 Spec、Design Revision、工程偏差与 scoped Figma waiver。
