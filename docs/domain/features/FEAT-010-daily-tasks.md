# FEAT-010 — 每日任务与今日默认折叠

- Status: `CLIENT_0.1.14_DEVELOPMENT_UPLOADED / BACKEND_UNDEPLOYED / PENDING_ACCEPTANCE`
- 2026-10-13设置视觉增量：每日任务移至课外活动下方，复用活动行、标记与添加入口，纸面背景同其他设置卡片；原预设、表单、时长和权限行为不变。SPEC-20261013-SETTINGS-TASK-VISUAL-02及SPEC-20261013-CARD-BACKGROUNDS-01已本地实现，验收待补。证据docs/quality/evidence/CARD-BACKGROUNDS-20261013.md。
- Current-state revision: `FEAT-STATE-20261012-DAILY-TASKS-01-LOCAL`
- Last verified: 2026-10-13；全套后端510通过、19跳过；前端238通过；另有隔离MySQL5.7迁移、11项集成检查及每日任务服务CRUD/幂等/快照/家庭范围通过。客户端0.1.14已开发上传，兼容过渡029已normal、流量待确认，新API/生产0019未部署，真机及云端新接口待验收。
- Approved Spec / Design / Architecture: `SPEC-20261012-DAILY-TASKS-01` / `DREV-20261012-DAILY-TASKS-01` / `ARCH-20261012-DAILY-TASKS-01`
- Source: `apps/api/src/push_kids/daily_tasks/`；设置与今日原生页面。
- Evidence: `docs/quality/evidence/DAILY-TASKS-20261012.md`。
- Change reference: `specs/active/FEAT-010-DAILY-TASKS.md`，当前VERIFYING；前端已开发上传，日任务新版后端尚未部署。兼容发布修订见`specs/active/BUG-20261013-DAILY-TASK-RELEASE-COMPATIBILITY.md`，实际阶段见`docs/deploy/releases/20261013-fullstack-diff.md`。

## 当前行为

设置中的每日任务按家庭和孩子独立保存。阅读、跳绳、练字、户外运动是快捷候选，点击后仍需保存；不自动启用。
允许自定义、编辑和删除。名称去首尾空白后为1～30字符；目标时长为1～180整数分钟；最多20个启用任务，启用名称不能重复。
保存失败保留表单，pending禁止重复请求。manager/editor可写，viewer只读；归档孩子禁止每日任务写入。

今日在复习安排下方显示每日任务，未完成在前，同组按创建时间和ID稳定排序。完成/撤销是当天的幂等命令，
不计时、不记录实际耗时。日期由服务端Asia/Shanghai确定，次日重新开始，历史未完成不形成债务。
当天修改配置影响当前展示，已完成事实保留当时名称和分钟快照；软删除移除今日条目，保留完成历史。

复习、每日任务、今天记录的学习、课外活动四个区块以完整服务端数据确定默认状态：
复习/每日任务/活动有未完成条目展开，空或全完成收起；学习记录非空展开、空收起。
复习使用稳定当日计划剩余数，不能按首页前三条或预算外积压判断；未来安排不会强制展开今天。
活动必须有当天实际活动记录才算已记录，时间已过不算完成，候选建议仍未完成。
本次浏览手动展开/收起保留到离开、刷新、切孩子/家庭/跨日；不再读取持久化todaySections旧偏好。
请求失败不改变完成事实，离开/切换后废弃迟到响应。

## API、存储与生命周期

路径前缀 `/api/v1/children/{child_id}/daily-tasks`：GET列表、POST配置、PATCH/DELETE `/{task_id}`、
GET `/today`、PUT `/{task_id}/today-completion`（严格布尔completed，不接受客户端日期）。
422非法字段/空值；404范围外或不存在；403只读/归档；409名称/容量冲突或清理中。

`daily_tasks`拥有配置和软删除状态；`daily_task_completions`拥有日期、完成时快照与occurred_at/created_at。
完成事实以家庭+孩子+任务+日期唯一。配置与完成写入按Child→Task顺序锁定，SQLite先获得写锁，MySQL使用当前锁定读。
迁移`20261012_0019`仅新增两表与tenant-leading索引，不填入默认配置，不修改原有学习数据；有任务事实时拒绝降级丢表。
daily_tasks owner提供purge_data，孩子/家庭永久清理先删除完成事实再删除配置，保留其他孩子/家庭的数据。

今日读取最多20任务，历史不随响应加载，单个任务查询与历史条数无关；10000历史验证2次SELECT（含孩子鉴权）、响应≤16KiB。
reporting通过DailyTasksService聚合；planning/AI/报告指标不依赖该域，目标分钟不扣复习预算。
提醒、星期安排、连续打卡及实际耗时统计均deferred。

## 验证边界

SQLite API、权限、清理、迁移、并发和大历史查询，以及前端状态回归已通过；三视口基础原生节点几何已通过。
真实MySQL5.7、原生全部状态矩阵、iOS/Android真机键盘与读屏未完成，不能据此声明生产验收通过。
