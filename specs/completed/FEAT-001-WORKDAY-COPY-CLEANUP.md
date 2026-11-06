# FEAT-001 — 工作日备注减法与通用文案约束（Spec Lite）

- Status: DONE

## 2026-11-06 开发完成与独立验收

- Development completed: 2026-11-06；依据已批准GOV-002的匹配云交付规则，迁入`specs/completed/`。
- Release authorization: 用户已批准OPS Spec01、确认本次备份/受控窗口，并明确“无需灰度账号，直接发布”（原话“不用配置 直接发布”）。原任务本地实施授权与后续发布授权分别保留。
- Delivered scope: 两处表单备注减法及结果短状态由0.1.18交付；三视口24状态证据保持，未配置自动日期更新任务。
- Source / stages: HEAD`0576ac30464908154c624effed41df6dfa3110cc`＋批准差异，冻结manifest SHA`c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`；后端040 normal/100%、Schema0027，客户端0.1.18开发上传1,200,417字节。
- Acceptance: 已执行范围见[发布报告](../../docs/deploy/releases/20261106-fullstack-040-client-0.1.18.md)和[新EVD](../evidence/EVD-20261106-FULLSTACK-DELIVERY.md)。家长内容PENDING、线上生成成功率NOT_MEASURED、设备/可访问性及其余业务验收缺项保留原状态；开发DONE不等于完整验收PASS。尚未设体验版、提审或正式发布。备份保留数量因站点安全策略阻断NOT_RUN。
- Closure: Feature/Behavior/Architecture/UI/测试策略/发布入口与索引按实际交付同步；批准设计源、历史失败和各阶段manifest保持。

## 原批准设计与实施时点记录

> 以下保留原修订、各历史运行及当时的“本地/未交付/VERIFYING”结论，不作为当前开发状态；当前交付以上节及新EVD为准，原验收失败不追改。
- Risk: `R1`，仅既有前端呈现与通用文案规范；API、日期政策、数据与架构不变。
- Owner: 产品负责人（用户）
- Implementer: Codex
- Reviewer: pending；作者自查不计独立Review
- Date: 2026-11-05
- Spec revision: `SPEC-20261105-WORKDAY-COPY-01`
- User confirmation: `APPROVED`；产品负责人于2026-11-05回复本Spec01+DREV03异步审批问题：“批准此修订并实施”（questionItemId `call_b33a200d66ca498db6f7498b57980aa7/0`）。批准包含删除稿及通用规范增补，不含数据更新任务或发布；编码前已记录。
- Affected Feature IDs: `FEAT-001`，通知规则不改，FEAT-003实现N/A。
- Feature current-state document: `docs/domain/features/FEAT-001-push-kids-mvp.md`
- Feature baseline revision: `FEAT-STATE-20261105-WORKDAY-02`
- Feature merge owner: Codex，仅合并验证后的本地事实；父工作日Spec仍VERIFYING/active。

## Frontend Design Impact and Repository-native Approval

- Frontend impact: `yes`，删除设置/日程表单的规则说明和覆盖说明卡，真实缺覆盖结果只留一次短状态。
- Frontend engineering impact: `yes`，清除重复呈现及无消费者状态/样式，补强既有通用文案要求。
- Affected UI IDs: `UI-001`
- UI current-state document: `docs/design/frontend/ui/UI-001-parent-miniapp.md`
- Frontend baseline revision: approved `FDB-20260913-04`
- Frontend engineering constraint revision: approved `FEC-20261007-NATIVE-GEOMETRY-02`
- Affected quality dimensions: content/state/form/a11y/native geometry/performance；无新网络、依赖、存储或权限。
- Budgets: 320×568 / 390×844 / 430×932；44px热区、14px正文、初始源预算1.5MiB；删除后收紧布局，不能用字号或hidden overflow掩盖问题。
- Current Design Revision: `DREV-20261105-WORKDAY-02`（源与批准导出冻结）。
- Approved Design Revision: `DREV-20261105-WORKDAY-03`
- Editable source: `docs/design/frontend/prototypes/DREV-20261105-WORKDAY-03/index.html`
- Design source SHA-256: 见同名`APPROVAL.md`生成清单。
- Required exports: 8个受影响状态×3精确视口，共24张HTML设计导出；其余模式沿用DREV02。
- Prototype status: `APPROVED`，编辑源与24张导出冻结。
- Approved Task Spec revision / Design Revision: `SPEC-20261105-WORKDAY-COPY-01 / DREV-20261105-WORKDAY-03`
- Approval evidence: 2026-11-05上述异步问题答复“批准此修订并实施”。
- Snapshot manifest: `docs/design/frontend/snapshots/UI-001/DREV-20261105-WORKDAY-03/APPROVAL.md`
- Permitted deviations: none；通用色彩、控件/时间规则和授权合同不改。
- External design dependency: none。

## 1. Problem and outcome

用户截图同时显示“按中国大陆法定安排，放假跳过，调休照常”和“工作日数据待更新：当前仅覆盖至2026年，超出范围的安排暂不显示，也不会发送提醒”。前者重复工作日选项语义，后者把维护年份与系统后果展开成长备注，并在结果和表单重复出现。

目标：编辑表单聚焦模式和时间；实际缺数据只在受影响结果表达一次短状态。将“删除过度防御说明、禁止把维护责任写给用户、状态只表达一次”写进既有通用文案正文。

## 2. Scope

- 设置活动安排、日程新建/编辑：删除固定工作日说明卡与覆盖说明卡，不移入帮助或折叠备注。
- 日程结果：正常年份没有备注；确有缺覆盖时，只有一次“工作日安排待更新”，与其他已有日程可并存，不能显示“整周为空”的确定结论。
- 今日活动：确有缺覆盖时，由该分区状态表达“工作日安排待更新”，移除同义长警告和重复空态；学习首次引导仍独立。
- 通用文档：补强`FRONTEND-DESIGN.md`“界面文案与减法”；FEC引用同一规则，不复制长清单。用户明确偏好作为来源，本条增量不放宽44px/14px/原生验收合同。
- 数据更新方式只做本轮Discovery答复与研究记录，不实施定时任务、自动PR或数据热更新。
- 保持：真实未知状态、后端不猜测2027规则、放假/调休判定、旧星期不同时间、viewer和保存失败恢复；不改API、Schema、权限、提醒或云发布。

Current-state merge：实施后替换UI001与Feature001有关长规则说明/覆盖警告卡的当前正文，保留父Spec02与EVD历史事实，更新本Spec状态和索引；获批DREV02只加本范围Superseded by指针。

已按批准范围合并通用文档正文：将既有“实现细节/预先辩护”条补强为“不把 AI 的思考、实现细节、后台流程、内部约束、维护年份、开发/验收说明或假想后果写成常驻备注；这些内容由设计与运维文档承担”。将既有“一次表达”条补强为“同一实际异常只在受影响位置表达一次；表单能正常编辑时，不插入结果区已有的数据维护说明”。既有必要授权、删除直接后果与真实错误恢复规则继续有效。FEC仅引用同一条通用规则，不再复制一份长清单。

## 3. Impact map and design views

```text
设置/日程编辑 → 原三模式及时间控件 → 删除两种备注卡
schedule/dashboard warning metadata → 原有缺覆盖判断 → 唯一短状态
FRONTEND-DESIGN文案规则 → FEC引用 → 本次及未来设计/审查
```

Sequence：`服务端返回原warning → 页面派生真实状态 → 结果区一次呈现；编辑表单只呈现字段`。无新请求或副作用，时序图N/A。

State machine：`covered → 正常内容 / unknown-with-items → 原内容+一次短状态 / unknown-empty → 短状态且不宣称空日`；只读/保存中/错误状态保持，非新业务状态机。

Architecture diagram：N/A，仍为API→既有Page→WXML/WXSS；模块边界、共享抽象和依赖方向不变。

| 方案 | 收益 | 代价 | 决定 |
|---|---|---|---|
| 删表单备注，真实未知结果一次短状态 | 简洁且不误导 | 需要同步所有显示位置 | 推荐 |
| 完全隐藏真实未知，显示没有安排 | 少文字 | 用户会把缺数据误认为无日程 | 拒绝 |
| 移到问号/折叠长文/继续列年份后果 | 复用原文 | 没有解决冗余说明 | 拒绝 |

## 4. Expected files and deletion plan

| 路径 | 动作 | 目的 |
|---|---|---|
| `pages/settings/index.{js,wxml,wxss}` | modify | 删除无消费者的warning映射/卡片/规则样式，保留模式与时间摘要 |
| `pages/calendar/index.{js,wxml,wxss}` | modify | 删除编辑备注；结果一次短状态，复用原有warning缓存 |
| `pages/today/index.{js,wxml,wxss}` | modify | 状态短文案与空态去重，覆盖判断保持，短状态14px沿用既有token |
| `docs/design/frontend/FRONTEND-DESIGN.md` / `FRONTEND-ENGINEERING-CONSTRAINTS.md` | modify | 通用约束正文与引用 |
| UI001 / Feature001 / Behavior / Spec/index / EVD / 本地发布记录 | modify/add | 最终事实与版本证据；旧证据不可重写 |
| DREV03 source / exports / manifest | add | 可审阅的删除后效果与精确SHA |
| `docs/research/china-workday/20261105-automatic-updates.md` | add | 上游/官方核验与自动化选项，明确未实施 |
| `tools/prepare_workday_native.py` / `tools/workday_geometry.js` | modify | 既有离线验收工具支持独立输出、8态短状态检查和序列化夹具；不进入产品代码 |

不新增运行时组件、API、依赖或共享文案工具。自动化测试优先复用父Spec的语义与状态验证；这是低风险可逆文案减法，不新增逐字镜像测试。旧assert仅在语义合同变化时调整，不为绕过测试改实现。

## 5. Acceptance and required test points

| AC/TP | 验证 | 所需证据 |
|---|---|---|
| AC/TP-001 | 两编辑表单没有这两种备注卡，也没有空占位容器 | 代码残留搜索＋DREV03三视口导出＋原生检查 |
| AC/TP-002 | 实际缺覆盖仍一次可见，原日程保留，unknown不等于empty | 既有warning/day-cache/Today状态测试及渲染 |
| AC/TP-003 | 模式、保存回填、逐日草稿、viewer/错误恢复保持 | `npm test`、`npm run lint:miniapp` |
| AC/TP-004 | 通用文档禁止防御说明堆积，当前正文与设计一致 | 新旧正文差异、引用/源SHA校验 |
| AC/TP-005 | 删除后没有空白卡/溢出/关键操作裁切，44px/14px下限保持 | 320/390/430设计与原生节点/实际观察；未执行项保留NOT_RUN |
| AC/TP-006 | 上游版本/年份核验和自动化建议真实，不声称已配置 | 官方/PyPI/holiday-cn源链接；不写入虚构2027/2028日期 |

附加命令：`uv run python tools/validate_miniprogram.py`、`uv run python tools/validate_design_evidence.py --check-current-policy`、`git diff --check`。后端未改，不重复全量Python或迁移测试。

## 6. Plan, verification and completion

1. 生成DREV03源、24导出和SHA，提供本Spec01与DREV03的具体审批；保留原源。
2. 获批后实施上述删除、清除无消费者内容并运行适用检查；未取得批准前不改生产界面或现行通用规范正文。
3. 合并已验证的Feature/UI/Behavior/设计规则和版本证据；本地无云交付留VERIFYING/active，不设DONE。

当前：用户批准后已本地实施，版本化结果见[EVD](../evidence/EVD-20261105-WORKDAY-COPY-01.md)与[证据目录](../../docs/quality/evidence/workday-copy-20261105/README.md)。采用诚实Baseline分支：改前既有专项10PASS，改后专项10PASS、全前端359PASS及lint/小程序/设计/架构检查通过；没有把可逆文案清理包装成Red。后端与迁移未改，本轮不重复Python全量，不将父Spec02的919/48记为本轮结果。

| TP | 当前结果 | 范围与缺项 |
|---|---|---|
| 001 | PASS_LOCAL | 两表单备注及空容器删除，原生三尺寸节点、390八态截图与源码核对 |
| 002 | PASS_LOCAL | 既有warning/cache/Today状态测试通过；未知一次表达，已知日程保留，无重复空态 |
| 003 | PASS_AUTOMATED | 专项10、全前端359通过；模式、回填、不同时间草稿、只读与错误恢复测试保持 |
| 004 | PASS_LOCAL | FDB正文/FEC引用、Feature/UI/Behavior当前事实已同步；批准源与24设计导出冻结 |
| 005 | PARTIAL | 原轮次24组节点PASS、390八张PNG及320/430截图超时保持历史；后续OPS批准续验补齐三视口24组节点/PNG并观察，真机/读屏和其他动作未验 |
| 006 | PASS_RESEARCH | 官方/PyPI/holiday-cn核验与建议已记录；未配置自动更新或虚构后续年份 |

历史设计渲染首次`uv run python .../render.py`因无Playwright失败，改用本机已有Playwright的`python3`完成24张导出，未变更依赖。原生验收曾连接旧项目、遇跨realm夹具不渲染与容器字号误判；失败工件均保留，修正验收工具后最终节点24组通过，不计这些失败为生产Red。320截图重试实际仍为430视口而失败，另存不覆盖最终320节点证据；不得用该次截图或HTML代替原生完整验收。

代码与文档冲突按实际增量核对，无本任务未记录冲突。作者自查不计独立Review。后续[OPS续验](../../docs/deploy/releases/20261105-fullstack-update-ops01.md)已用同源完整候选官方preview并补三视口24组PNG，设备/读屏、其他动作及完整独立视觉验收仍未完成；无后端部署/小程序上传/体验/审核/正式发布，继续VERIFYING/active。隔离MySQL两迁移路径已由OPS核对，生产0025及未来备份/迁移/恢复门禁仍独立。
