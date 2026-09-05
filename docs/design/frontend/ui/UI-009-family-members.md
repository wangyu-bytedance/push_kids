# UI-009 — 家庭与成员

- Status: `CURRENT_LOCAL / 390_NATIVE_CAPTURED / MATRIX_PENDING`
- Related Feature: `FEAT-002`
- Related Spec: `SPEC-20260831-09`
- Baseline: `FDB-20260830-01`
- Engineering contract: `FEC-20260830-01`
- Design revision: `DREV-20260905-UX-03 / AMENDMENT-02`
- Last reviewed artifact date: 2026-08-31
- Interactive artifact: `docs/design/frontend/prototypes/DREV-20260831-07/index.html`
- Snapshot manifest: `docs/design/frontend/snapshots/UI-009/DREV-20260831-07/APPROVAL.md`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `N/A` — 当前账号为 Starter/View，MCP 写入限额已触发

> BUG-010 revision 11 已获产品负责人批准并在本地实现；390视口成员主页及本人详情已由CUA验证，未部署，其他视口、双账号与真机证据仍待补齐。

## Information architecture

入口位于“设置 / 家庭与成员”。所有 active 家庭成员均可进入并查看成员姓名、与孩子的关系及
当前协作能力。manager 额外看到加入申请、邀请入口和成员管理入口；viewer/editor 不展示
这些管理操作，服务端仍须独立鉴权。

## Review states

| State | Visible contract |
|---|---|
| manager content | 孩子上下文、加入申请数量、全部成员、关系、能力、邀请和管理入口 |
| member content | 全部成员、自己的关系与能力；无申请处理、邀请、退出或成员管理入口 |
| narrow viewport | 成员列表保持内容高度并在页面内滚动，底部 Tab 可达 |

关系称谓和授权角色分开表达。`爸爸/妈妈/奶奶/其他` 不自动映射为 manager。服务端角色仍为
`viewer/editor/manager`，用户界面显示为“仅查看/可记录/管理员”。历史上传和监督记录即使成员
退出也保留原作者。

## Interaction and safety contract

- 成员列表对所有 active guardian 可见。
- 待审批数量、邀请、关系和权限调整只对 manager 可见。
- 本人详情不提供移除、退出或角色修改；服务端无条件拒绝成员管理接口自移除。
- 最后一位 manager 的移除或降权必须阻止并说明先转交管理权。
- 其他成员的降权和移除属于破坏性操作，展示影响并二次确认。
- 管理入口和成员卡片占满统一内容列；导航型行不依赖原生 button 的默认宽度；邀请说明与接口降级状态只占一个提示区。
- loading、empty、error、401/403、成员并发变更等工程状态遵循 `FEC-20260830-01`；本轮快照
  只评审权限差异最大的两个 content 状态。

## Visual and responsive contract

沿用现有暖纸色、低饱和青绿、系统中文字体、克制分隔线和低阴影；不新增品牌色、字体或
图像依赖。评审矩阵为 320×568、390×844、430×932。正文不小于 14px，主要触控目标不小于
44px，权限不只依靠颜色表达。

## Approval status

本地页面已改为整行进入成员详情；本人只可在现有授权下编辑称谓，其他成员的权限保存先确认，
移除位于独立危险区。390×844当前账号截图证明成员主页、自身标记和正圆刷新按钮；线上旧后端缺少
有效邀请GET时页面显示局部降级提示并继续展示成员。实施使用 `FIGMA-WAIVER-BUG010-20260905-01`；
320/430、成员详情真实点击和双账号验证仍是发布门禁。
