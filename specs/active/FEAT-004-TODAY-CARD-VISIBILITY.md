# FEAT-004 — 今日学习空区隐藏与样式统一（Spec Lite）

- Status: VERIFYING
- Risk: R1，原组件内局部呈现调整，可逆；不改API、资格政策、权限、计时或异步编排。
- Owner: 产品负责人（用户）；Implementer: Codex；Reviewer: 待实现后只读复核。
- Date: 2026-10-24
- Spec revision: SPEC-20261024-TODAY-CARD-VISIBILITY-01
- User confirmation: 用户于2026-10-24在call_ac391833df284fc7b0afcb71c55abec7回复「批准，按此实现」，明确批准本Spec01与DREV03；按批准范围实施。
- Affected Feature IDs: FEAT-004；UI-001。
- Feature current-state documents: [FEAT-004](../../docs/domain/features/FEAT-004-daily-learning-suggestions.md)
- Feature baseline revision: FEAT-STATE-20261024-INCREMENTAL-LEARNING-05-LOCAL。
- Feature merge owner: Codex；主Spec04及弹层Refinement Spec01仍VERIFYING，独立管理。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes，今日学习区域显隐、文案密度、卡片标题/按钮字阶与形状。
- Frontend engineering impact: yes，原today-learning组件WXML/WXSS，必要的纯显示条件；不新增请求或副作用。
- Affected UI IDs: UI-001；[UI current state](../../docs/design/frontend/ui/UI-001-parent-miniapp.md)。
- Frontend baseline revision: FDB-20260913-04，APPROVED。
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02，APPROVED。
- Affected frontend quality dimensions: component/state、responsive、a11y、motion、performance、security/privacy。
- Frontend quality budgets/requirements: 沿用tokens/atoms；正文与操作≥14px、触控≥44px；320×568、390×844、430×932；无横向溢出、长标题完整换行、无隐藏区域占位；1.5MiB预算、不新增资源/依赖/请求。
- Frontend quality verification plan: 21态×3设计导出、显隐/样式/入口目标核对；批准后前端测试、ESLint、静态检查及三视口原生节点/截图，设备/可访问性另记。
- Approved frontend engineering deviations: none。
- Current Design Revision(s): DREV03（今日卡片/状态区）及DREV02（本卡片修订未改弹层）；DREV01仅本次卡片范围被替代。后续已批准[Title Limit Spec01](FEAT-004-SUGGESTION-TITLE-LIMIT.md)/DREV04另将新生成/编辑标题限制20码点并增加字段反馈，旧长标题兼容、卡片字体与显隐仍沿本Spec；[标题增量证据](../../docs/quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)不覆盖本Spec其余门禁。
- Approved Design Revision: DREV-20261024-TODAY-LEARNING-03，仅今日页卡片与状态区。
- Editable design source path: [HTML](../../docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/index.html)。
- Design source SHA-256: 见[候选清单](../../docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-03/APPROVAL.md)。
- Required viewport/state exports: 21态×3=63张，精确矩阵见[Frontend Spec](../../docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md)。
- Prototype status: APPROVED。
- Approved Task Spec revision / Approved Design Revision / Approval evidence: SPEC-20261024-TODAY-CARD-VISIBILITY-01 / DREV-20261024-TODAY-LEARNING-03；用户，2026-10-24，call_ac391833df284fc7b0afcb71c55abec7「批准，按此实现」。
- Permitted implementation deviations: none；DREV01/02批准源保持冻结，批准后仅增加范围明确的Superseded by指针。
- UI current-state merge owner: Codex；批准/实现后替换显隐与当前字体事实，不用设计结果代验实现。
- External design dependency: none。

## 1. Problem and outcome

当前组件只排除disabled，仍将recent_new、warming_up、no_history、missing_grade、no_subject、inactive等状态渲染成“今日学习”空卡。符合资格但没有内容时也出现“沿着学过的，再走一小步”的通用广告式卡片。组件自写16px无衬线标题、20px内容标题和非胶囊按钮，与今日页17px衬线分区标题、普通内容字阶及胶囊按钮不一致。

没有实际建议/待学、也没有进行中或可恢复操作时，整块区域不渲染、不留额外边距。可用建议直接显示具体标题/科目/时间，去掉“小步延展，家长做主”和通用口号。已批准待学仍保留实际内容和操作。标题/正文/卡片/按钮沿用今日页的设计语言。

## 2. Scope

只修改today-learning外层今日卡片和必要错误/进度状态；DREV02弹层、生成触发/限额、共享提示消费、暂缓/换项、审批、实际记录、轮询/迟到保护保持既有合同。隐藏区域不等于卸载组件，自动请求与轮询仍由原组件生命周期执行。

| 服务端快照/权限 | 今日页显示 |
|---|---|
| null、无内容的disabled/inactive/no_history/missing_grade/no_subject/warming_up/recent_new、未知无内容状态 | 整块隐藏，不显示原因卡或空标题 |
| eligible但没有proposal/task/job，且无待恢复操作 | 整块隐藏；原automatic-prompt继续执行，有生成结果再显示 |
| manager/editor有可用proposal，且eligible或can_regenerate | 今日学习分区+实际标题/科目/可选时长/AI建议标识+“查看学习建议” |
| 有已批准task（含只读、部分学习、生成开关关闭） | 今日学习分区+具体待学内容；有权限者可记录/删除，viewer只读 |
| 无proposal/task，但queued/running job且有写权限及eligible/can_regenerate | 紧凑“正在准备学习建议”及查看进度，不显示通用学习标题 |
| 有写权限且失败job/失效建议可重试，或删除后can_regenerate恢复资格 | 紧凑状态与对应查看/重新准备入口，沿用原open/generate，防止关闭后无恢复入口 |
| viewer只有未批准proposal、生成任务或资格 | 隐藏，不能生成/审批；不新增只读空卡 |
| 请求错误 | 必要的原错误/重试保留；不以“没有内容”掩盖故障 |

以上显示判断只投影服务端快照，不重新计算两日资格。task优先于proposal，proposal优先于无内容的进度/恢复态；已批准task不会被“最近有新增”或生成开关误隐藏。未批准建议和生成/恢复操作沿用原eligible/can_regenerate门槛；关闭功能时不展示不可审批的旧提案。

样式：分区标题复用sec-bar/s-t的17px衬线600；卡片复用pk-card纸色、边框、圆角、间距和轻阴影；具体内容标题沿用复习卡todo-title的16px/600无衬线、1.4行高和0.2px字距，正文/元信息14px；查看建议用btn.secondary胶囊，记录实际学习用既有主btn胶囊，触控均≥44px。只作用于外层卡片，弹层字体与布局不变。

Feature/UI最终合并将替换“无资格也显示原因卡/eligible空壳入口”与独立卡片样式的当前事实；BHV-045仅补显示条件，不改变服务端领域规则。Architecture无新边界；发布状态不改变。

## 3. Impact map

`今日页（组件继续挂载）→ today-learning current/canWrite → 原组件显隐分支与卡片样式 → 既有open/openRecord/openRemove/retry → 既有API`。

现有tests/frontend/today-learning.test.js及Today生命周期测试；原生准备/采集工具只按本次状态补充合成夹具。无独立平行生产组件或重复资格算法。

## 4. Required design views

Link/call graph：见上方；没有新增调用或写入。

Sequence diagram：N/A，触发、提示、生成、审批与真实记录调用序列完全不变；变化只在每次快照投影后的渲染。

State machine：`empty→hidden`；`proposal→content`；`task→content`；`job→progress/recovery`；切孩子/家庭/角色仍由原reset/迟到保护清空旧快照。显示/隐藏本身不能触发生成、审批、学习确认或消费自动提示。

Architecture diagram：N/A，组件仍拥有显示状态，服务端拥有资格/Job/建议/任务权威，依赖方向及扩展点不变。

| 方案 | 收益 | 代价 | 选择 |
|---|---|---|---|
| 空区隐藏，实际内容显示，生成/失败仅紧凑状态 | 满足没有内容不占位，保留必要恢复能力 | 需明确快照优先级和边界状态 | 推荐 |
| 只隐藏recent_new | 改动最少 | 其他无内容状态仍出现空壳 | 拒绝 |
| 所有无proposal/task一律隐藏且不保留进度/错误 | 视觉最少 | 关闭生成弹层后无恢复入口，故障被当作空数据 | 拒绝 |

## 5. Expected file changes and deletion plan

| 文件 | 操作 | 原因 |
|---|---|---|
| 本Spec、新DREV03 HTML/导出/清单/设计证据 | add，当前设计阶段 | 具体可审阅方案及批准门禁 |
| today-learning/index.wxml、index.wxss及必要纯显示条件 | modify，批准后 | 删除空原因卡和通用口号；分区/卡片样式复用与显隐 |
| today-learning.test.js、原生取证夹具 | modify，批准后 | 空区、角色、任务优先级及恢复入口回归 |
| Feature/UI/Behavior/测试/发布记录、索引 | modify | 区分待批准、已实现及验证/发布状态 |

删除不再使用的空卡文案/样式；不改共用tokens/atoms，不创建通用工具包，不删除手工记录学习入口。

## 6. Acceptance criteria

AC-001：截图中的“最近已有新的学习内容”空卡及其同类无内容状态整块消失，复习分区自然上移，无空标题或残留边距。eligible纯空快照也不伪装成已有建议；组件仍挂载以保留既有自动生成。

AC-002：有实际建议/待学时显示具体内容；“今日学习”标题字体/大小/字重与“复习安排”一致，卡片与胶囊按钮沿用既有原子；移除两句口号。320/390/430下长标题完整换行，操作≥44px且无遮挡/横向溢出。

AC-003：queued/running、失败/失效可重试、删除后恢复有必要入口；viewer只看已批准task；任务不被资格或开关误隐藏。显示变化零业务写入，不改变自动提示/父弹层协调、幂等、权限或轮询。DREV02弹层及早复习不变。

## 7. Required test points

| TP | AC | 检查 | 要求 |
|---|---|---|---|
| TP-001 | 001–003 | DREV03 renderer、63张SHA、旧批准设计校验、链接/diff | 空区无节点、邻接间距、字体一致、44px/包含、入口目标通过 |
| TP-002 | 001/003 | 批准后显隐/角色/重试/旧Task开关与自动提示回归，npm test/ESLint | 关键状态明确，隐藏不卸载/不新增写入，全部适用回归通过 |
| TP-003 | 002 | 批准后原生三视口相应状态/长标题/按钮/相邻分区节点及截图 | 实际字体家族/字阶/圆角和44px/间隔/包含通过，空态零卡片与额外边距 |
| TP-004 | 002/003 | 静态预算/架构、代表设备/可访问性 | 不增资源/依赖；真实设备和读屏/大字体另有证据，未执行不得写通过 |

## 8. Plan

先完成候选设计和三视口导出，取得本Spec01+DREV03具体批准后修改原组件，运行TP-002..004并同步当前正文。旧批准快照只按规则添加Superseded by，未通过全部验收保持VERIFYING。

## 9. Verification

TP-001设计阶段PASS：63张布局、8个既有入口、Runtime异常0及SHA，见[历史设计证据](../../docs/quality/evidence/TODAY-CARD-DESIGN-20261024.md)。具体批准后已实施原组件，TP-002 PASS：专项13项、npm前端327项及ESLint通过；显示判断零业务写入，隐藏仍执行自动提示，角色/任务优先、恢复、失败保留和迟到保护回归通过。TP-003 PASS：320×568、390×844、430×932各21卡片态与6个既有弹层代表态，共81组原生节点/PNG通过，SHA与最终runner/源码匹配；锁屏缺口已消除，320取证高度假设更正及首次失败均留证。TP-004 PARTIAL：静态预算/150模块DAG通过；真实设备、读屏/键盘/系统大字体及独立复核未完成。详见[本轮实现证据](../../docs/quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)。

## 10. Completion

当前VERIFYING，保留specs/active/，批准记录先于生产修改。已更新Feature/UI/Behavior/测试策略/发布记录和索引，Architecture/ADR无边界变化并已核对；旧设计快照冻结，DREV01只添加范围明确的Superseded by。三视口原生已通过，仍缺真实设备/可访问性及独立复核，不能设DONE或迁入completed；补齐这些结论后再完成生命周期迁移。没有提交、上传、部署或改变开关。
