---
id: "ISS-20261105-MYSQL-HEAD-ASSERTION"
type: issue
created: "2026-11-05"
updated: "2026-11-05"
status: resolved
source: test
owner: "Schema/test maintainer / Codex"
severity: MAJOR
disposition: confirmed
observed_revision: "0027 / HEAD0576ac304649 + workspace"
source_evidence: "docs/deploy/releases/20261105-fullstack-update-preparation.md"
regression_case: "tests/integration/test_supersession_mysql.py::test_mysql_guarded_downgrade_and_reupgrade"
closure_evidence: "specs/evidence/EVD-20261105-FULLSTACK-OPS01.md"
observation_evidence: "isolated MySQL5.7; production read only0025"
prevention_control: "迁移head前进时更新兼容回归；隔离实库必测"
closure_reason: "批准OPS01仅更新明确head预期0027，同文件13/十文件48真实MySQL通过，独立Review验证其余保护不变；本地resolved，未云交付"
---

# 迁移重升级测试仍断言历史0025

独立MySQL5.7真实执行`upgrade head`得到0027，`tests/integration/test_supersession_mysql.py:281`仍硬断言0025，原12个同文件测试通过，此项FAIL。生产迁移链正常升级/current/check不等于这个回归通过；不能回退head、删迁移或删保护断言来消除FAIL。

根因是新增0026/27后可选MySQL测试预期未同步，默认Python环境skip未暴露。用户批准[OPS01](../../../specs/completed/OPS-20261105-FULLSTACK-UPDATE.md)后只改明确预期为0027，降级拒绝、数据保持、重升级和Schema check保持。批准后5.7.44同文件13PASS、十文件48PASS/0skip及两迁移路径check通过，独立Review核对保护断言原样，现本地resolved；不是生产迁移或云交付，不记closed。首轮harness错误及旧断言失败在原EVD保持。
