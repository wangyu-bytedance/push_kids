# OPS-20261031 — 测试维护独立只读复核

- Reviewer: TRAE，实施后新上下文
- Date: 2026-10-31
- Target: `0576ac30464908154c624effed41df6dfa3110cc`＋单个测试diff；最终测试SHA `b7ed69c1f4d060311f679f61474322ceb561281bbda7de32e6c97be54ed5acbd`
- Spec: [SPEC-20261031-RELEASE-STAGE-CACHE-TEST-01](../../../../../../specs/completed/OPS-20261031-RELEASE-STAGE-CACHE-TEST-MAINTENANCE.md)
- Policy: [REVIEW-20261028-01](../../../../../../REVIEW.md)
- Round: 1；read-only。本复核未重跑套件，直接核对已运行原始日志、精确候选源码和diff。
- Feature: FEAT-001；FEAT-012仅为后续发布对象。BUG-036不在复核或部署范围。
- Applicable ISS/REG: 无新增生产缺陷；原缓存数量不一致由本Spec和原实库FAIL追踪。

## Verdict

0 confirmed findings；测试修订APPROVE，置信度high。该结论仅覆盖维护范围，不是前端上传或039完整云验收批准。

## File necessity, placement and deletion

| 文件 | 必要性与位置 | 冗余/误改 |
|---|---|---|
| `tests/integration/test_staged_mysql.py` | 必要；既有真实MySQL恢复测试拥有缓存、重试和索引合同 | 仅改原函数；原锁顺序测试不变，无平行用例、skip或生产改动 |
| Spec、测试/发布证据及受影响当前文档 | 必要；保留批准、Baseline/Green、实际阶段和生命周期 | 只归并已验证事实；批准设计源/快照保持 |

选择精确身份及调用次数比放宽数量或删quality阶段更符合已批准Spec03。
未新增模块、共享抽象、依赖方向、事务、API或Schema；无旧代码共存和新增dead path。

## Spec alignment and test effectiveness

| 要求 | 源码与有效失败条件 | 已运行证据 | 结论 |
|---|---|---|---|
| AC-001 | 固定候选pipeline明确`review_quality(..., unit="review0")`；断言恰有`t/merge/review0`及相同family/child/submission/job，遗漏、额外或错误归属会失败 | [focused最终日志](round02/focused-staged-mysql-green.log) | PASS |
| AC-002 | StageFake按实际stage计数；恢复若重复extract/merge/review或不重试matching会失败；最终状态及0缓存仍为原断言 | 同上及[staged矩阵日志](round02/mysql57-isolated-staged_mysql.log) | PASS |
| AC-003 | 原真实MySQL索引possible_keys检查、锁顺序用例及pending_confirmation边界保留；possible_keys不冒充足迹实际索引计划 | [实库矩阵](round02/mysql57-isolated-matrix.json)及[规模日志](round02/approved-footprints-scale.log) | PASS |
| TP03 | 最终测试注入精确候选，154后端/168前端摘要匹配 | [完整789/46](round02/full-backend-sqlite-attempt02.log)、[payload](round02/resume-payload-audit.json) | PASS |

期望来自此前已批准的extraction→merge→quality review→matching合同；原断言2的FAIL_BASELINE是测试合同滞后，不能称为生产Red。
首轮format FAIL不是行为Red，最终只改换行，第二轮行为及格式均通过。
实际MySQL/Worker/checkpoint接线，无真实模型、儿童内容、生产数据或凭据输出。覆盖率按技能条件SKIPPED，不构成覆盖率达标声明。

## Correctness, architecture and scope audit

缓存归属、queued重试、attempt计数、成功终态/清理及provider失败恢复PASS；
原事务锁顺序有两项实库中的专门用例。模块、依赖、扩展点、API、Schema、权限和日志无运行时变化。
检查测试diff未发现不必要格式化或范围扩张。部署白名单只包含038加批准的足迹reads/router，不含测试和BUG-036。

## Documentation and release limits

Feature、Behavior、Architecture、UI、Spec和发布文档的旧“待批准/测试FAIL/未创建后端”正文由获授权闭合工作替换；
早期日志与报告明确标为历史。最终链接、SHA和生命周期另见[闭合检查](../../approved-delivery-closure.json)。

039 normal是启动/部署证据；部署前独立实际CRUD账号校验未补齐，后续本地探针OperationalError，
不能追认该门禁或定向ready通过。部署前服务live/ready200不证明039响应。
390/430原生、设备、完整动作及新focus双账号/非owner仍未验；前端upload、体验、审核和正式发布均未执行。
后续需完成定向灰度和适用上传门禁；无需因本测试修订重复未变源码的已通过检查。

Reviewer sign-off: 测试维护批准范围无确认发现；发布范围继续遵守上述证据限制。
