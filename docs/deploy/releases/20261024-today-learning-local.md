# 今日待学与空白日提前复习：本地交付

- Date: 2026-10-24
- State: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED / NOT_DEPLOYED
- Authorization: 两份Spec04、Architecture02/03和Design01已获「批准，按此实现」；建议弹层另获Refinement Spec01/DREV02批准，今日卡片获Visibility Spec01/DREV03批准，标题约束获Title Limit Spec01/Architecture01/DREV04批准。均仅本地实施，未请求或执行部署。
- Specs: [FEAT-001](../../../specs/active/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md)、[FEAT-004](../../../specs/active/FEAT-004-INCREMENTAL-LEARNING-PATH.md)。
- Evidence: [本轮验证](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)。

标题约束按[Title Limit Spec01](../../../specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md)/DREV04本地实现：API/Provider新生成与重新编辑要求trim后1–20码点、无内部换行，客户端显示计数及字段错误。没有DB迁移/flag/查询变化；旧21–120字读取/审批/实际记录/删除兼容，旧客户端超长PATCH返回422且保留服务端原文。未来发布须先部署兼容旧读取的后端，再上传带提示的客户端；本轮没有部署/上传授权或动作。回滚标题代码恢复原120字写入合同，无需数据回滚。后端780通过/40个MySQL环境相关跳过、前端332、三视口39态原生和独立复核通过；当前源码预算1,221,025字节，非上传包体，见[本增量证据](../../quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)。实际键盘/系统字体/读屏与真机仍待验，Spec active/VERIFYING；下方数字保留各前序增量时点。

建议弹层已按[Refinement Spec01](../../../specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md)精简标题与操作层级，新增等待展示标识，无API/Schema/开关变化。[该增量证据](../../quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)包含311项前端和三视口45组原生节点/截图通过；不抵扣真实设备、内容适用及数据库门禁，也不产生新的云端/前端发布版本。本地未提交基线仍为main / `82ca52775bc948f2a963a8f4ed614322d8859de8`；小程序静态源码预算1216563字节，非上传包体。

迁移0023接生产0022，添加early机会槽/触发器与计划来源快照；0024添加可靠知识计时、建议/共享提示/Job、待学和实际记录关联。共享工作区后续0025属于年级确认任务，不能混作本功能迁移证据；本轮迁移测试明确停在0024。生产仍以既有发布记录中的0022/035为准，本轮没有改动生产数据或版本。

今日卡片按[Visibility Spec01](../../../specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md)/DREV03本地实现：无内容空区隐藏，实际标题与分区/复习卡/胶囊按钮统一，保留进度/恢复；无API/Schema/请求时序变化。前端327项与三视口81组原生通过，设备/可访问性与独立复核仍待补，见[当前增量证据](../../quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)。上段311项/45组及1,216,563字节属于DREV02历史检查；不能作为新卡片结果。未新增发布版本，仍NOT_UPLOADED/NOT_DEPLOYED。

未来启用顺序：先在真实MySQL5.7隔离环境验证迁移、并发和索引；核验内容样本、类目/隐私条件及iOS/Android主路径；依部署手册审批部署范围后迁移，等待全部后端兼容，再上传有empty-day-v1能力的客户端，最后分别启用两个开关。任何上传、体验、提审、正式发布须分别记录，不以本地原型或工具启动替代。

默认 `PUSH_KIDS_EMPTY_DAY_EARLY_REVIEW_ENABLED=false`、`PUSH_KIDS_LEARNING_SUGGESTIONS_ENABLED=false`。旧客户端不能物化或操作early计划，返回升级提示；旧后端404时客户端隐藏学习建议。迁移后的既有计划legacy_fixed不猜测曾否安排过，开关启用不强制重写今天旧计划。

回滚：先停新生成/审批和新的提前选题，等待在途Provider租约收敛，保留已存在early反馈与StudyTask实际记录接口。不要把新客户端直接切向不支持它们的旧后端。0023存在early快照时拒绝降级；0024存在批准Task时拒绝降级，正式记录不因移除建议而删除。需要清理时走已授权的owner清理流程，不能手工删表绕过保护。

原生验收只操作`/private/tmp/push-kids-today-learning-native-20261024`合成副本，拒绝业务写入，没有访问真实孩子或调用付费模型。未到实际发布人工门禁，因此没有要求用户执行控制台操作。
