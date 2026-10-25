# FEAT-012 — 孩子照片足迹

- Feature ID: `FEAT-012`
- Status: `BACKEND_037_DEPLOYED / CLIENT_LOCAL / VERIFYING / CLIENT_NOT_UPLOADED`
- Current-state revision: `FEAT-STATE-20261025-PHOTO-FOOTPRINTS-21`
- Owner: 产品负责人（用户）
- Last verified: 2026-10-25（BUG-034当前335项前端/静态门禁、320/390/430各18原生态共54组及390实际点击通过；设备/用户验收未完成。后端仍037/0025，客户端未上传；[本轮UI证据](../../quality/evidence/footprints-timeline-20261024/README.md)与既有部署证据分开）
- Active Spec: [SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04](../../../specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)，`VERIFYING`；用户2026-10-18“落地编写代码”批准本地实施。
- Research: [孩子照片足迹可行性报告](../../research/child-footprints/20261017-feasibility.md)。
- Authoritative implementation: `apps/api/src/push_kids/footprints/`、`agent_processing/footprint_provider.py`、`apps/miniprogram/pages/footprints/`、迁移`20261018_0021`。
- Evidence: [本地实现与待验收项](../../quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md)。

## Current verified state

当前BUG-034增量：[Spec01 / Architecture01](../../../specs/active/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md)及[DREV01](../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-TIMELINE-01/FRONTEND-SPEC.md)已获明确批准并本地实施。普通主操作复用学习btn胶囊/16px，三视图使用seg.n3纸色选中态、44px等列。时间线沿用API当地日期DESC/id DESC及稳定cursor；每张实际缩略图下显示确认HH:mm，缺失为“时刻未知”，manual用文本、不伪造照片，失败保留时刻与详情入口。同日回放、100条窗口和预览清理不变。335项及三尺寸54组原生证据见[本轮验证](../../quality/evidence/footprints-timeline-20261024/README.md)，设备/读屏/大字体及用户验收待补；42张批准HTML仅设计证据，未上传。

2026-10-24用户明确批准并本地实现[足迹界面减法Spec01](../../../specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) / [DREV01](../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)：删除重复孩子标题与设置长文，常驻两行次要入口改统计右侧44px更多按钮。可用操作按权限/归档显示，单项直接执行、无项隐藏；原生归档选择每页4个孩子加翻页、最多6项，不截断历史，选择经过原放弃保护。设置仅开关/关闭/保存，内容收高，失败保留值重试。工程UI文案附加条款已并入设计/FEC正文；不改首次授权、候选确认、7天/24h业务规则。BUG-032的CR-001已在原批准范围修复并通过两种照片预览时序回归，见[当前证据与未验收项](../../quality/evidence/footprints-minimal-20261024/README.md)。本轮未上传或部署。

用户于2026-10-17提出可行性调研：给孩子上传一张/多张照片，提取每张时间、地点，缺地点时AI辅助，展示时间线、地图按时间播放、地图点亮与缩略图；默认中国，支持扩展世界。

研究、[grill review](../../research/child-footprints/20261017-grill-review.md)与[交互稿](../../design/frontend/prototypes/DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01/index.html)于2026-10-17获需求/设计确认；2026-10-18获得实施批准。已实现独立源码/API、五张领域表、持久worker和三视图；2026-10-24早间0022/035接管后，晚间独立OPS将生产迁至0025并由037接管，足迹领域/API未变。本地完整客户端可进入旅行日记，真实产品验收仍开放。客户端未上传、体验、提审或正式发布；其他任务未提交修改不作为本Feature验收。

现有FEAT-007“出行安排”是上学/放学等周期时段，没有照片地点/历史足迹能力。现有学习上传使用压缩图，媒体归属和AI合同绑定学习提交，不能直接描述成已经可用的足迹基础流程。

## Local implemented behavior

独立footprints领域拥有导入、照片、到访日、revision和成员偏好。EXIF优先，缺日期保持未知；AI首次明确开启后仅对缺地点照片给至多三个候选，允许拒答，不能生成正式到访或推断拍摄日期/坐标。人工可补日期/地点或无图记录，家长确认才入档。时间线、点亮与按当地日期/同日顺序回放读取同一确认事实，纠正/删除同步重算。

第一轮用户确认事后出游回忆、家长确认后入档、足迹相册不承诺原画备份、首版全球；国内优先/海外后置建议已撤回。第二轮确认主要区域优先可看全部、空态中国；地点点亮＋城市/国家汇总；每批一个孩子；有日期无地点可入时间线、无日期留草稿；记录页进入并按日期自动整理，无须先建行程相册。

第三、四轮确认：每张上传成功起固定7天清未确认草稿，编辑/重试不延期、正式照片保留；元数据/派生图成功后原件24h清理，失败原件至第7天；首次开启后仅缺地点按需AI，可关闭；地点＋当地日期为到访日；回放镜头跟随；几十张分批继续；足迹内访问归档孩子旧草稿，不新增；正式照片逐张纠正/删除并重算统计。

单批最多20张（旧基础库选择器9张，可分批），每孩子待整理上限200；服务端列表20/最大50，地图最多200簇，回放100点分段。客户端默认当前孩子全部已确认足迹，无日期筛选或start/end参数；时间线和地点详情每窗口最多100条，满100后显式“查看下一组”替换窗口、回到列表开头，不缓存历次窗口。触底仅在当前窗口内续读；失败保留窗口与游标，替换释放旧缩略图并使迟到预览失效；时间线响应返回时若已打开面板/切换视图，则不应用结果或回收新预览，游标仍可重试。仅JPEG/PNG/WebP、10MiB、4000万像素单帧；解码隔离进程10秒超时。展示2048/缩略320、去元数据、不上采样；HEIC提示转换。原件仅在元数据/派生成功后24h清理；未确认照片上传成功起168h固定到期，正式展示图保留。到期读取立即拒绝，物理清理有重试及管理员失败重试接口。

地图自动聚焦最密集空间区域，显示其他区域到访日数量；空态中国。国内/局部使用原生地图；全球总览目前为经纬度点位图与列表，可下钻原生地图，尚不是验收通过的全球底图。未转换WGS84单独提示，不混作GCJ02画点。全球地图合同仍待真实账号与原生验收，不视为已满足首版全球地图要求。

## Dependencies and verification status

已接入FEAT-002家庭鉴权（viewer只读）、FEAT-005归档旧草稿入口及FEAT-006媒体/数据owner清理。归档不接受新导入，既有槽位可继续；deleting冻结读写/任务。孩子删除保留同家庭其他孩子及家庭偏好；家庭删除一并清偏好。足迹不写learning/planning/travel。云媒体签名60秒、本地鉴权私有下载，响应no-store；不返回原件或完整EXIF。

合成EXIF/确认/权限/清理/归档/迟到覆盖、迁移和五万照片SQLite有界读取已运行。2026-10-23发布准备中真实MySQL5.7.44发现IN/UNION反复执行，用户批准BUG-031 Spec01后改为物化派生表JOIN；最终冻结包两种五万分布时间线0.3935/0.1724秒，实际索引/主键计划、分页/隔离/删除、响应/内存预算通过，相关MySQL专项加规模31项通过，见[当前证据](../../quality/evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md)。这不是生产性能或云存储验收。真机选图保留率、AI分层地点真值、地图全球账号/费用与清晰度未验证。用户解锁后24态×3隔离原生节点/截图通过，修正默认按钮宽度和间距；[原生范围](../../quality/evidence/child-footprints-20261018/native/README.md)仅合成布局子集，完整插件包、设计基线缺失7态和真机仍待验收。

沿用`FDB-20260913-04`、`FEC-20261007-NATIVE-GEOMETRY-02`与已冻结DREV01。[UI-018当前状态](../../design/frontend/ui/UI-018-child-photo-footprints.md)记录实现和设计待核对项；日期/时刻清空、同日排序控件需纳入后续设计核对，未宣称与批准快照逐像素一致。Spec因验收未闭环保留active/VERIFYING。

2026-10-24最终冻结容器/130源匹配通过，BUG-031已[completed/DONE](../../../specs/completed/BUG-031-FOOTPRINT-PREVIEW-MYSQL57.md)。用户备份后明确指定同库直接升级顺序，10:55冻结0019→0022/current/check、55表/8触发器/队列核验通过。035先GRAY normal/0%，随后用户100%接管并删除034；11:01–11:03完整清单显示旧实例0、035 normal/100%/1实例、coverage=false。接管后真实微信18项GET全部200，含足迹草稿/到访/统计/地图/回放，本地完整AppID/插件客户端菜单→旅行日记timeline加载无错。全量前定向检查未执行，不追认通过；真实上传、私有对象/双账号、全球地图、照片AI与真机验收仍未完成。

031/034删除已核验，配置差异已解决，不再要求重设开关或查找暂停入口。[Spec03维护桥接](../../../specs/rejected/OPS-20261024-SPEC03-MAINTENANCE-PROPOSAL.md)撤回且未实施；[OPS Spec04](../../../specs/active/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md)记录实际执行。本地项目现已重开并停留旅行日记；API/设计合同与Feature验收生命周期未变。见[迁移](../../quality/evidence/fullstack-release-20261024/database-upgrade-attempt02.json)、[035](../../quality/evidence/fullstack-release-20261024/backend-035.json)、[微信读取](../../quality/evidence/fullstack-release-20261024/cloud-smoke-035.json)和[本地入口](../../quality/evidence/fullstack-release-20261024/client-local-entry.json)。

用户要求精简冗余提示并选择标题切换入口，于2026-10-23要求“完成这个功能的代码编写”，批准[入口Spec01](../../../specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md)及[文案Spec01](../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md)。2026-10-24又批准[BUG-032 Spec05 / DREV01](../../../specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md)，本地记录标题改为顶部锚定下拉，菜单展开保留底部导航；旅行照片/编辑面板仍隐藏导航。右侧孩子使用既有纸色child-chip、首字头像和线性箭头，单孩子隐藏箭头、长姓名整块换行。普通Tab记住类型，学习文字/照片/日期/孩子/幂等键和滚动保留；明确学习入口经原离开保护切回学习，旧跨代确认结束后续接尚未消费的新意图，普通取消不重试。旅行孩子独立、归档可收尾旧草稿；原深链接与内嵌组件共享控制器。导入照片是各视图内容之后唯一的48px通栏普通按钮，随内容滚动；活动且可写时可见，保存/上传中拒绝重入，空态保留手动记录。见[本轮证据](../../quality/evidence/record-entry-20261024/README.md)，完整原生/真机验收以其中逐项状态为准，未上传或部署本增量。

本地生产文案已应用[DREV02](../../design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/FRONTEND-SPEC.md)，删除操作教学和重复内部规则，保留同意、AI候选、具体到期、实际到访确认、删除后果及示意标签。10-23入口设计及[当时实现证据](../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)保持历史范围，当前入口由上段DREV-20261024-RECORD-ENTRY-01覆盖；不以旧证据代表当前源码验收。入口和文案Spec均active/VERIFYING，主Spec04未完成项保持；本次客户端增量无上传或部署。

10-23历史验证中，用户解锁后完成29态×3的87份节点/PNG，38源SHA对应当时源码；不代表10-24新菜单/按钮差异已验收。当前结果见BUG-032证据，字体/键盘/读屏、完整插件包与真机仍待验收。

## Change references

| Date | Change | Spec / evidence | Release |
|---|---|---|---|
| 2026-10-24 | 获批实施MINIMAL Spec01/DREV01及工程文案条款；当前三尺寸27态、430原生菜单与最终331项前端通过，CR-001在原批准范围修复 | [精简实施证据](../../quality/evidence/footprints-minimal-20261024/README.md) | VERIFYING / CLIENT_NOT_UPLOADED |
| 2026-10-24 | 用户批准BUG-032 Spec05/DREV01并本地实施顶部菜单、纸色孩子chip、学习入口竞态修复、全时间有界续看与下方48px导入按钮 | [本轮验证](../../quality/evidence/record-entry-20261024/README.md) / [本地发布](../../deploy/releases/20261024-record-entry-local.md) | VERIFYING / CLIENT_NOT_UPLOADED |
| 2026-10-24 | 冻结迁移0019→0022通过；035部署，用户100%接管/删除034，旧实例0；真实18项读取200，本地旅行入口加载通过，coverage=false | [发布记录](../../deploy/releases/20261023-fullstack-test-deployment.md) | BACKEND_DEPLOYED / CLIENT_LOCAL / VERIFYING |
| 2026-10-23 | 用户批准BUG-031，修复MySQL5.7缩略图执行形态；最终冻结包真实MySQL/SQLite预算与计划通过；数据库与后端尚未部署 | [BUG-031证据](../../quality/evidence/FOOTPRINT-PREVIEW-MYSQL57-20261023.md) / [部署准备](../../deploy/releases/20261023-fullstack-test-deployment.md) | VERIFYING / 未上传部署 |
| 2026-10-23 | 用户再次解锁，补齐最终320/390，87份当前源码合成原生节点/PNG通过；完整验收仍开放 | [当前原生范围](../../quality/evidence/record-types-20261023/native/README.md) | VERIFYING / 未上传部署 |
| 2026-10-23 | 获批并本地实现标题类型切换、旅行内嵌及文案精简；完整验收仍开放 | [本轮证据](../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md) / 入口Spec01 / 文案Spec01 | VERIFYING / 未上传部署 |
| 2026-10-18 | 文案精简设计候选，删除重复解释但保留决策信息；生产未改 | SPEC-20261018-FOOTPRINTS-UI-COPY-01 / DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02 | 待批准 / 未实施 |
| 2026-10-18 | 解锁后完成72份原生合成布局导出，修正按钮几何；完整验收保留开放 | [原生证据](../../quality/evidence/child-footprints-20261018/native/README.md) | VERIFYING / 未上传 |
| 2026-10-18 | 用户批准Spec04/Architecture03后本地实现领域、三视图和验证；原生/真实服务待验收 | [实现证据](../../quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md) | 未部署/上传 |
| 2026-10-17 | 建立新Feature规划身份并交付可行性调研；无生产变更 | [DRAFT Spec](../../../specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)、[研究与来源](../../research/child-footprints/20261017-feasibility.md) | N/A |
| 2026-10-17 | grill第一轮确认全球/自适应等根决定；交互候选，后续前沿待答 | SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-02 / DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01 | N/A |
| 2026-10-17 | 第二轮五项确认入正文；第三轮五项待答；补充原生容量与归档/删除接入核查 | SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-03 / grill记录 | N/A |
| 2026-10-17 | 第三/四轮九项确认，更新27态交互与语义验证，待整体确认 | SPEC-20261017-CHILD-PHOTO-FOOTPRINTS-04 / ARCH-20261017-CHILD-PHOTO-FOOTPRINTS-03 | N/A |
| 2026-10-17 | Q19“认可，评审收敛”；需求/交互设计确认并冻结DREV，实施另批 | [grill确认记录](../../research/child-footprints/20261017-grill-review.md#q19-整体确认记录) / [设计批准清单](../../design/frontend/snapshots/UI-018/DREV-20261017-CHILD-PHOTO-FOOTPRINTS-01/APPROVAL.md) | N/A |
