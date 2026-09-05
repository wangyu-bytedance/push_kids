# 知芽部署手册

本文覆盖本地运行、Ark 接入和发布入口。当前推荐部署是“原生微信小程序 + 微信云托管
FastAPI + 托管 MySQL + 云托管对象存储”；完整配置、发布、回滚和排障以
`docs/operations/WECHAT-CLOUD-HOSTING.md` 为准。

> Current-state note: 云迁移代码已按 `CLOUD-SPEC-20260903-03` 实现，本地验证进行中；
> 真实云环境、双账号、对象存储、恢复和关闭公网尚未形成验收证据，因此不能表述为已上线。
> 家庭协作、数据导出/删除和公开生产隐私门禁仍属于 FEAT-002。

## 1. 重要边界

本地开发后端使用 `X-Family-ID`，只适合开发测试。云环境拒绝该 Header，改用云托管入口
注入的微信 actor，经服务端 HMAC 和受控 binding 解析 family。公网入口必须在 smoke 后关闭；
客户端自报 family 或在公网伪造 `X-WX-*` 都不能作为鉴权方案。

## 2. 本地开发

要求：Python 3.11+、uv、Node.js 20+、微信开发者工具。

```bash
cp .env.example .env
uv sync --all-groups
npm install
uv run uvicorn push_kids.bootstrap.app:create_app --factory --app-dir apps/api/src --reload --port 8011
```

检查：

```bash
curl http://127.0.0.1:8011/health
# {"status":"ok","ai_provider":"ark"}
```

运行库默认从空库开始，不会自动插入示例孩子、科目或学习记录。后端启动后配置真实档案：

```bash
uv run python tools/configure_local_profile.py \
  --family-id local-family --child-name "真实昵称" --grade "小学二年级" \
  --budget 15 --learning 语文 数学 英语 --activities 游泳 乒乓球
uv run python tools/audit_database.py data/push_kids.db
```

导入 `/absolute/path/to/push_kids/apps/miniprogram`。`project.config.json` 的
`urlCheck=false` 仅用于本地；发布前要打开域名校验。服务地址由
`apps/miniprogram/config.js` 固定，家长端不提供编辑入口；切换本地端口或部署环境时，
由开发者同步修改该构建配置后重新编译小程序。

`http://127.0.0.1:8011` 只适用于与 API 同一台 Mac 上的微信开发者工具。真机预览中的
`127.0.0.1` 指向手机自身，不能访问电脑服务；受控局域网调试应让 Uvicorn 监听明确的局域网
地址、在构建配置中使用该地址并限制防火墙来源。云托管体验版/正式版使用
`wx.cloud.callContainer`，不允许把局域网或 `urlCheck=false` 配置上传。

## 3. 火山方舟 Ark

不要把密钥写入 Python、小程序、Dockerfile、截图或 Git。只在后端环境设置：

```bash
PUSH_KIDS_AI_PROVIDER=ark
ARK_API_KEY=在火山方舟控制台新建的密钥
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-2-1-pro-260628
```

安全烟测：

```bash
PYTHONPATH=apps/api/src uv run python tools/smoke_ark.py --text "英语学习了 animal 和 rabbit"
PYTHONPATH=apps/api/src uv run python tools/smoke_ark.py --image /absolute/path/to/sample.jpg
```

脚本只输出科目和数量，不打印密钥、原图、完整提示词或模型原文。没有密钥时 API 仍可读取
档案、日程和报表，但学习分析会明确失败并支持密钥配置后重试。自动化只在显式 `test/e2e`
环境使用确定性测试适配器，development/production 没有模拟回退。

## 4. 单机 Docker（仅本地兼容，不作为云上线方案）

以下路径仅用于本地容器 smoke。云托管不能依赖 Compose、SQLite volume、本地 uploads 或 Nginx：

Docker Compose 从宿主机 `.env.runtime` 读取应用运行变量并注入容器进程；该文件不会被 `COPY`、
不会挂载到容器文件系统，也不会提交 Git。开发者 CLI 密钥保存在另一个 `.env` 中，Compose
不读取它。首次运行先复制不含真实密钥的模板：

```bash
cp .env.runtime.example .env.runtime
docker compose build --pull
docker compose up -d
docker compose ps
curl http://127.0.0.1:8000/health
```

本地连接 MySQL 时只在 `.env.runtime` 中设置 `MYSQL_ADDRESS`、`MYSQL_USERNAME`、
`MYSQL_PASSWORD`、`MYSQL_DATABASE`，并删除 `PUSH_KIDS_DATABASE_URL`。这表示密码仅作为容器
运行时环境变量可见，不进入镜像层。生产云托管不上传此文件，改由云托管服务/版本环境变量
注入同名配置。

## 5. 微信云托管与小程序配置

1. 确认 AppID、环境 `prod-d2g14rwoycac6b45d` 与服务 `flask-ik19` 已关联。
2. `config.js` 保持 `useCloud=true`，`app.js` 初始化云环境。
3. JSON 请求统一使用 `wx.cloud.callContainer`；图片统一使用 `wx.cloud.uploadFile`。
4. 云端使用 MySQL/Alembic 和私有对象存储，不能把 SQLite/uploads 放在容器层。
   `MYSQL_PASSWORD` 由云托管在启动容器时注入，不写入 Dockerfile、镜像或源码包。
5. 开放接口服务必须在创建目标版本前启用，供服务端取得 COS 临时凭证并解码上传元数据。
6. 定向测试和灰度完成后关闭公网访问，只保留小程序专用链路。

详细环境变量、存储规则、身份、发布顺序、回滚和故障排查见
[`operations/WECHAT-CLOUD-HOSTING.md`](operations/WECHAT-CLOUD-HOSTING.md)。

## 6. 预览、上传和提审

先登录微信开发者工具；游客 AppID 只能编译演示，不能完成真实预览/上传。

```bash
WECHAT_CLI=/Applications/wechatwebdevtools.app/Contents/MacOS/cli
"$WECHAT_CLI" open --project /opt/push-kids/apps/miniprogram --trust-project
"$WECHAT_CLI" preview --project /opt/push-kids/apps/miniprogram --qr-output /tmp/push-kids-preview.png
"$WECHAT_CLI" upload --project /opt/push-kids/apps/miniprogram --version 0.1.0 --desc "FEAT-001 MVP"
```

上传后在小程序后台：版本管理 → 设为体验版 → 配置体验成员 → 真机验收。先完成云服务定向
测试和灰度，再考虑提审。审核材料应说明：照片只用于提取家长上传的学习内容；AI 结果是
草稿且由家长确认；不做自动评分、排名或孩子间比较。

## 7. 隐私与未成年人数据

正式版本使用相册/相机和处理儿童学习照片，需要在小程序后台配置《用户隐私保护指引》，准确列明收集目的、保存位置、保留期限、第三方处理方（含 Ark）和删除/投诉渠道。体验版也要按当前微信后台提示配置体验版隐私指引。隐私声明必须与真实代码和数据流一致。

建议默认：原图私有存储、服务端加密磁盘、最短必要保留、日志不含原图和正文、按家庭删除、备份到期同步清除。当前仓库没有公开图片下载路由。

## 8. 正式公开发布门禁

以下工作属于下一版 R3，未完成前只能受控体验：

- 完成真实双账号云入口/actor binding 验证；公网始终关闭，云环境不得信任 `X-Family-ID`。
- 家庭成员绑定、设备迁移、退出登录、会话过期和跨家庭越权测试。
- 查看/导出/删除孩子、原图和派生知识的完整数据权利流程。
- 对象存储私有规则、内容安全策略、保留期任务和 orphan 审计。
- MySQL 备份恢复、告警、限流和隐私事件响应；扩为多实例前拆分 Worker。

当前 staging 使用云托管可信入口 actor；如未来引入非云托管入口或非微信客户端，必须重新设计
会话边界，不能复用公网可伪造 Header。

## 9. 上线验收清单

- `callContainer /health/ready` 返回 200，且 Provider、Schema 和依赖符合环境。
- 后端全量测试、Ruff、Mypy、前端测试和结构检查全部通过。
- 真实 AppID 下开发者工具“问题”面板为 0，无游客模式错误。
- `urlCheck=true`；文字、JPG/PNG/WebP、10MB 限制、断网和中断续传验证。
- 两个家庭会话互相返回 404；任何资源 ID 都不能越权读取。
- AI 失败不会产生正式记录；确认后才出现知识点与 Todo。
- 历史补录只生成当前检查；活动不进入记忆曲线。
- DB、HMAC 和 Ark 密钥不在 Git、小程序包、日志、截图和错误响应中。
- 公网关闭；非 owner 图片读取、伪造 actor/fileID/path 和过期 ticket 均失败。
- MySQL 备份恢复、Alembic exact head、双版本窗口和 Job lease 恢复均验证。
- 隐私保护指引、服务协议、类目和审核说明已按微信后台最新要求完成。

## 10. 数据一致性与空库交付检查

```bash
uv run python tools/audit_database.py data/push_kids.db --require-empty
```

空库交付要求 children、subjects、submissions/media、正式学习、知识、Review/Feedback、
活动/日程以及 `review_feedback_requests`、`calendar_event_requests` 全部为 0；同时执行
SQLite integrity/FK、family 归属和中断照片批次可恢复性检查。`--require-empty` 只用于首次
交付或显式清库后的开发环境，已有真实业务数据的升级只运行不带该参数的审计，绝不能为通过
检查删除用户数据。
