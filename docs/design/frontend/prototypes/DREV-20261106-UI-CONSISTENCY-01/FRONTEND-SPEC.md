# 全界面 UI 优化 · Design Revision 01

- Design: `DREV-20261106-UI-CONSISTENCY-01`
- Spec: [DESIGN-002-SPEC-01](../../../../../specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)
- Status: **PENDING_REVIEW**，生产实施 NOT_STARTED
- Updated: 2026-11-06
- Source: [index.html](index.html)，自包含，无 CDN、字体或业务请求
- Viewports: 320×568 / 390×844 / 430×932，DPR=1
- Export evidence: [manifest.json](../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-01/manifest.json)

## 视觉方向与通用控件

保留「纸 · 芽」的暖白纸面和松绿，采用衬线页面标题、系统中文正文、细分隔线与统一线性图标。
削弱装饰和持续凸起的中心导航，让用户先看到内容和当前选中位置。

| 元素 | 本稿取值 / 提议 |
|---|---|
| 色彩 | canvas #FAF7F0；surface #FFFDF8；primary #1F5B45；ink #22261F；关键说明 #464E43 |
| 字阶 | 页面标题 26px（320 下 24px）；区块 18px；正文 16px；说明、标签、Tab 14px |
| 间距 | 4px 基础；页面边距 18px（320 下 16px）；卡片内距 16px（320 下 14px） |
| 形状 | 卡片 16px；输入和添加操作 12px；标签 8px；主按钮和选中导航使用胶囊 |
| 图标 | 24×24，stroke 1.8，圆端；同类控件统一 |
| 添加入口 | 透明底 + 松绿字 + 细虚线，48px 高，所有业务分组一致 |
| 操作层级 | 主操作实心；次操作浅绿或描边；危险操作只在最终确认突出 |
| 触控 | 产品按钮、输入、文本域至少 44 CSS px，不按 88rpx 冒充窄屏 44px |
| 导航 | 仍是今日 / 日程 / 记录 / 报表 / 设置；统一当前 Tab 浅绿选中底，取消中心常驻凸起 |
| 响应 | 长页在内容区滚动，底部操作/Tab 不覆盖末尾可达内容；窄屏保留字体与点击面积 |

本稿采用 CSS px 表达逻辑设计，后续原生转换必须按 FEC 重新核对几何和职责限定的 rpx token，
不能把 HTML 渲染直接视为小程序一致性。无权修改现行 FDB/FEC。

## 17 路由 → 代表性效果图

| 当前路由（pages/） | 本稿 scene / 核心变化 |
|---|---|
| family-onboarding/index | family-onboarding、family-create、family-join、join-pending；创建与加入、无审批 ETA |
| today/index | today、empty、loading；任务前置、分区事实独立 |
| calendar/index | calendar；周历、回到今天、当天任务与定时日程分开 |
| records/index | records、manual-confirm、processing；显式学习/旅行切换、手动与 AI 路径 |
| footprints/index | travel、travel-review；日期倒序、草稿与正式日记分开 |
| reports/index | reports；范围、单位、事实统计与常用入口 |
| review-inventory/index | review-inventory；主状态与科目/日期筛选分层 |
| settings/index | settings、settings-routines、daily-form、activity-schedule、travel-plan、child-switch、error、permission、saved |
| submission/confirm | confirm、confirm-error；渐进展开、保留原材料、就地定位缺失字段 |
| record-detail/index | record-detail；已确认事实、发生/提交时间、原材料、复习情况；去今日反馈 |
| activity/edit | activity；实际日期、常用时长与数字输入 |
| child-edit/index | child、grade；固定保存、归档分区、单 picker 年级确认 |
| family-join/index | family-preview、join-pending；最小家庭预览、关系、六位申请核验码 |
| family-members/index | family-members；邀请码有效期、权限紧邻成员；不提供多家庭切换 |
| family-requests/index | family-requests；核验码、权限和处理后果一起展示 |
| delete-settings/index | delete-settings、delete-confirm；归档与永久清理，完整昵称确认 |
| notifications/index | notifications、notifications-unavailable、channel-unavailable；授权、渠道可用性与偏好分别表达 |

共 **39** 个代表性界面/状态；`unsaved` 为跨表单未保存退出的独立样张。
每个 scene 均导出三个指定视口，共 117 张单屏 PNG；另有 13 张 390 视口评审拼图，逐一覆盖这 39 个场景。
长页需滚动，单屏 PNG 只展示所选视口；设置下半屏另有 settings-routines。

## 关键交互提议与原型可用范围

| 场景 | 目标表现 | 本地原型能力 |
|---|---|---|
| 分区/高级设置 | 折叠与展开有状态 | 可点击，aria-expanded 同步 |
| 主导航/页面 | 页面位置与返回路径明确 | 可点击；画廊同步定位 |
| 时长 | 常用值与输入联动 | 可点击并更新数字输入 |
| 有修改时退出 | 继续编辑 / 放弃修改 | 本地表单可实际触发；继续时保留当前输入，离开后不持久化 |
| 草稿错误 | 滚动到错误项，错误贴近字段 | confirm-error 自动定位第 2 项；具体 picker 仅布局演示 |
| 永久清理 | 输入完整对象名称才允许继续 | 昵称匹配切换 disabled；点击不做清理 |
| 图片、日期、科目、成员 | 原生系统/业务选择器 | 固定示例与布局提示，不调用真实能力 |
| 微信提醒 | 授权状态和服务状态如实表达 | 固定样例，不申请授权、不保存偏好 |
| 保存与审批 | pending、结果、错误需要绑定真实结果 | 当前仅演示，不提交任何接口；不证明事务/幂等/竞态 |

### 报表语义

保留当前行为统计、每日方格和复习待办概览的阅读语言，不引入新的图表库或装饰图形。
近 7 天为 10月31日–11月6日；每日复习反馈示例 2/4/0/3/5/1/3，总计 18 条。
复习待办按该范围的**学习日期**分组，标题不再暗示未来时间预测。数值是合成样例。
可选范围只演示选中态，固定数据不会随点击重算；图表无无意义的单日点击状态。
当前方格与列表不表达掌握率、正确率或 AI 评分。
遵循 build-product-frontend/chart-system 与 Lieflat 的事实、单位、范围和受控配色原则；
因已有品牌图形语言，未套用独立报告模板，也不增加图表运行时依赖。

## 证据与仍需验证

运行 `python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-01/export.py`。
导出脚本记录每屏的溢出、控件高度、JS 错误和代表性交互结果，见
[verification.json](../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-01/verification.json)。
本稿的 SHA 清单是候选版本清单，尚未批准冻结。修改本稿必须重新导出并重算全部 SHA。

本轮未运行生产测试、微信开发者工具、原生节点、真机、读屏、系统大字或真实授权；
这些均不得以 HTML 结果替代。39 个设计样例并非完整生产验收状态矩阵。
获得用户对具体 Spec+DREV 的批准后，才制定生产变更清单和原生验证范围。
