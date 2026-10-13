# UI-001 — 家长端微信小程序

- 2026-10-13最新设置本地增量：SPEC-20261013-SETTINGS-CONSISTENCY-01 / DREV-20261013-SETTINGS-CONSISTENCY-01批准并实现；在学科目统一活动式单列行；每日任务独立书本/时钟装饰、整行编辑、添加候选半屏，预设需保存。取代科目三列、任务常驻预设/独立编辑/内联表单描述。239项测试、静态/设计/架构与430原生八态通过；320/390原生、完整截图、真机待验收，本轮未上传。证据docs/quality/evidence/SETTINGS-CONSISTENCY-20261013.md。

- 2026-10-13背景全面接入：设置科目/活动/出行不同插画与纸面背景；每日任务同款背景和列表、紧随活动之后；报表顶部成长记录插画和统一卡片背景。Spec SPEC-20261013-CARD-BACKGROUNDS-01 / Design DREV-20261013-CARD-BACKGROUNDS-01。238测试、静态校验及1017670字节CLI预览包通过，三视口HTML仅辅助；原生/真机/用户验收待补，未发布。证据docs/quality/evidence/CARD-BACKGROUNDS-20261013.md；本增量取代上文“设置/报表背景未接入”的历史事实。

- 2026-10-13报表展开区本地增量：`SPEC-20261013-REPORT-PANELS-01 / DREV-20261013-REPORT-PANELS-01` 已批准并实现；历史平铺分隔、计划明确「调整」、顶部与底部收起，两区独立展开。外层继承统一pk-card背景，不覆盖并行卡片美化。236项测试及三视口36态原生数字几何通过；完整截图、字体放大及真机待补；已随0.1.14开发上传，未设体验版/正式版。证据：`docs/quality/evidence/REPORT-PANELS-20261013.md`。

- 2026-10-13本地视觉增量：记录标题卡书本插画、空上传相机插画及日程台历插画使用统一纸面渐变；Design `DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01` 已批准，新增资源173638字节。保留原文案、业务和导航；装饰失败自动回退。233项测试通过，原生三视口及真机验收待补，未发布。详见 `docs/quality/evidence/RECORD-CALENDAR-ILLUSTRATIONS-20261013.md`。

- Status: `CURRENT / VOICE_INPUT_LOCAL_VERIFIED / MICROPHONE_PRIVACY_DECLARATION_BLOCKED / DEVELOPMENT_VERSION_0.1.14_UPLOADED / NATIVE_VIEWPORT_MATRIX_NOT_RUN`
- Release status: `0.1.14` 已上传为开发版本（1017762字节），包含每日任务、背景插画、报表布局；未设体验版/审核/正式版。2026-10-13生产Schema已升级0019、后端030已全量模式发布且normal，真实小程序设置依赖及每日任务等13项读取接口200；设置页刷新后档案与各设置数组加载、error为空。原生全部状态/真机验收仍待完成。证据：`docs/deploy/releases/20261013-fullstack-diff.md`；0.1.13是历史开发上传基线。
- Related Feature: `FEAT-001`
- Local report disclosures: `SPEC-20261011-REPORT-DISCLOSURES-01 / DREV-20261011-REPORT-DISCLOSURES-01` 已获用户批准并本地实现。
  报表科目统计后依次为「历史记录」「编辑计划」两张默认收起的卡，课外活动投入在其后；展开分别复用完整有界历史和条目清单，互不覆盖。原独立条目页标题同步改为「编辑计划」；记录页保留新增及待处理入口，历史列表移出。12张设计快照及SHA、前端自动化和三视口四状态微信原生数字几何已通过；开发版本 `0.1.13` 已上传，iOS/Android真机未验收，未设体验版/正式版。证据：`docs/quality/evidence/REPORT-DISCLOSURES-20261011.md`、`docs/deploy/releases/20261011-report-disclosures-frontend.md`。
- Local review-inventory redesign under verification: `SPEC-20261010-REVIEW-INVENTORY-REDESIGN-01 / DREV-20261010-REVIEW-INVENTORY-02` 已获用户批准并本地实现。
  当时原生导航保留唯一“复习条目”标题（2026-10-11 已改为「编辑计划」）；时间双日、科目/次数下拉分别占一层筛选；时间/次数按科目折叠、单科为扁平分隔清单。条目保留完整标题、真实次数、最近复习、建议/家长日期、今日安排状态和44×44就近菜单。科目翻页不再暗中切换当前科目。
  前端216项、设计SHA、静态与320/390/430十组微信原生数字矩形通过；320次数展开和390时间视图已人工看图。该客户端实现随 `0.1.13` 开发版本上传；iOS/Android真机与风险状态补充证据仍待完成，未设体验版/正式版。证据：`docs/quality/evidence/REVIEW-INVENTORY-REDESIGN-20261010.md`。
- Settings activity order: `SPEC-20261010-ACTIVITY-WEEKDAY-ORDER-02 / DREV-20261010-ACTIVITY-WEEKDAY-ORDER-01`
  用户2026-10-10批准，已本地实现首时段星期、开始时间升序，缺少有效星期或时段排最后，同键保序。
  WXML/WXSS、布局、图标、文案及交互结构完全不变；排序后点击仍按新列表索引编辑正确活动。
  213项前端测试及静态检查通过，该排序随 `0.1.13` 开发版本上传；原生三视口证据待补，未设体验版/正式版。
  证据：`docs/quality/evidence/ACTIVITY-WEEKDAY-ORDER-20261010.md`。
- Historical grouped-card revision superseded locally by the 2026-10-10 redesign: `SPEC-20261007-REVIEW-GROUP-CARDS-05 / DREV-20261007-REVIEW-GROUP-CARDS-01` 曾获用户批准并在本地小程序实现。
  时间/科目/次数视图将当前有界页按科目聚合为可折叠组卡；条目右侧固定 44×44px 的“…”就近打开操作菜单，指定次数仅在用户输入后显示具体数字。
  筛选用日期两列、科目和次数三列的等宽按钮，第四个科目按同列宽度换行。320×568、390×844、430×932 微信原生数字矩形共 12 组（含菜单）审计通过；320/430 原生截图和390 CUA模拟器画面已人工检查。
  前端 207 passed、静态检查通过；新版 DREV 快照仍为 AWAITING_EXPORT，iOS/Android 真机未验收，尚未部署此本地修订。详见 `specs/active/FEAT-001-REVIEW-INVENTORY-GROUPED-CARDS.md`。
- Fair-review local revision: `DREV-20261007-FAIR-REVIEW-01 / SPEC-20261007-FAIR-REVIEW-01` 已获批准。
  今日移除策略说明和等待总数；条目分别显示建议复习日/家长安排日期和今日已安排/等待安排等状态。
  旧API显示“计划日期/安排状态待更新”；200项前端测试及静态检查通过，39张设计导出及hash通过。
  本地微信preview通过，669664字节，未上传开发/体验/正式版；原生三视口及iOS/Android待用户验收。
  后端性能修复通过，生产迁移尚未执行。证据：`docs/quality/evidence/FAIR-REVIEW-PROJECTION-20261007.md`。
  下文旧“到期”条目日期展示由本地本修订替代。
- Baseline: `FDB-20260913-04`
- Engineering contract: `FEC-20261007-NATIVE-GEOMETRY-02`
- Design revision: `DREV-20261001-RECORD-VOICE-INLINE-03`（记录页紧凑输入框内嵌麦克风；仅本地验证）
- Current-state revision: `UI-STATE-20261006-REVIEW-MANAGEMENT-03-LOCAL`
- Review management design/spec: `DREV-20261006-REVIEW-MANAGEMENT-03 / SPEC-20261006-REVIEW-MANAGEMENT-03`，
  用户于2026-10-06“落地并实现”批准；原生页面已本地实现，未发布。DREV03导出/原生三视口/真机尚未验收。
  新页`pages/review-inventory/index`从报表区间前进入；单科目录无“全部”，与日期一致的下划线选择。
  次数全部/0/1/2/3直接选择；指定次数数字弹层确定才应用、取消保留，非法值留在表单内。
  条目显示实际次数/最近复习/到期，调整菜单提高/降低优先级，红色删除需确认；viewer/归档只读。
  翻页替换至多50行；科目目录后页刷新或调整后保留当前科目。
  云bootstrap后确定权限，家庭/孩子切换清除旧行并丢弃迟到响应。验证见`docs/quality/evidence/REVIEW-MANAGEMENT-20261006.md`。
- Today design revision: `DREV-20261006-SOURCE-DELETE-01`，用户于2026-10-06批准；本地实现，未发布。
- Today Spec: `specs/active/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md`
  revision `SPEC-20261006-SOURCE-DELETE-02`；原生三视口及iOS/Android验收尚未完成。
- Related Spec: `specs/completed/BUG-025-REVIEW-ONLY-CONFIRM-SUBJECT.md` revision `BUG-SPEC-20260919-REVIEW-ONLY-CONFIRM-01`
  （前序：`specs/completed/BUG-023-TODAY-REVIEW-SOURCE-MATERIAL.md` revision `BUG-SPEC-20260919-REVIEW-SOURCE-01`；
  `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01`、`SPEC-20260911-PRIMARY-NAV-BRAND-01`、`SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`、`SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02`、`SPEC-20260911-RECORD-SIMPLIFICATION-01`、`BUG-SPEC-20260911-01`）
- Last verified: 2026-10-02（语音输入专项 13 passed、全量前端 184 passed、后端 389 passed / 5 optional skipped，
  ESLint、小程序静态 15 pages/685412 bytes、Ruff check/format、Mypy、架构与设计证据均通过；真实 AppID
  preview 634.8 KB / 650045 bytes 通过且未上传。开发者工具本地调用麦克风授权返回 `errno 112`：目标
  AppID 的隐私保护指引尚未对运行态生效；管理员补充麦克风信息后清除 compile/network 缓存复测仍返回
  `errno 112`，因此授权与 iOS/Android 真机矩阵继续等待指引审核/生效。此前共享确认映射：
  修复前专项 9 passed / 1 failed，
  修复后专项 10 passed、全量前端 170 passed、ESLint、小程序静态 15 pages/667593 bytes、架构与设计策略
  均通过；没有布局、文案、控件或视觉变化。真实 AppID preview PASS，包体 603182 bytes / 589.0 KB，
  `0.1.12` 开发版本已上传；原生320×568/390×844/430×932节点几何、字体放大、iOS/Android仍为NOT_RUN）
- Screen-level spec: `docs/design/frontend/prototypes/DREV-20260919-TODAY-SOURCE-MATERIAL-01/FRONTEND-SPEC.md`
- Reference screens: `docs/design/frontend/prototypes/DREV-20260906-PKDS-01/screenshots/`（39 屏）
- Intermediate artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`（设计历史）
- Design evidence governance: `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`; former Figma anchor is historical only

## Current information architecture

原生微信小程序面向家长，采用五个一级 Tab。五个一级页面逐页使用 `navigationStyle: custom`，由共享
`components/primary-nav` 按状态栏与右上胶囊几何渲染居中的“嫩芽图标 + 知芽”；内容区不再重复产品名，
直接从句子式 hero 与紧凑孩子切换器开始。今日日期、日程周范围和报表统计边界作为 hero 次级文本保留。
二级页面（确认、记录详情、家庭、提醒等）不使用该组件，继续保留微信原生标题、返回按钮与返回手势。

| Tab | Hero 标题 | Current responsibility |
|---|---|---|
| 今日 | 今天，也慢慢来 | 今日到期复习、今日学习、今日活动；待确认/失败提示；未来安排在报表「编辑计划」查看 |
| 日程 | 这一周，心里有数 | 周日期轨、当天时间线、出行投影、全部日程项冲突提示、过去日程灰显、FAB 新建、编辑/删除日程 |
| 记录 | 一笔一画，都算数 | 默认展示照片、紧凑文字框与框内语音入口的统一新增表单，保留待处理入口；完整历史列表在报表 |
| 报表 | 一点一滴，看得见 | 7/30/100 天只读概览与固定 7 点趋势微图、组件内30天分页的复习紧迫度与活跃度、可下钻科目记录；科目之后依次为默认收起的历史记录、编辑计划，课外活动投入在最后 |
| 设置 | 按你们的节奏来 | 三项基础学科、手动添加的其他科目与课外活动、活动安排、出行安排、家庭成员入口 |

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
- 记录页不再显示“新增/历史”和“拍照/文字”两组切换。照片入口与学习内容输入始终同屏；有照片走
  既有照片批次，无照片但有文字走既有 manual submission，两者皆空时只做本地校验且不发请求。
- 学习内容框高度为 184rpx，右下角内嵌 88rpx（44px）麦克风热区。按住录音、松开转写、上滑
  80rpx 取消；首次授权后提示重新按住，不在旧手势上自动开录。识别结果追加到同一可编辑文字框，
  超过 4000 字时保留原文并进入独立可编辑的待加入态。录音/转写期间阻止重复录音和提交；失败、
  无语音、拒绝权限、离页、切孩子和迟到回调均保留现有表单，手动文字始终可用。
- 空照片状态和已有照片后的“+”使用同一个添加入口；每次均由微信原生媒体选择开放拍摄与相册。
  拍摄返回后可再次点“+”继续拍摄，相册可按剩余额度多选，所有轮次共享 9 张上限；取消、空返回或
  失败保留已有照片、学习内容、时间与提交状态，上传中不重复打开选择器。
- 历史位于报表科目学习记录之后，首次进入、切孩子和重新进入时默认收起，只读取待处理数量；展开、待处理入口或
  今日/报表显式历史意图才读取完整列表。viewer 无新增权限，展开后为只读历史。
- 历史按服务端筛选、每页 20 条，前后分页保持有界渲染。
  待处理/全部可见时轮询；服务器返回全量范围的分析标志，不因分析项在后页而停止轮询；已确认历史不轮询。
- 历史详情先显示正式总结和本次知识，原始材料与复习反馈按需展开；已确认/取消不出现编辑确认按钮。
  待处理详情可补传、继续分析、人工录入、重试或确认后取消；人工表单和既有确认逻辑保留。
- AI 自动生成的学习总结只显示一句、不超过 60 字且只描述本次实际学习/练习内容；不展示“没有某任务”
  “不包含某科”“未涉及某内容”等缺失项说明。该限制只约束模型草稿，家长仍可按既有 500 字合同编辑，
  已确认历史不自动重写。
- 原始材料展开后最多并发下载两张照片，缩略图点击重新鉴权取得原图；临时引用/文件在退出时清理，
  无图、图片删除、权限失效和网络失败分别呈现；搜索文字不进入 URL。真实云端预览仍待验证。
- 云环境的照片预览直接使用服务端签发的短期 HTTPS 地址（`<image>` / `previewImage` 不受 request
  合法域名限制，`wx.downloadFile` 受限），本地联调仍走带身份的容器下载并落临时文件；远端地址
  不做 unlink。图片自身的 load/error 也会落到状态上，失败只影响该张照片。
- 报表科目、今日学习/待处理进入报表内同一历史折叠区，日期/科目意图只消费一次；列表返回保留条件与页码。
  详情可查看每个知识的当前计划与每页 3 条反馈，到期时跳回今日；浏览材料不记为完成复习。
- AI 草稿可编辑；“确认”是创建正式记录、知识和复习项的唯一入口。待确认记录在记录详情页直接编辑确认，
  确认页与详情页共用同一份草稿实现，不存在两套编辑逻辑。
- 新草稿把识别结果明确呈现为“新知识 / 今日复习 / 历史复习”：标签只读，不要求家长选择分类；
  每项同时写明确认后是新增知识还是推进既有复习。取消复习关联时，本次内容保留为可编辑的新知识，
  后续复习日期仍由服务端确认事务计算。
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
- 重复材料提示放入“需要核对”；Todo匹配显示证据。确认前已经完成、推进、改期、删除或身份事实变化的
  原始匹配由服务端安全跳过，不会再次推进，也不阻断其余学习保存。确认遇到终态冲突时页面立即自动读取
  并展示最新只读详情，不再显示“刷新会离开当前编辑的草稿/查看最新”；仍未进入终态或读取失败时保留编辑
  和页内错误，不假成功。
- 今日从同一个 Dashboard 读取复习、已确认学习和日程。新后端存在 `review_selection` 时，复习数量、
  分钟和卡片只取首次物化的稳定日计划；完成后只减少，不从全量到期列表补题。未选到当日计划的到期项
  只显示低压力的后续安排数量。旧后端缺少该字段时继续使用原 Todo 兼容路径，不承诺稳定计划。
  四栏独立折叠，不使用只计算复习的“今日总体进度”卡。每日任务位于复习安排下面。
  本地 `DREV-20261012-DAILY-TASKS-01` 实现：复习、每日任务、活动按完整剩余计数默认展开，空或全部完成收起；
  学习记录非空展开、空收起。未来安排不强制打开今日复习。活动以实际记录判断，时间已过不算完成。
  手动选择只保留本次浏览，离开、刷新、切孩子/家庭或跨日重算；不读取旧todaySections偏好。
- Dashboard 只取得最多 20 条 Todo 和全量精确计数；用户沿用现有“还有 N 项 · 展开”动作时只追加
  一个服务端游标页，不自动下载完整积压。孩子、日期或加载代次变化会废弃迟到响应；续页失败保留
  已加载内容并允许重试，重复游标项不会重复渲染。
- Dashboard 同时只嵌入最近未来日期的 5 个 learning Review，准确显示该日总项数和预计分钟；“还有
  N 项”每次最多追加 20 项。未来卡只有可选的来源记录跳转，没有完成、反馈或带练操作；长知识名称
  完整折行。字段明确为 `null` 才显示“暂无后续安排”，旧服务端缺字段时只陈述今天没有到期内容。
- 设置页不展示或编辑每日复习预算；当前服务端默认值继续用于 required/optional 分组。
- 设置页每日任务提供阅读、跳绳、练字、户外运动快捷候选，以及自定义、编辑、删除。
  名称1～30字符、时长1～180整数分钟、每孩子最多20项；候选不自动保存，失败保留输入，pending禁止重复提交。
  今日提供完成/撤销及完成数，viewer只读；请求失败保留事实。设计源与审批manifest见对应DREV目录，
  三视口基础原生证据见 `docs/quality/evidence/daily-tasks-20261012/`；完整状态矩阵和真机键盘待补，未部署。
- 设置页有在用孩子时不在主内容重复展示学习档案列表；右上角孩子胶囊始终可打开统一档案面板，
  档案行以姓名/年级两级信息为主，“当前使用”为次级文字；可写成员通过透明 88rpx 铅笔点击区编辑，
  新增是列表末尾动作行，归档恢复与上限说明保持独立。viewer 只显示切换；无在用孩子时继续由页面
  空态提供首次建档和归档恢复入口。
- 设置主页固定展示数学、语文、英语及真实已添加项；其他科目和课外活动从候选目录或自定义名称显式添加。打开或取消添加/提醒弹层不写数据。
- 三栏成功空结果显示居中空文案；课外活动单栏为空时只显示“今天没有活动安排”，不再重复显示
  下方“添加日程”按钮。普通主卡和首次引导态各自保留一个互斥日程入口；添加日程意图只消费一次。
- ActivitySchedule 是设置、今日和日程的统一来源；固定安排必须有开始/结束时间。
- 今日还消费不与固定日程重复的柔性活动建议；活动提醒可直接移除。
- 当前 Todo 不再请求通用“带练提示”，也不显示“出现原因”。每个知识点可显示最多两行的已确认
  evidence 摘要；存在 `source_submission_id` 时显示“查看原始内容”，在 Today 当前页底部弹层读取
  对应提交和图片index的唯一照片，不跳历史页、不生成新的 review 文案。纯文字来源保留原文；
  混合照片来源不展示整批文字。照片标注“照片 N · 对应照片”，不把筛选后的下标当原编号。
- Today 原始材料弹层启用 `submission-materials.exactSource`，只鉴权/下载匹配照片；未知、非法或
  无匹配索引显示“未关联具体照片”。同提交切换index会重新加载，离页清除临时引用并丢弃迟到回调。
  410/权限/网络失败有错误与重试状态。历史详情保留默认的整批、最多两张缩略图并发模式。
- 更多菜单在“今天先跳过”下新增“删除记录”，只对可写成员和带knowledge_id的当前知识显示。
  确认弹层说明删除知识关联、复习与反馈，保留原图、原总结和同批其他知识；取消零请求、提交防重，
  失败保留卡片与错误，成功刷新计数；切孩子或离页不接收旧删除回调。无乐观删除。
- Todo“完成”胶囊视觉高64rpx，包装层有效热区至少88rpx；pending、disabled、更多反馈和失败回滚
  行为不变。
- Todo 的主观反馈在卡片内展开，选项旁写明对复习安排的影响；文案与服务端确定性策略一一对应
  （reinforce = 退一步、明天再出现；partial = 下一轮间隔取一半；defer = 同一步、明天再出现）。
- 日程卡点击编辑；重复日程 MVP 修改整个系列。结束时间早于当前时刻后统一灰显。
- 设置页是出行安排的唯一写入口；日程点击出行会回到设置并定位该项。出行不进入今日。
  日程中任意明确时段相交时，冲突双方以危险色、文字原因、冲突对象和重叠分钟数共同提示；端点相接不冲突。
- 报表范围切换会重新请求 7/30/100 天数据并回到第1屏；100天在组件内部按30/30/30/10左右分页，页面根容器不横向移动。
- 报表活动科目行直接消费 `report.activity_subjects`，不再额外下载原始活动记录和完整科目目录后在
  客户端重算。字段缺失的旧服务端显示“明细暂不可用”，不拿截断样本伪造完整统计。
- 报表四个概览指标是 2×2 独立描边的只读卡片，不带按钮角色、箭头、按压态或点击路径。数字右侧
  固定显示 7 点趋势：7 天逐日，30/100 天按 7 个连续近等宽时间桶求和；完整零序列显示水平线，
  缺失或无效字段显示“暂无趋势”。科目列表行仍是带当前区间筛选的明确下钻入口。
- 紧迫度同时显示数字/勾与颜色，活跃度同时保留次数语义，颜色不是唯一信息。
- 孩子切换器和折叠箭头都使用 CSS 矢量 chevron，不使用字体字形 `⌄`。
- Todo 仍兼容服务端来源提交、日期、轮次和间隔字段，但不再渲染“为什么出现”。Planning 从首次确认
  evidence 安全投影可空 `source_summary/source_image_index`；坏 JSON、空摘要或无来源时只隐藏对应
  摘要/入口，Todo 本体与反馈操作保持可用。
- 知识点的置信度一律表述为"AI 识别把握程度"，并附"仅供核对、不代表模型判定掌握"的说明。
- 原始材料按服务端 `sort_order` 升序渲染，照片编号稳定，重复进入顺序不变。
- 设置页区分内置三科与家长自定义科目；只有自定义项可以移出。
- 今日页与记录页都会用最新的待处理数更新"记录" Tab 徽标，两者不会互相覆盖出不一致的数字。
- 需要远程数据的页面统一开启原生下拉刷新；弱网失败时保留已加载内容并显示页内可重试错误条，不清空为空态。
- 报表区间和历史筛选条件按 childId 持久化在本地偏好中，不进入请求 URL；今日四分区和报表「历史记录」「编辑计划」展开态不持久化，今日按实时事实重算默认值，报表两区每次进入和切孩子均收起。
- 界面文案只写**后果**与**边界**，不写操作说明。控件自身表达可用性：可点的行有 chevron 或按钮角色，
  可多选的星期格有选中态，分页由 swiper 圆点表达。因此不再出现「点击切换」「可多选」
  「左右滑动查看」「可下钻」「点击可查看原图」「打开可以修改资料或归档」这类提示。
  必须保留的说明是：确认才入档、照片仅供核对不用于展示分享、出行只显示在日程不生成待办、
  编辑重复日程会作用于整个每周系列。
- 出行安排的边界只在设置页出行卡片副标题声明一次（「只显示在日程，不生成待办」），
  新增/编辑半屏不再重复同一句话。
- 报表紧迫度图用色块图例（「数字：当天待复习」「已全部通过」）替代原来的三行阅读说明，
  颜色仍不是唯一信息载体。

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
- 五个一级页面由 `primary-nav` 在导航中央显示 `.ico-sprout-pri + 知芽`，状态栏、胶囊与尺寸变化均由
  同一组件测量并提供保守回退；内容区旧 `brand-head/.under-brand` 已删除。品牌继续复用生成图标体系，
  不引入位图 logo、emoji 或文字符号；深页仍由原生导航负责返回语义。

实现分三层且方向单一：

| 层 | 文件 | 职责 |
|---|---|---|
| token | `apps/miniprogram/styles/tokens.wxss` | 语义色、科目色、圆角、间距、高度、动效、触控尺寸的唯一来源；含旧变量名兼容别名 |
| 原子/组件 | `apps/miniprogram/styles/atoms.wxss` | Card / Hero / Section / Button / Pill / SubMark / Confidence / Notice / Segmented / Chips / 表单 / RowList / Timeline / WeekStrip / FAB / Metrics / PhotoUploader / 浮层四件套 / 空态 / 骨架 |
| 图标 | `apps/miniprogram/styles/icons.wxss` | 43 个线性图标 × 6 个语义色变体（24×24 viewBox，stroke 1.8），由 `tools/gen_icon_styles.py` 生成，禁止手工编辑；TabBar 位图由 `tools/gen_tabbar_icons.py` 用同一图标语法生成 |
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
| pages | `apps/miniprogram/pages` | 15 pages validated；五个一级页 custom brand nav，深页 native nav |
| display helpers | `apps/miniprogram/utils/ui.js` | 纯函数，无网络与业务状态 |
| icons | `tools/gen_icon_styles.py` | 重跑产物 diff 为空（幂等） |
| API/config | `utils/api.js`, `utils/cloud-media.js`, `config.js` | cloud env/service + callContainer + server-issued upload path；local fallback retained |
| JS behavior | `tests/frontend` | 184 passed；新增语音权限、长按/上滑/松开、取消、迟到回调、错误脱敏、跨孩子隔离、4000 字边界及既有回归；拒绝无效的 `app.json permission["scope.record"]` 声明 |
| bounded remote reads | `tests/frontend/bounded-read-pagination.test.js` | Todo 与 upcoming first/next/stale/dedup/error state、Report no-raw-waterfall contract passed |
| static package | `tools/validate_miniprogram.py` | `MINIPROGRAM_VALID pages=15 source_bytes=685412`; no WXML method calls |
| lint | ESLint | passed |
| WeChat DevTools | registered AppID preview + local authorization | 语音修订 preview 634.8 KB / 650045 bytes 通过、未上传；记录页与框内麦克风已渲染；授权返回 `errno 112 / api scope is not declared in the privacy agreement`，等待管理员补充隐私声明 |
| changed-sheet approximate viewports | `dist/ui-preview/settings-sheet*-vp*.html` | sheet/viewer/limit 的 320/390/430 共 9 个 HTML fixture 已生成；PNG 因缺少 Playwright Chromium executable 未运行，不替代原生几何 |
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

- 2026-10-06 — `SPEC-20261006-SOURCE-DELETE-02 / DREV-20261006-SOURCE-DELETE-01`：Today单图来源与删除
  确认已实现；195项frontend tests与656208-byte微信preview通过。原生隔离副本遇插件41002，
  三视口和真机未验收；详细证据见 `docs/quality/evidence/SOURCE-DELETE-20261006.md`。

- 2026-10-01 — `SPEC-20261001-VOICE-INPUT-03 / DREV-20261001-RECORD-VOICE-INLINE-03`：记录页学习
  内容框缩至 184rpx，并把 44px 麦克风热区直接嵌入右下角；WechatSI 单次 60 秒普通话识别结果只追加
  到既有可编辑 `text` 草稿。首次授权不自动续录，上滑取消、离页/切孩子和迟到回调均不污染表单；
  超过 4000 字时保留原文并允许精简待加入文字。音频、临时路径与插件 payload 不上传、不持久化、
  不记录。专项 13 passed、全量前端 184 passed、后端 389 passed / 5 skipped，静态包 685412 bytes；
  真实 AppID preview 650045 bytes 通过、未上传。开发者工具麦克风授权因隐私协议未声明该 scope 返回
  `errno 112`，三视口与 iOS/Android 仍为 NOT_RUN。

- 2026-09-19 — `BUG-SPEC-20260919-REVIEW-ONLY-CONFIRM-01`：确认页与待确认记录详情共用的
  `confirmPayload` 在纯复习草稿 `groups=[]` 时保留原 `proposal.subject_name`，使请求满足既有 API
  非空合同；有知识点的单/多科目分组、页面状态与视觉完全不变。专项 10 passed、前端全量
  170 passed，ESLint、15 页静态校验、架构与设计策略通过；真实 AppID preview PASS，0.1.12
  开发版本已上传（603182 bytes / 589.0 KB），尚未设为体验版、未提审、未正式发布。

- 2026-09-19 — `BUG-SPEC-20260919-REVIEW-SOURCE-01 / DREV-20260919-TODAY-SOURCE-MATERIAL-01`：
  当前 Todo 以知识点级“原题提示 + 查看原始内容”替代“出现原因 + 带练提示”；原地底部弹层复用
  私有材料读取与预览清理，标记 evidence 对应照片。完成按钮视觉降至64rpx并保留88rpx热区。
  六张批准候选覆盖 photo/text × 320/390/430；原生节点几何与 iOS/Android 仍是发布前 NOT_RUN。

- 2026-09-12 — `BUG-SPEC-20260912-REVIEW-VISIBILITY-01 / DREV-20260912-TODAY-NEXT-REVIEW-01`：今日页
  分区更名为“复习安排”。今天为 0 且未来已有 Review 时，直接展开服务端最近日期、精确总数/分钟和
  完整换行知识点；今天有 Todo 时，后续计划收为低强调 disclosure。Dashboard 预览 5 项，续页最多
  20 项并保留去重、迟到响应丢弃和局部重试；未来项只读。所有新增热区源码下限 88rpx，前端 161 passed、
  ESLint/架构/静态检查与独立 R2 复核通过；原生三视口、字体放大、iOS/Android 与部署未运行。

- 2026-09-12 — `BUG-SPEC-20260912-STALE-CONFIRM-01 / DREV-20260912-STALE-CONFIRM-01`：确认页与待确认
  记录详情的共享草稿逻辑删除 `conflict` 状态及手动“刷新/查看最新”提示；非 consent 的 409 自动调用既有
  `load()`，服务端已进入 confirmed/cancelled 时直接切为最新只读详情，否则完整恢复本地编辑并显示原错误。
  focused frontend 28 passed、全量 frontend 155 passed，ESLint、架构与 15 页静态检查通过；未改布局、token
  或组件，原生三视口/字体放大/代表性 iOS 与 Android 为 `NOT_RUN`，未上传或部署。

- 2026-09-11 — `BUG-SPEC-20260911-PERF-01 / FEC-20260911-READ-PERF-01`：Today 延续既有展开控件，
  但只逐次追加有界服务端 Todo 页并拒绝迟到/重复数据；Report 直接消费同范围的服务端活动科目聚合，
  删除 raw activity/subject 请求瀑布。没有新增控件、文案或布局；自动化已覆盖 first/next/stale/error
  和旧服务端降级，云端体验版弱网/阶段信号仍待发布验收。

- 2026-09-11 — `SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH-01 / DREV-20260911-SETTINGS-PROFILE-MANAGER-02`：
  学习档案面板改为姓名/年级两级信息，当前状态收为次级文字；连续米色“编辑”块替换为透明 88rpx
  铅笔点击区，新增入口并入在用档案列表末尾。切换、编辑、归档恢复、viewer、limit、路由和权限合同
  未改。focused frontend 32 passed、全量 frontend 140 passed，ESLint、架构、小程序静态（630368 bytes）、
  图标幂等和 diff check 通过；真实 AppID preview 575988 bytes。三状态三视口 HTML fixture 已生成；PNG
  与修改后原生三视口/iOS/Android 为 `NOT_RUN`。未上传/部署；后端/API/Schema 未改。

- 2026-09-11 — `SPEC-20260911-SETTINGS-PROFILE-MANAGER-01 / DREV-20260911-SETTINGS-PROFILE-MANAGER-01`：
  设置页普通态删除重复的学习档案列表、页面内添加与上限提示；右上角孩子胶囊在单孩子时也可打开，
  面板统一承载切换、独立编辑、归档恢复、添加与达到上限说明。viewer 只保留切换，无孩子首次建档空态
  保留，编辑/恢复/添加导航前关闭面板。focused frontend 32 passed、全量 frontend 140 passed，ESLint、
  架构、小程序静态（629228 bytes）、图标幂等和 diff check 通过；三档 HTML fixture 已生成，真实 AppID
  preview 574991 bytes。PNG 与本修订原生三视口/iOS/Android 为 `NOT_RUN`；未上传/部署，后端/API/Schema 未变。

- 2026-09-11 — `SPEC-20260911-PRIMARY-NAV-BRAND-01 / DREV-20260911-PRIMARY-NAV-BRAND-01`：
  五个一级 Tab 由原生纯文字标题切换为共享 `primary-nav`，导航中央只显示一处生成嫩芽图标 + “知芽”；
  内容区旧 `brand-head` 与 `.under-brand` 已删除，today/calendar/reports 的日期、周范围和统计边界作为
  hero 次级信息保留。组件优先读取窗口/胶囊几何并带 20px + 44px 保守回退，尺寸变化时重新测量；
  详情页继续原生导航。前端 138 passed，ESLint、架构、小程序静态（629240 bytes）与图标幂等通过；
  五页三档近似 PNG 和 0 横向溢出已走查，真实 AppID preview 574832 bytes，开发者工具 iPhone 15 Pro Max
  记录/设置页标题与胶囊无重叠，调试器 0 errors。完整原生三视口、字体放大与代表性 iOS/Android
  真机为 `NOT_RUN`；未上传/部署。

- 2026-09-11 — `SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA-01 / DREV-20260911-TODAY-ACTIVITY-EMPTY-CTA-01`：
  删除今日页课外活动空态下方重复的“添加日程”按钮，保留空态文字、普通主卡与首次引导态的互斥入口；
  `addSchedule`、日程意图、活动列表和折叠状态未改。当前工作树前端 138 passed，ESLint、小程序静态
  （629154 bytes）、架构、图标幂等与 diff check 通过；真实 AppID preview 574832 bytes，未上传。
  三档 HTML fixture 已生成，PNG 因缺少 Playwright 未运行；原生三视口与 iOS/Android 为 `NOT_RUN`。

- 2026-09-11 — `SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02 / DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02`：
  空照片状态和照片网格“+”统一绑定 `addPhotos`，每次用 `wx.chooseMedia` 同时开放 camera/album；
  支持返回后反复拍摄、相册多选和跨轮次 9 张硬上限，取消/空返回/失败与上传中保护保留表单。
  全量前端 135 passed，ESLint、小程序静态（626018 bytes）、架构、图标幂等与 diff check 通过；
  真实 AppID preview 573065 bytes。0/1/8/9 图三视口近似 fixture 已生成，原生来源面板、连续拍摄、
  权限失败及 iOS/Android 真机仍为 `NOT_RUN`；未上传、未部署，后端/API/Schema 未变。

- 2026-09-11 — `SPEC-20260911-RECORD-SIMPLIFICATION-01 / DREV-20260911-RECORD-SIMPLIFICATION-01`：
  删除记录页“新增/历史”和“拍照/文字”两组分段选择，统一为照片与学习内容同屏表单；有照片沿用照片
  批次上传，无照片但有文字沿用 manual submission，空材料不发请求。历史移到表单末尾默认折叠，
  viewer 和显式历史意图自动展开，原有搜索/筛选/分页/详情及文字来源语义保留。前端 133 passed，
  ESLint、静态校验、架构检查和图标生成幂等通过；真实 AppID preview 编译 572,709 bytes，未上传。
  320/390/430 近似截图已走查；开发者工具模拟器 `reLaunch:fail timeout` 后停留旧缓存，故原生矩阵、
  键盘、字体放大和 iOS/Android 真机仍为 `NOT_RUN`，本轮未部署。
  用户后续原生截图暴露固定提交栏以 `bottom: 0` 落入自定义 TabBar 图层，遮住历史入口且被中央记录键反向遮挡；
  已为记录页增加专用 `record-cta`，以 TabBar 高度 + 32rpx 间距 + safe area 抬升，并将页面尾部占位改为
  376rpx + safe area。布局结构回归、全量前端、ESLint、静态和架构检查通过；修复后 preview 为
  572,880 bytes，未上传，修复后的原生点击复验仍为 `NOT_RUN`。

- 2026-09-11 — `BUG-017 / BUG-SPEC-20260911-01 / DREV-20260911-AI-SUMMARY-01`：不修改 WXML、
  WXSS、页面状态机或请求协议，只把后端提供的 AI 动态总结限定为一句、最多 60 字的实际学习事实，
  并恢复既有复习区成功数据路径。当前工作树前端 132 passed，小程序静态与架构校验通过；无新增几何可验，
  修复后云端请求和真机均为 NOT_RUN，本轮未部署。

- 2026-09-07 — `SPEC-20260907-PKDS-04 / DREV-20260907-PKDS-04`：页头与文案密度整改。
  (1) 五个一级页面删除 `navigationBarTitleText` 覆盖，原生标题统一继承「知芽」，消除与底部 Tab 的
  逐字重复；新增共享组件 `components/brand-head`（生成图标 `.ico-sprout-pri` + 衬线「知芽」 +
  可选 kicker），不引入位图 logo。(2) hero 标题改为句子式：今天，也慢慢来 / 这一周，心里有数 /
  一笔一画，都算数 / 一点一滴，看得见 / 按你们的节奏来。(3) 按「操作说明删除、后果与边界保留」
  的判定删除约 20 处提示（点击切换、可多选 ×2、左右滑动查看、可下钻、点击可查看原图、
  打开可以修改资料或归档、按实际参与情况添加、切换后所有页面同步 ×3、打开或取消这个弹层都不会
  写入数据、下拉刷新说明、草稿说明 ×3 等）；出行边界由三处收敛为出行卡片副标题一处，
  每周系列提示改为仅在「编辑 + 重复」时出现。(4) 报表紧迫度图的三行阅读说明改为色块图例，
  保持颜色不是唯一信息载体。(5) 删除随文案作废的 `.read-hint`、`.travel-only-note`、
  `.card-head .c-r`、`.sheet-foot .foot-note`、`.sheet-tip` 与 `catalogSub` 视图字段。
  自动化证据：前端 127 passed（新增 `tests/frontend/brand-header-and-copy.test.js`）、ESLint 通过、
  `validate_miniprogram.py pages=15 source_bytes=625897`、图标生成器幂等（`icons.wxss` 无 diff）、
  `ARCHITECTURE_VALID checked=3`、`tools/preview` 五页 × 320/390/430 截图走查与横向溢出扫描
  （`OVERFLOW_FAILURES 0`）。真机/开发者工具原生几何仍为 `NOT_RUN`，未部署。

- 2026-09-06 — `BUG-015 / BUG-SPEC-20260906-21 / DREV-20260906-REPORT-01`：报表概览卡改为只读，
  使用原生 WXML/WXSS 线段和点绘制四组固定 7 点微趋势，不引入 canvas 或图表依赖。前端校验 7 桶、
  连续日期、非负整数和概览总量守恒，缺失/异常与真实全零采用不同表现。前端 109 项与 ESLint、
  小程序静态校验通过；320/390/430 近似 HTML 已生成且 390 视觉走查未见数字/折线重叠。
  微信开发者工具 CLI 本地编译预览成功，包体 545.7 KB（558772 bytes），未上传；Playwright 截图因
  本机缺 Chromium 未运行。报表页原生三视口、字体放大及 iOS/Android 真机仍为 `NOT_RUN`，不能把
  本次近似预览当作发布验收，本轮未部署。

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
