# Push Kids 前端设计基线

待评审局部调优：[DESIGN-003 Spec01](../../../specs/active/DESIGN-003-THEME-VISUAL-REFINEMENT.md) / [DREV09](prototypes/DREV-20261106-UI-CONSISTENCY-09/FRONTEND-SPEC.md)针对报表标题、记录头图、上传装饰与嵌套边框。当前只完成可编辑设计及六主题三视口162组HTML导出，尚未批准/实施；不替换下方已批准基线或DESIGN-002 Spec08本地实现事实，原生与真机未验。

当前[旅行入口Spec01/Architecture01](../../../specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)与DREV01批准源/22张导出保持冻结，其余DREV/FDB/FEC不变。2026-11-01交付revision `DESIGN-EVD-20261101-0.1.17-UPLOAD-01`：168份冻结源覆盖0.1.17官方成功上传1,191,019字节；三尺寸两宿主42组原生节点/PNG/SHA与局部动作证据保持，用户正向focus/分页/双账号门禁确认PASS。设备/读屏/键盘仍未验，体验/审核/正式发布未执行；开发DONE归档不代全部验收。[当前上传](../../deploy/releases/20261101-client-0.1.17-upload.md)与[原生矩阵](../../quality/evidence/client-release-20261101/native-matrix-resumed.json)分别绑定；批准资产不因Spec迁移改写。

编辑计划局部验证revision `DESIGN-EVD-20261101-REPORT-FOOTER-TIPS-03-NATIVE`：
[BUG-037 Spec01](../../../specs/completed/BUG-037-REPORT-FOOTER-TIPS.md)与
[DREV-20261101-REPORT-FOOTER-TIPS-01](prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/FRONTEND-SPEC.md)
已获用户“批准 Spec01 + DREV01”，[54张批准导出/SHA](snapshots/UI-001/DREV-20261101-REPORT-FOOTER-TIPS-01/APPROVAL.md)冻结。
共享编辑计划Flex分页和专用提示容器已本地实现，仅接管此前DREV-ACTION-PAGER-CONSISTENCY-02与REPORT-PANELS-01重叠的分页/提示区域；
FDB/FEC、每日任务按钮、报表展开/收起和其他设计范围保持。
349项与原430双宿主16组方法/状态/尾部几何PASS；用户解锁后的齐套03包含三视口双宿主144组原生PNG/节点与逐图SHA；
真机/大字/读屏待补。官方preview1192127字节成功、无线真机码已生成，手机未扫码；
未上传，Spec VERIFYING/active，批准DREV源/54图保持冻结。
[齐套03](../../quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)独立记录模拟器、真机和preview阶段，不改写原01/02。

2026-10-26开发归档（历史；旅行三项2026-11-01交付见本页当前正文）：已交付037后端/0.1.16客户端所覆盖的需求按用户批准规则标记开发DONE，验收缺项独立保留；后续BUG-035和旅行导入精简尚未交付，继续active。当前归档和待验入口见[Spec状态清单](../../../specs/STATUS.md)，依据为[治理Spec](../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。本轮不改产品合同、测试结论、设计或发布阶段。

当前获批导入DREV02与[Spec01/Architecture01](../../../specs/completed/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md)已随0.1.17交付，DONE；仅接管说明/勾选/重复AI与选择/上传失败区域，暖纸松绿/FDB/FEC和其余DREV保持。15张批准HTML冻结，原349项/15组原生及430实际导入/设置方法级证据保留，设备/可访问性/完整产品验收开放。[原实施证据](../../quality/evidence/travel-import-simplification-20261025/README.md)区分设计、原生与真机。

获批DREV-20261025-TRAVEL-DIARY-E2E-01与[BUG-035 Spec01/Architecture01](../../../specs/completed/BUG-035-TRAVEL-DIARY-END-TO-END.md)已由039/0.1.17两端交付，DONE。批准源/快照冻结，设备/完整内容/可访问性不由交付代验；此前0.1.16不含本增量，体验/提审/正式发布未执行。[原本地验证](../../deploy/releases/20261025-travel-diary-e2e-local.md)保持原日期/范围。

旅行DREV-20261025-TRAVEL-DIARY-E2E-01覆盖相册返回、核对保选、仅补缺日期、编辑照片预览、失败/冲突续接、精确画廊和恢复状态，沿用FDB/FEC及btn/seg，不改变全局导航。批准HTML源与42张设计导出冻结；最终生产源另有14态×三视口42组原生节点/截图、前端347项及430隔离实际流程证据，含设置保存中返回恢复缩略图。真实云三张草稿上传/城市/预览和重试、409续接已验；真实日期/正式确认、新focus云端、实际键盘、设备、大字/读屏及产品验收尚缺，见[当前证据](../../quality/evidence/travel-diary-e2e-20261025/README.md)。其他DREV仅各自重叠动作由本revision接管，原有效区域继续生效。

已批准旅行局部修订：[BUG-034 Spec01 / Architecture01](../../../specs/completed/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md)及[DREV-20261024-FOOTPRINTS-TIMELINE-01](prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md)已本地实施学习同款胶囊主操作/三视图，以及倒序时间线的缩略图与确认时刻。42张批准设计导出冻结；335项/静态、320/390/430各18原生态共54组及390实际点击通过，2026-10-25补齐430，设备/用户验收开放。见[本轮证据](../../quality/evidence/footprints-timeline-20261024/README.md)；FDB/FEC主revision及其他批准范围不改。

- 已批准标题约束：[`DREV-20261024-TODAY-LEARNING-04`](prototypes/DREV-20261024-TODAY-LEARNING-04/FRONTEND-SPEC.md)与[Title Limit Spec01 / Architecture01](../../../specs/completed/FEAT-004-SUGGESTION-TITLE-LIMIT.md)获用户「批准，按此实现」，已本地实施。新生成/重新编辑标题trim后1–20码点、无内部换行，字段显示n/20和14px错误，超限保留输入不提交；旧提案/任务完整兼容。33张批准导出冻结；三视口39态原生、前端332项及独立复核通过，[实现证据](../../quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)明确真机/可访问性待验。DREV02仅本范围由DREV04替代，其余弹层与DREV03卡片风格继续有效；开发DONE，验收待补；已随037/0.1.16交付，未体验/审核/正式发布。

- 2026-10-24产品方批准[足迹精简 Spec01](../../../specs/completed/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) / [DREV01](prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)及[工程 UI 文案附加条款](prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/UI-COPY-REQUIREMENTS.md)，规则已合并到下方“界面文案与减法”；既有 FDB/FEC 预算继续有效。足迹本地实现及原生验收以该Spec当前证据为准。

- 已批准今日卡片修订：[`DREV-20261024-TODAY-LEARNING-03`](prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md) / [Card Visibility Spec01](../../../specs/completed/FEAT-004-TODAY-CARD-VISIBILITY.md)，已本地实现空区整体隐藏、具体标题及既有分区/复习卡字阶与胶囊按钮。63张批准导出冻结；320/390/430各21卡片态及6弹层回归，共81组原生通过；真实设备/可访问性与独立复核待补。DREV02弹层保持冻结；[实现证据](../../quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md)，开发DONE，验收待补；已随0.1.16开发上传，未体验/审核/正式发布。

- 已批准本地增量：[`DREV-20261024-ANNUAL-GRADE-PROMOTION-02`](prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md)与[年级弹窗精简Spec01](../../../specs/completed/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)获用户“继续”批准并本地实现，正常态只保留孩子名标题、一个picker和并排操作，恢复提示按需显示。33张批准HTML导出冻结；最终327项前端、53项定向、三尺寸51组原生及实际选级/重试/稍后通过，[实施证据](../../quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)单列真实设备/可访问性及全业务原生端到端缺口。旧DREV01只追加弹窗范围Superseded by，档案表单继续有效。

- 2026-11-05批准/本地增量：[`DREV-20261024-CHILD-ARCHIVE-01`](prototypes/DREV-20261024-CHILD-ARCHIVE-01/FRONTEND-SPEC.md)对应[BUG-033 Spec01](../../../specs/completed/BUG-033-CHILD-ARCHIVE-UI.md)，用户“批准”后已本地精简档案归档/恢复卡与确认文案，21张批准HTML导出冻结。[本轮EVD](../../../specs/evidence/EVD-20261105-BUG033-IMPLEMENTATION.md)分别记录原生和设备缺项；未上传，不追改年级弹窗设计或其既有验收事实。

- 已批准批注增量：[`DREV-20261024-TODAY-LEARNING-02`](prototypes/DREV-20261024-TODAY-LEARNING-02/FRONTEND-SPEC.md)及[SUGGESTION-SHEET-REFINEMENT Spec01](../../../specs/completed/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md)获用户「批准，按此实现」。原组件已精简提案标题和操作层级；84张批准设计导出冻结，三视口45组原生节点/截图通过，设备及可访问性仍待验。旧DREV01仅追加本次范围的Superseded by指针；当前事实见[实现证据](../../quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)。

- 已批准本地增量：`DREV-20261024-TODAY-LEARNING-01`与两份Spec04于2026-10-24获用户「批准，按此实现」。[可编辑源/状态矩阵](prototypes/DREV-20261024-TODAY-LEARNING-01/FRONTEND-SPEC.md)及[冻结78张SHA清单](snapshots/UI-001/DREV-20261024-TODAY-LEARNING-01/APPROVAL.md)覆盖今日待学与提前复习；沿用FDB/FEC，不改变全局设计基线。实现及原生/真机边界见[本轮证据](../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)。

> 本文是微信小程序交互与视觉方向的已批准实现基线。

## 1. Baseline identity and approval

- Frontend scope: PRESENT
- Baseline status: APPROVED
- Baseline revision: FDB-20260913-04
- Owner: 产品负责人（用户）
- Proposed by: Codex（FDB-20260830-01）、Aime（FDB-20260906-02、FDB-20260906-03）
- Approved by: 产品负责人（用户）
- Approved at: 2026-09-13
- Approval evidence: FDB-20260906-03 的视觉/交互批准继续有效；用户 2026-09-13 批准
  `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`，将证据源迁移为仓库原生文件
- Last verified: 2026-09-13（仓库原生设计证据治理、模板和离线校验器通过；PKDS-2.0 视觉/交互未改变，三视口原生几何证据仍为 NOT_RUN）
- Applies to: 家长使用的微信小程序；未来手机 Web 应保持相同信息架构
- Related current implementation Spec: `specs/completed/SPEC-20260906-PKDS-03-PAPER-SPROUT-UI.md` revision `SPEC-20260906-PKDS-03`（前序：`SPEC-20260906-PKDS-01`）
- Superseded baseline revision: `FDB-20260830-01`、`FDB-20260906-02`、`FDB-20260906-03`（本 revision 不改变 PKDS-2.0 视觉/交互，只替换设计证据方式）
- Frontend engineering constraints: approved `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`

本 baseline 的可见合同由 `DREV-20260906-PKDS-03`（PKDS-2.0「纸 · 芽」）定义，
落地记录见 `specs/completed/SPEC-20260906-PKDS-03-PAPER-SPROUT-UI.md`，三视口走查产物由
`node tools/preview/render.js` + `python3 tools/preview/shoot.py` 重放到 `dist/ui-preview/`。
`DREV-20260906-PKDS-01` 的信息架构、状态四件套与产品立场继续有效，其色彩/圆角/阴影/图标层
降级为设计历史；`DREV-20260830-03`、`DREV-20260905-UX-03`、`DREV-20260905-UX-04` 同为设计历史。
旧 Figma 和 waiver 记录仅作为当时流程的历史证据；当前设计与发布不依赖外部设计工具。

2026-10-06本地增量：`SPEC-20261006-REVIEW-MANAGEMENT-03 / DREV-20261006-REVIEW-MANAGEMENT-03`
已获用户“落地并实现”批准，复用本基线/FEC。源码在`prototypes/DREV-20261006-REVIEW-MANAGEMENT-03/`，
候选证据在`snapshots/UI-001/DREV-20261006-REVIEW-MANAGEMENT-03/APPROVAL.md`；原生实现状态见UI-001。
本增量的视觉导出、三视口与真机证据仍不完整，不纳入“已验证视觉”范围，不引用旧版截图充数。

### PKDS-2.0「纸 · 芽」视觉基线要点

- 纸面：画布 `#FAF7F0`，卡片 `#FFFDF8`，凹陷 `#F3EFE4`；分层靠大而淡的阴影 + 发丝线，不靠强描边。
- 色彩：主色松绿 `#1F5B45`（确定、可信），成长嫩芽 `#7FA65C`（可选、余力），提醒赭石 `#A9762A`，
  异常陶土 `#A85742`，信息远山蓝灰。颜色永远不是状态的唯一载体。
- 字体：标题用衬线族（`Songti SC` / `Noto Serif SC`）制造纸感，正文用系统中文无衬线，
  数字统一 `font-variant-numeric: tabular-nums`。
- 原始风格圆角使用 8 / 12 / 16 / 24 / 32 / 40 / 999rpx；Spec08批准的主题形状差异由registry的共享角色管理（含28/44/48rpx），页面不得自建刻度。
- 页面左右安全边距由 `--pk-gutter` 统一给出；主CTA名义高96rpx，共用按钮/添加/图标操作的触区通过`--pk-touch-min:44px`兜底，避免320屏幕上88rpx不足44px。
- 图标统一为24×24 viewBox、stroke-width 1.8的线性glyph，由`theme-icon`消费单份生成路径和主题语义色；禁止emoji或文字符号充当图标。自定义TabBar使用同一组件，app.json平台回退图与原生地图标记保留本地PNG。
- 单位约定：颜色语义 token 无单位，几何量用 rpx，字号用 px，发丝线固定 1rpx。

### PKDS-2.0 交互立场（可见合同的一部分）

- 一屏一决定：首屏只回答"现在做什么"，其余信息折叠。
- 草稿感可见：AI 草稿用虚线印章持续标注，与正式记录有持久分界。
- 后果先行：复习反馈的每个选项旁必须写明它如何改变下次复习安排。
- 手动路径平权：手动录入与手动反馈的入口层级不低于 AI 路径。
- 报表只统计行为（记录数、知识点数、反馈次数、活动次数）与待复习压力，不评价能力、不预测掌握。
- 科目归类由服务端确定性分组给出、家长可改：一次拍到多个科目分别成档，新增科目必须家长显式同意
  （沿用 `BUG-013`，PKDS-2.0 只负责它的视觉呈现）。

## Repository-native design sources and ownership

可编辑设计源、设计 token、批准证据及其 Owner 见下文“Repository-native sources”表。
任何新增界面必须建立 UI-ID、仓库内 Design Revision、精确 viewport/state exports 和
approval snapshot，获得 Task Spec revision + DREV 的明确批准后才能实现。

## Style consistency baseline

记录入口当前增量 `DREV-20261024-RECORD-ENTRY-01` 与BUG-032 Spec05于2026-10-24获用户「可以」批准并本地实施：标题下方锚定菜单切换学习记录/旅行日记，菜单展开保留五Tab；旅行照片/编辑面板继续隐藏导航。右侧复用纸色child-chip、首字头像与线性箭头，长名整块换行；明确学习入口经原保护切回学习。旅行默认全部时间，整行日期筛选删除，三视图内容之后使用唯一48px普通导入按钮；历史以有界窗口续看。UI-001/018共用旅行领域组件，暖纸/松绿和14px/44px约束保持。[当前批准清单](snapshots/UI-001/DREV-20261024-RECORD-ENTRY-01/APPROVAL.md)与旧批准快照冻结，当前验证边界见[本轮证据](../../quality/evidence/record-entry-20261024/README.md)。该增量已随0.1.16开发上传，开发DONE；未体验/审核/正式发布，完整真机验收仍开放。

本地背景增量 `VISUAL-20261021-HERO-ARC-01`：用户批准的
[DREV-20261021-HERO-ARC-REMOVAL-01](prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/FRONTEND-SPEC.md)
已删除所有共享 `.pk-hero` 卡片的细弧线；暖纸色、浅绿光斑、插画、边框和排版保留。
该增量覆盖 UI-001、UI-009、UI-011，其他可见合同继续沿用各自DREV；验证与未完成项见
[本轮证据](../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)，本地实现不代表上传或发布。

当前本地实现以获批DESIGN-002 Spec08 / Architecture01扩展为六种风格：原始、成长花园、星际探索、深海夜色、海洋、科技。原始保留纸面/松绿/衬线标题，其他五种采用DREV06的背景角色、系统无衬线字体与主题形状；4px间距、清晰状态文字、非游戏化反馈和同一套业务页面继续适用。主题权威源是`apps/miniprogram/presentation/theme/registry.js`，`styles/tokens.wxss`由其生成，`styles/atoms.wxss`拥有共用组件，`styles/theme.wxss`拥有有限材质差异；页面只写特有几何，不能重复主题值或逐页判断主题。

设置入口位于底部列表“提醒设置”之后、“关于知芽”之前。六选一面板暂存候选，应用才切换并写本机小型ID偏好；取消不改变当前风格。未知科目/活动直接使用当前主题固定默认图标，无AI或联网选图。DREV08[标准批准索引](snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-08/CANONICAL-APPROVAL.md)和DREV06[标准索引](snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06/CANONICAL-APPROVAL.md)关联原冻结JSON/源/导出与后续用户批准，不改原快照；本次[实现证据](../../quality/evidence/themes-20261106/README.md)区分本地验证、原生合成呈现、真机与尚未上传。六主题尚未进入已上传0.1.18版本。

## User interaction conventions

交互遵循微信原生导航、返回、分享、授权、Toast 和 Dialog 习惯；复习反馈这类"需要看清后果"的
选择改用卡片内嵌面板而不是系统 Action Sheet（PKDS-2.0）；
核心写操作必须展示 pending/success/error，恢复性失败保留输入，破坏性操作二次确认。
详细流程和完整状态见第 4、5、8、10 节。

## Resolution and responsive support

MVP 支持手机竖屏 320×568、390×844、430×932 三个逻辑视口，安全区、文字放大、
长内容和键盘态均不得裁切关键操作。Required viewport matrix 和响应规则见第 9 节。

## Frontend implementation and quality baseline

实现必须同时遵循批准的 `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`。仓库内获批 DREV 决定可见合同，FEC 决定组件、
状态、表单、可访问性、性能、安全隐私、AI 内容和证据要求；两者互不替代。

## 2. 设计立场

### 一句话方向

**像一个安静、可靠的家庭学习助理，而不是儿童游戏、学校教务系统或高压打卡工具。**

### 产品气质

- 安静：首屏只突出今天需要做的事情，不制造信息焦虑。
- 温暖：适度使用圆角、柔和底色和生活化语言，但不幼稚卡通化。
- 可信：清楚区分正式记录、AI 分析中、待家长确认和系统建议。
- 高效：常用操作单手完成；记录学习不超过一个主要决策流程。
- 非评判：不使用排名、红榜、连续打卡压力或“落后/欠账”等文案。
- 可追溯：每个建议都能看到“为什么出现”和对应的原始学习记录。

### 明确不采用

- 大面积高饱和渐变、霓虹色、玻璃拟态和重阴影。
- 以吉祥物、金币、等级、排行榜为核心的游戏化视觉。
- 类企业 BI 的密集仪表盘和大量饼图/仪表盘。
- 用红色填满逾期内容，或用恐吓式文案推动家长。
- AI 对话框占据产品主入口；AI 是后台能力，不是主要导航方式。

### 界面文案与减法

**界面用内容、状态和操作表达产品，默认不需要解释。** 本条经产品负责人2026-10-24明确批准 Spec01 / DREV01 后生效；2026-11-05批准[工作日备注Spec01 / DREV03](../../../specs/completed/FEAT-001-WORKDAY-COPY-CLEANUP.md)补强防御性备注与实际异常去重要求，适用于后续 UI 设计与评审，既有FDB/FEC预算不变。

- 每段可见文案须服务当前任务：识别对象、作出选择、完成操作或从实际错误中恢复。删掉不影响这些任务的句子。
- 不把 AI 的思考、实现细节、后台流程、内部约束、维护年份、开发/验收说明或假想后果写成常驻备注；这些内容由设计与运维文档承担。
- 同一对象、身份、状态和动作只表达一次；同一实际异常只在受影响位置表达一次，表单能正常编辑时不插入结果区已有的数据维护说明。上方已选孩子，不再重复“某某的足迹”；低频设置和管理操作按需展开。
- 优先改清楚标签、控件、层级和反馈，不用一段说明弥补不清楚的交互；不把删下的说明改成帮助弹层、折叠长文或更多提示。
- 当前必要的授权范围、实际错误与恢复动作、删除/放弃的直接后果，在发生的操作处简短呈现，日常浏览不反复显示。
- AI 候选/未确认、未知值、只读、归档、草稿实际到期日等影响操作的状态，用短标签表达；精简不改变业务规则和权限。
- 空态只留状态和可执行动作；成功反馈不重复叙述步骤。无事实支撑的统计、占位人物和演示内容不得混入真实业务数据。
- 删文案后同步收紧布局，移除空容器和无消费者样式；不靠隐藏溢出、缩小文字或触控目标制造简洁。

## 3. 平台与 Design System

### 平台原则

- 遵循微信小程序“重点突出、流程明确、来去自如、减少干扰”的交互习惯。
- 使用微信原生导航、返回、Action Sheet、Toast、Dialog、上传和权限流程能满足需求时，
  不发明新的操作模型。唯一例外是"必须看清后果"的复习反馈：它在卡片内展开面板，
  以便每个选项旁写明对下次复习安排的影响（PKDS-2.0）。
- 以 WeUI/微信小程序基础组件的行为和可访问状态作为平台原语；领域卡片、Todo、
  知识标签和报表建立独立语义组件。
- 不为了视觉差异重写微信用户已经熟悉的确认、取消、返回和授权方式。

### Repository-native sources

| Purpose | Repository source | Owner | Notes |
|---|---|---|---|
| Product UI | `prototypes/<DREV>/FRONTEND-SPEC.md` + editable SVG/self-contained HTML | 产品负责人 | 当前可编辑、版本化设计源 |
| Design tokens | `apps/miniprogram/presentation/theme/registry.js` → `styles/tokens.wxss` | 前端呈现域维护者 | 六主题语义角色唯一源与原始首屏生成值；PKDS-1.0 reference为设计历史 |
| Design components | `apps/miniprogram/styles/atoms.wxss` | 产品负责人 | 组件类唯一来源；页面 wxss 只写本页几何 |
| Design icons | `apps/miniprogram/styles/icons.wxss` | 产品负责人 | 由 `tools/gen_icon_styles.py` 生成，禁止手工编辑；TabBar 位图由 `tools/gen_tabbar_icons.py` 生成 |
| 三视口走查 | `tools/preview/` → `dist/ui-preview/` | 产品负责人 | WXML→HTML 近似渲染 + 320/390/430 截图；不能替代原生节点几何验收 |
| Approval evidence | `snapshots/<UI-ID>/<DREV>/APPROVAL.md` + PNG exports | 产品负责人 | Task Spec/DREV identity、尺寸和 SHA-256 不可变清单 |
| Screen-level spec | `prototypes/DREV-20260906-PKDS-01/FRONTEND-SPEC.md` | 产品负责人 | 39 屏逐屏规格与参考屏；旧 Figma 说明只作历史记录 |
| WeUI reference | 微信官方 WeUI / weui-wxss | 微信设计团队 | 参考平台行为，不直接决定业务视觉 |

### 参考来源

- 微信小程序设计指南的核心方向：友好礼貌、重点突出、流程明确、清晰导航。
- WeUI / weui-wxss：微信官方设计团队提供的微信内基础样式与组件参考。

## 4. 信息架构与导航

### 底部导航：5 个一级入口

| Tab | 主要任务 | 不放什么 |
|---|---|---|
| 今日 | 今日 Todo、课程、活动建议、待确认提醒、快速记录 | 完整历史报表 |
| 日程 | 课外活动时间线、创建与编辑重复安排 | 学习复习 Todo |
| 记录 | 照片/文字记录、补录、异步任务与确认入口 | 复杂统计 |
| 报表 | 7/30/100 天紧迫度、复习活跃度和科目记录 | 未来负荷、掌握率 |
| 设置 | 科目、课外活动安排、家庭成员入口 | 学习档案创建、复习时间配置、每日行动 |

### 孩子选择

- 最近使用的孩子保持选中，不要求每次启动重新选择。
- “今日、记录、报表”顶部统一显示当前孩子头像/昵称和切换入口。
- 点击后使用底部半屏选择器，而不是进入一个空白选择页面。
- 每个孩子卡片同时展示：今日 Todo 数/预计分钟、待确认数量、本周复习完成数。
- 切换孩子后保留当前 Tab，但清空上一孩子的临时选择和筛选。
- 没有孩子时进入明确的首次创建流程，不展示无意义空报表。

### 主要创建入口

- 今日页首屏提供主按钮“记录今天学了什么”。
- 点击后使用 Action Sheet：`拍照`、`从相册选择`、`手动记录`。
- 记录页提供相同入口，但不使用会遮挡 Tab 的自定义悬浮按钮作为唯一入口。
- 活动练习从今日活动卡或活动详情进入，避免与知识照片上传混在同一表单。

## 5. 关键页面交互

### 5.1 今日页

信息优先级从上到下：

1. 当前孩子与切换入口。
2. 今日预计复习时间和主记录按钮。
3. 待确认/分析失败提示条。
4. “建议完成”Todo。
5. “有余力再做”。
6. 今日课程与活动建议。
7. 已完成内容折叠区。

首屏文案示例：

> 今天建议复习 4 项，约 15 分钟。

不使用“今日欠 4 项”“连续打卡第 28 天”等压力文案。

### 5.2 Todo 卡片

Todo 卡片必须包含：

- 科目与复习方式；
- 内容范围，例如“8 个三天前学过的单词”；
- 预计时间；
- 最多两行、可空的原题提示；
- 每个知识点自己的原始学习内容入口；
- 明确可见的操作，不依赖隐藏滑动手势。

当前复习卡不展示“出现原因”或通用“带练提示”。有来源提交时，原始内容在 Today 当前页底部弹层中
展示已上传照片和/或家长原文，不跳历史记录、不触发新的 AI review；完成按钮视觉高度为64rpx，
有效触控区域仍至少88rpx。

主操作：`完成`。

次操作：`需要巩固`、`稍后`。部分完成从更多操作或完成后的轻量选择进入。

完成后使用卡片内状态变化和轻 Toast 反馈，不播放庆祝动画、不弹全屏成功页。

### 5.3 上传与异步 AI

- 上传前只要求选择孩子；实际时间默认当前，可编辑为历史时间。
- 多张照片默认为同一次学习提交，家长可在确认页拆分。
- 上传成功立即创建可见记录，允许离开页面和继续上传。
- 展示真实阶段：上传中、等待分析、分析中、待确认、失败、已取消。
- 不展示无法证明的百分比或精确剩余时间。
- 分析完成后进入“待确认中心”，不使用阻塞式弹窗打断当前操作。
- 应用打开时可使用顶部提示或 Tab 红点；未来微信订阅消息需要用户单独授权。
- 失败状态保留原图和文字，提供 `重试` 与 `改为手动记录`。
- 取消后拒绝迟到结果，不让页面状态回跳。

### 5.4 学习草稿确认

- 默认按科目分组展示，先显示摘要，再展开知识点。
- 清楚标记“新知识”“以前学过”“可能重复”“识别不确定”。
- 低置信内容不默认静默选中。
- Todo 匹配以建议卡出现：`可能完成以下任务`，必须由家长勾选确认。
- 保存失败时保留所有编辑，不让家长重新录入。
- 支持一次确认整个可靠草稿，同时允许逐项删除/修改。

### 5.5 记录与补录

- 默认时间线，顶部可切换日历。
- 同一天多条记录按实际时间排序，不按上传时间排序。
- 补录入口明确显示“实际学习时间”，避免误解为创建时间。
- 图片缩略图只作证据预览；核心信息仍以可读文字展示。
- 修改实际时间后，提示会更新对应日期总结和未来计划。

### 5.6 报表

- 默认近 7 天；可切换近 7 天、近 30 天、近 100 天。
- 100 天日期视图只在报表组件内部左右分页，每屏最多 30 天，实际分块为 30/30/30/10；根页面不横向移动。
- 首先展示周期概览，其次展示复习紧迫度与活跃度。
- 使用准确数字、简单条形图和时间线；避免仪表盘、3D 图和装饰性饼图。
- 报表不显示掌握率、正确率、排名和孩子间比较。
- 每项指标可下钻到原始学习记录。
- AI 周期摘要最多三条行动建议，使用“建议/可以考虑”，不输出诊断式结论。

### 5.7 设置

- 学习档案由后台配置；家长端编辑科目与课外活动安排，不展示复习时间配置。
- 服务地址属于开发者构建配置，不在家长端展示输入框或保存操作。
- 账号与微信授权在 MVP 不出现空入口。
- 删除照片、学习记录或孩子属于破坏性操作，要求说明影响并二次确认；能恢复时优先提供撤销。

## 6. 视觉系统草案

### 色彩角色

以下为原型候选值，批准前需做对比度和真实设备验证：

| Token | Candidate | Use |
|---|---|---|
| `color-bg` | `#F5F7F4` | 页面温和中性底色 |
| `color-surface` | `#FFFFFF` | 卡片、输入与浮层 |
| `color-text` | `#17211C` | 主文字 |
| `color-text-secondary` | `#667069` | 次要说明 |
| `color-border` | `#E1E7E2` | 分隔与卡片边界 |
| `color-primary` | `#216F62` | 主要按钮、选中和关键链接 |
| `color-primary-soft` | `#E6F2EE` | 选中背景和轻提示 |
| `color-attention` | `#A85A16` | 需要关注、临近到期 |
| `color-danger` | `#B42318` | 错误和破坏性操作，仅必要时使用 |
| `color-success` | `#287A52` | 完成状态，不与主色只靠颜色区分 |

科目色只用于小面积标签、图标或图表系列：语文暖陶、数学蓝、英语柔紫、活动青绿。
正文和重要状态不能只靠科目色传达。

### 字体

- 使用微信/系统字体栈：PingFang SC、系统中文字体与 sans-serif fallback。
- 页面关键数字/标题：28 px，600 weight。
- 页面标题：22 px，600 weight。
- 卡片标题：17 px，600 weight。
- 正文：16 px，400/500 weight，约 1.5 行高。
- 次要内容：14 px；必要辅助说明不低于 13 px。
- 不以极细字重或浅灰小字承载关键学习内容。

### 间距、形状与层级

- 4 px 基础网格；常用间距 8/12/16/24/32 px。
- 页面水平安全边距 16 px。
- 卡片圆角 16 px；输入/按钮圆角 12 px；标签可用胶囊形。
- 卡片优先使用边界、底色和间距形成层级；阴影只做轻微浮层分离。
- 列表卡片内部保持 12–16 px 空间，不把报表压成密集表格。
- 主要触控目标不小于 44×44 px，核心按钮推荐高度 48 px。

### 图标与插画

- 统一使用简洁、圆角、2 px 左右线性图标；选中态可用小面积填充。
- 空状态插画只解释状态，不占据首屏大部分空间。
- 不使用性别化、成绩化或刻板化儿童形象。
- 上传照片只显示安全缩略图，默认不在报表大面积铺开。

### 动效

- 常规反馈 150–240 ms，使用标准 ease-out；页面返回遵循平台行为。
- 状态变化优先局部淡入/位移，不使用弹跳、粒子或庆祝烟花。
- 分析中使用低干扰骨架/轻呼吸占位，并提供明确文字状态。
- 尊重减少动态效果偏好；核心信息不能依赖动画出现。

## 7. 内容语气

### 推荐

- “今天建议复习 4 项，约 15 分钟。”
- “这条记录可能完成了 2 个任务，请确认。”
- “距离上次游泳已经 8 天，可以考虑本周安排一次。”
- “有 3 个单词需要再巩固。”
- “分析没有完成，你可以重试或手动记录。”

### 禁止

- “孩子落后了。”
- “你已经断签 3 天。”
- “必须今天全部完成。”
- “AI 判断孩子已经掌握。”
- “还有 18 项欠账未清空。”

## 8. 完整状态要求

所有核心界面在原型中必须覆盖适用状态：

- 首次使用/无孩子；
- 空数据；
- 正常；
- 加载；
- 多批任务并行；
- 部分数据可用；
- 分析中；
- 待家长确认；
- 网络或 Agent 失败；
- 重试；
- 取消；
- 保存成功；
- 只读或已删除资源；
- 长文本、大量知识点和多孩子；
- 离线时查看已有数据及恢复提示。

## 9. 视口与适配

- Device classes: 微信小程序内手机；桌面和 Pad 专用布局不在 MVP。
- Minimum supported logical viewport: 320×568 px。
- Primary design viewport: 390×844 px。
- Wide phone verification: 430×932 px。
- Orientation: portrait required；landscape 保证可返回和基本操作，但不做专用布局。
- Maximum content width: 480 px；更宽环境居中显示。
- DPR: 使用矢量图标；位图按 2x/3x 与原始质量策略导出。
- Text scaling: 关键流程支持系统字体放大，文字可换行，不以固定高度裁切。
- Safe area: 底部操作、Tab 和浮层避开 iPhone Home Indicator 与小程序胶囊区域。

### Required viewport matrix

| ID | Device/use | Logical viewport | Orientation | Required states | Evidence after approval |
|---|---|---|---|---|---|
| VP-MIN | 小屏边界 | 320×568 | portrait | happy、long-content、keyboard、error | local DREV export + device/E2E |
| VP-PRIMARY | 主设计基线 | 390×844 | portrait | 全部核心状态 | local DREV export + visual/E2E |
| VP-WIDE | 大屏手机 | 430×932 | portrait | happy、report、bottom-sheet | local DREV export + visual/E2E |

### 响应规则

- 单列布局，不把手机报表变成并排多栏。
- 小屏优先保留任务标题、预计时间和主操作；次要说明可折叠但不可丢失。
- 报表图表允许横向滚动仅限时间序列，并始终提供数字摘要。
- Bottom Sheet 最大高度约为可用视口的 85%，内容独立滚动，关闭入口始终可见。
- 键盘弹起时保持当前输入和主要保存操作可达。
- 文字超长时换行；知识点名称只在列表预览截断，详情可看全文。

## 10. 可访问性与信任

- 目标：以 WCAG 2.2 AA 的可感知、可操作原则作为通用基线，并结合小程序能力验证。
- 颜色不作为唯一状态；图标配文字或可访问名称。
- 保持逻辑阅读顺序和足够对比度，支持文本放大与焦点恢复。
- Toast 只提供补充反馈，关键错误同时留在页面中。
- 破坏性操作说明将删除哪些照片、记录和计划。
- AI 内容统一标记“AI 建议/待确认”，正式记录标记“已确认”。
- 不把孩子照片用于装饰、排行榜或公开分享。
- 权限申请只在用户触发拍照/相册操作时出现，并先解释用途。

## 11. UI current-state index

2026-10-24本地增量：用户“好的 按照这个方案落地”批准FEAT-013的[Spec02 / Architecture02](../../../specs/completed/FEAT-013-ANNUAL-GRADE-PROMOTION.md)、UI-001/UI-015的[DREV01](prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/FRONTEND-SPEC.md)与[57张导出/SHA](snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-01/APPROVAL.md)，批准源已冻结。已本地实现每孩子独立核对弹窗和一至九年级选项，沿用有效FDB/FEC；[实现证据](../../quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md)含三视口呈现矩阵/系统picker/档案控件、短屏错误滚动及四项修复后的独立评审PASS。修复后原生端到端、真实设备与可访问性仍待验收，不抵扣以下历史增量验收。

| UI-ID | Surface | Feature | Design Revision | Status |
|---|---|---|---|---|
| [UI-001](ui/UI-001-parent-miniapp.md) | 家长端与复习目录 | FEAT-001 | [DREV-20261020-SUPERSEDED-REVIEW-01](snapshots/UI-001/DREV-20261020-SUPERSEDED-REVIEW-01/APPROVAL.md)（本次目录增量） | approved 2026-10-20; implemented locally; complete native/device acceptance pending; earlier surfaces retain their own evidence |
| UI-002 | 今日计划 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-003 | 上传与手动录入 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-004 | 待处理/待确认中心 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-005 | 学习草稿确认 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-006 | 历史日历与每日详情 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-007 | 科目与知识详情 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-008 | 活动日程与练习记录 | FEAT-001 | proposed DREV-20260830-01 | not prototyped |
| UI-009 | 家庭与成员 | FEAT-002 | current DREV-20260906-PKDS-01；DREV-20260913-FAMILY-INVITE-CODE-01 | 原交付/验收状态见UI-009；多家庭及附带退出提案2026-11-05取消，成员资料仍为独立低优先级记录 |
| UI-011 | 提醒设置、本人自动补充与微信授权 | FEAT-003 / FEAT-011 | DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01 | approved 2026-10-17; implemented locally, device/full native acceptance pending |
| [UI-014](ui/UI-014-family-switcher.md) | 家庭与孩子上下文切换 | FEAT-002 | cancelled DREV-20260906-MULTI-FAMILY-02 | CANCELLED 2026-11-05，用户不再需要；未批准/实施，关联Spec已移rejected |
| UI-015 | 学习档案管理与切换入口 | FEAT-005 / FEAT-013 | 年级DREV01/02；归档DREV-20261024-CHILD-ARCHIVE-01 | archive approved/local, verification pending；分范围见UI-015 |
| [UI-018](ui/UI-018-child-photo-footprints.md) | 孩子照片足迹：精简入口、直接导入、核对与三视图 | FEAT-012 | DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01 + DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02 + DREV-20261024-RECORD-ENTRY-01 + DREV-20261024-FOOTPRINTS-MINIMAL-01 + DREV-20261024-FOOTPRINTS-TIMELINE-01 + DREV-20261025-TRAVEL-DIARY-E2E-01 + DREV-20261025-TRAVEL-IMPORT-02 + DREV-20261031-TRAVEL-ENTRY-CLEANUP-01 | VERIFYING；frontend349/static/design PASS，CLI login/preview1191019 PASS，320内嵌七态原生PASS；390/430/独立宿主/设备未验。候选后端staged测试FAIL，未部署/upload；批准资产冻结，历史15/42组保持原范围 |

## 12. Review decisions requested

请产品负责人对 `FDB-20260830-01` 明确确认或修改以下内容：

1. 是否认可“安静、温暖、可信、非游戏化”的总体气质？
2. 是否认可底部五 Tab：今日、日程、记录、报表、设置？
3. 是否认可主色为低饱和青绿色，而非儿童化多彩主题？
4. 是否认可 Todo 的主操作为完成，次操作为需要巩固/稍后？
5. 是否认可报告以本周和可追溯数字为主，不展示掌握率和排名？
6. 是否认可 AI 全部采用异步状态和待确认中心，不用阻塞式对话？
7. 是否认可手机竖屏为 MVP 唯一主布局？

## 13. Revision history

| Date | Revision | Change | Approved by |
|---|---|---|---|
| 2026-08-30 | FDB-20260830-01 | 首版微信小程序交互与视觉基线草案 | pending |
