# FEAT-013 — 学年升年级建议与家长共享确认

- Feature ID: `FEAT-013`
- Status: `LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED`
- Current-state revision: `FEAT-STATE-20261024-ANNUAL-GRADE-LOCAL-08`
- Owner: 产品负责人（用户）
- Last updated: 2026-10-24
- Task Spec: [Spec02 / Architecture02](../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md)，用户“好的 按照这个方案落地”批准，当前VERIFYING。
- Verification: [本轮证据与未验收项](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)。

本文记录本地实现；原生端到端和设备门禁尚未全部满足，不代表线上可用。

当前呈现增量：[年级弹窗精简Spec01](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)与[DREV02](../../design/frontend/prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md)于2026-10-24获用户“继续”批准并本地实现，只保留孩子名标题、picker和并排操作，必要时显示简短恢复提示。最终全前端327项、定向53项、三尺寸51组原生及实际选级/失败重试/稍后通过；真实设备/可访问性及全业务原生端到端边界见[实施证据](../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)。主Spec02领域规则不变。

## Current user/system behavior

北京时间9月1日进入新学年。服务端提出小班→中班→大班→一年级至九年级的建议，家长确认前正式grade不变；首次没有确认基准的旧档案只核对原年级，不按建档日期补升。正式九年级、未知/空/其他/未细分学前、归档和清理中孩子不进入启动候选。归档保留基准，恢复后按跨过学年累计建议，封顶九年级，只核对当前一次。

每个孩子每学年全家共享一次确认。manager/editor可写，viewer无候选且写入403，跨家庭404。服务端按孩子锁及版本条件更新grade/确认学年/revision；同学年同结果重试返回已确认，不重复升，不同结果返回409。GET不写库，不涉及学习、复习、Todo或AI。

## Client and manual correction

五Tab承载一个共享确认组件；当前选中孩子优先，其他在用孩子按稳定顺序逐个核对，不切换全局孩子。弹窗可选择实际年级、保持原级或稍后处理。稍后零写入，本次前台会话不重复，下次进入重新提醒。已有弹层、上传和未保存输入时等待安全点；失败保留选择，冲突须读取最新结果，身份变化失效迟到响应。

弹窗当前按DREV02显示“孩子名的年级”、一个原生picker及左“稍后”/右“确认”。学年、旧级、独立姓名、开学/共享说明均删除；错误为行内短提示，无说明卡。保存中禁用picker与操作；冲突只能查看最新，最新态仅正式年级/短提示和“继续”，不提供覆盖picker。选级仍只更新草稿。

新建明确填写支持级，或在档案页触碰年级选择后明确保存，均建立保存当天所在学年的基准。只改名字/时长不确认年级。人工保存后bootstrap同步移除本会话旧候选；新增/恢复在用孩子时安全刷新，归档/确认元数据变化使旧在途候选失效，保留已稍后集合和当前选择。档案改级冲突时只读刷新最新正式级/version，保留草稿并要求重新选择，不能自动换版本覆盖。暑假提前填写仍属于保存当天学年，9月可确认保持原级。不增加暂停开关、常驻升级说明、订阅通知或自动归档。

## Contracts and data

- `GET /api/v1/children/grade-confirmations`：学年、权限及最多5项，数据库LIMIT6一致性哨兵；第6个在用档案返回异常，不静默截断。
- `POST /api/v1/children/{id}/grade-confirmation`：school_year、expected_grade_revision、支持级；事务返回正式ChildView与outcome。
- `PATCH /children/{id}`：明确改级必须携带confirm_grade和expected_grade_revision；未带grade不改变元数据。旧表单同级普通保存可用，旧改级返回升级要求409，不能覆盖新确认。
- 原有canonical字符串兼容存储，前端显示一至九年级；精确旧别名可识别，未知值原样保留。
- 迁移`20261024_0025`接0024，仅新增children两列及tenant-leading索引；旧grade和NULL基准不回填。存在确认事实时拒绝删列降级，重启不重置。

children拥有纯grade_policy和grade_confirmation用例，现有profile service接入；不反向依赖families、planning、reporting或provider。小程序coordinator拥有前台会话/队列/迟到失效，组件只呈现与发事件，页面只接宿主事件。无新框架、定时任务、历史表或持久化忽略记录。候选一次SQL、最多5项/8KiB，双数据库50k归档+5在用实际查询与索引验证见证据。档案生命周期由[FEAT-005](FEAT-005-multi-child-profiles.md)拥有，启动授权由FEAT-002拥有，其他消费者继续只读正式grade。

## Current evidence and limitations

- 规则/API/迁移/并发/规模/前端会话自动化已执行，具体命令和结果见[证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)。
- 当前弹窗采用[DREV02/33张批准导出](../../design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md)；[DREV01/57张冻结导出](../../design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/APPROVAL.md)保留初版呈现与档案表单事实，仅追加弹窗范围Superseded by指针。两轮HTML均不证明原生/设备验收。
- 解锁后已在官方开发者工具采集320×568、390×844、430×932各17态节点/截图、三尺寸档案九年级/保存控件与系统picker打开/取消；320错误提示已实际滚动核验完整可读。修正按钮默认缩宽、同步宿主通知递归及320档案保存按钮不足44px。随后修复恢复/互斥/冲突/在途竞态，前端313项及定向53项通过，[独立只读评审](../../quality/evidence/grade-confirmation-20261024/independent-review.md)PASS。修复后原生端到端、字体放大/读屏、iOS/Android和双家长旧端仍待验收，不能用合成呈现替代真实设备。
- 本任务未提交、推送、生产迁移、部署或上传。工作区0025不代表线上Schema升级；生产阶段以既有发布记录为准。Spec保持active/VERIFYING，不满足DONE门禁。

## Change References

| Date | Final current-state change | Spec | Verification / release |
|---|---|---|---|
| 2026-10-24 | DREV02局部精简：孩子名标题、单picker、并排操作与行内恢复提示，保留全部确认业务规则 | [精简Spec01](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md) | [实施证据](../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)；327/53项及三尺寸51组、实际局部交互通过，真实设备/可访问性待齐，未发布 |
| 2026-10-24 | Q1–Q18收敛并批准Spec02/Architecture02/DREV01；本地实现确定性建议、共享确认、独立会话弹窗与显式人工定级；原生呈现及四项独立评审修复 | [Spec02](../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md) | [实施证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)；独立review通过，原生端到端/设备验收待补，未发布 |
