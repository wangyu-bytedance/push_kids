# DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01 — 今日页活动空态行动收敛

- Status: APPROVED
- Related Spec: `SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`
- Affected UI: `UI-001 / pages/today/index`
- Baseline: `FDB-20260906-03`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260906-04`
- Figma anchor under existing FEAT-001 waiver: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Interaction direction

今日页是 Operate 型首页，继续保持“暖纸底、松绿主操作、低装饰”的既有方向。本修订只收敛重复行动：
添加日程保留在上方首屏主卡（首次引导态则保留其互斥链接），课外活动空态只陈述事实。

## Approved-target layout

```text
今天的复习安排
今天没有必须做的复习
[ 记录学习 ]  [ 添加日程 ]     ← 保留

……

课外活动  0项
────────────────────────
       今天没有活动安排        ← 保留
       [ 添加日程 ]             ← 删除
```

当首页处于首次引导态时，上方区域显示“也可以先添加日程”，与普通主卡互斥；下方活动空态仍不出现按钮。

## States and boundaries

- `activity_count=0`：显示居中空态文字，不具有按钮角色、`bindtap` 或 accessible action name。
- `activity_count>0`：时间线、活动建议和“记录这次练习”保持不变。
- 普通主卡：继续保留“添加日程”。
- 首次引导卡：继续保留“也可以先添加日程”。
- 不改折叠箭头、区块高度 token、空态文字样式、日程页或跳转逻辑。

## Responsive and accessibility matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / activity empty | 空态文字居中；删除按钮后无异常占位；上方唯一日程入口可达 |
| 390×844 / activity empty | 作为主视觉对照；活动区无重复交互语义 |
| 430×932 / activity empty | 内容最大宽度不变；空态不因按钮删除而拉伸 |
| screen reader semantics | 活动空态只读；页面当前状态仅暴露一个可用的日程添加入口 |

## Approval boundary

批准即授权：删除活动空态内的下方“添加日程”按钮，保留空态文字和上方互斥入口；不授权重排首页、
修改日程流程或删除首次引导入口。请明确批准：

- `SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`
- `DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`
- 本修订继续沿用 FEAT-001 scoped Figma waiver，且该 waiver 在公开生产发布前到期

Approval evidence: 用户于 2026-09-11 回复“落地”。批准快照：
`docs/design/frontend/snapshots/UI-001/DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01/APPROVAL.md`。

## Local implementation evidence

- 活动空态按钮节点已删除，只保留“今天没有活动安排”；普通主卡与首次引导态仍各有一个互斥日程入口。
- 当前工作树前端 `138 passed`，ESLint、小程序静态与架构检查通过；真实 AppID 本地 preview
  编译 `574832` bytes，未上传。
- 320/390/430 HTML fixture 已生成；PNG 渲染因环境缺少 Playwright 未运行，原生三视口和
  iOS/Android 仍为 `NOT_RUN`，不声明视觉矩阵完成。
