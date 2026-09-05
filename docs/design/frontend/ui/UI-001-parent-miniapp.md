# UI-001 — 家长端微信小程序

- Status: `CURRENT`
- Related Feature: `FEAT-001`
- Baseline: `FDB-20260830-01`
- Engineering contract: `FEC-20260905-02`
- Design revision: `DREV-20260830-03`
- Current-state revision: `UI-STATE-20260905-HISTORY-01-LOCAL`（包含 BUG-010 V3 amendment 01）
- Incremental design: `DREV-20260905-AI-01`（包含人工兜底；原视觉基线沿用）
- Layout design: `DREV-20260905-UX-03`（已批准；390 CUA 通过，完整矩阵 pending）
- Last verified: 2026-09-05（390×844 DevTools原生运行态；其他视口与真实设备 pending）
- Intermediate artifact: `docs/design/frontend/prototypes/DREV-20260830-03/index.html`
- Figma waiver anchor: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Current information architecture

原生微信小程序面向家长，采用五个一级 Tab。所有页头只保留当前上下文与统一的紧凑孩子
切换器，不重复显示 Tab 已表达的大标题。

| Tab | Current responsibility |
|---|---|
| 今日 | 可折叠的今日复习、今日学习、今日活动；待确认/失败提示 |
| 日程 | 周日期轨、当天时间线、过去日程灰显、FAB 新建、编辑/删除日程 |
| 记录 | 同页新增/历史；照片/文字与实际时间；已确认/待处理/全部、搜索/筛选/分页及原始材料回看 |
| 报表 | 7/30/100 天概览、组件内30天分页的复习紧迫度与活跃度、科目记录 |
| 设置 | 三项基础学科、手动添加的其他科目与课外活动、活动安排、家庭成员入口 |

学习流程的深层页面复用草稿确认页承载只读学习详情，另有活动练习记录。产品 UI 不编辑服务地址、不展示账号
占位；这些由后台配置或后续微信身份版本负责。

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
- 报表科目、今日学习/待处理进入同一历史入口，日期/科目意图只消费一次；列表返回保留条件与页码。
  详情可查看每个知识的当前计划与每页 3 条反馈，到期时跳回今日；浏览材料不记为完成复习。
- AI 草稿可编辑；“确认”是创建正式记录、知识和复习项的唯一入口。
- 草稿展示知识点的置信度文字、照片编号/家长文字证据及总体不确定项；缺证据的旧草稿/家长
  新增点明确提示核对原始材料。证据仅供核对，不代表模型判定掌握。
- 关联已有知识显示复用/保留进度说明，并可取消关联；改名/类型会解除该点关联，改科目会清空
  全部关联和Todo匹配。科目选择只提供有效learning项，并允许输入新学习科目。
- 人工表单保留完整原文与实际发生时间；原文超过500字时要求另写总结，不静默截断；不显示
  AI置信度或证据，不自动匹配Todo。保存失败保留输入和可见错误，保存中防重复操作。
- 重复材料提示放入“需要核对”；Todo匹配显示证据，已更新的任务不会再次推进。
- 今日从同一个 Dashboard 读取复习、已确认学习和日程。三栏独立折叠，不使用只计算复习的
  “今日总体进度”卡。
- 设置页不展示或编辑每日复习预算；当前服务端默认值继续用于 required/optional 分组。
- 设置主页固定展示数学、语文、英语及真实已添加项；其他科目和课外活动从候选目录或自定义名称显式添加。打开或取消添加/提醒弹层不写数据。
- 三栏成功空结果显示居中空文案；全部为空且没有待处理记录时显示“记录学习/添加日程”引导，添加日程意图只消费一次。
- ActivitySchedule 是设置、今日和日程的统一来源；固定安排必须有开始/结束时间。
- 今日还消费不与固定日程重复的柔性活动建议；活动提醒可直接移除。
- Todo 的“带练提示”只提交当前所选且已确认的 Review IDs。
- 日程卡点击编辑；重复日程 MVP 修改整个系列。结束时间早于当前时刻后统一灰显。
- 报表范围切换会重新请求 7/30/100 天数据并回到第1屏；100天在组件内部按30/30/30/10左右分页，页面根容器不横向移动。
- 紧迫度同时显示数字/勾与颜色，活跃度同时保留次数语义，颜色不是唯一信息。
- 孩子切换器和折叠箭头都使用 CSS 矢量 chevron，不使用字体字形 `⌄`。

## Visual system

方向是暖纸色背景、墨绿色主色、克制分隔线和低阴影。信息依靠排版和留白建立层级，不采用
儿童游戏化、排行榜、玻璃拟态或企业 BI 密集卡片。底部半屏层使用统一 handle、标题、关闭和
主操作；日程新增使用右下角浮动加号。

## Responsive and accessibility

目标竖屏视口为 320×568、390×844、430×932。触控目标不小于 44px；长内容垂直滚动；
普通业务页面不使用横向滚动；七天、报表范围、基础科目和活动星期均在当前视口完整显示。关键状态有文字语义，表单保留输入，错误不只
依靠 Toast。图片不进入本地存储或日志。云环境 JSON 统一走 `wx.cloud.callContainer`，图片按
服务端 ticket 使用 `wx.cloud.uploadFile` 后 claim；页面不持久化 fileID 或 OpenID。

## Implementation and current evidence

| Contract | Path/evidence | Result |
|---|---|---|
| shell/tokens | `apps/miniprogram/app.*` | five exact tabs |
| pages | `apps/miniprogram/pages` | 11 pages validated |
| API/config | `utils/api.js`, `utils/cloud-media.js`, `config.js` | cloud env/service + callContainer + server-issued upload path；local fallback retained |
| JS behavior | `tests/frontend` | 48 passed |
| static package | `tools/validate_miniprogram.py` | valid; no WXML method calls |
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

- 2026-09-05 — BUG-010 截图回归：目录按钮、星期居中、日历七天/FAB、报表单页提示及滚动范围条已本地修复。390视觉与320部分复查；[证据与未完成项](BUG-010-20260905-layout-followup.md)。UX-04二级交互仍为草稿，未替换原生视觉。

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
