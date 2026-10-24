# 学习建议弹层精简 — 本地实现证据

- Date: 2026-10-24
- State: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED / NOT_DEPLOYED。
- Approval: 产品负责人针对明确列出的[Spec01](../../../specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md)及[DREV02](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md)回复「批准，按此实现」（call_989b0367f519481a9dc9b890f5ae9f1b）。先记录APPROVED再改原组件。
- Workspace: main / `82ca52775bc948f2a963a8f4ed614322d8859de8`，共享未提交工作区；保留其他会话改动，无提交或推送。

直接以具体学习标题作为弹层标题，科目/预计时间和简短AI标识紧随其后，删除原口号式头部及重复标题。确认全宽；编辑/换项等宽浅底边框，44px高、8px间隔；暂缓全宽居中弱化；图标关闭44px。沿用已有tokens、事件、事务与幂等；JS只增加busyAction展示标识。确认中显示“正在加入…”，禁用全组和关闭，失败保留提案/错误与重试键。无新资源、依赖、请求、接口或数据模型。

完整标题上限120字。≤60字正常换行；更长标题和元信息在30vh区域纵向滚动，关闭位于区外，正文独立滚动，底部动作固定。430视口的120字样本能完整容纳，因此不要求无意义滚动；320/390样本实际scrollTop>0。没有省略文本或靠横向隐藏通过检查。

| 实际执行 | 结果与范围 |
|---|---|
| `npm test` | 311 passed / 0 failed / 0 skipped，1832.76ms；日志`/tmp/push-kids-sheet-refinement-frontend.log`。共享工作区计数包含当时其他会话测试，不将它们作为本功能专项 |
| `node --test tests/frontend/today-learning.test.js` | 9 passed / 0 failed / 0 skipped。新增异步审批用例覆盖等待中禁止重复/关闭、失败保留提案与错误、同幂等键重试成功；原权限、迟到、轮询及真实记录恢复回归通过 |
| `npm run lint:miniapp` | PASS，日志`/tmp/push-kids-sheet-refinement-eslint.log` |
| `tools/validate_miniprogram.py` | PASS：17页、1216563源码字节，小于1.5MiB；该数值是静态源码预算，并非上传包体 |
| `tools/check_architecture.py` | PASS：policies=4、modules=150，runtime/lazy DAG |
| Ruff check及format --check | PASS：`tools/prepare_today_learning_native.py`及DREV02 `render.py`，2 files already formatted |
| 新批准设计/当前政策校验 | PASS：`validate_design_evidence.py --manifest .../DREV-20261024-TODAY-LEARNING-02/APPROVAL.md --check-current-policy`返回DESIGN_EVIDENCE_VALID；HTML/84PNG/SHA不变 |
| 旧批准设计校验 | PASS：DREV01 APPROVAL.md返回DESIGN_EVIDENCE_VALID；78PNG/源SHA不变，只增加本次范围的Superseded by指针 |
| 原生15态×3 | PASS：45份节点JSON+45PNG，320×568/DPR2、390×844/DPR3、430×932/DPR3，默认字体15，基础库3.17.4。工具/矩阵/源与截图SHA见[原生证据](suggestion-sheet-refinement-20261024/native/README.md) |
| 文档链接、原生SHA/源码核对、diff空白 | PASS：15份文档相对链接0缺失、围栏/尾部空白检查通过；45态完整、90份JSON/PNG的SHA及生产源指纹核验通过；Spec为active/VERIFYING且无completed副本；`git diff --check`退出0；采集JS的`node --check`通过 |

原生操作限定`/private/tmp/push-kids-today-learning-native-20261024`离线合成副本。只读API拒绝所有业务写入；无真实孩子资料、后端/模型调用或付费生成。原生截图与节点共同检查44px控件、关闭位置、两列等宽/8px间隔、全宽主确认/暂缓、14px文字下限、零横向位移、正文与footer分离、长标题完整可见或实际滚动。目视检查320主态和120字滚动末端、430等待态；未用HTML截图代替原生节点。

曾遇到Mac锁屏及三个会话共用开发者工具窗口，最终在用户授权协调暂停其他两会话后完成取证；已向“获取照片拍摄时间”和“新增每年9月1日年级升阶”各发送恢复通知。一次390截图超时未完成的运行不算PASS，最终15态已覆盖重采。430最长标题初次断言误要求必须滚动；实际内容已全部容纳，修正为“完整可见或实际滚动”后重采通过，未改生产代码或放宽尺寸/遮挡要求。测试工具前后指纹保留于核验清单。

| 文档闭环 | 核对结果 |
|---|---|
| FEAT-004/current Feature索引 | revision05-LOCAL，替换待批准候选为批准后本地实现；领域规则、默认关闭和未发布保持一致 |
| UI-001/Frontend Design/Design02 Spec | 当前弹层与45组原生事实同步；区分84张批准原型、原生合成截图与真机；DREV01/02批准源保持冻结 |
| BHV-045 | 更新呈现证据引用，无领域/状态/写入合同变化 |
| Architecture/ADR | 按实际文件核对，无模块边界、依赖方向、共享抽象或扩展点变化，无须更改架构正文；150模块DAG通过 |
| Spec/索引 | 精简Spec01为active/VERIFYING；主Spec04只同步后续原生证据范围，仍VERIFYING；没有把未齐门禁的Spec迁为DONE |
| 测试策略及两阶段证据 | 增加最大长度与原生取证边界；设计阶段旧NOT_RUN标成历史，当前实现结果单列；不复用主功能760/295历史数字证明本修订 |
| 发布记录 | 增加已批准本地弹层增量，无新Schema/API/开关或已发布版本；生产0022/035沿用既有发布记录 |

以上当前正文与本次代码没有已知冲突，其他会话事实保留。后端全量、mypy及真实MySQL/模型未为此次纯呈现增量重跑，因为没有后端/SQL变动；主Spec04的真实MySQL5.7、内容适用、类目/隐私及独立实现Review等门禁仍保留。代表iOS/Android、实际键盘、读屏和系统大字体NOT_RUN；合成setter状态取证不能证明真实请求端到端或设备辅助功能。本次实现后独立只读复核尚未执行，自查不冒充独立评审。

Spec最终状态为VERIFYING，位置`specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md`。恢复条件为补齐设备、可访问性及独立复核证据，再评估DONE/迁移；无需重新批准已批准的Spec01/DREV02。两个业务开关仍默认false，没有上传、体验、提审或正式发布。
