# 年级弹窗精简 · 设计准备证据 · 2026-10-24

- Task: [Spec01](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)，创建本证据时READY_FOR_REVIEW，后获用户“继续”批准，当前VERIFYING。
- Design: [DREV02](../../design/frontend/prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md)，创建本证据时AWAITING_APPROVAL，后获批准并冻结。
- Design-preparation baseline: 主[FEAT-013](../../domain/features/FEAT-013-annual-grade-promotion.md)当时为DREV01本地实现/VERIFYING；设计准备阶段无业务代码修改。后续实现与原生当前事实见[实施证据](GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)。
- Scope: “孩子名的年级”＋一个picker＋并排“稍后 / 确认”；必要恢复态仅一行提示。无新业务语义。

## Executed design checks

| Check | Result | Evidence |
|---|---|---|
| `python3 docs/design/frontend/prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/render.py` | PASS / HTML_ONLY | [render-report.json](../../design/frontend/prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/render-report.json)：11态×320×568/390×844/430×932，共33张 |
| 精确视口几何/正文/触控 | PASS / HTML_ONLY | 无横溢；所有可见按钮/选择框≥44px且在视口内；检查正文≥14px、内容无裁切；正常高229.89px，错误264.28px，长名261.78px |
| HTML交互 | PASS / SYNTHETIC | 三视口均核对12选项、保留原级、提交禁用、错误保留四年级、稍后、冲突读取后仅展示最新；内存模拟，未访问服务 |
| 人工看图 | EXECUTED | 查看390正常、320错误、320长名裁图；标题/字段/按钮无重叠，错误无大面积卡片 |
| `.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md --allow-pending --check-current-policy` | PASS | `DESIGN_EVIDENCE_VALID`，逐项SHA/文件存在，允许候选待批准 |
| 设计render.py Ruff/format、文档引用与`git diff --check` | PASS | 最终检查结果见本轮工具输出；首轮两处脚本长行已修正 |

源SHA-256：`79c99d4b9cb9ffbc1b04fb226244e0bdaeb7c6baf3d2fa3645ceace58386a98a`。[manifest](../../design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md)含33张SHA，预览裁图SHA在render-report。冻结的DREV01源、57导出和批准记录未修改。

初次`uv run`被sandbox缓存读取权限挡住，未算通过；改用已安装`.venv/bin`完成同等检查。Chrome获得本地渲染权限，仅访问仓库HTML；没有部署、上传或外发数据。

## Documentation and lifecycle audit（设计准备时的历史状态）

- Feature/UI/FrontendDesign/Spec索引只登记“待批准候选”，当前实现正文/版本未被未批准设计改写。旧业务规则仍以主Spec02为准。
- Behavior Catalog、Architecture：业务确认、owner、调用/依赖方向不变，本轮只核对而不增加新事实。工程预算、服务端权限/CAS/队列不变。
- Test evidence：本文件只登记当前设计diff；此前313项前端、DREV01原生节点和真实MySQL证据均不冒充本候选的实施验证。
- Release docs：没有上传/体验/审核/正式发布变化，无新发布记录。原档案归档区BUG-033候选继续独立待批准。
- 设计准备时Spec01处于`specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md`，READY_FOR_REVIEW；当时尚未批准和实施，不能DONE或迁completed。现在已批准并本地实现、处于VERIFYING，当前验收以实施证据为准。主年级Spec02继续active/VERIFYING。

当时新增候选与生产文档的状态有明确区分，无因设计准备引入的代码/文档事实冲突。UI-015原有“锁屏阻断、未采集”与随后已采集段落的差异，已在本次获批实施范围中按证据澄清；具体新布局原生/设备门禁以精简实施证据为准。

## Not run（设计准备时）

生产组件/前端测试、原生节点及交互、iOS/Android、放大字体/读屏：仅设计准备阶段均NOT_RUN，原因是当时具体新设计尚未批准，未开始生产实施。后续实际执行与剩余缺口见实施证据；没有用HTML渲染替代以上门禁。
