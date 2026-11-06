# OPS缓存Spec01 — 灰度创建前质量门禁失败

后续成功率排查（独立于下面10/13发布候选）：当前12/15完整原40实际33/40＝82.5%、三科60%/86.7%/86.7% FAIL、正式写0。
[诊断EVD](../../../specs/evidence/EVD-20261101-BUG036-FIXED40-DIAGNOSIS.md)保留阶段与原失败；
[Spec04修复设计](../../../specs/completed/BUG-036-FIXED40-SUCCESS-REPAIR.md)READY_FOR_REVIEW/未实施。原发布manifest、34/40停止证据与039版本状态不变，没有新部署。

- Stage: `BLOCKED_PRE_DEPLOY_QUALITY_GATE`；未创建实际灰度版本。
- Spec: [OPS-SPEC-20261101-BUG036-CACHE-DEPLOY-01](../../../specs/active/OPS-20261101-BUG036-CACHE02-DEPLOYMENT.md)，用户2026-11-01明确“批准 OPS 发布 Spec01，开始灰度部署”。
- Candidate: 冻结10/13，154payload，manifest SHA `a07c0bf32a85afa80c1d69485d0c7d203dca663dddf10cd26f2c88c5c68f612b`；活动11/14不混入。
- Target: `prod-d2g14rwoycac6b45d` / `flask-ik19` / GRAY / 8000。
- Actual version: 仍039 normal、100%/1，PUBLIC关闭；无新版本号，不写已部署或DONE。
- Evidence: [批准后门禁EVD](../../../specs/evidence/EVD-20261101-BUG036-CACHE02-RELEASE-GATE.md)、
  [实际40-case报告](../../quality/evidence/bug036-cache02-release-20261101/live40-report.json)、
  [汇总](../../quality/evidence/bug036-cache02-release-20261101/approved-release-summary.json)。

固定40例实际运行18:30:31–18:37:37 exit1：34/40通过（85%），要求≥38/40；
语文10/15（66.7%）、数学12/15（80%）、英语13/15（86.7%），各科要求≥90%。
0基础设施失败，0空草稿、0剩余pending、0正式写入；6失败case和次数保留全部分母。
原合成材料、规定顺序、原Job尝试及冻结代码不变，未重复抽样、删失败case或换模型。

两份获批工具维护已完成：全库Ruff/格式865通过，AST/嵌入JS内容及syntax通过。
前端349/ESLint/设计policy/17页校验，当前mypy/DAG/head均通过；
冻结候选857/52skip、MySQL5.7新库8PASS和干净dry-run原证据保持。
管理员严格只读Schema及实际应用CRUD账号/ready检查PASS，Schema0025，无DDL或秘密改写。
容器arm64缓存构建质量FAIL后已停止，无健康/SIGTERM结果，NOT_RUN_INCOMPLETE；
两组独立只读Review各0确认工具/代码/包来源问题并明确NOT_READY。资源与手册基线差异、
可选coverage及Worker共存等后续门禁仍未代验；这些通过不会抵消40例FAIL。

按[发布手册](../README.md)必需检查失败即停止，未执行run:deploy、流量调整、生产任务重置、
数据库迁移、正式确认、前端upload/bump或Git提交。HTTP0%不隔离Worker，此时没有新实例进入生产队列。
OPS为BLOCKED/active；缓存/父生成Spec未由该候选云交付，保持原active状态，独立内容03也不由本任务代验。

后续在内容/质量的具体获批修订下修复并独立验收，明确新的发布范围/revision后重新冻结和执行门禁。
不得把活动11/14直接放进10/13旧包，也不得口头把34/40追认为通过。用户授权仍限定适用门禁通过后的灰度创建，
没有全量或跳过FAIL的例外。原失败和本次数据保留，不请求用户批准“带失败上线”。
