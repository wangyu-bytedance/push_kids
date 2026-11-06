# BUG-036 Spec06 — Independent Review Report

- Reviewer: `/root/acceptance_review`，独立上下文、`code-review` Skill，只读；本文件由实现者按其原始审查消息整理，独立验证与实施者验证分列。
- Review date: 2026-11-05。
- Reviewed target: 未提交工作树本轮18个生产/测试路径，实施前start manifest与candidate02冻结源；唯一最终f-string拆行机械等价。
- Spec/version: [Spec06](../completed/BUG-036-SYSTEM-ONE-ACCEPTANCE.md)，`BUG-SPEC-20261105-SYSTEM-ONE-06 / ARCH-20261105-SYSTEM-ONE-06`。
- Affected Feature IDs/documents: FEAT-001，FEAT-004消费者只回归；FEAT-005既有归档语义不变。Feature14/BHV09/Architecture06/UI03/测试/发布与Spec、ISS/REG。
- Baseline: Git HEAD `0576ac30464908154c624effed41df6dfa3110cc`加已有并行修改；不是全部HEAD dirty diff。18路径前后SHA见[change manifest](bug036-systemone06-20261105/change-manifest.json)。
- Review mode / policy: read-only，REVIEW-20261028-01；没有修改文件、部署、发消息给外部人员或授予合并权限。
- Review round: 第一轮完整代码/必要性/调用链；第二轮修复增量；第三轮文档、机械格式增量和最终度量补核。同轮消息补核不新增第四轮全面审查。
- Version: candidate02 manifest SHA `349320d7078dbb059386cf3975b1f4c7bd3b6f56efd852fa3bf34f79d470883c`；18路径规范审查映射SHA `981ca0dff4bf60ccded9b54804ae4fa365857da667b31d060c3bd3f757e428ee`。最终验收模块SHA33b03729由Reviewer独立核对与冻结bb55797b AST全等，其余155源字节相同。
- Historical ISS/REG: match uncertainty缓存ISS、Spec05历史REG（现retired）；本轮三项ISS和当前[辅助验收REG](../../docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md)。

## 1. Verdict

**APPROVE（本地代码及当前事实文档范围）**，当前0个未解决已确认问题。原1项MAJOR、2项MINOR均fixed；D-01/D-02文档闭合残留已修正。Confidence: medium；90次生成和58回验指标均已独立逐项重算匹配，家长内容、原生/设备及云交付独立，不由代码审查宣布合格。

## 2. Reviewed scope

覆盖原Pro路由恢复、验收固定标准/静态提示与降级、HTTP边界/共享槽、Worker事务和迟到保护、公开提案/家长确认、旧覆盖/迁移兼容，以及相关测试与事实文档。未重新审查无关工作日/出行/提醒/前端并行diff；未独立执行全量/MySQL/原生或模型请求。

## 2.1 Modified file inventory and necessity audit

18项生产/测试逐文件add/modify/delete、必要性、理由及放置位置完整列于[EVD逐文件表](EVD-20261105-BUG036-SYSTEMONE06.md)，并由manifest绑定。全部necessary/correct，0 questionable/unnecessary/misplaced。删除旧workflow和近期池测试有退役依据；保留迁移链/旧覆盖确认有未证全库草稿清零的兼容依据，无未声明双权威生成路径。

| 文档文件 | 动作/必要性与放置理由 |
|---|---|
| docs/domain/features/FEAT-001-push-kids-mvp.md | modify，necessary/correct；合并当前生成/验收与兼容事实 |
| docs/domain/BEHAVIOR-CATALOG.md | modify，necessary/correct；032/032a统一启闭行为 |
| docs/architecture/ARCHITECTURE.md | modify，necessary/correct；移除旧可选路由，明确事务/资源所有权 |
| docs/design/frontend/ui/UI-001-parent-miniapp.md | modify，necessary/correct；既有提示/家长确认合同，无新前端实现 |
| docs/quality/TEST-STRATEGY.md | modify，necessary/correct；当前测试消费者和历史FAIL分开 |
| docs/deploy/README.md | modify，necessary/correct；本地版本与现有云交付区分 |
| docs/deploy/releases/20261105-system-one-local-verification.md | modify，necessary/correct；默认开关新语义/迁移兼容与发布缺项 |
| specs/README.md、specs/STATUS.md | modify，necessary/correct；批准、位置、12/109/19目录索引 |
| specs/completed/BUG-036-SYSTEM-ONE-ACCEPTANCE.md | modify，necessary/correct；具体批准及真实验收/术语勘误 |
| specs/active/BUG-036-SYSTEM-ONE-GENERATION.md → rejected同名 | move，necessary/correct；获批替代清退未交付实验，保留原FAIL |
| docs/quality/issues/README.md | modify，necessary/correct；当前ISS索引、独立Review状态 |
| docs/quality/issues/ISS-20261105-MATCH-UNCERTAINTY-CACHE.md | modify，necessary/correct；共享修复保留与当前REG/证据 |
| docs/quality/issues/ISS-20261105-ACCEPTANCE-DB-TRANSACTION.md | add，necessary/correct；记录R2-CR-001根因、失败和修复 |
| docs/quality/issues/ISS-20261105-ACCEPTANCE-HINT-GROUPING.md | add，necessary/correct；记录R2-CR-003及回归 |
| docs/quality/issues/ISS-20261105-ACCEPTANCE-ARCHIVE-TERMINOLOGY.md | add，necessary/correct；记录R2-CR-002权威语义和处置 |
| docs/quality/regressions/README.md | modify，necessary/correct；当前/退役消费者分开 |
| docs/quality/regressions/REG-20261105-SYSTEM-ONE-DECISIONS.md | modify，necessary/correct；retired并保留历史命令适用范围 |
| docs/quality/regressions/REG-20261105-SYSTEM-ONE-ACCEPTANCE.md | add，necessary/correct；当前可执行测试与失效控制 |
| specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md | add，necessary/correct；版本、失败、检查/模型与人工验收分列 |

安全生成工件由脚本/输入指纹及EVD说明，不逐行人工审查依赖缓存或未变历史数据；源码zip/manifest仍核对来源和版本。

## 3. Spec and behavior alignment

| 范围 | 实现与验证 | 状态 |
|---|---|---|
| TP01/02/06 | 固定阈值、原事实保留、静态提示、依赖降级、5秒/容量/流式响应/2槽 | PASS，独立单元/Worker59项 |
| TP03/04 | 真实Worker待确认、家长确认后才写；外呼无事务，scope/lease/attempt/状态竞争 | PASS，独立59项及根因探针 |
| TP05 | 原Pro生成；删除分类/近期40/关系/硬纠正，uncertain checkpoint修复保留 | PASS，代码/路由回归 |
| TP07/08/09 | 真实58验收、90生成、家长内容质量 | 90唯一执行/启闭45次及58唯一回验，全部统计独立重算匹配；人工PENDING |
| TP10 | 实施者988PASS/56SKIP与静态/Node/MySQL12项，保留SDK首败 | 原日志已核对，不冒充Reviewer执行 |
| TP11 | 既有原生提示交互 | NOT_RUN；无前端源码改动，不能由静态/API代验 |

Scope deviations: 无新增产品行为。R2-CR-002是归档/删除冻结术语勘误：FEAT-005/BHV-025和原Worker均明确归档允许已有分析收尾；Spec06原“归档阻断”误称已保留勘误理由并分测试，无需在多个合理产品语义间作新决定。未新增归档阻断，不静默扩大批准。

Feature current-state: FEAT-001正文已合并当前行为，旧05当前路由描述删除，历史FAIL保留。文档检查aligned：Feature/BHV/Architecture/API隐藏内部验收字段/UI既有uncertainties/测试/发布/Spec与兼容Owner、2026-11-12复查及全租户清零退出条件。旧家庭计数0不当作全库0。

Frontend impact/engineering impact: no；UI-001核对现有动态数据合同，DREV/FEC/新设计源/视口批准N/A；本轮原生与真机未执行。没有依靠HTML结果表替代小程序验收。

## 4. Findings

| ID | 严重性/来源 | 触发/证据与处置 | ISS |
|---|---|---|---|
| R2-CR-001 | MAJOR；新验收暴露既有Pro事务行为，且引入验收合同违反 | rollback过期ORM scope字段隐式重开事务；独立SQLAlchemy复现、真实Worker Red。完整改捕获标量，事务/迟到Green，fixed | ACCEPTANCE-DB-TRANSACTION |
| R2-CR-002 | MINOR；本Spec/新测试术语误标 | deleting=True误称归档；分实际归档/删除测试并勘误，既有合同不变，fixed | ACCEPTANCE-ARCHIVE-TERMINOLOGY |
| R2-CR-003 | MINOR；新增提示汇聚实现 | 同目标5个低分耗提示槽；按目标汇聚静态短语，内部findings保留；真实Red/Green，fixed | ACCEPTANCE-HINT-GROUPING |
| D-01 | MINOR；文档闭合残留 | Architecture/Behavior旧05启闭措辞、缓存ISS Review元数据残留；明确历史/当前，fixed | 同缓存ISS/EVD |
| D-02 | MINOR；REG阈值文案 | 漏列summary/coverage的0.95；正文精确列八标准，代码不改，fixed | 当前REG/EVD |

## 5. Deletion and duplication audit

原Pro是唯一生成权威路径，新增模块只有产物验收职责；无fallback/重生成/历史判定。删除decision_workflow、近期池查询/时间字段/实验DTO、Pro实验纠正阶段与专属测试。classify键仅清理旧缓存，旧decision_revision/review_state_version仅兼容既有草稿；原Pro legacy coverage生产者保持。保留0027迁移链和compat Owner/退出条件合理，无额外可安全删除项。

## 6. Correctness and risk audit

PASS：有效产物保留、边界验证、服务端既有scope、原状态机/事务/迟到写回、原幂等/取消/有限重试、外部故障降级、公开API兼容、隐私安全类别日志、资源上限、Feature事实合并。认证实现N/A（本轮未改）；旧认证不能被本审查升级为公共发布认证。Schema无新迁移，旧链/确认兼容另有实施者MySQL12项。云rollout/线上观察NOT_VERIFIED，不授予发布结论。

## 7. Test effectiveness and coding discipline

真实Red包括旧Worker不调用验收、事务事件下迟到状态写回失败、同目标提示未合并、响应超限未提前停止。读源码和真实状态/副作用断言可在坏实现下失败；未知异常降级本身不被误判为正确事务。阈值独立用固定0.95/0.90上下边界，未从实现常量计算期望。此前文件同名收集错误/编辑NameError/脚本round遮蔽不是行为Red；未将重跑当稳定通过。旧Pro恢复是批准的行为保持，不人为制造无关失败。

## 8. Architecture, placement and necessity

PASS：依赖DAG、agent_processing验收所有权、Provider纯协议、Worker事务/状态所有权、learning正式确认与planning确定性政策不变。没有新增通用框架、无Owner共享库、跨域直接写表、循环依赖或投机扩展。实现删多余旧权威路径，改动比例与获批清退相称。并行dirty tree未覆盖；实际18路径有前后SHA。格式修复与冻结源AST相同，提示文本不变。

## 9. Validation evidence

Reviewer独立执行：`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/unit/test_proposal_acceptance.py tests/unit/test_system_one_provider.py tests/unit/test_system_one_workflow.py tests/integration/test_worker_acceptance.py -q -p no:cacheprovider --basetemp=/private/tmp/push-kids-systemone06-readonly-review02-pytest`，59PASS/3.30秒，仅Starlette弃用warning。第一轮另30单元PASS，不替代最终59范围。

另尝试REG命令collect-only，SDK导入文件读取阶段长时间无输出，主动中止130；未执行测试，无PASS/FAIL声明。实施者全量988/56、MySQL12、Node359、Ruff/mypy及架构/设计检查在EVD分列，Reviewer只核对原日志/来源，不假称独立执行。

第三轮核对当前文档相对Markdown去fragment目标0断链，active12/completed109/rejected19一致。20文件中间快照SHA `ac80f69a9bd58638e80f9407e80b221e1228a510f34a37e630a213ffc0821b4c`（其EVD为dad89f3e）；后续真实度量/本报告为增量，最终哈希另记，不能沿用旧文档SHA证明新数字。

最终58回验独立重算和逐行标签判定匹配：58返回/事实保留、43旧产物35未报/8核对；known指定来源问题0/3、仅1/3触发separate；合成二分类/定位11/12，s06误报。Reviewer核对EVD/Spec/Feature/发布说明和表footer如实披露限制。summary SHA `416372fa31ade2c597256c9d77fe81b6aa53a3edc1e71d553c6e63d64921cd99`，rows SHA `fbb4727a7965a712f00a7b25b1f67da9c1a10c808d72c19e926ac9aaa5a9d589`，freeze SHA `fded1287fa4d5dd930ada09cae5988547b8baa790a459f313f804da44baf9013`。43旧产物没有人工gold，summary中binary_correct=0代表未评估汇总，不是0%正确率。

## 10. Residual risk and re-review

原生/真机、家长生成质量、其他可选MySQL及云观察尚未完成；检查器存在已知误报/漏报，no_finding不等于质量通过。真实90次最终数字已独立逐项重算匹配：on43/45、off42/45，43有效产物0丢失，全部首轮/attempt/p50/p95及失败阶段均无偏差。safe rows与私有原metrics全等，rows SHA `c412201f70813466507f5592bcd16bd7dec55e7ecf63d8bc714afc228e277dcd`，metrics SHA `21ad26fabcaa4580d68cb30fe0df1df366075751dba04a1b17164bdcb85b4544`。小样本重复15材料不能视为45个独立输入或线上成功率。旧草稿全库计数未授权/未证清零，按Owner/退出条件保留兼容。

必要文件/正确位置由上述逐文件表和EVD确认；0可疑/不必要/放错文件，无额外要求删除项。代码侧没有待修复MAJOR/BLOCKER；有行为和根因证据的正确性结论可通过本地Review，内容效果/真机/云交付仍无相应通过证据。达到默认第三轮后不自动全面重审第四轮；新产品代码或边界变化需新版本验证。
