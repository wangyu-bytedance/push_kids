# 2026-10-31 — 前端0.1.17上传准备与阻断（初次记录）

本报告正文全部为初次准备时的历史快照，当前以[批准后交付报告](20261031-travel-diary-backend-compatibility.md)为准：
测试维护Spec01完成、精确候选789/46与10模块MySQL/规模通过，039 normal/0%已部署、038保持100%。
CLI登录与preview1191019成功，320两宿主七态通过；039定向smoke、双账号和剩余原生门禁未齐，
前端未upload/bump。下方旧EPERM、未部署和局部测试结果限定当时，不作为当前状态。

- Actual stage: `LOCAL_EFFECT_OPERATOR_CONFIRMED / CANDIDATE_0.1.17_PREPARED / UPLOAD_BLOCKED / NOT_UPLOADED`。
- Authorization: 用户本对话“当前效果OK 上传前端准备发布”，确认当前整体本地效果并授权前端上传；随后“后端也已经授权”明确补充BUG-035两份足迹文件的兼容后端部署授权。全量切流、提交审核、正式发布、提交/推送或修改家庭数据仍按各自范围与门禁处理。
- Scope: 当前已批准前端，包括[BUG-035](../../../specs/completed/BUG-035-TRAVEL-DIARY-END-TO-END.md)、[导入精简](../../../specs/completed/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md)、[入口精简Spec01/Architecture01/DREV01](../../../specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)。用户整体确认不扩张为各Spec全部验收点通过。
- Commit: `0576ac30464908154c624effed41df6dfa3110cc`＋既有工作区修改；前端相对HEAD变化六份footprints文件，和入口精简最终验证清单一致。本轮未改生产代码/测试，其他后端改动保留。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`；服务`flask-ik19`；`useCloud=true / urlCheck=true`。
- Frontend input: `dist/client-release-20261031-0.1.17/project`；168份跟踪源/资源，1233761源码字节；manifest SHA-256 `04c6668a20a0f99622c78424b4d7c5ba07aadc1fd515f20a494e0e4cfcbb2adb`。全部源与冻结副本一致，跟踪图片和此前0.1.16一致，没有新增儿童图片、测试注入或已知秘密模式。源码字节不是编译包体。
- Version: 当前已上传基准仍`0.1.16`；工具计算下一候选`0.1.17`。没有调用upload或bump，不能把候选记为已上传版本。
- Proposed description: 精简旅行日记入口，优化照片导入与核对恢复，修复照片精确回看。

## 初次阻断及证据（历史）

1. **配套后端未交付。** 本次只读版本列表最新为`flask-ik19-038 normal`，服务normal、PUBLIC关闭，流量比例和实际live/ready未验。038的精确发布清单SHA为`80278f7c3a218ca27d995f4523809f9208063278d2d7492ec237a1ecc7290b8b`；其footprints/reads及router没有`focus_photo_id`与`previous_cursor`。当前前端依赖该合同，旧服务会忽略focus参数，不能保证点中的照片就是打开的照片或支持向前分页。按[BUG-035后端先行约束](20261025-travel-diary-e2e-local.md)与[前端发布§2](../FRONTEND-RELEASE.md)，兼容证据不足时停止上传。
2. **上传工具环境失败。** 官方CLI `islogin`退出255，在写用户缓存`Default/.cli`时返回EPERM，没有取得登录状态。此次没有执行依赖它的preview/upload，没有改变系统权限或改用未授权凭据。恢复需在本机终端/微信开发者工具完成官方登录状态和编译核验。
3. **验收按实际范围保留。** 用户整体本地效果已确认；入口精简七态三视口、完整宿主/动作、iOS/Android及可访问性未逐项确认，代理也未采本增量原生证据。新gallery定位读合同触及按照片身份选择数据的路径，适用双账号/非owner云smoke需在配套后端交付后验证；0.1.16的用户双账号确认只保留原范围。

## 初次已完成的检查（历史）

| 检查 | 当前结果 |
|---|---|
| 依赖核对 | PASS；`npm install --ignore-scripts --offline --no-audit --no-fund --cache /private/tmp/push-kids-client-release-20261031-npm-cache` |
| 完整前端 | PASS；349 passed、0 failed、0 skipped |
| ESLint / 小程序源校验 | PASS；17页、1233761源码字节 |
| 全仓架构 / current-policy设计校验 | PASS；4 policies、151 modules；批准设计源/导出未变 |
| 当前前端/冻结包/原已验清单 | PASS；168份源摘要匹配，既有图片不变，无已知秘密模式 |
| 最小后端候选足迹与SQLite规模 | PASS；21 passed、2个MySQL用例明确未执行；测试导入来自候选包，不使用在改的agent_processing源码 |
| 最小后端候选Ruff / format / mypy | PASS；150份Python，mypy保留既有untyped-body note |
| 官方CLI登录状态 | FAIL_ENVIRONMENT；缓存EPERM，exit255 |
| 最小候选完整后端/真实MySQL/容器/云smoke/dry-run | NOT_RUN；这是待授权的独立后端交付，不以21项局部结果代验 |
| 本轮原生三视口/完整动作/设备/读屏/大字体 | NOT_RUN；用户仅确认整体本地效果 |
| preview包体 / upload / 体验版 / 提审 / 正式发布 | NOT_RUN |

[命令及结果](../../quality/evidence/client-release-20261031/checks.json)、[源清单](../../quality/evidence/client-release-20261031/source-manifest.json)、[后端兼容对比](../../quality/evidence/client-release-20261031/backend-compatibility.json)、[云端版本查询](../../quality/evidence/client-release-20261031/cloud-control-plane.json)。

## 已准备的最小兼容后端

候选位于`dist/client-release-20261031-0.1.17/backend-compatibility-candidate`，严格使用已部署038的154份payload，仅替换已批准BUG-035的`apps/api/src/push_kids/footprints/reads.py`和`router.py`；manifest SHA-256为`50a2ea9846fdfe9da13a5ae5b1b7f3ddd0e312d7f72b1961d5c2531060469c62`。测试后payload逐项仍匹配154份清单；生成的Python/Ruff缓存已清理。没有加入当前其他后端改动，未改Schema、依赖、运行配置或流量。该候选具有上述局部验证，尚不具备完整后端发布结论。

2026-10-31用户“后端也已经授权”已满足这两份文件的后端交付授权。继续按[后端手册](../BACKEND-RELEASE.md)补齐精确候选全套/实库/容器/Schema/秘密扫描与dry-run，再创建兼容不可变版本。健康、实际focus/分页、双账号与适用原生验收完成后，从冻结前端做preview/upload；只有上传成功才推进版本基准。全量切流、体验版选择、提审及正式发布继续保留各自人工门禁。补充授权后的执行证据见[兼容后端交付记录](20261031-travel-diary-backend-compatibility.md)。

## 文档、生命周期及回退

同步FEAT-012、Behavior Catalog、Architecture、UI-018/UI-001、设计索引、测试策略、入口精简Spec与Spec索引的当前事实；批准设计资产不变。当前入口精简仍`VERIFYING / specs/completed/FEAT-012-TRAVEL-ENTRY-CLEANUP.md`；三项旅行增量均没有匹配当前源码的云交付，未迁DONE/completed。

本轮未修改运行版本，故没有执行回退。0.1.16是上一已上传候选，当前正式/体验版本没有查询。旧037未出现在本次版本列表，不能在此报告宣称其仍可作为可用回退版本；后续后端交付需重新核对控制台实际流量及可用稳定版本。Schema本次不变，历史038证据为0025，本轮未重新查询Schema。代码/当前文档冲突与链接核对见[闭合检查](../../quality/evidence/client-release-20261031/closure-check.json)。
