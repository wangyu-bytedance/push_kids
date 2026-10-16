# Specs Directory

## Purpose

Spec 是单次变更的权威意图与验收来源。它描述“为什么改、要变成什么、不允许改变什么、如何证明正确”，不替代当前架构和领域事实文档。

Feature 长期当前状态位于 `docs/domain/features/`。了解 Feature 最终状态时先读
Feature 文档；Spec 只用于追溯某一次变化的原因、设计、批准和证据。

FEAT-001 早期实现的历史变更记录为
`completed/FEAT-001-PUSH-KIDS-FINAL-SPEC.md`；当前事实以 Feature/UI 文档为准。HTML 评审阶段记录为
`completed/DESIGN-001-HTML-REDESIGN.md`，原型文件保留在
`docs/design/frontend/prototypes/DREV-20260830-03/index.html`，不参与运行。

## Layout

复习完成后科目跳序修复：[`BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01`](active/BUG-029-REVIEW-SUBJECT-ORDER.md)，`VERIFYING`；后端518项、前端244项、补充MySQL18项和冻结镜像门禁通过；灰度031 normal/0%流量，定向smoke与全量人工门禁待完成，见[发布记录](../docs/deploy/releases/20261016-review-subject-order-backend.md)。

历史设计脚本lint清理：[`SPEC-20261016-RELEASE-LINT-01`](completed/CHORE-20261016-RELEASE-LINT.md)，用户明确批准，`DONE`；5个脚本等价整理，新旧168个输出哈希相同，批准快照未变，全仓Ruff通过。

今日按钮与编辑计划分页统一：[`SPEC-20261014-ACTION-PAGER-CONSISTENCY-02`](active/FEAT-010-TODAY-ACTION-STYLE.md)，本地实现，VERIFYING；两项功能提交前联合核对见[`验证记录`](../docs/quality/evidence/TWO-FEATURE-PRECOMMIT-20261015.md)。

学科管理与移出入口统一：[`SPEC-20261014-SUBJECT-MANAGEMENT-01`](active/FEAT-001-SUBJECT-MANAGEMENT-CONSISTENCY.md)，本地实现，VERIFYING；当前事实见FEAT-001、UI-001及`docs/quality/evidence/SUBJECT-MANAGEMENT-20261015.md`，未上传或发布。

```text
specs/
├── _templates/
├── active/
├── completed/
└── rejected/
```

- `_templates/`：只存模板，不在模板内记录真实任务。
- `active/`：已批准或正在实现/验证的任务。
- `completed/`：已通过完成门禁的任务。
- `rejected/`：明确否决或取消且保留理由有价值的任务。

目录可在首次使用时创建。

## Template selection

| Situation | Template |
|---|---|
| R1 局部、可逆变更 | `SPEC-LITE.md` |
| 新增或改变用户/系统行为 | `FEATURE-SPEC.md` |
| 修复错误行为或数据问题 | `BUGFIX-SPEC.md` |
| 保持行为、改变结构 | `REFACTOR-SPEC.md` |
| 初始化或迁移 AI Native 目录与边界 | `AI-NATIVE-MIGRATION-SPEC.md` |
| 中断或切换实现者 | `HANDOFF.md` |
| 独立代码/变更评审 | `REVIEW-REPORT.md` |
| 周/月/季度治理巡检 | `MAINTENANCE-REPORT.md` |

如果一个任务同时包含重构和行为变化：

1. 优先拆成两个 Spec；
2. 不能拆时使用 Feature/Bugfix Spec；
3. 把“行为变化”和“结构整理”的验收分别写清；
4. 不要用“重构”掩盖未批准的行为变化。

## Mandatory requirement workflow

任何改变行为、API、数据、架构、测试或文档事实的请求都必须：

1. 解析受影响的 Feature ID 和 `docs/domain/features/` 当前状态文档；若现有
   Feature 没有文档，先建立有证据的 Baseline。
2. 在实现前澄清用户意图，并处理与 Feature 当前行为或架构约束的冲突。
3. 从 `_templates/` 创建匹配的 Spec，并记录 Feature baseline revision、
   受影响章节和完成后的合并计划。
4. 取得用户对具体 Spec revision 的明确确认。
5. 只实现已确认的范围。
6. 执行覆盖所有 required test points 的测试，并记录已执行、失败和跳过的检查。
7. 关闭任务前，把验证后的最终事实合并回每个受影响 Feature 文档，替换过期
   正文，并追加 Spec、ADR、Release/Commit 和 Evidence 引用。
8. 对用户可见前端变更，先确认 `FRONTEND-DESIGN.md` 中 style、interaction、
   resolution baseline 已批准，再生成/更新仓库内可编辑 SVG 或自包含 HTML 原型，记录 UI-ID、
   Design Revision、源文件与视口/状态导出的 SHA-256 manifest；用户确认具体 Spec + Design revision 后才能编码。
9. 前端关闭时把最终事实语义合并到 UI current-state，并添加设计源文件、snapshot、
   commit 和验证引用。


每份任务 Spec 必须在相关时包含以下设计视图；不适用时写 `N/A` 和理由，不得静默省略：

- link/call graph；
- sequence diagram；
- state machine；
- architecture diagram；
- trade-offs 与 rejected alternatives；
- 预期修改、新增、移动和删除的文件；
- 与验收标准对应的 required test points。

仅仅创建了 Spec 或由 Agent 生成了 Spec，不代表它已经获得批准。

当任务是项目初始化，或改变模块边界、共性抽象、依赖方向、扩展点时，
Spec 还必须包含：

- 按目的/领域进行的模块划分和 Owner；
- 文件/组件职责及拆分理由，避免 God file；
- 共性代码抽取或暂不抽取的理由、Owner 和 Contract；
- 模块/Package 依赖 DAG 及循环依赖检测；
- 架构选择理由、备选方案、Trade-offs 和重审条件；
- open/closed/deferred 扩展轴；
- 每个 open 扩展点的兼容、隔离、资源、安全、观测和测试要求；
- 用户或架构 Owner 对 Architecture revision 的确认。

## Frontend design gate

All task templates include a `Frontend Design Impact and Repository-native Approval`
section. `Frontend impact: yes` requires:

- approved project frontend baseline revision;
- approved project frontend engineering constraint revision;
- affected frontend quality dimensions and rule/budget IDs;
- verification plan, retained evidence, and approved deviations;

- affected UI-ID(s) and UI current-state document(s);
- repository-local editable SVG or self-contained HTML design source and SHA-256;
- proposed and approved Design Revision;
- required state/viewport exports;
- explicit approval of Task Spec revision + Design Revision;
- immutable approval snapshot manifest;
- UI current-state merge owner and verification plan.

`Frontend impact: no` requires a reason. A frontend implementation-only change may have `Frontend impact: no` while
still affecting engineering quality; it must cite the FEC revision and select
quality dimensions when component/state/form, accessibility, browser,
performance, security/privacy, data-viz, observability, or similar facts change. A pure internal refactor or restoration
to a still-valid approved design may reuse that Design Revision. Required viewport/state
exports must match the immutable SHA-256 approval manifest. Native Mini Program
geometry and three-viewport/device evidence remain required under the FEC and test policy.
External design tools, node URLs and tool-availability waivers are not required.

## Naming

Recommended:

```text
specs/active/<YYYY-MM-DD>-<task-id>-<short-slug>/SPEC.md
specs/active/<YYYY-MM-DD>-<task-id>-<short-slug>/HANDOFF.md
specs/active/<YYYY-MM-DD>-<task-id>-<short-slug>/REVIEW.md
```

Example:

```text
specs/active/2026-08-17-AUTH-142-resource-authorization/SPEC.md
```

稳定 ID 应来自现有 issue/task 系统；没有时使用仓库内唯一短 ID。

## Lifecycle rules

1. `DRAFT`：设计中；凡受 Mandatory requirement workflow 约束的变更均不允许实现。
2. `READY_FOR_REVIEW`：完整但未批准。
3. `APPROVED`：批准人和日期已记录。
4. `IMPLEMENTING`：仅实现批准范围。
5. `VERIFYING`：冻结范围，执行验收和修复。
6. `DONE`：完成门禁通过，移到 `completed/`。
7. `BLOCKED`：记录阻碍、Owner 和恢复条件。
8. `CANCELLED/REJECTED`：记录原因；有长期价值时移到 `rejected/`。

## Change control

- 上游产品/架构决定改变时，更新同一份 Spec 并记录 revision。
- 实现中发现新事实时，不静默扩展范围。
- 验收标准在实现前确定；实现者不能为适配代码而自行弱化。
- Feature 文档在任务开始时提供当前基线，在任务关闭时吸收最终状态；不要把
  多份历史 Spec 当作当前状态的替代品。
- Feature 正文是可重写的 current-state snapshot；Change References 保存历史。
- 仅过程性对话不写入 Spec；只保留影响恢复、决策或验收的内容。
- 完成后保留最终行为、关键决策和证据；删除过期 Handoff 临时信息。

## Minimal approval record

所有受 Mandatory requirement workflow 约束的变更必须包含：

```text
Approved scope:
Approved by:
Approval date:
Spec revision:
Known accepted risks:
```

聊天中的“可以”“继续”只有能明确映射到某一 Spec revision 时才算批准。
