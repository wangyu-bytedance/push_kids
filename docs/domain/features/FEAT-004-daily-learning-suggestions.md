# FEAT-004 — 单项增量学习建议

- Status: BACKEND_037_NORMAL_100_PERCENT / CLIENT_LOCAL / VERIFYING / DEFAULT_OFF / FEATURE_NOT_ENABLED
- Revision: FEAT-STATE-20261024-INCREMENTAL-LEARNING-09-DEPLOY
- Current title constraint: 用户明确批准[Title Limit Spec01 / Architecture01](../../../specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md)与[DREV04](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/FRONTEND-SPEC.md)，已本地实现，VERIFYING。新生成/重新编辑标题trim后1–20个Unicode码点，无内部换行；编辑计数/错误就地显示，超限保留草稿、零PATCH。旧21–120字提案/任务保留原文和读取/审批/实际记录/删除路径，重新编辑须主动精简。后端780通过/40个MySQL环境相关跳过、前端332通过、三视口39态原生及独立复核通过，真实设备/可访问性待补；见[当前证据](../../quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)。33张批准设计导出冻结，不代替原生结果。
- Current card refinement: [Visibility Spec01](../../../specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md)/[DREV03](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md)获用户「批准，按此实现」，已在原组件实现。空区整体隐藏，具体内容沿用今日分区/复习卡字阶与胶囊按钮；保留生成/失败恢复与批准待学。前端327项及320/390/430三视口81组原生通过；真实设备/可访问性及独立复核待补，详见[本轮证据](../../quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)。该卡片范围未改领域合同、DREV02弹层和默认开关；当前标题写入合同另由DREV04覆盖。
- Updated: 2026-10-24
- Spec / Architecture / Design: [Spec04](../../../specs/active/FEAT-004-INCREMENTAL-LEARNING-PATH.md)、ARCH-20261024-INCREMENTAL-LEARNING-PATH-03、[Design01](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-01/FRONTEND-SPEC.md)，产品负责人已明确批准实施。
- Evidence: [当前验证与缺口](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)。2026-09-05历史提案继续REJECTED，不代表本次被取消。
- Current UI refinement: 用户已批准[弹层Spec01](../../../specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md) / [Design02](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md)，现为本地实现/VERIFYING。建议弹层直接突出标题、科目/时长和简短AI标识；主确认全宽、编辑/换项等宽并排、暂缓居中。等待禁操作，失败保留提案并沿用幂等键；长标题完整可滚动。[本轮证据](../../quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)：311项前端及三视口45组原生几何通过，真机/可访问性未验；领域行为与主Spec04状态不变。

服务端按北京时间判断：可靠计时覆盖前两个完整自然日，期间及今天没有首次确认的新知识，且孩子有年级、启用的学习科目和至少一项可用已确认知识，才允许自动建议。首次计时当天不算完整观察日；历史补录新知识计在确认日。重复知识、复习、活动和草稿不重置新增日期，删除也不擦除日期。

AI只给一项可编辑提案，展示具体活动、真实知识来源、衔接理由和不确定性。年级是参考，不代表掌握定位；不生成成绩、掌握结论、必须学习的下一课或复习日期。知识抽样最多20条、启用科目最多30、先前采纳摘要最多6条，上下文24KiB；不发送照片、姓名或生日。

标题仅概括活动动作/对象，prompt建议6–16字、硬上限20码点，详细步骤在instructions、理由在rationale。agent_processing拥有统一标题合同，输出验证与持久化前再验证、PATCH Edit共同消费；无效生成沿用既有最多3次尝试，不新增模型修复调用。编辑计数按trim后码点，非BMP字符计1；原生maxlength=120只作输入防护及历史编辑承载，20才是有效保存上限。服务端拒绝无效标题返回422且JSON/version/任务/正式事实不变。历史内容不迁移或裁切，超过60字仍沿用完整标题滚动。

每家庭/孩子/自然日共享一次自动弹出资格，先持久消费再返回；丢响应、丢ack不释放。今天先不学保留同项，次日仍合资格且未失效时复用。审批前可主动换一项，排除刚换内容；已有待学先删除再生成，新建议必须再次批准。失败可重试；无合适的不同内容时不伪造替代。小时/日生成尝试有限额，与孩子学习分钟预算无关。

manager/editor确认后只创建一项待学，不创建LearningRecord、Knowledge或Review。待学跨日保留，没有逾期债务或10分钟上限。家长记录实际内容和发生时间，照片可省略；部分学习只记录部分，原待学继续；明确完成并成功确认真实内容才结束。稳定intent和幂等提交键允许恢复确认成功但关联失败的请求。删除后的晚到记录仅关联审计，不复活任务。

今日组件保持挂载，内容区域位于hero后、复习前。无内容/进行中或恢复操作时不渲染标题、卡片或额外间距；eligible纯空快照也隐藏，但既有自动提示继续执行。有提案直接显示具体标题及元信息；Task优先且不受生成开关/资格误隐藏。生成中、失败/失效和删除后恢复保留入口，请求错误保留重试。已确认学习统计仍只消费正式记录。viewer只读已批准待学，未批准提案/生成空区隐藏，不触发生成或审批。切孩子、家庭、成员/角色或离页后丢弃迟到结果，轮询最多8次。普通GET不调用模型。

`PUSH_KIDS_LEARNING_SUGGESTIONS_ENABLED=false`为默认。关闭新生成和审批时仍保留已批准待学读取、删除和实际记录。0024已随生产0025落库，知识计时从迁移日起初始化；获批CRUD readiness修复后的037 normal/100%，当前建议GET真实微信200，开关仍关闭。真实MySQL5.7迁移/新查询规模和相关今日回归通过；真实模型分层样本、iOS/Android及实际类目/隐私/内容义务验收仍须单独完成，不能由mock或家长确认代替。前端未上传/体验/审核，建议未启用。[本轮发布记录](../../deploy/releases/20261024-latest-backend-test-deployment.md)描述实际阶段，036保留为旧失败。
