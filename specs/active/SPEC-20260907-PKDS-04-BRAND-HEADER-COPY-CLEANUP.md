# SPEC-20260907-PKDS-04 — 品牌页头与冗余提示清理

- Status: IMPLEMENTING
- Risk: R1
- Spec owner: 产品负责人（用户）
- Implementer: Aime
- Reviewer: 产品负责人（用户）
- Verifier: Aime（自动化 + 三视口近似渲染走查）+ 产品负责人（真机/开发者工具原生几何验收）
- Created: 2026-09-07
- Last updated: 2026-09-07
- Target release: 未部署（仅本地实现）
- Spec revision: `SPEC-20260907-PKDS-04`
- User confirmation: 用户 2026-09-07 指令「有很多备注……好的交互是不需要做提示的，你来删除类似于这些的无效提示，同时检查 UI 交互是否足够简单」+「小程序的标题：今日/日程 等是冗余信息，和下面的 tab 重复，可以改成小程序的名字以及增加一个 icon」+「今日：左上角的标题是 今天，也慢慢来；报表：一点一滴 看得见。日程和设置也换成类似的」+「修改以上代码 然后提交 mr」
- Affected Feature IDs: `FEAT-001`（可见层文案与页头），其余 Feature 行为不变
- Feature current-state documents: `docs/domain/features/FEAT-001-push-kids-mvp.md`
- Feature baseline revision: `SPEC-20260906-PKDS-03`
- Feature merge owner: Aime

## Frontend Design Impact and Figma Approval

- Frontend impact: yes — 5 个一级 Tab 页头结构改为「品牌头 + hero 句子」，并在 7 个文件里删除说明性提示
- Frontend impact reason: 导航标题、页头层级、卡片/半屏副标题、空态与图例文案
- Frontend engineering impact: yes（小）
- Frontend engineering impact reason: 新增共享组件 `components/brand-head/`，`tools/preview/render.js` 注册该组件
- Affected UI IDs: `UI-001`
- UI current-state documents: `docs/design/frontend/ui/UI-001-parent-miniapp.md`
- Frontend baseline revision: `FDB-20260906-03`（沿用，未修改基线）
- Frontend engineering constraint revision: `FEC-20260906-04` / 视口验收沿用 `FEC-20260905-02`
- Affected frontend quality dimensions: component / state / responsive / a11y / privacy
- Frontend quality budgets/requirements: 触控 ≥88rpx、正文 ≥14px、颜色不是唯一状态载体、根容器禁止横向滚动
- Frontend quality verification plan: `npm test`、`npm run lint:miniapp`、`tools/validate_miniprogram.py`、`tools/preview` 三视口截图 + 横向溢出扫描
- Approved frontend engineering deviations: none

- Current Design Revision(s): `DREV-20260906-PKDS-03`
- Figma project/file URL: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1
- Figma node URL(s): N/A — 沿用 FEAT-001 的 Figma Starter 限额 waiver；本轮以仓内三视口截图为准
- Proposed Design Revision: `DREV-20260907-PKDS-04`
- Required viewport/state exports: 320×568 / 390×844 / 430×932 × 五个一级页面
- Prototype status: APPROVED（用户 2026-09-07 直接指定标题文案与页头方向，并要求「修改以上代码」）
- Approved Task Spec revision: `SPEC-20260907-PKDS-04`
- Approved Design Revision: `DREV-20260907-PKDS-04`
- Design approval evidence: 用户 2026-09-07 的三条具体要求（删提示 / 换品牌头 + icon / 指定 hero 文案）
- Snapshot manifest path: `dist/ui-preview/`（本地生成，未纳入 git；截图脚本可重放）
- UI current-state merge owner: Aime
- Frontend visual/a11y/resolution verification: 三视口近似渲染截图 + 5 页 × 3 视口横向溢出扫描 PASS；真机/开发者工具原生几何 NOT_RUN
- Figma waiver: 继承 FEAT-001 的 Starter 限额 waiver；公开发布前必须补 node-specific URL

## 1. Problem and outcome

- Problem：
  1. 界面里存在大量**说明控件怎么用**的备注（「点击切换」「可多选」「左右滑动查看」「可下钻」
     「打开可以修改资料或归档」「按实际参与情况添加，可设置固定时间」等）。这些提示不是后果说明，
     控件本身已经表达了 affordance，多写一行只增加视觉噪声和阅读成本。
  2. 一级 Tab 页的原生导航标题（今日 / 日程 / 记录 / 报表 / 设置）与底部 TabBar 逐字重复，
     顶部两处同名，浪费首屏并且没有品牌表达。
  3. 页头 hero 标题（「学习记录」「学习设置」「日程」）同样是标签式复述，语气偏功能说明书，
     与「纸 · 芽」克制、陪伴的产品立场不一致。
- Intended observable outcome：
  1. 五个一级页面顶部原生标题统一为小程序名「知芽」；页内出现统一的品牌头（嫩芽图标 + 知芽 +
     可选上下文 kicker）。
  2. 一级页面 hero 标题改为句子式：今日「今天，也慢慢来」、日程「这一周，心里有数」、
     记录「一笔一画，都算数」、报表「一点一滴，看得见」、设置「按你们的节奏来」。
  3. 只保留**后果类**与**边界类**说明（确认才入档、照片不用于展示分享、出行只显示在日程不生成待办、
     每周系列修改范围），删除操作说明类提示。
- Evidence/current behavior：改造前 `git show HEAD:apps/miniprogram/pages/settings/index.wxml`
  在设置页一页内即出现 9 处操作说明；`pages/*/index.json` 各自覆盖 `navigationBarTitleText`。

## 2. Scope

### In scope

- 新增 `apps/miniprogram/components/brand-head/`（js/json/wxml/wxss）。
- 五个一级页面 `index.json`：删除 `navigationBarTitleText` 覆盖，注册 `brand-head`。
- 五个一级页面 `index.wxml`：页头结构与 hero 文案。
- 删除/收敛冗余提示：设置、日程、报表、记录、今日、草稿模板、提交材料组件、家庭引导页。
- 报表紧迫度图改为图例（色块 + 文字），取代两行阅读说明。
- 相关 wxss：新增 `.pg-head.under-brand`、`.text-counter`；删除随文案一起作废的 `.read-hint`、
  `.travel-only-note`、`.card-head .c-r`、`.sheet-foot .foot-note`、`.sheet-tip`。
- `tools/preview/render.js` 注册 `brand-head`，使近似渲染可复现新页头。
- 测试：更新 2 个受影响用例，新增 `tests/frontend/brand-header-and-copy.test.js`。

### Non-goals

- 不改后端契约、不改任何数据写入路径与复习策略。
- 不新增页面、不改路由与 Tab 顺序。
- 不改 PKDS-2.0 token、配色与图标资源。

### Must not change

- AI 输出仍是可编辑草稿，只有家长确认才产生正式记录与复习计划——相关文案必须保留。
- 隐私边界文案（照片仅供核对，不用于展示或分享）保留。
- 出行安排「只显示在日程、不生成待办」的边界必须仍然可见，只是从三处收敛为一处。
- 每周重复日程「修改会作用于整个系列」在编辑重复项时仍要出现。
- 现有测试依赖的结构不变：报表 `swiper.day-swiper` + `[30,30,30,10]` 分页、TabBar 图标、`.page`/`.action-row`。

### Feature current-state impact

- Current Feature sections affected：UI-001 的信息架构、状态/交互契约、视觉系统段。
- Final facts to merge：页头结构、导航标题继承、提示保留原则。
- Superseded statements：「所有页头只保留当前上下文与统一的紧凑孩子切换器」需补充品牌头；
  报表「可下钻」标注与三行阅读说明。
- Change Reference to add：`SPEC-20260907-PKDS-04`。

## 3. Impact map

- Entry/caller：五个一级 Tab 页 + 草稿共享模板 + 提交材料组件 + 家庭引导页。
- Existing authoritative path to modify：`apps/miniprogram/pages/{today,calendar,records,reports,settings}/*`。
- Dependencies/callees：`styles/atoms.wxss`（页头原子层）、`styles/icons.wxss`（`.ico-sprout-pri`）。
- Existing tests：`tests/frontend/*.test.js`（124 项 → 127 项）。
- Behavior/architecture docs：`docs/design/frontend/ui/UI-001-parent-miniapp.md`。

## 4. Required design views

### Link/call graph

```text
app.json navigationBarTitleText = "知芽"
  → pages/{today,calendar,records,reports,settings}/index.json（不再覆盖标题，注册 brand-head）
    → components/brand-head/index.wxml（.ico-sprout-pri + 「知芽」 + kicker）
      → styles/icons.wxss（生成图标，禁止手工编辑）
    → .pg-head.under-brand（atoms.wxss）→ .pg-title（hero 句子）
tools/preview/render.js（注册 brand-head）→ dist/ui-preview/*.html → shoot.py → 三视口 PNG
```

### Sequence diagram

N/A：本轮无新增运行时交互序列，改动为静态结构与文案。

### State machine

N/A：未引入新的视图状态。`brand-head` 只有一个可选 `kicker` 属性，无内部状态。

### Architecture diagram

N/A：样式与组件依赖方向不变（tokens → atoms → app → page/component）。

### Trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 保留各页 `navigationBarTitleText` | 改动为零 | 与 TabBar 逐字重复，首屏两处同名 | rejected |
| 原生标题统一继承「知芽」，页内加品牌头 | 品牌一致、消除重复、hero 可写句子 | 页内多一行高度 | selected |
| 品牌头用位图 logo | 视觉更强 | 新增二进制资源、多套 DPR、包体增长 | rejected |
| 品牌头复用生成图标 `.ico-sprout-pri` | 与图标体系同源、零新增资源 | 图标较小，品牌感偏轻 | selected |
| 一次性删除全部说明文字 | 最干净 | 会删掉后果/边界说明，家长可能误操作 | rejected |
| 只删「操作说明」类，保留「后果 / 边界」类 | 噪声降低且不丢关键约束 | 需要逐条判定归类 | selected |
| 报表删说明后不补任何解释 | 最简 | 数字/勾/深浅色失去语义锚点，违反「颜色不是唯一信息」 | rejected |
| 报表删说明并补色块图例 | 语义仍在，占位更小 | 需要图例样式 | selected |

## 5. Expected file changes and deletion plan

| File/path | Action | Intended change | Why required |
|---|---|---|---|
| `apps/miniprogram/components/brand-head/*` | add | 品牌头组件（图标 + 知芽 + kicker） | 目标 1 |
| `apps/miniprogram/pages/{today,calendar,records,reports,settings}/index.json` | modify | 删标题覆盖、注册组件 | 目标 1 |
| `apps/miniprogram/pages/{today,calendar,records,reports,settings}/index.wxml` | modify | 品牌头 + hero 句子 + 删提示 | 目标 1/2/3 |
| `apps/miniprogram/pages/settings/index.js` | modify | 删除 `catalogSub` 视图字段 | 文案已删，字段无消费者 |
| `apps/miniprogram/pages/{settings,reports}/index.wxss` | modify | 删除作废样式 | 无用样式不留存 |
| `apps/miniprogram/pages/records/index.wxss`、`pages/submission/draft.wxss` | modify | 新增 `.text-counter` 右对齐计数 | 删掉同行说明后计数需独立成行 |
| `apps/miniprogram/pages/submission/draft.wxml` | modify | 删两处说明、计数独立 | 目标 1 |
| `apps/miniprogram/components/submission-materials/index.wxml` | modify | 去掉「点击可查看原图」 | 操作说明 |
| `apps/miniprogram/pages/family-onboarding/index.wxml` | modify | 去掉「下拉这一页也可以刷新」 | 操作说明 |
| `apps/miniprogram/styles/atoms.wxss` | modify | 新增 `.pg-head.under-brand`，删 `.sheet-tip` | 页头间距/清理 |
| `tools/preview/render.js` | modify | 注册 `brand-head` 与其样式 | 走查可复现 |
| `tests/frontend/reports-pagination.test.js`、`travel-calendar.test.js` | modify | 断言改为新的 UI 合同 | 旧断言指向已删文案 |
| `tests/frontend/brand-header-and-copy.test.js` | add | 固化页头与文案清理合同 | 防回归 |

Old path/logic to delete or retain：

- 删除操作说明类文案：「点击切换」「可多选」×2、「左右滑动查看，每屏最多 30 天」「每格一天……」
  「数字表示当天待复习知识数……」「可下钻」「打开可以修改资料或归档」「已归档，记录和报表仍可查看」
  「按实际参与情况添加，可设置固定时间」「切换后所有页面同步」×3「打开或取消这个弹层都不会写入数据」
  「不在目录里，也可以按实际名称添加」「下拉这一页也可以刷新申请状态」「点击可查看原图」
  「保存后按所选星期重复，只显示在「日程」」「固定安排会显示在「日程」与「今日」」
  「开启后，之后每周的同一时间都会出现这条安排」「写清楚学了什么就够了，不用写评价」×2
  「照片会整理成可编辑的草稿……」「文字会整理成可编辑的草稿……」「每个科目会分别生成一条学习记录……」。
- 保留并收敛：出行边界由三处合并为卡片副标题「只显示在日程，不生成待办」一处；
  每周系列提示改为仅在「编辑 + 重复」时出现。

## 6. Acceptance criteria

### AC-001 — 顶部不再与 TabBar 重复

- Given 任一一级 Tab 页；When 打开；Then 原生标题是「知芽」；And not 页面 JSON 覆盖 `navigationBarTitleText`；
  And not hero 标题等于该 Tab 的标签文字。

### AC-002 — 品牌头存在且不引入位图

- Given 五个一级页面；When 渲染；Then 页头出现 `brand-head`（`.ico-sprout-pri` + 「知芽」）；
  And not 使用 `<image>` 或 emoji 作为品牌标识。

### AC-003 — hero 文案按用户指定

- Given 今日 / 报表页；When 渲染；Then 标题分别是「今天，也慢慢来」「一点一滴，看得见」；
  And 日程 / 记录 / 设置为同风格句子。

### AC-004 — 操作说明类提示已清除

- Given 全部小程序 WXML；When 静态检索；Then 不再出现「点击切换」「可多选」「左右滑动查看」
  「可下钻」「点击可查看原图」等操作说明；And not 依赖这些文字才知道控件可用。

### AC-005 — 后果与边界说明仍在

- Given 草稿区 / 出行卡片 / 原始材料 / 重复日程编辑；When 渲染；Then 仍分别出现「确认后才……」、
  「只显示在日程，不生成待办」、「照片仅供你核对，不用于展示或分享」、「修改会作用于整个每周系列」。

### AC-006 — 报表语义不靠颜色单载体

- Given 紧迫度图；When 渲染；Then 图例同时给出「数字：当天待复习」与「已全部通过」的文字说明。

### AC-007 — 三视口无横向溢出

- Given 320 / 390 / 430；When 渲染五个一级页面预览；Then `documentElement.scrollWidth <= viewport` 且无越界元素。

## 7. Required test points

| Test point | AC | Level | Command | Required result |
|---|---|---|---|---|
| TP-001 | AC-001..006 | unit/static | `npm test` | all pass |
| TP-002 | — | static | `npm run lint:miniapp` | no error |
| TP-003 | AC-001/002 | static | `uv run python tools/validate_miniprogram.py` | `MINIPROGRAM_VALID` |
| TP-004 | AC-002 | static | `uv run python tools/gen_icon_styles.py` | 产物 diff 为空 |
| TP-005 | — | static | `uv run python tools/check_architecture.py` | `ARCHITECTURE_VALID` |
| TP-006 | AC-001..006 | visual | `node tools/preview/render.js && python3 tools/preview/shoot.py today calendar records reports settings` | 三视口截图人工走查通过 |
| TP-007 | AC-007 | visual | Playwright 横向溢出扫描（5 页 × 3 视口） | 无溢出 |
| TP-008 | AC-001..007 | native | 微信开发者工具 / 真机三视口原生几何 | NOT_RUN（需人工） |

## 8. Plan

1. 建 `brand-head` 组件与 `.pg-head.under-brand` 间距。
2. 五个一级页 JSON/WXML 改页头与 hero。
3. 逐页删提示，按「操作说明删 / 后果边界留」判定。
4. 更新与新增测试，跑 TP-001..005。
5. 近似渲染三视口走查 + 溢出扫描（TP-006/TP-007）。
6. 合并 UI-001 现状与本 Spec 验证段。

## 9. Verification

| Test point / command | Result | Evidence/notes |
|---|---|---|
| TP-001 `npm test` | pass | 127 passed（改造前 124，其中 2 项断言旧文案，已按新合同更新；新增 3 项） |
| TP-002 `npm run lint:miniapp` | pass | ESLint 无输出（先执行 `npm install` 补齐依赖） |
| TP-003 `uv run python tools/validate_miniprogram.py` | pass | `MINIPROGRAM_VALID pages=15 source_bytes=625897` |
| TP-004 `uv run python tools/gen_icon_styles.py` | pass | `ICONS_WRITTEN icons=42 variants=6`，`icons.wxss` 无 diff |
| TP-005 `uv run python tools/check_architecture.py` | pass | `ARCHITECTURE_VALID checked=3` |
| TP-006 三视口截图走查 | pass | `dist/ui-preview/{today,calendar,records,reports,settings}-{320,390,430}-vp.png`，品牌头与 hero 完整、无顶部拥挤 |
| TP-007 横向溢出扫描 | pass | 5 页 × 3 视口 = 15 组，`OVERFLOW_FAILURES 0` |
| TP-008 原生三视口几何 | not run | 需微信开发者工具/真机；HTML 近似渲染不能替代原生节点几何 |

后端未改动，本轮未跑后端测试套件（无 Python 生产代码变更；`tools/` 变更由 TP-003..005 覆盖）。

## 10. Completion

- Changed behavior：仅可见层。导航标题继承、页头结构、hero 文案、提示密度、报表图例。
- Deleted/replaced behavior：操作说明类提示、`catalogSub` 视图字段、三处重复的出行边界说明、
  报表三行阅读说明（由图例替代）。
- Permitted implementation deviations：`dist/ui-preview/` 为本地产物不入库；Figma node URL 仍缺，沿用 waiver。
- Residual risk：原生导航栏在部分机型上的标题字重/截断、品牌头在超大字体下的换行未在真机验证；
  TP-008 NOT_RUN。

- [x] Scope/non-goals preserved.
- [x] Acceptance criteria pass（AC-001..007）。
- [x] Required commands ran（TP-001..007）。
- [x] No duplicate/legacy path remains.
- [x] Docs updated（UI-001 现状段与 Change reference）。
- [ ] 真机 / 开发者工具三视口验收（待人工）。
