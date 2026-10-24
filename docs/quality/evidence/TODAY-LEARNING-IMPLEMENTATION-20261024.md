# 今日学习与空白日复习实现证据

- Scope: 两份已批准Spec04、Architecture02/03、DREV-20261024-TODAY-LEARNING-01。
- Subsequent UI refinement: 用户另行批准Refinement Spec01/DREV02并已本地实施，当前弹层及其45组原生取证见[新实现证据](SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)。本表其他数字保留主功能实现阶段的实际执行结果，不冒充新源码的全量回归。
- Implementation: LOCAL；两个开关默认false；没有部署/上传/生产写入。
- Verification: VERIFYING；不能由代码完成推定全部验收通过。
- Workspace baseline: main / 82ca52775bc948f2a963a8f4ed614322d8859de8，存在其他聊天的共享未提交增量；没有提交、推送、上传或部署。本轮原生相关小程序源码/采集脚本指纹见native/source-manifest.json。
- Architecture: [ADR](../../architecture/decisions/ADR-EMPTY-DAY-AND-PARENT-APPROVED-LEARNING.md)。

实现包含：确定性early政策及每Review最多3槽投影、旧计划保守固定/新暂空按库存代次重判、early来源/日期/版本快照与真实反馈；可靠首次新增计时；独立严格建议Provider；共享一次性提示；单待学/审批/暂缓/换项；真实人工确认的可恢复关联；scope清理；今日卡片和编辑/实际记录弹层。安排不改Review事实，批准不写正式已学。

本轮新增测试文件：test_today_learning_policy、test_empty_day_early_review、test_learning_suggestions、test_today_learning_migrations、test_today_learning_reads、test_today_learning_mysql、today-learning.test.js。覆盖自然日/80%/冷却、预约排除、原日期/预算、暂空代次/不补排、非法未来反馈/版本、共享提示/次日同项、输入变化/过期、零正式写入、部分/明确完成、重复确认、关联失败恢复、删除晚到、开关回退、计时回滚/重复知识、草稿恢复不饥饿、owner清理、生成三次失败/限额/幂等、真实成员角色降级/移除拒写、其他家长弹窗阻挡时不消费自动提示及迟到UI结果。

| Check | Current result |
|---|---|
| 定向政策/复习/建议 | 集中执行政策/复习/建议/迁移/MySQL入口：47 passed / 1 skipped / 3 warnings，4.11s；`/tmp/push-kids-today-learning-targeted-final.log`。复习14项单独通过，含装不下的到期项仍阻止提前、多科机会和两日预览无写/不重复 |
| SQLite 10k/50k上下文和early探针 | 两规模通过：/current≤8 SQL、≤16KiB、读取<500ms；上下文≤24KiB；early固定3条SQL，实际计划使用ix_early_slots且无全槽扫描；见test_today_learning_reads |
| 0022→0023→0024及安全空数据降级/重升 | 1 passed；旧空计划legacy_fixed、可靠观察日起算、9个槽触发器及新索引存在；不包含其他任务0025 |
| Python全量 | `.venv/bin/pytest tests/unit tests/integration tests/contract -q`：760 passed / 40 skipped / 108 warnings，103.78s；日志`/tmp/push-kids-today-learning-backend-latest.log`。包含最新删除/生成事务修正及所有新增测试；跳过项需外部环境，不计PASS |
| 前端全量 | `npm test`：295 passed / 0 failed；`/tmp/push-kids-today-learning-frontend-final.log` |
| 类型与静态 | mypy150源码通过（既有untyped提示1条）、Ruff check与format通过、ESLint通过；架构150模块运行/延迟DAG通过，设计证据校验通过，小程序17页面/1208833源码字节通过。新增测试/采集工具后Ruff check、688文件format、ESLint与git diff --check均复验通过 |
| 设计 | 已批准HTML/78PNG/SHA冻结；原型8条交互通过，原生另列 |
| 原生 | 原DREV01阶段390×844十二态PASS，PNG/节点JSON/截图SHA及当时源指纹见[历史原生目录](today-learning-20261024/native/README.md)；当时320/430因锁屏未采集。解锁并完成跨会话协调后，当前DREV02建议相关15态×3共45组已通过，见[当前证据](SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)。复习组合、真实键盘/读屏、完整今日26态与真机仍未闭环 |
| MySQL5.7 | NOT_RUN：本机无5.7镜像；官方mysql:5.7.44两次下载registry-1.docker.io请求超时（包括获准使用沙箱外网络的重试），无测试容器创建。可恢复入口为`PUSH_KIDS_TODAY_TEST_MYSQL_URL`指向名称以today_learning_test开头的隔离库，`test_today_learning_mysql.py`校验真实5.7、0022→0024旧计划/触发器/重升及双家长竞争；当前为SKIPPED。不用现有MySQL8镜像代验 |
| 真实Provider/内容质量 | NOT_RUN；严格DTO及假Provider不证明儿童内容适合或年级衔接质量 |
| iOS/Android、完整读屏/键盘、类目/隐私条件 | NOT_RUN；保留为发布门禁 |
| 独立实现Review | NOT_RUN；当前可用Review工具只有PR CI诊断，未创建PR；本轮自行边界检查不冒充独立评审 |

Feature001/004、Behavior（BHV-044/045）、Architecture/ADR、UI001、设计规格/索引、AGENTS产品边界、Spec批准/最终位置、测试策略和本地发布记录已按实际diff核对。正文中的只读提取/学习建议例外、稳定计划/暂空重判、due/提前来源及审批/真实确认已分别消除冲突；其他聊天035生产/0025年级/记录入口事实保留。两份Spec保留active/VERIFYING，未通过门禁不勾选、不迁入completed。

领域SQL预算：首次automatic/manual生成及删除再生成三条路径均≤15（身份认证固定读取另计）；自动提示响应复用已锁定Child及知识上下文，不在提交后重复读取整个/current。删除和可选入队使用同一Child事务，资源/资格验证失败仍提交明确删除，Provider仅在提交后运行；不双重锁定/反复刷新状态。所有其他状态组合及完整反选择矩阵仍须补充。`get_context`验证复用Child的家庭/孩子范围。

本轮曾发现并已修正：旧0016迁移夹具使用最新ORM注入0025字段；以冻结SQL种子恢复独立旧库测试。mypy早期类型推导、初次提示24条SQL以及按钮默认宽度问题均有后续通过结果；这些失败不隐藏，也不当作当前PASS。
