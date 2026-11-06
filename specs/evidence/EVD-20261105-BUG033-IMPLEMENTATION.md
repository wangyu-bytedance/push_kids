---
created: "2026-11-05"
updated: "2026-11-05"
type: evidence
status: partial
owner: Codex
---

# BUG-033 — 已批准归档UI的本地实施与验证

- Evidence ID: EVD-20261105-BUG033-IMPLEMENTATION
- Requirement / acceptance: [BUG-033 Spec01](../completed/BUG-033-CHILD-ARCHIVE-UI.md)，AC-001..005 / TP-001..005。
- spec_revision: BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01
- subject_revision: base `0576ac30464908154c624effed41df6dfa3110cc`；未提交源码与测试SHA逐项见[source-manifest.json](../../docs/quality/evidence/child-archive-ui-20261105/source-manifest.json)，本任务文档/脚本/证据完整内容哈希见[task-snapshot.json](../../docs/quality/evidence/child-archive-ui-20261105/task-snapshot.json)。共享工作区其他任务修改不属于本补丁，共享文档保留并行内容。
- 方法/命令: 下表列明实际命令和范围。
- result: passed（仅本地实现、自动化、设计冻结哈希及原生几何）；完整原生/设备验收与独立Review为not_run，整体验收PARTIAL。

## Approval and coding slice

用户2026-11-05“批准”直接回复展示390×844 PNG并要求“批准 BUG-033 Spec01 + DREV01”的请求；编码前已记录Spec/Design APPROVED。批准源SHA `b52125179caf4d795ed9da701f5e5bca12bc400ac73a9e99160051b89aa5f576`与21张导出保持原字节。

Baseline见[独立阶段EVD](EVD-20261105-BUG033-BASELINE.md)：42/42通过，原CSS仍有居中长文与13px，不能据此视作视觉合格。此次为局部呈现/等价文案整理，Red N/A（不写逐字/CSS镜像测试）；替代可失败验证为冻结哈希、三视口原生矩形和待补截图。Green仍42/42，全前端349/349。Refactor只删除失去消费者的旧局部样式，未建立新组件/共享抽象。

## Executed verification

环境：macOS / Node v22.22.0；原生微信开发者工具Stable 2.01.2510290，基础库3.17.4，字体15；320×568 DPR2、390×844/430×932 DPR3。无后台/数据库/配置/依赖修改。

| Point | 实际命令/验证 | 结果及边界 |
|---|---|---|
| TP-001 | `uv run python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-015/DREV-20261024-CHILD-ARCHIVE-01/APPROVAL.md --check-current-policy`；逐项重算21 PNG SHA/签名/尺寸 | PASS，APPROVED manifest；没有重渲染或改批准源。2026-10-24 HTML交互证据仅保留原范围 |
| TP-002 | `node --test tests/frontend/child-profiles.test.js tests/frontend/grade-confirmation.test.js` | 42 pass / 0 fail / 0 skip；[原输出](../../docs/quality/evidence/child-archive-ui-20261105/focused-green.tap) |
| TP-003 | `npm test` | 349 pass / 0 fail / 0 skip；[原输出](../../docs/quality/evidence/child-archive-ui-20261105/frontend-green.log)；含其他任务当前共享代码，不声称其属于BUG-033 |
| TP-003 | `npm run lint:miniapp` | PASS |
| TP-003 | `uv run python tools/validate_miniprogram.py` | PASS，17 pages / source_bytes=1234126，绑定当时共享工作区 |
| TP-003 | `uv run python tools/check_architecture.py` | PASS，4 policies / 151 modules，runtime/lazy DAG；本次无模块/依赖/事务/开放点变化 |
| TP-003 | `git diff --check` | PASS；最终文档同步后再核对 |
| TP-004 | `python3 docs/quality/evidence/child-archive-ui-20261105/prepare-native.py`；官方CLI `auto --project /private/tmp/push-kids-archive-native-20261105 --auto-port 9612`；分别执行`NATIVE_SKIP_SCREENSHOTS=1 node docs/quality/evidence/child-archive-ui-20261105/collect-native.cjs 320`、`390`、`430` | 原生几何21组PASS：active/unfinished/archived/working/restoring/error/editor各三视口；[节点目录](../../docs/quality/evidence/child-archive-ui-20261105/native)与SHA在manifest。操作行84px、标题17px、说明/提醒14px，左对齐、无横溢；进行中移除箭头，editor无操作卡。**不是完整视觉验收** |
| TP-004 | `...collect-native.cjs 430 confirm-unfinished`（同样skip截图） | 仅确认前页面几何；未采到系统对话框正文/按钮/截图，不作确认框验收PASS |
| TP-005 | 实施者按REVIEW-20261028-01核对目标diff、调用链及Feature/Behavior/UI/Architecture/Spec/发布记录 | 本次范围自查0个已确认新问题；独立Reviewer尚未执行，TP-005为PARTIAL |
| 辅助脚本 | `uv run ruff check docs/quality/evidence/child-archive-ui-20261105/prepare-native.py`；同路径`ruff format --check`；`node --check .../collect-native.cjs` | PASS，无新依赖 |

## Native limitations and first failures

- 临时项目复用既有grade离线fixture，`useCloud=false`、family/child均synthetic，所有业务写入拒绝。WXML/WXSS与本次源码字节一致；JS只增加一个fixture setData方法，剥离后与生产源码一致，已逐项核验。没有访问真实家庭或写云端业务数据。
- 首次按430调用时实际为390×844，前置断言拒绝，未保存错名截图。按真实390重试后导航RPC一度超时；再初始化及直接发起导航后页面已加载。设备切换后的首次导航出现`Uncaught [object Object]`，页面就绪后重试采集成功。均为采集环境失败，不记为产品Red。
- `App.captureScreenshot`超时；CUA应用截图为白色区域，不能作为视觉证据。尝试重新初始化仍无有效截图，随后显式skip截图只采集几何；未保存/冒称白图为验收图。原生确认框未取得可审核结果。
- 因此TP-004为PARTIAL；三尺寸PNG、原生确认/取消及真正点击重试、iOS/Android、大字、读屏/焦点、长姓名/长数量压力场景仍NOT_RUN。已批准HTML不能抵扣。Owner为Codex/产品负责人；恢复条件为开发者工具有效截图与设备环境就绪。

## Per-file necessity and placement audit (self-check)

| 文件/范围 | 必要性、位置、残留 |
|---|---|
| `apps/miniprogram/pages/child-edit/index.wxml` | necessary / correct；权威页面替换局部归档/恢复呈现，原角色条件、handlers、年级表单保留 |
| 同目录`index.wxss` | necessary / correct；实现批准几何，删除card-head/c-t/c-s/danger-zone/danger-copy/danger-link旧局部样式，无隐藏溢出或全局覆盖 |
| 同目录`index.js` | necessary / correct；仅3处文案，计数读取、确认/取消、working、错误及生命周期流程未变 |
| `tests/frontend/child-profiles.test.js` | necessary / correct；仅更新2个旧长句断言，仍调用真实页面并检查实际归档请求和禁止新增提示，不新增镜像测试 |
| Spec、设计审批manifest、FRONTEND-SPEC | necessary / correct；记录用户具体批准和实际验收阶段，源/导出未动；年级DREV01只加局部Superseded by指针 |
| FEAT-005、Feature索引、BHV、UI-015、FrontendDesign、Spec索引 | necessary / correct；被替代的归档长文/危险区正文已改写；既有其他任务修改保留 |
| 本EVD/Baseline、原始日志、native JSON/SHA、采集脚本、Handoff/本地发布记录 | necessary / correct；版本化可复核结果与未完成项，均不进入生产包 |

未发现本次新增无主/重复业务路径或需要删除的其他代码；无questionable/unnecessary/misplaced文件结论。此为实施者自查，不能代独立Review；本会话没有独立Reviewer上下文，Owner为后续独立Reviewer/产品负责人，恢复时按上述快照复核。

## Documentation consistency and remaining boundary

- 本次归档/恢复卡和文案已与FEAT-005、UI-015、FrontendDesign、BHV对应呈现事实对齐，旧“档案状态/建议先处理完/处理中”不再作为本页当前合同。FEAT-013只回归同页，年级权威逻辑及批准快照未改。
- Architecture与约束已核对，无边界/调用/协议/数据变化，不制造新ADR或修改架构事实。API/Schema/后台测试N/A（纯前端呈现范围），未声称运行pytest/mypy或后台部署检查。
- 既有FEAT-005/归档BHV-025“档案资料仍可编辑”与`children/service.py::update_child`的active门禁存在差异；已在获批BUG-033 Non-goals中列明，由年级任务另记，**本次未修正该产品边界或宣称全库代码/文档零冲突**。有关ISS/REG检索未找到专属BUG-033记录；不借本UI改动扩大实施范围。
- 当前Spec为VERIFYING、保留`specs/active/`。本增量未preview/上传、未设体验、未提审/正式发布；旧0.1.17不含本修改。匹配本增量的成功云交付后才按GOV-002设DONE/迁completed，未完成验收和独立Review继续单列。
- 文档收尾后已再次通过全局及本DREV的`validate_design_evidence.py --check-current-policy`、`git diff --check`、本任务Markdown目标存在检查与源码SHA绑定检查；目录实际109 completed / 14 active / 14 rejected，active为6 VERIFYING / 6 READY_FOR_REVIEW / 1 BLOCKED / 1 DRAFT，与索引一致。
