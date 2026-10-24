# 档案归档区设计准备 — 2026-10-24

- State: DESIGN_ONLY / AWAITING_APPROVAL / NOT_IMPLEMENTED
- Task: [BUG-033 Spec01](../../../specs/active/BUG-033-CHILD-ARCHIVE-UI.md)，active/READY_FOR_REVIEW。
- Design: [DREV-20261024-CHILD-ARCHIVE-01](../../design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)。
- Source: [自包含HTML](../../design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/index.html)，SHA `b52125179caf4d795ed9da701f5e5bca12bc400ac73a9e99160051b89aa5f576`。
- Exports/SHA: [21张清单](../../design/frontend/snapshots/UI-015/DREV-20261024-CHILD-ARCHIVE-01/APPROVAL.md)，AWAITING_APPROVAL。
- Machine report: [render-report.json](../../design/frontend/prototypes/DREV-20261024-CHILD-ARCHIVE-01/render-report.json)。

用户截图和当前源码共同确认：泛标题下重复解释归档保留历史，正文居中且13px，垃圾桶容易被理解成删除。本候选收为整行操作和一句短说明，详细影响留在原确认框；不改档案业务或年级规则。

## Actual verification

| Command / action | Result | Limits |
|---|---|---|
| `python3 .../DREV-20261024-CHILD-ARCHIVE-01/render.py` | PASS / DESIGN_EXPORTS=21; VIEWPORTS=3; HTML_ONLY | Chrome155.0.8059.85、DPR1、font100%；7态×320×568/390×844/430×932；无横溢、控制≥44px、正文≥14px及控制屏内几何 |
| HTML交互 | PASS / 3视口 | 未完成数量呈现、打开确认、背景inert、Escape取消/焦点返回、提交后禁用；没有业务请求 |
| 目视检查 | EXECUTED | 390普通态，320有未完成及确认态；另核对390局部预览。原表单上下文仅示意，不是新增字段布局设计 |
| `.venv/bin/python tools/validate_design_evidence.py --manifest .../APPROVAL.md --allow-pending --check-current-policy` | DESIGN_EVIDENCE_VALID | 源/导出尺寸及SHA与待批准状态匹配，不等于批准 |
| `.venv/bin/ruff check .../render.py`、`ruff format --check .../render.py` | PASS | 初次长行失败已修正并格式化；源HTML不变，最终重渲染通过 |
| `git diff --check` | PASS | 文档及设计脚本空白检查 |
| 业务前端/后端测试、原生/真机/独立review | NOT_RUN | 尚未批准或实施；不借年级任务313项/原生呈现抵扣本次diff |

## Scope and document closure

设计工作没有修改生产页面。核对年级任务收尾清单：child-edit/index.js SHA仍为`d38fbe863bc1a8f230fbb1f1b31c65f245446dc00edf02010555d48a874efecf`，index.wxss仍为`0dcfcad94fe930385925b744bd98f9264a09a46c870ef2e0e22df1f7a6731288`；WXML亦无本轮修改。保留共享dirty工作区的已有年级和其他任务改动。

已在Spec索引、FrontendDesign、UI-015、FEAT-005登记“待批准候选”，未将提案写成当前已实现行为。Behavior和Architecture经范围核对无需修改当前事实；测试策略/发布状态不变，无上传/部署或业务数据操作。归档资料可编辑描述与既有active门禁的历史差异继续单列，不扩展本修订。

批准前保持Spec active/READY_FOR_REVIEW；批准Spec01+DREV01后才能实施，完成全部适用门禁后才迁completed。原批准年级设计源/57导出保持不变。
