# BUG-033 — 本地实施交接

- Updated: 2026-11-05 Asia/Shanghai，Codex。
- Spec: [BUG-033 Spec01](../../../../specs/completed/BUG-033-CHILD-ARCHIVE-UI.md)，VERIFYING / active。
- Base: `0576ac30464908154c624effed41df6dfa3110cc`；共享dirty工作区，无commit；本轮源码仅child-edit三文件及child-profiles测试2个断言。
- Feature merge: FEAT-005 revision `FEAT-STATE-20261105-CHILD-ARCHIVE-UI-04`，UI-015 `UI-STATE-20261105-CHILD-ARCHIVE-06`；相关索引/Behavior/本地发布记录已同步。FEAT-013仅回归，Architecture无边界变更。
- Approval: 用户2026-11-05“批准”明确对应BUG-033 Spec01 + DREV01；FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02。源SHA与21张批准PNG冻结，禁止重新运行render.py覆盖。
- Evidence: [本轮EVD](../../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)、[版本清单](source-manifest.json)。42定向、349前端及适用静态PASS；320/390/430各7态原生几何PASS。
- Pending: 原生PNG/系统确认框、真机/大字/读屏/焦点与独立只读Review；截图RPC超时、CUA白图未作证据。helper支持重新采集；在`/private/tmp/push-kids-archive-native-20261105`离线合成项目执行，不触碰真实家庭。
- Recovery: 截图环境就绪后去掉`NATIVE_SKIP_SCREENSHOTS=1`补原生截图与交互；独立Reviewer按REVIEW绑定source-manifest审查。未完成验收不标PASS。
- Release: 本增量未上传；匹配源码的成功开发上传后按GOV-002更新DONE并迁completed，修引用；验收与体验/审核/正式发布独立。
- Rollback: 仅撤回本任务3个生产文件和2个测试断言的diff；保留年级逻辑和其他并行任务修改。无数据库或后台恢复操作。
- Out of scope: 中国工作日日程Spec02仍待批准；多家庭Spec已取消；并行BUG-036代码/文档保留。既有归档资料编辑合同与active门禁差异见EVD，不在本UI增量变更。
