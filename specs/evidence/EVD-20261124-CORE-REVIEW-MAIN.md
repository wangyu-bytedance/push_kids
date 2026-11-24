---
created: "2026-11-24"
updated: "2026-11-24"
type: evidence
status: recorded
owner: 项目维护者
---

# 主分支修复提交验证

- Spec: [BUG-SPEC-20261124-CORE-REVIEW-01](../active/BUG-20261124-CORE-REVIEW-REMEDIATION.md)。
- Baseline: `a1ea8f61e642271b906575c5b4d202b21a2b0fe3`。源码及测试冻结树 `dcf18984d9e748a425720bb56c4e045eb405c644`，由 14 个 Python 文件的暂存区生成。最终提交另附本次文档和证据。
- Scope: CORE-001 至 CORE-004。13 个文件与[已评审工作区快照](core-review-20261124/review-snapshot-02.json)逐字相同。第 14 个文件 `platform/database.py` 只加入同一 SQLite 事务入口。现有主分支 MySQL Schema head 为 `20261105_0027`。题库代码、依赖它的两个路由改动与 DOC-001 保留在原工作区。
- Result: 本修复的定向检查通过。后端全量和全仓 Ruff 保留已复现的基线失败。云交付仍待补。

| 检查 | 实际结果 |
| --- | --- |
| `pytest tests/unit tests/integration tests/contract -q` | 1,003 通过、62 条件跳过、2 失败。两个失败在原始提交的独立导出中以相同原因复现，见本页下方。 |
| `pytest -q tests/integration/test_family_onboarding.py tests/integration/test_multi_child_profiles.py tests/integration/test_notification_channel.py tests/integration/test_notification_resilience.py tests/contract/test_api_contract.py` | 58 通过，4 条需 MySQL 的用例跳过，在下列隔离库专项执行。 |
| 隔离 MySQL 5.7.44，`alembic upgrade head`、`alembic current`、`alembic check` | 升级至 `20261105_0027`，无迁移漂移。 |
| 同一隔离库，`pytest -q tests/integration/test_mysql_runtime.py tests/integration/test_notification_resilience.py` | 24 通过，包含两个数据库共用的通知恢复用例。覆盖等待中的撤权写入、租约回收和额度交错。 |
| `npm test` | 370 通过。 |
| `ruff check apps/api/src tests tools`、`ruff format --check apps/api/src tests tools`、`mypy apps/api/src`、`python tools/check_architecture.py` | 通过。Ruff 格式覆盖 317 文件，mypy 和架构检查覆盖 156 模块。 |
| `ruff check .`、`ruff format --check .` | 全仓基线仍有 167 条 lint 问题、9 个文件需格式化，均在未改动的 UI 原型脚本。 |
| `python tools/validate_design_evidence.py --check-current-policy`、`python tools/validate_miniprogram.py`、`git diff --check` | 通过。小程序 17 页。 |
| 独立 R3 复评 | 对照暂存树与原快照，复核运行时兼容和已有基线失败。单独复跑 SQLite 额度交错 1 项通过，0 项新增确认问题。 |

## 已复现的基线失败

- `tests/unit/test_release_automation.py::test_backend_unknown_deploy_uses_read_only_polling`。灰度查询夹具的原承载流量条目无 `remark`，旧流程抛出 `KeyError`。
- `tests/integration/test_precise_source.py::test_numbered_photos_remain_bound_to_original_submission`。Node 夹具未提供 `withThemeComponent`，报 `TypeError`。

执行原提交的独立 Git 导出，保留相同失败原因。候选、基线复跑和静态原始日志位于 `/tmp/push-kids-main-review.O0J7PzeT`。真实微信双账号、owner、收件和云部署均未运行。[原工作区证据](EVD-20261124-CORE-REVIEW-IMPLEMENTATION.md)和[独立评审](CORE-REVIEW-20261124-R3.md)各自绑定原快照。
