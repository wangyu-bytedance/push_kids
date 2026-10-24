# FEAT-011 — 本地实现验证（2026-10-17）

- Spec: [SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01](../../../specs/active/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md)，VERIFYING
- Architecture / Design: ARCH-20261017-NOTIFICATION-AUTO-RENEWAL-01 / DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Approval: 用户2026-10-17“按照这个方案落地”；批准先于生产代码修改。
- Git baseline: main 8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a；工作区原有通知诊断及其他并行文档保留。
- Scope: 本地实现；未提交、推送、部署、上传、体验、提审、正式发布、真实授权或发送。

## Actual automated evidence

| Check | Result / limit |
|---|---|
| 完整后端unit/integration/contract | 617 passed / 21 skipped；64.16s。跳过为需独立环境的MySQL等门禁，不能算通过 |
| 完整前端 | 247 passed；含todo-card→Today真实事件链、原生调用先于网络、原事件恢复、hide/show身份迟到及过期跳过 |
| 续期纯策略 | 18 passed；0/9/10、正/无限额度、硬停止及技术退避 |
| 真实HTTP续期专项 | 16 passed；反馈幂等/同日去重、失败事务注入回滚、逐类冷却、不同结果、CAS、旧模板、成员/viewer边界及离开/保留策略 |
| SQLite新增迁移 | fresh及已有0019两例通过；五表与metadata一致、旧数据保留、带数据拒绝降级及空表回滚 |
| SQLite全量alembic check | FAIL：四个历史learning_records索引差异；另在仅升级至0019的隔离SQLite库复现相同四项，确认并非0020引入。未静默修复或当作通过；新增五表比较无差异 |
| SQLite规模读取 | 10k/50k attempt及receipt：2 passed；快照最多6条SQL、最多3类、响应<=12KiB，不扫描授权/receipt历史；游标使用索引 |
| 实际MySQL5.7.44 | 2 passed，13.28s：已有0019升级、metadata核对/保数据/拒绝破坏性降级；两会话同事件/同反馈/不同反馈/CAS并发；50k attempt及receipt读取与EXPLAIN索引 |
| MySQL完整Schema检查 | 隔离库升级head20261017_0020后，alembic check：No new upgrade operations detected |
| Ruff / format / mypy | 全仓Ruff及format通过；mypy 106 source files通过 |
| 静态架构/设计/小程序 | ARCHITECTURE_VALID checked=3、DESIGN_EVIDENCE_VALID、MINIPROGRAM_VALID pages=16 source_bytes=1087244；这是源码预算，未构建上传包 |

临时MySQL容器仅回环地址、合成数据，未访问生产数据库。首次latin1测试库因中文编码失败；
换为独立UTF8MB4测试库重跑通过，不能把初次失败归因于通知逻辑。最终容器清理状态见下文。
全套旧通知发送/消费及原反馈回归随完整后端执行；新代码未在测试中访问真实微信或发通知。

## Native evidence and gaps

微信开发者工具Stable2.01.2510290，基础库3.17.4。最初CLI复用了已有项目，路径核对后未操作其业务；
另建/private/tmp/push-kids-renewal-native-20261017，核验独立项目路径及useCloud=false后才注入合成展示数据。
原生工具tools/notification_renewal_geometry.js只setData/查询节点，不调用订阅、投递或云接口。
原生App.screenshot返回不可用，JSON明确记为NOT_RUN；不以设计PNG替代运行时截图。

320×568全14态和390×844全14态数字几何已通过。原生检查发现的触控区域、状态文字、
v2默认按钮宽度与独立底部导航遮挡已在批准设计内修正。Today为custom navigation，
节点坐标覆盖完整screenHeight；窗口高度与完整屏幕高度同时保留，未混用来隐藏溢出。
430、最终源码绑定、字体放大及截图状态以文末最终核对为准。

Mac随后锁屏，CUA明确要求用户解锁；已请求解锁，未尝试绕过。
缺少：完整三档原生截图、iOS/Android真实记住选项/授权/10次冷却、读屏焦点与关闭恢复、
SQLite双会话完整矩阵/死锁重试，以及独立只读评审。以上均不得标成通过。
历史0F58收件、HTML42张设计快照与本轮真机验收是不同证据。

## Documentation consistency and lifecycle

已逐项核对Feature001/003/011、BehaviorBHV-028/037、Architecture及依赖DAG、UI001/011与设计索引、
测试策略、Spec与本地发布状态。替换原PLANNED/尚无自动补充/旧手动授权及假就绪等冲突正文，
保留并明确区分历史云端诊断。批准HTML及42张PNG/manifest未修改。无新增域反向依赖或开放扩展点。
Spec保留specs/active/、Status VERIFYING；完成条件未满足，不移入completed。
恢复条件：补齐上述原生/真机及独立评审证据，关闭重大问题，再判断DONE/迁移；发布需后续明确授权。

## Final verification binding

- [源码与28份原生JSON摘要](notification-auto-renewal-20261017/source-manifest.json)绑定本次生产文件/测试/采集工具SHA-256；不包含原有诊断或照片足迹研究差异。
- 原生320/390各14态数字几何是本轮真实运行样本，保留原始JSON及其SHA；**不是最终源码完整验收**。最后的待登记状态隐藏重复申请入口、身份/新鲜度保护调整后未再次原生采集。430、完整截图、字体放大/读屏均NOT_RUN；Mac锁屏阻塞仍在，等待用户解锁后补采，不使用旧样本冒充新diff通过。
- 最终自动化：后端617/21 skipped，前端247/0，独立MySQL5.7两例PASS；Ruff、format（552文件）、mypy（106文件）、ESLint、架构/设计/小程序及git diff --check通过；Alembic单head0020。
- 临时容器push-kids-renewal-mysql-20261017停止成功（exit0，--rm自动清理合成数据库）；隔离原生副本保留用于解锁后继续验收。
- 文档冲突核对：本次涉及的实现/设计/合同正文已同步，历史设计快照保持不变；未把本地、自动化、原生样本、真机或发布状态混为一体。Spec保持active/VERIFYING。
- 独立只读评审NOT_RUN；自查覆盖事务/SQL当前读、手势调用、身份迟到、原事件恢复、文件职责与删除路径，不能替代独立评审。本记录不表示已发布。
- 最终链接检查：Spec、Feature011、UI011、设计说明、发布状态与本证据中的本地Markdown目标全部存在；35个源码摘要无不匹配。批准设计校验通过，git diff --check通过。
