# BUG-036 缓存10/13 — 后端发布准备

- Stage: `BLOCKED_PRE_DEPLOY_QUALITY_GATE`。本记录保留下方准备阶段原结果；批准后最终发布门禁见[灰度创建前停止记录](20261101-knowledge-cache-gray-blocked.md)。
- 用户本轮：“更新版本号及发布记录，将状态正式标记为已部署”。
- Release Spec: [OPS发布Spec01](../../../specs/active/OPS-20261101-BUG036-CACHE02-DEPLOYMENT.md)，已获“批准 OPS 发布 Spec01，开始灰度部署”，目前BLOCKED：固定40case真实34/40未过门禁。
- Actual backend version: 尚无新版本，当前仍`flask-ik19-039`；不预写040或已部署。
- Target: `prod-d2g14rwoycac6b45d` / `flask-ik19` / GRAY / 8000，PUBLIC关闭。
- Unique planned remark: `push-kids-20261101-cache02-01-0576ac3`，提交前再次查唯一性。
- Commit: `0576ac30464908154c624effed41df6dfa3110cc`及已批准未提交生成/缓存源。
- Candidate: `dist/release-20261101-bug036-cache02-01`。
- Frozen payload: 154文件 / 1,551,631字节，150Python源；manifest SHA-256
  `a07c0bf32a85afa80c1d69485d0c7d203dca663dddf10cd26f2c88c5c68f612b`。
- Evidence: [清单](../../quality/evidence/bug036-cache02-release-20261101/candidate-manifest.json)、
  [发布准备汇总](../../quality/evidence/bug036-cache02-release-20261101/preparation-summary.json)。
- Pipeline/prompt: `staged-20261101-10` / `child-aware-history-agent-20261031-13`。
- Schema: `20261024_0025`，应用expected revision与Alembichead一致；本次无DDL/数据迁移，新增备份门禁N/A。
- Frontend: 未上传/bump，仍既有0.1.17。后端版本不通过小程序版本工具递增。

## 精确发布范围

从039已交付154文件冻结基线复制，只替换已批准生成/缓存10份生产源：
`agent_processing/{checkpoints,contracts,failures,pipeline,prompt,stage_contracts,stage_provider,telemetry,worker}.py`
与`learning/service.py`。其他039源、Dockerfile、pyproject、uv.lock、wxcloud配置保持。
离线`knowledge/maintenance.py`仅参与现有工具测试，未进入payload。
活动工作区中的内容Spec03已开始修改6份相关源与5份测试；其11/14及额外合同不进入该10/13候选。
后续必须从候选目录发布，不能重新从活动仓库打包。

## 已执行准备检查

| 检查 | 实际结果 |
|---|---|
| 039基线manifest/10份批准源/SHA/秘密扫描 | PASS；154payload一致、只保留允许文件 |
| 精确150Python生产源Ruff/format/mypy | PASS，mypy150源；与活动工作区检查分开 |
| 冻结验证树DAG/纯策略 | PASS：4policy/151验证模块（含1测试专用离线模块，不进payload） |
| 首轮候选全量 | 856PASS/1FAIL/52skip；私有验证目录缺该用例读取的前端源码，属于夹具问题；实际错误/首败保留 |
| 夹具修正复验 | 补齐前端只供读取，原失败用例1PASS，不修改生产代码/测试断言 |
| 最终候选全量 | 857PASS/52skip/108warnings，111.59s；精确候选源码，当前并行测试不覆盖此冻结证据 |
| 独占真实MySQL5.7 | 新utf8mb4库head/current/check退出0；8缓存事务专项/0skip，结束销毁；无生产DB读写 |
| 首轮dry-run | CLIexit0但压缩包188entry含本任务生成.mypy/.ruff缓存，包边界FAIL，未实际上传 |
| 最终dry-run压缩包 | 清理本任务生成文件后CLIexit0；155文件＝154payload＋manifest，逐项SHA一致、0未知文件；生成ZIP已删 |
| Docker首轮 | daemon不可用；官方CLI启动后BuildKit访问Docker Hub metadata超时FAIL |
| Docker恢复 | 既有本地python基础镜像及镜像缓存已核验；legacy构建长时间无阶段进展后停止本任务构建，未生成可验证镜像/运行结果。NOT_RUN_INCOMPLETE，不记录通过 |
| 全库Ruff | FAIL：7项E501来自旅行/并行报告验证脚本；需本发布Spec批准后作最小维护 |
| 全库format | FAIL：报告脚本及后来并行内容03测试共2文件需格式；不代改并行测试 |
| fixed40-case live Ark | NOT_RUN；仍是发布阻断门禁，历史真实内容FAIL不能改为通过 |
| 实际运行账号/管理员严格Schema、真实云smoke/后台任务 | NOT_RUN；冻结候选需要本轮核验 |
| 新GRAY、实际版本/镜像、流量 | NOT_RUN；没有已部署证据或新版本号 |

当前全库与精确候选结果独立。禁止为上线改为“全部PASS”、用旧40-case结果代新对象或隐藏外部跳过。
源码和发布包freeze后如要纳入内容Spec03必须新发布revision，不修改已冻结10/13清单。

## 下一步与停止条件

具体OPS批准已收到，两份验证脚本E501/格式与JS语义核验已完成，全库检查通过；
实际运行Schema核验也通过。固定40-case结果34/40和各科低于90%导致发布停止，
后续恢复需要对应内容/质量修复与匹配发布revision，不能因用户要求“已部署”而虚构状态。

新版本normal且发布包/配置对应后才更新实际版本号、“已部署”与matched Spec开发DONE归档。
HTTP0%不阻止进程内Worker消费同数据库任务，发布前核验Worker与运行配置，不能把0%作为无生产影响证明。
全量切流、账号/配置/主体等人工门禁按[发布手册](../README.md)，不在本次预先批准。
回退点只使用实际存在且兼容039，无DDL降级/生产数据重置/Git提交。
