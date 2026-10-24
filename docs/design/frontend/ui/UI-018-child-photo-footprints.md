# UI-018 — 孩子照片足迹

当前精简增量：[Spec01](../../../../specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) / [DREV01](../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)获用户明确批准，已本地删除重复身份标题、设置两段长文及两行常驻次要入口。统计右侧44px既有线性更多图标，原生菜单按权限/归档显示，单项直接执行、无项隐藏；归档选择不截断并复用原放弃保护。设置只留开关/关闭/保存并按内容收高；工程文案要求已合并。CR-001已修复并有已加载/在途预览回归；[当前源码证据](../../../quality/evidence/footprints-minimal-20261024/README.md)与历史原生结果分开记录，仍未上传。

- Status: CLIENT_LOCAL / BACKEND_035_DEPLOYED / VERIFYING / CLIENT_NOT_UPLOADED
- UI state revision: UI-STATE-20261024-PHOTO-FOOTPRINTS-15
- Feature: [FEAT-012](../../../domain/features/FEAT-012-child-photo-footprints.md)
- Spec: [SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04](../../../../specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)，VERIFYING，2026-10-18获本地实施批准。
- Baseline: FDB-20260913-04；FEC-20261007-NATIVE-GEOMETRY-02。
- Effective Design Revisions: DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01基础流程；[DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02](../prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md)文案增量；[DREV-20261024-RECORD-ENTRY-01](../prototypes/DREV-20261024-RECORD-ENTRY-01/FRONTEND-SPEC.md)接管类型菜单/孩子外观/全部范围与导入入口；本次[DREV-20261024-FOOTPRINTS-MINIMAL-01](../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)再接管重复标题、次要入口和紧凑设置。旧批准源与快照冻结；其他主功能视觉差异验收未完成。
- Companion Specs: [BUG-032 Spec05](../../../../specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md)、[文案Spec01](../../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md)、[入口Spec01](../../../../specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md)，均VERIFYING。
- Last verified: 2026-10-24，最终共享工作区331项前端、lint、Mini Program/架构/批准设计校验通过；本次三尺寸27态原生及430实际菜单取消/设置/归档选择通过，系统操作菜单不在官方手机截图层内。设备/独立复核边界见[当前证据](../../../quality/evidence/footprints-minimal-20261024/README.md)。旧313项/51组原生与035接管后18项读取仅保留历史范围；完整设计/真机验收PARTIAL。

## 当前已验证事实

生产源码现有`pages/footprints/`，从记录Tab标题切换到“旅行日记”，与学习记录共用五个底部Tab。原足迹Page深链接保留，和内嵌组件共用控制器/模板/样式。支持孩子切换、全时间足迹、导入/人工、草稿批量核对与确认、三视图、逐张编辑/删除和照片分页预览。日期筛选整行及其客户端参数已删除，拍摄日期与纠正保留。当前调整见[BUG-032验证](../../../quality/evidence/record-entry-20261024/README.md)；旧领域/文案证据仍只证明各自历史范围，批准源和快照保持冻结。

## 本地实现与交互合同

点击记录标题展开其下8px、200px宽的顶部菜单，两项各48px，当前项淡绿底/勾选；无灰色遮罩、重复标题或关闭按钮。再次点击标题、外部点击、滚动或离页收起；外部点击不透传，选择先收起再走离开保护。菜单保留底部导航，旅行照片/编辑面板隐藏导航。右侧孩子复用纸色child-chip/首字头像/细箭头，单孩子无箭头、长名整块右对齐换行。首次默认学习，普通Tab返回记住类型；切换保留学习文字/照片/日期/孩子/幂等键和滚动。旅行孩子独立，上传中阻止切换，编辑离开须确认；明确学习入口经同样保护切回学习，旧确认跨代结束时续接新意图，普通取消不重复弹窗。

时间线、回放、点亮、统计和地点详情统一读取当前孩子全部已确认足迹。时间线/地点详情按游标读取、每窗口最多100条，“查看下一组”显式替换并回到列表开始；触底不自动替换，失败保留窗口和游标，释放旧窗口预览并拒收迟到文件。各视图内容之后只有一个48px通栏导入按钮，20px线性相机＋14px文字，上距20px、圆角12px，随页面滚动；底部留白避开导航及中央凸起键。活动且可写时显示，保存/上传保护有效；空态保留手动记录，学习上传路径不变。
用户已确认事后出游回忆、确认后入档、足迹相册、首版全球；主要区域优先可看全部、空态中国；地点点亮＋城市/国家汇总；一批一个孩子；无日期草稿、有日期无地点可入时间线；记录入口与自动日期整理。
第三、四轮确认的固定7天草稿、条件原件24h清理、按需AI、到访日、镜头跟随、分批继续、归档收尾及逐张纠正/删除已接入。首次文件失败保留批次重试；草稿多页停止首屏轮询以保留选择；画廊使用20张窗口可前后翻页。退出/切孩子忽略迟到请求、停止回放并清预览临时文件；AI设置以当前成员为单位。

国内/局部原生map支持拖动/聚类下钻；全球总览现为经纬度点位图和列表，不是全球真实底图的验收证据。原生scale限制、海外点位转换/底图和缩略图表现仍须真机验证。缺日期/时刻可清回未知；正式日期必填；同日顺序可编辑。这些控件及全球呈现与DREV01需逐项设计核对；若可见差异需新DREV批准，旧快照保持不可变。

## 验证及发布状态

2026-10-23 BUG-031只调整服务端缩略图SQL执行形态，API/顺序/预览数量/UI源码未变，设计与前端工程影响均N/A；真实MySQL5.7.44两种五万照片分布预算及计划通过，见[后端证据](../../../quality/evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md)。10-24镜像门禁及BUG-031 DONE已闭合；早期本地客户端连接旧031健康200是历史观察，后续0022/035及本地重开状态见下段，不把早期结果当新版本验收。产品Spec和本UI仍VERIFYING。

后续用户指定同库直接升级顺序，10:55冻结0019→0022/current/check及结构/队列核验通过；035先GRAY normal/0%，用户随后100%接管并删除034，11:01核验旧实例0、coverage=false。真实微信18项GET均200；完整本地客户端已重开，实际标题菜单→旅行日记timeline组件加载无错、有可用孩子，无fixture/源码改动，见[本地入口证据](../../../quality/evidence/fullstack-release-20261024/client-local-entry.json)。Spec03临时维护提案撤回未实施，[OPS Spec04](../../../../specs/active/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md)继续VERIFYING。全量前定向检查NOT_RUN，真实照片/地图/权限/设计/真机仍待验收，不把本地入口通过当成完整UI验收。

2026-10-23用户批准的DREV02曾将处理细则集中设置；该部分现由获批MINIMAL-01覆盖，设置不再展示供应商/7天/24小时及原件处理长文，规则仍在领域执行。授权、AI候选、真实到期日期、家长确认和删除后果保留在发生的操作处。[旧逐项文案目标](../prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/COPY-CHANGES.md)与27态×3 HTML只保留历史范围，不作为当前设置合同或原生验收。

本UI设计矩阵为27态×3精确视口（320×568、390×844、430×932）。实际导出/DOM/交互结果以DREV清单与render-audit为准。
81张手机PNG和桌面图、DOM/主要点击与R3/R4语义演示通过；本机虚构数据可刷新续接，确认/编辑/删除同步三视图。演示时钟的7天资格检查不证明服务端清理、真实对象删除或并发实现。
用户解锁后已完成24态×3精确视口的72份原生节点JSON/PNG，修正微信默认按钮样式引起的关闭/选择/底部操作宽度及间距。插画缩略图、长姓名和滚动后的地点候选有可视证据；详见[原生清单与范围](../../../quality/evidence/child-footprints-20261018/native/README.md)。隔离副本移除报41002的语音插件、关闭云和load并加入测试滚动绑定，生产配置未改。此结果不代表完整插件包、真实操作或DREV一致性通过。
2026-10-18旧证据缺少records/import/saved/denied/photo-delete/expired/draft-delete七态；本轮记录类型另有学习、旅行、双菜单及长名矩阵，旅行复用24态重采，不因此宣称完整27态逐态一致。真机字体放大/相册/地图、键盘/权限、读屏、真实AI和设计差异仍待验；字符图标/圆角、清空字段/同日排序及全球呈现须核对。没有上传、体验、审核或正式发布。

2026-10-23历史布局证据为320×568/390×844/430×932各29态、共87份当时源码节点/PNG；源SHA对应当时版本。先前320/390中间记录已被重采替换。[历史原生说明](../../../quality/evidence/record-types-20261023/native/README.md)列明合成压力标签与隔离差异；它不抵扣BUG-032当前diff，也不证明完整设计或真实设备/服务验收。

## Change references

| Date | Change | Evidence | State |
|---|---|---|---|
| 2026-10-24 | MINIMAL Spec01/DREV01获批并实施重复标题/次要入口/设置减法，工程文案规范合并；本轮三尺寸27态与实际菜单操作通过 | [当前证据](../../../quality/evidence/footprints-minimal-20261024/README.md) | VERIFYING / NOT_UPLOADED |
| 2026-10-24 | 批准BUG-032 Spec05/DREV01并本地实现顶部菜单、纸色孩子chip、默认全时间和下方普通导入按钮；学习入口竞态回归通过 | [本轮验证](../../../quality/evidence/record-entry-20261024/README.md) | VERIFYING / NOT_UPLOADED |
| 2026-10-23 | 最终三尺寸29态×3合成原生矩阵通过，当前源与87份SHA已核对，完整设计/真机仍开放 | [当前原生证据](../../../quality/evidence/record-types-20261023/native/README.md) | VERIFYING / NOT_RELEASED |
| 2026-10-23 | 获批并实施标题切换/共享旅行组件与文案精简，当前源码单独验证 | [实现证据](../../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md) | VERIFYING / NOT_RELEASED |
| 2026-10-18 | 新增文案精简候选及逐项改动，生产文案未改，待具体批准 | [DREV02](../prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md) / SPEC-20261018-FOOTPRINTS-UI-COPY-01 | AWAITING_APPROVAL / NOT_IMPLEMENTED |
| 2026-10-18 | 解锁后24态×3隔离原生布局及SHA通过，修正按钮几何；完整验收仍PARTIAL | [原生证据](../../../quality/evidence/child-footprints-20261018/native/README.md) | VERIFYING / NOT_RELEASED |
| 2026-10-18 | 本地实现与回归，记录原生/设计一致性及全球地图待验收 | [实现证据](../../../quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md) | VERIFYING / NOT_RELEASED |
| 2026-10-17 | 应用户要求制作交互候选并启动grill review | DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01 | PENDING / NOT_IMPLEMENTED |
| 2026-10-17 | 同步R2五项确认与R3待答边界，更新未批准稿的评审说明 | SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-03 | PENDING / NOT_IMPLEMENTED |
| 2026-10-17 | 同步R3/R4，新增AI设置、归档、正式纠正/删除、草稿删除/到期及照片预览7态与语义走查 | SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04 / DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01 | PENDING / NOT_IMPLEMENTED |
| 2026-10-17 | Q19确认需求共识/交互稿，冻结源/81张手机图与SHA，实施另批 | [Q19原话与范围](../../../research/child-footprints/20261017-grill-review.md#q19-整体确认记录) | DESIGN_APPROVED / NOT_IMPLEMENTED |
