# DREV-20260913-UNIFIED-REVIEW-01 — 统一复习计划与确认分类

- Status: `APPROVED`
- Surface: `UI-001 / Today / 上传确认`
- Related Task Spec: `SPEC-UNIFIED-REVIEW-20260913-04`
- Baseline: `FDB-20260913-04 / PKDS-2.0 纸 · 芽`
- Engineering contract: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Candidate snapshots:
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/today-plan-320.png`
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/today-plan-390.png`
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/today-plan-430.png`
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-320.png`
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-390.png`
  - `docs/design/frontend/snapshots/UI-001/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-430.png`
- Editable sources:
  - `docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/today-plan-390.svg`
  - `docs/design/frontend/prototypes/DREV-20260913-UNIFIED-REVIEW-01/confirm-kinds-390.svg`
- Design evidence governance: `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`
- External design dependency: `none`

## 一句话方向

沿用暖白纸面、松绿主色和衬线标题，用清楚但低压力的事实文案把“今天先复习什么”和“确认后会更新什么”
讲明白；不增加家长配置、分类选择或新的主流程。

## 用户目标

家长仍只做三步：上传材料、核对并确认、按 Today 复习。系统内部把知识分成 `new`、
`today_review`、`history_item`，但界面只呈现可理解的结果与确认后果，不要求家长理解算法或数据库状态。

## 1. Today：稳定的当日计划

- Today 的复习卡片、数量和分钟全部读取 `dashboard.review_selection`，不再读取全量到期
  `todo_groups` 作为主展示集合。
- Hero 显示“今天安排 N 项，约 M 分钟”；N 为尚未完成的当日计划项，M 为尚未完成分钟。
- 计划按科目聚合，卡片继续复用现有 TodoCard；反馈仍是完成、需要巩固、部分完成、稍后。
- `backlog_count > 0` 时只显示一条低强调说明：
  `今天先做 N 项，其余 K 项会按最早到期顺序安排到后续复习。`
- 不使用“欠账、积压、落后、必须清空”等压力词，不把 `backlog_count` 伪装成今天任务数。
- 当日计划首次生成后保持稳定；完成一项只更新当前计划状态，不动态补入新项目。
- `planned_count > 0 && selected_count == 0` 时显示：
  `今天安排的 N 项已完成，今天不会再补入新内容。`
- 当天没有计划时继续展示最近一次未来复习安排；旧后端没有 `review_selection` 时回落到现有
  `todo_groups`，但不展示积压或稳定计划承诺。

## 2. 确认页：三类 Item 的后果可见

每个 AI 知识点在标题旁显示一个只读分类标签，不增加新的选择器：

| 模型类型 | 家长可见标签 | 确认后说明 | 操作 |
|---|---|---|---|
| `new` / `new_learning` | 新知识 | 新增知识，并按规则安排下次复习 | 保留现有编辑/移除 |
| `today_review` | 今日复习 | 完成今天对应的复习，并更新下次复习时间 | 可取消已有知识关联 |
| `history_item` / `review` | 历史复习 | 沿用以前的知识，记录这次复习并更新下次复习时间 | 可取消已有知识关联 |

- 标签永远不表示掌握、正确或得分。
- `today_review/history_item` 必须同时显示已关联知识名称；引用缺失、过期或不属于当前家庭时由
  服务端拒绝，前端保留草稿并提示刷新。
- 家长不需要逐项重新选择类别；确认整批即可。若关联错误，沿用“取消关联”，取消后作为新知识处理。
- 原“可能已完成的复习”分区只保留兼容旧草稿；新草稿以知识点卡内标签为唯一主表达，避免同一项展示两次。
- 成功确认后返回服务端的 `updated_reviews`，只用于刷新 Today/记录详情，不在客户端计算日期。

## 3. 状态矩阵

| Surface/state | 可见结果 | 恢复/动作 |
|---|---|---|
| Today loading | 保留旧摘要或同几何骨架 | disabled |
| Today 正常计划 | 今日剩余 N 项、M 分钟、科目卡 | 反馈后原位更新 |
| Today 有历史到期未选 | 一句低压力后续安排说明 | 不展开全部、不改期 |
| Today 全部完成 | 今日已完成、今天不补题 | 可查看已完成折叠区 |
| Today 无计划、有未来 | 最近未来日期与只读知识 | 可查看来源 |
| Today 无计划、无未来 | 真实空态 | 记录学习 |
| Today 旧后端 | 复用 0.1.7 的 Todo 展示 | 不声称稳定计划 |
| Confirm new | 新知识标签与新增后果 | 编辑/移除/整批确认 |
| Confirm today review | 今日复习标签与对应知识 | 取消关联/整批确认 |
| Confirm history review | 历史复习标签与对应知识 | 取消关联/整批确认 |
| Confirm stale/409 | 保留所有编辑，说明计划已变化 | 刷新后重新核对 |
| viewer | 与 manager 同样可读 | 不显示写操作 |

## 4. 视口与无障碍

- 320×568、390×844、430×932 竖屏；单列，最大内容宽 480px。
- 分类标签与结果说明允许换行，不降低至 12px 以下；触控目标至少 44px。
- 状态由标签文字、说明和位置共同表达，不只依赖颜色。
- 长中文知识名称完整换行；积压说明里的 N/K 使用服务端整数，不在客户端推算。
- 不新增动画；沿用现有 disclosure 过渡和 reduced-motion 规则。

## 5. 数据映射

```text
dashboard.review_selection.sessions -> Today 复习卡
dashboard.review_selection.selected_count -> 今日剩余项数
dashboard.review_selection.selected_minutes -> 今日剩余分钟
dashboard.review_selection.planned_count -> 今日原始计划项数
dashboard.review_selection.backlog_count -> 后续安排说明
dashboard.review_selection.today_feedback_count -> 今日已完成数

proposal.knowledge_points[].kind -> 分类标签
proposal.knowledge_points[].existing_knowledge_id -> 关联说明/取消关联
confirm.updated_reviews -> 确认成功后的刷新依据
```

## 6. 不采用

| 方案 | 原因 |
|---|---|
| 把所有到期项继续显示在 Today | 违背稳定分钟预算，复习压力随历史增长 |
| 让家长逐项选择 new/review/history | 增加产品复杂度；家长只需核对和确认 |
| 完成一项马上补一项 | 当日集合漂移，形成无尽任务感 |
| 隐藏历史到期数量 | 家长无法理解为什么后续仍有安排 |
| 用红色“积压告警” | 制造压力，且积压不是用户错误 |
| 客户端计算下一复习日 | 复制确定性领域规则，容易与服务端漂移 |

## 7. 实现与发布门禁

实现前需明确批准：

`SPEC-UNIFIED-REVIEW-20260913-04 + DREV-20260913-UNIFIED-REVIEW-01`

批准对象是本目录的两份可编辑 SVG、approval manifest 中的六张精确视口候选图及其 SHA-256。
仓库预览不免除前端自动测试、三视口原生节点几何、真实 AppID 预览、iOS/Android 体验和微信平台人工发布门禁。
