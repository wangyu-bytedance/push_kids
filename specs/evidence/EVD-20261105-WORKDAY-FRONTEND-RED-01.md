---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: final
owner: Codex
---

# 工作日日程 · 前端行为 Red

- Evidence ID: EVD-20261105-WORKDAY-FRONTEND-RED-01
- Requirement / acceptance: SPEC-20261105-WORKDAY-02 / TP-005/010/011
- spec_revision: SPEC-20261105-WORKDAY-02
- subject_revision: HEAD0576ac30464908154c624effed41df6dfa3110cc；settings/calendar生产代码编码前原状。Red阶段未单独留存完整测试文件SHA，这是证据缺口；后续清单绑定最终10例版本，不能冒称原6例Red快照。
- 方法/命令: `node --test tests/frontend/workday-schedules.test.js`
- result: failed

6例全部预期失败：原代码无工作日回填、保存时未确认异时星期替换、工作日时间未校验、日程系列起始日期未回填、活动来源不能定位原编辑器、覆盖警告缺失。运行58.98ms；实际页面VM+真实模块，仅替换API与wx。不是import/环境错误。

Phase Red。具体DREV02审批尚待回复，未提前修改生产前端；获批后Green独立留证。本HTML设计60导出和测试均不替代原生/设备/读屏验收。
