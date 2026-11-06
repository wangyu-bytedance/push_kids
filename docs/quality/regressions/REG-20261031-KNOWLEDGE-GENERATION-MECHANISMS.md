---
id: "REG-20261031-KNOWLEDGE-GENERATION-MECHANISMS"
type: regression
created: "2026-10-31"
updated: "2026-11-01"
status: active
kind: behavior
owner: TRAE
issue: "docs/quality/issues/ISS-20261031-KNOWLEDGE-GENERATION-MECHANISMS.md"
bad_revision: "approval-time staged-20261031-06 and BUG036 Review01 snapshots"
fixed_revision: "staged-20261031-07/08/09; source ownership and transport counters in staged-20261101-12"
test_path: "tests/unit/test_staged_proposal_recovery.py"
command: "UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync pytest tests/unit/test_staged_analysis.py tests/unit/test_staged_proposal_recovery.py tests/unit/test_stage_provider.py tests/unit/test_provider_evidence.py tests/integration/test_analysis_checkpoints.py -q"
red_evidence: "specs/evidence/EVD-20261031-BUG036-IMPLEMENTATION.md"
green_evidence: "specs/evidence/EVD-20261031-BUG036-PROMPT09.md"
reviewer_fixture: "N/A: behavior-only；安全源码快照在specs/evidence/bug036-20261031/snapshot-manifest.json"
reviewer_evidence: "N/A: 不是审查器识别能力评测"
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# 知识生成机制重放契约

## Contract and behavior regression

- FEAT-001；完整候选账本、同编号纠正、历史严格复用、结构恢复、执行预算与18/33调用及18缓存键；MAJOR。
- 现有tests中合成文字、Provider和内存SQLite，不连接生产库；临时测试资源由fixture清理。不生成正式学习或复习事实。
- 验证合法候选保留、无证据省略、全省略拒绝、无关成员不漂移；结构第二次失败终止；queue/deadline取消释放；accept复用、reject/null保留当前目标、uncertain拒绝；同名不得旁路。
- 容量含合法跨科目360身份、20查询/100历史/512KiB、18缓存命中0Provider调用与第19键拒绝；任意未知模型字段不进入日志。

| 阶段 | 精确命令 / 对象 | 实际结果 | EVD |
|---|---|---|---|
| 首次Red | `pytest tests/unit/test_staged_analysis.py -k 'single_material_schema_failure or leaves_request_queue or unsupported_candidate_is_accounted or uses_review_alias' -q`；批准时旧实现 | 4项目标失败，分两次各2fail观察 | implementation EVD |
| Green | 同4条合并选择器 | 4pass | implementation EVD |
| 保存旧实现回放 | EVD中的baseline_override精确命令；冻结旧实现+兼容新DTO | 10个行为失败；发生于实施之后，明确不是事前TDD Red | implementation EVD |
| Review01 Red | EVD中的same_name/new_global_option_cap/numeric_unknown/worker_preserves/requires_actionable_names选择器 | 8fail，修复后同8条pass | implementation EVD |
| 集成边界07/08 | 上述command及完整backend suite | 各版本832pass/46条件skip，资源/身份/ledger邻界通过 | implementation EVD及review03/full-suite |
| 当前09/13 | 109项专项和完整backend suite | 832pass/46条件skip，独立71pass；语义holdout03FAIL另记内容ISS，不退役已通过机制REG | EVD-20261031-BUG036-PROMPT09 |

坏/修复源码和适用tests的不可变安全文本快照由[snapshot manifest](../../../specs/evidence/bug036-20261031/snapshot-manifest.json)关联；扩展名`.py.txt`避免变成第二套生产模块。重放时在私有目录还原`.py`，按EVD的模块覆盖命令执行；源码hash须与manifest相同。审批时没有的新测试使用修复tests，不能把不存在的旧tests算Red。

## Content03 source and correction increment

当前12/15在同一现有测试owner补充原图/完整输出、独立正式证据与置信度、空候选、
素材账本与q/素材/i/o授权边界，继承缓存02终态政策。11/14及批准基线保留于
[旧manifest](../../../specs/evidence/bug036-content03-20261101/manifest.json)，
12及对应增量保留于[新manifest](../../../specs/evidence/bug036-content03-20261101/candidate12/manifest.json)。
不改写历史07/08/09的Red/Green。

新增[素材纠正ISS](../issues/ISS-20261101-AUDITED-SOURCE-CORRECTION-SCOPE.md)和
[字节计数ISS](../issues/ISS-20261101-REQUEST-BODY-BYTE-ACCOUNTING.md)分别记录不同根因，
均resolved-local，未取得上线观察。

| 新回归 | 可失败证据与独立期望 | 当前结果 |
|---|---|---|
| candidate素材纠正后以正式evidence归属限制局部纠正 | `test_material_correction_uses_audited_source_after_candidate_attribution_changes`；原素材账本可修，但不得改另一素材已审查目标，历史查询前拒绝 | 修复前越界未raise，修复后正/负两路径PASS |
| HTTP运输字节精确计数 | `test_request_bytes_match_real_sdk_transport_body`；真实SDK+本地MockTransport、中文/图片输入，等于实际request.content长度 | 修复前1179≠1070；修复后PASS，内容不进入计数日志 |
| 原来源/证据/账本/容量/终态邻界 | 既有command，当前12/15 | 166专项PASS；896全量PASS/52条件skip，实际12 EVD |

[12验收EVD](../../../specs/evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)保存2FAIL/1PASS首败、
166Green、独立Review和真实素材结果。机制PASS不关闭内容ISS；
固定原30严格9PASS＋1正确拒绝、补充0/3、边界7/10，内容FAIL；原六PASS回退3。
语义纠正漂移被拒绝不代表充分材料成功，51/61表审计和实际资源PARTIAL。
精确64KiB存储、同步SHA/取消、MySQL/Worker/云/设备未验项分别保留。
本轮没有配置自动CI或定时回放。

## Reviewer evaluation（历史和当前限制）

N/A：本案例只证明行为防复发。已执行的独立Review01/02及跨组审查是修复证据，不作为审查器能力通过率，也不伪造模型、费用或人工标签。资料在[review retention](../../../specs/evidence/bug036-20261031/reviews/group/cross-review-audit.md)。

## Lifecycle decisions

active：已有真实Red/Green且纳入BUG-036 required验证；未配置新定时或CI任务，不声称持续回放已上线。当前标签分类PARTIAL单列于EVD；真实模型内容另立问题，不能因内容失败退役机制回归。
