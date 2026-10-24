# 空白日复习与家长批准的学习建议

- Status: ACCEPTED / LOCAL_IMPLEMENTATION / RELEASE_GATES_OPEN
- Date: 2026-10-24
- Approved: 产品负责人「批准，按此实现」；两份Spec04、Architecture02/03和DREV-20261024-TODAY-LEARNING-01。
- Scope: [复习Spec](../../../specs/active/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md)、[建议Spec](../../../specs/active/FEAT-004-INCREMENTAL-LEARNING-PATH.md)。

复习只从已确认知识选择。planning的纯early_review政策固定3日窗口、80%原间隔、真实复习/安排冷却2日，首次复习不提前；确定性日期公式不变。迁移0023用每Review最多3条机会槽换取slot_on等值索引读取，避免大库存上扫描未来项。SQL与纯政策的边界有对照测试；显式early_projection提供scope内漂移检查和事务修复，普通GET不修复全表。自动queue_eligible_on等于due_date时是旧队列锚点；其他恢复日期仍为下限，任何家长预约都不提前。

DailyReviewPlan持久区分legacy_fixed/provisional_empty/fixed_due/fixed_early。旧计划一律固定；新暂空计划只在正式库存revision变化后重判，一旦选过任何内容即保持固定。early项保存原日期和状态版本，安排不改due/count；实际反馈才改变复习事实。客户端申明empty-day-v1能力，避免旧版误把未来项当作普通到期任务。

learning_suggestions独立拥有提案、共享提示、持久Job、待学及正式记录关联。knowledge拥有可靠新增日期和输入代次；learning继续独占正式确认写入权。独立的suggestion_provider消费严格DTO，不扩展原提取Agent的职责。年级与已学上下文有界，不收集生日，不推断掌握、成绩或必须学习的下一课。

审批只产生StudyTask。实际学习采用既有人工Submission确认，再通过稳定RecordIntent关联；确认成功但请求丢失由租约worker恢复。partial保留原Task；complete释放待学指针；删除后的晚到确认只保留审计。删除与可选再生成入队在同一Child事务内完成；入队先验证资源/资格，失败仍提交家长的删除，Provider失败不恢复旧待学。数据库事务自身失败返回失败供重试，不伪称删除成功。Family→Child→State/Job锁、共享日期唯一键、版本与请求唯一键控制并发；网络调用在事务外，租约90秒，最多3次尝试，额外受小时/日成本限制。

依赖方向：bootstrap/router → learning_suggestions → children/knowledge/learning只读合同/agent_processing合同；learning和planning不依赖learning_suggestions。data_management只调用owner purge。knowledge计时随原确认交易回滚，删除知识不抹去已经发生的新增日期。未确认且无正式事实的过期intent可清理；已批准Task/关联审计保留到家长清理。

替代方案：全量未来项Python过滤会破坏规模预算；每日保证有题会破坏间隔和家长日期；审批直接入档会伪造已学；前端Storage提示去重无法支持多人多设备。保守旧计划和首次观察两个完整自然日增加等待，但不根据缺失历史猜测“没有新增”。观察起始日可能不完整，不计入两个完整自然日。

默认两个开关均关闭。0023/0024先迁移，再部署兼容后端和能力客户端，验收后才能启用；回滚先停新生成，保留已批准待学的读取、删除、实际记录和early反馈。当前工作没有执行生产DDL、部署、上传或开关启用。验收缺口见[证据](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)。
