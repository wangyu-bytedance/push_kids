# Feature Current-State Directory

本地新增当前能力：[FEAT-004两日无新增的单项学习建议](FEAT-004-daily-learning-suggestions.md)，Spec04/DREV01已批准并实现，建议弹层按另批Spec01/DREV02精简，今日卡片按Visibility Spec01/DREV03隐藏空区并统一风格（revision06-LOCAL）；默认关闭、VERIFYING。[FEAT-001](FEAT-001-push-kids-mvp.md)同步空白日少量提前复习。自动化和缺口见[主功能证据](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)、[弹层证据](../../quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)及[卡片证据](../../quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)，不代表已发布。

## Purpose

新增本地实现：[FEAT-013 — 学年升年级建议与家长共享确认](FEAT-013-annual-grade-promotion.md)，`LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED`；[Spec02](../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md)及Architecture02/DREV01已获用户批准，当前弹窗由另批[精简Spec01/DREV02](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)收敛为单标题/选择与并排操作。建议与正式级隔离、孩子学年共享、独立串行弹窗和显式人工定级保持；[主任务证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)与[精简实施证据](../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)分别记录采集时事实，真实设备、原生端到端和可访问性待验，不代表已发布。

新增本地实现：[FEAT-012 — 孩子照片足迹](FEAT-012-child-photo-footprints.md)，`LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED`。Spec04/Architecture03实现导入、家长确认和三视图；2026-10-23按获批入口Spec01和文案Spec01新增记录Tab标题切换“学习记录 / 旅行日记”及提示精简。当前验证见[本轮证据](../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)，完整原生/真机、设计差异、真实全球底图、MySQL5.7及AI/选图素材评估仍待验收。

本地实现入口：[FEAT-011 — 提醒授权自动补充](FEAT-011-notification-auto-renewal.md)，`LOCAL_IMPLEMENTED / VERIFYING / NOT_RELEASED`。
Spec/架构/DREV已获批准；本人完成游标、逐类冷却、授权事件去重和前端已接入；真机与独立评审待补，线上未改变。

`docs/domain/features/` 是功能当前状态的权威入口，用于回答：

> 这个 Feature 截至当前版本，最终是什么样子？

它解决 Feature 长期演进后信息散落在 `FEATURE-SPEC.md`、
`BUGFIX-SPEC.md`、`SPEC-LITE.md`、`REFACTOR-SPEC.md` 和提交记录中的问题。

核心心智：

```text
Feature Current-State = 当前最终事实
Task Spec = 单次变更意图、设计、批准和验收
Behavior Catalog = 关键行为和不变量
ADR = 长期技术决定理由
```

## Knowledge model

| Source | Answers | Update model |
|---|---|---|
| Feature current-state document | 功能现在是什么样子 | 每次相关任务完成时合并为最新事实 |
| Behavior Catalog | 哪些关键行为和不变量不能被破坏 | 行为或证据变化时更新 |
| Task Spec | 这一次为什么改、批准了什么、如何验收 | 每个任务一份，完成后归档 |
| ADR | 长期技术决定为什么如此 | 决策变化时新增或 supersede |
| Code/tests/runtime | 实际实现和证据 | 随实现变化 |

Feature 文档不是所有历史 Spec 的拼接，也不是 Change Log。正文只描述当前
有效事实；被替代的描述必须被改写或删除。历史通过 Change References 链接到
Spec、ADR、Release/Commit 和验证证据。

## Layout

```text
docs/domain/features/
├── README.md
├── FEATURE-TEMPLATE.md
├── FEAT-001-<feature-slug>.md
└── FEAT-002-<feature-slug>.md
```

一个 Feature 使用稳定 ID：

```text
FEAT-001
FEAT-AUTH-001
FEAT-ORDER-CHECKOUT
```

优先沿用团队已有稳定 Feature/Epic/Capability ID。名称变化时保持 ID 不变，
在文档 Metadata 中增加 Alias。

## Feature boundary

Feature 是用户或外部系统可以理解的完整能力，例如：

- 用户登录与会话管理；
- 创建和履约订单；
- 报表导出；
- Webhook 投递；
- 管理员权限配置。

不要把以下内容单独当作 Feature：

- 一个 private helper；
- 单个数据库表；
- 单个页面组件；
- 内部 Repository；
- 纯技术依赖升级。

纯技术重构仍需关联它影响的 Feature；若确实不影响任何 Feature，写
`Feature IDs: N/A`，并说明它属于哪个 Architecture/Platform capability。

## Task workflow

### 1. Resolve Feature identity before the Spec

处理任何行为、API、数据、架构、测试或文档事实变化前：

1. 根据入口、用户任务、领域 Owner 和现有代码确定受影响 Feature。
2. 搜索 `docs/domain/features/` 的 ID、名称和 Alias。
3. 阅读对应 Feature 当前状态、Behavior、active/completed Specs 和 ADR。
4. 如果一个请求横跨多个 Feature，在 Spec 中分别列出。
5. 如果边界不清或可能创建新 Feature，提出推荐边界并请求确认。

禁止仅根据最近一份 Spec 推断当前功能。

### 2. Establish current state

- 已有 Feature 文档：以它为导航，并用代码、测试和运行时验证关键事实。
- 功能已存在但没有文档：在实现变更前建立 Baseline Feature 文档，标记证据
  和未知项。
- 全新 Feature：在 Feature Spec 中预留目标文档路径；只有实现和验收完成后，
  才把它写成 `CURRENT` 事实。

### 3. Link the task Spec

每份 Feature、Bugfix、Spec Lite、Refactor 或 Migration Spec 必须包含：

```text
Affected Feature IDs
Current-state Feature document paths
Current-state sections affected
Feature merge owner
Feature merge plan
```

### 4. Merge at closure

任务完成前：

1. 重新读取当前 Feature 文档，避免覆盖并行任务的新事实。
2. 根据已验证实现更新当前行为、流程、状态、接口、数据、权限、错误、
   架构映射、扩展策略和测试证据。
3. 替换或删除已被本次变更淘汰的旧描述；不要在正文末尾追加冲突补丁。
4. 保留仍有效的未改内容。
5. 更新 `Last verified`、Evidence baseline 和 Authoritative code/tests。
6. 在 Change References 追加一条紧凑引用。
7. 更新 Behavior Catalog 中受影响的行为和不变量。
8. Review Feature 文档是否能独立表达最终状态。

### 5. Add references, not duplicated history

Change References 推荐格式：

| Date | Change summary | Spec | ADR | Release/commit | Verification |
|---|---|---|---|---|---|
| `YYYY-MM-DD` | `[最终发生的变化]` | `[task Spec]` | `[ADR/N/A]` | `[release/SHA]` | `[evidence]` |

不要把整份 Spec、实现过程、聊天记录或废弃设计复制进 Feature 文档。

## Merge rules

- Feature 正文是 current-state snapshot，不是 append-only。
- Change References 是 append-only；错误引用可更正但不能静默丢失重要来源。
- 多个并行任务修改同一 Feature 时，后完成者必须基于最新文档重新合并。
- 一个任务修改多个 Feature 时，逐个更新，不创建混合 Feature 文档逃避边界。
- Feature 被拆分/合并/废弃时，保留原 ID 文档为 `SUPERSEDED` 或
  `DEPRECATED`，链接替代 Feature 和迁移条件。
- 文档、代码、测试冲突时停止关闭任务，记录冲突并确认权威事实。

## Retrieval order

了解一个 Feature 时按以下顺序：

1. Feature current-state document；
2. 关联 Behavior Catalog；
3. 当前 Architecture 和 ADR；
4. Authoritative code/tests；
5. Change References 指向的 Specs，用于追溯原因；
6. Runtime evidence。

不要按时间把所有 Specs 顺序阅读后自行拼接最终状态，除非正在审计 Feature
文档的完整性。

## Completion gate

涉及 Feature 的任务不能标记 `DONE`，除非：

- [ ] Feature ID 和当前状态文档已解析。
- [ ] 当前 Feature 正文已合并最终事实，而非追加冲突说明。
- [ ] 被替代内容已删除或明确标记 Deprecated。
- [ ] Change Reference 已加入。
- [ ] 关键 Behavior 和测试证据已同步。
- [ ] Feature 文档中的接口、状态、权限、数据和架构映射与实现一致。
- [ ] Reviewer 已检查 Feature current-state consistency。
