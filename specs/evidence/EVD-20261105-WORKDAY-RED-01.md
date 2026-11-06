---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: final
owner: Codex
---

# 工作日日程 · API行为 Red

- Evidence ID: EVD-20261105-WORKDAY-RED-01
- Requirement / acceptance: specs/completed/FEAT-001-CHINA-WORKDAY-SCHEDULES.md / TP-002/003/004/011
- spec_revision: SPEC-20261105-WORKDAY-02
- subject_revision: HEAD0576ac30464908154c624effed41df6dfa3110cc + dirty workspace。test SHA256 2cc8a4ae13387f761c6d366ef0dc2cfa3f7be816cd47b0f46b202b7d67f790cc；schemas 437cdfc10dff495291c872d8cb58fd26fbb39b0074875deb110add129355628e；service eee107d7b369f220d6003afcd42b8465b8e150d7eb116f91710bf11562d21e2e。生产实现尚未修改。
- 方法/命令: `uv run pytest tests/integration/test_china_workday_schedules.py -q`
- result: failed

## Scope and output

2026-11-05，本地Python3.12/SQLite test client。9例：6 failed、3 passed，2.41s。
预期失败：API缺workday_only；混用模式200而非422；同幂等key不同模式未冲突；工作日活动被旧规则拒绝；放假日仍生成日程提醒occurrence。3个旧校验恰好已拒绝错误输入，不视为新功能实现。
首败保留于本会话工具输出；无原始用户数据或外部写入。此前错误alembic配置路径是准备命令失败，非Red；使用根alembic.ini已确认head20261024_0025。

## Coding slice

- Phase: Red；API与共享投影切片。
- 预期/实际：缺失工作日行为已由真实API断言捕获，非import或环境失败。
- Related Green: 后续独立证据，不能覆盖此记录。
- 未覆盖：纯策略全年边界、迁移、原生UI、通知入队与年度演练继续补测。
