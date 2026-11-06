# 工作日备注减法 · DREV-20261105-WORKDAY-03

Task：[SPEC-20261105-WORKDAY-COPY-01](../../../../../specs/completed/FEAT-001-WORKDAY-COPY-CLEANUP.md)。Status：APPROVED；产品负责人2026-11-05回复具体审批问题“批准此修订并实施”。基线FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02；源与24张导出冻结，批准记录及SHA见同名APPROVAL manifest。

## 具体删除稿

- 设置活动安排和日程新建/编辑：删除“按中国大陆法定安排……”与覆盖年份/未显示/不提醒的两张说明卡；时间控件向上收紧，不新增帮助、折叠说明或占位。
- 设置保留既有时间摘要；不改三模式、草稿、picker、保存/移除、只读与错误恢复。日程编辑既有“作用于整个系列”直接后果仍保留。
- 确有缺覆盖的日程结果：一次短状态“工作日安排待更新”；其他已知日程照常呈现，不显示“没有安排”的确定空态。
- 今日活动：分区已有状态位置改为同一短状态，删除分区内长警告和重复空态；有已知活动继续显示。Today导出聚焦受影响活动区，前置其他分区在设计源中省略，实际顺序/默认展开策略不变。
- 通用规则拟补强：维护年份、实现限制及假想后果不写成常驻防御备注；同一实际异常只在受影响位置表达一次。未获本Spec批准前不改现行通用规范正文。

## 矩阵与合同

8态：settings-workday / settings-coverage / calendar-create / calendar-edit / calendar-coverage / calendar-partial-coverage / today-coverage / today-partial-coverage。每态320×568、390×844、430×932，100%系统字体、DPR1，共24张HTML设计导出及SHA清单。

settings-coverage与正常表单相同是预期：覆盖状态属于结果，不占用编辑表单。日程结果使用合成2027日期表示真实unknown；不推定该年法定数据。其余原有模式、只读/保存中/失败/转换确认继续沿用DREV02，本稿不重新批准其冻结源。

44px操作/14px正文下限、底部操作固定、表单内容可纵向滚动；HTML input是原生picker的设计占位。无新依赖、API、网络、权限、存储、资源或埋点，不把数据更新自动化当作已实施。

`index.html`可编辑，`render.py`可再生未批准导出；批准后源和manifest冻结。导出只证明HTML设计，不替代原生节点、三视口截图、iOS/Android或读屏验收。
