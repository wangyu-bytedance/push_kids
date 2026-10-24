# 记录入口调整 — 本地实施证据

- Date: 2026-10-24
- Status: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED
- Task: [BUG-032 Spec05](../../../../specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md)，用户「可以」已批准，不再等待实施授权。
- Design: [DREV-20261024-RECORD-ENTRY-01](../../../design/frontend/prototypes/DREV-20261024-RECORD-ENTRY-01/FRONTEND-SPEC.md)，批准HTML与30张导出SHA冻结。
- Release: [本地交付状态](../../../deploy/releases/20261024-record-entry-local.md)。

实现范围为记录页顶部类型菜单、既有纸色孩子chip、明确学习入口跨代续接、旅行默认全部时间和有界续看、内容下方唯一48px导入按钮。原学习表单/幂等键/滚动、旅行归档与权限、上传同意/手动记录/家长确认合同保持；没有API、SQL、迁移、后端部署或客户端上传。

## 自动化与原生验证

| 检查 | 本轮实际结果 |
|---|---|
| `npm test` | 最终PASS，313/313（前一轮306/306；并行任务新增7项后重跑）；含真实Today/Reports handler→共享意图→records.onShow/load/消费、旧代离开保护反例修复及普通取消不重试 |
| `npm run lint:miniapp` | PASS |
| `python3 tools/validate_miniprogram.py` | PASS，17页；最终源大小以收尾audit为准，低于1.5MiB预算 |
| `python3 tools/check_architecture.py` | PASS，4 policies / 150 modules，runtime/lazy DAG |
| `python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261024-RECORD-ENTRY-01/APPROVAL.md --check-current-policy` | PASS，APPROVED源/导出SHA匹配 |
| `ruff check` / `ruff format --check tools/prepare_record_entry_native.py` | PASS，仅本轮新增Python工具 |
| 当前原生320×568 / 390×844 / 430×932 | 各17态、共51组节点/PNG全部PASS；菜单裁切修正后三尺寸全部重采，实际尺寸/overflow/截图SHA和2倍像素校验见[native-audit](native-audit.json)；含继续分页真实handler的100→20替换和滚动归位 |
| 当前diff完整客户端导航 | PASS，[完整AppID/插件项目回归](postimplementation-navigation.json)：官方自动化调用现有handler，普通Tab保留travel，旅行→今日recordLearning→记录最终learning、load结束、无error、intent已消费；无源注入/transport替换/正式事实写入。不是OS点击或真机证据 |
| 原生系统picker | 已实际打开并显示两个合成孩子；取消前锁屏。用户解锁后CUA在多个开发者工具窗口间失去可靠绑定，取消/选择未完成，不记通过；不再以重复解锁请求代替证据 |
| 后端全套、MySQL、AI/EXIF、真实地图供应商 | N/A，本次不改；既有未验收项不追认通过 |
| iOS/Android字体、读屏、真实选图、独立review | NOT_RUN，Spec保持VERIFYING |

原生工具：[prepare_record_entry_native.py](../../../../tools/prepare_record_entry_native.py)准备独立副本，[record_entry_geometry.js](../../../../tools/record_entry_geometry.js)通过微信开发者工具官方自动化接口采集。副本使用合成家庭/孩子、只读transport，拒绝业务写入；只在副本增加fixture，生产transport不替换。基础库3.17.4；iPhone5/12/14ProMax的逻辑尺寸严格核对，截图2倍像素与设备DPR分别记录，不混作HTML导出。

17态为learning、learning-menu、single、long、long-menu、travel、travel-menu、empty-bottom、timeline-bottom、playback-bottom、lit-bottom、viewer、archived、no-child、photo-sheet、timeline-window、place-window。[原生JSON/PNG](native/)保存节点矩形、字体、overflow、菜单/导航状态、窗口行数、截图SHA。断言包括44px目标/14px标签、长名整块右对齐、菜单200px/下8px/选项48px、不被头部裁切、无日期筛选、唯一48px普通导入按钮/20px图标、内容间隔20px、滚到底避开中央导航≥8px、权限和照片面板隐藏导航。

看图发现的真实缺陷已修复：全局`.page`的overflow-x:hidden导致头部菜单第二项裁切；记录页头部显式overflow:visible，并增加原生computed overflow断言。第一轮错误标记为320但实际390的中间文件已由真实320重采覆盖。没有用隐藏越界或HTML截图代替原生验收。

原生地图曾有腾讯瓦片`net::ERR_FAILED`，开发者工具也输出getSystemInfoSync弃用等平台警告；不将合成布局通过写成地图服务、全球底图或真实照片通过。既有学习空态插画及其他非本轮界面没有宣称与本次简化设计逐像素一致。

## Spec测试点对应

| Test point | 状态与边界 |
|---|---|
| TP01 孩子chip | 自动化归档标签/头像和原生单/多/长名几何通过；系统picker已实际打开，选择/取消受桌面窗口绑定限制未完成 |
| TP02 真实学习入口与竞态 | PASS，当前真实Today/Reports handler、共享intent、真实records load；实施前跨代FAIL→实施后PASS，无学习/足迹写入 |
| TP03 普通Tab与输入保留 | 前端回归PASS；当前完整原生项目现有handler往返保留travel通过；无未提交输入的完整客户端探针不替代前端表单保留测试 |
| TP04 保护、迟到、失败与权限 | 前端回归PASS，含上传/编辑取消/隐藏、只读/归档/无孩子；真实相册/跨设备PARTIAL |
| TP05 自动化与结构 | PASS（命令见上表）；后端测试N/A |
| TP06 批准设计SHA | PASS，冻结源和30导出未改 |
| TP07 三视口原生及picker | 51组当前节点/PNG通过；PARTIAL仅系统picker选择/取消待补，不复用10-23历史87份 |
| TP08 完整客户端与真机 | 完整客户端现有handler导航PASS，无源注入；OS实际点击、设备字体/读屏未全部执行，整体PARTIAL |
| TP09 review与文档闭合 | 当前正文按diff核对并同步；独立只读review NOT_RUN |
| TP10 全范围和有界续看 | 前端回归PASS：三视图/地点参数无日期泄漏、跨年/100条窗口、容量上限、游标失败原地重试、迟到预览删除；原生100→20时间线/地点滚动归位通过 |
| TP11 顶部菜单 | 前端toggle/滚动/离开保护和原生几何通过；真实外部点击命中/地图层叠/键盘读屏PARTIAL |
| TP12 下方普通导入按钮 | 前端权限/保存重入/首次同意/取消选图回归和原生各视图按钮几何通过；真实选图/读屏未验收 |

## 基线、历史和闭合

[实施基线](implementation-baseline.json)冻结实施前9份目标源/测试SHA与HEAD。[最终源摘要](implementation-final.json)记录9份耦合生产源（含本任务未改动的records/index.js）及两个测试文件；离线副本9源匹配。保留共享工作区其他任务变更，不把HEAD全部dirty当本轮改动。新imports保护在既有beginImport内增加saving/uploading检查，无新业务协议。

[原生导航诊断](preimplementation-navigation.json)为实施前完整本地项目：第一次前置条件不满足NOT_RUN，第二次干净旅行→今日学习主路径PASS。[确定性状态反例](preimplementation-race.json)为实施前预期FAIL：真实Today handler设置意图，旧切换等待期间隐藏/返回，最终仍travel、intent pending。API与时序为合成桩，真实load未替换，不等于真机复现全部报告条件。[最初8份基线](source-baseline.json)只保留历史；后续并行Today变化不恢复。

Spec01–04历史候选分别验证21/21/27/27张HTML；04的160px卡片已被用户撤回。Spec05批准源30张HTML和DOM点击/键盘/滚动检查为设计证据，不能替代原生或设备通过。冻结manifest保留其生成时说明，不重写为实施验收。

文档已同步FEAT-001/012、BHV-040/041、Architecture、UI-001/018、Frontend Design索引、当前设计规格、Spec及索引、发布记录。BHV-038授权/权限/确认行为未变；测试策略、部署手册和全局样式无本轮政策修订。旧类型抽屉隐藏Tab、日期筛选、小导入按钮的当前描述已替换；旧原生/发布事实保留日期边界，不冒充当前验证。批准源/快照不变，旧清单仅允许追加Superseded by。

[收尾核对](closure-audit.json)记录当时313项测试、51态SHA/尺寸及完整客户端导航。后续只读复核新增CR-001（P1 BLOCK）：满100条“下一组”在途时打开照片，返回会清理其预览，无写入反例已复现。该历史313项/51态未覆盖此时序。随后在BUG-032已批准TP04/TP10范围修复，已加载/在途照片预览及失效请求失败回归通过，最终331项前端全过，见[独立保存的新源/证据](../footprints-minimal-20261024/README.md)。本目录旧implementation-final和51图只保留原范围；不改写成当前diff通过。修复未冒充独立复审或完整交付。

Spec最终保留`specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md`，Status VERIFYING。恢复条件是补齐实际点击/系统picker、iOS/Android字体/读屏/真实选图和独立review，并由家长完成产品验收；未全部通过不标DONE、不移动completed。
