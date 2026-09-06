# ADR-001: 微信云托管使用 FastAPI、MySQL 与私有云存储

- Status: `ACCEPTED`
- Date: 2026-09-03
- Last reviewed: 2026-09-06
- Decision owners: 产品负责人（用户）
- Technical area: deployment, persistence, identity, media, asynchronous jobs
- Related Spec: `specs/active/CLOUD-001-WECHAT-CLOUDBASE-STAGE1.md`
- Related ADRs: N/A
- Supersedes: CLOUD-001 旧草案中的 CloudBase Document Database 目标

## 1. Decision

Push Kids 保留原生微信小程序和 FastAPI 业务后端。受控 staging 部署到微信云托管，
小程序通过 `wx.cloud.callContainer` 访问；结构化数据使用托管 MySQL/InnoDB，Schema
由 Alembic 管理；儿童媒体通过 `wx.cloud.uploadFile` 进入微信云托管私有对象存储，
再由后端验证平台上传者元数据并 claim。SQLite 和本地媒体仅保留给本地开发/测试。
第一阶段云端固定单实例，保留 durable database Job 和修正后的进程内 Worker。该 Worker 的技术债
只由本 ADR 的 `TD-001` 维护，其他工程文档只引用该条目。

## 2. Context and drivers

- 当前 FastAPI 已承载全部业务、确定性策略、事务与自动化测试。
- 微信云托管按容器运行，不要求 Flask；现有 Flask 服务是计数器模板。
- SQLite、本地图片目录和客户端 `X-Family-ID` 不能直接作为云端可信运行时。
- 用户已选择微信云托管、MySQL，并要求前端维持原生小程序方案。
- 微信云托管官方对象存储支持小程序按环境直传并返回 cloudID，服务端可用环境临时凭证和文件元数据校验上传者。
- 未成年人数据要求私有媒体、最小权限、可恢复持久化和不泄密日志。

优先级：保留行为正确性与测试资产 > 身份/数据安全 > 可恢复发布 > 迁移速度 > 立即横向扩容。

## 3. Options considered

### Option A — FastAPI + MySQL + private cloud storage（chosen）

- Benefits: 最大化复用现有代码；关系约束和事务语义与当前模型一致；迁移可逐步验证。
- Costs: 需要 Alembic、MySQL 方言验证、云媒体 adapter、COS 临时凭证/元数据校验和真实环境测试。
- Risks: Worker 演进约束见唯一技术债 `TD-001`；直传产生的未 claim 对象需要可靠清理。
- Reversibility: staging 可回到本地版本；数据写入后只能通过备份/兼容版本回退。

### Option B — Flask rewrite + MySQL

- Benefits: 表面上贴合官方 starter。
- Costs/risks: 重写路由、依赖注入和测试，无平台收益且扩大回归面。
- Decision: rejected。

### Option C — FastAPI + CloudBase Document Database

- Benefits: 原生文档/弹性能力。
- Costs/risks: SQLAlchemy 查询、关系约束和事务需要大规模重写，Python adapter 面显著扩大。
- Decision: superseded by the user's MySQL choice。

### Option D — FastAPI + SQLite/local uploads in Cloud Hosting

- Benefits: 最小初始改动。
- Costs/risks: 容器磁盘与伸缩生命周期不适合作为持久化；备份和恢复不可靠。
- Decision: rejected。

## 4. Consequences

### Positive

- 原生小程序页面和绝大多数 FastAPI 服务/领域逻辑保持不变。
- SQLAlchemy 继续作为持久化边界，MySQL 提供独立于容器生命周期的关系事务。
- `callContainer` 提供更窄的微信入口；云存储消除本地媒体持久化依赖。

### Negative / accepted debt

- staging 服务名 `flask-ik19` 与实际 FastAPI 不一致；仅临时复用。
- 本地 SQLite 与云端 MySQL 形成双方言测试矩阵。
- 官方直传 + 后端 claim 引入 ticket、上传者元数据校验、orphan cleanup 与安全规则运维。
- “仅创建者可读写”不直接覆盖未来 FEAT-002 多家长读取；协作上线前需另行批准授权读取方案。

#### `TD-001` — 单实例进程内 Worker

- Classification: accepted technical debt；不是代码缺陷，也不作为当前单实例 staging 的 blocker。
- Current boundary: 微信云托管保持 `min=1,max=1`；durable DB Job、lease、retry 与幂等终态继续生效。
- Risk: 横向扩容或请求结束后的 CPU 调度可能使后台执行所有权不再可靠。
- Revisit trigger: `maxNum>1`、Job p95 queue age 超过 60 秒，或平台执行语义不能满足验收。
- Exit criteria: 通过新批准的 Spec/ADR 把 Worker 迁到受支持的任务执行器，并验证重启、租约、重试、
  取消、清理、无重复终态和可观测性。
- Owner: 产品负责人 + backend maintainer。

### Security/privacy

- 云环境只信任平台入口 actor，拒绝 client family authorization。
- OpenID 只在内存中 HMAC；数据库和日志不存 raw OpenID。
- 运行时禁止 root 数据库账号；密钥只在云环境变量/密钥能力中。
- 对象存储前端规则必须是仅创建者可读写；儿童文件不得公开读、公开列举或暴露裸 COS URL。
- 后端只使用云托管环境临时 COS 凭证；claim 必须解码并比对 `x-cos-meta-fileid` 上传者，不信任客户端 cloudID/path。

## 5. Guardrails

- `planning/domain.py` 不得依赖 SQLAlchemy/MySQL/cloud SDK。
- cloud 环境不得执行 `create_all`，不得回退 SQLite 或本地 uploads。
- 页面不得直接调用 cloud service；JSON 网络仍由 `utils/api.js` 统一拥有。
- 媒体 provider 细节不得进入 learning domain/service 公共契约。
- 小程序上传路径必须来自后端的一次性随机 ticket；服务端拒绝错误环境、bucket、path、上传者或缺失元数据的对象。
- 多实例、公开生产、Flask 重写或文档数据库均需新批准 revision；Worker 演进统一由 `TD-001` 触发。
- 自动检查覆盖 SQLite/MySQL parity、Alembic head、family isolation、原子确认、Job lease、私有媒体和 secret scan。

## 6. Rollout and rollback

1. 轮换已暴露密码并创建最小权限账号。
2. 创建独立数据库、备份基线和私有存储规则。
3. Alembic 初始化空库；部署 immutable staging image。
4. 通过受限公网做无数据 smoke，再通过两个真实账号验证 callContainer/actor；该项已于 2026-09-06
   由用户确认通过，包含 actor/owner 隔离、metaid decode 与公网拒绝。
5. 关闭公网；完成端到端、重启、恢复和日志检查。
6. 失败时停止写入并切回上一兼容容器/小程序构建；涉及 Schema/数据时从一致备份恢复。

## 7. Revisit conditions

- 命中 `TD-001` 的任一 revisit trigger。
- 需要非微信客户端、家庭多人协作或公开生产发布。
- MySQL 成本、限制或事务证据不满足当前 SLO。
- 云存储临时凭证、metadata decode、owner-only 规则或 orphan cleanup 无法通过 `G-004`。

Owner for revisit: 产品负责人 + backend maintainer。

## 8. Validation after adoption

| Hypothesis | Metric/evidence | Target | Review date | Result |
|---|---|---|---|---|
| MySQL preserves FEAT-001 behavior | adapter/integration/E2E | no contract deviation | staging acceptance | pending |
| callContainer actor is trustworthy | two-account + forged-header smoke | zero unauthorized access | staging acceptance | **PASS 2026-09-06（用户确认）：双账号 actor/owner 隔离、metaid decode、公网拒绝通过** |
| single-instance Worker topology | ADR debt review | bounded staging scope | architecture review | accepted technical debt；唯一跟踪项 `TD-001`，不记为 Pending |
| private media lifecycle is bounded | read-denial + orphan audit | zero public/orphan past SLA | staging acceptance | pending |

## 9. Approval

- Approved by: repository owner（用户）
- Approval date: 2026-09-03
- Dissent/concerns retained: service-name debt；Worker 的分类、边界与退出条件只见 `TD-001`
