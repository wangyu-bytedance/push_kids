# UI-009 — 家庭与成员

- Status: `DELIVERED_CLIENT_0.1.16 / DEVELOPMENT_DONE / 390_NATIVE_CAPTURED / MATRIX_PENDING`
- Related Feature: `FEAT-002`
- Related Specs: `SPEC-20260831-09`; `BUG-SPEC-20260913-19`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Design revisions: `DREV-20260906-PKDS-01`（屏 G4）；`DREV-20260913-FAMILY-INVITE-CODE-01`（邀请就绪态）
- Last reviewed artifact date: 2026-09-13
- Lifecycle update: 2026-11-05；多家庭 Spec 及附带退出提案已取消，已交付页面与原设计/验收状态保持各自范围。
- Interactive artifacts: `docs/design/frontend/prototypes/DREV-20260831-07/index.html`;
  `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Current change snapshot manifest: `docs/design/frontend/snapshots/UI-009/DREV-20260913-FAMILY-INVITE-CODE-01/APPROVAL.md`
- Current change editable design source: `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Design evidence governance: `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`

> BUG-015 revision 19 与邀请就绪态 DREV 已获产品负责人批准并在本地实现；三视口仓库快照已通过
> manifest校验。对应实现已随037/0.1.16交付；完整原生三视口、双账号与真机证据仍待补齐。

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
- manager 创建邀请成功后在内存态显示六位纯数字“家庭邀请码”，支持复制或微信邀请；明确说明
  申请提交后仍需 manager 确认。页面不把长 token 显示或写入本地存储。
- 本人详情不提供移除、退出或角色修改；服务端无条件拒绝成员管理接口自移除。
- 最后一位 manager 的移除或降权必须阻止并说明先转交管理权。
- 其他成员的降权和移除属于破坏性操作，展示影响并二次确认。
- 管理入口和成员卡片占满统一内容列；导航型行不依赖原生 button 的默认宽度；邀请说明与接口降级状态只占一个提示区。
- loading、empty、error、401/403、成员并发变更等工程状态遵循 `FEC-20260830-01`；本轮快照
  只评审权限差异最大的两个 content 状态。

## Visual and responsive contract

本地视觉增量revision `UI-VISUAL-20261021-HERO-ARC-01`：家庭邀请卡已随共享样式删除右下角细弧线，
其余邀请、成员和权限合同保留。批准来源为
[Spec01](../../../../specs/completed/BUG-030-HERO-BACKGROUND-ARC.md) /
[DREV-20261021-HERO-ARC-REMOVAL-01](../prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/FRONTEND-SPEC.md)，
验收范围见[质量证据](../../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)；该样式已随0.1.16开发上传，完整原生/设备验收待补。

沿用现有暖纸色、低饱和青绿、系统中文字体、克制分隔线和低阴影；不新增品牌色、字体或
图像依赖。评审矩阵为 320×568、390×844、430×932。正文不小于 14px，主要触控目标不小于
44px，权限不只依靠颜色表达。

## Extension scope and cancellation

用户于2026-11-05明确取消[多家庭 Spec](../../../../specs/rejected/FEAT-002-MULTI-FAMILY-CHILD-TENANT-ISOLATION.md)，其中附带的非管理员退出与多家庭回落交互一并取消，未实施，不再等待本修订批准。本人详情继续不提供退出入口；当前家庭成员页面与服务端权限保持既有合同。

成员微信头像/昵称已由产品负责人于2026-09-11确认为非关键 feature，仍为独立低优先级后续记录；未来必须另立 Spec 和 Design Revision 并获得批准后才能实现。

### Deferred low-priority backlog — member row with optional identity

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
- 当前不新增数据库/API/对象存储字段，不安排实现或验收；成员行继续显示关系称谓与首字头像。

### Cancelled leave-family proposal

非管理员退出确认、pending/error/success、管理员交接提示和多家庭回落矩阵随关联 Spec 取消，历史方案保留在归档 Spec 与 UI-014。它们不再构成本页待实施范围或发布门禁，已有成员管理/角色的验收缺项不受此取消影响。

## Approval status

本地页面已改为整行进入成员详情；本人标记为“我”，只可在现有授权下编辑称谓，其他成员的权限保存先确认，
移除位于独立危险区。390×844当前账号截图证明成员主页、自身标记、卡片边界和正圆刷新按钮；线上旧后端缺少
有效邀请GET时静默降级并继续展示成员，不制造类似整页错误的警告。旧 Figma waiver 仅保留为当时批准历史；
320/430、成员详情真实点击和双账号验证仍是发布门禁。

## Change references

- 2026-11-05 — 产品负责人取消`SPEC-20260911-MULTI-FAMILY-06`；同步退出交互取消，当前页面未修改，原已批准设计资产不变。

- 2026-09-13 — `BUG-SPEC-20260913-19 / DREV-20260913-FAMILY-INVITE-CODE-01`：邀请就绪卡新增
  六位家庭邀请码和复制入口，同时保留微信分享；候选 320×568、390×844、430×932 快照及 SHA-256
  manifest 已批准并通过校验。原生矩阵和双账号仍为 `NOT_RUN`。

- 2026-09-06 — `SPEC-20260906-PKDS-01 / DREV-20260906-PKDS-01`（屏 G4）：成员页按 PKDS-1.0 重做。
  Hero 承载"邀请家人"；邀请口令只保留在内存中用于一次分享，不上屏持久化、不写入日志；
  成员行使用首字头像并明确区分角色文案与"你"；成员详情改为底部半屏，只读成员降级为只读值；
  移除成员与降权是破坏性操作，展示影响并二次确认；补齐骨架、空态、页内错误态与下拉刷新。
  为满足既有测试断言，复制按钮文案是"复制邀请"而不是设计稿的"复制口令"（成员页不得出现
  "邀请口令"字样）；editor 角色沿用 BUG-010 已定的"可共同记录"。
  320×568 / 430×932、双账号与真机仍为 `NOT_RUN`。
