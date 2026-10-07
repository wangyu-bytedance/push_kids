# 精确原图与知识删除：本地实现证据

- Date: 2026-10-06
- Spec: `specs/active/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md`，`SPEC-20261006-SOURCE-DELETE-02`
- Design: `DREV-20261006-SOURCE-DELETE-01`；已批准manifest不变。
- Implementation: complete locally；verification: partial；release: not deployed。
- Owner: Codex；以下为实现者验证与必要性自查，不冒充独立人员审查。

## 实际运行

| 命令/场景 | 最终结果 |
|---|---|
| `.venv/bin/python -m pytest tests/unit tests/integration tests/contract tests/performance -q` | 411 passed / 7 skipped / 41.07s；跳过的是环境变量未设置的MySQL组，已另行实际运行 |
| `npm test` | 195 passed |
| 隔离 MySQL5.7.44：alembic upgrade head/current/check | PASS，head=`20260913_0014`，无模型漂移 |
| MySQL runtime suite | 7 passed；最终删除计数修改后 `-k delete` 2 passed / 5 deselected |
| Ruff check / format --check / Mypy | PASS；无新的生产依赖 |
| `npm run lint:miniapp` | PASS，包含生产JS与frontend tests |
| architecture / design current policy / miniprogram static | PASS；15 pages / 692345 source bytes |
| `git diff --check` | PASS；不覆盖untracked，新增文本另由工具与人工核对 |
| 微信 DevTools CLI preview | PASS，最终656208 bytes；用户在自动审批首次拒绝后明确授权重试；未upload/审核/发布 |
| 原生运行时 | 隔离副本保留真实AppID和插件声明，但禁用云端请求；模拟器显示WechatSI插件41002 `appid missing`，automator没有可用运行时 |

终端日志保存在本机临时目录：`/private/tmp/push-kids-source-delete-final-pytest.log`、
`/private/tmp/push-kids-source-delete-final-node.log`、`/private/tmp/push-kids-source-delete-mysql.log`、
`/private/tmp/push-kids-source-delete-mysql-final.log`。它们不是持久化交付依赖；以上摘要保留关键结果，
可通过仓库测试复现。测试数据均为合成材料；未读取/删除生产儿童记录，未记录原图或模型原始payload。

实现后独立只读阶段发现 `Today.onShow` 在成员未加载时将canWrite设为true的入口显示缺陷
（P2 NON-BLOCK，服务端仍拒绝viewer写入）。结束只读阶段后回到用户已授权的实现范围修复：
云端未知身份时默认隐藏删除，load等待bootstrap，再只允许manager/editor；本地无身份模式兼容。
新增启动竞态回归覆盖viewer/manager/editor并通过，最终frontend 195项及微信preview再次通过。
该自查没有替代另一会话/人员的独立Review。

覆盖的反例：旧实现会下载整个批次；跨提交相同index可能错配；先文字证据挡住后面的图片；
后续确认补空evidence把新图片套到旧提交；离页迟到下载污染界面；重复删除、viewer/错家庭、
事务中途失败；日计划不补项且后加知识不扣旧计划；旧反馈回执不复活；待发摘要去除删除项；
MySQL旧读快照不能重新插入已删除Review。规模断言为1/10000关联、<=20语句、<5MB Python峰值，
SQLite删除语句和MySQL读路径均检查索引计划。

## 逐文件必要性自查

路径均相对仓库根；每行结论为 `necessary / correct / 无无关冗余`。通用媒体组件的整批模式由
记录详情继续消费，保留它是兼容要求；Today显式启用精确模式。没有添加无owner抽象或双写。

| 文件 | 类型 | 必要性与放置理由 |
|---|---|---|
| apps/api/src/push_kids/agent_processing/contracts.py | modify | 在模型/外部输入合同拒绝布尔或字符串索引隐式转换 |
| apps/api/src/push_kids/learning/service.py | modify | 确认保存层停止跨提交补空旧证据，保持首次来源成对 |
| apps/api/src/push_kids/planning/service.py | modify | 同源读投影、首条有效图片优先、删除公共边界、计划当前读锁、通知有界查询 |
| apps/api/src/push_kids/planning/deletion.py | add | 规划域拥有的单知识事务，集合清理与计划聚合；不放到router/通用工具 |
| apps/api/src/push_kids/planning/router.py | modify | DELETE传输入口和既有家庭权限依赖 |
| apps/api/src/push_kids/planning/domain.py | modify | 旧Todo DTO透传knowledge_id供删除，确定性策略不变 |
| apps/api/src/push_kids/notifications/service.py | modify | 在发送前更新存活复习内容，跨域仅经Planning公共服务 |
| apps/miniprogram/components/submission-materials/index.js | modify | 预览前单图筛选、索引观察、错误和临时路径生命周期 |
| apps/miniprogram/components/submission-materials/index.wxml | modify | 单图、原编号与未知状态；保留整批消费者 |
| apps/miniprogram/components/submission-materials/index.wxss | modify | 已批准单图自然宽高和可读状态样式 |
| apps/miniprogram/components/todo-card/index.js | modify | knowledge ID、可写判断、独立删除事件 |
| apps/miniprogram/components/todo-card/index.wxml | modify | 删除入口紧跟defer，不混作feedback |
| apps/miniprogram/components/todo-card/index.wxss | modify | 菜单分隔和44px删除热区 |
| apps/miniprogram/pages/today/index.js | modify | 页面拥有确认、请求、错误、刷新和跨孩子隔离 |
| apps/miniprogram/pages/today/index.wxml | modify | 精确模式和删除确认弹层，传递权限与事件 |
| apps/miniprogram/pages/today/index.wxss | modify | 已批准的确认弹层滚动/按钮布局 |
| tests/frontend/submission-materials.test.js | modify | 下载前过滤/整批兼容/异步/失效来源反例 |
| tests/frontend/knowledge-deletion.test.js | add | 点击意图与真正写入分离，取消、防重、失败、权限、切孩子 |
| tests/unit/test_planning_source_evidence.py | modify | 图片优先、严格索引与同源摘要的输入边界 |
| tests/integration/test_precise_source.py | add | 真实A/B上传确认与HTTP响应进入原组件的跨层链路 |
| tests/integration/test_knowledge_deletion.py | add | 数据库清理、共享材料保留、隔离、幂等、失败原子性、计划计数 |
| tests/integration/test_todo_provenance.py | modify | 再次确认不把另一次证据填到旧来源 |
| tests/integration/test_notification_channel.py | modify | 队列摘要删除后刷新/取消，不发送旧计数 |
| tests/integration/test_mysql_runtime.py | modify | 真实MySQL5.7事务、10k关联和旧快照反例 |
| tests/performance/test_read_paths.py | modify | 删除语句数、内存和索引不随历史条数恶化 |
| docs/architecture/ARCHITECTURE.md | modify | 记录删除owner、锁、通知公共查询和无迁移事实 |
| docs/domain/features/FEAT-001-push-kids-mvp.md | modify | Feature最新事实及未验收范围 |
| docs/domain/BEHAVIOR-CATALOG.md | modify | BHV-030/031稳定行为条目 |
| docs/design/frontend/ui/UI-001-parent-miniapp.md | modify | Today精确原图、删除交互与原生验证缺口 |
| specs/active/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md | add | 用户批准、范围、方案、验收与VERIFYING状态 |
| docs/quality/evidence/SOURCE-DELETE-20261006.md | add | 持久化验证摘要和逐文件必要性 |

设计目录 `docs/design/frontend/prototypes/DREV-20261006-SOURCE-DELETE-01/` 中
`FRONTEND-SPEC.md`、`index.html` 为新增、必要、放置正确的任务设计合同和可编辑源。
快照目录 `docs/design/frontend/snapshots/UI-001/DREV-20261006-SOURCE-DELETE-01/` 中
以下各文件均为新增、必要、放置正确的批准证据，无运行时消费者：

| 文件 | 用途 |
|---|---|
| APPROVAL.md | 冻结批准和SHA-256 manifest |
| menu-320.png | 窄屏菜单设计 |
| menu-390.png | 标准屏菜单设计 |
| menu-430.png | 宽屏菜单设计 |
| photo-320.png | 窄屏精确图片设计 |
| photo-390.png | 标准屏精确图片设计 |
| photo-430.png | 宽屏精确图片设计 |
| confirm-320.png | 窄屏删除确认设计 |
| confirm-390.png | 标准屏删除确认设计 |
| confirm-430.png | 宽屏删除确认设计 |
| unknown-320.png | 窄屏未知来源设计 |
| unknown-390.png | 标准屏未知来源设计 |
| unknown-430.png | 宽屏未知来源设计 |

## 交付边界

本任务必要文件见上表；未发现本任务新增的可疑、无关、错层或待清除的过渡实现。
工作区原有`output/`及另一任务新增的REVIEW-MANAGEMENT设计、快照、Spec均不属于本任务，未修改。

自动化支持数据和交互状态正确性；不能据此宣称原生视觉通过。仍需：
1. 解决原生隔离副本的插件启动问题，取得三个要求视口的节点几何/截图及iOS/Android、大字操作证据。
2. 独立会话/人员只读审查（当前是实现者自查），以及反馈/确认与删除真正并行的额外压力验证。
3. 只有上述完成门禁满足后，才能将Spec改为DONE并移至completed。发布另按deploy工作流执行。
