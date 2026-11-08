# GOV-004 — Agent 前端设备检查矩阵（Spec Lite）

- Status: DONE
- Risk: R1，限仓库内前端验证政策及离线工具，可逆。
- Owner / Implementer / Reviewer: 产品负责人（用户） / Codex / Codex（R1 只读复核）
- Date: 2026-11-07
- Spec revision: `GOV-004-SPEC-01`
- User confirmation: 产品负责人（用户） / 2026-11-07 / 本会话审批答复“批准 GOV-004-SPEC-01，按此更新”（`request_user_input_async` `call_07c775726c134e22904e658e520bb6fb`）。
- Affected Feature IDs: 全局小程序检查，以 [FEAT-001](../../docs/domain/features/FEAT-001-push-kids-mvp.md) 为入口；各 Feature 的产品行为不变。
- Feature baseline / merge owner: `FEAT-STATE-20261107-THEMES-02` / Codex，实施后同步 FEAT-001 与 UI-001 的全局检查引用，页面专项历史证据保留原结果。

## Frontend design and engineering impact

- Frontend impact: NO。页面、样式、交互和可访问性语义无变动。新 DREV、原型、设计导出、快照批准为 N/A；现有批准清单及 SHA-256 冻结。
- Frontend engineering impact: YES。影响全局视口、设备抽样及工具默认配置。当前 `FDB-20260913-04` / `FEC-20261007-NATIVE-GEOMETRY-02`；候选 `FDB-20261107-05` / `FEC-20261107-AGENT-DEVICE-MATRIX-03` 只修订验证覆盖范围。触区、安全区、大字、键盘、读屏、长文案、资源预算及六主题检查规则沿用。

## 1. 问题与目标

`AGENTS.md`、FDB、FEC、测试策略、Review 和部分发布指引把 320×568 列为常规必查项。`tools/validate_design_evidence.py` 对所有清单硬编码三档要求，`tools/preview/render.js` 默认生成三档预览，原生脚本也存在旧矩阵引用。只调整 Agent 文案会让离线设计检查继续要求 320×568。

Agent 日常原生几何、截图和新设计导出采用以下两个竖屏逻辑视口，覆盖受影响页面、实际共享组件宿主、相关状态及六主题。

| 视口 | 代表机型 | 用途 |
|---|---|---|
| 390×844 | iPhone 14 | 标准尺寸，作为日常主检查档 |
| 430×932 | iPhone 14 Pro Max | 大屏和顶部安全区代表档 |

后续 iPhone 机型可在涉及具体机型差异时补查，日常按视口抽样。320×568 等低分辨率、iPhone mini 和华为系列退出日常 Agent 检查。设备点数参考 [Apple 布局指南](https://developer.apple.com/cn/design/human-interface-guidelines/layout)。

## 2. 范围与证据边界

- 新矩阵覆盖设计导出、HTML 近似走查默认值、原生几何/截图检查及 Review；模拟器实际 `screenWidth`/`screenHeight` 与截图和节点证据绑定。HTML 结果只作辅助。
- 17 路由与 8 共享状态的全局默认矩阵为 `(17 + 8) × 6 × 2 = 300` 组；DESIGN-003 的 7 个新增运行态在新矩阵下为 `7 × 6 × 2 = 84` 组。局部改动只覆盖实际受影响宿主和状态。
- 已批准 DREV 的设计导出和已有运行报告保留原矩阵、结果与 SHA。DESIGN-002/003 等在途任务的后续通用 Agent 检查引用新矩阵，已有逐项执行结果按原轮次记录。专项设备复现按各任务明确的合同执行。
- 发布阶段的现有跨平台、隐私授权、相册/相机、后台恢复和人工操作门禁继续按发布指引执行；如既有发布要求 Android 平台验证，代表设备选用非华为机型。iOS 代表机型选 iPhone 14 或更新的非 mini 机型。
- 产品运行兼容性、平台能力检测、API、业务和数据无变更。历史脚本显式传入旧尺寸的取证或复核能力保留为历史兼容，默认计划不再枚举旧尺寸。

## 3. 影响地图与必需视图

- Link/call graph：`AGENTS.md` / `REVIEW.md` → FDB / FEC → 测试策略与当前任务 → 设计证据校验、预览、原生取证 → 版本绑定证据。发布专项另由 `docs/deploy/FRONTEND-RELEASE.md` 指向当前矩阵和既有平台门禁。
- Sequence diagram：N/A。离线规则和默认枚举更新，不涉及运行时调用时序。
- State machine：N/A。无业务状态转换；证据继续独立记录 PASS / FAIL / PARTIAL / NOT_RUN。
- Architecture diagram：N/A。无生产模块边界、依赖方向、共享抽象或扩展点变更。

| 方案 | 取舍 | 决定 |
|---|---|---|
| 两个现有的 iPhone 14 系列代表视口 | 减少同一状态的重复截图，保留标准/大屏及安全区代表 | 推荐 |
| 仅检查 390×844 | 工时更低，缺少大屏与另一类顶部安全区证据 | 不采用 |
| iPhone 14 起逐型号全量检查 | 对机型差异覆盖更细，重复执行相同视口和状态 | 仅专项按需选机 |

## 4. 预期变更和兼容

| 位置 | 变更 | 原因 |
|---|---|---|
| `AGENTS.md`、`REVIEW.md`、FDB/FEC、`TEST-STRATEGY.md` | 用当前矩阵替换生效的三档要求 | 避免 Agent 和 Review 读取冲突指令 |
| `tools/validate_design_evidence.py`、`tools/preview/`、适用原生取证入口及专项测试 | 将新批准/默认走查与旧版证据校验区分；适用默认矩阵引用同一离线数据源 | 默认检查可执行，旧清单仍可复核，避免硬编码漂移 |
| 发布指引、微信 API 验收条目、在途主题 Spec 和 FEAT/UI 当前状态 | 同步当前引用、设备规则与历史证据边界；检查其余实际消费者 | 避免在交付阶段重新引入低分辨率或指定华为设备 |
| `specs/STATUS.md`、本 Spec 与版本证据 | 记录批准、验证和归档结论 | 建立可追溯的本地治理交付 |

权威路径为 FDB 视口矩阵及其离线工具数据。清理生效入口中重复的旧三档规定，旧批准清单和显式历史复核保留原版本语义。回退以本任务增量为单位，保留工作区已有主题调优和证据。

## 5. 验收与测试点

| 测试点 | 验收 | 验证方式 |
|---|---|---|
| TP-01 | 默认只检查两档代表视口，低分辨率、mini、华为退出日常矩阵，六主题及状态覆盖仍生效 | 核对 Agent/FDB/FEC/质量/发布/在途 Spec 链路；验证默认预览只生成 390/430 产物 |
| TP-02 | 新两档清单通过，任一档缺失时失败；旧批准三档清单按原要求和哈希验证 | 新增或调整 `tests/unit/test_validate_design_evidence.py` 的针对性用例，先观察旧逻辑的预期失败，再运行专项 pytest，对比历史 manifest 校验结果 |
| TP-03 | 当前原生取证使用正确的两档逻辑尺寸，保留已有历史证据复核 | 用无设备的脚本检查/参数验证覆盖矩阵选择；原生界面实测独立记载 |
| TP-04 | 当前规则、历史快照和代码一致，业务和发布阶段无改动 | `uv run python tools/validate_design_evidence.py --check-current-policy`、`git diff --check`、受影响链接和快照检查、只读差异复核 |

## 6. 实施、验证与归档

1. 记录对 `GOV-004-SPEC-01` 的明确批准。冻结旧矩阵用例，重现新清单在旧校验器的实际失败。
2. 同步默认工具和生效政策，按 TP-01 至 TP-04 验证；按实际结果记录未运行项。
3. 对照 Feature、Behavior Catalog、Architecture、UI current state、Spec、证据与发布指引。治理在本地规则和工具验证完成后标 `DONE` 并迁 `specs/completed/`；产品云端交付及其历史验收独立。

- 交付：本地治理配置与工具已生效，当前为 `FDB-20261107-05` / `FEC-20261107-AGENT-DEVICE-MATRIX-03`，与 [版本化矩阵](../../tools/frontend_viewports.json)一致。主题取证默认写入 `dist/theme-native/`，归档可显式指定独立输出目录。
- 实施前基线：`uv run pytest tests/unit/test_validate_design_evidence.py -q` 为 9 PASS；`uv run python tools/validate_design_evidence.py --check-current-policy` 和 DREV09 的 `--manifest` 校验通过。遍历 `docs/design/frontend/snapshots/*/*/APPROVAL.md` 并调用 `validate_manifest(..., require_approved=False)`，84 份清单中 44 份通过、40 份已有元数据、路径、哈希或状态等校验缺项；这些结果用于对比旧清单行为。
- TP-01 至 TP-04 本地通过，前端 369 项与设计证据 13 项通过，84 份历史清单诊断逐份一致。[版本证据](../evidence/EVD-20261107-GOV004-AGENT-DEVICE-MATRIX.md)记录 Red/Green、实际 Chromium 预览、原生入口替身、历史重放、复核和未运行项。
- 治理任务 `DONE/completed`。原生、真机和可访问性没有在此任务执行，DESIGN-002/003 的产品验收和云交付继续在各自 Spec 记录。
