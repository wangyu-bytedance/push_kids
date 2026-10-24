# 自动替代复习词条 — 本地实现证据

实施日期2026-10-20至2026-10-21；Spec02获用户「按照这个方案落地代码，并经过严格的测试」批准；
具体DREV01随后获用户「批准该设计并继续实现」批准，21张设计导出和源hash保持冻结。
本轮保留工作区已有未提交修改；未部署、未读取/整理线上家庭数据、未发真实通知。

已实现：永久normal→superseded状态、同scope原子转换、确认时受控内容快照、AI可选完整覆盖阶段、
独立存量worker及持久游标/唯一任务/90秒租约/最多3次/30秒模型预算、queue v2、已有待办移出不补题、
保留一次人工预约、未来/积压/提醒/报表资格、状态分页API及删除SET NULL。
旧来源/Occurrence/反馈/实际次数守恒，无恢复、无联动删除。证据截断或实际承接内容变化则跳过。
独立目录页和报表共享组件已实现「参与复习 / 已替代」筛选、承接关系、原记录入口；
已替代只有科目/次数视图，管理菜单仅删除，只读无管理操作。切换状态隔离迟到响应并清空分页/过滤。

## 已执行与结果

环境：本机Darwin arm64、Python3.12.11、SQLite；真实MySQL5.7.44使用本机既有专用测试容器。
最终命令输出保留于[test-runs SHA清单](superseded-review-20261020/test-runs/MANIFEST.json)，
包括[后端](superseded-review-20261020/test-runs/backend.txt)、[MySQL5.7](superseded-review-20261020/test-runs/mysql57.txt)、
[前端](superseded-review-20261020/test-runs/frontend.txt)及[性能](superseded-review-20261020/test-runs/performance.txt)；不记录密钥、原始模型响应或孩子资料。

- unit/integration/contract最终全量：671 passed，35 skipped，93.03s。普通套件未注入MySQL环境，跳过项为MySQL运行/调度/公平性/分阶段/足迹/通知及本功能隔离门禁；本功能另由真实MySQL专项执行。scope与游标专项：31 passed（含14项AI合同/流水线、17项状态/确认/后台测试）。
- 真实AI：15个人工标注合成样本，覆盖数学/语文/英语/科学/未知范围与注入反例，1个live测试通过。该样本集通过不代表普适准确率。
- 独立MySQL5.7：迁移到head及13项状态/计划/确认/删除/后台/并发/真实目录EXPLAIN/安全回退重升测试通过（26.01s）；每个测试使用本次新建随机隔离库并清理，测试完成恢复专用容器原停止状态。
- 性能全套：14 passed、2 skipped，34.00s；2项跳过为既有公平计划MySQL规模门禁，未冒充通过。本轮10k/50k × normal/superseded四项均通过，核对数据库聚合、真实ORM EXPLAIN、≤20项/96KiB响应及固定查询数；50项MySQL目录分页另外验证。SQLite迁移专项最终1 passed，0.69s。
- 前端最终回归265 passed/0 fail、ESLint PASS；新增状态筛选、分页/删除保留筛选、旧请求迟到、viewer来源导航、共享内嵌、错误资格字段拒绝排期、几何审计反例。报表旧精确URL断言同步状态参数合同。
- 原生数字几何42组PASS：320×568、390×844、430×932，各独立页/内嵌 × 正常/已替代/菜单/只读/长标题/承接项删除/空态；真实WeChat基础库3.17.4、字体15。检查44px热区、等宽、8px间距、标题留白、边界、菜单唯一删除及viewer无管理动作。[JSON与来源清单](superseded-review-20261020/native/README.md)。截图接口超时，PNG与完整原生验收仍NOT_RUN；不是42组完整视觉通过。
- Ruff check全库PASS；Mypy130模块PASS（仅既有未标注函数note）；Architecture DAG 4 policies/130 modules PASS；当前设计策略与本DREV已批准SHA清单均PASS；Mini Program静态PASS（17pages、1156147source bytes）。原生隔离项目编译及渲染已运行，完整生产项目预览包/插件集成未运行。
- 最终选定161个Python文件format PASS（apps/api及本功能测试/诊断）；全库format为FAIL：仅既有无关`docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/render.py`两处格式差异，其他609个文件已格式化；保留未修改。`git diff --check`、新Node采集脚本语法检查PASS。

复现命令（隔离MySQL/Ark凭据通过运行时提供，不进入命令或聊天）：

```bash
.venv/bin/python -m pytest tests/unit tests/integration tests/contract -q -rs
.venv/bin/python -m pytest tests/unit/test_coverage_contract.py tests/integration/test_knowledge_supersession.py -q
.venv/bin/python -m pytest tests/performance -q
.venv/bin/python -m pytest tests/integration/test_supersession_migration.py -q
# 单独注入隔离PUSH_KIDS_TEST_MYSQL_URL后：
.venv/bin/python -m pytest tests/integration/test_supersession_mysql.py -q
PUSH_KIDS_RUN_COVERAGE_LIVE=1 .venv/bin/python -m pytest tests/live/test_coverage_semantics.py -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy apps/api/src
npm test
npm run lint:miniapp
.venv/bin/python tools/check_architecture.py
.venv/bin/python tools/validate_design_evidence.py --check-current-policy
.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261020-SUPERSEDED-REVIEW-01/APPROVAL.md
.venv/bin/python tools/validate_miniprogram.py
.venv/bin/ruff format --check apps/api tests/unit/test_coverage_contract.py tests/integration/test_knowledge_supersession.py tests/integration/test_supersession_migration.py tests/integration/test_supersession_mysql.py tests/coverage_fakes.py tests/live/test_coverage_semantics.py tests/performance/test_review_inventory_scale.py tools/diagnostics/supersession_native_project.py
node --check tools/superseded_review_geometry.js
# 原生隔离项目建立与三视口采集步骤见native/README.md
```

## 发现与修正

真实MySQL的秒级时间精度不能用于身份先后防环，改用两端normal的原子单向终态条件；
任务到期测试明确使用过去时间，避免MySQL舍入导致测试抖动。不同测试使用独立随机新库并清理。
规模测试暴露自引用SET NULL缺少SQLite反向索引；已补显式索引，重跑验证清理不再逐项全扫。
早期将全后端和性能合跑因该退化而中断（669 passed、34 skipped后KeyboardInterrupt），不计整套通过；补索引后分别完成全后端和性能重跑。
真实AI首次因沙箱网络限制未能连接，开放本次运行网络后重新执行15例通过；没有把网络失败计为语义通过。
MySQL优化器可选择已有等价租户索引，查询计划门禁核对实际有索引访问并拒绝ALL/全索引扫描，不绑定唯一索引名称。
旧v1投影冻结，新增v2及增量迁移；存在永久状态时拒绝丢弃schema。
新增真实MySQL回退用例先暴露1553（支撑自表外键的索引不能先删除）；调整downgrade为先移除外键、再删除其索引，SQLite与MySQL回退重升均重新通过。
原生首次fixture曾因路由尚未完成而被新页覆盖，采集脚本现等待目标路由并核对实际状态/只读/空态标志；最终42份JSON均为修正后采集，未保留旧错误结果。官方自动化包0.13.0源码确认截图方法为App.captureScreenshot；多次15/40秒超时，未伪造PNG或以HTML替代。

## 未完成及恢复条件

本地实现与自动化已完成，Spec为VERIFYING，保留specs/active；不能标为DONE。
恢复原生截图通道后，重跑42组节点+PNG并逐图检查设计一致性、长文案换行与菜单；
完成iOS/Android、字体放大和读屏验收及完整生产项目预览/包体门禁。
独立只读评审在本轮代码及文档冻结后执行，结论以本轮最终输出为准；不预写PASS。
全库format仅受上述既有无关文件阻断，未静默扩大本次修改范围。未部署、上传或触达线上家庭数据。

## 文档冲突核对

已同步FEAT-001/003/006、Behavior Catalog、Architecture、Frontend Design索引、UI-001、Test Strategy、Spec/索引及本地发布记录；
替换active即可排期、历史重激活即可恢复的当前表述。其他Feature的既有本地/灰度状态保留。
已替换DREV待批准及前端未实现的过时正文；逐项核对实际diff，未发现本功能当前正文与实现冲突。
未将HTML设计、历史测试、数字几何或旧发布证据写成本次完整原生/真机验收事实。
