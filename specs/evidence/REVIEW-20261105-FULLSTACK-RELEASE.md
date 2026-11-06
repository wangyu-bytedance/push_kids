# 当前前后端发布候选独立审查

- Date: 2026-11-05；Risk R3；template：[REVIEW-REPORT](../_templates/REVIEW-REPORT.md)。
- Reviewer: 独立只读`acceptance_review`；本文件由协调者转录其逐文件消息及最终报告，并补充之后实际门禁结果；不伪称Reviewer重跑后续结果。
- Baseline: 039冻结后端与0.1.17冻结客户端；target `dist/fullstack-release-20261105/`，SHA `c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`。
- Verdict: **BLOCK，发布检查未通过**。所查生产代码0新增已确认确定性缺陷；不等于质量、原生或云交付PASS。

## 范围、必要性与放置

后端逐文件审查范围与理由如下；各项均necessary/correct，无已确认顺手改动或错误Owner。156生产源与Spec06最终清单全等，沿用已绑定源码的该轮审查，新增release范围另核。以下花括号展开为逐个同职责理由，不代表审查整个dirty HEAD。

| 文件 | 必要性/放置理由 |
|---|---|
| activities/router.py | warning传输留router，规则不放transport |
| activities/schemas.py | workday mode及互斥合同 |
| activities/service.py | 统一occurrence与旧fingerprint兼容 |
| activities/workday.py | activities-owned纯日历政策 |
| agent_processing/checkpoints.py | 已批准缓存边界 |
| agent_processing/contracts.py | 提案与legacy元数据合同 |
| agent_processing/decision_contracts.py | 现存答案消费者与严格验证 |
| agent_processing/failures.py | 失败分类语义 |
| agent_processing/pipeline.py | 原Pro阶段、来源及结果验证 |
| agent_processing/prompt.py | 已批准来源/候选合同 |
| agent_processing/proposal_acceptance.py | 只提供辅助核对意见 |
| agent_processing/request_limits.py | 实际SDK运输字节预算 |
| agent_processing/stage_contracts.py | 阶段输出Schema |
| agent_processing/stage_provider.py | 原生成及辅助能力接线 |
| agent_processing/system_one_provider.py | Lite协议和资源边界 |
| agent_processing/telemetry.py | 安全分类与预算 |
| agent_processing/worker.py | 有界执行、事务、迟到保护和原子写回 |
| knowledge/maintenance.py | 历史知识修复的领域用例 |
| learning/coverage.py | 旧server-owned覆盖草稿兼容 |
| learning/service.py | 原确认事务及正式事实边界 |
| persistence/models.py | 两workday列及0027索引 |
| platform/config.py | 批准的开关/Provider配置 |
| platform/database.py | 云head0027、本地重启合同 |
| reporting/service.py | dashboard同源warning |
| pyproject.toml | 锁定工作日日历依赖 |
| uv.lock | chinesecalendar1.11.0依赖一致 |
| migrations/versions/20261105_0026_china_workday_schedules.py | 默认false两列，单独迁移交付 |
| migrations/versions/20261105_0027_recent_learning_history.py | 保留批准链及租户领先索引，不恢复旧实验路由 |
| pages/calendar/index.js | 工作日模式/起始日/导航/状态 |
| pages/calendar/index.wxml | 批准表单和状态 |
| pages/calendar/index.wxss | 批准几何 |
| pages/settings/index.js | 三模式/逐星期草稿/转换确认 |
| pages/settings/index.wxml | 批准活动编辑结构 |
| pages/settings/index.wxss | 批准控件及状态几何 |
| pages/today/index.js | 缺覆盖状态且保留已知日程 |
| pages/today/index.wxml | 结果短状态 |
| pages/today/index.wxss | 批准短状态样式 |
| pages/child-edit/index.js | 已批准确认文案，生命周期不改 |
| pages/child-edit/index.wxml | 归档/恢复呈现 |
| pages/child-edit/index.wxss | 14px/整行操作几何 |
| pages/review-inventory/content.wxml | 两宿主共用批准页脚/提示 |
| pages/review-inventory/content.wxss | 局部几何，原JS行为保持 |

前端路径前缀apps/miniprogram；后端包前缀apps/api/src/push_kids；迁移前缀apps/api。Dockerfile/wxcloud.config/config.js/project.config未改，不将旧配置当成本轮云运行实证。独立审查160白名单/168客户端/迁移SHA；无可安全额外删除项。Spec05死路径已由已批准06清退，不在本次恢复。

## Spec、Feature、设计与文档对齐

工作日Spec02/DREV02/03、BUG033 Spec01/DREV01、BUG037 Spec01/DREV01与冻结源一致；相应原生manifest也与源一致。原生节点不能代截图，官方preview不能代原生；设备/可访问性仍未验。Feature及本轮发布记录区分本地/云、原产出/门禁、历史/当前；不把43/45或旧988PASS冒充新门禁。

## Findings与处置

- **RLS-001 / P1，首轮BLOCK，现本地fixed**：首轮Python真实SDK deadline及MySQL stale0025断言已确认。随后用户具体批准OPS01，两行测试修正后988全量、SDK25、MySQL48通过，独立增量Review确认关键保护原样；前后证据分版本保留，不改Worker或迁移迎合错误夹具，不等于完整发布通过。
- **RLS-002 / P1，原v1 BLOCK，v2自动门禁已解除**：原固定40实测37/40、数学/英语不达标FAIL保持。用户随后具体批准材料Spec07，v2唯一补充具体词汇，原评分完整单轮40/40、三科各15/15、零empty/pending/formal；不是生产改进或家长内容PASS，不能追改原37/40。
- **RLS-003 / P1 BLOCK，部分补证**：协调者在解锁/官方重连后补父工作日48＋备注减法24＋归档21＝93组状态节点/PNG。320/390确认框AX/取消及430确认框CUA视觉/取消已观察；App下层图不算modal视觉。320/390目视归档、设备/完整动作仍缺，再次锁屏已请求解锁；FEC不以HTML或preview替代。后48组与430视觉不是Reviewer目视复验，见[阶段03](../../docs/deploy/releases/20261105-fullstack-native-followup.md)。
- **Migration constraint**：旧039严格0025，0027后ready失败；不符合免备份的旧版继续服务条件。迁移前必须有备份、窗口与0027兼容恢复方案。当前未进入生产动作，不冒称已准备可直接使用的旧版回滚点。
- **SQLite issue boundary**：已有四索引漂移仍开放，但新库/0025→0027真实MySQL check均PASS；无证据称生产缺这些索引。保留SQLite修复项，云目标严格Schema检查单列。

## 正确性、架构与测试有效性

所查代码保留家长确认、family/child边界、确定性排期、外部调用事务边界及有界读取。独立额外执行工作日后端16PASS、前端10PASS；不将它们替代整库或云smoke。新40的三个失败均留在分母，未放宽原标签/科目标准；尚无本轮内容逐条人工真值。

SDK字节测试首轮3秒预算阻断字节断言到达，并未证明生产请求字节计算坏了；获批改为30秒后专项/全量已验。旧head断言确实过期，不能回退生产head迎合断言；已按批准更新0027并实库复验。真实MySQL按各文件独立DB，历史失败和恢复因果保持。没有新增框架、模块边界或扩展点。

## 验证证据与剩余范围

首轮事实见[批准前记录](../../docs/deploy/releases/20261105-fullstack-update-preparation.md)及[首轮摘要](fullstack-release-20261105/summary.json)；两行测试修正后的[阶段01](../../docs/deploy/releases/20261105-fullstack-update-ops01.md)和[摘要](fullstack-release-20261105-ops01/summary.json)独立绑定。之后材料Spec07获批，完整v2单轮40/40见[阶段02](../../docs/deploy/releases/20261105-fixed40-v2-verification.md)，原37FAIL不改。原生/设备及生产门禁仍开放；Reviewer只读，没有修复、批准或生产操作，整体发布无PASS。

## 第二轮：批准OPS01后的两行测试增量

独立Reviewer先核对批准Spec、before快照和真实after，再补核SDK整文件25PASS；独立进程只在内存替换Provider进行错误字节偏移及重复原请求注入，两者分别被精确request_bytes和len(sent)==1拒绝。不是修改生产代码制造Red。baseline SHA为`c0c35b5545a8924d69671e775a65d067630cbf30f1f506ad27b3d5a750b090c9`。

| 文件 | 动作 | 必要性、位置及测试有效性 |
|---|---|---|
| tests/unit/test_stage_provider.py | modify，1行3→30秒 | necessary/correct；运输合同不兼任3秒冷SDK性能门槛，仍有界；真实SDK、MockTransport、中文/合成图片、精确字节、单次请求及专门deadline/queue/cancel保护原样。after SHA `ef41dfe0095215346fa2920ecfad8b8e44fb254bf5dda39f533cb0c7364c5e7a` |
| tests/integration/test_supersession_mysql.py | modify，1行0025→0027 | necessary/correct；显式期望绑定批准迁移head，未从实现动态生成期望，守护降级/正式事实/重升级/check/finally销毁原样。after SHA `6763d9635556c61d2f44f9d0dfee0a27296be886572d2fa7f2b32189f2ee1104` |

两行增量0新增已确认代码问题，无冗余/误放/额外删除建议。协调者全量988/56skip与独立MySQL48/0skip实测结果单列在新EVD，不伪称Reviewer重跑MySQL。文档按批准后事实替换待批准/未修正的当前正文，并将首轮失败限定为原轮次。新材料冲突结论与Spec07是本轮诊断事实，尚未改变评分/阈值/生产；当前仍BLOCK，不启动BUG036 Spec06第四轮全面审查。

同轮材料07窄核追加：独立Reviewer确认明确批准、v1 SHA不变、v2逐字段只改multi-04.material；40唯一ID/顺序、36单科＋4多科、30图＋10文和每科预期分母15保持。生产/Prompt/评分/阈值不改，没有新增confirmed finding。新完整40结果与320补证由协调者独立版本化，最终证据/文档增量复核另记，不称Reviewer重跑模型或完整产品验收。

最终材料v2结果/文档窄核已完成：private与安全报告相同，40/40、各科15/15、零operational/empty/pending/formal；mtime验算527.8秒，独立21.071秒样本不替评分。该阶段24项manifest、23份文档SHA及676本地链接均相符；旧OPS01的90项manifest保持。0新增confirmed finding、无必改项，局部证据PASS、整体发布BLOCK。绑定v2 manifest `ffeb1b5d850ca82b31eb2e221923d4dc17eab79f2b02ae60a4e98470c5915ebb`；后续解锁的原生增量另版本化，不把此阶段审查冒充其独立视觉验收。
