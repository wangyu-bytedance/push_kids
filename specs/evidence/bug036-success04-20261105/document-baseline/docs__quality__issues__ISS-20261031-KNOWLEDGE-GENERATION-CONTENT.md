---
id: "ISS-20261031-KNOWLEDGE-GENERATION-CONTENT"
type: issue
created: "2026-10-31"
updated: "2026-11-01"
status: open
source: test
owner: "Product owner / TRAE"
severity: MAJOR
disposition: confirmed
observed_revision: "staged-20261031-06/07/08/09"
source_evidence: "dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.md"
regression_case: "N/A: 真实来源30条评测尚未全部满足内容标准；不伪装active合成行为REG"
closure_evidence: NEEDS_VERIFICATION
observation_evidence: "N/A: 当前07/08/09增量未部署，零测试业务写入；09通知历史并发差异单独记录"
prevention_control: "固定同30来源、当前会话C1–C6、原PASS无回退、独立记录内部review和真实内容判定"
closure_reason: "内容验收实际失败，机制Green与输出数不能关闭本问题"
---

# 真实素材知识提案内容未全部达标

2026-11-01成功率诊断：当前12/15完整原40仍FAIL，33/40＝82.5%、三科60%/86.7%/86.7%，正式写0。
原六条10/13单次观察确认单来源needs_context整单早退、审查/命名导致数学省略；新zh-04/en-12复审失败同样保留。
[Spec04](../../../specs/active/BUG-036-FIXED40-SUCCESS-REPAIR.md)拟澄清技能证据边界、单来源核验和空结果终态，READY_FOR_REVIEW/未实施。
[诊断EVD](../../../specs/evidence/EVD-20261101-BUG036-FIXED40-DIAGNOSIS.md)只记录观察事实；原真实30、旧40失败与本次40不拼接，ISS仍open，未宣称质量修复。

2026-11-01缓存OPS灰度门禁新证据（独立于原真实30）：获批发布冻结10/13的固定40合成来源，
实际34/40＝85%，语文10/15、数学12/15、英语13/15，均未达发布要求，正式写0。
失败multi-01/zh-05/multi-02/zh-07/zh-09/multi-04及原attempts保留，
[门禁EVD](../../../specs/evidence/EVD-20261101-BUG036-CACHE02-RELEASE-GATE.md)与[报告](../evidence/bug036-cache02-release-20261101/live40-report.json)绑定。
发布在GRAY创建前停止，OPS BLOCKED/active、生产仍039；该结果不替换原真实30或独立内容Spec03的12/15验收，不重复抽样以覆盖FAIL，ISS保持open。

## Impact and reproduction

- FEAT-001默认知识生成：充分素材仍可能质量拒绝；有输出也可能粒度、对象范围、普通场景和字形错误。
- 固定原30source digest、68原图、同Doubao模型/参数、2case并发、一来源一次完整尝试；生成无DB/Worker/checkpoint，前后READ ONLY审计61表。原失败和各revision分开保留。
- 当前会话逐条核对原素材，以C1–C6判完整提案；内部passed及正确拒绝都不等于生成严格通过。
- 首轮07：24输出、13严格PASS、10FAIL、1PARTIAL、5NO_OUTPUT、1INSUFFICIENT_MATERIAL。case02摘要错数的初判修正有记录；原PASS case25字母遗漏回退。
- 既有08：25输出、原报告9严格PASS、16FAIL、4NO_OUTPUT、1材料不足，原PASS18/25回退。当前会话另一次08：20输出、C1–C6内容12PASS、完整11PASS，61表一致。两次运行独立保留，不以25输出覆盖20输出失败。
- 当前09/13：26输出、C1–C6内容12PASS、含输出合同完整10PASS/15FAIL/1待核对/3无提案/1材料不足，原13无输出12恢复。原PASS18摘要误扩书写范围、25将I认成汉字一并遗漏英语I，仍回退。六个holdout5PASS/1FAIL，cat/dog书写因缺音频错误拒绝。09为60/61表指纹一致，通知38→37的并发来源未证明；测试写入仍为0。真实清理独立记录，旧173文件清理不代替本轮。

## Root cause and escaped controls

- 观察到同域/同目标仍拆碎、题型/场景残留、对象泛化或遗漏、错误高置信字形及跨科目插图推断。
- Review和生成消费相同模型/规则，可能共同误判；确定性schema、预算和省略账本只能控制输出形状/覆盖归属，不证明视觉忠实和语义粒度。
- 历史09/13对教学区、未圈选词表和共享成员审查补充通用规则，生产DTO/预算不变；仍发生分合反转、视觉高置信错误、同词跨页重复与历史坏名称accept。该历史版本的审查只有候选概括/材料编号，没有原图或完整excerpt。来源可见性与证据owner缺口由已批准内容Spec03在本地11/14接入，12/15继续修正局部边界；实际质量改善仍须看对应新版本固定素材结果。
- 机制根因另在[ISS](ISS-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md)；不能把真实素材尚未通过的问题混记为机制已永久解决。每个质量拒绝的具体模型成因仍有随机性，不以一次重跑推定全部根因。

## Fix and verification

- 2026-11-01用户已明确“修复全部未通过样本”，并批准[内容Spec03 / Architecture03 / Prompt05](../../../specs/active/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)。本地12/15接入原图/完整摘要审查、正式证据owner和限定纠正；两项Review缺陷经诚实2FAIL/1PASS后修复，166专项/896全量PASS、52条件skip，第二轮0新确认问题。11诊断仅2/8产出，不替换最终12结果。最终原30为20产出/10内容PASS/9严格PASS＋1正确缺材料拒绝，10FAIL/9NO_PROPOSAL/1家长核对，原六PASS回退3；补充0/3、边界7/10严格通过，内容FAIL。超时、受保护纠正漂移、规则/对象命名、字形/备注归类和摘要合同仍失败；[逐条报告](../../../specs/evidence/bug036-content03-20261101/evaluation-12.md)及[12 EVD](../../../specs/evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)保留。资源及51/61表审计PARTIAL、外部写入归因未证，缓存02政策保持，无部署，ISS仍open。
- 已批准BUG-036 Spec01 / Architecture01 / Prompt04。本地staged07修复确定性机制，08/09在相同批准规则内细化；未扩大调用/缓存预算或放松标准。09新证据前提实验预算已按Spec用完，不继续无界改提示/重跑。
- [首轮报告](../../../dist/knowledge-generation-evaluation-20261031-prompt04/revision07/evaluation-30.md)保留；08末轮结果由同Spec/EVD追加。
- [当前会话多轮报告](../../../dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.md)和[09EVD](../../../specs/evidence/EVD-20261031-BUG036-PROMPT09.md)保留独立内容/输出合同判断、每轮失败、源SHA与60/61审计差异。109专项/独立71/全量832pass不关闭内容问题。
- 不做生产数据清理、取消Review、模型答题/判掌握或未覆盖材料的半成品发布。手动录入与家长确认保持。
- 后续修复须对照具体失败形成可审阅revision；若改变批准规则/流程/预算，先批准对应Spec，不借此ISS静默扩展。

## Closure and recurrence

open：仍未达到AC-008，Owner在下次该域迭代/发布前逐条复查；先满足固定分母、原PASS不回退及真实素材充分项内容正确，再讨论关闭。当前cloud delivery不是本地内容通过证据。
