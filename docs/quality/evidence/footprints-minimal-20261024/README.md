# 足迹界面减法 — 本地实施证据

- Date: 2026-10-24
- Status: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED
- Approval: 用户针对call_3e246df48da4467983d023b06a443aeb回复“批准 Spec01 + DREV01，按此实施并合并 UI 规范”；实施前已将批准写入Spec与清单。
- Spec: [SPEC-20261024-FOOTPRINTS-MINIMAL-UI-01](../../../../specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md)，active/VERIFYING。
- Design: [DREV-20261024-FOOTPRINTS-MINIMAL-01](../../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)；源和24张批准设计导出冻结。
- Release: [本地阶段](../../../deploy/releases/20261024-footprints-minimal-local.md)。

生产改动仅footprints控制器、模板、样式；测试更新真实操作路径。内嵌组件/独立Page仍共用源码，records只承载。去掉重复孩子标题、两行常驻次要操作和设置长文；统计右侧44px既有线性更多按钮，按权限/归档显示原生操作，单项直接执行、无项隐藏。归档选择每页4个孩子及必要翻页，单页最多6项，保留全部历史可达；取消和放弃保护不改孩子/输入。设置正文内容收高，失败保留开关与重试。原AI同意、家长确认、固定7天草稿及条件24小时原件清理均不变。

工程“界面默认不需要解释”条款已合并到FRONTEND-DESIGN“界面文案与减法”和FEC“Information architecture and action hierarchy”。当前授权/真实错误/直接后果在发生操作处简短呈现；不增加帮助层，不扩展清理其他页面。旧设置长文作为历史方案标明被覆盖。

## 当前检查

| 检查 | 实际结果与范围 |
|---|---|
| `npm test` | PASS，最终331/331，0 fail/skip（共享工作区含并行任务新增）；足迹文件26项，其中10项本轮新增，另更新原records归档路径回归。此前首次全量326/327，旧归档断言随真实路径更新后327/327通过；本次最终复跑331/331 |
| `npm run lint:miniapp` | PASS |
| `python3 tools/validate_miniprogram.py` | PASS，17页，最终共享源1221025 bytes，低于1.5MiB；共享工作区含其他本地任务，不等于上传包体 |
| `.venv/bin/python tools/check_architecture.py` | PASS，4 policies / 150 modules，runtime/lazy DAG |
| `validate_design_evidence.py --check-current-policy`及本次指定APPROVAL清单 | PASS，批准源/24导出SHA匹配；旧批准源不变 |
| 新原生准备工具 Ruff check / format | PASS |
| 原生320×568 / 390×844 / 430×932 | 最终控制器版本各9态PASS，共27份节点/PNG；截图2倍像素、实际视口、节点和SHA已核对，独立于旧51组，见[native-audit.json](native-audit.json) |
| 430系统菜单实际操作 | PASS，实际点击更多/取消、设置打开/关闭、归档打开/取消/选择；顶部身份更新，归档无导入，菜单锁释放。见[操作记录](native-actions.json)及6份合成状态/截图；未把未保存表单保护、真实设置写入或系统读屏写成原生通过 |
| 后端pytest/MySQL/迁移/真实媒体AI | NOT_RUN / N/A，本轮不改后端、API、Schema或provider；既有未验收项不追认通过 |
| iOS/Android字体/读屏/真实照片、独立复核、家长验收 | NOT_RUN；不以合成开发者工具代替 |

新增行为回归覆盖：可写/viewer与有/无归档动作矩阵、单项直达/空菜单、重复打开、原生取消/迟到选择、未保存输入保护、归档翻页前后及尾页可达、加载派生/403清理、设置失败原值重试。

原生工具[prepare_footprints_minimal_native.py](../../../../tools/prepare_footprints_minimal_native.py)准备独立副本`/private/tmp/push-kids-footprints-minimal-native-20261024`；[footprints_minimal_geometry.js](../../../../tools/footprints_minimal_geometry.js)通过官方本地自动化端口9572采集。副本移除插件、禁用云、使用合成家庭/孩子/照片、只读transport拒绝业务写；只在副本加fixture/滚动绑定，不改生产transport。复用既有fixture时会替换副本load/预览以固定几何，不能据此证明真实服务/地图/选图。

9态为overview、empty、settings、settings-error、archived、viewer、viewer-archive、long、no-child。断言涵盖44px更多/操作目标、14px文字、统计与图标间距≥8px、无横向越界、无旧标题/归档入口、权限/归档可达、紧凑设置正文≤120px/总高≤280px（含安全区）及错误重试面板、设置时导航隐藏。

第一次320采集曾`App.captureScreenshot timeout`；第二次严格核对320×568后采集全部通过，未伪造或用390图改名。开发者工具显示getSystemInfoSync弃用和并行年级组件的合成API/选择器警告，未把布局通过写成完整包无警告或真实地图验收。

最终三尺寸重采均使用包含刷新期续看保护的同一控制器；9份耦合生产源与副本摘要一致。系统菜单通过CUA实际点击及原生AX确认，不替换wx成功/取消回调；官方`App.captureScreenshot`不包含微信系统操作菜单层，actions-open/archive-open的PNG只记录底层页面，不能作为菜单视觉证据。实际设置面板、取消后状态及归档结果有PNG与状态记录。最初setup辅助命令在reLaunch尚未完成时读取组件返回null；随后通过实际顶部类型下拉进入旅行，真实handler取证成功，已删除这个不稳定的setup捷径。

## CR-001 修复

此前只读复核以无写入反例证明：满100条下一组请求在途时打开照片，返回会全局清理新面板预览。按BUG-032已批准TP04/TP10修复，未添加新缓存抽象：返回时若已进入面板或其他视图，则不应用分页、不推进游标、不回收预览；关闭面板后可重试。新load重置过期loadingMore，刷新完成前不续看，失效请求不污染新页面错误。

真实openVisit及fillPreviews回归分别覆盖已加载文件和在途下载，两者均保留photoList.previewUrl且无删除；原100条窗口/游标保持、busy清除。旧313项/51组只证明历史范围，新源摘要与最终331项结果单独保存；修复不冒充独立复审。

## 文档与生命周期

已逐项核对并同步FEAT-001/012、BHV-040/041、Architecture、UI-001/018、设计/FEC、Spec与索引、旧文案Spec/设计规格、当前及历史证据和本地发布记录。旧“细则集中设置”、当前候选/未实施、CR-001未修复等正文已按实际新状态替换或标明历史。旧批准清单只添加Superseded by，不修改源/截图。

当前代码与文档范围一致，无后端/权限/确认合同扩展。[自动化实际输出](automated-checks.json)与[17份源/测试/工具摘要](source-manifest.json)单独保存；不是共享工作区全部dirty文件的验收声明。[收尾核对](closure-audit.json)验证文档路径、两份冻结HTML、当前17源、27份原生节点/PNG及6份实际操作状态。全量发布门禁不属于本次开发请求；没有提交、推送、上传、部署或业务写入。完成全部必需原生/设备/复核及产品验收后才DONE并移completed，目前Spec保持active/VERIFYING。
