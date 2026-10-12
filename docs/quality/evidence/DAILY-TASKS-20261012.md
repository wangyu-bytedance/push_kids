# 每日任务本地实施与验证记录

- Date: 2026-10-12；Verifier: Codex。
- Spec / Design / Architecture: `SPEC-20261012-DAILY-TASKS-01` / `DREV-20261012-DAILY-TASKS-01` / `ARCH-20261012-DAILY-TASKS-01`。
- Baseline commit: `719cb337177d218bc1654a9b598192c8311202ba`；target为未提交工作树，仅每日任务范围。
- Approval: 用户「好的按照这个方案实现前后端代码。」；未授权/执行部署、上传或生产迁移。
- Runtime: 仓库现有`.venv` Python3.12；uv启动遇本机Rust system-configuration panic，改用同一环境可执行文件。

## 自动化结果

| 检查 | 实际结果 |
|---|---|
| `.venv/bin/pytest tests/unit tests/integration tests/contract -q` | 510 passed、19 skipped、62 warnings，48.05s；跳过包含需要真实MySQL连接的现有测试 |
| `.venv/bin/pytest tests/integration/test_daily_tasks.py tests/integration/test_daily_task_migration.py -q` | 22 passed；含并发同状态/相反完成命令、容量准入与迁移 |
| `npm test` | 231 passed、0 failed |
| `.venv/bin/pytest tests/performance/test_read_paths.py -q` | 4 passed，7.64s |
| `.venv/bin/mypy apps/api/src` | 103 source files，0 issues |
| `npm run lint:miniapp` | PASS |
| `.venv/bin/ruff check apps/api tests/integration/test_daily_tasks.py tests/integration/test_daily_task_migration.py tests/integration/test_activities_and_reports.py` | PASS |
| 同上范围 `ruff format --check` | 126 files already formatted |
| `.venv/bin/ruff check . --output-format json` | FAIL；142项位于6个其他设计render.py，本功能Python文件无发现；未改动这些文件 |
| `.venv/bin/ruff format --check .` | FAIL；同6个其他设计脚本未格式化，459个文件已格式化 |
| `tools/check_architecture.py` | PASS，3个纯政策检查 |
| AST读取全部API模块导入图 | 103模块，0循环；只读检查绝对导入，与仓库现有导入形式一致 |
| `tools/validate_miniprogram.py` | PASS，16 pages，739191 source bytes |
| `tools/validate_design_evidence.py --check-current-policy` | PASS |
| `tools/validate_design_evidence.py --manifest …/DREV-20261012-DAILY-TASKS-01/APPROVAL.md` | PASS，15设计导出及哈希 |
| `git diff --check` | PASS |

全局Ruff失败文件为DREV-20261010-REVIEW-INVENTORY-02、DREV-20261011-REPORT-DISCLOSURES-01和
DREV-20261012-SETTINGS-SUBJECT-LIST-01/02/03/04目录的render.py。设置科目设计是工作区同时存在的无关工作，未覆盖。

## 验收点对应

- TP-001 PASS SQLite：真实API+DB配置CRUD、严格输入、trim、名称唯一、20上限和并发准入。
- TP-002 PASS SQLite：重复完成不新增事实、撤销、并发相反命令、上海午夜、快照不随配置编辑/删除改写；旧日未完成不变债务。
- TP-003 PASS：12新增前端页面测试覆盖完整计数、稳定计划/积压区分、空/完成/部分、手动选择、旧偏好不生效、切孩子/家庭/日和迟到响应；全套回归含reviewReturn。
- TP-004 PARTIAL：真实角色鉴权与跨家庭/孩子拒绝、归档、child/family删除worker、SQLite迁移保持原有数据与降级保护PASS；真实MySQL5.7迁移/锁语义未运行。
- TP-005 PARTIAL：三视口设置/今日基础矩形与截图PASS；390真实点击完成2项后自动收起PASS；所有视口长名称/键盘/只读/pending/错误全矩阵和iOS/Android真机未完成。
- TP-006 PASS SQLite：20配置+10000历史，2次SELECT（含孩子鉴权），tenant-leading索引EXPLAIN、响应≤16KiB。
- TP-007 PASS本地：全套回归、性能检查、纯政策及导入图无环；旧报告指标、规划预算不受每日任务影响。

## 原生证据及适用范围

`daily-tasks-20261012/`保存wx.createSelectorQuery获得的数字矩形和CUA开发者工具窗口截图，全部为合成家庭/孩子/任务。
使用Stable2.01.2510290开发者工具、基础库3.17.3、默认字号15、显示比例75%。
设备矩阵：iPhone5 320×568 Dpr2；iPhone12/13(Pro)390×844 Dpr3；iPhone14ProMax430×932 Dpr3。
JSON中的height是小程序可用windowHeight，屏幕全高与顶部/TabBar安全区由设备截图呈现，不能混为HTML viewport。

| 状态 | 320 | 390 | 430 |
|---|---|---|---|
| 设置：2任务、4候选 | settings-320.json/png | settings-390.json/png | settings-430.json/png |
| 今日：每日任务未完成展开、其他空区收起 | today-320.json/png | today-390.json/png | today-430.json/png |
| 最后一项真实完成后收起 | NOT_RUN | today-completed-390.json/png | NOT_RUN |

命令：`node tools/daily_task_geometry.js capture <settings|today> <width> <file>`；
`node tools/daily_task_geometry.js audit docs/quality/evidence/daily-tasks-20261012/*.json`实际7 captures PASS。
检查区域不越界、文字与按钮留白、44px触控（1px测量容差）、候选间距、表单两列几何。
基础捕获不含编辑表单，不能从空节点推出表单已验收。

原生运行通过`/private/tmp/push-kids-daily-tasks-native`临时项目副本连接隔离SQLite API（8769），
生产源码页面与样式不变；临时配置改为本机API和合成身份，禁用该副本域名检查。
WeChatSI插件在该本地appid环境报41002，临时副本移除可选语音插件后测试这两个页面；生产插件配置未改。
因此本证据确认每日任务基础原生布局与操作，不确认生产插件编译或真实云身份链路。
临时API已正常关闭。捕获后逐字节比较两页js/wxml/wxss，6文件与仓库源码一致。

### 原生捕获SHA-256

以下仅封存测试证据，不改动已批准设计manifest。

| Evidence file（相对于daily-tasks-20261012/） | SHA-256 |
|---|---|
| settings-320.json | f05d9feb03b32045127d9760ece6276631a91a6d5f54ed1f004769e24bbea52d |
| settings-320.png | c681c55df840758b8bd38397a2fcf04e065ec76189a1aedc7378a1caaef789cd |
| settings-390.json | 0d36d6efe87256e54b40e50d68f5755ca5698f12ade90a89a6739a5b56e50ea8 |
| settings-390.png | e02d63269797b2ee0825159a53bf688756e46680b662c58a1c188ca106e0b4a2 |
| settings-430.json | 4e4b2cccad4ca99c3ccb0a589fb343341169b05436731587ea003778195084b0 |
| settings-430.png | f8cfcd87cfc1f517187e93581fe8adf90d5ff02ea0ce444251fb17323a0bd706 |
| today-320.json | ecf092a63e74801ea9f7aa023173884a9776abc50d308de874f51d3755af1889 |
| today-320.png | e82b69076d2c8a7bb7d22f50634e4e3024f2b3431b78af36f0dbe3c0d2ec41bd |
| today-390.json | 2902eb016c2e74e62d83a4308eccd944625e80d1556bcce4e829c65794d1865e |
| today-390.png | 82e504140abd1bc8ede8fb0d9ac003a49e9ab5694636de3647d22cf15e3d3ed1 |
| today-430.json | c33afe48ef7284101a366142079a739c3cc6cf92916b81247491e06371c4005a |
| today-430.png | dd891c4a9a112c6498e31b54bd5527f5dfa843d051a3b2b15cee2695854eaa19 |
| today-completed-390.json | cd8a45394f13ef8ba20da027d678ae55ddf8a9333d22a5c3e0f71f4bbfb50040 |
| today-completed-390.png | c2bba0cb997d1112956e49e46e4787498c645324d97c3c1e89788b3f55fa9f04 |

| Native source | SHA-256 |
|---|---|
| settings/index.js | 49a5d0c661c3b05c37948fb17650547831ae265d95543477cd01cce71abac68b |
| settings/index.wxml | b57ce9d73f2a4059d031d670fddd147bb2ed7f1bbb7393dd35dfd55289a49479 |
| settings/index.wxss | e9be037049e0090e0a65c6e418f9ea830e4fe7cf650ed14ad6e8745307a5daef |
| today/index.js | b2aeb0e2f583a593edbbbf7e31ad3ac9b694698b770a67f3f8d053705d3f1e38 |
| today/index.wxml | f4051ad613eb227e9a5a4ed50def781201dcb56d3ce6d79e51a1d50c00709d8a |
| today/index.wxss | aab8aeb591fc8b70bd420f39d207b37d29069f4a41e3b597a9d89749706dca05 |

## 剩余门禁与生命周期

未配置真实MySQL测试URL，未索取凭据；未运行MySQL5.7并发/迁移，也未进行真机键盘/读屏/放大字号/弱网。
用户已批准实施，代码完成；验收Spec保持VERIFYING以保留这些具体缺项，不标DONE、不移completed、不声称发布完成。
部署仍须后端迁移/API先于新设置客户端，沿用`docs/deploy/README.md`和MySQL门禁；不能因迁移仅增量而跳过未验证的门禁。
只读复核作为本次最后独立阶段，其结果在聊天末尾提供，不将预期结果写作已通过。
