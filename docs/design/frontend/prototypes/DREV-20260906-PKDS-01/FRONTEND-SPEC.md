# 知芽 Push Kids · 微信小程序前端设计规范（PKDS-1.0）

> 交付物：`push_kids_design/`
> 设计基线：`PKDS-1.0`，继承仓库已批准基线 `FDB-20260830-01`，遵守 `FEC-20260905-02` 工程约束
> 基准视口：`390 × 844`（iPhone 12/13/14）；兼容矩阵 `320 × 568` / `390 × 844` / `430 × 932`
> 原型源码：`push_kids_design/screens/*.html` + `assets/tokens.css` + `assets/mp.css`
> 截图：`push_kids_design/shots/*.png`（39 张，2× DPR，780 × 1688 起）

本规范的目标是：**前端工程师不需要再问设计问题，就能把每一屏写出来。** 凡是文中给出具体数值的，实现时按数值走；凡是标注「禁止」的，一律不做。

---

## 1. 产品定位与设计原则

### 1.1 一句话定位

家长用的「孩子学习档案 + 复习安排 + 课外活动」记录工具。家长拍一张作业照片或写一句话，AI 把它整理成**可编辑草稿**，家长确认后才生成正式学习记录与复习计划。

### 1.2 五条产品红线（直接约束 UI）

| 红线 | UI 表现 |
| --- | --- |
| AI 输出只是草稿 | 草稿必须带「AI 整理草稿」标识；确认按钮文案永远含「确认」；未确认内容不进报表、不进复习 |
| AI 不评分、不判掌握、不预测 | 界面禁止出现正确率、掌握度、等级、星级、能力雷达、下一步该学什么 |
| 复习日期由确定性策略生成 | Todo 卡必须有「出现原因」说明（哪条记录、第几次复习、间隔多久），不写「AI 认为」 |
| 手动录入是一等路径 | 任何 AI 入口旁边必须有等权重的「文字记录 / 人工录入」入口，不做二级折叠 |
| 家庭隔离 | 未获批的加入申请看不到任何孩子数据，空态必须显式说明 |

### 1.3 设计气质

安静、温暖、可信、克制。**不做**的清单：游戏化奖励、连续打卡压力、排行榜、庆祝动画、玻璃拟态、霓虹渐变、重投影、企业 BI 式密集仪表盘、儿童卡通插画。

配色策略：暖纸底（`#F4F3EC`）+ 墨绿主色（`#2E6A56`）+ 一枚琥珀（提示）+ 一枚砖红（危险）。科目色只用于 22–34px 的小色块，不做大面积着色。

---

## 2. 信息架构与路由

### 2.1 TabBar（5 项，固定顺序）

| # | 路由 | 标签 | 图标语义 | 首屏内容 |
| --- | --- | --- | --- | --- |
| 1 | `pages/today/index` | 今日 | 嫩芽 | 今日复习 / 今日学习 / 今日活动 |
| 2 | `pages/calendar/index` | 日程 | 日历 | 周日期轨 + 当天时间线 |
| 3 | `pages/records/index` | 记录 | 文档 | 新增记录 / 历史记录 |
| 4 | `pages/reports/index` | 报表 | 柱图 | 7 / 30 / 100 天 |
| 5 | `pages/settings/index` | 设置 | 光点 | 科目 / 活动 / 家庭 |

`app.json` 相关值：
```json
{
  "window": {
    "navigationBarTitleText": "知芽",
    "navigationBarBackgroundColor": "#F4F3EC",
    "navigationBarTextStyle": "black",
    "backgroundColor": "#F4F3EC"
  },
  "tabBar": {
    "color": "#7A857F",
    "selectedColor": "#2E6A56",
    "backgroundColor": "#FFFEFA",
    "borderStyle": "white"
  }
}
```

### 2.2 深层页面

| 路由 | 页面 | 进入来源 |
| --- | --- | --- |
| `pages/submission/confirm` | 草稿确认 / 记录详情 | 今日待确认条、记录页待处理、历史列表 |
| `pages/activity/edit` | 活动练习记录 | 今日活动卡「记录这次练习」、日程卡、设置 |
| `pages/family-onboarding/index` | 首次引导 | 无家庭时启动重定向 |
| `pages/family-join/index` | 加入家庭 | 引导页、邀请链接 |
| `pages/family-members/index` | 家庭与成员 | 设置页 |
| `pages/family-requests/index` | 加入申请审批 | 家庭成员页、成员页红点 |

### 2.3 主动线（一条主路 + 两条兜底）

```
主路：今日 → 拍照记录 → AI 整理（异步）→ 待确认徽标 → 草稿确认（编辑）→ 正式记录 → 明日 Todo
兜底 1（AI 失败 / 不想等）：记录 → 文字记录 → 人工录入 → 确认
兜底 2（历史补录）：记录 → 新增记录 → 改「实际学习时间」为过去日期 → 确认（只排当前检查，不补历史欠债）
```

导航层级不超过 2 层：Tab → 详情。半屏 Sheet 不计入层级，不允许 Sheet 里再开 Sheet。

---

## 3. 视觉基础 Token

所有 token 定义见 `assets/tokens.css`；WXSS 落地时把 `:root` 换成 `page`，变量名保持不变。

### 3.1 单位规则（重要）

- 设计稿标注一律用 **px @375 基准**。
- WXSS 换算：`rpx = px × 2`。示例：圆角 `16px → 32rpx`，间距 `12px → 24rpx`。
- **例外：发丝线（1 物理像素）用 `1rpx` 或 `0.5px`，不要写 `2rpx`。** 卡片描边、列表分隔线、TabBar 上边线全部按发丝线处理。
- 字号建议直接用 `px`（微信不随系统缩放 rpx 之外的字号，用 px 更可控），本规范字号均为 px。
- 触控目标最小 `44 × 44px（88rpx）`，主 CTA 高度 `48px（96rpx）`。

### 3.2 语义色

| Token | 值 | 用途 | 禁止 |
| --- | --- | --- | --- |
| `--pk-canvas` | `#F4F3EC` | 页面底色、状态栏、导航栏 | 不用于卡片 |
| `--pk-canvas-deep` | `#EDEBE1` | 下拉刷新区、Sheet 背后底色 | — |
| `--pk-surface` | `#FFFFFF` | 卡片、输入、列表 | — |
| `--pk-surface-warm` | `#FCFBF6` | 次要卡片（可选 Todo、已过时间线） | — |
| `--pk-surface-sunken` | `#EFEEE6` | 分段控件槽、进度轨、圆形图标底 | 不用于大面积 |
| `--pk-primary` | `#2E6A56` | 主按钮、选中态、强调数字 | 不做大面积铺底 |
| `--pk-primary-strong` | `#21503F` | 主色文字（在 tint 上）、Hero 标题 | — |
| `--pk-primary-pressed` | `#1A4133` | 主按钮按下 | — |
| `--pk-primary-tint` | `#E6F0EA` | 次按钮底、AI 提示条、空态图标底 | — |
| `--pk-primary-tint-2` | `#D3E4DB` | 日期轨小圆点、图表浅色档 | — |
| `--pk-primary-hairline` | `#BCD5CA` | 主色描边（ghost 按钮、虚线上传框） | — |
| `--pk-ink` | `#1D2B24` | 主文字 | — |
| `--pk-ink-2` | `#46544D` | 次文字、表单标签 | — |
| `--pk-ink-3` | `#79857E` | 说明文字、元信息 | 不用于正文 |
| `--pk-ink-4` | `#A6AFA9` | 占位符、禁用文字、坐标轴 | 不用于任何可点文字 |
| `--pk-line` | `#E3E1D6` | 卡片 / 输入描边 | — |
| `--pk-line-soft` | `#EEECE3` | 卡内分隔线 | — |
| `--pk-line-strong` | `#D3D0C3` | 开关关闭态、Sheet 把手、虚线框 | — |
| `--pk-attention` | `#9A6318` | 需核对 / 待处理文字 | 不用于按钮底 |
| `--pk-attention-bg` | `#FBF0DA` | 待确认提示条底 | — |
| `--pk-attention-line` | `#EDD9AF` | 待确认提示条描边 | — |
| `--pk-danger` | `#A6423B` | 失败、删除、移出 | — |
| `--pk-danger-bg` | `#F9E9E6` | 失败条底、危险按钮底 | — |
| `--pk-danger-line` | `#EBCFCB` | 失败条描边 | — |
| `--pk-success` | `#2C7A5A` | 已完成、成功 | 不与 primary 混用于按钮 |
| `--pk-success-bg` | `#E5F1E9` | 成功轻底 | — |
| `--pk-info` | `#3D5A6C` | 中性说明（离线、缓存） | — |
| `--pk-info-bg` | `#E9EFF3` | 中性说明底 | — |

**颜色语义唯一性**：绿 = 主操作 / 已完成；琥珀 = 需要你处理；砖红 = 失败或破坏性；靛蓝灰 = 中性信息。禁止再引入第五种状态色。

### 3.3 科目色（仅小面积）

| 科目 | 前景 | 背景 | 用于 |
| --- | --- | --- | --- |
| 语文 | `#B4693D` | `#F8EDE3` | `sub-mark` 34px 方块、`tag-sub` 22px 标签 |
| 数学 | `#3A6491` | `#E8EFF7` | 同上 |
| 英语 | `#6B5A9C` | `#EDEAF7` | 同上 |
| 活动 | `#2C7B69` | `#E3F1EC` | 同上 + 时间线左侧 3px 强调条 |
| 其他 / 自定义 | `#6E7A72` | `#EDEFEB` | 同上 |

自定义科目按名称首字符 hash 取上述 5 色循环，不新增颜色。

### 3.4 字阶

| Token | 字号 / 行高 / 字重 | 字距 | 用于 |
| --- | --- | --- | --- |
| `t-display` | 28 / 1.15 / 700 | `-0.4px` | Hero 里的关键数字（`建议复习 4 项`） |
| `t-h1` | 22 / 1.3 / 700 | `-0.2px` | 页内主标题 |
| `t-h2` | 18 / 1.4 / 600 | 0 | 半屏标题 |
| `t-h3` | 17 / 1.45 / 600 | 0 | 卡片标题、分区标题、导航栏标题 |
| `t-body` | 16 / 1.55 / 400 | 0 | 正文、输入值 |
| `t-body-m` | 16 / 1.55 / 500 | 0 | 列表主行、Todo 标题（600） |
| `t-sub` | 14 / 1.5 / 400 | 0 | 次要说明、按钮小号 |
| `t-cap` | 13 / 1.45 / 400 | 0 | 元信息、help 文案、时间线时间 |
| `t-micro` | 11 / 1.3 / 500 | 0 | **仅**图表坐标轴、日期刻度 |

规则：
- 正文最小 `14px`；辅助文字最小 `13px`；`11px` 只允许出现在图表刻度和 TabBar 标签（10px 为微信原生规格）。
- 所有数字用 `font-variant-numeric: tabular-nums`（类 `.tnum`），避免跳动。
- 中文不加 `letter-spacing` 正值；只在 22px 以上标题用轻微负字距。
- 一屏内不同字号不超过 4 级。

### 3.5 圆角（每个值都有唯一职责）

| Token | px | rpx | 唯一用途 |
| --- | --- | --- | --- |
| `--pk-r-xs` | 4 | 8 | 进度条轨 / 填充、图表小色块 |
| `--pk-r-sm` | 6 | 12 | 科目标签 `tag-sub`（22px 高） |
| `--pk-r-md` | 8 | 16 | 分段控件滑块、小按钮（32–36px 高）、热力格、Todo「出现原因」块 |
| `--pk-r-lg` | 12 | 24 | 输入 / 文本域 / 选择器、主按钮、列表行卡、时间线卡、科目色块、提示条 |
| `--pk-r-xl` | 16 | 32 | **默认卡片**、行列表容器、Todo 卡、指标卡、Action Sheet 分组、上传占位块 |
| `--pk-r-2xl` | 20 | 40 | Hero 卡、底部半屏上圆角 |
| `--pk-r-pill` | 999 | 999 | 孩子切换 chip、筛选 chips、状态 pill、FAB、头像 |

判定口诀：**能点的 12，装东西的 16，最重要那张 20，标签一律药丸。** 圆角不允许出现 10 / 14 / 18 / 24 等中间值。

嵌套规则：子元素圆角 = 父圆角 − 内边距，且不小于 `--pk-r-md`。例：16px 卡片 + 14px padding 内放小块 → 用 8px。

### 3.6 边界与描边

| 场景 | 规则 |
| --- | --- |
| 卡片 | `1rpx solid var(--pk-line)`，**不叠阴影** |
| 卡内分隔 | `1rpx solid var(--pk-line-soft)`，左右不留缩进（列表行内分隔线左侧对齐文字起点） |
| 输入框 | 常态 `--pk-line`；聚焦 `--pk-primary` + `0 0 0 3px rgba(46,106,86,.10)`；错误 `--pk-danger` |
| 提示条 | 底色 + 同族描边（`attention-bg` + `attention-line`） |
| 虚线上传框 | `1px dashed`，主色态用 `--pk-primary-hairline`，中性态用 `--pk-line-strong` |
| 分区标题下横线 | `1px` `--pk-line`，左右各留 2px |
| TabBar 上边线 | `0.5px rgba(29,43,36,.08)` |
| 禁止 | 双层描边、描边 + 阴影同时出现、圆角内 2px 以上粗边、彩色描边（除聚焦与错误） |

### 3.7 高度（阴影）

| Token | 值 | 用于 |
| --- | --- | --- |
| `--pk-e0` | `none` | 卡片默认（用描边分层，不用阴影） |
| `--pk-e1` | `0 1px 2px rgba(29,43,36,.04)` | 吸底操作条 |
| `--pk-e2` | `0 2px 8px rgba(29,43,36,.06)` | 分段控件滑块、开关滑块 |
| `--pk-e3` | `0 8px 24px rgba(29,43,36,.10)` | 浮层卡（很少用） |
| `--pk-e-sheet` | `0 -6px 28px rgba(29,43,36,.13)` | 底部半屏 |
| `--pk-e-fab` | `0 6px 18px rgba(33,80,63,.26)` | FAB |

原则：**层级靠底色 + 描边表达，阴影只给真正浮起来的东西。** 全屏最多同时出现 1 个 `e3` 及以上的阴影。

### 3.8 间距

4px 网格。常用值：`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40`。

| 位置 | 值 |
| --- | --- |
| 页面左右安全边距 | `16px` |
| 页面顶部（导航栏下 → 首个元素） | `12px` |
| 卡片内边距 | `16px`（紧凑卡 `14px`；Hero `20px`） |
| 卡片之间 | `12px` |
| 分区之间（section） | `20px` |
| 分区标题条高度 | `44px`，标题下横线与内容间距 `12px` |
| 表单字段之间 | `14px`；标签 → 控件 `6px`；控件 → help `6px` |
| 按钮组内间距 | `10px` |
| 列表行最小高度 | `56px`，内边距 `12px 14px` |
| 页面底部留白 | `20px` + TabBar 高度 + `env(safe-area-inset-bottom)` |

### 3.9 动效

| Token | 值 | 用于 |
| --- | --- | --- |
| `--pk-dur-fast` | `150ms` | 按压反馈、chevron 旋转、颜色过渡 |
| `--pk-dur-base` | `200ms` | 折叠展开、开关滑动、Tab 切换 |
| `--pk-dur-slow` | `240ms` | Sheet 弹出 / 收起 |
| `--pk-ease` | `cubic-bezier(.25,.46,.45,.94)` | 通用 |
| `--pk-ease-sheet` | `cubic-bezier(.32,.72,0,1)` | Sheet |

按压反馈统一：`opacity .72` 或背景加深一档，**不做缩放**。禁止庆祝动画、粒子、弹跳、循环呼吸动效（骨架屏微光除外）。

### 3.10 图标

- 线性图标，`24 × 24` 画板，线宽 `2px`（TabBar `22px` 显示，线宽视觉 1.8px），端点与拐角 `round`。
- 一律 `currentColor` 单色，不用双色、不用填充实心（仅「已完成」勾选、选中态 TabBar 例外允许实心点）。
- 全量图标在 `assets/icons.svg.html`，共 30 个 symbol：`tab-today / tab-calendar / tab-records / tab-reports / tab-settings / camera / image / pen / plus / check / close / back / info / warn / clock / refresh / search / filter / more / sparkle / trash / family / user / share / book / ball / list / cloud-off / eye / sprout`。
- 「AI」一律用 `sparkle`（四角星），禁止机器人头、大脑、魔法棒。
- 小程序落地：图标以 `<image>` + 本地 SVG/PNG 或字体图标实现；`iconPath` 需导出 `81 × 81` PNG（TabBar 规范）。

---

## 4. 页面骨架

```
┌─────────────────────────────┐
│ 状态栏 statusbar 47px（系统）  │  底色 = canvas
├─────────────────────────────┤
│ 导航栏 navbar 44px（系统）     │  底色 = canvas，标题 17/600，右侧胶囊 87×32
├─────────────────────────────┤
│ 页内头部 pg-head             │  kicker 13 + title 22/700，右侧孩子切换 chip 40px
│                             │
│ 内容区（scroll-view）         │  左右 16px
│                             │
├─────────────────────────────┤
│ TabBar 49px + safe-bottom   │  底色 #FFFEFA
└─────────────────────────────┘
```

WXSS 骨架：

```css
page {
  --pk-canvas: #F4F3EC;
  /* ...其余 token 同 tokens.css... */
  background: var(--pk-canvas);
  color: var(--pk-ink);
  font-family: -apple-system, "PingFang SC", sans-serif;
}
.pk-page { min-height: 100vh; padding: 0 32rpx; box-sizing: border-box; }
.pk-page--tabbed { padding-bottom: calc(40rpx + env(safe-area-inset-bottom)); }
.pk-page--sticky-cta { padding-bottom: calc(160rpx + env(safe-area-inset-bottom)); }
```

导航栏策略：**全部使用微信原生导航栏**（`navigationStyle: default`）。理由：胶囊按钮位置固定、返回手势与系统一致、避免自定义导航在异形屏上的高度计算错误。标题固定为页面名（今日 / 日程 / 记录 / 报表 / 设置 / 确认学习记录 / 活动练习记录 / 家庭与成员 / 加入申请 / 知芽）。

页内头部（`pg-head`）承担两件事：**当前上下文**（日期 / 说明）与**孩子切换**。孩子只有 1 个时，chip 仍显示但不可点（去掉 chevron），保持布局稳定。

吸底操作条（草稿确认、活动记录、家庭表单）：
```
height: 48px 按钮 + 上下 12px + safe-area
background: rgba(244,243,236,.92) + backdrop-filter: blur(12px)
border-top: 1rpx solid var(--pk-line)
```

---

## 5. 组件规格

组件命名建议：`components/pk-<name>/`，类名前缀 `pk-`。下表「原型类名」列对应 `assets/mp.css`，可直接搬。

### 5.1 Card / Hero

| 变体 | 原型类名 | 背景 | 描边 | 圆角 | Padding |
| --- | --- | --- | --- | --- | --- |
| 默认卡 | `.card` | `surface` | `line` | 16 | 16 |
| 紧凑卡 | `.card.tight` | `surface` | `line` | 16 | 14 |
| 次要卡 | `.card.flat` | `surface-warm` | `line` | 16 | 16 |
| 小卡 | `.card.plain` | `surface` | `line` | 12 | 16 |
| Hero | `.hero` | `linear-gradient(158deg,#E4EFE8,#EDF1E4)` | `1px #DAE7DE` | 20 | 20 |

Hero 内部结构固定三行：eyebrow 13/`#4C6459` → 主句 20/700/`primary-strong`（内嵌 28px 数字）→ 补充 13/`#5A6E64`，下方可接一组按钮（主 + 次，各占 50%，间距 10）。**每屏最多一个 Hero。**

### 5.2 Section（可折叠分区）

结构：`sec-bar`（44px：标题 17/600 + 计数 13/`ink-3` + 右侧 chevron）→ `sec-rule`（1px 横线，下方 12px）→ `sec-body`（子项间距 10px）。

- 折叠状态写入本地缓存，按孩子维度记忆。
- 折叠动画 200ms，chevron 旋转 150ms。
- 分区为空时不折叠，直接渲染 `empty.inline`（22px 上下内边距，14px `ink-3` 单行文案）。

### 5.3 Button

| 变体 | 背景 | 文字 | 描边 | 用于 |
| --- | --- | --- | --- | --- |
| `primary` | `--pk-primary` | `#fff` | 无 | 每屏唯一主操作 |
| `secondary` | `--pk-primary-tint` | `--pk-primary-strong` | 无 | 与主操作并列的次操作 |
| `ghost` | 透明 | `--pk-primary` | `1px primary-hairline` | 卡内轻操作 |
| `neutral` | `--pk-surface` | `--pk-ink` | `1rpx line` | 取消、返回、否 |
| `danger` | `--pk-danger-bg` | `--pk-danger` | 无 | 删除、移出、拒绝 |

| 尺寸 | 高 | 字号 | 圆角 | 横向 padding |
| --- | --- | --- | --- | --- |
| `lg`（默认） | 48 | 16 / 600 | 12 | 18（通常 `width:100%`） |
| `md` | 44 | 15 / 600 | 12 | 18 |
| `sm` | 36 | 14 / 600 | 8 | 14 |
| `xs`（卡内） | 32 | 14 / 600 | 8 | 14 |

状态：
- `pressed`：背景换 `--pk-primary-pressed`（次级：tint 加深至 `--pk-primary-tint-2`）。
- `loading`：文案换成进行时（`保存中…`），左侧加 16px 旋转指示，按钮**保持可见宽度不变**，禁用点击。
- `disabled`：背景 `--pk-surface-sunken`，文字 `--pk-ink-4`，不加 opacity。
- 主按钮在表单未满足条件时用 `disabled`，且必须在按钮上方或下方用 13px `ink-3` 说明缺什么。

文字链按钮 `.link-btn`：44px 高、14/500、主色、无底无边，右侧可跟 6px chevron。

### 5.4 Pill / Tag / SubMark / Confidence

| 组件 | 尺寸 | 圆角 | 变体 |
| --- | --- | --- | --- |
| `pill` 状态标签 | 高 24，padding 0 9，12/600 | pill | 默认（tint/primary-strong）、`att`、`dan`、`neutral`、`info`、`line` |
| `tag-sub` 科目标签 | 高 22，padding 0 8，12/600 | 6 | 5 科目色 |
| `sub-mark` 科目色块 | 34 × 34，14/700 单字 | 12 | 5 科目色 |
| `confidence` 置信指示 | 3 根 4 × 10 竖条 + 12/600 文字 | 1 | 3 档：识别可靠 / 请核对 / 不确定 |

置信度文案表（**禁止出现百分比**）：`识别可靠`（3 条亮，success）｜`请核对`（2 条亮，attention）｜`不确定`（1 条亮，danger）。低置信项默认**不预选**，并在字段上方给出 `请核对` 标记。

### 5.5 Notice（提示条）

高度 ≥ 48，padding `11 12`，圆角 12，18px 图标 + 14/1.45 文字，可带右侧 chevron 或按钮。

| 变体 | 底 / 边 / 字 | 语义 | 图标 |
| --- | --- | --- | --- |
| 默认（attention） | `attention-bg` / `attention-line` / `attention` | 有事等你处理 | `sparkle` 或 `warn` |
| `err` | `danger-bg` / `danger-line` / `danger` | 失败、离线 | `cloud-off` / `warn` |
| `info` | `info-bg` / `#D7E2E9` / `info` | 中性说明 | `info` |
| `ai` | `primary-tint` / `primary-hairline` / `primary-strong` | AI 草稿说明 | `sparkle` |
| `quiet` | `surface-warm` / `line` / `ink-2` | 补充说明 | `info` |

规则：一屏最多 2 条 Notice；同类合并计数（`有 2 条待处理 · 查看`）；提示条必须可点或自带操作，纯装饰性提示删掉。

### 5.6 Segmented / Chips

- `seg`：槽 `surface-sunken`，padding 3，圆角 12；按钮高 36，圆角 8，14/500；选中态白底 + `primary-strong` + 600 + `e2`。**2 项或 3 项**，超过 3 项改用 chips 横滑。
- `chips`：高 32，padding 0 13，pill，`surface` + `line` + 13/500；选中态 `primary` 底 + 白字 + 600。可带 12px 计数。横向可滑，左右边缘留 16px。

### 5.7 表单

| 元素 | 尺寸 | 说明 |
| --- | --- | --- |
| `label` | 13/600 `ink-2`，下 6px | 可选项在标签后加 13/400 `ink-3` 的「选填」 |
| `input` / `picker` | min-height 46，padding `12 14`，16px 文字，圆角 12 | picker 右侧 7px chevron |
| `textarea` | min-height 104，同上 | 右下角 12px 计数 `n / 500` |
| `help` | 13/1.5 `ink-3`，上 6px | 解释规则、边界、隐私 |
| `switch` | 46 × 28，滑块 24 | 关：`line-strong`；开：`primary` |
| `slider` | 轨 3px，滑块 22 | 用于时长（15/30/45/60 分钟吸附） |
| 错误态 | 描边 `danger`，下方 13px `danger` 文案 | 错误文案说「怎么改」，不说「格式错误」 |

时间与日期一律用原生 `picker`（`mode="date"` / `mode="time"` / `mode="multiSelector"`），不自造滚轮。

### 5.8 RowList（行列表）

容器 `surface` + `line` + 圆角 16 + `overflow:hidden`；行高 ≥ 56，padding `12 14`，行间 `1rpx line-soft`。
行结构：`[34px 色块/图标] [主 16/500 + 副 13/ink-3] [右侧：pill / 开关 / 按钮 / chevron]`。
整行可点时右侧必须有 chevron；行内含独立按钮时，整行不可点（避免误触）。

### 5.9 TodoCard（复习待办）

这是产品最重要的卡，规格必须严格执行。

```
┌─ card 16 / padding 14 14 12 ────────────────┐
│ [sub-mark 34] 科目 · 复习方式        [pill]  │  标题 16/600
│               3 个三天前学过的单词 · 约 4 分钟 │  meta 13/ink-3
│ ┌ todo-why  bg surface-sunken r8 p8 10 ────┐ │
│ │ 出现原因：9 月 2 日确认的学习记录，今天第 2 次复习。│  13/1.45/ink-2
│ └──────────────────────────────────────────┘ │
│ ─ 知识点行（≥44px，行间 1rpx line-soft）───── │
│ recycle（回收）              [完成] [⋯]      │  15px + 32px 按钮
│ plastic（塑料）              ✓ 已完成         │  13/600 success
│ ─ todo-foot（上边线 + 10px）──────────────── │
│ ⏱ 建议家长陪读一遍                            │  13/ink-3
└─────────────────────────────────────────────┘
```

- 状态 pill：`建议完成`（primary tint）｜`可选`（neutral）｜`已完成`（success 文本，不用 pill）。
- 「有余力再做」的可选 Todo 使用 `.todo.opt`（`surface-warm` 底），并在分组上方加 13px `ink-3` 小标题「有余力再做」。
- `[完成]` 主按钮 32px 高；`[⋯]` 32 × 32 打开 Action Sheet：`需要加强` / `只做了一部分` / `今天先跳过`。四种反馈**都是家长主观标记**，文案不含评分含义。
- 出现原因（`todo-why`）为必填内容，缺失时不渲染该 Todo，前端记 warning。
- 一屏 Todo 超过 3 张时，第 4 张起折叠为「还有 n 项 · 展开」。

### 5.10 Timeline / WeekStrip

**WeekStrip**：7 列等宽 grid，gap 4；单元 62px 高、圆角 12，内含 12px 周标 + 16/600 日期 + 4px 圆点（有安排）。选中态 `primary` 满底白字；今天未选中时日期用 `primary` 字色；非本月用 `ink-4`。左右滑动切周，切周不改选中「星期」。

**Timeline**：左侧 40px 时间列（13/600 tabular）+ 1px 竖线（left 47）+ 9px 节点圆（primary，2px canvas 描边）+ 卡片（圆角 12，padding `12 14`）。
- 已过去：节点与时间 `ink-4`，卡片 `surface-warm`，标题 `ink-3`。
- 课外活动卡左侧加 3px `sub-activity` 竖条。
- 「建议」类条目时间列写「建议」而非时间，节点用 `attention` 色。

### 5.11 FAB

48px 高、pill、`primary` 底、`e-fab` 阴影、右下 `16px / 16px`（在 TabBar 之上、内容之外）。仅**日程页**使用，文案「加日程」带 plus 图标。其他页禁止 FAB，避免与吸底 CTA 冲突。

### 5.12 数据展示

| 组件 | 规格 |
| --- | --- |
| `metrics` 指标条 | 4 列等宽，卡内 padding `14 4`，圆角 16；数值 24/700 tabular，标签 12/`ink-3`；列间 1px `line-soft` 竖线（`::before`，上下各留 4px） |
| `bar-row` 横向条 | 行高 ≥44；名称 52px 固定 14/500；轨 8px 圆角 4 `surface-sunken`；填充 `primary`；数值 13/`ink-3` |
| `ugrid` 紧迫度网格 | 7 列，gap `6 4`；圆点 34px；4 档底色 `sunken → #F3EDDC → #F0DCC9 → #E7C7BC`；全通过用 `primary` 满底 + 白勾；下方 11px 日期 |
| `hgrid` 活跃度热力 | 7 列，方块 `aspect-ratio:1` 上限 34px，圆角 8；5 档 `#EBEAE1 / #D5E5DB / #A9CDBC / #6DA894 / primary`；底部图例「少 ▢▢▢▢▢ 多」+ 总次数 |
| `pager` 组件内分页 | 高 40；左右 30px 圆形按钮（`surface-sunken`，不可用时 opacity .35）；中间 13/600 区间 + 11px 说明；下方 5px 圆点指示（当前变 14 × 5 胶囊） |

图表规则：
- **只用色块与数字，不画折线、不画饼图。** 理由：家长关心「今天有没有事」「最近有没有断」，不需要趋势拟合。
- 100 天视图按 30 / 30 / 30 / 10 组件内分页，绝不横向压缩成 100 格。
- 任何图表必须有一句 13px 的读法说明（「数字表示当天待复习知识数，绿色勾表示当天已全部通过。」）。
- 报表页顶部固定一句 13px `ink-3` 口径声明：**只统计已确认的学习**。

### 5.13 PhotoUploader

- 未选照片：2 列 104px 高的虚线块（`up-tile`：主色态「拍摄一张」+ 中性态「从相册选择」），圆角 16。
- 已选照片：3 列 grid，gap 8，`aspect-ratio:1`，圆角 12；右上 22px 半透明删除；左下 18px 序号；末尾「+」虚线块。
- 上限 9 张，标题右侧显示 `n / 9`。
- 上传中：单格白色蒙层 66% + 13/700 百分比；卡片底部 4px 进度条 + 13px `n / m 张已上传`。
- 失败：该格右下角 `warn` 角标，卡片下方 `notice.err` + `重试这张`。
- 图片压缩到长边 1600px、质量 0.8 后再上传；本地预览用原图。
- 隐私：上传区下方固定 13px help「照片会整理成可编辑的草稿，由你确认后才存为学习记录。」

### 5.14 浮层四件套

| 类型 | 何时用 | 规格 |
| --- | --- | --- |
| 底部半屏 `sheet` | 编辑、筛选、目录选择、孩子切换 | 上圆角 20，`max-height 85%`，padding `8 16 (12+safe)`，`e-sheet`；顶部 36 × 4 把手；头部 18/700 标题 + 13/`ink-3` 副标 + 右上 36px 关闭；底部固定按钮区（上 12px）。遮罩 `rgba(24,36,30,.45)`，点击关闭 |
| Action Sheet `asheet` | 3 项以内的路径选择、Todo 反馈 | 左右 8px，分组圆角 16、`rgba(252,251,246,.96)` + 20px 模糊；标题 13/`ink-3` 居中 12px；项高 56，17/500 居中；取消独立成块，上间距 8 |
| Dialog | 破坏性确认 | 微信原生 `showModal`；标题「移出这个科目？」，内容说明**影响范围**，确认按钮红色，取消在左 |
| Toast | 轻量成功反馈 | 微信原生 `showToast`（图标 success，1500ms）；**同时**在页面内把对应卡片状态改为已完成，不能只靠 Toast |

Sheet 里禁止再弹 Sheet；Sheet 内表单必须能被键盘顶起（`adjust-position`），底部按钮跟随键盘上移。

### 5.15 空态 / 骨架 / 错误

**空态**：64px 圆形 `primary-tint` 底 + 24px 图标 → 16/600 标题 → 14/1.5 `ink-3` 说明（最多 2 行）→ 可选主操作按钮。文案必须说明「为什么空」+「下一步做什么」。

行内空态 `empty.inline`：22px 上下内边距，14/400 `ink-3` 单行。

**骨架屏**：`linear-gradient(100deg,#EBEAE2 20%,#F4F3EC 42%,#EBEAE2 64%)`，`background-size:300% 100%`，1.4s 循环。骨架块沿用真实布局的圆角（Hero 20 / 卡 16 / 文本行 7）。首屏骨架最多 3 组，超过 800ms 才显示（避免闪烁）。

**错误 / 离线**：
- 顶部 `notice.err`（`网络暂时不可用 · 显示的是上次读取到的内容 · 点此重试`，右侧 refresh 图标）。
- 已缓存内容保留可见，并在分区标题旁加 13px「缓存」标记。
- 写操作入口置灰，卡内 13px 说明「恢复网络后才能提交复习反馈。」
- **禁止**用 Toast 代替错误页；**禁止**乐观更新后静默回滚。

---

## 6. 逐屏规格

截图目录：`push_kids_design/shots/`。每屏给出「目标 / 结构 / 交互 / 数据」，实现时逐条对照。

### A · 首次使用与家庭绑定

#### A1 首次进入 · 选择路径 — `A1-onboarding-choice.png`
- 目标：15 秒内让家长明白这是什么、AI 做什么、然后二选一。
- 结构：56px 品牌方块（`primary` 底 + 白色嫩芽，圆角 16）→ 22/700 两行标题 → 14/1.55 `ink-2` 两行说明（第二行必须是「AI 只提供可编辑的建议，不替你做判断。」）→ 主卡「开始记录 / 创建家庭…」（`primary-tint` 底 + 32px 圆形 plus + chevron）→ 次卡「申请加入家庭」（白底）→ `notice.quiet` 说明审批与可见性。
- 交互：两张卡整卡可点，按压 opacity .72。无返回按钮，导航标题「知芽」。
- 数据：`GET /me` 返回无家庭 → 重定向此页。

#### A2 创建家庭档案 — `A2-onboarding-create.png`
- 结构：家庭名称（选填）→ 孩子昵称（必填，help「用于区分多个孩子，可随时改」）→ 年级 picker → 在学科目多选 chips（语文/数学/英语 + 其他）→ 吸底主按钮「创建并开始」。
- 交互：昵称为空时主按钮 disabled + 下方 13px 说明；科目 0 选时允许提交，但 help 提示「之后在设置里补也可以」。
- 数据：`POST /families` → `POST /children` → `POST /subjects`（批量）。

#### A3 使用邀请口令加入 — `A3-onboarding-join.png`
- 结构：口令输入（16px，居中，字距 2px，大写自动转换）→ 预览卡（口令有效后展示家庭名 + 管理员 + 孩子数）→ 申请说明输入（选填）→ 主按钮「发送加入申请」。
- 交互：输入 6 位后自动 `POST /family-invites/preview`；无效时输入框错误态 + 「口令无效或已过期，请向家人重新获取」。
- 数据：`POST /family-invites/preview` → `POST /family-requests`。

#### A4 申请已发送 · 等待确认 — `A4-onboarding-pending.png`
- 结构：空态图（clock）→「等家人确认一下」→ 说明（谁会收到、审批后能看到什么）→ 状态卡（申请时间、目标家庭、当前状态 pill `待确认`）→ 次按钮「撤回申请」（danger 变体）→ `notice.quiet`「获批前不会看到孩子的学习记录或照片。」
- 交互：下拉刷新查询状态；撤回走 Dialog 二次确认。
- 数据：`GET /me`、`DELETE /family-requests/current`。

### B · 今日

#### B1 / B2 今日主态 — `B1-today-main.png`、`B2-today-scroll.png`
- 目标：**打开就知道今天要不要做事**，且 3 秒内能进入记录。
- 结构（自上而下）：
  1. `pg-head`：kicker「9 月 5 日 星期五」+ title「今天，也慢慢来」+ 右侧孩子 chip。
  2. Hero：eyebrow「今天的复习安排」→「建议复习 **4** 项，约 **15** 分钟」→「已完成 1 项 · 都是之前确认过的学习内容」→ 按钮组［记录学习（primary，camera 图标）｜加日程（neutral，plus）］。
  3. `sec` 今日复习（计数 4 项）→ TodoCard 列表 → 可选组「有余力再做」。
  4. `sec` 今日学习（已确认 n 条）→ RowList（科目色块 + 一句摘要 + chevron）。
  5. `sec` 今日活动（n 项）→ Timeline（含固定安排 + 建议条目）。
- 交互：
  - 有待确认草稿时，Hero 上方插入 `notice`（`有 2 条待处理 · 查看`）→ 跳记录页待处理。
  - 有失败草稿时插入 `notice.err`（`1 条整理失败 · 去看看`）。
  - Hero 数字为 0 时改文案「今天没有必须做的复习」，按钮保留。
  - 分区可折叠，状态按孩子记忆。
- 数据：`GET /children/{id}/todos`、`GET /children/{id}/daily-summary`、`GET /children/{id}/schedule`、`GET /submissions?status=pending|failed`。

#### B3 今日 · 首次引导空态 — `B3-today-empty.png`
- 结构：Hero 换成引导卡（「先记一次，明天就有复习安排」+ 三步说明 1→2→3，每步 14px 一行）→ 主按钮「记录第一次学习」→ 下方 `sec` 全部渲染 `empty.inline`。
- 规则：三步说明必须包含「你确认后才生效」。

#### B4 孩子切换 · 底部半屏 — `B4-today-child-sheet.png`
- 结构：标题「选择孩子」+ 副标「切换后所有页面同步」→ 行列表（40px 头像 + 昵称 16/500 + 年级 13 + 右侧 check）→ 底部 ghost 按钮「添加孩子」。
- 交互：选中即关闭并全局切换（写入 storage + 全局事件），不需要「确定」。

#### B5 记录入口 · Action Sheet — `B5-today-action-sheet.png`
- 项：`拍照记录（推荐）` / `写一句话` / `记录课外活动练习`，取消独立块。
- 规则：顺序固定，「写一句话」不加「不推荐」类贬义措辞。

### C · 日程

#### C1 日程主态 — `C1-calendar-main.png`
- 结构：`pg-head`（kicker「本周」+ title「日程」+ 孩子 chip）→ WeekStrip → 当天标题行（16/600「9 月 4 日 · 周五」+ 右侧 13px「2 项」）→ Timeline → FAB「加日程」。
- 交互：点日期切换（150ms 内更新，不整页重刷）；左右滑切周；点条目打开 C3 编辑；已过去的活动卡显示「记录这次练习 ›」。
- 数据：`GET /children/{id}/calendar`、`GET /children/{id}/schedule`。

#### C2 当天空态 — `C2-calendar-empty.png`
- 空态文案：「这天还没有安排」+「课外活动的固定时间可以在设置里配置，之后会自动出现在日程里。」+ ghost 按钮「去设置固定时间」。

#### C3 新建 / 编辑日程 · 半屏 — `C3-calendar-editor.png`
- 字段：类型（chips：课外活动 / 其他安排）→ 活动（picker，来源于已配置活动）→ 日期（picker）→ 开始 / 结束时间（两列 picker）→ 重复（chips：仅这次 / 每周 / 自定义）→ 备注（选填 textarea）。
- 底部：`删除`（danger，仅编辑态）+ `保存`（primary，占 2/3 宽）。
- 交互：结束时间早于开始时间时，结束时间字段错误态 + 「结束时间要晚于开始时间」。删除走 Dialog，说明「只删这一次，还是删掉每周安排？」→ Action Sheet 两选项。
- 数据：`POST/PATCH/DELETE /calendar-events`、`/activity-schedules`。

### D · 记录

#### D1 / D2 / D3 新增记录 — `D1-record-photo-empty.png`、`D2-record-photo-upload.png`、`D3-record-text.png`
- 结构：`pg-head` → `seg`（新增记录 / 历史记录）→ 待处理 `notice`（`有 2 条待处理 · 查看`）→ 实际学习时间行（clock 图标 + 值 16px + 右侧 `修改` 小按钮）→ `seg`（拍照记录 / 文字记录）→ 内容区 → help → 吸底主按钮。
- 「实际学习时间」默认当前时间，可改为过去时间；改为过去日期时，下方出现 13px `info` 说明「历史补录只安排今天起的复习检查，不会补出过去的待办。」
- 拍照态：PhotoUploader（见 5.13）+ 补充内容 textarea（选填，placeholder「例如：今天练习了乘法，重点是进位。」）。
- 文字态：主 textarea（必填，min-height 104，计数 `n / 500`）+ 科目 picker（选填）+ help「写清楚学了什么就够了，不用写评价。」
- 主按钮文案：拍照态「上传并整理」；文字态「提交整理」；两者提交后都进入待确认状态而不是直接入档。
- 上传中：按钮 loading，页面保持可滚动，卡内进度可见；离开页面时给出 Dialog「正在上传，离开会中断」。
- 数据：`POST /media/upload-tickets` → 上传 → `POST /submissions/upload` 或 `POST /submissions` → 轮询 `GET /submissions/{id}`。

#### D4 / D5 历史记录 — `D4-record-history.png`、`D5-record-pending.png`
- 结构：`seg` → 搜索框（44px，圆角 12，左 18px search 图标，右侧 `筛选` 小按钮带角标）→ 状态 chips（已确认 / 待处理 / 全部，带计数）→ 分组列表（按日期分组，组标题 13/600 `ink-2`，`今天` / `昨天` / `9 月 2 日`）→ 记录卡 → 分页「加载更多」。
- 记录卡（已确认）：`sub-mark` + 标题 16/600（一句摘要，最多 2 行）+ meta 13（`实际学习 09-03 19:20 · 3 个知识点`）+ 底部 pill 组（复习 2 次 / 已确认）+ chevron。
- 记录卡（待处理）：pill `整理中` + 4px 进度条 + 13px「预计 10 秒内完成，可以先去别的页面」；失败态 pill `整理失败` + 13px 原因 + ［重试］［改成人工录入］两个 32px 按钮。
- 交互：待处理卡不可确认，只能查看详情；整理完成后卡片就地变为 `待确认` + 主按钮「查看并确认」。轮询间隔 2s，最多 30 次，之后转「后台继续，稍后回来看」。
- 数据：`GET /submissions?status=&q=&page=`、`GET /children/{id}/history`。

#### D6 历史筛选 · 半屏 — `D6-record-filter.png`
- 字段：科目（chips 多选）→ 状态（chips 单选）→ 时间范围（chips：近 7 天 / 近 30 天 / 自定义 → 两个日期 picker）→ 有照片（switch）。
- 底部：`重置`（neutral）+ `查看 n 条结果`（primary，实时计数）。

#### D7 历史详情（只读） — `D7-record-detail.png`
- 结构：状态卡（pill `已确认` + 确认人 + 确认时间）→ 学习总结（只读文本卡）→ 科目 + 实际学习时间 → 知识点列表（每项：名称 16/500 + 证据 13/`ink-3`）→ 复习情况（时间线式：已复习 2 次 / 下次检查 09-08）→ 原始材料（照片九宫格，点开大图）→ 底部 ghost「编辑这条记录」。
- 规则：只读态不出现任何输入控件；证据行必须带一句「证据仅供你核对，不代表模型判断孩子已掌握。」

#### D8 待处理详情 — `D8-record-detail-pending.png`
- 结构：`notice.err`（失败原因，具体到「第 2 张照片太模糊」）→ 已上传照片（可删除 / 可补传）→ 三个并列出口：［重试整理］（primary）［改成人工录入］（secondary）［删掉这条］（danger 文字按钮）。
- 规则：失败原因必须可读、可行动，不暴露服务地址、堆栈、模型名。

### E · AI 草稿确认（唯一入档入口）

#### E1 / E2 草稿确认 — `E1-confirm-draft.png`、`E2-confirm-draft-scroll.png`
- 目标：让家长**快速改、放心确认**。
- 结构：
  1. `notice.ai`：「这是 AI 整理的草稿 / 点「确认」后才会进入学习档案和复习计划」。
  2. `notice`（attention，仅当有低置信或疑似重复）：「需要核对 2 项 / 照片 2 有一处字迹不清；第 4 个知识点可能与 9-02 重复」。
  3. 主体卡：pill `AI 整理草稿` + 右侧 13px「实际学习 09-05 19:20」→ 学习总结 textarea（标签后跟 13px「可修改」，右下计数）→ 科目 picker + help「只能选择已在学的科目，也可以输入新的学习科目。」
  4. `sec` 知识点（计数 + 右侧 `+ 添加` 小按钮）：每个知识点一张卡 —— 头行「知识点 n」+ 右侧 `confidence` + `移除`；名称 input；证据块（`surface-sunken`，13px，两行：证据来源 + 免责句）；关联已有知识（picker，可空，help「关联后复习会合并计算」）。
  5. `sec` 关联今天的复习 Todo（可选）：匹配到的 Todo 列表，每项带 checkbox + 13px 匹配理由；**默认不勾选**，标题旁 13px「AI 猜的，勾选前请核对」。
  6. `sec` 原始材料：照片九宫格（只读）+ 家长原始文字引用（`blockquote` 样式，13px）。
  7. 吸底：［保存为草稿］（neutral，40%）+［确认并生成复习计划］（primary，60%）。
- 交互：
  - 任意字段变更后，返回 / 切页触发 Dialog「还有未确认的修改，保存草稿还是丢弃？」。
  - `移除` 知识点即时生效，顶部出现 13px「已移除 1 项 · 撤销」（10 秒内可撤销）。
  - 确认时校验：总结非空、科目非空、至少 1 个知识点；不满足则滚动到第一个问题字段并聚焦。
  - 确认成功：Toast「已确认」+ 返回上一页 + 目标列表就地更新为「已确认」。
- 数据：`GET /submissions/{id}`、`POST /submissions/{id}/confirm`。

#### E3 人工录入 — `E3-confirm-manual.png`
- 与 E1 结构一致，区别：pill 换 `人工录入`，无 `notice.ai`、无置信度、无证据块；知识点卡只有名称 input + `移除`；顶部 `notice.quiet`「这条由你手动填写，不会经过 AI。」

#### E4 保存失败 — `E4-confirm-save-error.png`
- 顶部 `notice.err`「保存失败，你的修改都还在。」+ 右侧 `重试`；吸底主按钮变为「重试确认」，次按钮保留「保存为草稿」。
- **硬约束**：失败后表单内容 100% 保留，不清空、不回滚、不跳页。

### F · 报表

#### F1 / F2 / F3 报表 — `F1-report-7.png`、`F2-report-100.png`、`F3-report-scroll.png`
- 结构：`pg-head`（kicker「只统计已确认的学习」+ title「一点一滴，看得见」+ 孩子 chip）→ `seg.n3`（近 7 天 / 近 30 天 / 近 100 天）→ `metrics`（学习记录 / 新增知识 / 复习反馈 / 活动练习）→ `sec` 哪些内容最需要先复习（`ugrid` + 读法说明）→ `sec` 复习活跃度（`hgrid` + 图例 + 总次数）→ `sec` 科目学习记录（`bar-row` 列表）→ `sec` 课外活动（RowList：活动 + 次数 + 上次时间）。
- 100 天：`ugrid` / `hgrid` 外层加 `pager`，按 30 / 30 / 30 / 10 分页，标题右侧显示当前区间（`第 1–30 天 · 06-30 至 07-29`）。
- 交互：切换区间只重算数据，不改滚动位置；点 `ugrid` 圆点跳到当天的复习列表（可选增强）。
- 规则：**不出现**掌握率、正确率、排名、同龄对比、预测曲线。
- 数据：`GET /children/{id}/report?days=7|30|100`、`GET /children/{id}/dashboard`。

#### F4 报表空态 — `F4-report-empty.png`
- 结构：`metrics` 全 0（保留结构，数字用 `ink-4`）→ 空态图 + 「还没有已确认的学习记录」+「确认第一条记录后，这里会显示复习安排和活动统计。」+ 主按钮「去记录」。

### G · 设置、家庭与活动

#### G1 设置主页 — `G1-settings-main.png`
- 结构：`pg-head`（kicker「让安排贴合孩子的日常」+ title「学习设置」+ 孩子 chip）→ 卡 1「在学科目」（说明 13px + 右侧 13px「点击切换」+ 基础科目 chips 三列 + 自定义科目行（`自定义` pill + 名称 + `移出` 小按钮）+ `+ 添加其他科目` 链接）→ 卡 2「课外活动」（RowList：图标 + 名称 + 时间说明 + chevron，`+ 添加课外活动`）→ 卡 3 入口列表（家庭与成员（带 `1 份申请` pill）、孩子资料、关于知芽）。
- 交互：科目 chip 点击即切换在学状态，`移出` 走 Dialog，说明「已有的学习记录会保留，只是不再出现在选项里。」
- 数据：`GET /children/{id}/subjects`、`PATCH /subjects/{id}`、`GET /children/{id}/activity-schedules`。

#### G2 添加科目 / 活动 · 半屏目录 — `G2-settings-catalog.png`
- 结构：标题「添加科目」+ 搜索框 → 目录分组（小学常见 / 兴趣类）chips 多选 → 分隔 → 「找不到？自己填一个」input + `添加` 小按钮 → 底部主按钮「添加 n 项」。

#### G3 活动安排 · 半屏 — `G3-settings-schedule.png`
- 字段：活动名称 → 是否有固定时间（switch）→ 每周哪几天（7 个 chips 多选）→ 开始 / 结束时间 → 每次时长 slider（15/30/45/60/90）→ 提醒（switch + help「只在小程序内提示，不发订阅消息」）。
- 底部：`删除活动`（danger）+ `保存`。

#### G4 家庭与成员 — `G4-family-members.png`
- 结构：家庭卡（家庭名 + 成员数 + `管理员` pill）→ 待审批 `notice`（`1 份加入申请 · 去处理`）→ 成员 RowList（头像 + 昵称 + 角色 pill + `管理员` / `成员` + chevron）→ 邀请卡（口令 24/700 字距 4px + 有效期 13px + ［复制口令］［微信邀请］两按钮 + `重新生成` 链接）→ 危险区（`退出家庭` danger 文字按钮）。
- 交互：非管理员看不到邀请卡与审批入口；成员行点开半屏（改昵称 / 设为管理员 / 移出家庭）；移出走 Dialog，说明数据归属。
- 数据：`GET /families/current/members`、`/invites`、`/requests`。

#### G5 加入申请 · 审批 — `G5-family-requests.png`
- 结构：说明 `notice.quiet`「通过后对方可以看到这个家庭所有孩子的学习记录和照片。」→ 申请卡列表（微信头像 + 昵称 + 申请时间 + 申请说明引用 + ［同意］（primary 36px）［拒绝］（neutral 36px））→ 空态「暂时没有待处理的申请」。
- 交互：同意前 Dialog 二次确认（重复说明可见范围）；操作后卡片就地变为结果状态 13px 文案，2 秒后移出列表。

#### G6 活动练习记录 — `G6-activity-record.png`
- 结构：`notice.quiet`「课外活动只做记录，不进入复习曲线。」→ 活动 picker → 日期 + 开始时间 picker → 时长 slider（显示 `45 分钟`）→ 强度 chips（轻松 / 正常 / 有点累，可空）→ 备注 textarea（选填）→ 吸底主按钮「保存记录」。
- 规则：不出现评分、成绩、名次字段。
- 数据：`POST /activity-records`。

### H · 全局状态与规范页

| 截图 | 内容 |
| --- | --- |
| `H1-state-loading.png` | 今日页首屏骨架：Hero 96px + 2 张 116px 卡 + 文本行 |
| `H2-state-error.png` | 离线态：顶部 `notice.err` + 缓存内容可见 + 分区「缓存」标记 + 写操作禁用说明 |
| `H3-destructive.png` | 破坏性确认：原生 Dialog，标题问句 + 影响范围说明 + 红色确认 |
| `H4-toast-success.png` | 成功反馈：Toast + 卡内状态同步变为「已完成」 |
| `H5-tokens.png` | Token 速查页：语义色、科目色、圆角、字阶、按钮与状态 |

---

## 7. 交互与状态规范

### 7.1 写操作三态（强制）

每个写操作都必须实现 pending / success / error 三种可见状态：

| 阶段 | 表现 |
| --- | --- |
| pending | 触发控件进入 loading（文案变进行时），页面其余部分保持可交互；耗时 > 3s 时在卡内补 13px 进度说明 |
| success | 原生 Toast（1500ms）**并且**就地更新对应卡片/列表状态；不整页刷新 |
| error | 就地保留用户输入 + 页面内错误说明 + 明确的重试入口；不只弹 Toast |

禁止乐观更新后静默回滚。若必须先更新 UI，回滚时要显式提示「刚才那条没保存成功」。

### 7.2 破坏性操作

统一走原生 `showModal`：标题是问句，内容说明**影响范围与可恢复性**，确认文案是具体动词（`移出`、`删除`、`退出`），确认按钮红色。适用：移出科目、删除日程 / 记录、移出成员、退出家庭、撤回申请、丢弃草稿修改。

### 7.3 加载策略

- 首次进入某 Tab：骨架屏；再次进入：先渲染缓存 + 静默刷新（右上角不加 spinner，改在分区标题旁加 13px「更新中」）。
- 骨架屏延迟 800ms 出现；请求 < 800ms 直接渲染内容。
- 列表分页用「加载更多」按钮而非无限滚动（家长更需要「读完了」的确定感）。
- 轮询（AI 整理）：2s 间隔，最多 30 次；期间允许离开页面，回来继续。

### 7.4 滚动与吸底

- 内容区用 `scroll-view` 或页面滚动，左右 16px 内边距不随滚动改变。
- 有吸底 CTA 的页面，底部预留 `160rpx + safe-area`。
- 长表单：键盘弹起时 `adjust-position` + 当前字段滚动到可视区中部。
- 半屏内滚动时页面本体不滚动（`catchtouchmove` 遮罩）。

### 7.5 徽标与提醒

- 记录 Tab 显示待处理数量徽标（`wx.setTabBarBadge`），上限显示 `9+`。
- 家庭申请在设置页用 pill 而非 TabBar 徽标（避免抢注意力）。
- 不使用订阅消息推送打卡提醒；提醒只在小程序内呈现。

---

## 8. 文案规范

### 8.1 语气

平和、具体、第二人称。像懂事的同事，不像老师，也不像客服。

- ✅「今天，也慢慢来」「照片和文字，都是成长的线索」「一点一滴，看得见」
- ❌「太棒了！继续保持！」「你已连续打卡 7 天 🔥」「孩子掌握度 78%」

### 8.2 AI 相关措辞（严格）

| 场景 | 用 | 不用 |
| --- | --- | --- |
| 草稿标识 | AI 整理草稿 | AI 智能分析 / 智能诊断 |
| 置信度 | 识别可靠 / 请核对 / 不确定 | 置信度 92% |
| 匹配建议 | AI 猜的，勾选前请核对 | 已智能匹配 |
| 确认按钮 | 确认并生成复习计划 | 一键入档 / 智能生成 |
| 失败 | 这次没整理出来，可以重试或改成人工录入 | 服务异常 / 系统错误 |
| 复习原因 | 9 月 2 日确认的学习记录，今天第 2 次复习 | AI 认为该复习了 |

禁用词：掌握、精通、薄弱、差、能力值、正确率、排名、超过 x% 同龄人、预测、智能诊断。

### 8.3 按钮文案表

| 场景 | 文案 |
| --- | --- |
| 拍照提交 | 上传并整理 |
| 文字提交 | 提交整理 |
| 草稿确认 | 确认并生成复习计划 |
| 保存草稿 | 保存为草稿 |
| 重试 | 重试整理 / 重试确认 |
| 人工兜底 | 改成人工录入 |
| Todo 完成 | 完成 |
| Todo 其他反馈 | 需要加强 / 只做了一部分 / 今天先跳过 |
| 活动记录 | 记录这次练习 |
| 危险 | 移出 / 删除 / 退出家庭 / 撤回申请 |

按钮文案 2–8 字，动词开头，不用「确定」「提交」这类无信息量词（危险确认除外）。

### 8.4 空态文案模板

`还没有 <对象>` + `<为什么会空 / 下一步做什么>`。例：「还没有已确认的学习记录 / 确认第一条记录后，这里会显示复习安排和活动统计。」

---

## 9. 适配

### 9.1 三视口验收矩阵

| 视口 | 设备 | 必须验证 |
| --- | --- | --- |
| `320 × 568` | iPhone SE 1 | Hero 数字不换行错位、`metrics` 四列不挤压（数值 24px 可降 20px）、`ugrid` 圆点降至 30px、按钮组文案不截断 |
| `390 × 844` | iPhone 12/13/14 | 基准，像素级对齐本规范 |
| `430 × 932` | iPhone 14 Pro Max | 卡片不被拉伸得空洞（内容左对齐，不居中）、`hgrid` 方块上限 34px 生效 |

实现要求：所有横向多列布局用 `flex` / `grid` + `1fr`，禁止写死宽度（除固定 34/40/52px 的色块与时间列）。`FEC-20260905-02` 要求以原生节点几何验收，不接受 `overflow:hidden` 掩盖溢出。

### 9.2 长文本与极端数据

| 情况 | 处理 |
| --- | --- |
| 孩子昵称过长 | chip 内昵称最多 4 字 + `…`，头像取首字 |
| 科目名过长 | chips 单行省略，最多 6 字 + `…` |
| 知识点名过长 | Todo 内单行省略；详情页允许 2 行 |
| 学习总结过长 | 列表卡最多 2 行省略；详情完整展示 |
| 数字过大 | `metrics` 数值 ≥ 1000 时降为 20px；≥ 10000 显示 `9999+` |
| 0 值 | 保留结构，数值用 `ink-4`，不隐藏卡片 |

### 9.3 字体放大 / 暗色

- 微信「字体大小」调至最大时，页面不允许出现内容截断；`t-cap` 以上字号用 `px` 固定，容器高度用 `min-height` 而非 `height`。
- **本期不做暗色模式**（`darkmode: false`）。理由：暖纸色系在暗色下需要重做整套语义色，超出当前范围。需要时按 token 一一映射，不做自动反色。

---

## 10. 可访问性

- 触控目标 ≥ 44 × 44px；相邻可点区域间距 ≥ 8px。
- 正文对比度 ≥ 4.5:1（`ink` on `surface` = 13.4:1，`ink-3` on `surface` = 4.6:1，`ink-4` 仅用于非文本信息与禁用态）。
- 状态不只靠颜色：`ugrid` 用数字 + 颜色，`hgrid` 用图例 + 总数，成功用勾 + 文字，失败用图标 + 文字。
- 所有图标按钮必须有 `aria-label` 等价物（小程序用 `aria-label` 属性）。
- 图片必须有 `alt` 等价说明（照片九宫格用「第 n 张学习照片」）。
- 不使用纯图形传达关键信息（口令、日期、时长一律有文字）。

---

## 11. 隐私与合规呈现

| 位置 | 必须出现的说明 |
| --- | --- |
| 上传区下方 | 照片会整理成可编辑的草稿，由你确认后才存为学习记录。 |
| 加入申请页 | 通过后对方可以看到这个家庭所有孩子的学习记录和照片。 |
| 待审批空态 | 获批前不会看到孩子的学习记录或照片。 |
| 证据块 | 证据仅供你核对，不代表模型判断孩子已掌握。 |
| 活动记录页 | 课外活动只做记录，不进入复习曲线。 |

界面禁止出现：服务地址、接口路径、模型名称、请求 ID（错误页可显示可读的「错误码」但不含内部标识）、家庭 ID。

---

## 12. 工程落地

### 12.1 目录建议

```
apps/miniprogram/
├─ app.wxss                 # token 注入 page 作用域 + 少量全局原子类
├─ styles/
│  ├─ tokens.wxss           # 由 assets/tokens.css 转换（: root → page）
│  └─ atoms.wxss            # t-*, c-*, mt-*, row, grow, trunc
├─ components/
│  ├─ pk-card / pk-hero / pk-section
│  ├─ pk-button / pk-pill / pk-tag-sub / pk-sub-mark / pk-confidence
│  ├─ pk-notice / pk-segmented / pk-chips
│  ├─ pk-field（input/textarea/picker/switch/slider 统一壳）
│  ├─ pk-rowlist / pk-rowitem
│  ├─ pk-todo-card
│  ├─ pk-timeline / pk-week-strip
│  ├─ pk-metrics / pk-bar-row / pk-urgency-grid / pk-heat-grid / pk-pager
│  ├─ pk-photo-uploader
│  ├─ pk-sheet / pk-action-sheet
│  └─ pk-empty / pk-skeleton / pk-error-state
└─ pages/…（见 2.1 / 2.2）
```

### 12.2 组件 props 约定（关键几个）

```ts
// pk-button
{ type: 'primary'|'secondary'|'ghost'|'neutral'|'danger', size?: 'lg'|'md'|'sm'|'xs',
  block?: boolean, loading?: boolean, disabled?: boolean, icon?: string, text: string }

// pk-todo-card
{ todo: { id, subject, subjectKey, method, estimateMin, reason, status:'suggested'|'optional',
          points: [{ id, name, done }], tip? }, onFeedback(reviewId, kind) }

// pk-notice
{ tone: 'attention'|'err'|'info'|'ai'|'quiet', icon?: string, title?: string,
  text: string, action?: { text, type:'chevron'|'button'|'icon' } }

// pk-photo-uploader
{ value: File[], max: 9, uploading?: { index, percent }, onAdd, onRemove, onRetry }

// pk-urgency-grid / pk-heat-grid
{ days: 7|30|100, page?: number, cells: [{ date, value, level, allPassed? }] }
```

### 12.3 命名与顺序

- 类名 `pk-<block>__<element>--<modifier>`，或直接复用原型的扁平类名（更短，WXSS 无嵌套压力）。
- WXSS 属性顺序：定位 → 盒模型 → 排版 → 视觉 → 动效。
- token 只在 `page` 层定义一次，组件内不重复定义，不写魔法值。**代码评审时出现未在本规范中的色值、圆角、字号，一律打回。**

### 12.4 性能预算（配合 `FEC-20260905-02`）

| 项 | 预算 |
| --- | --- |
| 单页首屏节点数 | ≤ 900 |
| `setData` 单次体积 | ≤ 64KB，列表更新走路径赋值 |
| 图片 | 上传前压缩至长边 1600 / q0.8；列表缩略图用 `mode="aspectFill"` + 固定容器 |
| 长列表 | 单页 ≤ 20 条，分页加载；不使用无限滚动 |
| 首屏请求 | ≤ 3 个并发，骨架屏 800ms 阈值 |
| 动效 | 只对 `opacity` / `transform` 做过渡，不对 `height` 做逐帧动画（折叠用 `max-height` + `overflow` 或条件渲染） |

---

## 13. 验收清单

实现完成后逐条勾：

**视觉**
- [ ] 页面底色 `#F4F3EC`，卡片 `#FFFFFF` + 1rpx `#E3E1D6`，无阴影
- [ ] 圆角只出现 4 / 6 / 8 / 12 / 16 / 20 / pill 七个值
- [ ] 字号只出现 28 / 22 / 18 / 17 / 16 / 14 / 13 / 11 / 10
- [ ] 一屏最多 1 个 primary 按钮、1 个 Hero、2 条 Notice
- [ ] 科目色只出现在 ≤ 34px 的小色块与 22px 标签上
- [ ] 所有数字使用 tabular-nums

**布局**
- [ ] 页面左右 16px，卡间 12px，分区间 20px
- [ ] 触控目标 ≥ 44px，主 CTA 48px
- [ ] 三个视口（320/390/430）无溢出、无截断，以原生节点几何为证

**交互**
- [ ] 每个写操作有 pending / success / error 三态
- [ ] 所有破坏性操作有 Dialog 二次确认且说明影响范围
- [ ] 错误保留用户输入，页面内有重试入口
- [ ] 离线可读缓存，写入口禁用并说明原因
- [ ] 折叠状态、选中孩子、区间选择按孩子维度持久化

**产品红线**
- [ ] 未确认内容不出现在报表与复习计划里
- [ ] 界面无正确率 / 掌握度 / 排名 / 预测
- [ ] 每个 Todo 都有「出现原因」
- [ ] 每个 AI 入口旁有等权重的手动入口
- [ ] AI 匹配的 Todo 默认不勾选
- [ ] 五条隐私说明文案全部就位
- [ ] 界面不暴露服务地址 / 模型名 / 内部 ID

---

## 14. 截图索引

| 分组 | 文件 | 界面 |
| --- | --- | --- |
| A | `A1-onboarding-choice.png` | 首次进入 · 选择路径 |
| A | `A2-onboarding-create.png` | 创建家庭档案 |
| A | `A3-onboarding-join.png` | 使用邀请口令加入 |
| A | `A4-onboarding-pending.png` | 申请已发送 · 等待确认 |
| B | `B1-today-main.png` | 今日 · 主态（首屏） |
| B | `B2-today-scroll.png` | 今日 · 完整滚动视图 |
| B | `B3-today-empty.png` | 今日 · 首次引导空态 |
| B | `B4-today-child-sheet.png` | 孩子切换 · 底部半屏 |
| B | `B5-today-action-sheet.png` | 记录入口 · Action Sheet |
| C | `C1-calendar-main.png` | 日程 · 周轨 + 时间线 |
| C | `C2-calendar-empty.png` | 日程 · 当天空态 |
| C | `C3-calendar-editor.png` | 新建 / 编辑日程 · 半屏 |
| D | `D1-record-photo-empty.png` | 新增记录 · 拍照（未选） |
| D | `D2-record-photo-upload.png` | 新增记录 · 上传中 |
| D | `D3-record-text.png` | 新增记录 · 文字 |
| D | `D4-record-history.png` | 历史记录 · 已确认 |
| D | `D5-record-pending.png` | 历史记录 · 待处理 |
| D | `D6-record-filter.png` | 历史筛选 · 半屏 |
| D | `D7-record-detail.png` | 历史详情 · 只读 |
| D | `D8-record-detail-pending.png` | 待处理详情 · 兜底出口 |
| E | `E1-confirm-draft.png` | AI 草稿确认 · 首屏 |
| E | `E2-confirm-draft-scroll.png` | AI 草稿确认 · 完整滚动 |
| E | `E3-confirm-manual.png` | 人工录入 |
| E | `E4-confirm-save-error.png` | 保存失败 · 保留编辑 |
| F | `F1-report-7.png` | 报表 · 近 7 天 |
| F | `F2-report-100.png` | 报表 · 近 100 天分页 |
| F | `F3-report-scroll.png` | 报表 · 完整滚动 |
| F | `F4-report-empty.png` | 报表 · 空态 |
| G | `G1-settings-main.png` | 设置 · 主页 |
| G | `G2-settings-catalog.png` | 添加科目 / 活动 · 目录 |
| G | `G3-settings-schedule.png` | 活动安排 · 半屏 |
| G | `G4-family-members.png` | 家庭与成员 |
| G | `G5-family-requests.png` | 加入申请 · 审批 |
| G | `G6-activity-record.png` | 活动练习记录 |
| H | `H1-state-loading.png` | 加载 · 骨架屏 |
| H | `H2-state-error.png` | 失败 / 离线 · 可重试 |
| H | `H3-destructive.png` | 破坏性操作 · 二次确认 |
| H | `H4-toast-success.png` | 轻反馈 · Toast + 卡内状态 |
| H | `H5-tokens.png` | 设计 Token 速查 |
