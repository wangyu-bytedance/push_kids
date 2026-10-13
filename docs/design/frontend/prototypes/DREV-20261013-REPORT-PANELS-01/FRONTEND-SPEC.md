# 报表展开区设计合同

- Design Revision: DREV-20261013-REPORT-PANELS-01
- Task Spec: SPEC-20261013-REPORT-PANELS-01，`specs/active/FEAT-001-REPORT-PANELS-REFINEMENT.md`
- Approved by: 产品负责人（用户），2026-10-13，“可以 这个方案可行”。
- Baseline: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02。
- Editable source: `index.html`；预览范围为报表科目统计至活动段落，示例数据。
- Matrix: collapsed/history/plan/both/menu × 320×568、390×844、430×932。

保持历史和编辑计划独立展开。每个区为完整外层卡片，标题含说明与展开/收起文字，展开体通过细线衔接；历史使用日期分组与分隔行，计划保留时间/科目/次数筛选及科目组，条目右侧44×44px「调整」打开原有菜单。两块底部均可收起。原有搜索、筛选、分页、详情、只读、冲突、保存与删除确认合同保留。

用户在同一批准消息明确要求不影响并行的card背景优化。因此外层背景、材质、阴影及装饰由统一pk-card/并行任务负责；本设计批准范围集中于内部布局与交互。允许最终背景随该任务批准的视觉变化；不得覆盖其共享token或背景样式。

HTML演示不接API，筛选及写操作提示只用于说明意图，原生实现须沿用已有领域控制器，三视口节点几何不能由HTML替代。真机验收另行记录。
