# BUG-036 缓存 Spec02 — 最终验收报告

最新批准后发布阶段：`BLOCKED_PRE_DEPLOY_QUALITY_GATE`。用户“批准 OPS 发布 Spec01，开始灰度部署”后，
完成获批工具维护、其他静态及运行Schema检查，冻结10/13固定40例实际34/40和三科低于90%FAIL，
正式写0；因此未创建GRAY，仍039/100%。[门禁EVD](../../../specs/evidence/EVD-20261101-BUG036-CACHE02-RELEASE-GATE.md)与[停止记录](../../deploy/releases/20261101-knowledge-cache-gray-blocked.md)保留6case及恢复条件。
下方17:21报告的静态FAIL/9源“当前”一致等措辞限定原核验时点；活动源已是独立12/15，
该旧源只作为冻结10/13证据，不追认新源。工具静态FAIL已在获批范围修复，新40caseFAIL不能被旧结果替代。

- Report revision: `ACCEPTANCE-20261101-BUG036-CACHE02-01`
- 用户本轮要求：“将状态更新为已部署，并生成最终验收报告”。
- 当前结论：缓存机制本地验收PASS；部署状态`NOT_VERIFIED`；整体验收PARTIAL。不得据旧版本或期望状态写成新缓存已部署。
- Spec / architecture: [缓存Spec02](../../../specs/completed/BUG-036-CHECKPOINT-RETRY-STRATEGY.md)，`BUG-SPEC-20261101-KNOWLEDGE-CACHE-02` / `ARCH-20261101-KNOWLEDGE-CACHE-02`。
- 当前源码：`staged-20261101-10` / `child-aware-history-agent-20261031-13`，9份代码/测试与[最终源清单](../../../specs/evidence/bug036-cache-20261101/source-manifest.json)一致；本轮没有新生产代码修改或重复部署。
- [可浏览最终报告](../../../output/bug036-cache02-final-acceptance/bug036-cache02-final-acceptance.html)及[云端/源码核验JSON](../../../output/bug036-cache02-final-acceptance/assets/acceptance-evidence.json)包含具体时点。

## 云端交付核验（原17:21报告时点）

本轮真实运行官方`wxcloud version:list -e prod-d2g14rwoycac6b45d -s flask-ik19`、
`wxcloud service:list -e prod-d2g14rwoycac6b45d`，均exit0。
返回的最新版本为`flask-ik19-039`，创建于2026-10-31 19:15:02，19:18:08更新，状态normal；
服务normal、PUBLIC关闭。未重查流量比例，未读取容器内部runtime revision或执行缓存云smoke。

039已有冻结发布包的pipeline为`staged-20261031-06`。本轮按其manifest逐项核验源码，
当前缓存Spec02五份生产源均与该包不同，039不覆盖10/13。本轮未找到对应的新不可变版本、
冻结发布包/镜像摘要和正常部署对应关系。因此保留`VERIFYING`于`specs/active/`，
部署核验状态明确更新为`NOT_VERIFIED`，不迁completed、不写DONE或“已部署”。
这限定于当前CLI返回及已有发布材料，不伪称已直接读取云容器源码。

## 验收矩阵（原17:21报告时点；最新发布门禁见上方）

| 维度 | 实际结果 | 证据及边界 |
|---|---|---|
| 终态缓存、明确retry、首审恢复 | PASS | TP-C01–05；最终拒绝不缓存/不自动重试，家长retry刷新语义分支保留有效提取 |
| 专项 / 全量后端 | PASS_WITH_SKIPS | 已运行116专项、857全量PASS/52默认外部条件skip；当前9文件SHA仍一致，本报告未重复行为测试 |
| 实际MySQL5.7 | PASS | 8专项/0skip；独占utf8mb4库、迁移head及Schema检查、并发/锁/rollback/租户/Worker；结束销毁 |
| 独立Review | PASS_AFTER_FIX | 0确认代码缺陷，1项P2文档计数错误fixed，0未解决发现；原报告和修正保留 |
| 本任务静态 | PASS | 9代码/测试Ruff/format、mypy151、架构4/151原对象证据 |
| 全库Ruff / format | FAIL | 本次真实重查：两范围外文件7项E501、1个并行证据脚本需格式化；不追认旧832份formatPASS |
| 原三份内容09/13 | COMPLETE_WITH_FAILURES | 六图/2产出/1内容PASS/1FAIL/1NO_OUTPUT，61表一致；名称长度、拼音归类/教学角色反证保留 |
| 新10/13内容 / 云业务 | NOT_RUN | 原三份内容不代表10/13验收；live40、灰度/实际家长retry及发布观察未验 |
| 缓存Spec云交付 | NOT_VERIFIED | 当前039源为06；缺匹配10/13版本及摘要证据 |

上述测试实际原结果、首败、固定源与限制见[实现EVD](../../../specs/evidence/EVD-20261101-BUG036-CACHE02.md)。
本报告生成/本次云读取与静态重查是新证据，不把旧运行重复写成当前执行。
前端UI/DREV/FEC/原生设备验证N/A：本缓存Spec没有前端改动。

## 后续恢复条件

若由其他操作者部署，补充非敏感不可变版本号/发布记录，核对该版本normal及覆盖10/13的
五份源SHA或镜像/发布包摘要。匹配范围云交付后按GOV-002开发DONE迁completed，剩余内容、
设备、灰度smoke与全库检查保持真实结果。若尚未部署，按既有发布流程完成适用门禁后部署；
不能仅将状态文字改为“已部署”。

本轮没有部署/切流/生产数据重置/迁移/正式确认/Git提交。
密钥、OpenID和数据库URL不作为聊天或报告附件。API/Schema/排期/家长确认合同及旧验收失败保持。
已同步Spec部署核验字段、Feature/Behavior/Architecture当前交付说明、测试策略、发布记录及索引。

## 报告文件检查

自包含HTML含本地字体、ECharts、Mermaid和纯文本/JSON来源附件；33项HTML相对资源/证据链接存在，
9份状态/事实文档本地链接核对通过。浏览器桥接工具已确认图表与流程图DOM渲染，
但桥接窗口viewport不可用，未将截图失败当作布局通过。
随后使用本机Google Chrome独立headless浏览器真实渲染1280×900与390×844，
均无页面横向溢出、JavaScript错误或请求失败；6章节、7项来源与图表/流程图实际渲染通过。
此处为验收报告网页检查，不是微信小程序原生视口、真机、内容或生产业务验收。
[报告渲染检查](../../../output/bug036-cache02-final-acceptance/assets/render-check.json)保留环境和实际结果。
