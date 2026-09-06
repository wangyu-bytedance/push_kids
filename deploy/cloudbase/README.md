# 微信云托管发布材料

这里的 JSON 是控制台配置基线，不包含凭据，也不会自动修改云环境。

- `service-settings.json`：容器内端口 8000、单实例、stdout 日志和关闭公网的目标值。首次 smoke
  可短时开启公网，验证后必须关闭。
- `storage-rules.json`：小程序端仅文件创建者可读写。不得改成 public；服务端使用云托管
  环境临时 COS 凭证读取和清理对象。

环境变量按 `.env.example` 的 cloud 段配置。`MYSQL_PASSWORD`、`ARK_API_KEY`、
`PUSH_KIDS_ACTOR_HMAC_KEY` 只进入云托管环境变量/密钥能力，不进入发布包、日志或截图。
云托管在容器启动时注入这些变量；“容器需要密码”不等于“镜像保存密码”。本地 Compose 使用
`.env.runtime` 作为应用变量白名单文件，不读取保存 CLI 密钥的 `.env`。

发布前从可访问 MySQL 内网的受控环境执行 `uv run alembic upgrade head`。应用容器不会自动
建表或迁移；Schema 不在 `20260903_0001` 时会拒绝启动。

控制台“本地代码/源码上传”或 CLI 只使用本地生成的 `dist/cloud-release`：

```bash
uv run python tools/prepare_cloud_release.py
(cd dist/cloud-release && wxcloud deploy --dryRun \
  -e prod-d2g14rwoycac6b45d \
  -s flask-ik19)
```

该目录只含 Dockerfile、Python 依赖锁、云托管构建配置和 API Python 源码，不含 `.env`、`.git`、
测试、文档、图片、本地数据库或 pycache；`release-manifest.json` 记录文件大小和 SHA-256。
工具还会拒绝当前进程持有的 Ark、MySQL 和 actor HMAC 秘密值出现在发布文件中。任何源码变更后
必须重新生成、检查清单并重新执行 Docker 验证，不能复用旧目录或旧压缩包。

使用微信云托管 CLI 部署时，生成目录中的 `wxcloud.config.json` 明确选择 `run` 模式、容器内端口
8000 和现有 Dockerfile，避免 CLI 自动迁移并覆盖已经验证的容器配置。CLI 登录密钥只保存在被
Git 忽略且权限为 0600 的本地 `.env` 中，不得加入发布包。`ARK_API_KEY` 在云托管控制台作为
运行时环境变量配置，禁止通过 Docker build 参数或带值的 CLI 参数传递。
