# CHORE — 清理阻断后端发布的历史设计脚本 lint

- Status: `DONE`
- Spec revision: `SPEC-20261016-RELEASE-LINT-01`
- User confirmation: `APPROVED — 产品负责人（用户），2026-10-16，当前会话异步确认选择“批准该 Spec，修复 lint 并继续部署（推荐）”。`
- Risk: `R1 — 仅离线设计生成脚本的等价整理，无运行应用变更`
- Owner: `产品负责人（用户）`
- Implementer / merge owner: `Codex`
- Affected Feature IDs: `FEAT-001 / FEAT-010，既有设计生成工具，产品行为不变`
- Current state: `docs/domain/features/FEAT-001-push-kids-mvp.md`、`docs/domain/features/FEAT-010-daily-tasks.md`、`docs/design/frontend/ui/UI-001-parent-miniapp.md`；现有已批准设计与产品事实保持。
- Related task: `BUG-SPEC-20261016-REVIEW-SUBJECT-ORDER-01`

## 问题、范围与设计

2026-10-16 后端修复专项 30 passed / 8 optional MySQL skipped，API/tests/tools 的 Ruff 已通过，但全仓 Ruff 因下列5个历史脚本68处问题失败。5个文件均逐字节等于 HEAD `8b933da`，不是本次 bug 改动引入。发布手册要求必需检查通过，因此先提请单独批准这项范围扩展。

| File | lint issues | Proposed change |
|---|---|---|
| `docs/design/frontend/prototypes/DREV-20261013-SETTINGS-CONSISTENCY-01/render.py` | 35 | 格式、等价字符串拆行、循环中立即使用的 helper 绑定当前循环局部值、lambda改def |
| `docs/design/frontend/prototypes/DREV-20261014-ACTION-PAGER-CONSISTENCY-02/render.py` | 13 | 同上及拆除分号多语句 |
| `docs/design/frontend/prototypes/DREV-20261014-SUBJECT-MANAGEMENT-01/export.py` | 2 | 等价字符串拆行及格式 |
| `docs/design/frontend/prototypes/DREV-20261014-SUBJECT-MANAGEMENT-01/render.py` | 11 | 等价字符串拆行、helper绑定当前绘制列表、格式 |
| `docs/design/frontend/prototypes/DREV-20261014-TODAY-ACTION-STYLE-01/render.py` | 7 | 等价字符串拆行、lambda改def、格式 |

- 调用图：`离线设计脚本 → SVG文本 → rsvg-convert → PNG / 设计manifest`。不进入应用发布包。
- Sequence / state machine / architecture diagram: `N/A — 同步离线脚本的等价整理，不改变执行顺序、产品状态机、模块或部署结构。`
- 推荐：修复脚本并在隔离临时目录验证新旧生成输出一致；不在批准快照目录重跑生成器。
- 替代：只提交已通过的 bug 修复并停止部署，保留全仓门禁失败。拒绝通过忽略 lint、修改校验配置或将旧失败伪装为通过来继续部署。
- Non-goals: `设计重绘、交互/文案/样式变化、修改既有SVG/HTML/PNG/APPROVAL.md、生产逻辑、依赖升级、扩大后端发布内容。`
- Frontend impact: `no — 既有可见设计不变，无新DREV。`
- Frontend engineering impact: `yes — 离线设计生成工具；沿用 FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，重点为设计证据不可变和可重现。`
- Editable design source / exports / new approval manifest: `N/A — 本次不修改设计内容或已批准证据。`
- 回滚：回退5个脚本修改；无数据或运行时回滚。

## 验收与关闭

| Test point | Required evidence | Result |
|---|---|---|
| LINT-001 | 全仓 `.venv/bin/ruff check .` 和 `.venv/bin/ruff format --check .` 通过 | PASS；519文件格式通过 |
| LINT-002 | 新旧脚本在隔离路径执行或拦截文件/绘制输出，生成的SVG内容及可比manifest字段一致 | PASS；隔离执行5个脚本，168个输出逐字节SHA-256一致：82 SVG、81 PNG、5 manifest |
| LINT-003 | `git diff`证明既有SVG/HTML/PNG/APPROVAL.md无修改；当前设计政策校验通过 | PASS；批准设计资产无修改，DESIGN_EVIDENCE_VALID |
| LINT-004 | 发布manifest只含原白名单，5个脚本不在发布包内；逐文件Diff Review确认无行为变化 | PASS；107文件/1239653字节白名单，docs/tests/tools/小程序均排除；Codex逐文件Diff Review通过 |

- Expected documentation changes: 本Spec、`specs/README.md`和本次质量/发布证据；产品事实与设计正文不因等价工具清理而修订。
- 批准后单独提交工具清理，与bug提交区分；完成四项验证和文档核对后设DONE并移入completed，未满足则保留active并记录原因。
- 实际仅修改上述5个脚本；产品实现、设计源和批准快照均未随本chore改变。Feature、Behavior、Architecture与UI正文核对无冲突，无需为等价清理更改产品事实。
- 2026-10-16完成四项门禁，迁移到 `specs/completed/`；证据与逐文件审查见 `docs/quality/evidence/RELEASE-LINT-20261016.md`。关联BUG-029的容器/云发布阶段单独跟踪，不影响本chore完成判定。
