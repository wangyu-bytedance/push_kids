# Push Kids Review Policy

- Policy revision: REVIEW-20261028-01
- Approval: [GOV-003 Spec01](specs/completed/GOV-003-TDD-CODING-REVIEW-INCREMENTAL-MERGE.md)，用户2026-10-28“批准 Spec01，按方案合并”。
- Owner: 产品负责人（用户）；获授权实现者协调修复，Reviewer只读。

这是仓库审查规则，单次报告使用 [REVIEW-REPORT](specs/_templates/REVIEW-REPORT.md)。
先读适用AGENTS、本文件、批准Spec、Feature/UI当前状态及相关ISS/REG。
历史任务的Review报告不是模块规则；模块增量须明确声明范围和适用版本。

## 1. Review contract and sensitive paths

本项目的失败包括：未经家长确认创建正式学习/复习记录，AI评分或决定复习日期，
跨家庭/孩子越权，历史回填产生过去Todo债务，数据丢失/重复副作用，无界读取，
泄露凭据/儿童内容，原生交互不可用，以及把未验证/上传状态误写成验收/正式发布。
Review同时发现发布前缺陷，并核对团队能否从仓库理解当前行为和理由。

| 敏感范围 | 主要审查内容 |
|---|---|
| `apps/api/src/push_kids/planning/`、学习确认/记录及建议调用链 | 纯确定性策略、家长确认、发生/创建时间、事务和正式事实边界 |
| 身份/家庭/孩子、媒体、删除、worker及`agent_processing/` | 服务端scope、归档/冻结、输入/模型验证、租约/恢复/取消、隐私 |
| 各domain读取、`apps/api/migrations/`、`tools/`中发布/Schema路径 | 有界查询、MySQL5.7真实兼容、索引/计划、迁移/回滚及平台CPU边界 |
| `apps/miniprogram/`、相关前端测试及设计规范 | 批准Spec+DREV/FEC、状态/竞态/表单、原生三视口、44px触控及真实设备缺口 |
| `docs/`、`specs/`、`AGENTS.md`和本规则 | 当前事实/批准/历史/假设分开，证据版本、文档同步和发布阶段准确 |

排除逐行人工阅读的范围：依赖安装目录和工具缓存、确定生成且源/再生命令可追溯的
产物。锁文件、发布配置、设计批准manifest不因机器生成而免审；仍查来源、哈希和
合同。格式/风格交已有工具，不凭个人偏好要求无关重构。路径Owner沿用架构和Spec。

## 2. Depth and version evidence

| Risk | 深度 |
|---|---|
| R0 | 机械diff及适用自动检查 |
| R1 | 目标行为、调用上下文、边界和相关历史回归；不确定时补独立检查 |
| R2 | 新上下文独立审查边界、契约、数据及测试有效性 |
| R3 | R2加安全/失败分析、发布/恢复证据及适用人工Owner决定 |

风险按实际范围/可逆性/敏感路径判断；Agent不占人工审批名额，不授予合并或发布
权限。绑定具体commit或未提交完整快照（base、路径和内容哈希，含相关untracked）；
新改动需对新增及受影响范围复验，旧批准和EVD不追认新版本。

Reviewer先独立看验收和真实实现，再核对实现者解释；不修改代码或文档。
没有有证据的缺陷时写“0个已确认问题”，同时列出未覆盖范围，不能凑问题。

## 3. Mandatory dimensions and per-file audit

1. 功能正确性：批准Spec、验收/测试点、Feature与实际调用链一致；主/拒绝/边界、
   状态转换、事务、并发、幂等、中断恢复和禁止副作用有对应证据。
2. 设计合理性：抽象/接口、状态归属、依赖方向、扩展和复用符合项目边界；Bugfix
   检查因果链，不接受仅隐藏症状的guard、吞异常或无限重试。
3. 修改必要性：每项回答不改会怎样、为什么必须改这里；检查顺手整理、批量改名、
   无收益重构或额外接口，不能因为看起来整洁就判必要。
4. 放置位置：领域规则不进router/framework文件，一次性逻辑不进shared/common，
   调用方适配不污染核心，不在错误Owner边界下写实现。
5. 冗余与残留：重复规则/转换/配置/测试、死代码、无消费者抽象、旧路径/flag。
   临时共存有Owner、期限与退出条件，删除也须属于批准范围并有证据。
6. 测试有效性：真实路径、可失败断言、独立期望值、首败/重试/skip、Red/Baseline
   版本、重构后行为保持；质量工具状态按测试策略，退出0不等于验收。
7. 文档有效性、正确性、一致性及可理解性：含diff外受影响文档，按第7节核对。

报告逐文件列出路径、add/modify/delete/move、摘要、
necessary/questionable/unnecessary及理由、correct/acceptable/misplaced、冗余/误改。
异常判断须进入finding或剩余风险。结尾分别总结必要/可疑/不应修改/位置不合理的
文件、可安全删除项及哪些正确性结论有证据、哪些仍缺证据。

前端审查完整沿用现有模板章节和 [FEC](docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md)：
HTML、CSS静态检查或隐藏overflow不能代替原生节点/截图和320×568、390×844、430×932
证据；设备、读屏、键盘、大字与真实内容缺项单独记录。可见偏离需新DREV批准。

## 4. Findings and disposition

每条用稳定ID、BLOCKER/MAJOR/MINOR/NOTE、位置、触发条件、预期/实际影响、
证据及验证方法；introduced/pre-existing与严重性分开。先核对调用者和现有防护，
高影响/有争议发现用独立复核或可执行复现确认；怀疑放待验证，不冒称确定缺陷。

处理结论为fixed/false_positive/intentional/deferred，附理由、Owner和证据；延期
需后续任务和复查日期。需跟踪的人工/AI有效发现、验收失败、线上问题及有害误报
进入[ISS](docs/quality/issues/README.md)，格式工具可处理的琐碎意见不逐条建档。

未解决BLOCKER/MAJOR不能获得通过的本地验证/发布结论；风险例外须按既有规则
由指定人工Owner批准。已交付范围仍按GOV-002归档开发DONE，质量缺项和ISS独立
保留，不改成PASS，不追认批准，也不削弱未来发布门禁。

## 5. Re-review convergence

默认最多三轮审查/修复。首轮覆盖完整本次变化及必要上下文；后续聚焦增量、原
finding和受影响调用链，跨边界时扩大范围。稳定ID去重，同类根因检查其他实例；
不重复报告有理由关闭的同一问题，不以评论数或模型投票代替证据。

达到上限保留证据，重审前提/根因/方案，不自动开始第四轮；追加轮次需明确
新假设、范围和预算。共享前提下两次修复失败时优先执行开发协议Failure policy。

## 6. Verification and feedback

真实测试/构建/CI/安全及发布门禁独立有效。本次未接入Git平台保护规则、合并
队列、自动审查、定时回放或自动熔断，不能因本文件存在就宣称已强制执行。
ISS、[REG](docs/quality/regressions/README.md)和版本化EVD按各自契约处理；实际
命令、环境、工具版本、范围/预算、未配置项以[测试策略](docs/quality/TEST-STRATEGY.md)为准。

## 7. Joint document review and human decisions

从变化反查Feature、Behavior、Architecture/ADR、API/Schema、README/运维、规则、
测试说明和关联Spec，包含diff外受影响文档，不要求无关历史全部通读。
报告给出文档/章节、契约/适用版本、代码/测试/运行/批准证据、
aligned/stale/conflicting/missing/ambiguous/not_verified、更新动作和Owner/ISS。
确认链接、命令、术语和当前正文有效；不能只改文字掩盖实现偏差。

可据明确证据确定的错误交获授权实现者修正。有多种合理语义时准备完整来源包，
协调者用[专项ISS模板](docs/quality/issues/DOC-AMBIGUITY-TEMPLATE.md)在当前会话请人工决定：
原/新提交SHA及链接、PR/MR、Spec/revision、提交人和身份依据、两边原文/范围及
代码/测试证据、推荐统一行为/术语/权威文档、拟改代码/测试、必要备选及后果。
文档来源不同另列；未提交给base+完整快照hash，不能只hash漏掉新文件的git diff。

Git author/committer、PR提交人和Spec Owner分别记录；不猜机器人背后的自然人。
缺来源标NOT_FOUND/UNAVAILABLE和查证过程，不能按最新提交自行选语义，也不
因知道提交人就私信/发邮件。待答仅暂停依赖该裁决的部分，不把建议当当前事实。

同一ISS记录裁决人、答复/引用、日期、范围和版本，依次pending→answered→applied→verified。
明确批准具体范围的答复复用授权；新增未批范围更新Spec再确认。获授权实现者应用
到代码/测试/权威正文、同步引用和必要ADR，不倒改历史Spec意图；绑定应用版本
复验文档/契约并复审，关联REG后满足ISS关闭条件才关闭。答复本身不表示完成。
