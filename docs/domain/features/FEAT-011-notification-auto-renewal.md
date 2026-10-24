# FEAT-011 — 提醒授权自动补充

- Feature ID: FEAT-011
- Status: BACKEND_035_DEPLOYED / CLIENT_LOCAL / VERIFYING / CLIENT_NOT_UPLOADED
- Current-state revision: FEAT-STATE-20261024-NOTIFICATION-AUTO-RENEWAL-02
- Owner: 产品负责人（用户）
- Last verified: 2026-10-24（生产迁移0022/表结构；功能验收未重测）
- Approval: 用户2026-10-17“按照这个方案落地”，批准SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01、ARCH-20261017-NOTIFICATION-AUTO-RENEWAL-01及DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01。
- Task Spec: [active / VERIFYING](../../../specs/active/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md)
- Related Features: [FEAT-003](FEAT-003-notification-channel.md)、[FEAT-001](FEAT-001-push-kids-mvp.md)
- Design: [批准的设计](../../design/frontend/prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/FRONTEND-SPEC.md)，42张批准快照不变。

## Current local behavior

本地视觉增量 `FEAT-VISUAL-20261021-HERO-ARC-01`：提醒正常/中性卡随共享样式删除细弧线，自动补充合同保留。
[Spec01](../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md) / DREV-20261021-HERO-ARC-REMOVAL-01已批准；
实际验证和验收缺口见[本轮证据](../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)，未上传/部署。

默认尚未选择。本人已有授权历史、已开启且次数为0的类型，在成功完成复习后可显示首次说明。
只有点击“开启自动补充”才调用微信并登记开启选择。“暂不开启”、遮罩或离开说明尝试保存关闭；
保存失败不伪造已关闭。候选过期时保留说明并刷新，须再次明确点击。

已开启后，仅手动复习complete的同步点击链可以调用微信，在任何业务await前执行。
服务端复核成员/角色、通道、类别开关、当前模板同意、次数0、选择版本、逐类型冷却和租约。
微信记住允许可以绕过普通冷却；未记住允许、普通拒绝或取消，以结果登记时本人完成游标为基准，
再成功完成10条后，下一次点击才申请。正额度或长期额度-1不补充，不替其他成员增加次数。

明确关闭、微信总开关关闭、记住拒绝及ban/filter停止自动申请，须手动恢复。
换模板或旧granted_at没有当前模板证明时，先明确授权，不静默绑定。
复习保存与微信结果独立，失败复习不计数，没有额外自动补充Toast。

授权按原attempt ID幂等登记，真实accept最多增加一次额度。登记失败仅重试原结果，不再次请求微信。
进程退出丢失回调时不能从getSetting推导额度：未决事件保持待确认，停止自动申请，提供手动恢复。
租约60秒、客户端最多55秒；查询失败、身份变化时跳过。业务状态不写Storage。

## Contracts, ownership and data

- planning拥有本人完成游标及同成员/复习/上海日receipt，与反馈同事务；历史不回填，其他反馈和每日任务不计。
- notifications拥有选择CAS、模板证明、逐类型冷却及事件去重；只通过PlanningService公开合同读游标，无反向依赖。
- 新API：GET/PATCH `/notifications/renewal`；POST `/notifications/grant-attempts`；GET `/{id}`；POST `/{id}/started`和`/{id}/result`。全部仅可信本人，最多3类。
- 旧`/notifications/subscriptions`保留兼容，旧格式本身没有事件去重；新客户端全部迁移到attempt合同。
- 增量迁移`20261017_0020`新增5表。receipt及非活动attempt保留30天；累计游标不回退，活动未知attempt不自动回收。
- 孩子删除清理其receipt；家庭删除清理全部本域数据；成员离开由维护扫描停止选择并失效租约。新表有数据时拒绝破坏性降级，应用回退保留数据。
- UI-001增加首次说明，显示时隐藏底部导航、背景aria-hidden，关闭后恢复导航。UI-011增加独立开关和逐类次数/冷却/停止/待确认及手动恢复入口，失败不显示假就绪。

## Verification, release and lifecycle

[实现证据](../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)记录自动化、真实MySQL5.7迁移/并发/规模、原生证据及缺口。
[设计期证据](../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-DESIGN-20261017.md)只证明批准设计，不代验运行时。
iOS/Android真实授权、记住偏好、字体放大/读屏、完整原生截图及独立评审未完成，Spec保留active/VERIFYING。
2026-10-24按用户明确同库顺序执行冻结0019→0022/current/check，续订五表在生产；035部署后由用户100%接管并删除034，11:01–11:03旧实例0、035正常、18项原配置保留。真实微信GET续订/设置及live/ready均200，完整客户端本地已打开，见[发布记录](../../deploy/releases/20261023-fullstack-test-deployment.md)。全量前定向检查未执行；真实点击授权/额度/记住偏好仍未验收，未提交git、客户端上传/体验/提审/正式发布，未额外调用授权或发送。后端接管不代验完整续订；Spec仍VERIFYING。

## Change references

2026-10-17：批准并本地实现本人自动补充、完成游标及事件去重；本页替换原PLANNED事实。
Spec为SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01，发布状态为未发布。
