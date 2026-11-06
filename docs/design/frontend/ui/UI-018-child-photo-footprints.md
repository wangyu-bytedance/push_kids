# UI-018 — 孩子照片足迹

当前本地呈现revision `UI-STATE-20261106-THEMES-01`：[DESIGN-002 Spec08 / Architecture01](../../../../specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)与DREV08已获用户“好的 按照以上方案落地”批准并实施，DREV06视觉方向保持。独立足迹页、records嵌入宿主及共享弹层显式接入六主题；导入/核对/三视图/照片编辑及分页原合同保持。原生地图底图和本地PNG标记属平台边界，路线覆盖色集中在registry命名角色，避免随深色背景失去底图对比。 本增量尚未上传；原生合成呈现、共享业务回归及真机/独立评审缺项见[当前证据](../../../quality/evidence/themes-20261106/README.md)。下方原特性发布与验收记录保持其版本范围，不能代验六主题。

当前交付：[Spec01 / Architecture01](../../../../specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)＋DREV01批准实现保持，168份冻结源覆盖0.1.17官方上传成功1,191,019字节，基准已bump。039 normal/100%/1、微信健康与三尺寸42组原生/局部动作分别自动留证；用户本轮照片回看/分页与双家庭非owner门禁PASS_OPERATOR_CONFIRMED。三项旅行Spec DONE/completed，设备/可访问性/完整内容缺项开放，未体验/提审/正式发布。[当前上传](../../../deploy/releases/20261101-client-0.1.17-upload.md)保留原失败和证据范围。

2026-10-26开发归档（历史；旅行三项2026-11-01交付见本页当前正文）：已交付037后端/0.1.16客户端所覆盖的需求按用户批准规则标记开发DONE，验收缺项独立保留；后续BUG-035和旅行导入精简尚未交付，继续active。当前归档和待验入口见[Spec状态清单](../../../../specs/STATUS.md)，依据为[治理Spec](../../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。本轮不改产品合同、测试结论、设计或发布阶段。

当前导入：[Spec01 / Architecture01](../../../../specs/completed/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md)与DREV02获批实现已随0.1.17开发上传，DONE；直接相册、选择忙态、实际上传计数/进度、批次保留重试与AI仅已有紧凑设置保持。原349项/15组原生/430取消多选失败重试与设置方法级结果保留，设备/读屏/大字/完整家长验收独立开放。[原证据](../../../quality/evidence/travel-import-simplification-20261025/README.md)不作为本轮重跑；原DREV局部接管边界不变。

BUG-035：[Spec01 / Architecture01 / DREV01](../../../../specs/completed/BUG-035-TRAVEL-DIARY-END-TO-END.md)已由039与0.1.17两端交付，DONE；本轮用户正向回看/分页/双家庭非owner门禁确认与自动原生/健康证据分别保留。此前0.1.16不含本修复，完整设备/内容验收开放，体验/审核/正式发布未推进。

已批准并本地实施：[BUG-034 Spec01 / Architecture01](../../../../specs/completed/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md)及[DREV01](../prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md)。普通主操作与三视图复用学习btn/seg胶囊，时间线保留日期倒序/游标，缩略图下显示确认HH:mm或“时刻未知”；manual文本无伪图，失败仍可看日期/时刻和详情。335项/静态、320/390/430各18原生态共54组及390实际点击通过；设备/用户验收开放。42张批准HTML与原生证据分开，见[本轮证据](../../../quality/evidence/footprints-timeline-20261024/README.md)。

当前精简增量：[Spec01](../../../../specs/completed/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) / [DREV01](../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)获用户明确批准，已本地删除重复身份标题、设置两段长文及两行常驻次要入口。统计右侧44px既有线性更多图标，原生菜单按权限/归档显示，单项直接执行、无项隐藏；归档选择不截断并复用原放弃保护。设置只留开关/关闭/保存并按内容收高；工程文案要求已合并。CR-001已修复并有已加载/在途预览回归；[当前源码证据](../../../quality/evidence/footprints-minimal-20261024/README.md)与历史原生结果分开记录，已随0.1.16开发上传，未体验或正式发布。

- Status: DEVELOPMENT_DONE / BACKEND_039_NORMAL_100_PERCENT / FRONTEND_0.1.17_UPLOADED / ACCEPTANCE_PARTIAL
- UI state revision: UI-STATE-20261101-TRAVEL-ENTRY-CLEANUP-08-CLIENT-UPLOADED
- Current increment verified: 2026-11-01；官方upload1191019/bump0.1.17，42组原生/局部动作与039微信健康PASS；用户正向focus/分页/双账号确认PASS，设备/完整内容仍未验。
- Feature: [FEAT-012](../../../domain/features/FEAT-012-child-photo-footprints.md)
- Spec: [SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04](../../../../specs/completed/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)，开发DONE，2026-10-18获实施批准，已随037/0.1.16交付；验收缺项独立保留。
- Baseline: FDB-20260913-04；FEC-20261007-NATIVE-GEOMETRY-02。
- Effective Design Revisions: DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01基础流程；[DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02](../prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md)文案增量；[DREV-20261024-RECORD-ENTRY-01](../prototypes/DREV-20261024-RECORD-ENTRY-01/FRONTEND-SPEC.md)类型菜单/孩子外观/全部范围与导入位置；[DREV-20261024-FOOTPRINTS-MINIMAL-01](../prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)重复标题、次要入口和紧凑设置；DREV-20261024-FOOTPRINTS-TIMELINE-01普通按钮/三视图/缩略时刻；DREV-20261025-TRAVEL-DIARY-E2E-01核对/编辑/确认/画廊；DREV-20261025-TRAVEL-IMPORT-02直接相册/上传/失败；DREV-20261031-TRAVEL-ENTRY-CLEANUP-01接管零草稿与空态两入口。旧批准源/快照冻结，局部接管边界见Current approved increment；其他主功能视觉差异验收未完成。
- Companion Specs: [BUG-032 Spec05](../../../../specs/completed/BUG-032-RECORD-ENTRY-CONTEXT.md)、[文案Spec01](../../../../specs/completed/FEAT-012-FOOTPRINTS-UI-COPY.md)、[入口Spec01](../../../../specs/completed/FEAT-012-RECORD-TYPE-SWITCHER.md)，均开发DONE并随0.1.16上传；完整验收仍待补。
- Current approved increment: [入口精简Spec01/Architecture01](../../../../specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)及DREV-20261031-TRAVEL-ENTRY-CLEANUP-01接管零草稿兜底和空态新建手动到访入口。[DREV-20261025-TRAVEL-IMPORT-02](../prototypes/DREV-20261025-TRAVEL-IMPORT-02/FRONTEND-SPEC.md)的直接相册/选择/上传/失败与设置，[BUG-035 / DREV01](../../../../specs/completed/BUG-035-TRAVEL-DIARY-END-TO-END.md)的核对/编辑/确认/画廊等其余区域继续有效；旧批准源/导出冻结，仅在原DREV02清单增加局部Superseded by指针。
- Last verified: 2026-10-31（349项/静态与HTTP V2 preview通过，320两宿主各七态原生通过；兼容后端789/46、实库/规模及039部署通过，实际应用账号Schema/数据库ready/无DDL独立只读PASS；定向云/双账号与其余矩阵未验，未上传）
- Previous source verification: 2026-10-25；BUG-035专项41/全量347及320/390/430各14态共42组最终源原生节点/PNG通过；430隔离系统选图→补日期→保选→确认→第三张回看及回放通过。地图夹具修复及CR-001设置保存中返回缩略图恢复有方法级证据。真实云三张草稿上传/重试、城市保存409续接、缺日期校验和预览通过；AI两失败/一空候选，日期/正式确认、新focus云端、真实键盘/设备/读屏/大字/家长验收尚缺，见[当前证据](../../../quality/evidence/travel-diary-e2e-20261025/README.md)。旧335/54和0.1.16上传保持历史范围。

## 当前已验证事实

当前有效[DREV-20261025-TRAVEL-DIARY-E2E-01](../prototypes/DREV-20261025-TRAVEL-DIARY-E2E-01/FRONTEND-SPEC.md)覆盖导入恢复、核对/缺日期面板、编辑照片、失败/冲突续接和精确回看；原批准HTML/42张设计导出冻结，另有42组原生证据，不相互代验。其余有效DREV仍按各自范围生效。

真实六六现有3草稿，城市“大连”、日期未知、0正式照片/到访；原生缩略图及编辑预览可见。日期来源仅EXIF或家长输入，不以下载/上传时间代填。城市输入使用生产editField自动化，保存/冲突刷新/重试/缺日期CTA与空值保存为实际原生点击，不能写成整段CUA输入通过。

生产源码现有`pages/footprints/`，从记录Tab标题切换到“旅行日记”，与学习记录共用五个底部Tab。原足迹Page深链接保留，和内嵌组件共用控制器/模板/样式。支持孩子切换、全时间足迹、照片导入与日期/地点人工纠正、草稿批量核对与确认、三视图、历史到访编辑/删除和照片分页预览；本地客户端不再提供新建无图到访入口，服务端manual兼容API未改。日期筛选整行及其客户端参数已删除，拍摄日期与纠正保留。BUG-032等旧领域/文案证据只证明各自历史范围，当前入口精简结果见本页顶部本轮证据，批准源和快照保持冻结。

## 本地实现与交互合同

导入按钮直接调用系统相册，删除说明、勾选与同意CTA，不迁移长文；选择中原按钮显示忙态并拒绝重复操作。取消恢复原页面/孩子且零业务写入，正常hide/show取消或失败恢复首页预览；选图失败在导入入口显示短错误并可再选。选中后只POST既有imports合同，不写成员偏好；AI保持已有值，在更多→足迹设置显式修改。上传面板按内容收高，显示完成张数/总数与完成文件百分比；上传中关闭/主CTA禁用。失败面板保留真实错误、成功数量、重试与核对已上传，重试继续同批次且跳过已收讫项。此合同覆盖旧首次说明/勾选/重复AI区域；空态手动创建入口已由2026-10-31入口精简删除。

点击记录标题展开其下8px、200px宽的顶部菜单，两项各48px，当前项淡绿底/勾选；无灰色遮罩、重复标题或关闭按钮。再次点击标题、外部点击、滚动或离页收起；外部点击不透传，选择先收起再走离开保护。菜单保留底部导航，旅行照片/编辑面板隐藏导航。右侧孩子复用纸色child-chip/首字头像/细箭头，单孩子无箭头、长名整块右对齐换行。首次默认学习，普通Tab返回记住类型；切换保留学习文字/照片/日期/孩子/幂等键和滚动。旅行孩子独立，上传中阻止切换，编辑离开须确认；明确学习入口经同样保护切回学习，旧确认跨代结束时续接新意图，普通取消不重复弹窗。

时间线、回放、点亮、统计和地点详情统一读取当前孩子全部已确认足迹。三视图复用学习seg.n3胶囊、44px等列，on态纸色底/绿字/轻阴影。时间线按当地日期DESC/id DESC显示，照片两列/8px间隔/每卡≤4张，图下14px时刻HH:mm或“时刻未知”；历史manual文本无伪图、计数仍为真实照片数。时间线/地点详情按游标读取、每窗口最多100条，“查看下一组”显式替换并回到列表开始；触底不自动替换，失败保留窗口和游标，释放旧窗口预览并拒收迟到文件。各视图内容之后只有一个48px通栏导入按钮，20px线性相机＋16px文字，上距20px、btn胶囊圆角，随页面滚动；底部留白避开导航及中央凸起键。活动且可写时显示，保存/上传保护有效。空时间线保留原插画和“还没有足迹”，删除手动创建按钮后按原布局自然收高；零草稿不显示兜底入口，有真实草稿仍显示“X 张待核对”。本增量原生位置/收高验收待补，学习手动录入及上传路径保留。
用户已确认事后出游回忆、确认后入档、足迹相册、首版全球；主要区域优先可看全部、空态中国；地点点亮＋城市/国家汇总；一批一个孩子；无日期草稿、有日期无地点可入时间线；记录入口与自动日期整理。
第三、四轮确认的固定7天草稿、条件原件24h清理、按需AI、到访日、镜头跟随、分批继续、归档收尾及逐张纠正/删除已接入。上传失败保留批次幂等键/成功项续接；草稿多页停止首屏轮询以保留选择。画廊20张窗口以focus_photo_id准确打开被点照片，previous/next游标前后可达，迟到画廊请求不覆盖新照片。真正退出/切家庭/孩子/成员废弃操作；普通hide停止回放/读取/轮询，释放文件同时清URL，大图正在使用的文件保留至返回再清；show恢复草稿、编辑/画廊预览、选择和表单。AI设置以当前成员为单位。

核对主动作在所选照片缺日期时进入“补拍摄日期”，只更新选中且缺日期项，不默认日期；已有日期保留。编辑显示当前照片、日期旁错误和预览重试。单张/批量保存返回核对保留所选ID/新version；部分成功重试跳过成功项，409保留输入并提供“读取最新版本后继续”。确认分批成功后移除成功选择，失败只续接剩余。选图/选点/上传/保存期间防重入及离开保护；正常系统返回不清操作上下文。面板具可访问名称、独立滚动、固定关闭/主CTA，响应keyboardheightchange；210px占位原生几何通过不等于实际软键盘通过。

设置保存中隐藏会释放首页预览；若保存未完成就已返回前台，保存成功后补载缩略图，仍在后台则由下次show恢复。CR-001两种返回/完成时序与原生方法通过，不改变批准视觉。

国内/局部原生map支持拖动/聚类下钻；全球总览现为经纬度点位图和列表，不是全球真实底图的验收证据。原生scale限制、海外点位转换/底图和缩略图表现仍须真机验证。缺日期/时刻可清回未知；正式日期必填；同日顺序可编辑。这些控件及全球呈现与DREV01需逐项设计核对；若可见差异需新DREV批准，旧快照保持不可变。

## 验证及发布状态

2026-10-23 BUG-031服务端SQL调整的真实MySQL5.7预算/计划与镜像证据保留原范围，早期031健康200不代后续版本验收。主产品及本UI旅行三增量现已开发DONE；当前039/0.1.17交付与完整产品/设备验收分别记录，见[历史后端证据](../../../quality/evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md)及当前上传报告。

后续用户指定同库直接升级顺序，10:55冻结0019→0022/current/check及结构/队列核验通过；035先GRAY normal/0%，用户随后100%接管并删除034，11:01核验旧实例0、coverage=false。真实微信18项GET均200；完整本地客户端已重开，实际标题菜单→旅行日记timeline组件加载无错、有可用孩子，无fixture/源码改动，见[本地入口证据](../../../quality/evidence/fullstack-release-20261024/client-local-entry.json)。Spec03临时维护提案撤回未实施，[OPS Spec04](../../../../specs/completed/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md)按新规则开发DONE归档，原缺失验收保留。全量前定向检查NOT_RUN，真实照片/地图/权限/设计/真机仍待验收，不把本地入口通过当成完整UI验收。

2026-10-23用户批准的DREV02曾将处理细则集中设置；该部分现由获批MINIMAL-01覆盖，设置不再展示供应商/7天/24小时及原件处理长文，规则仍在领域执行。本次导入精简DREV02再覆盖首次说明和勾选：系统权限由微信处理，AI仍由已有设置显式选择；AI候选、真实到期日期、家长确认和删除后果保留在发生的操作处。[旧逐项文案目标](../prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/COPY-CHANGES.md)与27态×3 HTML只保留历史范围，不作为当前导入/设置合同或原生验收。

本UI设计矩阵为27态×3精确视口（320×568、390×844、430×932）。实际导出/DOM/交互结果以DREV清单与render-audit为准。
81张手机PNG和桌面图、DOM/主要点击与R3/R4语义演示通过；本机虚构数据可刷新续接，确认/编辑/删除同步三视图。演示时钟的7天资格检查不证明服务端清理、真实对象删除或并发实现。
用户解锁后已完成24态×3精确视口的72份原生节点JSON/PNG，修正微信默认按钮样式引起的关闭/选择/底部操作宽度及间距。插画缩略图、长姓名和滚动后的地点候选有可视证据；详见[原生清单与范围](../../../quality/evidence/child-footprints-20261018/native/README.md)。隔离副本移除报41002的语音插件、关闭云和load并加入测试滚动绑定，生产配置未改。此结果不代表完整插件包、真实操作或DREV一致性通过。
2026-10-18旧证据缺少records/import/saved/denied/photo-delete/expired/draft-delete七态；本轮记录类型另有学习、旅行、双菜单及长名矩阵，旅行复用24态重采，不因此宣称完整27态逐态一致。真机字体放大/相册/地图、键盘/权限、读屏、真实AI和设计差异仍待验；字符图标/圆角、清空字段/同日排序及全球呈现须核对。上述原生采集时没有上传；后续基础实现已随0.1.16开发上传，未体验、审核或正式发布。

2026-10-23历史布局证据为320×568/390×844/430×932各29态、共87份当时源码节点/PNG；源SHA对应当时版本。先前320/390中间记录已被重采替换。[历史原生说明](../../../quality/evidence/record-types-20261023/native/README.md)列明合成压力标签与隔离差异；它不抵扣BUG-032当前diff，也不证明完整设计或真实设备/服务验收。

## Change references

| Date | Change | Evidence | State |
|---|---|---|---|
| 2026-10-31 19:57核对 | 039 normal/0%交付且实际应用账号数据库检查通过；320两宿主14组及168份冻结源摘要通过，390/430真实尺寸守卫预检未采集 | [当前交付](../../../deploy/releases/20261031-travel-diary-backend-compatibility.md) / [原生采集准备](../../../quality/evidence/client-release-20261031/native-current-matrix.md) | BACKEND_DELIVERED / NATIVE_PARTIAL / NOT_UPLOADED |
| 2026-10-31 续接（历史） | login/preview1191019及320内嵌七态原生通过；其余矩阵待验，兼容后端测试FAIL | [续接](../../../deploy/releases/20261031-client-release-resume.md) | VERIFYING / NATIVE_PARTIAL / NOT_UPLOADED |
| 2026-10-31 | 入口精简Spec01/Architecture01/DREV01获批并本地删除两入口与manual创建状态；349项及静态校验通过 | [本轮证据](../../../quality/evidence/travel-entry-cleanup-20261031/README.md) | VERIFYING / NATIVE_NOT_RUN / NOT_UPLOADED |
| 2026-10-25 | BUG-035 Spec01/Architecture01/DREV01获批并实施选图恢复、缺日期/编辑保选、续接与精确回看，42组当前原生和隔离实际流程通过 | [本轮证据](../../../quality/evidence/travel-diary-e2e-20261025/README.md) | VERIFYING / NOT_UPLOADED / NOT_DEPLOYED |
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
