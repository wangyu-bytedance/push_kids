# DREV-20261024-TODAY-LEARNING-03 — 今日学习空区与风格一致性

- Status: APPROVED
- Approved by / at / evidence: 用户 / 2026-10-24 / call_ac391833df284fc7b0afcb71c55abec7「批准，按此实现」。HTML、63张PNG及其SHA清单自此冻结。
- Date: 2026-10-24
- Task Spec: [SPEC-20261024-TODAY-CARD-VISIBILITY-01](../../../../../specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md)，APPROVED。
- FDB / FEC: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，均APPROVED。
- UI / Feature: UI-001 / FEAT-004；[当前UI](../../ui/UI-001-parent-miniapp.md)。
- Source: [index.html](index.html)；[候选SHA清单](../../snapshots/UI-001/DREV-20261024-TODAY-LEARNING-03/APPROVAL.md)。
- Base: DREV01今日卡片；DREV02弹层保持批准源不变，本稿不重画弹层。

Operate方向：沿用知芽的暖白纸面和松绿，分区标题采用现有衬线字阶，正文采用既有无衬线字阶，胶囊操作与邻接模块一致；没有内容的区域整块消失，不加装饰或动效。

无内容的无资格/未知/eligible待生成快照隐藏整个今日学习分区，不留下标题、原因或额外间距。生成中及明确可恢复失败/删除重生只显示必要状态和入口，避免关闭后找不到进度。viewer只有已批准待学才显示。服务端资格、共享提示与请求时序不改。

有proposal时直接显示具体学习标题、科目/可选时长、简短AI建议标识和查看按钮；删除“小步延展，家长做主”“沿着学过的，再走一小步”及其通用介绍。有task时保留具体内容、状态及实际记录/删除操作。

分区标题与复习安排相同：17px、600、var(--pk-serif)，字距0.4px；实际标题与复习卡todo-title相同：16px/600无衬线、1.4行高、0.2px字距，正文与元信息14px。卡片沿用pk-card（32rpx内边距、40rpx圆角、纸面描边/轻影），按钮沿用btn胶囊（查看为secondary、记录为primary），确保≥44逻辑像素。标题/正文完整换行；不通过overflow-x:hidden掩盖问题，不截断实际标题。

精确矩阵：320×568、390×844、430×932，DPR1，各21态，共63张。状态名：recent-new、warming-up、no-history、missing-grade、no-subject、disabled、inactive、eligible-empty、viewer-empty、unknown-empty、proposal、proposal-long、task、partial、viewer-task、task-feature-off、generating、generation-error、stale、recover-after-remove、network-error。每张包含Hero和相邻复习分区以核对隐藏间距与字体一致性；长标题态向下滚动展示完整卡片。顶部导航等为合成上下文，不重新批准全局设计。

查看/实际记录/删除及进度/失败入口在原型中链接到已批准DREV02相应状态，仅用于说明原处理器保持不变；设计不调用后端/模型，不承诺真实请求端到端。当前设计导出、布局与入口目标核对结果见[设计证据](../../../../quality/evidence/TODAY-CARD-DESIGN-20261024.md)。批准后才进行生产显隐/样式修改与原生取证；原型不能替代原生或真实设备。
