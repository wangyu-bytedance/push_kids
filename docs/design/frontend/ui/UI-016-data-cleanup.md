# UI-016 — 删除配置

- Status: `IMPLEMENTING / FIGMA_WAIVED`
- Related Feature: `FEAT-006`
- Related Spec: `SPEC-20260906-DATA-CLEANUP-01`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Proposed design revision: `DREV-20260906-DATA-01`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `N/A — FIGMA-WAIVER-FEAT006-20260906-01`
- Snapshot manifest: `docs/design/frontend/snapshots/UI-016/DREV-20260906-DATA-01/APPROVAL.md`

> 用户于 2026-09-06 批准本 Spec、DREV 与一次性 Figma waiver；本文仍在实现中，尚不能描述为已验证 current state。

## Proposed information architecture

设置页在“家庭与成员”附近新增低强调导航行“删除配置”。入口本身不使用整块危险红色；进入页面后再按
影响范围分成两个操作：

```text
设置
└─ 家庭与成员
   └─ 删除配置 ›

删除配置
├─ 删除孩子资料 → 选择孩子 → 影响摘要 → 输入孩子称呼 → 确认/状态
└─ 删除当前家庭 → 资格检查 → 影响摘要 → 输入家庭名称 → 确认/状态
```

## Proposed states

| State | Visible contract |
|---|---|
| overview | 解释“归档可恢复、删除不可恢复”；列出两个作用域，不默认选中 |
| child eligible | 显示目标孩子、将删除的数据类别、归档替代入口与永久删除入口 |
| child confirmation | 必须输入当前孩子称呼；取消零写入；确认按钮明确写“确认删除” |
| family ineligible | 多成员或非 manager 时说明原因，不展示可误触的 enabled 按钮 |
| family confirmation | 显示整个家庭影响与 actor 将回到首次进入；输入当前家庭名称 |
| pending/running | 显示“正在清理”，无虚假百分比；离页后可恢复状态 |
| retryable failure | 页内安全错误、重试入口和目标仍被冻结的说明 |
| succeeded child | 刷新 bootstrap，回落到剩余孩子或无档案空态 |
| succeeded family | 清理 family/child 选择后 reLaunch 无家庭 onboarding |
| unauthorized/not-found | 安全拒绝，不泄露其他家庭/孩子存在性 |

## Proposed interaction and safety contract

- “删除配置”只是导航名；最终按钮和确认文案必须直接说明永久删除及不可恢复。
- 删除孩子前提供“改为归档”的可恢复替代，但不把它设为已选择状态。
- 提交中禁用重复操作；请求使用稳定幂等键；页面恢复时查询服务端状态。
- 客户端只负责展示，manager/sole-member/family scope 必须由服务端再次验证。
- 删除后清除本地 stale child/family selection；本地存储和日志不得保留确认名称、媒体路径或身份信息。

## Related UI-010 change

`unbound` 首屏只展示两个等价可理解的路径：主操作“创建家庭”、次操作“申请加入家庭”。创建家庭表单只收
家庭名称与本人家庭内称谓，不收孩子字段，不调用 `/children`。创建成功进入家庭内的无档案空态；
`child-edit` 对未绑定 actor 直接回到 onboarding。

## Visual and responsive proposal

沿用 PKDS-1.0 `pk-card / rowitem / pk-notice / pk-field / btn / link-btn` 与现有 danger semantic token，
不新增颜色、圆角、字体、依赖或图标风格。危险色只用于最终确认和影响提示。要求 320×568、390×844、
430×932；长家庭/孩子名称换行；键盘打开时确认与取消均可达；触控目标 ≥44px，正文 ≥14px，状态不只靠颜色。

## Approval and evidence status

- Task Spec approval: `SPEC-20260906-DATA-CLEANUP-01` approved 2026-09-06.
- DREV/Figma nodes/snapshot: `DREV-20260906-DATA-01` 通过 `FIGMA-WAIVER-FEAT006-20260906-01` 批准；公开生产前补齐 node 与三视口证据。
- Frontend code/tests/native viewport/device evidence: not started/not run.
- Waiver 只覆盖本 Feature 本地实现，不扩展到其他 Feature。
