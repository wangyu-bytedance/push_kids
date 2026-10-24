# 今日学习空区隐藏与风格一致性 — 设计阶段证据

- Date: 2026-10-24
- State: HISTORICAL_DESIGN_STAGE / NOW_APPROVED / NOT_RELEASED。本文件记录批准前设计阶段；用户随后批准Spec01/DREV03，当前实现及验收见[TODAY-CARD-IMPLEMENTATION](TODAY-CARD-IMPLEMENTATION-20261024.md)，下述未修改源码/待批准等描述仅指当时。
- Scope: [Card Visibility Spec01](../../../specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md) / [DREV03](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md)。
- Sources: [editable HTML](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/index.html)、[63张SHA清单](../../design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-03/APPROVAL.md)、[render-report.json](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/render-report.json)。

设计阶段基线组件仅排除disabled，因而recent_new/观察期/缺学习基础等状态仍显示原因卡；eligible纯空快照显示通用口号和生成入口。当时外层标题16px无衬线、内容20px和非胶囊按钮，与sec-bar/s-t、todo-title及btn不一致。本次设计明确整块隐藏无内容区域，已有生成/恢复保留必要状态，有内容直接显示具体标题；沿用17px衬线分区标题、16px复习卡内容标题、14px正文和胶囊按钮。

实际执行：.venv/bin/python docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/render.py，经工具审批启动隔离临时Chrome profile，只打开本地合成原型及原已批准DREV02入口，不连接业务后端、模型或真实儿童数据。

- 初次63张导出与8入口通过；复核仓库tokens/todo-title后，将实际标题精确校准为16px/600、1.4行高/0.2px字距，校正primary-strong和pk-border值，再重导最终63张与8入口，全部通过。当前清单只对应最终源。
- 21态×3视口，320×568、390×844、430×932，DPR1；10种纯空状态无study-region节点，复习区域距Hero只保留原分区间距；不残留空标题/卡片或额外占位。
- 有内容/进度分区标题与复习安排的font-family/font-size/font-weight一致；内容标题16px，正文/操作≥14px；所有操作≥44px且在横向边界内，页面无横向滚动；只读task无写按钮。无口号式文案。
- 8个入口跳至已批准DREV02的建议、实际记录、删除、生成中、失败、失效、删除重生、网络恢复状态；相应dialog存在。该检查只说明候选入口沿用原流程，不是实际API/原生端到端。
- Runtime异常0；Chrome/155.0.8059.85。目视检查390主态/空区、320最长120字换行，校准后复核390主态及430待学；长标题样本滚动到本分区便于阅读，未截断实际内容。

收尾校验实际结果：

| 检查 | 结果 |
|---|---|
| DREV03候选及当前政策 | validate_design_evidence.py --manifest DREV03/APPROVAL.md --allow-pending --check-current-policy：DESIGN_EVIDENCE_VALID |
| DREV01/02批准源及SHA | 分别运行同校验器，无allow-pending：均DESIGN_EVIDENCE_VALID，旧78/84张与源未修改 |
| 新render.py | Ruff check、format --check通过；初次check发现1处长行，已仅换行修正检查脚本，HTML/导出不变 |
| 链接/生命周期/源码 | 8份本轮相关文档，链接0缺失、围栏和尾部空白通过；Spec为active/READY_FOR_REVIEW，无completed副本；生产today-learning四文件SHA与上一轮取证一致 |
| 架构 | check_architecture.py：ARCHITECTURE_VALID policies=4 modules=150，runtime/lazy DAG |
| Diff空白 | git diff --check退出0 |

设计阶段生产组件未改，Feature revision05-LOCAL与UI/设计/Spec索引当时只登记候选；已批准DREV02及上一轮311项/45组原生证据不证明新卡片。Behavior Catalog的BHV-045与Architecture/ADR所有权、依赖方向保持有效，设计阶段不添加发布事实。

设计阶段Spec为READY_FOR_REVIEW、位于specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md。随后用户批准并实施，当前VERIFYING；DREV01仅追加卡片范围Superseded by，旧源/PNG/SHA不变。

设计阶段生产修改、npm/ESLint/原生/真实设备/读屏/大字体均NOT_RUN；批准后的实际执行与缺口以实现证据为准，设计布局、入口跳转、SHA与链接检查不能替代。
