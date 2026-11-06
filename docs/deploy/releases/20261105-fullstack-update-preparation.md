# 2026-11-05 — 当前前后端发布检查与打包

- Stage: `PREPARED_LOCAL / RELEASE_GATE_FAILED / NOT_UPLOADED`。
- Record scope: 本文保留OPS批准前的检查轮次；批准后两行测试维护及988/48回归、原生补证见[最新续验](20261105-fullstack-update-ops01.md)。下表987/1FAIL等为原轮次，不代表修正后仍失败；原40质量FAIL则保持有效。
- User authorization: 本聊天“好的，检查本地的服务端和客户端的代码，打包上传 更新”。已完成检查及可逆准备；因真实必需门禁FAIL而停止上传，未迁移生产数据库、未创建新GRAY、未切流、未upload或bump、未Git提交/推送。
- Follow-up Spec: [OPS Spec01 / Architecture01](../../../specs/completed/OPS-20261105-FULLSTACK-UPDATE.md)在本准备阶段为READY_FOR_REVIEW，随后用户具体批准并完成测试维护；当前BLOCKED/active，原质量和剩余原生门禁未通过。功能和DREV批准保持，不追认未展示的新生产变更。
- Source: HEAD `0576ac30464908154c624effed41df6dfa3110cc`＋已列明工作区差异；不是HEAD全部变更直接上传。
- Frozen candidate: `dist/fullstack-release-20261105/`。manifest SHA256 `c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`。
- Backend: 160白名单文件，1,607,791字节；156份Python生产源与Spec06最终source-manifest逐字节相同。无.env/测试/前端/文档/图片/数据库。
- Client: 168文件，1,244,228源字节；相对0.1.17只有calendar/settings/today各三文件、child-edit三文件、review-inventory两文件，共14份变化。新候选未上传。
- Official preview: PASS，1,200,319字节；不代表upload、体验版、审核或正式发布。工具登录有效，AppID/环境/服务与发布手册一致。
- Current cloud: 本轮只读version/service:list为039 normal、服务normal、PUBLIC关闭；MySQL只读事务确认`20261024_0025`且无workday_only列。客户端基准仍0.1.17，未读取后台体验/正式版本，不虚构其状态。

## 实际门禁结果

| 检查 | 本轮结果 |
|---|---|
| Python全量 | **FAIL：987PASS、56条件SKIP、1FAIL**；`test_request_bytes_match_real_sdk_transport_body`触发local_deadline；隔离再执行仍FAIL。原988PASS是Spec06早先对象验证记录，不替代本次发布检查 |
| 前端/ESLint | **359PASS**、0skip；ESLint PASS |
| Ruff/format/mypy | PASS；962文件格式、156生产模块类型；保留既有未检查无类型函数note |
| 架构/设计政策/小程序/diff | PASS；5策略/156模块DAG，17页/1,244,228源字节 |
| MySQL5.7 Schema | PASS：5.7.44新库base→0027、0025→0027，两条upgrade/current/check均无新operations；测试数据隔离，未访问生产业务 |
| MySQL并发/权限/规模 | 首轮33PASS/9FAIL/3ERROR/3SKIP：私有harness没有满足独立库与迁移合同；第二轮按文件独立迁移为46PASS/1FAIL/1ERROR，FAIL是旧head断言，ERROR为today基库未创建；harness修正后today第三轮1PASS。十个文件按最终独立对象合计47PASS/1FAIL；[安全检查摘要](../../../specs/evidence/fullstack-release-20261105/summary.json)保留全部轮次，不称一次全套PASS，也不覆盖默认56skip的全部其他可选测试 |
| 当前fixed40 live Ark | **FAIL：37/40＝92.5%**；语文14/15＝93.3%、数学13/15＝86.7%、英语12/15＝80%。原顺序/模型/评分/重试政策；40例全部在分母，empty/pending/formal为0 |
| 本轮fixed40产物与失败 | 按评分合同38份非空产物，其中1份科目不全；2份原Pro review1拒绝。产物38/40不等于门禁37/40；没有基础设施失败，没有为了验收重新生成或删除有效产物 |
| 先前真实材料回放 | Spec06同15材料×3轮，开启43/45、关闭42/45、验收0丢弃仍为该独立样本事实；不是当前fixed40得分、线上率或人工内容合格率 |
| Docker | 本地test模式合同PASS：UID10001、8000、live/ready200、SIGTERM后exit0；镜像`sha256:826aa9df11b3cb524448f350218f3f778598239447768181e90b99817e6b9d67`。首试development+test Provider被正确拒绝，私有harness改为test后再验，未改产品 |
| 最小白名单/dryrun | PASS：CLI派生zip510,614字节，161文件＝160白名单＋manifest，源字节一致，无嵌套旧包或秘密；SHA `f07c96ac468db772f9140a979da6bfc6e73854c3e843cdfd4746a72d240e4279`。派生.temp zip已移到私有证据，防止后续打包混入；未部署 |
| 原生三视口/实际动作 | PARTIAL：既有有效节点/部分PNG保持；BUG033/工作日截图仍缺，本轮320切换、RPC超时及官方auto重连后连接失败。没有用preview或HTML弥补 |
| 独立Review | 发布结论BLOCK；所查生产增量0新增已确认确定性代码bug，工作日独立后端16/前端10PASS；测试/固定40/原生门禁仍阻断。见[报告](../../../specs/evidence/REVIEW-20261105-FULLSTACK-RELEASE.md) |
| 生产迁移/严格Schema/新版本smoke/流量/upload | NOT_RUN；本轮没有生产修改，不声称生产0027或新版本已可用 |

固定40失败为multi-02（review1 vague_name）、en-08（review1 unsupported_by_evidence）、multi-04（subject.mismatch）。原评分报告只保留短case、静态码与计数，不存儿童原图、原输入或模型payload。不能据此断言某个通用Prompt机制已被确定定位；下一步诊断须保留原失败，不能随机重跑取最好或降低标准。

## 迁移、恢复及下一步

039严格要求0025，因此升到0027后其ready失败，不能作为直接回滚版本。本次不满足后端手册§4.2“旧版仍可服务”的免新增备份条件；未来发布必须先确认备份、受控窗口与理解workday字段的0027恢复方案。仅有增量DDL不能自动免除这个合同。

目前停止点是本地必需检查FAIL，并未到生产备份或最终切流人工门禁；不提前要求管理员改运行秘密、切流、选体验版或备份清理。新测试维护与诊断方案由OPS Spec01审阅，原生证据和实际质量门禁全部通过后才进入后续发布。所有秘密继续留在批准的运行配置，不向聊天索取。

SQLite四索引[ISS](../../quality/issues/ISS-20261105-LEARNING-RECORD-INDEX-DRIFT.md)保持未修。本次真实MySQL两路径无漂移，仅限定影响判断，不将SQLite问题resolved，也不冒称已核生产MySQL完整索引合同。

## 文档与生命周期

本准备轮次没有生产或测试源码修改；随后获批OPS续验的两行测试变更、当前文档状态和实际证据另记，不倒改本轮失败。Architecture/Behavior/API/FEC合同不变，批准设计源和manifest不改。未交付功能仍VERIFYING/active，OPS目前BLOCKED/active，无新增DONE。后端039与客户端0.1.17继续是最近已确认交付版本。

收尾检查：15份相关文档的本地链接目标、Spec目录141份（completed109/active13/rejected19）及`git diff --check`通过，准确数量见[文档闭合摘要](../../../specs/evidence/fullstack-release-20261105/documentation-closure.json)。没有把检查范围之外的设备、内容或云端验收记为通过。
