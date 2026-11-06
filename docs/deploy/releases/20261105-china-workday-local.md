# 中国工作日日程本地实施记录

- Date: 2026-11-05
- Release revision: WORKDAY-LOCAL-20261105-02
- Scope: [Spec02/Architecture02](../../../specs/completed/FEAT-001-CHINA-WORKDAY-SCHEDULES.md)；用户“完成这个方案的落地”，随后批准具体DREV02并继续前端实施。
- Stage: LOCAL_IMPLEMENTED / VERIFICATION_PARTIAL，未部署、未迁移云DB、未preview、未上传；体验/审核/正式发布NOT_RUN。
- Lifecycle: VERIFYING，保留`specs/completed/FEAT-001-CHINA-WORKDAY-SCHEDULES.md`。

设置辅导课与日程均可选择工作日，统一时间并回填原模式；中国大陆全国法定放假跳过、调休照常。服务端两表加`workday_only=false`，由activities统一判定日程/今日/建议/冲突/提醒。离线锁定日历覆盖至2026年底，超出覆盖明确警告、跳过工作日项，不猜测。旧星期不同时间与false模式保持。

[版本化EVD](../../../specs/evidence/EVD-20261105-WORKDAY-IMPLEMENTATION-01.md)记录后端专项16PASS、最终全量Python919PASS/52隔离MySQL条件skip、全前端359PASS、静态与三尺寸48组原生节点PASS。完整原生PNG/设备/读屏/独立Review未完成；截图RPC超时。SQLite升级、旧行及重启PASS，全库Alembic check仍FAIL：四个既有learning_records索引漂移在0025与0026一致，工作日表无新增漂移，问题见[ISS](../../quality/issues/ISS-20261105-LEARNING-RECORD-INDEX-DRIFT.md)。本增量隔离MySQL未配置/未执行，不拿历史实库测试代验。

后续依[发布手册](../README.md)先补独立Review、原生/设备及MySQL证据，闭合Schema检查；再从具体验证对象构造最小冻结候选，0025→0026迁移后部署兼容后端，最后上传前端。已有true行时不能回滚到不理解该模式的旧后端或直接降级Schema。遵守现有备份/灰度/smoke/人工门禁，不直接打包当前含并行任务的脏工作区。此处SHA清单仅绑定本地观察对象，不是可直接发布的完整allowlist。

039/Schema0025与已上传0.1.17不覆盖本工作日增量。本任务没有执行云发布，因此未到达发布人工门禁。取得两端各自匹配的云交付后才设开发DONE并移completed；验收缺项仍保留实际状态。
