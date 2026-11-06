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
toolchain/policy changes even without a new visible design.


For user-visible frontend changes, read
`docs/design/frontend/FRONTEND-DESIGN.md` and
`docs/design/frontend/ui/`, then follow the repository-native design evidence gate. The style
consistency, target-user/platform interaction conventions, and supported
resolution matrix must be approved before prototyping. The user must approve
Task Spec revision + Design Revision before frontend implementation. Persist the
repository-local editable SVG/self-contained HTML source, required viewport/state
exports and matching immutable SHA-256 approval manifest; a source path alone is not approval.


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
- for frontend impact: current style/interaction/resolution baseline, editable SVG/HTML
  design sources, required UI states/viewports, code component mapping, and visual/a11y evidence.
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
- for `Frontend impact: yes`, the approved baseline revision, UI-ID, editable SVG/HTML
  source paths and SHA-256, proposed Design Revision, viewport/state exports, approval
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

Frontend implementation planning starts only after the repository-native design evidence gate is approved.
Frontend engineering planning also maps each changed/risk-relevant quality
contract to a test point, command/environment, budget, retained report, and Owner.

Plan by visible user outcome/state/viewport, not by vague “frontend” phases.


### Gate E — Implementation

实施循环（Work → Right → Practice；仅在批准后执行）：

```text
选择一个可验证切片，确认数据形状、领域术语、不变量和验收
→ 新行为/Bugfix：先写行为测试并观察预期失败（Red）
  纯重构/迁移：先运行现有/characterization 行为基线（Baseline）
→ 最小必要修改现有权威路径，验证目标行为成立（Green）
→ 在批准范围内小步重构、迁移调用者、删除被替代路径（Refactor）
→ 重跑行为测试及适用 focused/static 验证，检查 Diff
→ 记录 Spec/Handoff/Evidence 后再推进依赖它的下一片
```

- Red 必须来自预期行为差异，语法错误、依赖缺失或坏夹具不算 Red；新功能可先
  建立最小可运行接口再证明行为缺失。先排除环境错误，不靠随机补丁变绿。
- 纯重构/迁移不故意破坏代码制造 Red；未知历史行为先在旧实现上运行
  characterization test，疑似 Bug 单独记录，不静默固化。
- 无法写诚实自动测试时，记录 N/A/not run 的具体原因、替代可失败验证、Owner、
  范围和剩余风险；重大缺口仍阻断相应验收/发布并交 Owner 决定。低影响文档、
  机械变更选择链接/哈希/结构等适用验证，不为形式添加逐字镜像测试。
- 保留各阶段命令、对象版本、预期与实际原因、失败/重试和结果。新 EVD 使用
  `specs/evidence/EVIDENCE-TEMPLATE.md`，历史证据保留原路径；版本变化需新证据，
  旧结论不追认新实现。工具范围和预算以测试策略为准。
- 每片完成时可构建、可测试、可回退。计划内 Red/调用者迁移中的暂时不通过
  只限可撤销局部，需恢复步骤、检查点和退出条件；不扩散到共享环境，不以
  完成结果提交，不放宽迁移/发布门禁。
- Refactor 仅处理必要结构改进；代码已清楚且局部时写 `N/A: 无必要重构` 并复验，
  不为阶段名制造改动。

如果实际代码暴露出 Spec 错误：

1. 停止扩大补丁；
2. 记录新事实；
3. 回退到 Gate C；
4. 重新批准受影响部分；
5. 再继续实现。

禁止为了让实现通过而静默弱化验收标准。

Frontend code must stay within approved Design Revision/Spec scope. A material change to
layout, flow, copy meaning, state, accessibility semantics, or responsive
behavior returns to Gate C/repository-native design approval, creates a new Design Revision, and requires
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

Review 规则以根 [REVIEW.md](../../REVIEW.md) 为准，任务报告继续使用
`specs/_templates/REVIEW-REPORT.md`。Reviewer 只读，先独立读 Spec、Diff、
调用上下文和相关历史 ISS/REG，再核对实现者解释与真实自验输出。

R2/R3 至少进行：

- Spec/行为 Review；
- 相关文档有效性、正确性、一致性及可追溯性 Review（含 diff 外受影响文档）；
- 正确性与安全 Review；
- 测试有效性 Review；
- 删除/重复路径 Review。

Review 发现需求缺陷时，返回 Spec Gate；发现实现缺陷时，返回 Implementation Gate。

所有 Review 都检查正确性、设计合理性、逐文件修改必要性、放置位置和冗余；
按根 REVIEW 的稳定 finding ID、默认三轮上限、增量复审和去重规则收敛。
发现是否解决以对应版本验证为据，不以“已改代码”或评论数量判断。

有多种合理语义而证据无法确定时，Reviewer 输出原/新提交、Spec revision、提交人、
契约、证据及推荐统一方案，协调者用文档歧义 ISS 模板在当前会话请人工裁决。
只暂停依赖该决定的部分；答复明确批准具体范围后复用授权，应用到代码/文档，
绑定版本复验并复审。答复本身不关闭问题；超出原范围回 Gate C。

### Gate H — Closure

2026-10-26用户批准的开发完成口径：对应实现已由匹配源码版本的云端后端正常部署，或小程序开发版本成功上传，即可将相应Spec标为`DONE`并移至`specs/completed/`；两端范围分别核对，旧交付不覆盖后续本地增量。`DONE`表示开发完成，验收和发布阶段分别记载。真机/真实业务/内容/可访问性/Review缺项保留原结果及后续条件，不把NOT_RUN/PARTIAL/FAIL改为PASS，也不追认缺失批准。此规则只改变已交付任务的开发归档口径，未来发布的必需检查与人工门禁继续执行。见[治理Spec](../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。

Frontend closure additionally:
Engineering closure additionally records actual state/form/a11y/i18n/browser/
performance/security/privacy/data-viz/observability evidence, not merely a
filled checklist, and merges final facts/deviations into UI current state.


- semantically merges final facts into each affected UI current-state document;
- updates the frontend index when a global fact changed;
- records editable design source, Design Revision, SHA-256 approval snapshot, release/commit, and verification;
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
7. Review Feature 文档能否独立回答“这个 Feature 现在是什么样子”；同时核对其他
   受影响文档及文档歧义 ISS 的答复、应用版本和复审证据；
8. 新架构决定形成 ADR；
9. 遗留项进入明确的后续任务，不写模糊 TODO；
10. 将 Spec 归档到 `completed/`。

开发状态、验收和发布继续分别记录；已交付的开发归档不把未修复发现写成通过，
也不追认缺失批准。相关 ISS 按真实修复、回归和适用上线观察独立关闭；缓解不等于
永久修复。本次及后续纯治理文档任务按其获批 Spec 的完成条件处理，不能据此豁免
产品云交付或发布门禁。

## 5. Context handoff

长任务不得依赖聊天窗口保持记忆。以下情况更新 `HANDOFF.md`：

- 会话结束；
- 切换实现者；
- 完成一个重要切片；
- 发现 Spec 偏差；
- 验证失败但暂时无法修复。

Handoff 只记录恢复工作所需的当前状态，不复制整份 Spec。记录目标、决定、
动作/理由/版本/结果及证据索引；大日志按路径引用，敏感内容脱敏，不复制聊天。
已有提交授权时可采用小型有序提交说明 why/what/how verified；推送、合并、
发布与 worktree 清理仍需各自适用授权，不默认推主线或删除工作区。

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

### Attack the shared premise

两次修复共享同一前提且都未通过同一门禁时，停止第三次补丁：

1. 用一句话写出共同前提和支持/反驳证据。
2. 列出 actor、状态、权威路径和逻辑写入者，核对是否错误共享、责任重复或
   要求了不可能的不变量；对照架构约束 ARC-017/018。
3. 先验证前提；若不成立，推荐正确的状态/责任分配，不先追加 guard、锁、retry
   或旁路。权限和领域义务不能未经批准移除。
4. 记录可证伪实验；改变 Spec/架构/验收则先回批准门禁。

不共享同一前提时，同一问题连续三次仍无进展也停止补丁，重新检查假设、调用链
和证据。两个条件同时适用，取先触发者。

### Preserve failures for regression

需跟踪的人工/AI 有效发现、验收失败和线上问题进入 `docs/quality/issues/`，
记录因果链、应拦截层及漏检原因，关联修复 Spec、REG、真实测试和版本化 EVD。
紧急线上问题先按已有授权止损再补档；无法复现不宣称已修复。重复/高影响问题
优先改进类型、测试、Lint 或边界；回放命令及实际接入状态进入测试策略。

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

实现时按 Gate E 的 Red/Baseline 分支修改现有权威路径，必要重构后复验。
重复失败先查共同前提；不创建平行路径。完成后运行 Spec/测试策略规定的验证，
回填阶段命令、对象版本和证据，并报告删除了什么、未验证什么、剩余风险是什么。
```

独立 Review 请求：

```text
请以独立 Reviewer 身份审查 <commit/diff>，不要修改代码。
先读 Spec 和仓库规则，再检查行为对齐、回归、权限/数据/并发/错误、
旧路径残留、测试有效性、部署与回滚。
只报告有证据的问题，按 BLOCKER/MAJOR/MINOR/NOTE 分级，
每条包含位置、触发场景、影响和建议验证方法。
```
