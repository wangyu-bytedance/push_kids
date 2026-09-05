# AI-Assisted Development Protocol

## 1. Purpose

本协议规定一次 AI 辅助变更如何从模糊请求变成可验证的软件变更。它适用于人类与 Coding Agent 协作，不依赖某一个模型或工具。

核心原则：

```text
先理解，再设计；
先定义正确，再实现；
先替换旧路径，再增加新路径；
用证据验收，不由实现者自行宣布正确；
把稳定知识写回仓库，把临时对话留在任务记录。
```

## 2. Roles

一人可承担多个角色，但在高风险变更中应尽量分离：

| 角色 | 责任 | 不应独自决定 |
|---|---|---|
| Requester | 描述问题、价值、优先级 | 技术实现已正确 |
| Spec Owner | 收敛范围、非目标、验收 | 未经授权扩大业务范围 |
| Implementer | 按批准的 Spec 实现 | 修改验收来适配自己的代码 |
| Reviewer | 找回归、风险和偏差 | 在 Review 时偷偷重写需求 |
| Verifier | 执行验收并保留证据 | 仅凭代码阅读宣布通过 |
| Maintainer | 清理过期知识和重复规则 | 静默删除仍有效的决策 |

R2/R3 任务中，Implementer 与 Reviewer/Verifier SHOULD 具有独立上下文。可以是不同的人，也可以是新会话中的独立 Agent，但后者仍需人工处理业务判断。

## 3. Change classification

### R0 — Mechanical

满足全部条件：

- 无运行时行为变化；
- 不改变公共接口、数据、配置或依赖；
- 可由自动工具验证。

示例：格式化、拼写、确定性的生成文件刷新。

### R1 — Local reversible

- 行为变化局限于一个模块；
- 没有持久化或跨服务影响；
- 回退简单；
- 已有契约清楚。

需要 Spec Lite。

### R2 — Boundary change

任一命中：

- 跨模块或跨服务；
- 修改 API、事件、Schema、数据库、缓存、异步任务；
- 修改权限、租户范围、事务或并发语义；
- 需要兼容或迁移。

需要完整 Spec、计划批准、集成测试和独立 Review。

### R3 — Critical

任一命中：

- 身份认证、授权、安全边界；
- 金钱、结算、计量；
- 数据删除、不可逆迁移；
- 对外公共协议；
- 合规、隐私、生产基础设施；
- 故障可能造成高影响。

需要完整 Spec、ADR、威胁/失败分析、回滚或恢复、E2E、人工批准和发布观察。

## 4. Workflow and gates

### Mandatory requirement rule

Any user request that changes behavior, APIs, data, architecture, tests, or
documentation facts MUST go through Discovery and Spec approval before
implementation, including R1 changes. R0 is exempt only when it is purely
mechanical and changes none of those facts.

The selected Spec MUST include relevant link/call graph, sequence diagram, state
machine, architecture diagram, trade-offs, expected file changes, and required
test points. Mark non-applicable views `N/A` with reasons. Ask the user to
confirm the concrete Spec revision; a generated draft is not approval.

For initial project coding or architecture-changing tasks, also confirm the
purpose/domain module split, file/component decomposition, shared abstraction
ownership, acyclic dependency graph, architecture rationale, and
open/closed/deferred extension policy. If the user has not supplied a technical
design, propose a recommended design with alternatives and trade-offs, then
wait for confirmation rather than silently selecting it.

Before writing the task Spec, resolve the affected Feature ID(s) and read
`docs/domain/features/` as the Feature current-state layer. Existing Features
without a document require a baseline document backed by code/tests/runtime.
Every task Spec records the Feature baseline revision and merge plan.
Before any frontend implementation, verify
`docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md` is approved and
matches the frontend scope. Classify visible `Frontend impact` separately from
`Frontend engineering impact`. The latter includes frontend code/quality/
toolchain/policy changes even without a new Figma design.


For user-visible frontend changes, read
`docs/design/frontend/FRONTEND-DESIGN.md` and
`docs/design/frontend/ui/`, then follow the Figma design gate. The style
consistency, target-user/platform interaction conventions, and supported
resolution matrix must be approved before prototyping. The user must approve
Task Spec revision + Design Revision + node-specific Figma targets before
frontend implementation. Persist an approval snapshot; a file URL alone is not
approval.


### Gate A — Intake

输入：

- 原始请求；
- 业务/用户问题；
- 期望结果和紧迫性。

产出：

- 任务标题；
- 风险级别；
- 初步范围；
- 使用哪个 Spec 模板；
- 是否允许立即实现。
- Frontend impact yes/no and reason;
- Frontend engineering impact yes/no and reason;
- approved FEC revision, affected quality dimensions/budgets, and exceptions;

- affected UI ID(s), current Design Revision, and baseline readiness when relevant.


失败条件：

- 请求只是解决方案，没有问题描述；
- 不知道谁会受到行为变化影响；
- 无法判断是否涉及关键边界。

### Gate B — Discovery

Agent 必须建立影响地图：

```text
入口
→ 调用链
→ 核心规则
→ 数据/状态
→ 外部副作用
→ 现有测试
→ 可观测信号
→ 回滚/恢复
```

Discovery 输出至少包括：

- 当前行为及证据；
- 目标行为；
- 必须保持的不变量；
- 相关文件/模块；
- 现有扩展点；
- 旧逻辑候选；
- 未知项；
- 风险升级建议。
- for frontend impact: current style/interaction/resolution baseline, Figma
  nodes, required UI states/viewports, code component mapping, and visual/a11y evidence.
- for frontend engineering impact: component/state/form boundaries, complete
  states, a11y/i18n/browser/performance/security/privacy/data-viz/motion/media/
  AI/observability facts, test commands, reports, and current deviations.



不得仅搜索同名函数后立刻修改。

### Gate C — Spec

Spec 把任务从“让 AI 猜测”变成“让 AI执行”。Spec Owner 必须区分：

- **事实**：代码、测试、运行时或已批准文档支持；
- **决定**：已经明确选择；
- **假设**：为推进暂时采用，需验证；
- **待决问题**：不同答案会改变实现或验收。

Spec 通过条件：

- 当前和目标行为可比较；
- 范围与非目标明确；
- 每个关键状态/错误/权限有语义；
- 所需 link/call graph、sequence diagram、state machine、architecture
  diagram 和 trade-offs 已填写，或明确标记 N/A 和理由；
- 预期修改、新增、移动和删除的文件明确；
- required test points 与验收标准、测试层级和命令/Case 可追踪；
- 删除和兼容策略明确；
- 验收标准可观察；
- R2/R3 的发布和回滚明确；
- 没有 Blocker 级待决问题。
- for `Frontend impact: yes`, the approved baseline revision, UI-ID, Figma
  file/node URLs, proposed Design Revision, viewport/state exports, approval
  snapshot path, and explicit design approval are complete.
- for `Frontend engineering impact: yes`, the approved FEC revision, quality
  dimensions/rule IDs/budgets, verification plan, and approved deviations are complete.



### Gate D — Plan

计划必须是“可以逐步验证的变更序列”，而不是文件清单。

每一步应包含：

```text
Step:
Intent:
Files/boundaries:
Modification:
Deletion/replacement:
Validation:
Failure/rollback:
```

先实施最能验证核心假设的切片。数据库、公共接口和不可逆动作尽量延后，直到前置假设被验证。

Frontend implementation planning starts only after the Figma gate is approved.
Frontend engineering planning also maps each changed/risk-relevant quality
contract to a test point, command/environment, budget, retained report, and Owner.

Plan by visible user outcome/state/viewport, not by vague “frontend” phases.


### Gate E — Implementation

实施循环：

```text
选择一个切片
→ 修改现有路径
→ 删除被替代路径
→ 写/改测试
→ 运行聚焦验证
→ 检查 Diff
→ 更新 Spec 进度
```

如果实际代码暴露出 Spec 错误：

1. 停止扩大补丁；
2. 记录新事实；
3. 回退到 Gate C；
4. 重新批准受影响部分；
5. 再继续实现。

禁止为了让实现通过而静默弱化验收标准。

Frontend code must stay within approved Figma/Spec scope. A material change to
layout, flow, copy meaning, state, accessibility semantics, or responsive
behavior returns to Gate C/Figma, creates a new Design Revision, and requires
approval again.


### Gate F — Verification

验证层级按风险选择：

| 层级 | 证明什么 |
|---|---|
| Static | 格式、类型、依赖或架构规则 |
| Unit | 纯规则与局部边界 |
| Integration | 模块、数据库、队列、权限、事务 |
| Contract | 调用双方对协议的理解一致 |
| E2E | 用户从真实入口完成关键旅程 |
| Operational | 部署、迁移、回滚、指标和告警有效 |

验证记录必须包含：

- Spec required test point ID；
- 完整命令；
- 环境与版本；
- 结果摘要；
- 失败和重试；
- 证据位置；
- 未验证内容及原因。

Every required test point must be executed. A skipped/not-run point records its
reason, impact, and residual risk.

For frontend impact, verification also covers every affected supported
viewport, loading/empty/error/success/disabled/unauthorized states, keyboard and
focus, semantics/contrast/screen reader/reduced motion, and visual comparison or
regression evidence. Record unsupported or manually verified cases explicitly.

### Gate G — Independent review

Review 使用 `specs/_templates/REVIEW-REPORT.md`。Reviewer 先读 Spec 和 Diff，再读实现细节，避免被实现者的解释锚定。

R2/R3 至少进行：

- Spec/行为 Review；
- 正确性与安全 Review；
- 测试有效性 Review；
- 删除/重复路径 Review。

Review 发现需求缺陷时，返回 Spec Gate；发现实现缺陷时，返回 Implementation Gate。

### Gate H — Closure

Frontend closure additionally:
Engineering closure additionally records actual state/form/a11y/i18n/browser/
performance/security/privacy/data-viz/observability evidence, not merely a
filled checklist, and merges final facts/deviations into UI current state.


- semantically merges final facts into each affected UI current-state document;
- updates the frontend index when a global fact changed;
- records Figma node, Design Revision, approval snapshot, release/commit, and verification;
- removes replaced UI/CSS/flags or records an owned, expiring exit plan.


关闭任务前：

1. 更新 Spec 为 `DONE`；
2. 写最终行为摘要；
3. 写被删除/替换的行为；
4. 记录验证和 Review；
5. 将验证后的最终状态合并到每个受影响的
   `docs/domain/features/<FEAT-ID>-*.md`：更新正文、删除被替代描述、追加
   Spec/ADR/Release/Commit/Evidence 引用；
6. 更新 Behavior Catalog、Architecture、接口和其他事实面文档；
7. Review Feature 文档能否独立回答“这个 Feature 现在是什么样子”；
8. 新架构决定形成 ADR；
9. 遗留项进入明确的后续任务，不写模糊 TODO；
10. 将 Spec 归档到 `completed/`。

## 5. Context handoff

长任务不得依赖聊天窗口保持记忆。以下情况更新 `HANDOFF.md`：

- 会话结束；
- 切换实现者；
- 完成一个重要切片；
- 发现 Spec 偏差；
- 验证失败但暂时无法修复。

Handoff 只记录恢复工作所需的当前状态，不复制整份 Spec。

## 6. Change budget

默认 SHOULD 控制：

- 一个任务只解决一个用户/系统结果；
- 一次变更不同时引入多个新基础设施概念；
- 大规模重命名、格式化与行为修改分开；
- 如果 Diff 超出 Reviewer 能建立完整心智模型的范围，拆分；
- 如果新增代码远大于删除/修改且任务本质是“改变现有行为”，必须再次检查是否出现平行实现。

行数不是质量目标，但异常增量是架构失控的诊断信号。

## 7. Test design separation

理想顺序：

1. Spec Owner 定义验收行为；
2. Verifier 设计关键验收 Case；
3. Implementer 根据已确定的 Case 实现；
4. Implementer 增加必要的单元/集成测试；
5. Reviewer 检查测试是否会在错误实现下失败；
6. Verifier 执行最终 Case。

小型任务允许角色合并，但仍应先定义验收、后写实现。

## 8. Failure policy

遇到失败时禁止反复随机修改。使用以下分类：

| 类型 | 处理 |
|---|---|
| Spec 缺陷 | 回到 Spec，重新决定 |
| 代码缺陷 | 最小修复并增加回归证据 |
| 测试缺陷 | 修复测试；说明为何旧测试无效 |
| 环境缺陷 | 记录环境证据，不误判代码 |
| 依赖/外部服务 | 明确降级、重试或阻塞 |
| 历史行为未知 | 先写 characterization test |
| 架构不支持 | 提 ADR/重构任务，不堆旁路 |

同一问题连续尝试三次仍无进展时，停止补丁，重新检查假设、调用链和证据。

## 9. Prompting pattern

给 Agent 的任务请求 SHOULD 引用仓库内 Spec，而不是重新在聊天中复制并改变需求：

```text
请实现 specs/active/<task>/SPEC.md 中已批准的范围。

先阅读 AGENTS.md、目标目录局部说明，以及 Spec 引用的架构/领域文档。
在改代码前：
1. 复述当前行为、目标行为、不变量和非目标；
2. 给出影响地图和删除/替换清单；
3. 给出按垂直切片拆分的计划；
4. 若发现 Spec 与代码冲突，停止并报告，不要自行扩大设计。

实现时优先修改现有逻辑，不创建平行路径。完成后运行 Spec 规定的验证，
回填命令和证据，并报告删除了什么、未验证什么、剩余风险是什么。
```

独立 Review 请求：

```text
请以独立 Reviewer 身份审查 <commit/diff>，不要修改代码。
先读 Spec 和仓库规则，再检查行为对齐、回归、权限/数据/并发/错误、
旧路径残留、测试有效性、部署与回滚。
只报告有证据的问题，按 BLOCKER/MAJOR/MINOR/NOTE 分级，
每条包含位置、触发场景、影响和建议验证方法。
```
