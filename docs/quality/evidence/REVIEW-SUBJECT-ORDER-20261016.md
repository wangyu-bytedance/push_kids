# BUG-029 — 复习反馈后科目保序验证

- Date: 2026-10-16
- Spec: [`BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01`](../../../specs/active/BUG-029-REVIEW-SUBJECT-ORDER.md)，用户明确批准实现、Git提交与部署。
- Baseline: `8b933dae762f6dbdb1bb9c2286155106b0a5fdc6`。
- Local implementation verified；不以本地通过或旧后端030的生产smoke表示本修复已上线。

## 根因与修复

原日计划读取按ordinal稳定，但daily_review_selection先过滤非pending行，再根据首次剩余项建立科目组。交错计划`语文1、数学1、英语1、语文2、数学2、英语2`完成语文1后，首次遇到的剩余科目变为数学，组序因此跳动。客户端只是采用服务端sessions顺序。

现有有界遍历先建立科目组，再处理pending/反馈状态；终态行保留顺序锚点，pending才装入卡片，返回时去掉空组。无新查询/排序缓存/协议/Schema/依赖。删除/手动改期改变保留计划行集合不在此次新增保证内。

## 实际测试结果

| 检查 | 本轮结果 |
|---|---|
| 旧实现确定性反例 | FAIL（预期），同plan/count正确但完成语文1后由语数英变为数英语 |
| 新持久回归在旧实现运行 | 5 failed/3 passed（预期红灯）；4种feedback及自定义HTTP顺序断言失败 |
| 修复后专项：新文件 + review_fairness + review_inventory + test_review_selection | PASS，30 passed/8 skipped，3.53s；MySQL URL未配置的可选变体跳过 |
| 全量`.venv/bin/python -m pytest tests/unit tests/integration tests/contract -q` | PASS，518 passed/19 skipped/62 warnings，44.46s；未配置隔离MySQL的可选测试未运行 |
| `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | PASS，519文件格式通过；原68处历史问题经[单独批准chore](../../../specs/completed/CHORE-20261016-RELEASE-LINT.md)清理 |
| `.venv/bin/mypy apps/api/src` | PASS，103 source files |
| `npm test` / `npm run lint:miniapp` | PASS，244/244前端测试，ESLint通过 |
| `node --test tests/frontend/bounded-read-pagination.test.js` | PASS，8/8 |
| `.venv/bin/python tools/check_architecture.py` | PASS，ARCHITECTURE_VALID checked=3 |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | PASS，DESIGN_EVIDENCE_VALID |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS，16 pages / 1070913 source bytes |
| `.venv/bin/alembic heads` | PASS，唯一head 20261012_0019；生产只读核对同为0019，未执行迁移 |
| `git diff --check` | PASS |
| 原生三视口/iOS/Android | NOT_RUN；无小程序源码或几何变化，本轮不替代已有前端任务待验收项 |
| 新候选本地容器/云部署/真实写反馈 | 尚未执行完成；持续状态见[发布报告](../../deploy/releases/20261016-review-subject-order-backend.md) |

`uv`先因默认缓存权限失败，临时缓存又触发其Rust system-configuration panic；上述Python/Ruff/Mypy命令均通过已有`.venv/bin`直接实际运行，不把uv失败记为通过。全量后端日志暂存`/private/tmp/push-kids-bug029-pytest.log`，无真实孩子内容。

## 测试覆盖与R1 Diff Review

新增8个用例覆盖4种反馈、组id/余项顺序、分钟/计数、all_items、无补题、空组/全部完成/空计划、新DB会话重读、真实HTTP dashboard、幂等重放、自定义非语数英顺序、跨家庭拒绝及同家庭兄弟计划隔离。fixture仅含虚构数据。

2026-10-16，Codex实现者逐文件Diff Review，未发现剩余问题；这是同一实现者复核，不是独立人员审查。

| 文件 | 必要性与位置核对 |
|---|---|
| apps/api/src/push_kids/planning/service.py | 唯一权威投影内移动既有分组初始化并过滤空组；8加7删，无新SQL或跨模块写入；计数/snapshot逻辑保持 |
| tests/integration/test_daily_review_session_order.py | 真实服务及HTTP regression守住旧测试遗漏的不变量；修复前实际失败，测试fixture不进入生产 |
| Feature、Behavior、Architecture、UI | 在稳定日计划正文合并局部事实、排除删除/改期扩展；不改变设计/架构边界，保留旧任务各自发布状态 |
| Task Spec、索引、本证据、发布报告 | 记录批准、实际验证和生命周期；部署前记录不冒称上线，恢复步骤明确 |
| 5个设计工具 | 归单独批准chore，[逐文件审查及168输出一致证据](RELEASE-LINT-20261016.md)；不在后端白名单 |

## 文档闭环核对

| 项目 | 结论 |
|---|---|
| FEAT-001 | revision更新为本地保序修复，原计划正文加入终态锚点；旧030/客户端0.1.15仍是既有发布事实 |
| Behavior Catalog | BHV-006补充session不变量、反例与本地证据；保留fair-v2的BHV-034覆盖关系 |
| Architecture | 单service内响应组装，数据不变量正文同步；模块/依赖/Schema/扩展点不变，架构revision不变 |
| UI-001/FDB/FEC | UI正文同步服务端保序；无前端代码和新设计，批准资源保持不可变 |
| Spec/测试证据 | TP-001..008有实际结果；BUG为active/VERIFYING，部署与操作验收未完成不迁移DONE；lint chore已completed/DONE |
| Release | 独立记录候选/容器/平台/人工门禁，不将030的读取smoke当新修复验收 |

实际diff与以上相关正文无冲突；未扩展科目设置顺序、选题算法或删除/改期的语义。未执行项均显式保留。
