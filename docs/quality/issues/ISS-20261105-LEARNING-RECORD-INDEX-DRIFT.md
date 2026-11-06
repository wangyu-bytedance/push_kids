---
id: "ISS-20261105-LEARNING-RECORD-INDEX-DRIFT"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: triaged
source: test
owner: "Schema maintainer / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "local 20261024_0025 and 20261105_0026 / HEAD0576ac304649 + workspace"
source_evidence: "docs/quality/evidence/china-workday-20261105/alembic-baseline-comparison.json"
regression_case: "N/A: 未修复，隔离compare_metadata反证保留"
closure_evidence: NEEDS_VERIFICATION
observation_evidence: "原SQLite漂移仍在；发布准备新库及0025→0027隔离MySQL5.7 check无漂移；生产仅只读revision，未执行云DDL"
prevention_control: "Alembic check发布门禁保持；需批准的Schema修订及SQLite/MySQL一致性验证"
closure_reason: "未修复；不能将无新增工作日漂移写成全库检查通过"
---

# 学习记录模型与迁移链的四个单列索引漂移

2026-11-05发布准备补核：当前冻结源码的真实隔离MySQL5.7.44新库到0027、0025到0027，两条`alembic current/check`均无新operations，见[发布记录](../../deploy/releases/20261105-fullstack-update-preparation.md)。这限定本问题已证实的SQLite影响，不将其静默resolved，也不证明生产MySQL所有索引已核。原SQLite重现/待修合同保持；云发布的目标Schema门禁独立执行。

工作日Spec02本地迁移检查发现：从空SQLite迁移到0026后，Alembic check仍建议新增`ix_learning_records_child_id`、`ix_learning_records_family_id`、`ix_learning_records_occurred_at`、`ix_learning_records_subject_id`。预期迁移链与模型metadata一致，实际全库检查FAIL，阻断后续发布检查通过结论。未观察业务数据错误或生产同类差异。

独立临时SQLite先升级0025，以当前metadata去掉本次两个workday_only字段作为旧metadata比较，已有同样四个索引差异；再升级0026用当前metadata比较，差异完全相同，工作日activity_schedules/calendar_events无新增漂移。复现脚本、实际日志及JSON见[本轮证据](../evidence/china-workday-20261105/README.md)。根因已确认到旧迁移链与当前模型声明不一致；产生不一致的具体历史提交及索引是否仍有必要尚未核定，不据此推断生产索引现状。

该问题不属于工作日新增字段授权，不修改旧迁移或静默加索引。需维护者在下次数据库发布前形成明确Spec修订，核对现有租户领先索引、查询计划和真实隔离MySQL，再决定删除冗余模型声明或新增迁移。之后SQLite/MySQL Alembic check、旧数据/查询计划验证及独立Review真实通过，才能resolved；适用上线观察后再closed。Owner Schema maintainer/Codex，复查日期2026-11-06或下次数据库发布准备（取先到者）。
