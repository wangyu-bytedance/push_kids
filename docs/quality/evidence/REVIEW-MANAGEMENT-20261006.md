# 复习条目管理：本地实现与验证

- Spec: `SPEC-20261006-REVIEW-MANAGEMENT-03`，用户2026-10-06“落地并实现”批准。
- Design/Architecture: `DREV-20261006-REVIEW-MANAGEMENT-03 / ARCH-20261006-REVIEW-MANAGEMENT-01`。
- Implementation: 本地源码完成。Verification: 自动化/数据库通过，原生视觉待补。Release: 未部署、未上传、未提审或发布。
- Schema: 新增0016，父版本为同工作区STAGED-ANALYSIS的0015；部署不能只上传前端或忽略迁移依赖。

## 实际执行证据

| 检查 | 结果 |
|---|---|
| `.venv/bin/pytest tests/unit tests/integration tests/contract tests/performance -q` | 2026-10-07 最终复跑：476 passed / 11 skipped；跳过项需要可选外部环境 |
| `npm test` | 199 passed，包含次数确认/取消、非法输入、单科及跨科目目录页刷新保留选择、分页替换、迟到响应、删除、防重复、云bootstrap和家庭切换 |
| 新接口/排期SQLite专项 | `test_review_inventory.py` 13 passed；覆盖预览零写、次数精确过滤、游标失效、预算优先、幂等/version/日期冲突、回滚、inactive重启、历史补录、删除清理、四种同日反馈，以及已物化计划的积压计数和移出后删除不重复扣减 |
| 10k/50k规模 | 2 passed；非时间页≤8条SQL，时间预览≤16；默认20条、响应≤96KiB；捕获生产ORM实际SQL做SQLite EXPLAIN，全部/单科/具体次数/游标页无全表扫描 |
| SQLite迁移与日历纯规则 | 5 passed；旧due/count/version保留、预约非空禁止downgrade、跨月/年/闰日及120项上限 |
| 隔离MySQL5.7.44 | 2026-10-07 重新用utf8mb4空库upgrade head=0016；修改汇总SQL后并发排期2项+既有runtime7项，共9 passed；临时容器已停止清理。前次alembic check与模型无漂移验证仍适用 |
| MySQL并发反例 | 两事务先建立RR旧快照，119预约并发加项只有一个成功；既有未来计划并发加两个不同项，总数3/9分钟不丢增量 |
| Ruff check / format、Mypy、ESLint | 通过；没有新增生产依赖 |
| architecture / design current policy / miniprogram static | 通过；静态设计策略检查不代表DREV03导出/原生几何已验收 |
| 原生DevTools/视觉 | NOT_VERIFIED；隔离合成数据副本automator启动失败，`Cannot read properties of undefined (reading 'split')`；随后CUA原生界面请求被自动审批拒绝为与此前本地预览限制冲突，已停止，不换表面绕过 |
| DREV03 54张导出、320×568/390×844/430×932原生几何、字体放大/iOS/Android | NOT_RUN / 待验收；旧DREV01图片不得冒充本修订 |

隔离MySQL首次空库使用镜像默认latin1导致历史0003迁移中文IN比较collation错误；改为单独utf8mb4空库后完整迁移通过。
没有修改历史迁移或任何生产/其他任务库。测试使用合成条目、独立随机家庭；临时测试凭据未写入仓库。

2026-10-07 增补：既有计划的应复习总数和最早日期在手动改期后按当前有界租户范围重新聚合，避免把原本因分钟预算未选中的积压条目重复计数；
已移出的计划项在删除知识时不再重复扣除总数与分钟。科目目录翻到后页后，刷新和写入成功保留当前科目。

## 独立只读审查及修复

独立子任务`review_management_audit`依据code-review技能执行只读审查，主任务在其终结后进入实现修复阶段。

- CR-001：RR旧快照可能绕过预约容量、覆盖目标计划合计。资格/容量/候选/结果查询及`refresh(target_plan)`全部改为当前读；实际MySQL并发测试通过，独立复查关闭。
- CR-002：同日提前复习消费预约后保留手动due污染曲线。消费状态明确为none/preserve/consumed；同日消费基于last_reviewed_on+interval_days恢复策略输入，审计before仍为实际手动日期。complete/observed/partial/reinforce四动作回归和独立复查关闭。
- CR-003：简化EXPLAIN不能证明生产查询。改为捕获实际ORM SQL及参数，在10k/50k运行EXPLAIN，独立复查关闭。

## 文件必要性及归属

| 文件组 | 用途与边界 |
|---|---|
| planning/inventory.py | family/child/filter/revision游标、数据库聚合、有限两天预览；读页面不物化计划 |
| planning/plan_candidates.py、selection.py、domain.py | 预览/物化共用有界候选；纯优先级、分钟预算和日期规则 |
| planning/scheduling.py、service.py、router.py、schemas.py | 排期事务、幂等/锁、真实反馈消费、HTTP校验；旧兼容读API保留 |
| models.py、0016迁移、platform/database.py | 单条预约、独立审计、Child清单revision、次数索引；升级与降级保护 |
| children/service.py、learning/service.py | 配置/确认变更经Children公开边界失效revision，不复制排期策略 |
| planning/deletion.py / purge_data | 删除目标知识/孩子/家庭时清新表，复用另一已批准删除工作 |
| miniprogram review-inventory/index.*、app.json | 原生二级页、三视图、指定次数表单、编辑/删除/错误/只读与有界分页 |
| reports/index.*、today/index.* | 报表区间前入口；移除下一次复习的状态/渲染/续页，保留原来源和删除实现 |
| 新unit/integration/performance/frontend测试 | 真实状态、事务和反例覆盖；旧Today未来UI断言按批准移除，兼容后端测试保留 |
| Feature/UI/Behavior/Architecture/ADR/Spec | 合并本地已验证事实和明确未验收边界；其他任务记录保留 |

未发现新增的无owner抽象、临时生产分支或不必要依赖。工作区同时存在SOURCE-DELETE与STAGED-ANALYSIS变更，
本轮只在交点做必要合并；不将其质量门禁或发布状态据为本任务成果。

## 尚未关闭的完成门禁

原生视觉访问需解除本次自动审批阻断；之后取得DREV03导出、三视口节点几何/状态截图、大字和真机证据。
Spec保持VERIFYING并留在active，以上证据齐备后才能标记DONE并归档。发布依照deploy流程另行授权执行。
