# FEAT-004 — 学习建议弹层精简与按钮层级（Spec Lite）

- Status: VERIFYING
- Risk: R1，局部可逆的展示调整，沿用既有事件和状态。
- Owner: 产品负责人（用户）；Implementer/当前自查: Codex；独立Reviewer: 尚未执行。
- Date: 2026-10-24
- Spec revision: SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01
- User confirmation: 产品负责人2026-10-24针对明确列出本Spec01和DREV02及改动清单的审批问题回复「批准，按此实现」（request_user_input_async / call_989b0367f519481a9dc9b890f5ae9f1b）。此批准只覆盖本次呈现修订，主Spec04的批准及验收状态独立保留。
- Affected Feature IDs: FEAT-004；FEAT-001复习排期及界面不变。
- Feature current-state documents: [FEAT-004](../../docs/domain/features/FEAT-004-daily-learning-suggestions.md)
- Feature baseline revision: FEAT-STATE-20261024-INCREMENTAL-LEARNING-04-LOCAL
- Feature merge owner: Codex；主[Spec04](FEAT-004-INCREMENTAL-LEARNING-PATH.md)保留VERIFYING。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes，精简建议主态头部，整理确认/编辑/换项/暂缓的层级和触控区。
- Frontend engineering impact: yes，修改today-learning组件WXML/WXSS及命令等待的展示标识；事件/API及数据所有权沿用。等待标识只区分确认、换项、暂缓的按钮文字，不改变调用/事务/重试合同。
- Affected UI IDs: UI-001；[current state](../../docs/design/frontend/ui/UI-001-parent-miniapp.md)。
- Frontend baseline revision: FDB-20260913-04，APPROVED。
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02，APPROVED。
- Affected frontend quality dimensions: state/form、responsive、a11y、motion、privacy、performance。
- Frontend quality budgets/requirements: 正文≥14px，所有操作≥44×44逻辑像素、相邻操作≥8px；原生按钮显式宽度和盒模型；无横向溢出，长中文可滚动；主包≤1.5MiB，无新资源/请求/依赖，纯文本展示。
- Frontend quality verification plan: 三视口原型导出、动作与键盘检查；批准后运行现有前端测试/ESLint/静态检查及变化状态三视口原生节点/截图；真机、读屏、字体放大单列。
- Approved frontend engineering deviations: none。
- Previous Design Revision: DREV-20261024-TODAY-LEARNING-01（已批准并冻结，本次弹层范围已标记Superseded by）。
- Current Design Revision: DREV-20261024-TODAY-LEARNING-02（已批准并本地实现）；后续[Title Limit Spec01](FEAT-004-SUGGESTION-TITLE-LIMIT.md)/DREV04已批准并实现，仅覆盖新生成/编辑的20码点合同及字段反馈，其余弹层布局和旧长标题完整显示继续有效。[标题增量证据](../../docs/quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)不替代本Spec其余待验项目。
- Editable design source: [HTML](../../docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/index.html)；SHA见[批准清单](../../docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-02/APPROVAL.md)。
- Required viewport/state exports: 320×568、390×844、430×932；完整28态及变化范围见[Frontend Spec](../../docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md)。
- Prototype status: APPROVED。
- Approved Task Spec revision / Approved Design Revision / Approval evidence: SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01 / DREV-20261024-TODAY-LEARNING-02 / 产品负责人2026-10-24「批准，按此实现」，对应上方审批问题。
- Permitted implementation deviations: none；旧DREV01、PNG和SHA保持冻结。
- UI current-state merge owner: Codex；已同步本地实现及45组原生证据，真机与可访问性仍待验收。
- External design dependency: none。

## 1. Problem and outcome

用户在DREV01批注：弹层头部“AI 建议 · 待家长确认 / 沿着已学内容，再试一小步”不需要，突出重点；底部按钮交互需优化。目前口号先于具体学习内容，次级按钮与暂缓缺少一致的对齐和点击反馈。

具体学习标题成为弹层标题，其下紧凑显示科目、预计时间和AI标识。确认动作独占绿色主按钮；编辑和换项等宽并排、采用浅底边框；“今天先不学”独占一行居中弱化。保留每个动作、关闭入口及已有等待/失败恢复语义。

## 2. Scope

只改可审批建议主态、长内容、提交中和审批失败的头部/底部。编辑、生成中、失效、实际记录及删除沿用现有语义；原型补齐提交中和审批失败，编辑示例改为与实际组件一致的“保存修改→返回建议”。AI标识保留一处，学习内容、衔接依据和实际学过后再记录的提示保留。

不增加弹层、接口、状态转换、服务端规则或生成次数，不改变共享自动提示、角色、家长确认、真实记录和确定性排期。主Spec04与早复习Spec04未完成的验收仍独立存在。

Feature/UI合并仅替换建议呈现及验证事实；Behavior Catalog、Architecture和发布文档核对无领域变更，不把合成几何证据写成真实设备或业务端到端通过。

长文本兼容采用有界实现：历史标题不超过60字时正常换行；61–120字的完整旧标题和元信息置于30vh纵向滚动区，关闭按钮固定在区外，正文另行滚动、底部动作固定。未省略或截断旧内容；430视口可完整容纳120字时无需产生滚动。新生成/重新编辑现由已批准Title Limit Spec01限制为20码点，此历史显示分支不再代表新写入上限。该实现服务于已批准的长中文可读、正文和操作可达要求，不新增业务状态。

## 3. Impact map

`今日页 → components/today-learning/index.wxml + index.wxss + index.js（等待展示标识） → 既有 edit / generate / approve / defer / close → utils/api.js`。

现有 `tests/frontend/today-learning.test.js` 验证权限、幂等、迟到请求及表单恢复。无模块边界、依赖方向或扩展点变化，沿用ARCH-20261024-INCREMENTAL-LEARNING-PATH-03。

## 4. Required design views

Link/call graph：见上方原权威路径，无新增调用。

Sequence diagram：N/A，沿用“查看→可编辑/换项→家长确认→待学”的已批准调用序列；此次只调整呈现。

State machine：沿用`proposal → edit → proposal`、`proposal → saving → task / proposal+error`、`proposal → generating`、`proposal → deferred`。等待时禁用所有写操作和关闭；失败保留内容可重试。以上是既有业务行为，原型补齐可视证据。

Architecture diagram：N/A，无边界或数据流变化；组件继续拥有单领域展示与既有表单，服务端继续拥有权威状态。

| 方案 | 收益 | 代价 | 选择 |
|---|---|---|---|
| 具体标题+紧凑元信息；一个主按钮、两个并排次按钮、独立弱化暂缓 | 核心信息先读，操作对齐且含义清楚，小屏触控可达 | 底部保留三行，正文独立滚动 | 推荐 |
| 四个操作同排 | 更低 | 小屏挤压、长字与触控不足，层级不清 | 拒绝 |
| 删除编辑、换项或暂缓 | 更少按钮 | 破坏已批准能力 | 拒绝 |

## 5. Expected file changes and deletion plan

| 文件 | 操作 | 原因 |
|---|---|---|
| 新DREV02及UI-001 snapshots目录 | added、APPROVED并冻结 | 可审阅HTML、导出/审计和SHA |
| today-learning/index.wxml、index.wxss、index.js | modified、本地实现 | 删重复头部和三等分操作行；JS仅提供命令等待展示标识，使用原事件与数据合同 |
| today-learning.test.js、原生准备/采集工具 | modified | 等待/失败恢复回归，以及45组原生矩形与截图取证 |
| Spec、FEAT-004、UI-001、设计/Spec索引、验证证据 | add/modify | 区分候选、批准、本地实现和原生验收 |

不新建平行生产组件。旧快照保留冻结，新设计批准后才添加对应范围的Superseded by指针。

## 6. Acceptance criteria

AC-001：可审批提案打开后，首先看到具体学习标题，科目/预计时长/AI标识紧随其后；无原口号和重复“学习建议”标题。关闭区≥44px，主确认清楚；仅确认后加入待学。

AC-002：确认按钮独占一行、编辑与换项等宽且间隔≥8px、暂缓全宽居中；所有操作有按下/焦点/禁用反馈，提交中显示正在加入并禁止重复提交/关闭，失败保留建议与错误。

AC-003：320/390/430下长标题、正文和按钮无遮挡/越界，正文可独立滚动、底部操作可达；AI/依据/实际学习提示与原权限/记录语义保留。原型不替代原生验收。

## 7. Required test points

| Test point | AC | 检查 | 结果要求 |
|---|---|---|---|
| TP-001 | 001–003 | DREV02 render.py，28态×3、按钮流程/禁用/Tab/关闭 | 导出84张，控件尺寸/间距/包含通过，Runtime异常0 |
| TP-002 | 001–003 | 候选validator、旧快照validator、diff/链接核对 | SHA匹配，旧批准源不变，文档不冒充实现 |
| TP-003 | 001–003 | 批准后npm test、ESLint、validate_miniprogram.py | 现有业务回归通过，无包体/模板问题 |
| TP-004 | 001–003 | 批准后变化状态三视口原生节点/截图及代表真机/读屏/大字体 | 宽度、44px、8px、滚动、关闭/等待/错误恢复证据绑定当前源码 |

## 8. Plan

准备原型和导出，获取本具体Spec01/DREV02批准后修改原组件，执行TP-003/004并按实际结果合并文档。未满足验收保留VERIFYING，不以代码完成冒充DONE。

## 9. Verification

| 检查 | 当前结果 | 证据 |
|---|---|---|
| TP-001 | PASS（设计阶段） | 28态×3共84张，12条点击、禁用/Tab/Escape/焦点恢复及几何检查通过；[设计证据](../../docs/quality/evidence/SUGGESTION-SHEET-DESIGN-20261024.md) |
| TP-002 | PASS | 新批准清单/当前政策及旧78张冻结源复验通过；相对链接、Ruff与diff见[实现证据](../../docs/quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md) |
| TP-003 | PASS | npm test 311/0；专项9/0（含等待禁重复/关闭、失败保留、同键重试）；ESLint、小程序17页/1216563源码字节、架构150模块DAG及工具Ruff通过 |
| TP-004 原生几何 | PASS（限定合成范围） | 320×568、390×844、430×932，每视口15态，共45组节点JSON/PNG/SHA；44px控件、8px间距、正文/标题滚动和底部可达通过 |
| TP-004 真机与可访问性 | NOT_RUN | 代表iOS/Android、实际键盘、读屏、系统大字体；模拟器默认字体15，合成状态取证不代验设备操作与真实请求 |

## 10. Completion

本Spec01/DREV02已批准且本地实现，自动化与45组原生几何通过。Feature、Behavior Catalog、Architecture、UI、Spec、测试证据及本地发布记录已逐项核对，没有本次代码与当前正文冲突。设计HTML/PNG/SHA保持冻结；旧DREV01仅增加范围明确的Superseded by指针。

最终Status为VERIFYING，保留`specs/active/`：真机、实际键盘/读屏/系统大字体和实现后独立只读复核尚未完成，不能迁为DONE。恢复条件是补齐上述设备及复核证据；主功能Spec04的真实MySQL、真实内容与适用条件门禁独立保留。没有提交、上传、部署、体验、审核或正式发布。
