# Issue Learning Records

Owner：项目维护者。人工检查、AI Review、验收/测试、用户反馈、安全检查及线上
故障的可行动问题使用稳定ISS ID，从[问题模板](ISSUE-TEMPLATE.md)创建。
已有工单、历史Spec和 `docs/quality/evidence/` 继续作为来源；这里只存脱敏摘要、
根因、版本和防复发链接，不复制工单/事故/发布台账。

## Capture and retrieval

当前发布验证两项测试ISS已本地resolved：[SDK字节测试deadline](ISS-20261105-SDK-BYTE-TEST-DEADLINE.md)、[MySQL旧head断言](ISS-20261105-MYSQL-HEAD-ASSERTION.md)，批准OPS01后988/48及独立Review通过，不将原失败改标或视为已发布。[固定40材料/科目期望冲突](ISS-20261105-FIXED40-SUBJECT-TRUTH.md)在Spec07获批后新增v2唯一词汇补充，独立材料Review与完整单轮40/40通过，记本地resolved；原40/37FAIL保持，生产未变，内容review及其余发布门禁仍独立。

当前辅助验收边界：事务[ISS](ISS-20261105-ACCEPTANCE-DB-TRANSACTION.md)、同目标提示[ISS](ISS-20261105-ACCEPTANCE-HINT-GROUPING.md)、归档术语[ISS](ISS-20261105-ACCEPTANCE-ARCHIVE-TERMINOLOGY.md)。获批Spec06本地修复及独立复核，关联可执行[REG](../regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md)；未云交付，不将线上观察改PASS。

当前缓存问题：[ISS-20261101-FINAL-REFUSAL-CACHE-RETRY](ISS-20261101-FINAL-REFUSAL-CACHE-RETRY.md)记录生产失败来源、本地确定性Red及获批Spec02的终态/明确retry恢复；本地resolved、未部署观察，不能closed。内容失败沿既有内容ISS独立跟踪。

- Discovery/Review按Feature、模块及失效类别检索本目录和[REG](../regressions/README.md)，
  选择相关测试进入Spec required test points，不加载全部历史。
- 记录发生了什么、因果链、应拦截层、漏检原因、修复Spec、真实测试、REG/EVD和
  最靠近根因的控制。复发保留版本/次数并关联原ID，根因不同则另建。
- 紧急问题按已有授权先止损再补档；无授权不能借问题记录扩大操作权限。
- 文档语义歧义使用[专项模板](DOC-AMBIGUITY-TEMPLATE.md)，提问前备齐原/新来源
  和推荐方案，按根[REVIEW](../../../REVIEW.md)第7节执行；不新建平行裁决台账。

## Lifecycle and closure

`open → triaged → fixing → resolved → closed`；`mitigated`只表示止损。
无法继续时保留真实状态、Owner、阻碍及复查日期。

- disposition：unresolved / confirmed / false_positive / intentional / duplicate。
- resolved说明修复已验证，不代表已发布或长期防复发完成。
- closed+confirmed需关联active REG、真实关闭EVD、防复发控制和适用上线观察。
  修复及规则修改仍需Spec批准；测试本身可作为控制，不为闭环制造额外流程。
- false_positive/intentional/duplicate需理由及证据；重复项指向原问题，有害误报
  可进入审查器负例，不能靠关闭重复项掩盖根因。
- 文档裁决的decision_status独立为pending/answered/applied/verified；answered不
  算应用，verified后仍须通用关闭条件。契约/版本改变需重核裁决适用性。
- 未知项用NEEDS_VERIFICATION，不能把未复现写已修复。秘密、儿童数据及原始
  生产载荷不入库。机器只查字段/路径/状态，不能证明远程来源或语义正确。

模板建立时未批量追认历史问题关闭或制造事故记录；后续实例按真实来源追加。旧Spec状态保持原样；
GOV-002开发DONE与ISS是否closed是独立维度。

## Current records

- [学习记录索引漂移](ISS-20261105-LEARNING-RECORD-INDEX-DRIFT.md)：工作日任务全库Alembic check发现，隔离0025/0026同样四个旧索引差异；triaged，未修复，工作日两表无新增漂移不等于全库门禁通过。

- [匹配不确定缓存空转](ISS-20261105-MATCH-UNCERTAINTY-CACHE.md)：成功率Spec04真实回放与无模型探针确认；获批Spec05本地修复，Spec06保留并完成独立代码复核，云观察未完成，triaged/open；不将机制测试PASS或停止重试当产出成功。
- [素材局部纠正来源](ISS-20261101-AUDITED-SOURCE-CORRECTION-SCOPE.md)和[实际请求字节](ISS-20261101-REQUEST-BODY-BYTE-ACCOUNTING.md)：内容Spec03独立Review发现，12/15本地resolved；真实Red/Green与既有active机制REG相连，未云观察/未closed。
- [知识生成机制](ISS-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md)：resolved-local，关联真实Red/Green与active REG；不代表内容验收或部署。
- [知识生成内容](ISS-20261031-KNOWLEDGE-GENERATION-CONTENT.md)：open，固定真实素材评测失败保留。
- [Review重试上限](ISS-20261031-REVIEW-STAGE-RETRY-BOUND.md)：历史Spec02证据，当前review/reuse仍每位置一次。
