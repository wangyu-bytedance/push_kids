# 后端、数据库与微信云托管发布

## 1. 发布原则

- 数据库 migration、后端镜像/源码和云托管版本是三个独立发布物；任一失败都停止切流。
- 应用启动只校验 Schema，不自动迁移生产数据库。
- 数据库变更采用 expand-first：先发布向前兼容的 additive migration，再发布同时兼容新旧版本的代码；
  收缩或删除字段必须放到后续独立版本。
- 事故回滚优先回退不可变后端版本并停止相关写入口，不在故障处理中执行破坏性
  `alembic downgrade`。
- 正式运行账号仅保留业务所需 CRUD 权限；DDL 使用发布窗口内的 migration 账号。
- 云托管公网入口保持关闭，小程序只使用 `MINIAPP` 专用入口。
- 密钥只在控制台运行时变量/密钥能力中配置，不通过 CLI 参数、聊天、截图或仓库传递。

## 2. 冻结发布范围

发布开始前记录：

```bash
git status --short
git rev-parse HEAD
PYTHONPATH=apps/api/src uv run alembic heads
rg -n "expected_cloud_revision" apps/api/src/push_kids/platform/database.py
wxcloud --version
```

当前代码库的 Alembic head 和应用 `expected_cloud_revision` 必须完全一致。本文编写时二者均为
`20260905_0002`；后续发布以命令输出为准，不复制历史文档中的旧值。

有未提交改动时，必须在发布报告中列出并确认它们属于本次范围；不能无记录地把整个脏工作区发布。

## 3. 发布前检查

在仓库根目录执行全部必需门禁：

```bash
uv sync --all-groups
npm install
uv run pytest tests/unit tests/integration tests/contract -q
uv run ruff check .
uv run ruff format --check .
uv run mypy apps/api/src
npm test
npm run lint:miniapp
uv run python tools/check_architecture.py
uv run python tools/validate_miniprogram.py
```

还需执行并记录：

- 新 MySQL 空库从 base 升级到 head，并运行 `alembic current`、`alembic check`。
- 目标版本涉及的 MySQL 集成测试、家庭隔离、幂等、Job lease 和图片 claim 测试。
- 本地 Docker 构建、非 root UID、端口 8000、SIGTERM、`/health/live`、`/health/ready`。
- 发布包清单和镜像环境中没有 `.env`、密钥、OpenID、儿童内容或本地数据库。

任何未运行项必须写明 `NOT_RUN` 和原因；必需项不能被口头视为通过。

## 4. 数据库变更流程

### 4.1 开发阶段

1. 修改 SQLAlchemy model。
2. 新增单向、可审查的 Alembic revision；禁止应用启动时 `create_all` 或偷偷补生产表。
3. 审查 upgrade 对旧代码和双版本窗口是否兼容；破坏性改动拆成 expand/migrate/contract 多个版本。
4. 在全新 MySQL 和上一生产 Schema 的副本上分别执行 upgrade。
5. 验证 migration 失败时事务、人工修复和重新执行行为。
6. 更新应用 `Database.expected_cloud_revision`，使其等于唯一 Alembic head。

### 4.2 生产迁移前人工门禁

```text
【需要人工操作】创建并确认生产数据库备份
原因：备份、恢复点和数据库管理权限只能由云账号管理员确认。
操作入口：https://cloud.weixin.qq.com/
导航路径：目标环境 prod-d2g14rwoycac6b45d → MySQL → 备份/恢复
需要填写/选择：创建发布前备份；记录备份 ID、完成时间、数据库 push_kids 和恢复验证状态。
完成标志：备份状态为成功，且管理员确认存在可用的隔离恢复路径。
完成后回复：已完成数据库发布前备份
```

如果 migration runner 无法通过内网访问 MySQL，只能由管理员在受控发布窗口短时开放数据库访问，
限制来源 IP，迁移完成后立即关闭；不得把数据库密码发到聊天或写进 shell history。

### 4.3 生产迁移执行

在可访问生产 MySQL 的受控 runner 中，通过安全环境变量注入 migration 账号：

```bash
export PUSH_KIDS_ENV=cloud
export MYSQL_ADDRESS='<从安全存储注入>'
export MYSQL_USERNAME='<migration账号>'
export MYSQL_PASSWORD='<从安全存储注入>'
export MYSQL_DATABASE=push_kids

PYTHONPATH=apps/api/src uv run alembic current
PYTHONPATH=apps/api/src uv run alembic heads
PYTHONPATH=apps/api/src uv run alembic upgrade head
PYTHONPATH=apps/api/src uv run alembic current
PYTHONPATH=apps/api/src uv run alembic check
```

不要把上述占位值替换后复制到聊天、Issue 或文档。优先由密码管理器、CI secret 或临时安全会话
注入变量，执行结束后关闭会话并回收 migration 账号权限。

当前 `20260905_0002` 在升级前会阻止“已有孩子数据但没有 active 微信绑定”的历史家庭继续迁移。
若命中该保护，停止发布并人工确认归属；不得删数据或放宽 migration 来强行通过。

完成标准：

- `alembic current` 唯一 revision 等于 `alembic heads`。
- `alembic check` 输出没有新的 upgrade operations。
- 使用 CRUD-only 应用账号连接成功，但创建/修改表被拒绝。
- 数据库外网入口（如曾临时开启）已经关闭。

## 5. 云托管运行配置人工门禁

仅当环境变量、实例、入口、存储规则或服务配置发生变化时执行：

```text
【需要人工操作】核对微信云托管运行配置
原因：运行时密钥和控制面设置不能进入仓库或 CLI 历史，必须由云环境管理员配置。
操作入口：https://cloud.weixin.qq.com/
导航路径：prod-d2g14rwoycac6b45d → 云托管 → flask-ik19 → 服务设置/版本配置
需要填写/选择：
- 端口 8000；0.5 CPU / 1 GiB；当前保持 min=1、max=1。
- MINIAPP 入口开启，PUBLIC 公网入口关闭。
- PUSH_KIDS_ENV=cloud、PUSH_KIDS_MEDIA_BACKEND=wechat_cloud、PUSH_KIDS_AI_PROVIDER=ark。
- WECHAT_APP_ID=wx5d2e0014690bf285、WECHAT_SERVICE_NAME=flask-ik19。
- MySQL CRUD 账号变量、COS_BUCKET/COS_REGION，以及有效的 Ark Key 和至少 32 字符的 actor HMAC Key。
- 不手工创建 CBR_ENV_ID；它由平台注入。
完成标志：配置预览与 deploy/cloudbase/service-settings.json 一致，敏感值只存在于运行时配置。
完成后回复：已完成云托管运行配置
```

对象存储规则必须保持创建者读写，不得改成 public；需要图片处理时先确认开放接口服务已启用，
并由目标后端版本验证临时 COS 凭证和 metaid decode。

## 6. 创建后端不可变版本

先执行不会部署的 dry run：

```bash
uv run python tools/prepare_cloud_release.py
cd dist/cloud-release
wxcloud deploy --dryRun \
  -e prod-d2g14rwoycac6b45d \
  -s flask-ik19
cd ../..
```

检查 `dist/cloud-release/release-manifest.json`、Dockerfile 和端口，确认没有 `.env`、`.git`、文档、
测试、图片、本地数据库或过期压缩包。发布工具使用允许列表并扫描当前进程中的秘密值；任何命中都
停止发布。随后创建灰度版本；版本备注必须唯一且能关联 commit/spec：

```bash
BACKEND_RELEASE_REMARK='push-kids-YYYYMMDD-NNN-<short-sha>'

wxcloud run:deploy dist/cloud-release \
  -e prod-d2g14rwoycac6b45d \
  -s flask-ik19 \
  --containerPort 8000 \
  --dockerfile Dockerfile \
  --targetDir . \
  --releaseType GRAY \
  --remark "$BACKEND_RELEASE_REMARK" \
  --override
```

不要添加包含密钥的 `--envParams`，也不要用 `--noConfirm` 跳过 CLI 的发布确认。记录平台返回的
不可变版本号、镜像/源码摘要、创建时间和发布范围。wxcloud CLI 2.3.3 即使在 dry run 中读取到
`Dockerfile`，实际 `run:deploy` 仍可能在未显式传参时以“缺少Dockerfile”拒绝发布，因此以上两个
参数不得省略；若上传日志仍出现 `.venv` 或 `dist`，停止全量放量并记录为打包门禁缺陷。

### 6.1 发布确认表门禁

输入 `yes` 前逐项核对 CLI 确认表：

| 字段 | 必须显示 |
|---|---|
| 环境 ID | `prod-d2g14rwoycac6b45d` |
| 服务名称 | `flask-ik19` |
| 发布模式 | 灰度发布 |
| Dockerfile 文件名 | `Dockerfile`，不得为空 |
| 目标目录 | `.`，不得为空 |
| 端口号 | `8000` |
| 版本备注 | 唯一并包含日期、Spec/序号和 short SHA |

任一字段为空或不一致都输入 `no`。不要依赖 `--override` 自动继承 Dockerfile 和目标目录；
2026-09-05 的首次发布正是在这两个字段为空时被平台以“缺少Dockerfile”拒绝。

### 6.2 上传包门禁

`wxcloud deploy --dryRun` 通过不代表实际上传包完全遵守 `.dockerignore`。必须从刚生成且已审查
manifest 的 `dist/cloud-release` 发布，并观察实际上传/解压日志。若出现下列任一内容，立即停止
该版本继续放量并重新生成发布目录：

- 仓库根 `.venv`、`.git`、`dist` 或历史 ZIP；
- `.env*`、密钥值、数据库、儿童图片或日志；
- `docs`、`specs`、`tests`、`tools`、`apps/miniprogram`；
- manifest 中不存在的未知文件。

Dockerfile 最终没有 `COPY` 某个多余文件，不等于上传边界合格。发布报告必须保留 manifest 文件数、
总字节数和实际上传日志核对结果。源码在 manifest 生成后有任何变化，都必须重新生成发布目录，防止
发布期间的并行工作混入版本。

### 6.3 CLI 日志异常时的权威判定

wxcloud CLI 2.3.3 可能在镜像构建和实例部署期间重复输出：

```text
ResourceNotFound.TopicNotExist: topic not exist
```

这是 CLI 实时日志 Topic 订阅失败，既不能证明部署失败，也不能证明成功。另开终端使用以下只读命令
确认平台状态：

```bash
wxcloud version:list -e prod-d2g14rwoycac6b45d -s flask-ik19
wxcloud service:list -e prod-d2g14rwoycac6b45d
```

- 新版本为 `creating`：继续等待，不切流、不修改任务数据；
- 新版本为 `normal` 且服务为 `normal`：记录完成时间，进入健康检查；
- 新版本为 `deploy_failed`：停止发布，保留上一正常版本；
- 只有独立确认新版本为 `normal` 后，才可终止仍重复 Topic 错误的本地 CLI 监听；终止监听不会
  停止已完成的云版本。

### 6.4 2026-09-05 真实发布复盘

| 现象 | 结果 | 后续强制措施 |
|---|---|---|
| Dockerfile/目标目录未显式传入 | 发布在创建版本前被拒绝，线上未切流 | 显式参数 + 确认表非空门禁 |
| dry run 展示忽略规则，但实际上传出现 `.venv` 和旧 `dist/*.zip` | 上传约耗时数分钟；Dockerfile 白名单 COPY 避免进入镜像，但上传包不合格 | 只发布最小白名单目录并审查 manifest/实际日志 |
| 构建期间反复 `TopicNotExist` | 镜像最终成功，`flask-ik19-006` 于 23:33:53 达到 `normal`，CLI 未正常结束 | `version:list`/`service:list` 是权威状态源 |
| 活动仓库在发布期间继续产生并行修改 | `006` 打包开始时已核对范围，但当前工作区随后变化 | 发布命令只指向冻结目录，源码变化后重新生成 manifest |
| revision 14 与 Ark Key 门禁联合发布 | 冻结白名单目录共 57 个文件；`flask-ik19-008` 于 23:58:58 达到 `normal`，服务 `normal`、公网关闭 | 运行时秘密只由人工在云控制台配置；`normal` 只证明启动门禁通过，仍须真实图片 smoke |
| revision 15 租约精度修复 | MySQL 秒级 `DATETIME` 与内存微秒值严格比较导致有效 proposal 被丢弃；`flask-ik19-009` 于 00:27:48 达到 `normal` | claim 后 refresh 持久化 lease；达到 max_attempts 的过期任务终态化；真实新图片已完成 Ark 与写回并进入待家长确认 |

上述问题未触发数据库 migration、密钥写入或稳定版本回退，但均是后续每次发布的停止条件，不能只作
提示性备注。

## 7. 灰度、验收与全量

新版本进入 `normal/ready` 后：

1. 通过真实 AppID 和 `wx.cloud.callContainer` 验证 `/health/live`、`/health/ready`。
2. 验证未绑定 actor、已绑定 actor、错误 AppID/env、伪造 `X-Family-ID` 的预期状态。
3. 完成两个真实账号的创建家庭、邀请、申请、批准和业务 API 流程。
4. 完成文字、图片、AI、确认、Todo、活动、报表、重试、取消和重启恢复。
5. 检查 5xx/429、延迟、MySQL、Job queue age、图片 claim/orphan 和脱敏日志。
6. 至少覆盖约 2 分钟的新旧版本共存窗口，再逐步增加流量。

全量切流是人工门禁：

```text
【需要人工操作】确认后端全量发布
原因：全量切流会影响所有小程序用户，必须由发布负责人核对灰度证据和回滚点。
操作入口：https://cloud.weixin.qq.com/
导航路径：prod-d2g14rwoycac6b45d → 云托管 → flask-ik19 → 版本/流量管理
需要填写/选择：选择刚通过验收的不可变版本；核对版本号、配置、数据库 head、灰度指标和上一回滚版本。
完成标志：目标版本承载预期流量，PUBLIC 仍关闭，MINIAPP 主流程和 ready 检查持续正常。
完成后回复：已完成后端全量发布
```

## 8. 回滚和发布后记录

触发下列任一情况立即停止放量：跨家庭访问、身份可伪造、公开媒体、Schema 不匹配、重复正式写入、
secret 泄漏、ready 持续失败、Job 无法恢复或数据库备份不可恢复。

回滚顺序：

1. 停止新版本继续放量；必要时先关闭新写入口。
2. 将流量切回上一兼容的不可变后端版本。
3. 保留 additive Schema，不在事故中执行 destructive downgrade。
4. 验证上一版本 ready、读取、幂等和家庭隔离。
5. 数据修复、字段删除和备份恢复另开经过审批的 migration/事故流程。

发布报告必须记录：Git SHA/工作区差异、Alembic before/after、备份 ID、后端版本与摘要、运行配置版本、
所有检查 PASS/FAIL/NOT_RUN、灰度指标、人工操作人、全量时间、前端版本和回滚目标。
