# BUG-036 内容Spec03本地机制实施证据

- Evidence revision: `EVD-20261101-BUG036-CONTENT03-IMPLEMENTATION-01`。
- Approved: Product owner，2026-11-01，“批准 BUG-036 内容 Spec03（含 Architecture03、Prompt05）”。
- Scope: [内容Spec03](../completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)，Architecture03，Prompt05。
- Baseline: 批准时冻结`staged-20261101-10` / `child-aware-history-agent-20261031-13`；实际本地实现为`staged-20261101-11` / `child-aware-history-agent-20261101-14`。
- 本证据对象为历史11/14本地机制时点；后续两项独立Review发现、12/15修复与新素材验收见[12 EVD](EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)。以下163/893、NOT_RUN及资源值保持其原观察，不作为当前12结果。历史30条和补充3条失败不覆盖。

## 可失败证据与实现

| 切片 | 真实观察 | 实现后结果 |
|---|---|---|
| 同来源阶段输入 | 原实现新增用例1FAIL：merge的images为`[]` | 原图/文字/科目/素材/excerpt进入merge、correction及两次review；该片邻界73PASS |
| 正式证据所有权 | 新用例2FAIL：合法科目/独立证据DTO被拒绝；空候选在extract被coverage拒绝 | 正式e目录、item证据键/置信度、完整素材账本；候选科目不再作为事实；空候选可继续原来源核验 |
| 纠正范围 | 增量中7FAIL/1PASS：q/m未处理导致KeyError；无关evidence改动未被拒绝 | q只改摘要/核对文案；真实素材及i/o限定成员/证据；无关目标/e编号/内容/来源账本保持 |
| 资源/完整性 | 增量中7FAIL：Provider未拒绝超文本/图片/数量；未计请求字节；改图未拒绝；64KiB诊断被旧白名单丢弃 | 512KiB纯文本、9张/配置上传上限、有限读取；来源SHA前后检查；64KiB在有/无缓存都验证；仅新增静态诊断和安全计数 |

原始失败输出按阶段保留于[安全证据目录](bug036-content03-20261101/manifest.json)。新增引用/账本/分合目标邻界在实现后验证，属于实施后验证，不能冒称事前Red。基线127PASS/1warning；源码冻结和历史失败均保留，未用HEAD代替缓存Spec02已批准基线。

正式证据只由merge/correction建立并经Review核对，历史match/reuse和公开装配都消费它。source_checks验证每素材及实际item引用；结构完整仍不能证明语义完整。一次语义纠正、两次Review、18/33核心调用、18缓存键及原TTL/事务政策保持。共享Prompt05补原始来源优先、教学角色、完整字词集合、长词组、作品去重、方向、读写集合和摘要事实；无原30答案对照表、无服务端语义改名。

## 实际检查

命令前缀：`UV_CACHE_DIR=/private/tmp/push-kids-uv-cache uv run --no-sync`。

| 检查 | 实际结果 |
|---|---|
| `pytest tests/unit/test_staged_analysis.py tests/unit/test_staged_proposal_recovery.py tests/unit/test_stage_provider.py tests/unit/test_provider_evidence.py tests/integration/test_analysis_checkpoints.py -q` | 163PASS，1warning，6.73秒 |
| `pytest tests/unit tests/integration tests/contract -q` | 893PASS，52条件SKIP，108warnings，111.16秒 |
| 受影响agent_processing和5份测试/fixture的Ruff | PASS |
| `mypy apps/api/src` | PASS，151源；既有untyped note |
| `python tools/check_architecture.py` | PASS，4policies/151modules，无环 |
| `git diff --check` | PASS |
| 全库`ruff check .` | FAIL，7条范围外E501：旅行native脚本1条、并行BUG-037证据脚本6条；未修改 |
| 全库`ruff format --check .` | FAIL，BUG-037证据脚本1文件；857文件已格式化，未修改范围外文件 |

52个条件skip不记PASS；本轮没有新执行隔离MySQL并发测试，缓存02既有8PASS为历史对象证据。公开API、SQL/迁移、Worker和明确retry事务不改，新的SQLite阶段缓存恢复与终态回归由上述专项覆盖。

## 资源与来源准备

[合成探针](bug036-content03-20261101/resource-probe.json)：两请求、每请求9×10MiB，纯文本69字节、原图94,371,840字节/请求、构造JSON125,831,293字节/请求；0.686秒，Python分配峰值279,687,811字节，macOS进程RSS峰值359,038,976字节。没有外部调用，合成字节不代表可解码真实图，SDK序列化及真实模型内存未测；不据此宣称云端资源验收通过。

只读事务已重新定位原30固定source digest及补充3固定source digest；只读取一个获授权家庭的来源。原30有68图/3份文字，补充3份有6图，74图全部按数据库SHA/字节数下载核对，补充6图还逐项匹配先前安全报告SHA；没有替换来源。冻结同家庭/孩子/科目且在来源之前创建的历史，共264项/7,214索引词。READ ONLY61表before已获取；after、真实生成、当前会话逐原图C1–C6和清理尚待执行。

没有生产部署、任务reset、业务POST、自动确认或Git提交。私有素材、身份、下载引用和阶段响应只留任务私有目录，待验收后清理；本安全目录仅保存源码/测试、静态输出和资源计数。

## 后续和生命周期

- 独立只读Review、原30一次完整尝试、补充3及边界组、内容逐项判定、after审计和清理：NOT_RUN。
- 真实内容成功条件仍为原29份充分来源完整PASS + case11正确补材料拒绝；完整30分母保留。补充3另计，原PASS检查回退。
- Spec为VERIFYING，位于`specs/active/`。本地机制通过不是内容验收通过，也未满足本增量云交付/DONE归档。
