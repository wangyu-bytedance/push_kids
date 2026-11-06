---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: final
owner: Codex
---

# BUG-033 — 修改前行为基线

- Evidence ID: EVD-20261105-BUG033-BASELINE
- Requirement / acceptance: [BUG-033](../completed/BUG-033-CHILD-ARCHIVE-UI.md)，TP-002 / AC-002..003。
- spec_revision: BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01（用户2026-11-05已批准，配套DREV01）
- subject_revision: base `0576ac30464908154c624effed41df6dfa3110cc`；本轮生产修改前的child-edit三文件及child-profiles/grade-confirmation测试在基线时无Git diff，其他任务dirty工作区保留。
- 方法/命令: `node --test tests/frontend/child-profiles.test.js tests/frontend/grade-confirmation.test.js`
- result: passed

## Scope and output

- 2026-11-05，macOS / Node v22.22.0 test runner，42 tests / 42 pass / 0 fail / 0 skipped。覆盖计数汇总、读失败降级、取消不写、恢复、服务端拒绝、年级确认与冲突路径。
- 修改前SHA-256：`index.js=d38fbe863bc1a8f230fbb1f1b31c65f245446dc00edf02010555d48a874efecf`、`index.wxml=427053c33fc49341400e3bb9aa93074a59935309751b95b8a67a2f8b8d0659d9`、`index.wxss=0dcfcad94fe930385925b744bd98f9264a09a46c870ef2e0e22df1f7a6731288`、`child-profiles.test.js=c45fcc1769c31e49d3b1f17906a0500f37c246a59de73120bb118ed5f2dc8f2c`、`grade-confirmation.test.js=cf3077506034c9604f52b168a13aab97cb0eedf8cf94cacb86e1bc63f6bcdeaf`。
- 视觉问题由现存WXML/WXSS直接定位：重复标题/说明、居中danger-zone与13px文案。行为测试通过不证明其布局符合已批准设计。
- 未覆盖：原生节点、三视口截图、真实设备、读屏；均不能由此基线抵扣。

## Coding slice

- Phase: Baseline。此次为局部呈现与文案语义等价整理；不为CSS和逐字文案制造镜像测试或故意失败。
- Red: N/A；替代可失败验证为冻结设计SHA、原生几何和人工视觉比较。若原生不可用，记录NOT_RUN及剩余风险，Owner为Codex/产品负责人。
- Refactor: 仅删除被替代的页面局部danger样式，无新增抽象或重复路径。
- 本证据只绑定修改前对象；修改后的验证另记EVD，不追认为Green。
