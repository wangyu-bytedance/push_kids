# OPS缓存灰度发布Spec01 — 批准后门禁结果

- Evidence revision: `EVD-20261101-BUG036-CACHE02-RELEASE-GATE`
- Approved Spec: [OPS-SPEC-20261101-BUG036-CACHE-DEPLOY-01](../active/OPS-20261101-BUG036-CACHE02-DEPLOYMENT.md)。
- User approval: 2026-11-01当前会话“批准 OPS 发布 Spec01，开始灰度部署”，包括两份工具维护及适用门禁通过后GRAY创建；未授权跳过质量门禁、全量切流、秘密改写或生产重置。
- Subject: 冻结`staged-20261101-10` / `child-aware-history-agent-20261031-13`，154payload / 150Python源；
  [candidate manifest](../../docs/quality/evidence/bug036-cache02-release-20261101/candidate-manifest.json) SHA
  `a07c0bf32a85afa80c1d69485d0c7d203dca663dddf10cd26f2c88c5c68f612b`。
- result: failed — 发布必需固定40-case模型质量门禁FAIL，停止创建实际灰度版本；不是缓存机制回归失败。
- Stage: `BLOCKED_PRE_DEPLOY_QUALITY_GATE`。生产仍039，实际新版本号不存在，流量未修改。

## 必需模型门禁 — 实际失败

冻结验证树执行原`tools/evaluate_analysis_quality.py --provider staged
--cases tests/fixtures/analysis_quality/cases.json --report <private>`。
密钥从已批准本地安全配置注入子进程环境，不放命令参数/日志。原固定40合成case、规定顺序及材料、
最多3次持久Job attempts均保持；未读写生产DB。隔离SQLite/图片随临时目录退出清理，
报告只保存case ID、静态代码、次数及汇总。未重复抽样或换模型以覆盖失败。

- Run: 2026-11-01 18:30:31–18:37:37，北京时间；exit1。
- 实际34/40通过＝85%；要求≥38/40＝95%。
- 语文10/15＝66.67%、数学12/15＝80%、英语13/15＝86.67%；各科要求≥90%，多科case参与相关科目分母。
- operational failure count0；全部失败仍在端到端分母，不能按基础设施排除。
- empty pending0、remaining pending0、formal writes0。
- [完整固定分类报告](../../docs/quality/evidence/bug036-cache02-release-20261101/live40-report.json)、
  [实际运行元数据](../../docs/quality/evidence/bug036-cache02-release-20261101/live40-run.json)和安全日志保留。

| Case ID | 静态失败码 | Attempts |
|---|---|---:|
| multi-01 | analysis_output_invalid | 3 |
| zh-05 | analysis_output_invalid | 3 |
| multi-02 | subject.mismatch | 1 |
| zh-07 | analysis_output_invalid | 3 |
| zh-09 | analysis_output_invalid | 3 |
| multi-04 | analysis_output_invalid | 3 |

原三份/30份09内容报告是另一批素材，不能与本次40相加、互替或重标通过。
本次证据是冻结10/13的发布质量，不代验独立内容Spec03活动11/14。

## 工具维护及其他门禁

两份已批准工具只改变Python格式及JS token间换行，AST（按嵌入JS空白规范化）等价、
JS引号内容保持、前后`node --check`通过；未执行原生复制脚本或改批准设计快照。
变更前7项E501保留；变更后全库RuffPASS、format865文件PASS。
工具probe首次误用系统Python3.9的zip(strict)发生TypeError，改用项目Python3.12后通过；
不把probe环境错误算产品Red。

| Check | Result / actual scope |
|---|---|
| 冻结候选完整后端 | 857PASS/52默认外部条件skip；已准备精确源SHA匹配，不重复冒称新全量 |
| Worker/作用域/云媒体claim等专项 | 63PASS；入口首次使用不存在文件exit4，修正为实际测试入口后真实通过，未改断言 |
| 当前前端 | 349PASS，0fail/0skip；ESLintPASS，设计current-policy PASS，小程序17页校验PASS；无前端上传 |
| 当前工作区类型/DAG/head | mypy151PASS，架构4policy/151PASS，唯一head0025；活动11/14结果与冻结候选分别记录 |
| 管理员严格只读Schema | PASS，0025，verify_triggers=true |
| 实际039运行账号/冻结候选Schema | PASS，0025/SELECT1，SHOW GRANTS未检测DDL；账户变量仅进私有子进程，不持久化 |
| 控制平面 | 039normal/100%/1，PUBLIC关闭，OA+MINIAPP；端口8000、0.25CPU/0.5GiB、min0/max5保持未改，run_worker=true |
| 独占MySQL候选 | 新utf8mb4库迁移/current/check与8缓存事务专项PASS，已销毁；不冒充生产业务写入 |
| Docker | 本机arm64缓存匹配后已开始依赖下载；质量FAIL后停止本任务构建，NOT_RUN_INCOMPLETE，无容器健康/SIGTERM结果，不声称PASS。前次metadata超时和未完成构建保留 |
| 实际GRAY创建/云新版本/定向健康 | NOT_RUN：质量门禁失败后停止，无部署成功或新版本号 |

依赖同步已执行；npm install实际审计6项（5moderate/1high），未自动运行破坏性audit修复或改依赖。
这是依赖工具输出，不变成质量通过或自动授权额外依赖升级。

两组独立只读Review各0确认代码/工具/包来源问题；154payload/10批准替换/144保留039核验，
明确NOT_READY，不把质量FAIL、容器未验或配置资源差异当已通过。039资源0.25CPU/0.5GiB/min0/max5
与发布手册基线不同且worker=true；后续若继续发布仍需适用人工配置核验，当前质量FAIL已在该步骤前停止。
发布包组建议包括可选coverage总预算与后台共存风险核验，不能用18/33核心调用省略可选阶段；
本轮fixed40环境显式coverage=false，只证明所声明核心生成范围，不代完整后台云验收。
独立报告保留各自原Spec快照/status和时点，不倒改为审查时已BLOCKED。最终cross为0代码/包缺陷、
2项P2文档问题：报告更新期间manifest摘要漂移、TP-R03仍称旧全库lint阻断。
已将当前结果同步为获批修复PASS、质量FAIL保持，并在所有报告/附件更新完成后重新生成和核验manifest；
原2项发现不删除或重标误报。[审查](../../docs/quality/evidence/bug036-cache02-release-20261101/review/report.html)
与[处置](../../docs/quality/evidence/bug036-cache02-release-20261101/review/disposition.md)区分静态发现和实际NOT_READY。

## 状态、恢复与文档闭合

OPS设`BLOCKED`留`specs/active/`，缓存/生成/独立内容Spec均未由本任务云交付；
不标已部署、不迁DONE。后续修复必须在对应内容/质量的具体批准范围验证，重新冻结发布revision，
并完整重跑适用门禁；不能把当前活动11/14替入旧10/13候选，不能跳过本次失败。
全量流量/配置/主体等人工门禁保持，本轮无秘密修改、生产重置、迁移或Git提交。

原始批准、旧失败和当前FAIL分别保留。发布记录、Spec测试点/索引、Feature/Behavior/Architecture、
测试策略与最终验收报告按本次实际门禁结果同步，机械链接/hash复核不代替独立代码/内容验收。
