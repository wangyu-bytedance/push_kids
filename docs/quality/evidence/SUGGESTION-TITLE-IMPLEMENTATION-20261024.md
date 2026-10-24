# 学习建议标题约束 — 实现与验收

- Date / State: 2026-10-24 / LOCAL_IMPLEMENTATION / VERIFYING / DEFAULT_OFF / NOT_RELEASED。
- Approval: 用户针对call_39aaa3dd3cdf4a52b2bfc9c4d862ee58回复「批准，按此实现」，明确批准[Spec01 / Architecture01](../../../specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md)及[DREV04](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/FRONTEND-SPEC.md)，先记录批准再修改生产源码。
- Baseline: main / `82ca52775bc948f2a963a8f4ed614322d8859de8`，共享未提交工作区。相关文件此前即未跟踪，git diff不包含其全部变化；[设计阶段7份SHA](SUGGESTION-TITLE-DESIGN-20261024.md)与[最终21份源码SHA](suggestion-title-20261024/implementation-source-manifest.json)界定本次版本，不将其他任务修改归属本标题任务。

新生成和家长重新编辑标题为trim后1–20个Unicode码点，无内部CR/LF/U+2028/U+2029；非BMP按1。prompt建议6–16字，活动动作/对象放标题，步骤和理由放原独立字段。统一合同位于agent_processing，Provider输出和持久化前再验证、PATCH Edit共用；非法模型结果沿既有最多3次有界尝试，不新增模型修复调用。

编辑显示n/20及14px字段错误，超限保留草稿且零PATCH，保存触发标题聚焦；排队聚焦在孩子/scope/页面失效后不生效。保留原maxlength=120作为输入防护及旧提案编辑承载，20才是有效保存上限。网络失败保留草稿与幂等键，成功后的新操作使用新键。服务端无效PATCH422，JSON/version及任务/正式事实不变。

旧21–120字提案/已批准待学完整读取、审批、实际记录/删除继续兼容，不迁移、不静默裁切或重写；超过60字沿用既有30vh完整标题滚动。只有重新编辑保存时须家长精简。正式知识名、实际学习、资格/额度/预算、默认flag、查询/数据库结构和权限不变。

## 实际检查

| 检查 | 结果与边界 |
|---|---|
| 修改前新增回归 | 后端选中20项：11失败/9通过（32未选）；前端新增4项均失败，复现21字/换行/未验证实例被接受、无计数/字段错误等缺口 |
| `.venv/bin/python -m pytest tests/unit/test_today_learning_policy.py tests/integration/test_learning_suggestions.py -q` | PASS，52项；边界、非法输出/编辑零写入、旧120读取/编辑/审批/记录/删除、Job最多3次失败 |
| `node --test tests/frontend/today-learning.test.js` | PASS，最终18项（独立复核实际重跑）；计数/trim/非BMP/无效零请求、完整旧编辑、失败/等待/幂等、排队focus失效 |
| `.venv/bin/python -m pytest tests/unit tests/integration tests/contract -q` | PASS，780通过/40跳过/108 warnings，129.64s，退出0；日志/private/tmp/push-kids-suggestion-title-backend.log。跳过均属未配置隔离MySQL或其repeatable-read/migration环境，不能算MySQL验收 |
| 可选数据库跳过审计（8个MySQL文件及test_review_fairness.py，`-q -rs`） | PASS，6通过/40跳过，1.28s；明确skip原因，日志/private/tmp/push-kids-suggestion-title-optional.log，不借用其他任务数据库结果 |
| `npm test` / `npm run lint:miniapp` | PASS，最终332/0失败/0跳过，ESLint退出0；日志/private/tmp/push-kids-suggestion-title-frontend.log。全量含共享工作区其他任务用例，不能全归属标题改动 |
| `.venv/bin/python -m ruff check .` / `ruff format --check .` | PASS，731文件格式正确 |
| `.venv/bin/python -m mypy apps/api/src` | PASS，150个源文件；既有未类型化函数体提示不作为新增问题 |
| `tools/check_architecture.py` | PASS，4政策、150模块runtime/lazy DAG |
| `tools/validate_miniprogram.py` | PASS，17页、源码预算1,221,025字节，低于1.5MiB；不是上传包体，无新增依赖/图片/请求/计时器 |
| DREV04批准清单/current-policy、DREV01/02/03各自清单 | PASS，DREV04源/33PNG及旧78/84/63PNG SHA保持有效，无allow-pending |
| DREV04设计原型 | 批准前设计阶段33导出/21交互通过；历史结果独立留存，不代验生产原生 |
| `node --check tools/today_learning_geometry.js` / `git diff --check` | PASS |
| 320×568、390×844、430×932原生 | PASS，每视口13态，共39份PNG/节点；[目录说明](suggestion-title-20261024/native/README.md)与[核验清单](suggestion-title-20261024/native/verification-manifest.json)绑定14源码、3共享样式和截图SHA；默认字体/基础库3.17.4 |
| 独立只读复核 | PASS，fresh-context reviewer，CR-001测试覆盖已修复并复核关闭，详见下节 |
| 真实iOS/Android、实际软键盘/读屏/系统大字体 | NOT_RUN，本机合成模拟器无法替代；TP-007尚未完成 |
| 真实模型/真实家庭数据/线上API | NOT_RUN，本次未调用付费模型或操作真实学习数据；不把mock/旧样本写成新模型质量验收 |
| 上传/体验/审核/正式发布 | NOT_RUN，未请求、未执行；原开关默认false，无数据库迁移 |

原生13态含短/20字提案、20字卡片、默认/20/21/空/旧120/失败/保存/非BMP编辑、旧120提案及实际长标题滚动。20字中文正常字体小屏两行完整展示，字体及主次按钮延续DREV02/03；错误贴近输入，不依赖省略、缩字或隐藏溢出。已目视核对320最大新标题、390超限编辑、430旧长标题。合成副本拒绝业务写入；几何取证不等同真实键盘、HTTP或数据库提交，后两者由专项测试分别验证。

## 独立复核与文件必要性

依据R2 fresh-context复核要求，由独立只读reviewer检查7个生产文件、3个测试文件及原生runner，运行专项后端52/前端17通过。初次结论PASS WITH NON-BLOCKS，无生产正确性/架构/历史兼容阻断。

CR-001（P2/non-block）发现失败重试测试始终返回fixture-key，同键断言不能识别错误清缓存。实现者改用递增key并断言失败重试只生成1次、成功后新操作生成第2个不同key；另补延迟nextTick在reset/hide后不恢复focus。独立reviewer重跑前端18通过，纯内存变异模拟失败后清commandKeys时，测试因edit-key-1与edit-key-2不等而失败，确认断言有效；最终CR-001关闭、Gate PASS。reviewer未改文件或操作桌面。

| 文件组 | 必要性/所有权结论 |
|---|---|
| suggestion_contracts.py / suggestion_provider.py | 原输出合同owner增加唯一标题约束；原prompt及TestProvider遵守同合同，无新provider扩展点 |
| learning_suggestions/schemas.py / generation.py | 原Edit消费者及提交前守卫，已有suggestions→agent_processing边复用，无反向依赖 |
| today-learning/index.js / index.wxml / index.wxss | 原表单即时计数/错误/焦点及样式；无新组件或并行状态机 |
| unit/integration/frontend三个测试文件 | 每层独立边界、HTTP/DB零写入与历史兼容、用户操作/迟到/幂等有实际断言 |
| today_learning_geometry.js | 复用原有官方原生取证路径，增加标题节点/真实edit与field夹具及必要几何断言；prepare工具未修改 |

## 文档核对与生命周期

已同步FEAT004 revision07、BHV045、Architecture合同owner/消费者、UI001 title04、Frontend Design、主Spec04的当前DTO正文、Title Limit Spec、测试策略、发布记录与Spec索引。新写入20与旧120兼容分清；历史设计阶段SHA/旧自动化数字保留明确时点，不冒充当前结果。旧DREV02只追加本标题范围Superseded by，其余批准源/PNG/清单冻结。架构约束/FEC/数据库结构逐项核对，无新增偏离或迁移；没有通过追加说明掩盖相反的当前DTO正文。

最终复算39份PNG/节点SHA、21份实现与测试源码、3份共享样式均匹配；15份收尾文档的223个本地链接目标存在，Spec仅在active/VERIFYING，git diff --check通过。前序卡片/弹层Spec已加明确标题增量引用和历史120字边界；无本次代码与当前正文冲突。

Spec最终位置为`specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md`、VERIFYING，completed无同名副本。尚缺TP-007代表iOS/Android、实际软键盘/读屏/大字体验收，取得环境后继续；当前无需新增设计批准。主功能及卡片其他开放门禁不被本次独立标题复核覆盖。没有提交、推送、上传、部署、生产写入或开关修改。
