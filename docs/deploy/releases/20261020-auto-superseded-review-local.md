# AI自动替代复习词条 — 本地状态

Spec：SPEC-20261020-AUTO-SUPERSEDED-REVIEW-02及DREV-20261020-SUPERSEDED-REVIEW-01均已批准，前后端已本地实现；无提交/部署/上传/体验/审核/正式发布操作。源码基线8f3c5b0及保留的既有工作区改动；未产生发布镜像、上传包或版本摘要。
迁移head：20261020_0022，接本地既有0021；先增量schema与queue v2，再部署全部理解状态的消费者。
PUSH_KIDS_COVERAGE_ENABLED默认true；false停止分析覆盖、存量处理及确认时新标记，不清除永久状态。
旧状态normal默认；迁移不调用AI。后台以持久游标发现存量，新确认同事务写任务，单任务3次/90秒租约/30秒模型预算。
schema回退在存在superseded时明确拒绝，避免旧后端重新排期；不得回退到忽略状态的消费者。
已替代词条保留历史，承接项删除不联动、不恢复。已有人工预约按原规则消费一次。
验证与缺失验收见[证据](../../quality/evidence/AUTO-SUPERSEDED-REVIEW-20261020.md)。
后端671 passed/35 MySQL条件跳过、前端265 passed；本功能隔离MySQL5.7专项13 passed，覆盖有状态拒绝回退、无状态安全回退及重升。生产Schema未变；仅隔离测试库演练0021→0022→0021→0022。存在永久状态时不得回退0021，开关false仅停止新标记。
剩余门槛：完整原生三视口/截图、iOS/Android与独立只读评审；后续发布需另按docs/deploy/README.md执行。本轮没有到达发布人工门禁。
