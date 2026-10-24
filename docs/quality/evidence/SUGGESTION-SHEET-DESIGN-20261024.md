# 学习建议弹层批注 — 设计阶段历史证据

- Date: 2026-10-24
- Scope: SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01 / DREV-20261024-TODAY-LEARNING-02。
- State at capture: DESIGN_ONLY / AWAITING_APPROVAL / NOT_IMPLEMENTED / NOT_RELEASED。以下描述设计阶段当时的状态；之后用户已批准并本地实施，当前事实见[实现证据](SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)，不将此历史阶段的NOT_RUN作为当前结论。
- Sources: [Task Spec](../../../specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md)、[Frontend Spec](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md)、[84张SHA清单](../../design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-02/APPROVAL.md)、[render-report.json](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/render-report.json)。

## 1. 实际执行

命令：`.venv/bin/python docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/render.py`。首次受沙箱限制Chrome退出；经工具审批启动隔离Chrome/155.0.8059.85后成功，退出码0。仅file合成原型、临时Chrome profile，没有访问后端、真实儿童资料或模型。

- 28态×320×568、390×844、430×932，84份PNG。检查所有活动控件≥44px、横向包含、两列按钮等宽/8px间距、正文最小可滚动空间、固定底部可达，PASS。
- 12条点击转移：确认、换项、暂缓、编辑/保存返回、失效重新生成、失败重试、实际部分/完成、删除换项、早复习完成/原内容；PASS。
- 确认过渡中所有操作/关闭禁用，Tab循环，Escape不能中断正在确认、普通关闭后焦点回查看建议；PASS。无Runtime异常。
- 目视检查：390主态、320长中文标题、430主态；学习标题优先，主次操作清晰。长内容允许正文滚动，截图中的裁切是滚动视窗，未隐藏正文。
- IAB拒绝打开file协议，因此不继续绕过浏览器URL策略；使用已有本地导出图审阅。该限制与原型导出是否通过分开记录。

## 2. 设计阶段完整性与文档核对

最终检查均已实际执行：

- 新候选：`.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-02/APPROVAL.md --allow-pending --check-current-policy`，`DESIGN_EVIDENCE_VALID`。
- 旧批准：`.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-01/APPROVAL.md`，`DESIGN_EVIDENCE_VALID`；78张PNG及源SHA仍匹配。
- 新renderer的Ruff check及format --check通过；初次check发现3处长行，已仅换行修正（不改HTML/导出或JS语义）。
- 三份本轮Spec/Frontend Spec/证据全部相对链接检查0缺失；`git diff --check`通过。Feature/UI/设计与Spec索引的新增候选链接与当前实现措辞核对一致。

新HTML SHA-256：`0215d1d3f1be2ad080ecf49156c33bedb044034c962703a225b8a865d5321d66`。代码/文档冲突核对未发现新增冲突；没有将候选替换为当前实现事实。

| 文档/路径 | 本次事实与核对 |
|---|---|
| FEAT-004 | 仅登记待批准候选；本地功能仍为主Spec04/Design01 |
| UI-001、设计索引、Spec索引 | 明确候选和既有实现；没有用新设计结果代替旧原生验收 |
| Behavior Catalog | 复核BHV-045，家长审批/真实记录/暂缓换项语义不变，无领域正文修改 |
| Architecture | 复核today-learning单领域组件与服务端所有权；无边界/依赖方向/扩展点变化 |
| 既有发布文档 | LOCAL_IMPLEMENTATION/VERIFYING/未发布仍成立；此次没有上传、部署、开关或版本变更 |
| 两份主Spec04 | 仍active/VERIFYING，本次候选不解除已有MySQL/原生/真机/内容/独立评审缺口 |
| 新弹层Spec01 | active/READY_FOR_REVIEW，待具体批准；不能因原型完成移为DONE |
| DREV01 | 冻结HTML/PNG/SHA保留，尚不追加Superseded by，因为DREV02未批准 |

## 3. 设计阶段未执行项

新设计的生产组件修改、npm/ESLint/小程序静态回归、原生三视口、代表iOS/Android、读屏/大字体/安全区均NOT_RUN，原因是新具体修订待批准。此次为原型展示调整，未运行后端全量测试；主实现760/295等历史自动化不代验本修订。

批准后按Spec01在原组件实施并补齐验证。领域功能原有发布验收仍由主Spec04独立管理。
