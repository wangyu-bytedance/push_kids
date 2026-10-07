# 公平复习排期 — 2026-10-07 验证记录

结论：**功能实现已完成，发布门禁BLOCK；没有部署或迁移生产。**

对应`SPEC-20261007-FAIR-REVIEW-01`、`ARCH-20261007-FAIR-REVIEW-01`与
`DREV-20261007-FAIR-REVIEW-01`，均由用户“生成代码，然后测试后提交部署服务端”批准。
初始代码基线`8214557bf5431dae5b7d385d84c01a88b8c9d1ad`；既有未跟踪`output/`未修改或纳入提交。

## 已实现与实测

预约→科目覆盖→首次/再次机会→类内等待优先；只有实际家长反馈增加复习次数。
等待计算只使用最近3个fair-v2实际计划日，预览/刷新不写等待，旧计划不重排。
历史/归档恢复/启用通过本地日期限定等待起算。SQLite/MySQL共同选择器的候选固定6次SQL，
实际返回≤1268、选入≤120，所有候选读包含家庭与孩子作用域。

今日移除用户截图中的两段解释与其分隔线；条目分开显示建议/预约日期和实际安排状态，
旧API回退中性“计划日期/安排状态待更新”。39张批准设计导出是设计证据，不是原生运行验收。

| 检查 | 实际结果 |
|---|---|
| `.venv/bin/pytest tests/unit tests/integration tests/contract -q` | PASS：487 passed、16 skipped、59 warnings；跳过为可选环境MySQL测试，相关MySQL另行执行 |
| MySQL5.7真实公平/预览/并发预约/身份/幂等/任务/删除测试 | PASS：19 passed；使用全新本机隔离utf8mb4库 |
| 初次MySQL复跑 | FAIL：两个旧测试固定ID撞上上轮夹具残留；新建隔离库迁移后19项全通过，未修改断言绕过 |
| SQLite0016→0017迁移及保护回退 | PASS：保留实际次数、due_date、state_version与旧plan policy；不伪造last_offered，存在fair-v2计划时禁止删列回退 |
| MySQL5.7空库→0014→0017、current/check | PASS：最终`20261007_0017`，No new upgrade operations detected；最终完整迁移含两条新索引 |
| `npm test` | PASS：200 passed，0 skipped |
| `npm run lint:miniapp` | PASS |
| Ruff check/format、Mypy | PASS（完整检查后续补充工具/文档又单独检查）；Mypy 97个源文件 |
| 架构/设计/小程序校验 | PASS：ARCHITECTURE_VALID、DESIGN_EVIDENCE_VALID；16 pages / 704467 source bytes |
| 既有1万/5万inventory有界读取测试 | PASS：2 passed；新投影增加固定查询预算，普通≤13、后天≤27；不是按科目N+1 |
| 新公平候选规模/延迟门禁 | **FAIL**：最终SQLite 1万最大550ms、5万最大1323ms；MySQL5.7 5万最大3558ms，均超过500ms目标；不能以有界条数代替时延通过 |
| 同环境旧路径相对p95≤2倍 | NOT_RUN：绝对门槛已经失败；需修订02实现后一起补测 |
| 本地白名单验证包与Docker镜像 | PASS：非root UID10001，8000端口，live/ready均200，SIGTERM exit0、OOM=false；未上传云端 |
| 原生三视口节点/iOS/Android | NOT_RUN；本轮仅本地原生源码与批准HTML设计，不能宣称真机验收 |
| 真实家庭当前快照28天仿真 | NOT_RUN；本轮未再次连接生产，合成仿真单独标注，不冒充真实历史 |
| 云端dry-run、数据库备份/迁移、灰度和切流 | NOT_RUN；必需性能和迁移兼容检查未通过，停止在发布前 |

环境说明：现有虚拟环境与node_modules运行检查；本轮未重新执行依赖安装。
MySQL为`mysql:5.7.44`的linux/amd64本地Docker，非生产性能环境，但不因此豁免方案中的本轮500ms门槛。
早期MySQL排序表达式的collation错误已修复并以真实MySQL测试确认。

## 独立只读审查

审查者`/root/fairness_review`，两轮独立只读审查：

- FR-01：预算不足时后天预览没有模拟明天的科目安排；已修复。
  独立复现现在预览与物化均为`a0 → b0`；新增SQLite/MySQL集成覆盖。
- BLOCK：5万条性能超预算，不能部署。
- BLOCK：旧服务严格要求原schema revision，迁移0017后旧镜像ready失败，不能直接作为回滚目标。
  必须先核实目标生产源码/版本，制作明确兼容additive迁移的过渡镜像并验收。
- 未发现其他明确可复现正确性问题；审查者独立16项单元/SQLite测试通过，5项MySQL未选取。

待用户批准`SPEC-20261007-FAIR-REVIEW-02`新增planning索引投影及schema过渡方案后继续实施。
首版Spec保持active/BLOCKED，未达到DONE归档门槛。

## 可重跑的合成仿真

`PYTHONPATH=apps/api/src .venv/bin/python tools/replay_fair_review.py`，仅合成固定积压，
28个实际计划日、每天30分钟、3或10科学习科目；完成全部/一半/不反馈三种固定假设，无新内容流入。
完成时调用实际`curve_heat_v1`纯策略；不是对真实家庭未来的预测。

- 3科情况下，各科有资格但缺席的累计“科目×日”由旧规则51/55/56变为0/0/0。
- 3科且不反馈时，初始首次项28天仍未获得机会从73项降至0项；不等于已复习。
- 10科每科3分钟正好耗尽30分钟，覆盖轮占满预算，首次池没有余量；全部反馈场景下
  初始首次项仍未获得机会从旧规则0项变成38项，最大等待21→27日。这是已批准优先级的真实取舍，
  不可宣称新策略让所有条目更早复习或保证固定天数清空积压。
- 所有情景重复选入和自动预算超额均为0。

机器生成聚合：[synthetic-replay.json](fair-review-20261007/synthetic-replay.json)、
[candidate-benchmark.json](fair-review-20261007/candidate-benchmark.json)。不含真实姓名、ID、学习内容或凭据。
