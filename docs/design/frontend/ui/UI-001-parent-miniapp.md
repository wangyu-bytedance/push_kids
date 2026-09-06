# UI-001 — 家长端微信小程序

- Status: `CURRENT_LOCAL / AUTOMATION_PASSED / VIEWPORT_MATRIX_NOT_RUN`
- Related Feature: `FEAT-001`
- Baseline: `FDB-20260906-03`
- Engineering contract: `FEC-20260906-04`
- Design revision: `DREV-20260906-PKDS-03`（PKDS-2.0「纸 · 芽」；取代 `DREV-20260906-PKDS-02` 的视觉层与三处交互，信息架构与多科目/多孩子动线沿用）
- Current-state revision: `UI-STATE-20260906-PKDS-03-LOCAL`
- Related Spec: `specs/active/SPEC-20260906-PKDS-03-PAPER-SPROUT-UI.md` revision `SPEC-20260906-PKDS-03`
  （前序：`SPEC-20260906-PKDS-01`、`specs/active/BUG-013-MULTI-SUBJECT-AND-PARENT-FLOW.md` revision `BUG-SPEC-20260906-16`）
- Last verified: 2026-09-06（PKDS-2.0 合并 BUG-013 后全量自动化检查通过；320/390/430 原生几何与真机为 NOT_RUN）
- Screen-level spec: `docs/design/frontend/prototypes/DREV-20260906-PKDS-01/FRONTEND-SPEC.md`
- Reference screens: `docs/design/frontend/prototypes/DREV-20260906-PKDS-01/screenshots/`（39 屏）
- Intermediate artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`（设计历史）
- Figma waiver anchor: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Current information architecture

原生微信小程序面向家长，采用五个一级 Tab。所有页头只保留当前上下文与统一的紧凑孩子
切换器，不重复显示 Tab 已表达的大标题。

| Tab | Current responsibility |
|---|---|
| 今日 | 可折叠的今日复习、今日学习、今日活动；待确认/失败提示 |
| 日程 | 周日期轨、当天时间线、过去日程灰显、FAB 新建、编辑/删除日程 |
| 记录 | 同页新增/历史；照片/文字与实际时间；已确认/待处理/全部、搜索/半屏筛选/分页；列表进入独立的只读记录详情页 |
| 报表 | 7/30/100 天概览、组件内30天分页的复习紧迫度与活跃度、科目记录 |
| 设置 | 三项基础学科、手动添加的其他科目与课外活动、活动安排、家庭成员入口 |

学习流程的深层页面分成两类责任：`pages/submission/confirm` 是**可编辑草稿**的独立入口（从新增流程
或通知进入），`pages/record-detail` 承载**记录详情**——已入档为只读态，待确认态则在同页就地编辑并确认，
不再要求家长再跳一层。只读部分共用 `pages/submission/detail.js` 的 mixin 与 `detail.wxml` 模板，
可编辑草稿部分共用 `pages/submission/draft.js|wxml|wxss`，因此两个入口的文案与行为逐字一致。
另有活动练习记录页。产品 UI 不编辑服务地址、不展示账号占位；这些由后台配置或后续微信身份版本负责。

## State and interaction contract

- 每个远程页面有 loading、empty、content 和可重试 error；不会用示例卡片填空。
- AI 状态使用真实命名阶段，不显示虚构完成百分比；失败保留提交并可重试或人工录入，
  排队/分析中也可人工录入。进入表单不取消Job，提交成功才由服务端停止原任务。
- 图片可单张拍摄、相册一次多选和多次追加，统一 9 张上限；一次提交只创建一个分析任务。
- Job 创建前中断的多图批次显示“补传照片/取消”；零照片显示“等待上传照片”且不轮询。
  已有照片还可“继续分析”。补传沿用原草稿及批次票标识；失败后可重试，按钮有 loading/禁用态。
- 新增页只显示待处理数量；历史按服务端筛选、每页 20 条，前后分页保持有界渲染。
  待处理/全部可见时轮询；服务器返回全量范围的分析标志，不因分析项在后页而停止轮询；已确认历史不轮询。
- 历史详情先显示正式总结和本次知识，原始材料与复习反馈按需展开；已确认/取消不出现编辑确认按钮。
  待处理详情可补传、继续分析、人工录入、重试或确认后取消；人工表单和既有确认逻辑保留。
- 原始材料展开后最多并发下载两张照片，缩略图点击重新鉴权取得原图；临时引用/文件在退出时清理，
  无图、图片删除、权限失效和网络失败分别呈现；搜索文字不进入 URL。真实云端预览仍待验证。
- 云环境的照片预览直接使用服务端签发的短期 HTTPS 地址（`<image>` / `previewImage` 不受 request
  合法域名限制，`wx.downloadFile` 受限），本地联调仍走带身份的容器下载并落临时文件；远端地址
  不做 unlink。图片自身的 load/error 也会落到状态上，失败只影响该张照片。
- 报表科目、今日学习/待处理进入同一历史入口，日期/科目意图只消费一次；列表返回保留条件与页码。
  详情可查看每个知识的当前计划与每页 3 条反馈，到期时跳回今日；浏览材料不记为完成复习。
- AI 草稿可编辑；“确认”是创建正式记录、知识和复习项的唯一入口。待确认记录在记录详情页直接编辑确认，
  确认页与详情页共用同一份草稿实现，不存在两套编辑逻辑。
- 一次提交跨多个科目时，草稿按服务端 `subject_groups` 分组展示“科目归类”：每组可整体换科目，
  单个知识点也可单独换科目；确认后每个科目各生成一条学习记录，不会出现“数学、语文”这类合成科目。
- 科目名不在孩子的科目列表里时该组显示提醒，并要求家长明确回答“新增这个科目吗”；未回答时确认
  返回 `consent_required`，界面用弹窗再问一次，草稿与输入保留，不静默创建科目。
- 草稿展示知识点的置信度文字、照片编号/家长文字证据及总体不确定项；缺证据的旧草稿/家长
  新增点明确提示核对原始材料。证据仅供核对，不代表模型判定掌握。
- 关联已有知识显示复用/保留进度说明，并可取消关联；改名/类型会解除该点关联，改科目会清空
  全部关联和Todo匹配。科目选择只提供有效learning项，并允许输入新学习科目。
- 人工表单保留完整原文与实际发生时间；原文超过500字时要求另写总结，不静默截断；不显示
  AI置信度或证据，不自动匹配Todo。保存失败保留输入和可见错误，保存中防重复操作。
- 重复材料提示放入“需要核对”；Todo匹配显示证据，已更新的任务不会再次推进。
- 今日从同一个 Dashboard 读取复习、已确认学习和日程。三栏独立折叠，不使用只计算复习的
  “今日总体进度”卡。默认复习与学习折叠、日程展开；本地偏好里的非布尔脏值回落到该默认。
- 设置页不展示或编辑每日复习预算；当前服务端默认值继续用于 required/optional 分组。
- 设置主页固定展示数学、语文、英语及真实已添加项；其他科目和课外活动从候选目录或自定义名称显式添加。打开或取消添加/提醒弹层不写数据。
- 三栏成功空结果显示居中空文案；全部为空且没有待处理记录时显示“记录学习/添加日程”引导，添加日程意图只消费一次。
- ActivitySchedule 是设置、今日和日程的统一来源；固定安排必须有开始/结束时间。
- 今日还消费不与固定日程重复的柔性活动建议；活动提醒可直接移除。
- Todo 的“带练提示”只提交当前所选且已确认的 Review IDs。
- Todo 的主观反馈在卡片内展开，选项旁写明对复习安排的影响；文案与服务端确定性策略一一对应
  （reinforce = 退一步、明天再出现；partial = 下一轮间隔取一半；defer = 同一步、明天再出现）。
- 日程卡点击编辑；重复日程 MVP 修改整个系列。结束时间早于当前时刻后统一灰显。
- 报表范围切换会重新请求 7/30/100 天数据并回到第1屏；100天在组件内部按30/30/30/10左右分页，页面根容器不横向移动。
- 报表四个概览指标是 2×2 独立描边卡片并保留间距；学习记录跳记录页并带上当前区间筛选，新增知识/
  复习反馈/活动练习在页内滚动定位到对应区块；指标为 0 时弱化显示并用 Toast 说明，不跳到空页面。
- 紧迫度同时显示数字/勾与颜色，活跃度同时保留次数语义，颜色不是唯一信息。
- 孩子切换器和折叠箭头都使用 CSS 矢量 chevron，不使用字体字形 `⌄`。
- Todo 卡片的"为什么出现"由服务端结构化字段拼装：来源提交、来源学习日期、复习轮次和间隔天数。
  历史数据缺这些字段时只隐藏该行，Todo 本体与操作保持可用。
- 知识点的置信度一律表述为"AI 识别把握程度"，并附"仅供核对、不代表模型判定掌握"的说明。
- 原始材料按服务端 `sort_order` 升序渲染，照片编号稳定，重复进入顺序不变。
- 设置页区分内置三科与家长自定义科目；只有自定义项可以移出。
- 今日页与记录页都会用最新的待处理数更新"记录" Tab 徽标，两者不会互相覆盖出不一致的数字。
- 需要远程数据的页面统一开启原生下拉刷新；弱网失败时保留已加载内容并显示页内可重试错误条，不清空为空态。
- 折叠分区、报表区间和历史筛选条件按 childId 持久化在本地偏好中，不进入请求 URL。

## Visual system

当前视觉系统是 PKDS-2.0「纸 · 芽」，可见合同见 `DREV-20260906-PKDS-03`。

方向是暖白纸面 `#FAF7F0`（卡片 `#FFFDF8`）、松绿主色 `#1F5B45`、嫩芽成长色 `#7FA65C`、
提醒赭石 `#A9762A`、异常陶土 `#A85742`。阴影大而淡，卡片像纸叠在纸上；标题使用衬线族
（`Songti SC` / `Noto Serif SC`）制造纸感，正文用系统中文无衬线，数字统一 tabular-nums。
信息依靠排版和留白建立层级，不采用儿童游戏化、排行榜、玻璃拟态或企业 BI 密集卡片。
底部半屏层使用统一 handle、标题、关闭和主操作；日程新增使用右下角浮动加号。

PKDS-2.0 相对 PKDS-1.0 的可见变化：

- 底部 TabBar 为半透明毛玻璃底栏 + 中央凸起的「记录」主键（拍照即主操作），徽标显示待处理数。
- 今日页首屏是"安排环"：12 刻度按 必做 / 有余力 / 未占用 三态着色，中心是「N 项 今日到期」。
  它只描述今天到期复习的构成，不是完成率、不是评分。
- Todo 卡片左侧有主色轨区分"建议完成 / 可选"；「其他反馈」在卡片内展开面板，
  三个选项各自标注对下次复习的影响（明天再出现一次 / 间隔取一半 / 今天不再提醒）。
  不再使用系统 ActionSheet。
- 确认页用「AI 草稿 · 待确认」虚线印章持续标注草稿态，人工录入用 `.stamp.manual`。
- 确认页科目字段只有一个决定点：命中已在学科目时显示 picker + 「换成新科目」；
  新科目态显示输入框 + 「选已在学的科目」。
- 报表第一段标题是「接下来的复习压力」，只陈述待复习数量与是否已全部通过，不含能力评价词。
- 原生自定义 TabBar 是独立图层，页面内 `fixed` 半屏无法遮住它，因此 `.pk-sheet` 默认预留
  TabBar 高度；非 Tab 页用 `.pk-sheet.plain` 收回这段预留。

实现分三层且方向单一：

| 层 | 文件 | 职责 |
|---|---|---|
| token | `apps/miniprogram/styles/tokens.wxss` | 语义色、科目色、圆角、间距、高度、动效、触控尺寸的唯一来源；含旧变量名兼容别名 |
| 原子/组件 | `apps/miniprogram/styles/atoms.wxss` | Card / Hero / Section / Button / Pill / SubMark / Confidence / Notice / Segmented / Chips / 表单 / RowList / Timeline / WeekStrip / FAB / Metrics / PhotoUploader / 浮层四件套 / 空态 / 骨架 |
| 图标 | `apps/miniprogram/styles/icons.wxss` | 42 个线性图标 × 6 个语义色变体（24×24 viewBox，stroke 1.8），由 `tools/gen_icon_styles.py` 生成，禁止手工编辑；TabBar 位图由 `tools/gen_tabbar_icons.py` 用同一图标语法生成 |
| 页面 | `pages/*/**.wxss` | 只写本页特有几何，不重复定义 token |

`apps/miniprogram/utils/ui.js` 承担纯展示派生（科目色/首字标记、活动图标映射、置信度档位、反馈文案、
月日格式、复习原因文案、本地偏好读写），不发请求、不持有业务状态；这是为了满足 WXML 不支持
方法调用的平台约束。圆角只允许 8/12/16/24/32/40/999rpx；图标不允许使用 emoji 或文字符号。
课外活动图标由 `activityIcon(name, tone)` 按名称关键字包含匹配派生（游泳/乒乓球/篮球/羽毛球/
足球/网球/棋/钢琴/音乐/舞蹈/武术/书法/绘画/机器人/编程各自一个图标），家长自建且命中不了的活动
统一使用默认星形图标；页面在 JS 里算好 `iconClass` 后 setData，WXML 只做拼接。

## Responsive and accessibility

目标竖屏视口为 320×568、390×844、430×932。触控目标不小于 44px；长内容垂直滚动；
普通业务页面不使用横向滚动；七天、报表范围、基础科目和活动星期均在当前视口完整显示。关键状态有文字语义，表单保留输入，错误不只
依靠 Toast。图片不进入本地存储或日志。云环境 JSON 统一走 `wx.cloud.callContainer`，图片按
服务端 ticket 使用 `wx.cloud.uploadFile` 后 claim；页面不持久化 fileID 或 OpenID。

## Implementation and current evidence

| Contract | Path/evidence | Result |
|---|---|---|
| shell/tokens | `apps/miniprogram/app.*`, `apps/miniprogram/styles/*` | five exact tabs; PKDS-2.0 三层样式 |
| pages | `apps/miniprogram/pages` | 12 pages validated（新增 `pages/record-detail/index`） |
| display helpers | `apps/miniprogram/utils/ui.js` | 纯函数，无网络与业务状态 |
| icons | `tools/gen_icon_styles.py` | 重跑产物 diff 为空（幂等） |
| API/config | `utils/api.js`, `utils/cloud-media.js`, `config.js` | cloud env/service + callContainer + server-issued upload path；local fallback retained |
| JS behavior | `tests/frontend` | 78 passed |
| static package | `tools/validate_miniprogram.py` | `MINIPROGRAM_VALID pages=12 source_bytes=533311`; no WXML method calls |
| lint | ESLint | passed |
| WeChat DevTools | registered AppID preview | compiled; final 175,099-byte preview package |
| WeChat platform API audit | `WECHAT-MINIPROGRAM-API-BASELINE.md` | compatibility/error-recovery changes proposed; not implemented |

The accepted HTML version remains a design-history artifact. It is not loaded by the Mini Program and does
not provide runtime data.

BUG-007 增量执行了真实页面 JS 的 Node VM 测试（等待上传无轮询、同草稿续传、票槽复用、
分页后轮询继续/页面保留、低置信度证据展示）。原生开发者工具已查看，当前显示“当前微信用户
尚未绑定家庭”，未进入受影响页面；没有修改云身份或真实数据。因此 320×568、390×844、
430×932 的实际渲染/交互验收和真机弱网测试仍为 NOT_RUN，不将源码/VM 测试称为视觉通过。
记录操作区允许换行、按钮至少 44px；证据长文本折行，沿用现有 notice/card 样式。

BUG-010 本地实现已通过微信开发者工具 registered AppID preview 编译，并通过 automator 在
iPhone 12/13 (Pro)、390×844、DPR 3、SDK 3.16.2 下采集今日、日程、记录、报表、设置、家庭
成员和申请空态截图。证据确认7日、3档报表、3基础科目完整，圆形与拍照操作居中；
期间再次发现并修复三科溢出、刷新按钮椭圆和线上旧后端邀请列表405拖垮成员页。320/430、
字体放大、键盘、真机和双账号仍为 `NOT_RUN`，因此当前修复不能描述为完成全矩阵验收或已部署。

## Known deviation / release gate

Cloud transport and upload wrappers have automated coverage, but real `callContainer`、storage owner rule、
camera authorization、weak-network resume and iOS/Android evidence are not claimed. They are mandatory before
the experience build is accepted. The repository does not yet retain a minimum base-library setting or capability
guards for `callContainer`、`uploadFile` and `chooseMedia`; media permission failures, safe platform error
classification and cancelable uploads are tracked by `BUG-SPEC-20260905-02` and remain unimplemented.

## Change references

- 2026-09-06 — `SPEC-20260906-PKDS-03 / DREV-20260906-PKDS-03`：视觉语言换为 PKDS-2.0「纸 · 芽」
  （暖白纸面 + 松绿 + 嫩芽色，衬线标题，大扩散淡阴影），重做 TabBar（中央「记录」凸起键）、
  今日页安排环（只表达必做/有余力的构成，不表达完成率）、Todo 卡片内嵌反馈面板（每个选项直接
  写明它如何改动复习安排）、草稿区「AI 草稿 · 待确认」印章、报表首段文案改为「接下来的复习压力」。
  修复：日程页/报表页 `.chev.left` 被错误覆盖导致左箭头显示为上箭头；`.pk-sheet` 未预留原生
  TabBar 高度导致半屏末条被遮；`app.json` 与 `wx.showModal`、`switch` 等原生控件仍残留 PKDS-1.0 色值。
  与 `BUG-013` 合并时的取舍：保留上游按活动语义派生的 16 个图标与按知识点分组的多科目动线，
  本轮的通用 `ico-ball` 与确认页单一科目路径作废；印章与滑杆配色改到共享模板
  `pages/submission/draft.*`，确认页与待确认页同时生效。
  新增本地设计走查工具 `tools/preview/`（WXML→HTML 近似渲染 + 320/390/430 截图 + 横向溢出扫描）。
  自动化证据（与 `BUG-013` 合并后复跑）：前端 91 passed、ESLint 通过、
  `validate_miniprogram.py pages=13 source_bytes=580105`、图标生成器幂等、
  后端 186 passed / 2 skipped、ruff check + format（185 files）、mypy（55 files）、
  `ARCHITECTURE_VALID checked=2`、三视口预览 15 组页面 45 个视口无横向溢出。
  真机/开发者工具原生几何仍为 `NOT_RUN`，未部署。
  设计稿与实现走查（外部只读参考，非验收依据）：
  <https://0e91e62cff85.aime-app.bytedance.net>（可点击原型）与
  <https://0e91e62cff85.aime-app.bytedance.net/impl.html>（15 页 × 320/390/430 源码渲染截图，
  取自合并后的源码）。

- 2026-09-06 — `BUG-013 / BUG-SPEC-20260906-16 / DREV-20260906-PKDS-02`：六项家长动线修复。
  (1) 多科目草稿按服务端确定性归类分组展示，可整组或按知识点改科目，新增科目需家长显式同意，
  不再出现「数学、语文」这类合成科目；(2) 待确认记录在 `pages/record-detail/` 就地编辑确认，
  新增共享草稿模块 `pages/submission/draft.*`，确认页与详情页不再各写一套；(3) 课外活动图标
  按活动语义派生，生成器新增 swim/pingpong/basketball/badminton/soccer/tennis/chess/piano/music/
  dance/martial/brush/palette/robot/code/star 共 16 个图标并删除通用 `ico-ball`，自建活动用星形默认；
  (4) 报表四指标改 2×2 独立卡片并加 `gap`，支持跳转记录页或页内定位，0 值只提示不跳空页；
  (5) 今日默认折叠复习与学习、展开日程；(6) 云环境照片预览改用服务端签发的 HTTPS 地址，
  远端地址不再 unlink，预览签发限额从 30/min 提到 120/min，解决「照片暂时无法读取」。
  自动化证据：前端 78 passed、ESLint 通过、图标生成器两次产物 md5 一致（幂等）、
  `validate_miniprogram.py pages=12 source_bytes=533311`、后端 171 passed / 2 skipped、
  ruff check + format（172 files）、mypy（55 files）、`ARCHITECTURE_VALID checked=2`。
  320×568 / 430×932 原生几何、字体放大、键盘态、真机弱网与真实云端图片预览仍为 `NOT_RUN`，未部署。

- 2026-09-06 — `SPEC-20260906-PKDS-01 / DREV-20260906-PKDS-01`：全部 12 个页面与 2 个组件按
  PKDS-1.0 重做；新增 `apps/miniprogram/styles/{tokens,atoms,icons}.wxss` 与 `utils/ui.js`；
  新增只读记录详情页 `pages/record-detail/`，确认页只保留可编辑草稿；服务端新增
  `review_items.source_submission_id`、`submission_media.sort_order`、
  `knowledge_items.confidence/evidence_json`、`subjects.is_custom` 并在 todos/dashboard/report/
  history/subjects 返回，使 Todo 出现原因、照片顺序、识别把握程度和自定义科目在界面上可解释。
  自动化证据：后端 131 passed / 2 skipped，ruff、mypy、architecture check 通过，前端 59 passed，
  ESLint 通过，`validate_miniprogram.py` pages=12，图标生成器幂等。
  320×568 / 430×932 原生几何、字体放大、键盘态与真机弱网仍为 `NOT_RUN`，因此本轮不能描述为
  完成全矩阵可见验收，也未部署。已知与设计稿的偏差（为满足既有测试断言而保留的文案与网格模板、
  报表周期摘要未实现等）逐条记录在 Spec 的 §16 Deviations。

- 2026-09-05 — `DREV-20260905-UX-04`：六个主要页面已按批准 HTML 在原生小程序中落地，并完成 390×844 同尺寸截图对照。自定义 Tab 使用本地图标并在直接进入页面时恢复高亮；七日日历同屏，整页禁止横向滚动；100 天报表仅图表区按 30/30/30/10 分屏。当前账号数据与原型例数据的差异不视为布局问题；320/430、字体放大、键盘和真机仍是发布门禁。

- 2026-09-05 — BUG-010 截图回归：目录按钮、星期居中、日历七天/FAB、报表单页提示及滚动范围条已本地修复。390视觉与320部分复查；[证据与未完成项](BUG-010-20260905-layout-followup.md)。该条是 UX-04 获批落地前的阶段记录，现已由上一条更新。

- 2026-09-05 — `SPEC-HISTORY-20260905-01 / DREV-20260905-HISTORY-01`：实现历史/材料回看，
  未增加页面路由；继承既有 FEAT-001 waiver，批准快照位于 `snapshots/UI-001/DREV-20260905-HISTORY-01/APPROVAL.md`。
  58 项前端测试与预览编译通过；CUA 因 Mac 锁屏无法执行本次三视口、字体放大和键盘验收，不能引用 BUG-010 的截图代替。

- 2026-08-31 — `DREV-20260830-03 / SPEC-20260831-08`: native conversion of the accepted HTML,
  five Tab IA, unified schedule, contextual reports, multi-photo batch and backend-configured profiles.
- 2026-08-30 — `BUG-002`: removed parent-editable API URL and ambiguous child create/save copy.
- 2026-09-03 — `CLOUD-SPEC-20260903-03`: switched the non-visible network/media infrastructure to
  callContainer and private cloud direct upload without changing the approved visual design.
- 2026-09-05 — `WX-API-BASELINE-20260905-01 / BUG-SPEC-20260905-02`: audited the used `wx.*` APIs and
  proposed minimum-version, capability, permission, error and upload-recovery hardening; implementation pending approval.
- 2026-09-05 — `BUG-SPEC-20260905-05 / DREV-20260905-P2-01`: P2 上传恢复、待处理分页、证据提示；
  当前可执行页面逻辑已验证，真实设备/视口验收待家庭绑定测试环境。
- 2026-09-05 — `BUG-SPEC-20260905-07 / DREV-20260905-AI-01`: 人工兜底、关联已有知识与重复材料
  提示；本轮开发者工具未运行且CUA选择超时，320/390/430真机渲染仍NOT_RUN，详见BUG-009验证。
