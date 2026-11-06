---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: final
owner: Codex
---

# 工作日覆盖警告 · 停用活动 Red

Spec02 AC-003/TP-002的既有科目可见性兼容边界。作者收尾检查发现calendar_warning未像日程投影一样排除已停用科目。真实API创建工作日活动、查询2027有警告，再停用科目后查询，预期警告为null；实际仍有warning。

- Pre-fix service SHA-256: `e15f01eca5527e5b371ada4734b4b7388e0f90395330f6982e885bcee3786cf9`
- Red test SHA-256（格式化前）: `a3f6118b5f2fb39b2fd437033d31eac8c735ed24a378ac66e2883cee3d293e2d`
- Command: `uv run pytest tests/integration/test_china_workday_schedules.py -k hidden_activity -q`
- Result: `1 failed / 10 deselected`，0.43s；失败为warning字典不为None，非环境/fixture失败。
- Raw log: `docs/quality/evidence/china-workday-20261105/logs/hidden-red.log`

修正仅给existing bounded warning query加同family/child科目join和active过滤，与已批准共享投影语义一致，仍最多两次limit1查询；不改停用行为、权限或数据。最终Green与完整回归、版本SHA独立保留于实施EVD，不覆盖本Red。
