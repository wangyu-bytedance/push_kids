# BUG-036 — 固定40评测材料与证据规则对齐

- Status: DONE

## 2026-11-06 开发完成与独立验收

- Development completed: 2026-11-06；依据已批准GOV-002的匹配云交付规则，迁入`specs/completed/`。
- Release authorization: 用户已批准OPS Spec01、确认本次备份/受控窗口，并明确“无需灰度账号，直接发布”（原话“不用配置 直接发布”）。原任务本地实施授权与后续发布授权分别保留。
- Delivered scope: 已批准v2材料唯一补充与单轮40/40验证完成，关联OPS的040与0.1.18交付完成；原37/40 FAIL不改。
- Source / stages: HEAD`0576ac30464908154c624effed41df6dfa3110cc`＋批准差异，冻结manifest SHA`c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`；后端040 normal/100%、Schema0027，客户端0.1.18开发上传1,200,417字节。
- Acceptance: 已执行范围见[发布报告](../../docs/deploy/releases/20261106-fullstack-040-client-0.1.18.md)和[新EVD](../evidence/EVD-20261106-FULLSTACK-DELIVERY.md)。家长内容PENDING、线上生成成功率NOT_MEASURED、设备/可访问性及其余业务验收缺项保留原状态；开发DONE不等于完整验收PASS。尚未设体验版、提审或正式发布。备份保留数量因站点安全策略阻断NOT_RUN。
- Closure: Feature/Behavior/Architecture/UI/测试策略/发布入口与索引按实际交付同步；批准设计源、历史失败和各阶段manifest保持。

## 原批准设计与实施时点记录

> 以下保留原修订、各历史运行及当时的“本地/未交付/VERIFYING”结论，不作为当前开发状态；当前交付以上节及新EVD为准，原验收失败不追改。
- Risk: R1，仅评测材料；不改变产品生成、人工确认或发布阈值。
- Spec revision: `BUG036-SPEC-20261105-FIXED40-MATERIAL-07`
- Architecture revision: N/A，生产源码、模块、依赖、Schema和扩展点均不变。
- Created / Last updated: 2026-11-05
- Approval: APPROVED，批准人为用户，2026-11-05回复具体审批问题“批准固定40材料 Spec07”，questionItemId `call_f219e47f25d04eddbc39f0e707193871/0`；批准本修订的v2单条材料补充、原评分完整单轮与证据闭合，不改变生产或阈值。OPS Spec01本身仍只涵盖先前诊断/两行测试维护。
- Feature baseline: FEAT-001 `FEAT-STATE-20261105-SYSTEM-ONE-14`；[当前状态](../../docs/domain/features/FEAT-001-push-kids-mvp.md)。
- Discovery: [OPS续验](../../docs/deploy/releases/20261105-fullstack-update-ops01.md)、[ISS](../../docs/quality/issues/ISS-20261105-FIXED40-SUBJECT-TRUTH.md)。

## 目标与非目标

原固定40的multi-04期待语文、数学、英语三科，但英语材料只给主题而没有具体词汇。批准的共同规则明确禁止用主题猜词表。一次诊断中原流程保留两科、以indeterminate_object省略英语，随后被科目齐全评分拒绝。这是评测材料与三科覆盖目标的冲突，不能靠产品补造英语内容解决。

推荐新增版本化40条材料，仅将multi-04英语改为明确给出三个学习词汇：`英语练习 school objects 词汇 pen、book、ruler。` 语文/数学部分不变。原40文件及其37/40 FAIL报告保持不可变；新材料仍40条、原顺序、36单科/4多科、每科15计数及图片分布不变。新结果独立报告，不将两版本差异称为生产成功率提升。

不更改生产代码、Prompt、Pro硬复审、System One辅助验收、重试/预算、评分实现、95%整体及90%每科阈值；不把诊断两条复跑通过替换原失败，不使用多轮择优。家长内容质量仍独立验收。

## 设计与取舍

| 方案 | 判断 |
|---|---|
| 推荐：新增材料v2，只补multi-04已明确要考查的具体英语词汇 | 保持三科覆盖目标及各科分母；输入变更透明，新旧报告不可直接声称生成改进 |
| 将原multi-04预期改成两科 | 符合该原材料的证据边界，但改变各科分母/三科测试目标；本修订不采用 |
| 让模型在只有主题时猜词，或降低整体/每科标准 | 违反证据/质量合同，不采用 |
| 重跑原40直至偶然通过 | 没有实现或材料修正，不能证明已修复，不采用 |

Link/call graph：`原40不可变对照 → v2材料及唯一差异/SHA → 原evaluate_analysis_quality.py → 原Worker/Pro/System One → 独立40条完整报告 → 内容/原生/发布门禁`。
Sequence：N/A，现有评测调用时序不变，只更换经批准的输入文件。
State machine：N/A，不改变生产/Job状态；结果仍passed/failed/not_run，不能混并旧分数。
Architecture：N/A，无模块/依赖/扩展点变更，沿用原Provider/Worker分层。
Frontend impact / Frontend engineering impact：均no；无客户端或工具链修改，新DREV N/A。

## 预期文件与验证

| 文件/对象 | 动作及理由 |
|---|---|
| `tests/fixtures/analysis_quality/cases-20261105-v2.json` | 新增可追溯40条版本，仅multi-04英语词汇差异；旧文件保持 |
| `specs/evidence/`及发布/Feature/测试策略/ISS | 记录v1/v2各自对象/SHA/结果，不伪造历史通过 |
| 生产、客户端、迁移、`tools/evaluate_analysis_quality.py`、原40文件 | 不修改 |

| TP | 必需验证 |
|---|---|
| Q01 | 逐条diff确认只有multi-04 material变化；旧40 SHA不变，40唯一ID、顺序/分科/输入类型/图片比例不变；记录生产/评分/Prompt SHA相同 |
| Q02 | 原校验器和原命令对v2只执行一轮完整40：整体至少38/40、每科至少90%、0empty/pending/formal；全部40留分母，失败不择优替换 |
| Q03 | 三个词汇无新增输入之外的含义，生成结果表供家长review，不输出原图/原输入；自动科目PASS不代表内容合格 |
| Q04 | 独立只读Review确认不是降低门槛；对原multi-04正确保留两科/省略英语的诊断记录保持，不追改v1统计 |
| Q05 | 仅所有适用门禁通过后恢复OPS受控发布；备份、窗口、0027兼容恢复、灰度smoke及人工流量门禁继续执行 |

2026-11-05实施状态：批准后新增v2文件；Q01独立逐字段核对PASS，仅multi-04.material补三个具体词汇，40条ID/顺序、36单科＋4多科、30图＋10文、各科分母15均不变。原文件SHA为`9bdaec483fa9f6cc65e7a46c3656e70f2304efd42ecab3fe362864afa8fd829f`。Q02完整单轮40/40、三科各15/15、零empty/pending/formal，PASS，约527.8秒。Q03另取一次21.071秒的三科输出样本，英语仅所给三个词汇，结果表供家长review，内容PENDING，不替换评分。Q04独立材料及最终结果/证据窄核PASS，0新增confirmed finding，绑定该阶段manifest `ffeb1b5d850ca82b31eb2e221923d4dc17eab79f2b02ae60a4e98470c5915ebb`；Q05因适用原生与生产人工门禁未齐，尚未恢复发布。见[本阶段EVD](../evidence/EVD-20261105-FIXED40-V2.md)。

完成条件：先完成材料与单轮评测，记录本地实施/验收结果；按仓库规则核对关联OPS匹配云交付后再判断DONE归档，未交付保持active。任何生产改动必须另有具体批准，不能用本修订扩展。
