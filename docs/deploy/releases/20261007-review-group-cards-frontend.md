# 2026-10-07 复习条目科目组卡 — 前端发布候选

- Scope: `SPEC-20261007-REVIEW-GROUP-CARDS-04` / `DREV-20261007-REVIEW-GROUP-CARDS-01`，仅修改小程序复习条目页和对应前端测试。
- Target AppID: `wx5d2e0014690bf285`；源码目录：`apps/miniprogram`；`useCloud=true`，连接 `prod-d2g14rwoycac6b45d / flask-ik19`，`urlCheck=true`。
- Candidate source tree: 125 文件、711965 字节。按相对路径排序，把每个路径、NUL、对应文件 SHA-256 二进制摘要依次写入 SHA-256 所得：`a4c3b7f11fd8eba3c51e3db249ce68996344d83e9b7d76e3e277a68ba7e38207`。上传前需重算并核对；该值不是微信构建产物摘要。
- `project.config.json` 中存在开发者工具自动加入的 `simulatorPluginLibVersion: {}`；这是工作区的既有附带改动，本次未回退，因而包含在上述目录摘要中。仓库根部无关的 `output/` 不在小程序源码目录内。
- 敏感内容检查：目录内未发现 `.env`、密钥/数据库文件名；文本未发现私钥头、MySQL URL 或扫描规则中的密钥特征。仅代表本次静态扫描，不能替代平台上传清单复核。
- Version baseline `0.1.12`；下一开发版本候选 `0.1.13`，**尚未上传，不推进版本基准**。

## 已完成的本地检查

- `node --test tests/frontend/review-inventory.test.js`：11/11 PASS。
- `npm test`：203/203 PASS；`npm run lint:miniapp`：PASS。
- `npm run check:miniapp`：`MINIPROGRAM_VALID pages=16 source_bytes=711965`。
- `python3 tools/check_architecture.py`：`ARCHITECTURE_VALID checked=3`；`git diff --check`：PASS。
- `python3 tools/validate_design_evidence.py --check-current-policy`：`DESIGN_EVIDENCE_VALID`，只覆盖当前已批准基线，**不代表本候选 DREV 的快照已合格**。
- `uv run python tools/validate_miniprogram.py`：本机 uv 缓存访问 EPERM；直接以 `python3` 运行相同校验脚本通过。
- 微信开发者工具 CLI `islogin` 为 true；`open` 成功打开本地项目，工具显示问题 0、调试器错误 0。目标页新布局的原生节点几何、三视口和真机尚未验收。

## 发布状态与门禁

- 状态：**本地源码已修改并通过自动检查；未生成新版预览二维码，未上传开发版本，未设置体验版，未提审，未发布正式版。**
- `APPROVAL.md` 中现有截图是旧版；新版菜单、动态次数与等宽筛选的 320×568 / 390×844 / 430×932 快照和 SHA-256 manifest 待补。当前 HTML `file://` 浏览器入口受安全策略阻止，不从其他浏览器入口绕过。
- 预览命令被自动审批拒绝：它会把当前小程序构建包传到微信开发者工具关联服务并生成二维码；审核认为本会话此前授权未明确指向这份载荷和外部目的地。未改用界面或其他命令绕过。
- 发布前还需按 `docs/deploy/FRONTEND-RELEASE.md` 完成新版原生三视口、iOS/Android、后端目标版本及双真实账号 smoke，并复核确切上传版本与包内容。
