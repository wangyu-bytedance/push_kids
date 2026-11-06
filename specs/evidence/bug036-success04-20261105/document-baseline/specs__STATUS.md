# Spec 开发状态与独立验收清单 — 2026-11-01

新增[BUG-036成功率修复Spec04](active/BUG-036-FIXED40-SUCCESS-REPAIR.md)：READY_FOR_REVIEW，尚未批准/实施；原六条诊断与12/15完整40复测33/40＝82.5%、各科60%/86.7%/86.7% FAIL见[诊断EVD](evidence/EVD-20261101-BUG036-FIXED40-DIAGNOSIS.md)。
保留原40测量对象和失败分母，未云交付；旧10/13的发布Spec仍BLOCKED。

缓存灰度发布：[OPS发布Spec01](active/OPS-20261101-BUG036-CACHE02-DEPLOYMENT.md)已明确批准，现BLOCKED。
工具维护/全库Ruff与format、前端349和运行Schema通过；冻结10/13固定40例实际34/40和各科低于90%导致发布门禁FAIL。
未创建GRAY，仍039/100%，缓存及父Spec未由此云交付。[停止记录](../docs/deploy/releases/20261101-knowledge-cache-gray-blocked.md)保留真实结果和恢复条件，活动12/15不混入此候选。

2026-11-01[BUG-036内容Spec03 / Architecture03 / Prompt05](active/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)已获批准并本地实施12/15，VERIFYING/active；[12 EVD](evidence/EVD-20261101-BUG036-CONTENT03-ACCEPTANCE.md)166专项/896全量PASS、52条件skip。两个独立finding经真实Red修复、第二轮0新确认问题；缓存02政策保持。原30为20产出/10内容PASS/9严格PASS＋1正确拒绝，原六PASS回退3；补充0/3、边界7/10严格通过，内容FAIL；资源与51/61表审计PARTIAL。历史FAIL和11诊断不追改，无本增量云交付。

本轮BUG-036缓存最终状态核验：用户要求“将状态更新为已部署，并生成最终验收报告”后真实查询最新返回云版本仍039 normal；该已交付包为staged06，与缓存10/13五份源不同。[最终验收](../docs/quality/evidence/BUG036-CACHE02-FINAL-ACCEPTANCE-20261101.md)将部署核验记NOT_VERIFIED、整体验收PARTIAL，缓存及父Spec仍VERIFYING/active；没有匹配云交付，不新增DONE归档。

- 当前完成规则：[GOV-SPEC-20261026-CLOUD-DELIVERY-DONE-01](completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。
- 用户批准：本对话“如果已经发布到云端就认为需求已经开发完成，你来更新”。
- 基线：`0576ac304649`加各任务既有工作区修改；旅行交付仅上传已验证168份冻结客户端0.1.17，版本bump及文档闭合，无Git提交/推送；并行BUG-036/037不混入。
- `DONE`表示需求开发完成。对应实现已由匹配版本的云端后端正常部署或小程序开发版本成功上传即可归档；涉及两端时分别核对。
- 验收与发布独立：NOT_RUN/PARTIAL/FAIL保持原结果；开发上传不等于体验、审核或正式发布，关闭的功能开关保持关闭；缺失批准不因归档得到追认。

## 1. 当前目录结论

| 分类 | 数量 | 状态含义 |
|---|---:|---|
| completed中的完成记录 | 108 | 原完成归档、038知识Spec/测试维护及039＋0.1.17本轮旅行三Spec |
| completed中的设计阶段产物 | 1 | DESIGN-001，保留STAGE_COMPLETE |
| active / VERIFYING | 4 | BUG-036父Spec/缓存Spec02/内容Spec03及BUG-037本地实施未匹配云交付；内容/原生等缺项独立保留 |
| active / READY_FOR_REVIEW | 8 | 含BUG-036成功率修复Spec04；具体修订待批准，不能因其他功能已发布推定完成 |
| active / BLOCKED | 1 | OPS缓存发布Spec01已批准，固定40例质量门禁FAIL，未创建GRAY |
| active / APPROVED | 0 | 已批准任务的实际实施进度分别记录；未因其他功能交付追认完成 |
| active / DRAFT | 2 | 多家庭隔离与云成本审计草案，具体修订待批准 |
| rejected | 13 | 保留取消/否决理由 |

合计137份：`completed/109 + active/15 + rejected/13`。039后端与0.1.17客户端已交付，16:15:08官方upload成功1,191,019字节并bump；用户補齐正向focus/分页/双家庭非owner门禁，记PASS_OPERATOR_CONFIRMED。三项旅行Spec DONE/completed，42组原生/局部动作及微信健康证据保持，设备/内容等缺项独立。BUG-036父Spec/缓存补充/独立内容03/成功率Spec04、新OPS和BUG-037不在上传包，计数以目录为准。[上传记录](../docs/deploy/releases/20261101-client-0.1.17-upload.md)为当前事实。

2026-11-01独立[BUG-036缓存Spec02 / Architecture02](active/BUG-036-CHECKPOINT-RETRY-STRATEGY.md)获“批准 BUG-036 缓存 Spec02，开始实施”后本地实施10/13，VERIFYING。116专项、857全量PASS/52条件skip、隔离MySQL5.7迁移/Schema/8PASS；全库Ruff范围外E501仍FAIL。[EVD](evidence/EVD-20261101-BUG036-CACHE02.md)绑定代码/测试/审查与首败；未云交付，父Spec亦VERIFYING。原三份六图09/13内容反证保持，缓存机制通过不代表内容验收。

2026-11-01新增[BUG-037页脚与提示Spec01](active/BUG-037-REPORT-FOOTER-TIPS.md)与
[DREV01修改稿](../docs/design/frontend/prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/index.html)：
用户两张报表截图对应共享编辑计划分页和操作结果提示；批准记录为“批准 Spec01 + DREV01”，现已本地实现，状态VERIFYING。
349项/静态和原430双宿主16组方法等PASS；用户解锁后的齐套03包含三视口双宿主144组PNG/节点/解码/SHA，TP-004 PASS。
本Spec独立168份冻结源＋批准2份替换的官方preview1192127字节成功，无线真机码已准备，未扫码/未upload；
本增量不由0.1.17交付，留active；[齐套03证据](../docs/quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)保留真实设备/大字/读屏NOT_RUN，不借并行任务代验。

[BUG-036 Spec01 / Architecture01](active/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md)与[Prompt04](evidence/KNOWLEDGE-PROMPT-04-DRAFT-20261031.md)已批准并本地实现09/13。832pass/46条件skip、独立增量71pass/0新增确认缺陷；[当前会话同30](../dist/knowledge-generation-evaluation-20261031-prompt04/session-evaluation/evaluation-30.md)26输出/12内容PASS/10完整PASS，原PASS18/25回退，AC-008 FAIL。零测试写入已验证，09通知投递38→37导致60/61表一致，归因未证明；实际清理独立留证。无云交付，保持VERIFYING/active，旧Spec03的DONE不覆盖09；07和两次08运行保留，旅行任务不代验。

此前同日“没有可新增归档项”的审计结论采用旧的全部验收完成门槛；用户本次已明确修改开发完成定义，本清单按新规则取代前一分类。产品质量要求和测试阈值未调整。

## 2. 云端交付与范围证据

| 交付对象 | 已有实际阶段 | 本轮核对 |
|---|---|---|
| [2026-10-24历史后端](../docs/deploy/releases/20261024-latest-backend-test-deployment.md) | 当时037 normal/100%，Schema0025；非当前版本 | 150份Python源码＋pyproject/uv.lock共152份与原冻结02清单SHA逐项一致 |
| [知识点质量后端038](../docs/deploy/releases/20261031-knowledge-prompt-backend.md) | 038 immutable gray `normal`，Schema0025；服务normal、PUBLIC关闭 | 精确冻结包793 passed/46 skipped；流量比例、定向038 smoke和全量切流NOT_RUN |
| [客户端0.1.16](../docs/deploy/releases/20261025-latest-client-upload.md) | 开发版本成功上传，未体验/提审/正式发布 | 168份源码/资源与[上传源码清单](../docs/quality/evidence/client-release-20261025/source-manifest.json)SHA逐项一致 |
| [兼容后端039及客户端0.1.17](../docs/deploy/releases/20261101-client-0.1.17-upload.md) | BACKEND_039_NORMAL_100_PERCENT / FRONTEND_0.1.17_UPLOADED | 168份冻结源官方upload1191019/bump成功；用户确认focus/分页/双家庭非owner门禁，42组原生/局部动作与微信健康PASS；未体验/审核/正式发布 |
| BUG-035和旅行导入/入口精简 | DONE / completed | BUG-035两端039/0.1.17及两个客户端增量均交付；设备/完整内容等验收缺项独立保留 |

2026-10-31开发DONE归档：[知识点生成Review与历史等价](completed/FEAT-001-KNOWLEDGE-POINT-ABSTRACTION-PROMPT.md)及[存量知识清理](completed/FEAT-001-HISTORICAL-KNOWLEDGE-CLEANUP.md)已由后端038云交付或完成对应生产数据修复。真实038语义/业务smoke、流量接管与正式发布独立保留为NOT_RUN。

源码核对按交付版本：037/0.1.16覆盖旧基线，039/0.1.17覆盖已批准旅行三增量；工作区并行BUG-036/缓存和BUG-037页脚不在本次冻结包。后端和客户端按对应Spec范围分别核对，成功开发上传作为对应客户端交付。

## 3. 本次开发DONE归档与待验项（41份）

下列待验项从原Spec/证据保留，独立于开发DONE管理；本轮没有补跑这些验收，也没有将缺项改为PASS。Owner和恢复条件沿用各Spec；需要产品/设备/真实内容时由相应验收者执行。

| 已归档Spec | 独立保留的验收/证据归并事项 | 原依据 |
|---|---|---|
| [BUG-028 — 分阶段材料分析、受控并发与失败恢复](completed/BUG-028-STAGED-ANALYSIS-RELIABILITY.md) | 完整历史消融、人工语义/费用验收及旧实验消费者退出；合成112次不代验 | [原证据](../docs/quality/evidence/BUG-028-STAGED-ANALYSIS.md) |
| [BUG-029 — 完成复习条目后科目分组跳序](completed/BUG-029-REVIEW-SUBJECT-ORDER.md) | 定向业务反馈保序、共存/指标验收未留完整证据；后续031全量记录不代验 | [原证据](../docs/quality/evidence/REVIEW-SUBJECT-ORDER-20261016.md) |
| [BUG-030 — 删除背景中类似头发丝的细弧线 (Spec Lite)](completed/BUG-030-HERO-BACKGROUND-ARC.md) | 完整原生/长内容/大字体、iOS/Android及用户视觉验收 | [原证据](../docs/quality/evidence/HERO-ARC-REMOVAL-20261021.md) |
| [BUG-032 — 记录页照片入口、顶部选择与学习入口回归](completed/BUG-032-RECORD-ENTRY-CONTEXT.md) | 系统picker真实选择/取消、OS操作、独立评审及真机/可访问性 | [原证据](../docs/quality/evidence/record-entry-20261024/README.md) |
| [BUG-034 — 旅行按钮一致性与倒序时间线](completed/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md) | 设备/读屏/大字体与家长真实数据验收；三视口54组已补齐 | [原证据](../docs/quality/evidence/footprints-timeline-20261024/README.md) |
| [BUG — CRUD账号Schema readiness与触发器元数据权限隔离](completed/BUG-CRUD-SCHEMA-READINESS.md) | 用户业务写入/设备反馈；037接管和20项读取已通过 | [原证据](../docs/quality/evidence/latest-backend-release-20261024/README.md) |
| [CLOUD-001 — 微信云托管、MySQL 与私有云存储迁移](completed/CLOUD-001-WECHAT-CLOUDBASE-STAGE1.md) | 独立R3评审、TP-005..010剩余真实staging项及隐私/删除门禁 | 见归档Spec原验收记录 |
| [FEAT-001 — 设置页课外活动按星期排序 (Spec Lite)](completed/FEAT-001-ACTIVITY-WEEKDAY-ORDER.md) | TP-004三视口原生证据；开发上传不代验 | [原证据](../docs/quality/evidence/ACTIVITY-WEEKDAY-ORDER-20261010.md) |
| [FEAT-001 — Ark 会话上下文复用开关](completed/FEAT-001-ARK-CONTEXT-REUSE-FLAG.md) | 用户要求的真实Ark配对延迟A/B及相应结论 | 见归档Spec原验收记录 |
| [FEAT-001 — AI 自动替代复习词条](completed/FEAT-001-AUTO-SUPERSEDED-REVIEW-STATE.md) | 三视口原生/真机、独立评审及最终事实核对；MySQL专项已有证据 | [原证据](../docs/quality/evidence/AUTO-SUPERSEDED-REVIEW-20261020.md) |
| [FEAT-001 — 卡片背景与插画全面接入](completed/FEAT-001-CARD-BACKGROUNDS-COMPLETE.md) | 完整原生状态矩阵、iOS/Android及用户视觉验收 | [原证据](../docs/quality/evidence/CARD-BACKGROUNDS-20261013.md) |
| [FEAT-001 — 空白日少量提前复习](completed/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md) | 后续实库证据与各TP归并；完整原生/设备、独立评审及策略适用验收，开关仍关闭 | [原证据](../docs/quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md) |
| [FEAT-001 — 每日复习科目覆盖与等待优先](completed/FEAT-001-FAIR-DAILY-REVIEW.md) | 原生三视口/真机、真实业务及全量AC/TP验收；首轮性能阻塞已由修订02关闭 | [原证据](../docs/quality/evidence/FAIR-REVIEW-PROJECTION-20261007.md) |
| [FEAT-001 — 公平复习索引投影与迁移兼容补充方案](completed/FEAT-001-FAIR-REVIEW-PERFORMANCE-AMENDMENT.md) | 性能/兼容本地证据已通过；父Spec原生与真实业务验收仍未闭合 | [原证据](../docs/quality/evidence/FAIR-REVIEW-PROJECTION-20261007.md) |
| [FEAT-001 — 精确原图与单知识点删除](completed/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md) | 原生/真机、独立审查及删除与反馈/确认的额外并行压力验证 | [原证据](../docs/quality/evidence/SOURCE-DELETE-20261006.md) |
| [FEAT-001 — 记录与日程纸艺插画](completed/FEAT-001-RECORD-CALENDAR-ILLUSTRATIONS.md) | 完整原生节点/截图、真机解码/交互及视觉验收 | [原证据](../docs/quality/evidence/RECORD-CALENDAR-ILLUSTRATIONS-20261013.md) |
| [FEAT-001 — 报表内历史记录与编辑计划折叠区](completed/FEAT-001-REPORT-DISCLOSURES.md) | TP-005 iOS/Android真机；0.1.13开发上传不代验 | [原证据](../docs/quality/evidence/REPORT-DISCLOSURES-20261011.md) |
| [FEAT-001 — 报表展开区视觉与交互修订（Spec Lite）](completed/FEAT-001-REPORT-PANELS-REFINEMENT.md) | 完整原生截图、字体放大/loading视觉及双平台真机 | [原证据](../docs/quality/evidence/REPORT-PANELS-20261013.md) |
| [FEAT-001 — 报表复习条目预览与手动调整](completed/FEAT-001-REVIEW-INVENTORY-AND-RESCHEDULING.md) | DREV03完整视觉导出/冻结manifest、原生三视口及真机 | [原证据](../docs/quality/evidence/REVIEW-MANAGEMENT-20261006.md) |
| [FEAT-001 — 复习条目按科目卡片展示（Spec Lite）](completed/FEAT-001-REVIEW-INVENTORY-GROUPED-CARDS.md) | 新版设计导出/完整manifest及真机；后续界面已另批重设计，未据此自动取消 | 见归档Spec原验收记录 |
| [FEAT-001 — 复习条目清单式改版（Spec Lite）](completed/FEAT-001-REVIEW-INVENTORY-REDESIGN.md) | 风险状态导出及iOS/Android真机；后续重设计不自动关闭前序验收 | [原证据](../docs/quality/evidence/review-inventory-redesign-20261010/) |
| [FEAT-001 / FEAT-010 — 设置列表与每日任务统一（Spec Lite）](completed/FEAT-001-SETTINGS-CONSISTENCY.md) | 320/390原生、完整截图和双平台真机；430八态已有证据 | [原证据](../docs/quality/evidence/SETTINGS-CONSISTENCY-20261013.md) |
| [FEAT-001 — 学科管理与删除入口统一（Spec Lite）](completed/FEAT-001-SUBJECT-MANAGEMENT-CONSISTENCY.md) | 原生确认框/完整视觉截图、iOS/Android及读屏 | [原证据](../docs/quality/evidence/SUBJECT-MANAGEMENT-20261015.md) |
| [FEAT-001 — Item 生成、每日复习与自适应复习策略统一设计](completed/FEAT-001-UNIFIED-ITEM-REVIEW-STRATEGY.md) | 受控Ark/实库分项证据、原生设备矩阵与独立评审；不能用后来全量测试整体代验 | 见归档Spec原验收记录 |
| [FEAT-001 — 家长语音输入学习内容](completed/FEAT-001-VOICE-INPUT.md) | 隐私声明生效/麦克风授权、目标插件条款、完整原生音频/设备及独立评审 | 见归档Spec原验收记录 |
| [FEAT-004 — 连续两日无新增知识时的单项增量学习建议](completed/FEAT-004-INCREMENTAL-LEARNING-PATH.md) | 后续实库证据与各TP归并；真实内容/主体适用条件、完整设备与独立评审，默认关闭 | [原证据](../docs/quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md) |
| [FEAT-004 — 学习建议弹层精简与按钮层级（Spec Lite）](completed/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md) | 真实设备/键盘/读屏/大字体及实现后独立只读复核 | [原证据](../docs/quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md) |
| [FEAT-004 — 学习建议标题约束](completed/FEAT-004-SUGGESTION-TITLE-LIMIT.md) | TP-007真实iOS/Android、键盘、大字体及读屏；独立复核已通过 | [原证据](../docs/quality/evidence/SUGGESTION-TITLE-IMPLEMENTATION-20261024.md) |
| [FEAT-004 — 今日学习空区隐藏与样式统一（Spec Lite）](completed/FEAT-004-TODAY-CARD-VISIBILITY.md) | 真实设备/可访问性及独立复核；三视口81组已通过 | [原证据](../docs/quality/evidence/TODAY-CARD-IMPLEMENTATION-20261024.md) |
| [FEAT-009 — 每周不同日期使用不同时间](completed/FEAT-009-WEEKDAY-SPECIFIC-TIMES.md) | 具体DREV本地源/快照/批准、实库分项证据、原生/真机及独立评审；自记IMPLEMENTING | 见归档Spec原验收记录 |
| [FEAT-010 — 每日任务与今日区块自动折叠](completed/FEAT-010-DAILY-TASKS.md) | 完整原生/设备、生产写路径/多账号及所需独立审查证据 | [原证据](../docs/quality/evidence/DAILY-TASKS-20261012.md) |
| [FEAT-010 / FEAT-001 — 今日按钮与编辑计划分页统一（Spec Lite）](completed/FEAT-010-TODAY-ACTION-STYLE.md) | 320/390、报表内嵌、完整截图及iOS/Android；430部分状态已采集 | [原证据](../docs/quality/evidence/ACTION-PAGER-CONSISTENCY-20261015.md) |
| [FEAT-011 — 提醒授权自动补充](completed/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md) | 真实授权/完整原生与真机矩阵、独立评审；旧单条通知收件不代验 | [原证据](../docs/quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md) |
| [FEAT-012 — 孩子照片足迹](completed/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md) | 完整原生/真机、设计差异、全球底图及真实AI/素材质量；MySQL专项不再全记未运行 | [原证据](../docs/quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md) |
| [FEAT-012 — 足迹界面减法与 UI 文案要求](completed/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) | 设备/可访问性、独立复核及家长验收；原生27组及430部分实际操作通过 | [原证据](../docs/quality/evidence/footprints-minimal-20261024/README.md) |
| [FEAT-012 — 足迹界面文案精简（Spec Lite）](completed/FEAT-012-FOOTPRINTS-UI-COPY.md) | 完整状态/真机、设计差异及主功能剩余验收；同后续入口Spec共用实施证据 | [原证据](../docs/quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md) |
| [FEAT-012 — 记录类型标题切换](completed/FEAT-012-RECORD-TYPE-SWITCHER.md) | 字体放大/键盘/读屏及双平台完整包真机；87组隔离原生不代验全球底图/素材 | [原证据](../docs/quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md) |
| [FEAT-013 — 学年升年级建议与家长共享确认](completed/FEAT-013-ANNUAL-GRADE-PROMOTION.md) | 修复后原生全链路、真实双平台/前后台、可访问性及双家长旧端 | [原证据](../docs/quality/evidence/ANNUAL-GRADE-IMPLEMENTATION-20261024.md) |
| [FEAT-013 — 年级确认弹窗精简（Spec Lite）](completed/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md) | 真实设备/大字体/读屏/焦点及全业务原生端到端 | [原证据](../docs/quality/evidence/GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md) |
| [OPS-20261023 — 当前完整代码的服务端部署与客户端本地测试](completed/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md) | R09真实写入/照片/隔离及产品验收；迁移/035接管已留证据 | [原证据](../docs/deploy/releases/20261023-fullstack-test-deployment.md) |
| [OPS-20261024 — 最新服务端部署与完整客户端本地测试](completed/OPS-20261024-LATEST-BACKEND-TEST-DEPLOYMENT.md) | R09用户真实业务/设备/内容反馈；037接管后读取已通过 | [原证据](../docs/deploy/releases/20261024-latest-backend-test-deployment.md) |

每份归档Spec头部记录DONE、实际交付依据、治理revision及原开发状态；原批准范围和执行证据保留在历史记录中。FEAT-009此前IMPLEMENTING但其逐日时段代码已进入交付包，本次按实际交付归档，既有设计/批准缺项继续保留。

2026-11-01旅行新增归档的独立验收缺项：BUG-035真实日期/完整正式确认、AI地点质量、媒体生命周期、
完整设备/可访问性与末尾独立评审，导入精简的iPhone/Android/EXIF保留率和完整家长验收，入口精简的
真实键盘/读屏/大字与体验全矩阵。照片回看/前后分页和双家庭非owner上传门禁由用户本轮确认PASS；
原NOT_RUN/PARTIAL/FAIL保持，开发DONE不等同平台体验或正式发布。

## 4. 仍在active的开发任务（14份）

| Spec | 开发状态 | 保留原因及下一步 |
|---|---|---|
| [OPS — BUG-036缓存10/13后端灰度交付](active/OPS-20261101-BUG036-CACHE02-DEPLOYMENT.md) | BLOCKED | 已批准并完成工具维护及其他门禁；冻结10/13固定40case34/40、各科低于90%FAIL，停止GRAY创建；实际039/100%，无匹配云交付 |
| [BUG-004 — 微信小程序平台 API 兼容与失败恢复](active/BUG-004-WECHAT-MINIPROGRAM-API-COMPATIBILITY.md) | READY_FOR_REVIEW | 批准具体Spec及可见状态设计；实施后取得最低/当前基础库和双平台证据 |
| [BUG-033 — 档案归档区层级与文案精简（Spec Lite）](active/BUG-033-CHILD-ARCHIVE-UI.md) | READY_FOR_REVIEW | 具体Spec01与DREV01批准；随后实施和完整验收 |
| [BUG-036 — 修复知识点提案中断与质量规则冲突](active/BUG-036-KNOWLEDGE-GENERATION-FINAL-PROPOSAL.md) | VERIFYING | 批准范围本地09/13实现、832pass/46skip；同30为26输出/12内容PASS/10完整PASS，原PASS回退，内容FAIL；标签/全表审计PARTIAL，零测试写入，清理独立留证；未云交付/未DONE |
| [BUG-036 — 阶段缓存与明确重试策略补充](active/BUG-036-CHECKPOINT-RETRY-STRATEGY.md) | VERIFYING | 已批准并本地10/13实施；116专项/857完整PASS、52条件skip、隔离MySQL8PASS；全库Ruff范围外FAIL与内容反证保留；未部署/未云交付，保持active |
| [BUG-036 — 全部失败素材原始证据核验与纠正](active/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md) | VERIFYING | Spec03/Architecture03/Prompt05已批准，本地12/15、166专项/896全量PASS、52条件skip；两finding修复/第二轮0新问题；原30严格9PASS＋1正确拒绝、补充0/3、边界7/10，内容FAIL/原六回退3；资源/审计PARTIAL，无匹配云交付 |
| [BUG-037 — 编辑计划页脚与删除提示对齐](active/BUG-037-REPORT-FOOTER-TIPS.md) | VERIFYING | Spec01/DREV01已实施；349项/原16组方法等PASS，齐套03三视口双宿主144组PNG/节点/解码/SHA PASS；桌面已解锁，真机待扫码；独立preview1192127成功，未upload/未云交付 |
| [CLOUD-002 — 前后端确定性发布自动化](active/CLOUD-002-DETERMINISTIC-RELEASE-AUTOMATION.md) | READY_FOR_REVIEW | 具体发布自动化Spec/架构修订批准；现有发布工具不代表候选整体完成 |
| [DOC-001 — 图片与知识生命周期文档沉淀 (Spec Lite)](active/DOC-001-DATA-LIFECYCLE-DOCUMENTATION.md) | READY_FOR_REVIEW | 具体文档Spec批准及其全项事实/引用核验 |
| [DOC-003 — 以当前代码校正工程文档（Spec Lite）](active/DOC-003-CURRENT-CODE-DOCUMENTATION.md) | READY_FOR_REVIEW | 具体文档修订批准；该Spec自记仅完成范围准备，不能由本次索引整理代验 |
| [FEAT-001 / FEAT-003 — 中国工作日日程](active/FEAT-001-CHINA-WORKDAY-SCHEDULES.md) | READY_FOR_REVIEW | 具体Spec/DREV及R2批准；尚为候选 |
| [FEAT-002 — 多家庭访问与家庭/孩子全链路隔离](active/FEAT-002-MULTI-FAMILY-CHILD-TENANT-ISOLATION.md) | DRAFT | 多项产品/R3/ADR决定、精确DDL与设计批准；明确尚未开始实施 |
| [FEAT-008 — 当日无学习记录提醒](active/FEAT-008-DAILY-LEARNING-GAP-REMINDER.md) | READY_FOR_REVIEW | 具体Spec/架构/DREV批准及真实微信模板核验；未授权实施 |
| [OPS-20261010 — 云资源成本审计与发布后备份保留（Spec Lite）](active/OPS-20261010-CLOUD-COST-RETENTION.md) | DRAFT | 具体保护集/保留流程批准；本次不修改发布规则或删除云资源 |

当前7份待批准、1份BLOCKED、2份草案及4份VERIFYING对应范围未完整云交付。旅行三项已归档；BUG-036父Spec/缓存/独立内容03、新OPS和BUG-037分别记录，具体批准以各自Spec为准，0.1.17不追认其实施或验收。

## 5. completed完整索引（109份）

历史状态命名保留原文；本次新增DONE只代表开发完成，验收和发布限制见各Spec。

| Spec | 记录状态 |
|---|---|
| [BUG-035 — 旅行日记真实照片全链路与交互恢复](completed/BUG-035-TRAVEL-DIARY-END-TO-END.md) | DONE；039后端＋0.1.17客户端交付，设备/内容验收缺项独立 |
| [FEAT-012 — 旅行日记导入精简](completed/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md) | DONE；0.1.17开发上传，EXIF/设备/完整家长验收缺项保留 |
| [FEAT-012 — 旅行日记入口精简](completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md) | DONE；0.1.17开发上传，原生42组/用户账号门禁通过，真机/可访问性未验 |
| [OPS — 发布阶段缓存测试维护](completed/OPS-20261031-RELEASE-STAGE-CACHE-TEST-MAINTENANCE.md) | DONE；批准范围全部TP完成、无运行时变更；039发布验收缺项独立保留 |
| [AI-NATIVE-001 — Push Kids Agent Native 工程治理基线](completed/AI-NATIVE-001-REPOSITORY-BOOTSTRAP.md) | DONE |
| [BUG-002 — 设置页配置入口与学习档案文案修正（Spec Lite）](completed/BUG-002-SETTINGS-CONFIG-AND-COPY.md) | DONE |
| [BUG-003 — 云托管非 root 容器端口修正](completed/BUG-003-CLOUD-NONROOT-PORT.md) | DONE（历史限定见原文） |
| [BUG-005 — Worker 异常恢复与健康检查](completed/BUG-005-WORKER-FAULT-TOLERANCE.md) | DONE（历史限定见原文） |
| [BUG-006 — activity 不进入学习复习链路](completed/BUG-006-ACTIVITY-WITHOUT-REVIEW.md) | DONE（历史限定见原文） |
| [BUG-007 — CR-010 至 CR-015](completed/BUG-007-P2-REVIEW-FIXES.md) | DONE（历史限定见原文） |
| [BUG-008 — AI 不可用提示与人工录入兜底](completed/BUG-008-MANUAL-LEARNING-FALLBACK.md) | DONE（历史限定见原文） |
| [BUG-009 — AI 上下文、核心内容与重复分析保护](completed/BUG-009-AI-ANALYSIS-CONTEXT-AND-DEDUP.md) | DONE（历史限定见原文） |
| [BUG-010 — 家庭学习手册交互设计提案 V4](completed/BUG-010-INTERACTION-DESIGN-V4-DRAFT.md) | DONE（历史限定见原文） |
| [BUG-010 — 原生小程序视口适配与家长端关键交互修复](completed/BUG-010-NATIVE-LAYOUT-AND-PARENT-FLOWS.md) | DONE（历史限定见原文） |
| [BUG-011 — 云端分析卡死阶段诊断](completed/BUG-011-CLOUD-ANALYSIS-STALL-DIAGNOSTICS.md) | DONE（历史限定见原文） |
| [BUG-012 — Ark API Key 未被云运行时强制校验](completed/BUG-012-ARK-RUNTIME-SECRET.md) | DONE（历史限定见原文） |
| [BUG-013 — 多科目归类、待确认就地确认与四项家长动线修复](completed/BUG-013-MULTI-SUBJECT-AND-PARENT-FLOW.md) | DONE（历史限定见原文） |
| [BUG-014 — 归档档案的写入边界：拦新增、放收尾](completed/BUG-014-ARCHIVED-CHILD-WRITE-BOUNDARY.md) | DONE（历史限定见原文） |
| [BUG-014 — 无家庭用户启动时先进入家庭配置](completed/BUG-014-NEW-USER-FAMILY-ENTRY.md) | DONE（历史限定见原文） |
| [BUG-015 — 报表概览指标去跳转并增加区间趋势微图](completed/BUG-015-REPORT-METRIC-TRENDS.md) | DONE（历史限定见原文） |
| [BUG-015 — 六位家庭邀请码在申请前不可获得](completed/BUG-015-SIX-DIGIT-FAMILY-INVITE-CODE.md) | DONE |
| [BUG-016 — 通知数据接入永久删除流程](completed/BUG-016-NOTIFICATION-DELETION-INTEGRATION.md) | DONE（历史限定见原文） |
| [BUG-017 — AI 学习总结夹带无关排除项、复习记录接口返回 500](completed/BUG-017-AI-SUMMARY-AND-REVIEW-HISTORY.md) | DONE（历史限定见原文） |
| [BUG-018 — 历史、报表与看板读取必须有界](completed/BUG-018-BOUNDED-READ-API-PERFORMANCE.md) | DONE（历史限定见原文） |
| [BUG-019 — MySQL 5.7 read-path compatibility](completed/BUG-019-MYSQL57-READ-COMPATIBILITY.md) | DONE（历史限定见原文） |
| [BUG-020 — 过期复习匹配导致草稿无法确认](completed/BUG-020-STALE-REVIEW-CONFIRMATION.md) | DONE |
| [BUG-021 — 今日页复习计划不可见且内容截断](completed/BUG-021-TODAY-REVIEW-PLAN-VISIBILITY.md) | DONE |
| [BUG-022 — 图片分析 Agent 逐轮观测、容量与分类重试](completed/BUG-022-ANALYSIS-AGENT-OBSERVABILITY-AND-RETRY.md) | DONE |
| [BUG-023 — 今日复习项缺少可执行的原始材料上下文](completed/BUG-023-TODAY-REVIEW-SOURCE-MATERIAL.md) | DONE |
| [BUG-024 — MySQL 5.7 worker claim compatibility blocks release](completed/BUG-024-MYSQL57-WORKER-CLAIM-COMPATIBILITY.md) | DONE |
| [BUG-025 — 纯复习草稿确认丢失科目](completed/BUG-025-REVIEW-ONLY-CONFIRM-SUBJECT.md) | DONE |
| [BUG-026 — 分析最终校验回路与重试队列公平性](completed/BUG-026-ANALYSIS-VALIDATION-RETRY-FAIRNESS.md) | DONE |
| [BUG-027 — 空分析提案伪成功与基础科目识别缺口](completed/BUG-027-EMPTY-ANALYSIS-PROPOSAL-QUALITY.md) | DONE |
| [BUG-028 — 分阶段材料分析、受控并发与失败恢复](completed/BUG-028-STAGED-ANALYSIS-RELIABILITY.md) | DONE（云端交付） |
| [BUG-029 — 完成复习条目后科目分组跳序](completed/BUG-029-REVIEW-SUBJECT-ORDER.md) | DONE（云端交付） |
| [BUG-030 — 删除背景中类似头发丝的细弧线 (Spec Lite)](completed/BUG-030-HERO-BACKGROUND-ARC.md) | DONE（云端交付） |
| [BUG-031 — MySQL5.7足迹缩略图查询反复执行UNION](completed/BUG-031-FOOTPRINT-PREVIEW-MYSQL57.md) | DONE |
| [BUG-032 — 记录页照片入口、顶部选择与学习入口回归](completed/BUG-032-RECORD-ENTRY-CONTEXT.md) | DONE（云端交付） |
| [BUG-034 — 旅行按钮一致性与倒序时间线](completed/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md) | DONE（云端交付） |
| [BUG-20261013 — 每日任务发布的双版本 Schema 兼容](completed/BUG-20261013-DAILY-TASK-RELEASE-COMPATIBILITY.md) | DONE |
| [BUG — CRUD账号Schema readiness与触发器元数据权限隔离](completed/BUG-CRUD-SCHEMA-READINESS.md) | DONE（云端交付） |
| [BUG — MySQL永久替代历史迁移测试隔离](completed/BUG-MYSQL-SUPERSESSION-MIGRATION-ISOLATION.md) | DONE |
| [CHORE — 清理阻断后端发布的历史设计脚本 lint](completed/CHORE-20261016-RELEASE-LINT.md) | DONE |
| [CLOUD-001 — 微信云托管、MySQL 与私有云存储迁移](completed/CLOUD-001-WECHAT-CLOUDBASE-STAGE1.md) | DONE（云端交付） |
| [DESIGN-001 — 家长端关键交互 HTML 重设计评审稿（Spec Lite）](completed/DESIGN-001-HTML-REDESIGN.md) | STAGE_COMPLETE（设计阶段） |
| [DOC-002 — 全工程 Markdown 状态与冲突修订（Spec Lite）](completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md) | DONE |
| [FEAT-001 — 设置页课外活动按星期排序 (Spec Lite)](completed/FEAT-001-ACTIVITY-WEEKDAY-ORDER.md) | DONE（云端交付） |
| [FEAT-001 — Ark 会话上下文复用开关](completed/FEAT-001-ARK-CONTEXT-REUSE-FLAG.md) | DONE（云端交付） |
| [FEAT-001 — AI 自动替代复习词条](completed/FEAT-001-AUTO-SUPERSEDED-REVIEW-STATE.md) | DONE（云端交付） |
| [FEAT-001 — 卡片背景与插画全面接入](completed/FEAT-001-CARD-BACKGROUNDS-COMPLETE.md) | DONE（云端交付） |
| [FEAT-001 — 空白日少量提前复习](completed/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md) | DONE（云端交付） |
| [FEAT-001 — 每日复习科目覆盖与等待优先](completed/FEAT-001-FAIR-DAILY-REVIEW.md) | DONE（云端交付） |
| [FEAT-001 — 公平复习索引投影与迁移兼容补充方案](completed/FEAT-001-FAIR-REVIEW-PERFORMANCE-AMENDMENT.md) | DONE（云端交付） |
| [FEAT-001 — 历史学习与上传材料回看](completed/FEAT-001-HISTORY-AND-SOURCE-REVIEW.md) | DONE（历史限定见原文） |
| [FEAT-001 — 精确原图与单知识点删除](completed/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md) | DONE（云端交付） |
| [FEAT-001 — 家庭学习持续跟进系统最终产品 Spec](completed/FEAT-001-PUSH-KIDS-FINAL-SPEC.md) | DONE_WITH_EXTERNAL_RELEASE_GATES |
| [FEAT-001 — 家庭学习持续跟进系统 MVP](completed/FEAT-001-PUSH-KIDS-MVP.md) | COMPLETED（历史记录） |
| [FEAT-001 — 记录与日程纸艺插画](completed/FEAT-001-RECORD-CALENDAR-ILLUSTRATIONS.md) | DONE（云端交付） |
| [FEAT-001 — 报表内历史记录与编辑计划折叠区](completed/FEAT-001-REPORT-DISCLOSURES.md) | DONE（云端交付） |
| [FEAT-001 — 报表展开区视觉与交互修订（Spec Lite）](completed/FEAT-001-REPORT-PANELS-REFINEMENT.md) | DONE（云端交付） |
| [FEAT-001 — 报表复习条目预览与手动调整](completed/FEAT-001-REVIEW-INVENTORY-AND-RESCHEDULING.md) | DONE（云端交付） |
| [FEAT-001 — 复习条目按科目卡片展示（Spec Lite）](completed/FEAT-001-REVIEW-INVENTORY-GROUPED-CARDS.md) | DONE（云端交付） |
| [FEAT-001 — 复习条目清单式改版（Spec Lite）](completed/FEAT-001-REVIEW-INVENTORY-REDESIGN.md) | DONE（云端交付） |
| [FEAT-001 / FEAT-010 — 设置列表与每日任务统一（Spec Lite）](completed/FEAT-001-SETTINGS-CONSISTENCY.md) | DONE（云端交付） |
| [FEAT-001 — 学科管理与删除入口统一（Spec Lite）](completed/FEAT-001-SUBJECT-MANAGEMENT-CONSISTENCY.md) | DONE（云端交付） |
| [FEAT-001 — Item 生成、每日复习与自适应复习策略统一设计](completed/FEAT-001-UNIFIED-ITEM-REVIEW-STRATEGY.md) | DONE（云端交付） |
| [FEAT-001 — 家长语音输入学习内容](completed/FEAT-001-VOICE-INPUT.md) | DONE（云端交付） |
| [FEAT-002 — 微信云托管家庭创建、加入与成员审批](completed/FEAT-002-USER-FAMILY-BINDING.md) | DONE（历史限定见原文） |
| [FEAT-003 — 通知消息通道（Notification message channel）](completed/FEAT-003-NOTIFICATION-CHANNEL.md) | DONE（历史限定见原文） |
| [FEAT-004 — 连续两日无新增知识时的单项增量学习建议](completed/FEAT-004-INCREMENTAL-LEARNING-PATH.md) | DONE（云端交付） |
| [FEAT-004 — 学习建议弹层精简与按钮层级（Spec Lite）](completed/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md) | DONE（云端交付） |
| [FEAT-004 — 学习建议标题约束](completed/FEAT-004-SUGGESTION-TITLE-LIMIT.md) | DONE（云端交付） |
| [FEAT-004 — 今日学习空区隐藏与样式统一（Spec Lite）](completed/FEAT-004-TODAY-CARD-VISIBILITY.md) | DONE（云端交付） |
| [FEAT-005 — 一家庭多孩子档案管理与切换](completed/FEAT-005-MULTI-CHILD-PROFILE-MANAGEMENT.md) | DONE（历史限定见原文） |
| [FEAT-005 — 学前班级细分](completed/FEAT-005-PRESCHOOL-CLASS-GRANULARITY.md) | DONE（历史限定见原文） |
| [FEAT-006 — 家庭资料清理与重新开始](completed/FEAT-006-DATA-CLEANUP-AND-FAMILY-RESET.md) | DONE（历史限定见原文） |
| [FEAT-007 — 出行安排与日程冲突提示](completed/FEAT-007-TRAVEL-ARRANGEMENTS.md) | DONE（历史限定见原文） |
| [FEAT-009 — 每周不同日期使用不同时间](completed/FEAT-009-WEEKDAY-SPECIFIC-TIMES.md) | DONE（云端交付） |
| [FEAT-010 — 每日任务与今日区块自动折叠](completed/FEAT-010-DAILY-TASKS.md) | DONE（云端交付） |
| [FEAT-010 / FEAT-001 — 今日按钮与编辑计划分页统一（Spec Lite）](completed/FEAT-010-TODAY-ACTION-STYLE.md) | DONE（云端交付） |
| [FEAT-011 — 提醒授权自动补充](completed/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md) | DONE（云端交付） |
| [FEAT-012 — 孩子照片足迹](completed/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md) | DONE（云端交付） |
| [FEAT-012 — 足迹界面减法与 UI 文案要求](completed/FEAT-012-FOOTPRINTS-MINIMAL-UI.md) | DONE（云端交付） |
| [FEAT-012 — 足迹界面文案精简（Spec Lite）](completed/FEAT-012-FOOTPRINTS-UI-COPY.md) | DONE（云端交付） |
| [FEAT-012 — 记录类型标题切换](completed/FEAT-012-RECORD-TYPE-SWITCHER.md) | DONE（云端交付） |
| [FEAT-013 — 学年升年级建议与家长共享确认](completed/FEAT-013-ANNUAL-GRADE-PROMOTION.md) | DONE（云端交付） |
| [FEAT-013 — 年级确认弹窗精简（Spec Lite）](completed/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md) | DONE（云端交付） |
| [GOV-001 — 移除 Figma 依赖，采用仓库原生前端设计证据](completed/GOV-001-REPOSITORY-NATIVE-FRONTEND-DESIGN-EVIDENCE.md) | DONE |
| [GOV-002 — 云端交付作为需求开发完成依据](completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md) | DONE |
| [GOV-003 — 增量合并TDD、编码与Review规范](completed/GOV-003-TDD-CODING-REVIEW-INCREMENTAL-MERGE.md) | DONE；纯治理交付，真实任务效果NOT_RUN |
| [OPS-20261011 — 按变更影响判定双账号与数据库备份门禁](completed/OPS-20261011-RISK-BASED-RELEASE-GATES.md) | DONE |
| [OPS-20261017 — 微信接口502的有界错误分类与协议对照](completed/OPS-20261017-NOTIFICATION-502-DETAIL-DIAGNOSIS.md) | DONE |
| [OPS-20261017 — 通知诊断包经现有灰度发布链路部署](completed/OPS-20261017-NOTIFICATION-GRAY-DEBUG-DEPLOYMENT.md) | DONE |
| [OPS-20261017 — 通知 HTTP 拒绝原因的隔离诊断](completed/OPS-20261017-NOTIFICATION-HTTP-DIAGNOSIS.md) | DONE |
| [OPS-20261017 — 补齐订阅消息接口的微信令牌权限](completed/OPS-20261017-NOTIFICATION-OPENAPI-PERMISSION-FIX.md) | DONE |
| [OPS-20261017 — 用一条临时日程验证真实通知投递](completed/OPS-20261017-NOTIFICATION-SINGLE-EVENT-SMOKE.md) | DONE |
| [OPS-20261023 — 当前完整代码的服务端部署与客户端本地测试](completed/OPS-20261023-FULLSTACK-TEST-DEPLOYMENT.md) | DONE（云端交付） |
| [OPS-20261024 — 最新服务端部署与完整客户端本地测试](completed/OPS-20261024-LATEST-BACKEND-TEST-DEPLOYMENT.md) | DONE（云端交付） |
| [SPEC-20260906-PKDS-01 — PKDS-1.0 设计系统落地与字段级功能补齐](completed/SPEC-20260906-PKDS-01-DESIGN-SYSTEM-ROLLOUT.md) | DONE（历史限定见原文） |
| [SPEC-20260906-PKDS-03 — PKDS-2.0「纸 · 芽」视觉与交互落地](completed/SPEC-20260906-PKDS-03-PAPER-SPROUT-UI.md) | DONE（历史限定见原文） |
| [SPEC-20260907-PKDS-04 — 品牌页头与冗余提示清理](completed/SPEC-20260907-PKDS-04-BRAND-HEADER-COPY-CLEANUP.md) | DONE（历史限定见原文） |
| [SPEC-20260911-PRIMARY-NAV-BRAND — 一级页品牌移入导航栏 (Spec Lite)](completed/SPEC-20260911-PRIMARY-NAV-BRAND.md) | DONE（历史限定见原文） |
| [FEAT-001 — 记录入口简化（Spec Lite）](completed/SPEC-20260911-RECORD-ENTRY-SIMPLIFICATION.md) | DONE（历史限定见原文） |
| [FEAT-001 — 记录页照片来源统一追加（Spec Lite）](completed/SPEC-20260911-RECORD-PHOTO-ADD-SOURCE.md) | DONE（历史限定见原文） |
| [FEAT-001 — 设置页学习档案入口收敛（Spec Lite）](completed/SPEC-20260911-SETTINGS-PROFILE-MANAGER.md) | DONE（历史限定见原文） |
| [FEAT-001 — 设置页学习档案面板视觉降噪（Spec Lite）](completed/SPEC-20260911-SETTINGS-PROFILE-MANAGER-POLISH.md) | DONE（历史限定见原文） |
| [FEAT-001 — 今日页删除重复的课外活动空态日程入口（Spec Lite）](completed/SPEC-20260911-TODAY-ACTIVITY-EMPTY-CTA.md) | DONE（历史限定见原文） |

## 6. rejected索引（13份）

| Spec | 记录状态 |
|---|---|
| [BUG-010 交互稿 — DREV-20260905-UX-02](rejected/BUG-010-INTERACTION-DESIGN.md) | REJECTED |
| [BUG-010 视觉与布局修订 — DREV-20260905-UX-03](rejected/BUG-010-INTERACTION-DESIGN-V3-DRAFT.md) | REJECTED |
| [FEAT-001 — 确定性自适应复习策略 V2](rejected/FEAT-001-ADAPTIVE-REVIEW-POLICY-V2.md) | CANCELLED |
| [FEAT-001 — 聚合复习单元与每日稳定随机抽样](rejected/FEAT-001-BOUNDED-REVIEW-LOAD.md) | CANCELLED |
| [FEAT-001 — 聚合学习条目、全量当日复习上下文与确认后分流](rejected/FEAT-001-FULL-DUE-REVIEW-CONTEXT.md) | CANCELLED |
| [FEAT-001 — 设置页在学科目风格统一 (Spec Lite)](rejected/FEAT-001-SETTINGS-SUBJECT-LIST.md) | REJECTED |
| [FEAT-001 — AI 学习内容结构化确认](rejected/FEAT-001-STRUCTURED-AI-CONFIRMATION.md) | CANCELLED |
| [FEAT-001 — AI 按科目识别当日新增与复习条目](rejected/FEAT-001-SUBJECT-GROUPED-INCREMENTAL-AI.md) | CANCELLED |
| [FEAT-003 — 复习余量与课程提醒](rejected/FEAT-003-REVIEW-AND-CLASS-REMINDERS.md) | REJECTED |
| [FEAT-004 — 基于学习要求与历史节奏的每日学习建议](rejected/FEAT-004-DAILY-LEARNING-SUGGESTIONS.md) | REJECTED |
| [FEAT-010 — 设置每日任务视觉统一（Spec Lite）](rejected/FEAT-010-SETTINGS-TASK-VISUAL.md) | REJECTED |
| [OPS-20261023 — 当前完整代码的服务端部署与客户端本地测试](rejected/OPS-20261024-SPEC03-MAINTENANCE-PROPOSAL.md) | REJECTED |
| [VERIFY-001 — FEAT-001 完整端到端验证](rejected/VERIFY-001-FULL-E2E.md) | REJECTED |

## 7. 文档同步与维护边界

- 已将用户规则写入AGENTS、Spec README、开发协议及发布/测试说明；Feature/UI当前开发状态与可变索引/引用同步归档路径。
- 41份旧active文件已经迁移；冻结设计源/APPROVAL、发布原始JSON/日志、历史SHA库存不重写。它们保留批准或发布时的旧路径，可按文件同名在第3/5节进入当前completed文件。
- 原有BUG-015邀请码、已取消STRUCTURED-AI、已否决SETTINGS-SUBJECT-LIST/SETTINGS-TASK-VISUAL的冻结/历史路径同样保留，以completed/rejected真实目录为准。
- 当前正文已交付开发改为DONE、验收待补；BUG-035及旅行两精简于2026-11-01随039/0.1.17归档，原设备/内容缺项保持。旧执行结论明确历史阶段，冻结设计旧路径按同名completed索引解析。
- 代码/API/数据/架构边界、设计内容、测试矩阵和后续发布必需门禁均未改变；后续需求修订、实际缺陷修复或新发布按原授权和工作流执行。

## 8. 2026-10-26归档检查（历史证据）

| 检查 | 结果 |
|---|---|
| TP-001 云端源码/范围匹配 | PASS：168份客户端＋152份后端源码/依赖逐项SHA一致；两后续本地增量排除 |
| TP-002 Spec状态/目录/索引与可变链接 | PASS：41份DONE迁移；126份全部索引，目录102/11/13；可变文档1680处Markdown链接无缺失文件，旧迁移路径引用已修复；冻结历史链接按第7节保留 |
| TP-003 生产/测试/工具及冻结设计保护 | PASS：任务开始时2496份保护文件SHA逐项一致，原有工作区代码/测试/工具/冻结设计增量未改动 |
| TP-004 文档冲突/空白/架构及设计政策 | PASS：已交付范围的当前开发/发布正文完成冲突核对；41份原批准范围和验收正文仅调整标题层级/历史状态标签/引用，内容保留；check_architecture.py为ARCHITECTURE_VALID（4 policies/150 modules），validate_design_evidence.py --check-current-policy为DESIGN_EVIDENCE_VALID，git diff --check通过 |
| 产品后端/前端测试、原生/真机、实库、Ark、云端查询或发布 | NOT_RUN：本次仅文档和生命周期更新，引用历史结果并保留未验事实 |

本轮只按用户已明确批准的口径进行文档更新；没有提交Git、上传代码、切流或操作生产数据。

## 9. 2026-10-28治理合并

用户“批准Spec01，按方案合并”后，GOV-003增量更新AGENTS、开发/编码/维护协议、
架构约束、测试策略、Review模板，并补根REVIEW、ISS/REG模板和版本化EVD入口。
前端审查章节和1959份设计资产保持；历史任务Spec、产品代码/测试及发布阶段不改。
本任务纯治理交付按已批准Spec01归档DONE，不能作为产品云交付或质量收益证据。
实际命令、逐文件/文档核对、校验缺口及未执行项见
[EVD-20261028-GOV-003](evidence/EVD-20261028-GOV-003-BASELINE.md)。
