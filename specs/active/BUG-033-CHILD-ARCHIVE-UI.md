# BUG-033 — 档案归档区层级与文案精简（Spec Lite）

- Status: READY_FOR_REVIEW
- Risk: R1；局部可逆的呈现/文案变更，不改数据、API、权限或异步流程。
- Owner: 产品负责人（用户）
- Implementer: Codex（待批准后实施）
- Reviewer: 实施后独立只读复核，尚未执行。
- Date: 2026-10-24
- Spec revision: `BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01`
- User confirmation: PENDING；用户指出截图“这个部分的ui和文字堆砌有问题”，未批准本具体修订。
- Affected Feature IDs: FEAT-005；FEAT-013仅回归年级表单同页兼容。
- Feature current-state documents: [FEAT-005](../../docs/domain/features/FEAT-005-multi-child-profiles.md)、[FEAT-013](../../docs/domain/features/FEAT-013-annual-grade-promotion.md)。
- Feature baseline revision: FEAT-STATE-20260906-02-MULTI-CHILD；年级增量FEAT-STATE-20261024-ANNUAL-GRADE-LOCAL-06。
- Feature/UI merge owner: Codex依据已验证实施事实同步，当前不改写已实现语义。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes；归档/恢复操作卡、提醒和归档确认文案。
- Frontend engineering impact: yes；页面局部WXML/WXSS及JS文案，操作流程不改。
- Affected UI: [UI-015](../../docs/design/frontend/ui/UI-015-child-profile.md)。
- Baseline: `FDB-20260913-04`（APPROVED）；engineering: `FEC-20261007-NATIVE-GEOMETRY-02`（APPROVED）。
- Quality dimensions: component/state/form/responsive/a11y/i18n/browser/performance/security/privacy/observability。无表格、图表、媒体、AI或新动画。
- Requirements: 保留既有token与纸色风格；正文≥14px、所有触控≥44px、自然换行；FEC-PERF-READ-001..004维持既有有界读取、计数口径和0新增请求。
- Current design: 年级DREV-20261024-ANNUAL-GRADE-PROMOTION-01已批准，其源和57导出不可改。本修订只替代同页归档卡局部视觉。
- Proposed Design Revision: `DREV-20261024-CHILD-ARCHIVE-01`。
- Editable source: [自包含HTML](../../docs/design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/index.html)。
- Design source SHA-256: `b52125179caf4d795ed9da701f5e5bca12bc400ac73a9e99160051b89aa5f576`，与[候选manifest](../../docs/design/frontend/snapshots/UI-015/DREV-20261024-CHILD-ARCHIVE-01/APPROVAL.md)一致。
- Required exports: 320×568、390×844、430×932；active/unfinished/archived/working/error/confirm/confirm-unfinished共21张。
- Prototype status: AWAITING_APPROVAL；approved Task Spec/Design/approval evidence均PENDING。
- UI current-state merge: 目前仅登记待批准候选，实施验收后替换相关正文。
- Engineering evidence: HTML几何、字体和交互检查单列；生产/原生/真机待批准后验证。
- Approved deviations: none。External design dependency: none。

## 1. Problem and outcome

用户截图中，“归档和恢复都不会删除任何记录”与正文再次说明历史保留；居中长文形成松散的多行，标题“档案状态”却没有实际状态值，红色垃圾桶又与可恢复归档含义不符。

源码可直接复现：child-edit WXML的card-head/c-s、danger-copy和danger-link三层；局部CSS将danger-zone居中，说明及链接字号13px，低于现行正文14px要求。不是日期升级逻辑导致。

期望结果：家长扫到一个明确操作及一句简短说明，点击后才核对完整影响。

## 2. Scope

- 归档卡改为左对齐整行操作：“归档档案”＋“保留全部记录，随时可恢复”＋右箭头。删除“档案状态”泛标题、重复长说明及垃圾桶/常驻危险色。
- 未完成时仅补一条“还有 N 条记录待处理，归档后仍可继续完成。”；未知数量不编造、不阻断。
- 已归档时用同一结构“恢复档案”＋“重新加入孩子列表，继续记录”。
- 归档确认框集中说明隐藏、停止新增、保留历史与可恢复；有未完成数量时补确认和复习反馈可继续，具体文案见[前端合同](../../docs/design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)。
- 进行中禁用重复点击；错误沿用页内错误区并保留表单。

Non-goals：改归档写入许可、归档态顶部说明、保存表单、年级确认、数据库/接口、清理/删除、发布或全局样式。既有“归档资料可编辑”文档与服务active门禁的差异已由年级任务单列，不在本修订中改行为或掩盖差异。

Must not change：manager权限、二次确认、归档/恢复幂等、未完成数量来源、归档后的收尾能力、全家切换回落，以及FEAT-013的touched/version/冲突恢复。

Feature current-state impact：实施后更新FEAT-005/UI-015中危险区提醒/文案结构，替换原长说明约定并引用本Spec与实际证据；Behavior BHV-023/归档BHV-025的业务规则不改，只同步呈现事实；Architecture复核后记录无边界变更，不新增抽象。

## 3. Impact map

- Entry: 设置→学习档案→child-edit编辑态。
- Authoritative presentation: `pages/child-edit/index.wxml` / `index.wxss`；JS仅改unfinishedHint与归档确认文案。
- Existing dependencies: `api.request`、`app.refreshBootstrap`、`children`生命周期服务，全都沿用。
- Existing tests: `tests/frontend/child-profiles.test.js`、`grade-confirmation.test.js`；先复用有效权限/保留草稿/归档恢复断言，必要时更新文案断言，不为纯CSS增加镜像测试。

## 4. Required design views

### Link/call graph

```text
设置档案 → child-edit → 归档操作行 → 原wx.showModal → 原archive/lifecycle
                    → 恢复操作行 → 原restore/lifecycle
                    → 原API → children service → bootstrap切换回落
```

### Sequence diagram

```mermaid
sequenceDiagram
  participant P as 家长
  participant V as 档案页
  participant API as 原生命周期API
  P->>V: 点归档行
  V-->>P: 集中显示归档影响及未完成提醒
  alt 取消
    V-->>P: 保留表单，无请求
  else 确认
    V->>API: 原归档请求
    API-->>V: 原成功或错误结果
    V-->>P: 原返回或错误保留路径
  end
```

### State machine

```mermaid
stateDiagram-v2
  active --> confirming: 归档行
  confirming --> active: 取消
  confirming --> working: 确认
  working --> archived: 原API成功
  working --> active: 原API失败，表单保留
  archived --> working: 恢复行
  working --> active: 恢复成功
```

只描述既有状态在新呈现中的映射，不新增领域状态。

### Architecture diagram

N/A：无模块、owner、依赖方向、事务、开放点或部署拓扑变化；只修改原页面的权威呈现和文案，不建立组件/工具层。接口/序列closed，其他档案能力deferred。

### Trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 单行操作＋短说明＋原确认框 | 信息集中，减少重复，归档含义准确 | 详细影响需点击后查看，确认前完整展示 | selected |
| 保留大卡仅缩文案 | 改动少 | 泛标题/居中/垃圾桶仍然冲突 | rejected |
| 加开关或自定义弹层 | 可改变展示 | 引入新的状态/组件与误操作风险，超出问题 | rejected |

## 5. Expected file changes and deletion plan

| File | Action | Purpose |
|---|---|---|
| child-edit/index.wxml、index.wxss | modify after approval | 原归档/恢复区域收敛成整行；移除废弃card-head/danger-copy/danger-link局部样式 |
| child-edit/index.js | copy-only after approval | 精简unfinishedHint及modal文案，保留事件/计数/事务/错误逻辑 |
| tests/frontend/child-profiles.test.js | minimal modify if needed | 保留真实行为断言并调整旧长句断言 |
| 本Spec、prototypes/DREV与snapshots/UI-015/DREV | add | 提供可审阅方案、源/SHA与状态矩阵 |
| UI-015、FEAT-005、Behavior、FrontendDesign、Spec/Feature索引、验证证据 | scoped update | 批准/实施/原生/发布事实分别记录 |

最终仍由原child-edit负责；没有备用路径、迁移或数据修复。回滚仅撤回本次局部呈现/文案，不碰年级任务改动。当前共享工作区dirty，保留其他任务全部修改。

## 6. Acceptance criteria

- AC-001：普通在用档案只显示一个归档操作行和一句短说明；左对齐、无垃圾桶、无泛标题与重复段落。
- AC-002：未完成计数真实、未知不显示；提醒不阻断，确认框可理解全部后果，取消不写。
- AC-003：恢复/进行中/错误/权限语义沿用；年级字段、明确意图与冲突草稿路径回归通过。
- AC-004：三精确视口及长提醒/原生确认可读，所有触控≥44px、正文≥14px；没有靠隐藏溢出通过。
- AC-005：文档/证据真实对应；批准设计源不可变；未通过适用门禁不DONE，不把HTML当原生或部署。

## 7. Required test points

| Point | AC | Command / case | Required result |
|---|---|---|---|
| TP-001 | 001/004 | 设计render.py、manifest validator --allow-pending --check-current-policy | 21导出/SHA、无横溢、14px/44px、HTML取消/焦点/禁用通过；不抵扣原生 |
| TP-002 | 002/003 | `node --test tests/frontend/child-profiles.test.js tests/frontend/grade-confirmation.test.js` | 归档/恢复/取消/错误保留、计数汇总/失败降级、年级路径均通过 |
| TP-003 | 001/003/005 | `npm test`、`npm run lint:miniapp`、小程序/architecture/design验证及`git diff --check` | 适用检查通过，无其他任务混入；纯前端无后端测试要求 |
| TP-004 | 001..005 | 原生320×568/390×844/430×932归档/有未完成/恢复/进行中/错误及确认框；iOS/Android、字体放大/读屏 | 原生矩形和截图、操作/标签/焦点记录；未执行明确NOT_RUN，Spec保持VERIFYING |
| TP-005 | 005 | 独立只读复核与逐文档冲突检查 | 无Blocker/Major；只读阶段不修改代码 |

## 8. Plan

1. 生成具体设计与三视口候选；用户批准本Spec01+DREV01后再改业务页面。
2. 在原页面替换呈现与文案，定向/全前端及适用静态检查。
3. 原生/设备验证、只读复核、文档闭合；完成门禁通过才DONE并迁completed。

## 9. Verification

| Check | Status | Evidence |
|---|---|---|
| 截图及源码定位/同模式检查 | EXECUTED | 用户截图；同页归档/恢复共享danger-zone，未涉及其他页面 |
| TP-001 | PASS / HTML_ONLY | `python3 docs/design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/render.py`生成21导出；validator `--manifest .../APPROVAL.md --allow-pending --check-current-policy`通过，详见[证据](../../docs/quality/evidence/CHILD-ARCHIVE-UI-DESIGN-20261024.md) |
| 设计脚本Ruff/format及文档空白检查 | PASS | 脚本首轮长行已修正，最终Ruff/format与`git diff --check`通过；不代表生产实现已验证 |
| TP-002..005 | NOT_RUN | 尚未批准/实施，不能借年级任务313项和既有原生证据抵扣新diff |

## 10. Completion

当前只完成问题定位与设计准备，业务页面未修改；Spec保留active/READY_FOR_REVIEW，恢复条件为本Spec01+DREV01明确批准。API/数据/架构/发布事实未改变。待批准候选只登记索引/UI当前文档，不把提案合并成已实现行为。

- [x] 局部范围、原因、替代方案及设计视图明确。
- [ ] 具体Spec01+DREV01批准。
- [ ] 生产实现、全部适用检查及原生/设备验收完成。
- [ ] 独立复核、Feature/Behavior/UI/Spec/证据收尾，无无主或旧分支。
