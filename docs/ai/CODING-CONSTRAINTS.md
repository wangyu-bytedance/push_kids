# Coding Constraints for AI-Assisted Changes

> 这些约束关注 AI 常见的维护性风险。语言/框架特定规则应由 Lint、类型系统和模块级说明补充。

## 1. Priority order

发生取舍时按以下优先级：

1. 正确性与数据/安全不变量；
2. 已批准的外部行为和兼容性；
3. 失败可恢复、可观察；
4. 单一事实源与架构边界；
5. 可测试、可读、可维护；
6. 性能预算；
7. 实现简洁与交付速度。

“改动最少”不能凌驾于正确性；“更通用”不能凌驾于当前需求。

## 2. Modify before adding

AI 在新建文件/函数/类型/开关前 MUST 回答：

- 当前行为在哪里实现？
- 现有扩展点为什么不足？
- 新实现将替换什么？
- 旧实现何时删除？
- 是否形成第二个事实源？

默认做法：

```text
定位现有权威路径
→ 修改它
→ 迁移调用者
→ 删除旧逻辑
→ 搜索残留引用
→ 用测试证明只有一个行为
```

禁止：

- 为绕过难以理解的旧代码新建 `*V2`、`new*`、`legacy*` 并长期共存；
- 同一规则在 UI、Controller、Service、Job 分别实现；
- 新增 Feature Flag 而没有 Owner 和删除条件；
- 用兼容包装层隐藏语义不一致；
- 保留注释掉的旧代码。

## 3. Functions and modules

MUST:

- 一个函数/模块有一个可描述的责任；
- 名称表达领域意图，不只是实现机制；
- 输入、输出、错误和副作用清楚；
- 依赖通过现有边界传入或获取，避免隐式全局状态；
- 在可信边界校验输入；
- 把核心规则与 I/O 编排分开；
- 保持调用方向符合架构约束。

SHOULD:

- 在产生结果的最近位置处理错误语义；
- 使用早返回减少嵌套，但不打散事务/资源清理；
- 选择最小可用接口；
- 对状态转换使用显式命令/方法而非任意字段修改；
- 对复杂分支使用决策表或策略，而不是继续追加布尔条件。

MUST NOT:

- 捕获异常后静默继续；
- 用 `boolean`/`null` 表示多个含义而不建模；
- 从低层基础设施反向调用 UI/业务编排；
- 在读取函数中隐藏写入或网络副作用；
- 以“helper/utils/common”作为无边界逻辑堆放区。

## 4. Data and state

- 对象/记录的所有者和生命周期 MUST 明确。
- 无效状态 SHOULD 尽量通过类型、Schema 或构造约束变得不可表示。
- 状态转换 MUST 校验当前状态和调用者权限。
- 金额、时间、时区、单位、精度、排序和空值语义 MUST 显式。
- 持久化写入 MUST 说明事务边界和并发策略。
- 缓存默认不是事实源；失效和一致性 MUST 设计。
- 删除操作 MUST 区分软删、硬删、归档、保留和恢复。
- 数据迁移脚本 MUST 可观测、可重入或明确一次性约束，并有恢复策略。

禁止：

- 用字符串散落表示状态；
- 读改写而无版本/锁/原子操作，导致 lost update；
- 在多个表/服务复制同一业务事实而无同步协议；
- 修改 Schema 但遗漏旧版本代码和已有数据。

## 5. Errors and control flow

每个失败必须属于可行动类别：

- 输入无效；
- 未认证；
- 无权限；
- 资源不存在；
- 状态冲突/并发冲突；
- 限流/配额；
- 可重试依赖失败；
- 终止性依赖失败；
- 内部缺陷。

MUST:

- 保留可诊断原因和 correlation/request ID；
- 向用户/调用者返回稳定且不泄密的错误；
- 只重试明确可重试且幂等安全的操作；
- 失败时不产生禁止的部分副作用；
- 清理资源或使用语言原生结构保证清理。

MUST NOT:

- `catch (all) { return success }`；
- 对所有异常返回同一状态；
- 将敏感 payload、密钥、Token 或个人数据写入日志；
- 无边界重试或递归恢复。

## 6. APIs, events, and jobs

- 契约优先于实现细节。
- 输入限制、默认值、错误、分页、排序和版本 MUST 明确。
- 对重试请求定义幂等键/去重范围。
- Event 名称用已发生事实；Command 名称用意图。
- 消费者不得依赖未声明字段或事件顺序。
- 异步 Job MUST 有明确状态、超时、重试、取消和死信/人工恢复。
- Webhook/外部事件 MUST 验签、去重并验证时间窗口。

新增字段通常比改变字段含义安全；删除字段必须先证明消费者迁移完成。

## 7. Dependencies and configuration

新增生产依赖前必须记录：

- 当前需求；
- 为什么标准库/现有依赖不足；
- 维护活跃度、许可证、安全与体积/运行成本；
- 替代方案；
- 锁定版本和升级策略。

配置要求：

- 环境变量/配置项有 Owner、类型、默认值和缺失行为；
- Secret 只来自批准的 Secret 管理方式；
- 配置在启动时验证，避免流量中途失败；
- 删除废弃配置和文档；
- Feature Flag 有默认值、Owner、指标和删除日期。

## 8. Tests

每个测试应明确回答“什么错误会让它失败”。

MUST:

- 断言可观察结果和必要副作用；
- 对拒绝路径断言状态没有改变；
- Bugfix 回归测试在修复前失败（可行时）；
- 对权限/租户同时覆盖允许与拒绝；
- 对状态机覆盖非法转换；
- 对重试/幂等覆盖重复和并发；
- 保持数据独立且确定；
- 使用与风险相称的真实基础设施。

MUST NOT:

- 只断言 Mock 被调用而不验证结果；
- 使用与生产代码相同的 helper 计算期望值；
- 用大 Snapshot 隐藏关键语义；
- 用 `sleep` 猜测异步完成；
- 删除失败测试只为让 CI 变绿；
- 把重跑后成功当成稳定通过。

## 9. Comments and documentation

Comments SHOULD explain:

- 为什么直观方案不正确；
- 不变量、兼容性或外部限制；
- 临时方案的 Owner 和删除条件；
- 算法/协议来源。

Comments MUST NOT:

- 重复代码语法；
- 记录容易过期的任务进度；
- 用“temporary”但无任务/期限；
- 保留已删除代码的叙述。

公共行为变化同时更新：

- Spec；
- 测试；
- Behavior Catalog；
- API/Schema 文档；
- 必要 ADR/Runbook。

## 10. Security baseline

- 不信任用户、文件、Webhook、队列、外部 API 和模型输出。
- 服务端执行资源和租户授权。
- 使用参数化查询/安全编码/允许列表。
- 文件上传限制类型、大小、名称、存储与扫描。
- 网络访问限制目标、协议、重定向和私网范围，防 SSRF。
- 破坏性/高权限动作要求明确确认、审计和最小权限。
- Secret 不进入代码、测试夹具、日志或错误响应。
- 依赖更新不绕过锁文件和安全检查。

## 11. Performance and resource controls

- 先有预算/证据再优化。
- 避免无界查询、循环网络请求、N+1、无界并发和全量内存加载。
- 列表 API 有分页和上限。
- 队列/批处理有批次、背压和终止条件。
- 大对象/文件使用流式处理（适用时）。
- 性能变化有基线、相同条件和可复现测量。

不要用缓存掩盖错误的数据所有权或低效边界设计。

## 12. Refactoring

重构完成必须减少至少一种成本：

- 重复事实；
- 概念数量；
- 改动扩散；
- 循环/非法依赖；
- 不可测试 I/O；
- 复杂分支；
- 运行时开销。

如果只是把旧代码包进新接口但旧接口仍被广泛使用，重构尚未完成。

重构与行为变更 SHOULD 分开。无法分开时使用 Feature/Bugfix Spec 并明确行为差异。

## 13. Final diff audit

提交前检查：

1. 是否有任务范围之外的文件？
2. 是否新增了可以修改现有逻辑完成的平行实现？
3. 旧函数、分支、Flag、配置、导出、测试和文档是否删除？
4. 是否出现新的 `TODO/FIXME/temporary/legacy/V2`？
5. 公共契约、数据和权限变化是否批准？
6. 测试能否对错误实现失败？
7. 错误和失败是否可观察、可恢复？
8. 是否泄露 Secret/PII？
9. 文档是否描述最终事实而非过程猜测？
10. 验证命令和结果是否真实记录？

## 14. Frontend implementation against approved design
The detailed authoritative frontend rules are in
`docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md`. Read its approved
revision before frontend work. A visual match does not prove correct state,
forms, accessibility, localization, browser behavior, performance, security,
data integrity, or observability.


- Do not implement a user-visible frontend before the approved Figma gate.
- Inherit the approved style consistency, interaction convention, and
  resolution baseline; do not introduce ad-hoc colors, spacing, typography,
  components, novel interaction patterns, or undocumented breakpoints.
- Implement every approved critical state, not only the happy screenshot:
  loading, empty, error, success, disabled, unauthorized, and recovery when applicable.
- Treat each claimed viewport as a contract. Verify reflow, truncation, scroll,
  navigation transformation, orientation, zoom/large text, and density rules.
- Preserve familiar target-platform behavior unless the approved design records
  a deliberate, user-benefiting deviation.
- Reuse Design System tokens/components when semantics match. Similar pixels do
  not alone justify a shared component; extracted UI abstractions still need a
  stable contract, Owner, consumers, and tests.
- Record Figma component ↔ code component mapping; use Code Connect when available.
- A material difference from the approved layout, flow, state, copy meaning,
  accessibility semantics, or responsive behavior requires a new Design Revision.
- Delete replaced component branches, CSS, pages, flags, stories, snapshots, and
  tests, or document the authoritative path and an owned removal condition.
- Keep remote, URL, form/draft, persisted preference, and ephemeral UI state
  distinct; derive rather than synchronize duplicate state.
- Preserve user input on recoverable form errors, prevent duplicate mutations,
  and model pending, cancellation, retry, idempotency, race, and rollback.
- Treat complete UI states, semantic HTML, keyboard/focus, accessible names,
  contrast/non-color cues, zoom/reflow, localization/RTL/formatting, browser
  support, and reduced motion as implementation contracts.
- Meet declared performance/resource budgets under comparable conditions;
  avoid unbounded DOM/data/listeners/requests/memory and unnecessary hydration.
- The client is untrusted: server authorization remains authoritative; sanitize
  untrusted content and keep secrets/PII out of bundles, URLs, storage, logs,
  analytics, screenshots, and errors.
- Tables/charts state units, aggregation, time, missing/stale data, honest scale,
  accessible alternatives, and tested transformations.
- Analytics/errors have stable schemas, privacy rules, deduplication, Owner, and
  release/correlation evidence; re-renders must not duplicate events.


## 15. Project-specific additions

项目可增加语言/框架规则，但 SHOULD 优先实现为：

- formatter/linter；
- compiler/type checker；
- Schema validator；
- architecture test；
- dependency rule；
- code generator；
- CI policy。

只有无法稳定自动化、且每次任务都需要 Agent 判断的规则，才加入 `AGENTS.md`。

## 16. WeChat Cloud Hosting constraints

修改微信小程序云调用、云身份、FastAPI 启动、异步任务、媒体存储或部署配置前，MUST 阅读
[`docs/operations/WECHAT-CLOUD-HOSTING.md`](../operations/WECHAT-CLOUD-HOSTING.md) 的“微信云托管必须遵守的平台边界”和“编写代码时的强制注意事项”。最低约束是：

- 小程序统一使用 `wx.cloud.init` + `wx.cloud.callContainer`，显式配置 env、path 和
  `X-WX-SERVICE`；图片走 `wx.cloud.uploadFile`。
- `X-WX-OPENID`、`X-WX-APPID`、`X-WX-ENV` 等身份只从关闭公网后的微信专用链路读取，客户端
  不得自报或伪造；后端仍需执行 AppID/env/binding/family-scope 校验。
- 服务监听平台 `PORT`，保持无状态，不回显或记录原始 Header、环境变量、凭证和儿童数据。
- 云托管请求返回后不保证继续分配 CPU。MUST NOT 在 lifespan 或请求作用域外依赖后台线程、进程、
  定时器或永久轮询协程完成业务；`minNum>0` 不是例外。
- 任一上述约束被破坏时，代码评审和上线门禁必须标记为阻断。
