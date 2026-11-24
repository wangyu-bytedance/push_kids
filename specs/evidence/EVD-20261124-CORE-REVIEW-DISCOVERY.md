---
created: "2026-11-24"
updated: "2026-11-24"
type: evidence
status: recorded
owner: Push Kids maintainer
---

# 2026-11-24 评审发现基线与原型脚本验证

- Evidence ID: `EVD-20261124-CORE-REVIEW-DISCOVERY`。
- Requirement: 本地原评审报告 Q-001。后端基线见 [Spec 发现阶段](../active/BUG-20261124-CORE-REVIEW-REMEDIATION.md)。
- spec_revision: `BUG-SPEC-20261124-CORE-REVIEW-01`（待批准；Q-001 为独立机械修复）。
- subject_revision: 基准 `760adeed5169c0ff53a8f145544c9de56499b497` 加既有工作区修改。脚本 SHA-256 首次 `cc602b7ad6e693805a4a2201996746a625624c7a80011d7c3066f8f6629a2841`，修订后 `296ab099c8c3ac03373a0d32a09eca9a81a43bf793a0029de6fb6c47bb45cca0`。
- Result: `passed`，限 Q-001、一般后端及所列隔离 MySQL 基线。

| 阶段 | 实际命令及结果 |
| --- | --- |
| Q-001 基线 | `.venv/bin/ruff check . --output-format concise` 失败，18 E501 + 1 B023，全部在竞赛原型 `render.py`。 |
| Q-001 验证 | Ruff 0.16.5。`uv run --no-sync ruff check .`、`uv run --no-sync ruff format --check .` 均通过，1,176 个文件符合格式。 |
| 设计证据 | `uv run --no-sync python tools/validate_design_evidence.py --check-current-policy`、`uv run --no-sync python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261115-COMPETITION-LEARNING-01/APPROVAL.md --allow-pending` 均返回 `DESIGN_EVIDENCE_VALID`。 |
| 原型对照 | macOS arm64。使用临时环境的 Playwright 1.60.0 和本机 Chromium headless shell build 1248，在两个临时目录分别执行原版及修订版 `render.py`。两次交互检查均覆盖 390×844 和 430×932。两版 HTML、清单及全部 228 张 PNG 逐字节相同。仓库设计来源、候选清单及截图未重写。默认 Chromium 缓存版本不匹配的初次启动失败，以指定本机已安装 Chromium 路径恢复。目录 `/tmp/push-kids-review-20261124.T8vqb8/`。 |
| 后端基线 | Python 3.12.11，pytest 8.4.2。`uv run --no-sync pytest tests/unit tests/integration tests/contract -q --tb=short`，1,166 通过、84 跳过，199.84 秒。此命令未提供隔离 MySQL 测试 URL。 |
| 静态及文档闭环 | `uv run --no-sync mypy apps/api/src` 通过，183 个源文件，含未注解函数体默认未检查提示。`uv run --no-sync python tools/check_architecture.py` 通过，5 条策略、183 模块。`git diff --check` 通过，15 个新增文档内部引用存在。仅脚本修复可归入本地已验证，Feature／Behavior／UI／发布正文无由该脚本引起的事实变动，待批准的应用事实仍列在 active Spec。 |
| MySQL 首次环境验证 | Docker 恢复，临时容器 `SELECT VERSION()` 返回 5.7.44。首轮 12 个自建库的题单用例通过。其余 10 失败、3 设置错误，分别受初始库未迁移、数据库名约束和字符集配置影响。此轮结果保留为环境基线缺项。 |
| MySQL 修正环境后基线 | 同版本隔离容器，统一 utf8mb4，运行库升级到 `20261115_0030`，年级和续订迁移各用独立空库。`uv run --no-sync alembic upgrade head`、`current`、`check` 均通过，无新升级操作。`uv run --no-sync pytest tests/integration/test_mysql_runtime.py tests/integration/test_review_worksheet_mysql.py tests/integration/test_grade_confirmation_mysql.py -q --tb=short` 为 23 通过。`uv run --no-sync pytest tests/integration/test_notification_renewal_mysql.py -q --tb=short` 为 2 通过。 |

本地基线未新增 CORE-001 至 CORE-004 的 Red/Green 用例，未进行独立实施评审、原生真机验证、真实微信投递或云部署。新测试和实际发布证据分别随其版本补记。
