# BUG-034 旅行控件与倒序时间线 — 本地实施证据

- Status: LOCAL_IMPLEMENTATION / VERIFYING / NOT_UPLOADED
- Approval: 产品负责人（用户），2026-10-24，call_a4e6de3e6be5408fb860b26f20a09323回复「批准 Spec01＋Architecture01＋DREV01，按此实施」。
- Spec: [BUG-034 Spec01 / Architecture01](../../../../specs/active/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md)。
- Design: [DREV-20261024-FOOTPRINTS-TIMELINE-01](../../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md)，批准源与42张HTML快照冻结，不替代原生。
- Local stage: [本地交付记录](../../../deploy/releases/20261024-footprints-timeline-local.md)。

仅修改共享footprints模板/样式、presentation显示映射和controller初次/续页接入，共4份生产文件。主操作复用学习页btn胶囊（16px，主操作48px），三视图复用seg.n3及on态，局部44px高/三等列；不另建全局样式。每张缩略图下显示确认当地时刻HH:mm，缺失/非法值显示“时刻未知”，不从created_at推断。手动记录独立文本行、无伪照片，0照片用“查看到访”；预览失败仍保留时间和原详情入口。

服务端现有local_date DESC/id DESC及游标不改，客户端保持返回顺序；同日父母编辑的回放顺序、100条窗口/20条续读、≤4预览、离页/切孩子/面板失效与私有文件清理不变。未改API/SQL/数据库、授权、学习页或全局tokens，037/0025继续原阶段。

## 检查与范围

| 检查 | 实际结果 |
|---|---|
| npm test | PASS，335 tests / 335 pass / 0 fail / 0 skip，1268.881ms；本次新增3项 |
| npm run lint:miniapp | PASS |
| validate_miniprogram.py | PASS，17页，1221792源码字节（小于1.5MiB）；非上传压缩包体 |
| check_architecture.py | PASS，4 policies / 150 modules，runtime/lazy DAG |
| 指定批准清单＋current-policy design validator | PASS；批准源和42张导出SHA一致 |
| 新原生准备工具Ruff check/format | PASS |
| 原生320×568、390×844、430×932 | 每尺寸18态PASS，共54组节点/PNG；430于2026-10-25解锁后补齐，见[native-audit.json](native-audit.json) |
| 390原生实际点击 | PASS：回放tab→播放/暂停状态→时间线→未知时刻缩略图打开详情→关闭→更多直达设置→开关0→1→关闭。仅离线合成项目，无真实设置写入或照片读取 |
| 2026-10-25真实本地客户端交接 | 已重新编译完整云端客户端，停在记录→旅行日记→时间线；加载完成/无错误，三个44px等宽pill及导入按钮可见。仅取状态/几何，无合成注入、未打开真实照片或请求业务写入；见[交接状态](local-client-runtime.json) |
| 后端pytest/MySQL/迁移/真实媒体 | NOT_RUN / N/A，本次未改后端、Schema、接口与provider |
| 真机iOS/Android、读屏、系统大字体、家长真实数据验收 | NOT_RUN，不以合成开发者工具代替 |

3项新增回归验证：HH:mm/秒/小数秒/午夜、未知与非法时刻，不使用创建时间且保留原字段/manual/真实计数；初次＋跨页追加＋100条换窗口保持服务端次序和显示映射、保留孩子scope；私有预览失败后日期/时刻和openVisit详情可达。既有并发预览、viewer/归档/离页/切孩子、分页失败游标和回放回归随335项通过。

原生工具：[准备器](../../../../tools/prepare_footprints_timeline_native.py)、[采集器](../../../../tools/footprints_timeline_geometry.js)。独立副本位于/private/tmp/push-kids-footprints-timeline-native-20261024，禁云、移除插件、合成家庭/孩子/照片、只读transport拒绝业务写入。只在副本增加fixture/滚动绑定；fixture调用真实timelineVisit派生标签。11份耦合源码经去除已声明注入后与当前源逐字匹配；[14份源/测试/工具摘要](source-manifest.json)不代表全工作区dirty diff验收。

18态为overview、preview_failed、empty、loading、error、viewer、long、playback、lit、settings、saving、photo、older_window、standalone，以及受按钮样式影响的consent/review/edit/confirm。原生节点核对44px/14px、主操作48px/16px、pill半径、三等列、不重叠、两列缩略图8px间隔、日期倒序、manual无伪图、未知时刻及紧凑设置。2026-10-25补齐430后再次核对14份源摘要及11份隔离副本，无差异；人工查看430总览与设置截图未见裁切或重叠。PNG原始像素和SHA逐张保留；独立Page的官方截图不含原生导航/状态区，与内嵌页全屏图的高度不同，不改尺寸或改名冒充。

首轮新项目出现开发者工具内部path undefined，App.callFunction超时；重新编译后采集成功，生产代码未因此修改。首轮390审计把44px紧凑播放按钮误按48px主CTA断言；修正为仅导入/面板主操作适用48px，再采18态均通过。上述为工具/审计问题，不写成业务修复。getSystemInfoSync弃用与既有合成年级接口提示不算本次业务/真实服务通过。

## 文档与生命周期

当前Spec保留active/VERIFYING，三尺寸原生已通过，用户业务/设备/读屏/大字体验收尚待闭环；最终单独只读复核结论见本会话收尾报告，不伪称其他代理独立审查。当前事实同步Feature/Behavior/Architecture/UI/设计/测试/发布与Spec索引；旧批准清单仅追加对应范围Superseded by。按实际diff核对未发现本范围当前正文与代码冲突，不把历史原生或037读取结果移作本次界面验收。未提交、推送、上传、部署或操作业务数据。
