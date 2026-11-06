# 2026-11-01 — BUG-036 内容Spec03本地12版本

- Stage: LOCAL_IMPLEMENTED / VERIFYING。没有本任务BACKEND_DEPLOY、客户端upload、体验、审核或正式发布。
- Approved scope: [内容Spec03 / Architecture03 / Prompt05](../../../specs/completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)；用户“批准 BUG-036 内容 Spec03（含 Architecture03、Prompt05）”，授权本地实施、隔离/只读验证及文档同步。
- Frozen source: `staged-20261101-12` / `child-aware-history-agent-20261101-15`；[11文件源码清单](../../../specs/evidence/bug036-content03-20261101/candidate12/manifest.json)对批准10/13基线与11/14增量独立留存。
- Verification: [12 EVD](../../../specs/evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)，166专项/896全量PASS、52条件skip；全库lint/format、mypy151、架构4/151PASS；两项Review修复、第二轮0新确认问题。最终原30为20产出/10内容PASS/9严格PASS＋1正确拒绝，原六PASS回退3；补充0/3、边界7/10严格通过，内容FAIL。成功请求资源留证、最大9图SDK/云及失败成本未验；51/61表指纹一致、10表变化归因未证，资源/审计PARTIAL。清理与文档闭合按EVD实际记录，不由机制PASS替代。
- Backend/API/DB/UI scope: 原图/完整输出核验、正式证据与置信度owner、素材账本、限定纠正及真实HTTP body字节计数。保留缓存02终态、明确retry/事务、公开API、Schema和UI；本轮没有DDL/生产Job或缓存重置/自动确认/Git提交。

旧云039/staged06及旅行0.1.17不覆盖12/15。另一个缓存发布准备包是154文件10/13，
其候选测试/dry-run与本地内容12固定源验收不同；本记录不修改那个包或发布阶段。
后续发布按[既有门禁](../README.md)准备并核对匹配范围与源码，取得对应授权和人工门禁；
不得因0% HTTP流量推定同库Worker不会工作。

Spec保持VERIFYING，`specs/completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md`；
本地验证不满足云交付/DONE归档规则。内容失败和未验设备/Worker/MySQL/云资源独立。
