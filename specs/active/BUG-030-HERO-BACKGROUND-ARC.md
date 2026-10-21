# BUG-030 — 删除背景中类似头发丝的细弧线 (Spec Lite)

- Status: VERIFYING
- Risk: R1（单个共享样式规则删除，可逆）
- Owner / Reviewer: 用户
- Implementer: Codex
- Date: 2026-10-21
- Spec revision: BUG-SPEC-20261021-HERO-ARC-01
- User confirmation: 用户，2026-10-21。在助手展示本Spec01/DREV01、明确询问确认后，用户回复“还有很多其他的背景 有类似的问题 一起修复掉”。该继续实施指令唯一对应本轮Spec01/DREV01；本Spec既定范围已包含全部共享卡片，并非仅今日预览图。全面排查后未发现需要新增方案的第二种背景弧线来源，因此按已展示的全局方案执行。
- Affected Feature IDs: FEAT-001、FEAT-002、FEAT-003、FEAT-007、FEAT-010、FEAT-011（均仅继承共享装饰变化）
- Feature current-state documents: `docs/domain/features/FEAT-001-push-kids-mvp.md`、`FEAT-002-family-collaboration.md`、`FEAT-003-notification-channel.md`、`FEAT-007-travel-arrangements.md`、`FEAT-010-daily-tasks.md`、`FEAT-011-notification-auto-renewal.md`
- Feature baseline revisions: FEAT-STATE-20261020-AUTO-SUPERSEDED-FULLSTACK-02-LOCAL；FEAT-STATE-20260913-BUG015-SIX-DIGIT-INVITE；FEAT-STATE-20261017-NOTIFICATION-LIVE-RECEIPT-05 / AUTO-RENEWAL-LOCAL-01；FEAT-STATE-20260906-03-LOCAL；FEAT-STATE-20261015-ACTION-PAGER-02；FEAT-STATE-20261017-NOTIFICATION-AUTO-RENEWAL-LOCAL-01。
- Feature merge owner: Codex，仅在批准实现并验证后合并事实。
- Commit boundary: 用户要求提交后，仅收录本次共享样式及文档/证据增量；FEAT-011及其旧通知DREV是并行未提交任务，已同步的视觉说明随该任务保留。提交内由FEAT-003/UI-011及新DREV记录提醒卡背景事实；六份Feature/三份旧清单的同步数量及自动化结果均指验证时工作树，详见质量证据。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes — 删除共享卡片背景的细弧线。
- Frontend engineering impact: yes — `styles/atoms.wxss` 装饰规则。
- Affected UI IDs: UI-001、UI-009、UI-011
- UI current-state documents: `docs/design/frontend/ui/UI-001-parent-miniapp.md`、`UI-009-family-members.md`、`UI-011-reminder-settings.md`
- Frontend baseline revision: FDB-20260913-04 APPROVED
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected frontend quality dimensions: component/state/responsive/a11y/browser/device/media/performance/security/privacy/observability。
- Frontend quality budgets/requirements: 320×568、390×844、430×932；原生节点与截图证据不能由 HTML 替代；保持原控件几何/至少44px触控、可访问名称与状态；主包≤1.5 MiB；无新增资产、网络请求、依赖或日志。
- Frontend quality verification plan: TP-001～TP-005；不新增只断言 CSS 字符串的实现镜像测试。
- Approved frontend engineering deviations: none
- Current Design Revision(s): DREV-20261013-CARD-BACKGROUNDS-01；DREV-20260913-FAMILY-INVITE-CODE-01；DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01，各页面后续增量继续有效。
- Proposed Design Revision: DREV-20261021-HERO-ARC-REMOVAL-01
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/*-<width>x<height>.html`；生成器 `render.cjs`。
- Design source SHA-256: 逐文件记录在下列三个候选清单。
- Required viewport/state exports: 三视口×今日正常/引导、记录、日程、报表、设置上部/下部、家庭邀请、提醒就绪/中性；共30张。
- Prototype status: APPROVED
- Approved Task Spec revision: BUG-SPEC-20261021-HERO-ARC-01
- Approved Design Revision: DREV-20261021-HERO-ARC-REMOVAL-01
- Design approval evidence: 用户2026-10-21在具体Spec01/DREV01对比及确认请求后的“一起修复掉”；批准按现有全局共享规则方案实施。未重绘图片或新增视觉方案。
- Snapshot manifest paths: `docs/design/frontend/snapshots/{UI-001,UI-009,UI-011}/DREV-20261021-HERO-ARC-REMOVAL-01/APPROVAL.md`
- Permitted implementation deviations: none
- UI current-state merge owner: Codex
- UI current-state merge evidence: UI-001、UI-009、UI-011正文已合并本地去弧线事实与本Spec/证据链接，增量revision UI-VISUAL-20261021-HERO-ARC-01。
- Frontend visual/a11y/resolution verification: 候选 `render-audit.json` 与PNG仍仅为设计证据；批准后原生采集与缺口见本轮质量证据。
- Frontend engineering verification evidence: [HERO-ARC-REMOVAL-20261021.md](../../docs/quality/evidence/HERO-ARC-REMOVAL-20261021.md)；已实现并通过前端回归、静态校验与批准设计一致性核对。
- External design dependency: none

## 1. Problem and outcome

背景卡片右下角可见一条像头发丝的细弧线，用户要求删除。源码确认不是图片瑕疵：
`apps/miniprogram/styles/atoms.wxss:70` 的 `.pk-hero::after` 用低透明度1rpx圆形描边绘制，
被 `.pk-hero` 的边界裁切成弧。可观察结果应是所有共享卡片去掉弧线，现有背景与内容保留。

## 2. Scope

删除该共享伪元素规则并修正对应“年轮弧线”注释；同步经验证的Feature/UI现状和证据。
不改图片、颜色、渐变、文案、表单、事件、API、数据、排期、授权、模块边界或扩展点。
没有存量数据修复或迁移。已有并行工作树改动必须保留。

现状合并：各受影响Feature/UI正文已写明弧线删除、增量revision、本Spec及真实验证/发布状态；
Behavior Catalog、Architecture、测试策略和发布文档已按实际diff核对，无业务/架构/发布事实变化，
无需修改其规则正文，具体理由见质量证据。旧获批快照源/PNG保持不可变，仅添加局部 Superseded by 指针。

## 3. Impact map

入口：今日正常/引导、日程、记录、报表、设置四张卡、家庭邀请卡、提醒设置就绪/中性卡。
权威来源：`app.wxss` 导入 `styles/atoms.wxss`。已检索所有WXML/WXSS引用，没有第二条同类共享规则。
既有前端测试覆盖相关页面行为；本修订只改纯装饰，运行既有回归与渲染核对。

## 4. Required design views

### Link/call graph

```text
各页面 WXML .pk-hero → app.wxss @import → styles/atoms.wxss .pk-hero
                                                     └→ ::after 圆描边（拟删除）
原页面事件 → 原控制器 → 原API（保持现状）
```

### Sequence diagram

N/A：静态装饰删除，没有事件顺序、网络调用或事务变化。

### State machine

N/A：没有状态迁移；所有业务状态保留，仅共享卡片装饰减少。

### Architecture diagram

N/A：保留 tokens→atoms→page 依赖方向，没有模块边界/部署/信任边界/扩展点变化。

### Trade-offs

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| 删除共享伪元素 | 一处去除全部同类弧线，减少样式与装饰 | 所有引用页面均需视觉核对 | selected |
| 页面分别覆盖隐藏 | 可逐页控制 | 留下无用原规则，遗漏次级页风险 | rejected |
| 重绘PNG背景 | 可以修复位图瑕疵 | 本问题不在位图，额外资源与视觉偏差 | rejected |

## 5. Expected file changes and deletion plan

| File/path | Action | Intended change | Why required |
|---|---|---|---|
| apps/miniprogram/styles/atoms.wxss | modify after approval | 删除 `.pk-hero::after` 与注释中的弧线描述 | 权威渲染源 |
| specs/active/BUG-030-HERO-BACKGROUND-ARC.md | add/update/move | 批准、测试与状态；完成后移completed | 任务门禁 |
| docs/design/frontend/prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/ | add | 自包含候选HTML、生成器、对比、审计 | 可审阅设计 |
| docs/design/frontend/snapshots/{UI-001,UI-009,UI-011}/DREV-20261021-HERO-ARC-REMOVAL-01/ | add | 三视口PNG与SHA-256清单 | 设计证据 |
| specs/README.md | modify | 候选/最终状态索引 | 可发现性 |
| 上述Feature/UI current-state与FRONTEND-DESIGN.md | modify after verification | 核对并合并真实实现/验证状态 | 文档闭环 |
| docs/quality/evidence/HERO-ARC-REMOVAL-20261021.md | add after implementation | 本diff检查、原生/真机与缺口 | 验证证据 |
| docs/quality/evidence/hero-arc-removal-20261021/ | add | 批准设计一致性JSON、隔离源哈希、复现脚本、原生数值/PNG及清单 | 保留实际检查证据与未完成项 |

最终权威路径仍为 atoms.wxss；直接删除装饰，无兼容分支。回滚可恢复原规则与注释。

## 6. Acceptance criteria

- AC-001：全部共享卡片的右下角细弧线消失，三视口/正常与引导/设置下部/提醒中性均覆盖。
- AC-002：原渐变、图片、边框、阴影、排版、按钮触控、文案、失败回退与业务交互保持现状；无新增请求。
- AC-003：生产diff只有批准范围；文档事实一致，清楚区分设计预览、本地实现、原生验收与发布状态。

## 7. Required test points

| Test point | Acceptance criterion | Test level / Command or case | Required result |
|---|---|---|---|
| TP-001 | AC-001/002 | `node docs/design/frontend/prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/render.cjs`；候选弧线前后及hero几何核对 | 30导出，伪元素none，hero几何不变，无图片/运行错误/远程请求；仅设计证据 |
| TP-002 | AC-002 | `npm test`；`npm run lint:miniapp` | 既有相关页面回归和lint通过 |
| TP-003 | AC-002/003 | `.venv/bin/python tools/validate_miniprogram.py`；`.venv/bin/python tools/check_architecture.py`；`.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | 静态预算、架构与设计检查通过 |
| TP-004 | AC-001/002 | 微信原生320/390/430上述卡片截图与节点几何、长内容/字体放大；iOS/Android视觉及触控验收 | 原生弧线消失，原几何与交互保持，证据留存；HTML不替代 |
| TP-005 | AC-003 | 实际diff逐项对照Feature/Behavior/Architecture/UI/Spec/测试/发布与路径索引 | 无本次冲突；历史未验收不冒充已通过 |

## 8. Plan

1. 准备可编辑设计源、导出、哈希和对比；用户确认具体Spec01+DREV01。
2. 记录批准后删除权威规则与注释；运行既有前端及静态校验，完成原生/真机核对。
3. 按实际验证同步当前事实和证据；只有全部完成门禁通过才DONE并迁移completed。

## 9. Verification

| Test point | Result | Evidence/notes |
|---|---|---|
| TP-001 | PASS（设计期） | 27组状态/视口、30张PNG；所有hero前后位置/尺寸一致，原弧线content为`""`、候选为none；图片解码/运行错误/远程请求均为0。证据：候选 `render-audit.json`，不等同生产修复验收。 |
| 设计清单与政策 | PASS（设计期） | `.venv/bin/python tools/validate_design_evidence.py --manifest <UI-001/UI-009/UI-011本DREV清单> --allow-pending`各通过；UI-001命令同时加`--check-current-policy`通过；生成器`node --check`通过。已目视核对390设置卡片与今日前后对比。 |
| TP-001生产对照 | PASS | `node /private/tmp/push-kids-hero-arc-verify.cjs`：27组当前WXML/WXSS渲染在仅规范化CSS空行/注释后与冻结批准HTML相同；JSON留存于 `docs/quality/evidence/hero-arc-removal-20261021/approved-parity.json`。75个既有预览均无该弧线规则。 |
| TP-002 | PASS | `npm test`：265 passed / 0 failed / 0 skipped；`npm run lint:miniapp`通过。 |
| TP-003 | PASS | `.venv/bin/python tools/validate_miniprogram.py`：17页/1155936字节；`tools/check_architecture.py`：4策略/130模块DAG通过；`tools/validate_design_evidence.py --check-current-policy`通过；三个新DREV的`--manifest`按批准状态通过。 |
| 额外历史清单复核 | PARTIAL / pre-existing FAIL | 三份被局部替代的旧清单中，CARD-BACKGROUNDS与NOTIFICATION-AUTO-RENEWAL通过；旧家庭邀请源哈希不一致。当前源与HEAD相同，确认非本次修改；详情记录在质量证据，旧源/哈希未重写。 |
| TP-004 | PARTIAL | 三视口共20组卡片几何、17张原生截图；390全部9组/10张，320为6组/3张，430为5组/4张。其余截图/导航API超时及字体放大/长内容、iOS/Android仍待补；见本轮质量证据，不用HTML替代。 |
| TP-005 | PASS（本diff） | Feature六份、UI三份、前端设计正文、Spec索引/批准证据与质量证据已同步；生产diff仅删除共享弧线规则及修正注释，无新增模块/资产/API/数据。 |

实现后文档闭环核对：

| 文档类别 | 与本次实际diff的核对结果 |
|---|---|
| Feature / Behavior Catalog | 六份Feature正文加入本地装饰事实与revision/证据；业务行为未变，Behavior Catalog规则正文无需修改。 |
| Architecture | 无生产模块边界、依赖或扩展点变化，架构正文无需修改；本轮架构检查通过。 |
| UI current-state / frontend baseline | 三个UI正文和设计基线加入具体局部DREV；新清单已记录批准，批准源/PNG不变；旧清单仅添加局部Superseded by指针。 |
| Spec / 索引 / 路径 | 本Spec为VERIFYING且保留active；索引同步实现与验收边界，相关目标路径存在。 |
| 测试证据 | 合并本轮265项及静态/设计/原生真实检查；未引用历史自动化作为本轮验证。 |
| 发布文档 | 无上传/体验/审核/正式发布操作，保持既有线上记录；本轮质量证据明确仅本地。 |

本次diff与所影响当前正文未发现新冲突；收尾发现的旧家庭邀请设计源/清单哈希不一致已在质量证据独立列出，
确认源与HEAD一致且本次未改动，未重写历史证据。这不代替并行工作树已有改动的全面事实审计。

## 10. Completion

代码已统一删除共享弧线，当前为 VERIFYING，保留 `specs/active/`，未上传或发布。
批准、当前diff自动化、设计一致性、Feature/UI事实合并均已完成；完整原生/真机门禁尚未齐全。
恢复/完成条件：补齐质量证据所列原生、字体放大/长内容与iOS/Android验收，用户视觉验收后才DONE并移completed；代码完成不等于全部验收完成。
