# AI Coding Knowledge Maintenance Playbook

## 1. Purpose

AI 能快速追加规则、文档和抽象，也会快速制造信息熵。定期整理的目标不是生成更多总结，而是：

1. 删除失效指令；
2. 合并重复事实源；
3. 把稳定经验转为自动化控制；
4. 关闭临时兼容路径；
5. 校验文档与代码、测试、运行时的一致性；
6. 保证下一次 Agent 能在有限上下文内获得正确规则。

维护过程默认只产出报告和小型文档修正；大范围代码重构必须另开 Spec。

## 2. Cadence

| Cadence | Scope | Timebox | Owner | Output |
|---|---|---:|---|---|
| 每次任务结束 | 本次行为、证据、删除项、文档同步 | 5–15 min | Implementer | Spec closure |
| 每周 | active Spec、失败测试、临时 TODO/兼容层 | 30–60 min | Maintainer | Weekly report |
| 每月 | AGENTS、架构、行为目录、ADR、测试策略一致性 | 1–2 h | Tech lead/maintainer | Monthly audit |
| 每季度 | 架构漂移、依赖、关键 E2E、恢复演练、模板有效性 | 0.5–1 day | Team | Governance review |
| 事故后 | 失败控制、行为/测试/监控缺口 | 事故复盘内 | Incident owner | Prevention changes |

## 3. End-of-task maintenance

每个任务关闭时检查：

- [ ] Spec 的当前行为已变为最终行为；
- [ ] `BEHAVIOR-CATALOG.md` 更新了关键行为和证据；
- [ ] 每个受影响 Feature 的 `docs/domain/features/` 正文已合并最终状态，并
      添加本次 Spec/ADR/Release/Evidence 引用；
- [ ] 前端变更已将最终状态合并到 `docs/design/frontend/ui/`，并关联
      Figma node、Design Revision、批准 snapshot 和视觉/a11y/分辨率证据；

- [ ] 新的架构决定形成 ADR；
- [ ] 删除旧路径、旧测试、旧配置、旧文档；
- [ ] 未删除兼容层有 Owner、期限、移除条件；
- [ ] 验证命令和结果已记录；
- [ ] 未完成项不是裸 `TODO`，而是可跟踪任务；
- [ ] Handoff 已删除或明确标记完成，避免过期快照被误读。

## 4. Weekly maintenance

### 4.1 Inputs

- `specs/active/`
- 最近一周合并的 Spec/PR/commit
- CI 失败和 flaky test
- Review 中的 Blocker/Major
- 新增 TODO/FIXME/temporary/deprecated/legacy 标记
- 架构例外和临时 Feature Flag
- 前端 baseline、UI current-state、Figma node、批准 snapshot 和视觉回归证据
- frontend engineering constraint revision、quality budgets、browser/a11y
  matrices、performance reports、exceptions、analytics schemas 和安全隐私证据



### 4.2 Review questions

1. 哪些 active Spec 已无人负责或长期无进展？
2. 哪些临时兼容路径已满足删除条件？
3. 哪些同类 Review 问题重复出现？
4. 哪些测试只在重跑后通过？
5. 哪些行为变更没有更新行为目录？
6. 哪些任务实际扩大了范围但 Spec 未同步？
7. 是否出现新增实现与旧实现并行？
8. 哪些前端 Spec 已完成但 UI current-state 未合并？
9. 哪些 Figma 记录只有文件链接、缺 node ID、Design Revision、snapshot 或 hash？
10. 哪些页面声称支持的分辨率没有设计或测试证据？
11. 哪些 frontend engineering constraints 仍是 Draft、与代码不符或包含假命令？
12. 哪些 a11y/browser/performance/security/privacy 声明没有实际证据？
13. 哪些组件、状态库、表单、样式或图表工具形成第二事实源？
14. 哪些性能/质量例外已过期，analytics 重复或 schema 无 Owner？



### 4.3 Actions

- 关闭、阻塞或重新分配 stale Spec；
- 删除已到期临时逻辑；
- 把重复三次以上的问题升级为自动检查或架构规则；
- 为未知历史行为添加 characterization task；
- 修正错误文档，不追加“补充说明”叠加冲突；
- 对超大 active Spec 拆分。
- 修复失效 Figma node/索引，补齐批准证据或创建阻塞任务；
- 删除非必要草稿导出，保留要求的批准快照；
- 对 style、interaction、resolution baseline 漂移提出重新确认任务。


## 5. Monthly audit

### A. Instruction audit

检查所有 `AGENTS.md` / `AGENTS.override.md`：

- 是否仍适用；
- 是否有互相矛盾的规则；
- 是否写了可自动化的格式要求，应移到 Lint/CI；
- 是否包含大段架构百科，应移到 `docs/`；
- 是否引用不存在的命令或路径；
- 是否存在过期临时 override；
- 根规则与模块规则的覆盖关系是否明确；
- 总体是否足够精简。

规则分类：

| Category | Action |
|---|---|
| 始终适用、频繁用到 | 留在最近的 `AGENTS.md` |
| 详细架构事实 | 移到 architecture docs 并链接 |
| 领域历史行为 | 移到 behavior catalog |
| 单次任务约束 | 移到 active Spec |
| 可机器检查 | 移到 CI/lint/architecture test |
| 已失效 | 删除 |

### B. Architecture drift

- 实际依赖是否违反 `ARCHITECTURE-CONSTRAINTS.md`；
- 模块是否绕过公共接口；
- 新增数据库/队列/外部服务是否已记录；
- 是否有多个事实源；
- ADR 是否被实现，或已被实际代码悄悄推翻；
- 例外表是否存在过期项。

### C. Behavior drift

从高风险行为抽样：

1. 读取行为条目；
2. 定位权威代码；
3. 运行关联测试；
4. 检查生产/预发可观察证据；
5. 修正文档或创建缺陷任务。

### C2. Feature current-state drift

抽样 `docs/domain/features/`：

1. 从 Feature 文档复述当前行为、接口、状态、权限、数据和架构映射；
2. 与代码、测试、运行时和最新完成 Spec 核对；
3. 查找 completed Specs 已关联 Feature 但没有 Change Reference；
4. 查找 Feature 正文仍描述已被 Bugfix/Refactor 替代的行为；
5. 合并正确事实，删除冲突描述，保持历史只存在于引用中。

### C3. Frontend design drift

抽样 `docs/design/frontend/`：

1. 检查 style consistency、user interaction conventions 和 resolution
   support baseline 是否已批准且仍匹配代码/Design System；
2. 从 UI current-state 复述当前节点、状态、视口、a11y 和实现映射；
3. 核对 Figma node、Design Revision、snapshot/hash、代码和视觉测试；
4. 查找 completed frontend Specs 未合并 current-state 或无 Change Reference；
5. 查找实现超出批准设计、失效链接、无证据分辨率和到期 waiver；
6. 替换过期正文，不把历史追加成冲突状态。
7. 核对 FEC 与组件/state/form、a11y/i18n/browser/performance/security/
   privacy/data-viz/observability 的真实实现和报告；
8. 删除过期基线，关闭或升级过期例外，不把零自动扫描告警写成已合规。


### D. Test health

- Flaky、quarantine 和长期跳过测试；
- 关键行为没有 integration/E2E；
- Mock 导致的假阳性；
- 迁移、权限、并发、幂等、失败恢复空缺；
- 测试耗时导致 Agent 只跑局部测试；
- CI 与本地命令不一致。

### E. Spec quality

抽样已完成任务，检查：

- 验收失败是否源于 Spec 遗漏；
- 是否明确写了非目标；
- 是否有删除清单；
- 是否出现未批准扩展；
- 实际验证是否回填；
- 是否能够由新 Agent 根据文档复述最终行为。

## 6. Quarterly governance review

### 6.1 Outcome metrics

| Metric | Definition | Trend | Interpretation |
|---|---|---|---|
| Lead time | APPROVED → DONE | `[TODO]` | 速度 |
| Rework rate | Review 后回到设计的任务比例 | `[TODO]` | Spec/Discovery 质量 |
| Escaped defects | 合并后产生的有效回归 | `[TODO]` | 验证质量 |
| Major review yield | 独立 Review 找到的 Major | `[TODO]` | 自检盲点 |
| Stale-doc incidents | 过期文档导致的问题 | `[TODO]` | 知识质量 |
| Legacy removal time | 临时路径创建到删除 | `[TODO]` | 熵控制 |
| Flaky rate | 非确定性失败占比 | `[TODO]` | 测试可信度 |

不要把行数、提示次数或 AI 生成占比作为质量 KPI。

### 6.2 Control improvements

对重复问题选择一个最靠近根因的控制：

```text
模型提醒
  < Review checklist
  < 编码约束
  < 类型/Schema
  < 自动测试
  < 架构测试/Lint
  < API/数据设计使错误状态不可表示
```

优先采用更稳定、可执行的右侧控制，而不是不断扩充提示词。

### 6.3 Recovery exercise

R3 系统至少检查：

- 数据恢复是否实际演练；
- 回滚命令是否可执行；
- 告警是否能到达 Owner；
- 关键 E2E 是否在接近生产的环境运行；
- 密钥/依赖失败是否有降级或明确中止；
- 审计证据是否完整。

## 7. Safe maintenance procedure

### Phase 1 — Read-only audit

1. 固定审计基线 commit；
2. 收集文件和自动化结果；
3. 生成 `MAINTENANCE-REPORT.md`；
4. 不在同一阶段做大范围代码修改。

### Phase 2 — Classify

每项标为：

- `DELETE`：失效、重复或已完成；
- `CORRECT`：事实错误；
- `MOVE`：放错层级；
- `AUTOMATE`：可转 CI/测试；
- `DECIDE`：需要 ADR/Owner；
- `TASK`：需要独立实现；
- `KEEP`：正确且仍有价值。

### Phase 3 — Apply low-risk cleanup

可以直接处理：

- 修复断链；
- 删除明确过期文档；
- 合并重复规则；
- 更新真实命令；
- 归档已完成 Spec。

需要独立 Spec：

- 修改生产代码；
- 删除可能仍有调用者的兼容层；
- 改架构边界；
- 改测试语义；
- 改公共契约或数据。

### Phase 4 — Verify

- 搜索旧链接和旧名称；
- 运行文档/Markdown/Lint 检查；
- 验证 `AGENTS.md` 发现顺序；
- 请新上下文 Agent 复述项目规则，观察是否存在歧义；
- 由 Owner 批准高影响更正。

## 8. Automation prompt template

可以把以下提示交给定时 Agent，但默认只允许它生成报告和低风险文档补丁：

```text
对仓库执行一次只读 AI Coding 治理巡检，基线为 <commit/range>。
阅读根和局部 AGENTS.md、架构文档、行为目录、ADR、测试策略、
active/completed Specs、最近 CI/Review 证据。

目标：
1. 找出相互冲突、过期、重复、不可执行或放错层级的指令；
2. 找出行为/架构文档与代码测试不一致；
3. 找出平行实现、到期兼容层、无 Owner TODO、失效 Feature Flag；
4. 找出重复出现但尚未自动化的 Review 问题；
5. 找出关键行为的验证空缺和 flaky/quarantined 测试；
6. 评估上期整改项是否关闭。
7. 检查前端 current-state、Figma nodes、批准 snapshots、分辨率和 a11y 证据。


只生成 MAINTENANCE-REPORT.md，不改生产代码，不删除不确定内容。
每条发现提供证据、影响、分类（DELETE/CORRECT/MOVE/AUTOMATE/DECIDE/TASK/KEEP）、
Owner 建议和完成条件。事实不确定时标记 NEEDS_VERIFICATION。
```

## 9. Anti-patterns

- 每周让 AI 自动“总结一下”但没有删除和 Owner；
- 把聊天记录全文塞进仓库；
- 用越来越长的 `AGENTS.md` 修复所有问题；
- 在没有证据时由 Agent自动删除“看起来没用”的兼容逻辑；
- 把所有警告都变成 MUST，导致规则失去优先级；
- 维护报告没有关闭条件，下月继续重复；
- 为提高指标而拆分/合并任务或写低价值测试。
