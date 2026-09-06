# UI-009 — 家庭与成员

- Status: `CURRENT_LOCAL / 390_NATIVE_CAPTURED / MATRIX_PENDING`
- Related Feature: `FEAT-002`
- Related Spec: `SPEC-20260831-09`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Design revision: `DREV-20260906-PKDS-01`（屏 G4；取代 `DREV-20260905-UX-04` 的视觉部分）
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

## Proposed FEAT-002 extension — not implemented

`SPEC-20260906-MULTI-FAMILY-05 / DREV-20260906-MULTI-FAMILY-02` proposed 以下增量；它不改变上文
CURRENT_LOCAL 事实，在 Spec + Figma node/snapshot 获批前不得实现。

### Member row with optional identity

```text
（头像） 张明  你                                  ›
        爸爸 · 可共同记录 · 可记录与确认
```

- 当前页面没有真实名字/头像字段；“爸爸”和“爸”均来自 `relationship_label`。
- 新资料为 optional、本人维护、按 FamilyMember 隔离：有名字时主标题显示名字，副标题显示关系+权限；
  无名字时继续以关系称谓为主标题。
- 有头像时正圆裁切；未设置、加载失败或成员已退出时回落到关系称谓首字，不显示破图。
- 本人详情增加“我的展示资料”，可修改/清空名字和选择/移除头像；管理员不能编辑他人的名字/头像，
  仍只管理 relationship 与 role。
- 不自动读取微信资料，不从 OpenID/metaid 推导；资料不阻断家庭创建、加入、审批或使用。

### Leave-family danger zone

viewer/editor 打开本人详情时，在表单之后显示：

```text
退出家庭
退出后，你将无法查看或记录「小雨的家」的内容。
已有的学习记录会保留；以后需要重新申请才能加入。

[退出这个家庭]
```

- 点击后再次确认具体家庭名；确认按钮为“退出家庭”，pending 时 sheet 不可关闭且不可重复提交。
- 成功后清当前家庭 cache/preference，刷新 `/me`：有其他家庭则进入已重新验证的选择，无家庭则 onboarding。
- manager 不显示退出按钮，显示“管理员不能直接退出，请先完成管理权交接并由另一位管理员调整你的权限”。
- 退出不是数据删除；学习历史不变。头像对象与 optional display profile 按隐私合同清理，历史归属回落到
  member ID + 关系称谓。

需补齐 320×568、390×844、430×932 的本人非管理员、本人管理员、头像/无头像、长名字、退出确认、
pending/error/success 及多家庭回落状态。

## Approval status

本地页面已改为整行进入成员详情；本人标记为“我”，只可在现有授权下编辑称谓，其他成员的权限保存先确认，
移除位于独立危险区。390×844当前账号截图证明成员主页、自身标记、卡片边界和正圆刷新按钮；线上旧后端缺少
有效邀请GET时静默降级并继续展示成员，不制造类似整页错误的警告。实施使用 `FIGMA-WAIVER-BUG010-20260905-01`；
320/430、成员详情真实点击和双账号验证仍是发布门禁。

## Change references

- 2026-09-06 — `SPEC-20260906-PKDS-01 / DREV-20260906-PKDS-01`（屏 G4）：成员页按 PKDS-1.0 重做。
  Hero 承载"邀请家人"；邀请口令只保留在内存中用于一次分享，不上屏持久化、不写入日志；
  成员行使用首字头像并明确区分角色文案与"你"；成员详情改为底部半屏，只读成员降级为只读值；
  移除成员与降权是破坏性操作，展示影响并二次确认；补齐骨架、空态、页内错误态与下拉刷新。
  为满足既有测试断言，复制按钮文案是"复制邀请"而不是设计稿的"复制口令"（成员页不得出现
  "邀请口令"字样）；editor 角色沿用 BUG-010 已定的"可共同记录"。
  320×568 / 430×932、双账号与真机仍为 `NOT_RUN`。
