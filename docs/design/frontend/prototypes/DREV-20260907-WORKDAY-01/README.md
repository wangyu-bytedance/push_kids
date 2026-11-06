# DREV-20260907-WORKDAY-01

- Status: `HISTORICAL_UNAPPROVED_CANDIDATE`
- Related Spec: 旧`SPEC-20260907-WORKDAY-01`，现由[SPEC-20261105-WORKDAY-02](../../../../../specs/completed/FEAT-001-CHINA-WORKDAY-SCHEDULES.md)替代；本HTML仅作历史参考，不覆盖当前逐星期不同时间兼容和完整结果态。
- Related UI: `UI-001`
- Baseline: `FDB-20260906-03 / FEC-20260906-04`
- Scope: 活动安排与日程编辑器的中国工作日选择。
- Evidence mode: repository-native；新Spec02实施前须补齐对应DREV02可编辑源、三视口状态导出与SHA manifest并明确批准，Figma不是前置条件。

以下保留旧候选的交互方向，本候选未获批准；新修订的审批范围以Spec02及待生成DREV02为准：

1. 活动安排使用“指定星期 / 工作日 / 时间不固定”；
2. 日程使用“不重复 / 每周 / 工作日”；
3. 工作日按中国大陆全国统一法定安排，法定假日跳过，周末调休上班日出现；
4. 日程的日期字段在工作日模式下是“起始日期”；
5. 卡片与编辑态统一显示“工作日”，数据覆盖缺失时显示明确警告。

原型只用于设计批准，不参与小程序运行。
