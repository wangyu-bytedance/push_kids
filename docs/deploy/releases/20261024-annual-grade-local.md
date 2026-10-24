# 学年年级确认：本地交付

- Date: 2026-10-24
- State: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED / NOT_DEPLOYED
- Authorization: 用户“好的 按照这个方案落地”，批准[Spec02、Architecture02、DREV01](../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md)。
- Evidence: [本轮验证](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)。

2026-10-24前端局部增量：[精简Spec01](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md) / DREV02获用户“继续”批准，已在原年级组件实现单标题/选择、并排操作和行内短提示。最终327项前端/53项定向、三尺寸51组原生及实际选级/重试/稍后通过；真实设备/可访问性及全业务原生端到端边界见[精简实施证据](../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)。该增量不改API、Schema、后端版本或四类平台发布状态；仍为本地VERIFYING，未上传部署。下文313项和旧原生采集是DREV01/主任务证据，不抵扣新布局。

本轮没有提交、推送、生产DDL、云端部署、上传、体验版、提审或正式发布。现有生产版本/Schema与其他任务的发布记录不因本地实现改变。

本任务迁移为0025，接共享工作区已有0024；新增children.grade_confirmed_school_year、grade_revision及家庭/在用/清理/排序索引。旧grade不变、旧基准为NULL；首次由家长核对。SQLite与隔离MySQL5.7.44验证增量升级、重启保持及有事实时拒绝降级。没有对生产数据库执行本迁移。

未来发布先冻结实际范围、核验0023/0024依赖及原生真机门禁，再遵循[部署手册](../README.md)执行迁移→后端→兼容客户端。本地独立评审已通过，不能代替上线验收。旧客户端无明确意图/version的改级会返回409，须在灰度前验证更新提示与输入保留；同级普通保存和旧读兼容。旧后端无候选接口时客户端不阻断日常使用，但不能据此宣称功能上线。

回滚优先保留增量Schema与最后正式grade；有确认事实时0025拒绝破坏性降级。回退旧writer前必须停止确认并验证基准/version兼容，不可混用覆盖新事实。需要保留/恢复数据的方案须单独批准，不绕过降级保护。

原生采集工具只操作`/private/tmp/push-kids-grade-native-20261024`离线合成副本，生产配置和transport不改，副本拒绝业务写入。解锁后已采集三尺寸17态、档案九年级控件及系统picker打开/取消。四项独立review发现已修复并关闭，最终前端313/定向53项通过；修复后原生端到端、真实iOS/Android、可访问性及双家长旧端仍待验收，整体为PARTIAL。不存在上传或真实孩子数据操作。
