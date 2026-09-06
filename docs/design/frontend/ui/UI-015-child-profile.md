# UI-015 — 学习档案管理与切换入口

- Status: `CURRENT_LOCAL / MATRIX_PENDING / FIGMA_WAIVED`
- Related Feature: `FEAT-005`
- Related Spec: `SPEC-20260906-MULTI-CHILD-01`
- Baseline: `FDB-20260906-02`（PKDS-1.0）
- Engineering contract: `FEC-20260906-04`
- Design revision: `DREV-20260906-CHILD-01`（DRAFT，视觉沿用 `DREV-20260906-PKDS-01` 既有 token 与组件类）
- Last reviewed artifact date: 2026-09-06
- Interactive artifact: `N/A` — 未产出原型
- Snapshot manifest: `pending — docs/design/frontend/snapshots/UI-015/DREV-20260906-CHILD-01/APPROVAL.md`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `N/A` — 本环境无 Figma 访问能力，适用 `SPEC-20260906-MULTI-CHILD-01` 的 waiver

> 本文描述已在工作区实现并通过 `npm test` / `npm run lint:miniapp` / `tools/validate_miniprogram.py` 的当前状态。
> 320×568 / 390×844 / 430×932 三视口原生节点几何证据未采集（本环境无微信开发者工具），公开生产发布前必须补齐。

## Information architecture

- 入口一：设置页新增「学习档案」区，列出在用档案（标记「当前」）与已归档档案（标记「已归档」），
  底部是「添加孩子」；达到上限时该入口替换为上限说明文案。
- 入口二：今日、日程、报表、设置四个页面的「选择孩子」弹层底部新增「添加孩子」。
- 入口三：无档案空态提供「建立学习档案」主按钮，与「家庭与成员」并列。此前空态只指向「家庭与成员」，
  而该页面无法建档，是死路；现已修复。
- 目标页：`pages/child-edit`（导航标题「学习档案」），同一页面承担新建、编辑、归档与恢复。

```text
设置 / 学习档案 ─┬─ 在用档案行 → child-edit（编辑 / 归档）
                 ├─ 已归档档案行 → child-edit（恢复）
                 └─ 添加孩子 → child-edit（新建）
今日 / 日程 / 报表 / 设置 选择孩子弹层 └─ 添加孩子 → child-edit（新建）
```

## Review states

| State | Visible contract |
|---|---|
| 新建 | 名字、年级、每天复习时长、「已经在学的科目」多选（语文/数学/英语）、主按钮「建立档案」 |
| 编辑（在用，manager） | 名字/年级/时长 + 「档案状态」卡的归档危险区 |
| 编辑（已归档，manager） | 顶部归档说明提示 + 「恢复这个档案」 |
| 编辑（editor） | 只有资料表单，无「档案状态」卡 |
| 只读成员（viewer） | 设置页不展示建档与添加入口；页面级也不进入表单 |
| 达到上限 | 新建页顶部提示上限文案；设置页隐藏「添加孩子」并显示上限说明 |
| loading | 表单区骨架屏 `card-sk` |
| error | 页内 `pk-notice err`，不使用只在 Toast 里出现的关键错误 |

## Interaction and safety contract

- 名字是切换列表的识别依据：同时在用的档案不能重名，帮助文案在输入框下明确说明；
  服务端 409 文案回显在页内错误区。
- 空名字不发请求；创建失败保留已填内容与已选科目，家长不必重填。
- 创建成功后自动把全局选中孩子切换为新档案并返回上一页，避免「建完却看不到」。
- 归档与恢复是改变全家可见范围的操作：仅 manager 可见入口，归档需二次确认，
  文案明确说明「不会删除任何记录，报表和历史仍可查看」；服务端拒绝时展示错误而不静默。
- 选中的档案被归档或消失时，各 Tab 自动回落到第一个在用档案；全部归档后清空选择并回到空态，
  不出现白屏或 404。
- 设置页请求带代际标记（race guard），快速切换或重复刷新时丢弃迟到响应，不展示上一个孩子的数据。
- 保存与归档进行中按钮进入 `is-disabled` 并展示「正在保存…/处理中…」，避免重复提交。

## Visual and responsive contract

沿用 PKDS-1.0：`pk-card`、`pk-field`、`pk-input`、`pk-picker`、`pk-notice`、`rowlist/rowitem`、
`btn`、`link-btn`、`add-entry`、`pill`、`sk`。不新增配色、字号、圆角或图像依赖；`add-entry` 由
设置页局部样式提升为 `styles/atoms.wxss` 中的全局原子，供四个弹层与设置页复用。评审矩阵为
320×568、390×844、430×932；正文不小于 14px，主要触控目标不小于 44px；「当前 / 已归档」状态
同时用文字标签表达，不只依赖颜色。图标均带 `aria-role` / `aria-label`。

## Approval status

`SPEC-20260906-MULTI-CHILD-01` 已获产品负责人批准并在本地实现。自动化证据：`npm test` 72 pass
（其中 `tests/frontend/child-profiles.test.js` 13 例覆盖回落、上限、只读成员、创建/归档/恢复流程与
迟到响应丢弃）、`npm run lint:miniapp` 通过、`MINIPROGRAM_VALID pages=13 source_bytes=484544`。
待补齐：Figma 节点与审批快照、三视口原生节点几何、真机与双账号验证。

## Change references

- 2026-09-06 — `SPEC-20260906-MULTI-CHILD-01 / DREV-20260906-CHILD-01`：新增 `pages/child-edit` 与设置页
  「学习档案」区，四个选择孩子弹层新增「添加孩子」，修复无档案空态死路；新增共享
  `utils/child-context.js` 统一孩子装饰、选中解析与失效回落，并为设置页补齐请求代际保护。
  三视口与 Figma 证据为 `NOT_RUN`，沿用本 Spec 的 waiver。
