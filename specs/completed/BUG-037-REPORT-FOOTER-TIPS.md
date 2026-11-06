# BUG-037 — 编辑计划页脚与删除提示对齐（Spec Lite）

- Status: DONE

## 2026-11-06 开发完成与独立验收

- Development completed: 2026-11-06；依据已批准GOV-002的匹配云交付规则，迁入`specs/completed/`。
- Release authorization: 用户已批准OPS Spec01、确认本次备份/受控窗口，并明确“无需灰度账号，直接发布”（原话“不用配置 直接发布”）。原任务本地实施授权与后续发布授权分别保留。
- Delivered scope: 共享Flex分页及提示区由0.1.18交付；原三视口双宿主144组证据保持。
- Source / stages: HEAD`0576ac30464908154c624effed41df6dfa3110cc`＋批准差异，冻结manifest SHA`c96b30d102d2fff317865040bd8b65c419bbb1374689199c41bcebcd0b157f60`；后端040 normal/100%、Schema0027，客户端0.1.18开发上传1,200,417字节。
- Acceptance: 已执行范围见[发布报告](../../docs/deploy/releases/20261106-fullstack-040-client-0.1.18.md)和[新EVD](../evidence/EVD-20261106-FULLSTACK-DELIVERY.md)。家长内容PENDING、线上生成成功率NOT_MEASURED、设备/可访问性及其余业务验收缺项保留原状态；开发DONE不等于完整验收PASS。尚未设体验版、提审或正式发布。备份保留数量因站点安全策略阻断NOT_RUN。
- Closure: Feature/Behavior/Architecture/UI/测试策略/发布入口与索引按实际交付同步；批准设计源、历史失败和各阶段manifest保持。

## 原批准设计与实施时点记录

> 以下保留原修订、各历史运行及当时的“本地/未交付/VERIFYING”结论，不作为当前开发状态；当前交付以上节及新EVD为准，原验收失败不追改。
- Risk: R1
- Severity: 局部视觉错位，分页可用性和提示可读性受影响
- Owner: 用户（产品负责人）
- Implementer: GPT-6
- Reviewer: 按R1实际diff核对共享边界、批准合同、证据和文档；未执行独立通用代码审查
- Date: 2026-11-01
- Spec revision: BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- User confirmation: 用户2026-11-01本会话回复“批准 Spec01 + DREV01”，批准BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01及DREV-20261101-REPORT-FOOTER-TIPS-01
- Affected Feature IDs: FEAT-001
- Feature current-state documents: docs/domain/features/FEAT-001-push-kids-mvp.md
- Feature baseline revision: 当前工作区2026-10-31状态；分页基线SPEC-20261014-ACTION-PAGER-CONSISTENCY-02
- Feature merge owner: GPT-6，实施验证后合并

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes
- Frontend impact reason: 分页按钮、页码与操作结果提示可见几何调整
- Frontend engineering impact: yes
- Frontend engineering impact reason: 共享WXML/WXSS、原生几何兼容和通用类冲突修复
- Affected UI IDs: UI-001
- UI current-state documents: docs/design/frontend/ui/UI-001-parent-miniapp.md
- Frontend baseline revision: FDB-20260913-04（APPROVED）
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02（APPROVED）
- Affected frontend quality dimensions: component/state/responsive/a11y/browser/performance/security/privacy/observability
- Frontend quality budgets/requirements: FEC原生三视口几何；44px热区/14px正文；FEC-PERF-READ-001..004保持；包≤1.5MiB；无敏感日志
- Frontend quality verification plan: TP-001..006
- Approved frontend engineering deviations: none
- Current Design Revision(s): DREV-20261014-ACTION-PAGER-CONSISTENCY-02；DREV-20261013-REPORT-PANELS-01
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/index.html
- Design source SHA-256: cbc393766dc06c42bae3771849a9bf7f915ae93173d62a0ba8de0a74de0d33ff
- Proposed Design Revision: DREV-20261101-REPORT-FOOTER-TIPS-01
- Required viewport/state exports: 两宿主×九态×320×568/390×844/430×932，共54张
- Prototype status: APPROVED
- Approved Task Spec revision: BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- Approved Design Revision: DREV-20261101-REPORT-FOOTER-TIPS-01
- Design approval evidence: 用户2026-11-01本会话“批准 Spec01 + DREV01”；批准源SHA与54张导出保持不变
- Snapshot manifest path: docs/design/frontend/snapshots/UI-001/DREV-20261101-REPORT-FOOTER-TIPS-01/APPROVAL.md
- Permitted implementation deviations: 无可见偏差；HTML标签映射到WXML，像素几何以原生验收为准
- UI current-state merge owner: GPT-6
- UI current-state merge evidence: UI-STATE-20261101-REPORT-FOOTER-TIPS-03-NATIVE；当前分页/提示正文已同步，旧Grid标为历史；docs/quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md
- Frontend visual/a11y/resolution verification: 批准54张PNG/SHA保持；原基线320/390双宿主20组JSON/PNG；齐套03两宿主三视口144组节点/PNG/解码/SHA PASS；实际触摸/设备/大字/读屏仍PARTIAL或NOT_RUN
- Frontend engineering verification evidence: 前端349/ESLint/小程序/架构/manifest/current-policy PASS；原430双宿主16组方法/状态/尾部检查PASS；恢复02官方preview1192127字节PASS，未上传
- External design dependency: none

## 1. 问题与预期

用户2026-11-01提供两张942×2048截图：报表“编辑计划”底部“下一页”落到独立一行，
禁用按钮呈白色大块；第二张删除结果“条目和相关复习历史、计划已删除”紧贴暖色色块左缘。
预期分页一排、等宽按钮与居中页码；提示有明确内边距、文本左对齐且垂直居中，长句完整换行。

证据：

- 用户原图：`20261101-153001.jpg`、`20261101-153009.jpg`，保留在上传附件路径，不写入仓库。
- `components/review-inventory/index.js`使用`styleIsolation: "apply-shared"`，两入口引用同一`content.wxml/content.wxss`。
- 全局`app.wxss .notice`定义暖色容器和左右padding；共享`content.wxss .notice, .readonly`
  又定义`padding: 12px 0`，可确认左右padding被覆盖，且直接在`text`上叠加容器语义。
- 共享分页已有三列Grid；历史证据仅部分验证430独立页，明确内嵌/320/390未验。
  截图证实视觉异常，故障运行版本及Grid/样式隔离机制NEEDS_VERIFICATION：TP-001采集原生和版本。

## 2. 范围与事实合并

- 修改共享编辑计划的条目分页、科目目录分页、结果/预算提示结构及样式。
- 包含报表内嵌和独立入口，覆盖三个筛选方式及当前已有状态。
- 页脚在本Spec中指列表分页与“收起编辑计划”区域；全局五Tab不改，若用户指全局Tab应另修订。
- 不改文案、删除/改期范围、API、分页游标、排序、家庭/孩子隔离、只读权限、规划策略或后端。
- 无数据修复、迁移、状态新增、依赖或共享抽象变更。
- 合并FEAT-001与UI-001现有“固定三列Grid”正文为验证后的Flex事实，保留历史证据与未验状态。
  Behavior Catalog BHV-033与Architecture核对后，如业务和边界确实无变化则不改正文，记录核对结果。
- 变更引用：BUG-037 / Spec01 / DREV01；旧批准快照不改，批准后仅添加精确Superseded by指针。

## 3. 影响图

```text
报表pages/reports → components/review-inventory ─┐
独立pages/review-inventory ────────────────────┤
                                             ↓
                     pages/review-inventory/content.wxml + content.wxss
                          ↓ tokens / controller（后两者保持）
```

- 现有测试：tests/frontend/review-inventory.test.js、review-inventory-geometry.test.js、
  report-panel-geometry.test.js，以及npm test。
- 架构图：N/A，沿用上述已有依赖方向，不增加模块、抽象、跨域调用或部署边界。
- Sequence diagram：N/A，仅替换渲染结构；查询/动作/刷新时序无变化。
- State machine：N/A，首页/末页/加载/操作成功/只读均消费现有data，不引入状态迁移。

## 4. 方案与取舍

| 方案 | 收益 | 成本/风险 | 选择 |
|---|---|---|---|
| 共享分页明确Flex，提示专用容器与文本 | 两宿主统一；左右等宽；隔离通用类；不依赖Grid轨道 | 需补两宿主原生矩阵，不能据HTML认定修复 | 推荐 |
| 保持Grid，仅补覆盖和padding | 修改行数少 | 截图分页仍需证明运行机制，不能排除Grid/宿主差异 | 不选 |
| 全面重做底部Tab与报表卡片 | 更广泛视觉调整 | 超出截图问题，引入导航和设计回归 | 不选 |

具体布局由[前端合同](../../docs/design/frontend/prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/FRONTEND-SPEC.md)定义。
分页Flex不换行、左右`flex: 1 1 0; width: 0`、中央64px与两侧8px；
禁用透明底/细描边；提示专用view+text，12px×16px padding、14px/1.5文字。
消除旧`.notice`局部覆盖并迁移两个消费者，`.readonly`独立保留；无平行V2路径。

## 5. 预期文件与删除计划

| 文件 | 操作 | 目的 |
|---|---|---|
| apps/miniprogram/pages/review-inventory/content.wxml | modify，批准后 | 两处提示包裹容器；按钮与标签延用现有绑定 |
| apps/miniprogram/pages/review-inventory/content.wxss | modify，批准后 | 分页Flex、禁用和文字居中；专用提示几何；移除旧通用.notice覆盖 |
| docs/domain/features/FEAT-001-push-kids-mvp.md、docs/design/frontend/ui/UI-001-parent-miniapp.md | modify，实施后 | 替换冲突的当前分页描述并记录实际证据 |
| docs/design/frontend/prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/ | add，本阶段 | 可编辑修改稿与合同 |
| docs/design/frontend/snapshots/UI-001/DREV-20261101-REPORT-FOOTER-TIPS-01/ | add，本阶段 | 54张导出、SHA、浏览器设计审核结果 |
| 本Spec、specs/STATUS.md | add/modify | 单次需求与待批准入口 |
| docs/quality/evidence/REPORT-FOOTER-TIPS-20261101.md、docs/deploy/releases/20261101-report-footer-tips-local.md | add，实施后 | 本次源码、测试、原生与实际交付阶段 |
| specs/evidence/EVD-20261101-BUG037-BASELINE.md、EVD-20261101-BUG037-FINAL.md | add，证据闭合 | 按现行工程模板分别绑定改前/改后对象，引用上述详细证据，不扩展生产范围 |

权威路径保持共享content；不新增生产组件/JS，不改全局样式。
发布按docs/deploy/README.md，独立记录preview/upload/体验/审核/生产；未经对应端交付不标DONE。
回退仅撤回本Spec两个生产文件的具体增量，保留并行改动；无需数据回滚。

## 6. 验收

- AC-001：两个入口三个视口，首页/中间/末页/加载的分页同排、按钮等宽且≥44px、文字≥14px，
  页码居中、两侧≥8px；禁用无白色大块。长页码仅中央折行，科目目录两列等宽。
- AC-002：删除和预算结果单行/多行均在色块内，左/右16px、上/下12px内边距，
  文字左对齐、单行垂直居中、无裁切；操作成功继续礼貌播报，失败不出现假成功。
- AC-003：时间/科目/次数筛选、只读、下一页替换、迟到响应、失败保留和删除后刷新仍符合现有合同。
  操作菜单、内容尾部与五Tab无遮挡；文字放大可读。

## 7. 必需测试点与当前结果

| Test point | 检查 | 命令/方法 | 当前结果 |
|---|---|---|---|
| TP-001 | 原故障原生基线及版本 | 两宿主×320/390/430分页、提示节点/截图；合成只读fixture | PARTIAL，320/390共20组JSON/PNG，基础库3.16.2；提示padding=0复现，分页掉行未复现；430基线缺失 |
| TP-002 | 候选设计导出与SHA | 54张PNG、design-audit.json；`uv run python tools/validate_design_evidence.py --allow-pending --manifest docs/design/frontend/snapshots/UI-001/DREV-20261101-REPORT-FOOTER-TIPS-01/APPROVAL.md` | PASS，54组Chromium几何/截图、源/导出SHA匹配；非原生验收 |
| TP-003 | 现有行为回归/静态 | `npm test`、`npm run lint:miniapp`、`uv run python tools/validate_miniprogram.py` | PASS，349项/ESLint/17页校验；源码资源1,234,665字节，非上传包体 |
| TP-004 | 修复原生矩阵 | DREV工程验证要求中的两宿主×三视口×相关筛选/状态节点与截图 | PASS，齐套03两宿主×320/390/430×24态共144组JSON/PNG，几何/解码/SHA通过；默认字体合成原生范围，设备另验 |
| TP-005 | 原生操作与可访问性 | 合成读数据测试首页/下一页/加载拒重入/失败保留、只读；iOS/Android及文字放大、读屏 | PARTIAL，原430双宿主16组方法/状态/尾部PASS；官方preview1192127成功及无线真机码已准备；手机未扫码，实际触摸/设备/大字/读屏NOT_RUN，未真实删除 |
| TP-006 | 架构与设计政策/文档闭合 | `uv run python tools/check_architecture.py`、`uv run python tools/validate_design_evidence.py --check-current-policy`；代码/Feature/Behavior/UI/Spec/发布正文一致核对 | PASS，架构/批准manifest/current-policy及diff检查；Feature/UI/设计/Spec/索引/证据/发布正文已同步，Behavior/Architecture合同无冲突 |

不为可逆样式修改新增逐字/逐CSS镜像单测；布局故障用真实渲染/原生矩形作前后证据，现有行为测试验证回归。

## 8. 实施计划

1. 用户批准具体Spec01 + DREV01，冻结匹配SHA与批准记录。
2. TP-001先保留真实基线；异常未重现则记录实际版本/条件，不能将猜测称为根因。
3. 修改两个权威共享文件；删除通用.notice覆盖，替换Grid分页，执行TP-003与TP-004。
4. 完成TP-005/006并合并当前文档；任何未执行项记录原因/风险。
5. 按后续授权执行发布门禁；对应客户端成功上传才按AGENTS.md开发DONE归档，独立保留验收缺项。

## 9. 当前闭合状态

2026-11-01用户已批准具体Spec01 + DREV01，批准源SHA与54张导出冻结。
两个权威共享文件已按批准范围本地实现；前端349项和静态/架构/设计政策检查通过。
原生基线320/390双宿主20组，提示贴边已复现；原430双宿主48态节点与16组方法/状态/尾部检查PASS。
用户随后要求修复截图工具并补真机：恢复02先补390/430双宿主96组JSON/PNG，320当时因机型/锁屏未完成。
用户本轮“已经解锁”后真实320×568已恢复并补48组，齐套03共144组节点/PNG/解码/SHA PASS。
分页掉行在基线未复现，不宣称Grid兼容根因已确认；真实触摸/设备/大字/读屏仍缺，整体验收PARTIAL。
已准备168份冻结生产源加本Spec两份替换的官方preview，1192127字节成功、二维码已生成；
桌面已解锁；官方无线真机调试码已生成，手机尚未扫码，设备/触摸取证仍待完成。
独立生产debug副本本地语音插件41002失败，固定基础库后仍失败，不宣称插件已修复；
扫码码为官方Tool.enableRemoteDebug返回，二维码准备不等于设备已连接。
当前Feature/UI冲突正文、设计索引、重叠范围Superseded by与测试/发布证据已闭合；
Behavior/Architecture/测试策略核对没有业务、依赖或预算冲突。
本轮未commit/push/upload；新preview不等于upload，0.1.17冻结上传包不覆盖这两份修改。
Spec为VERIFYING，位于specs/active/：本地实施完成但验收/云交付未齐，不标DONE。
当前恢复条件见[齐套03证据](../../docs/quality/evidence/REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)；
[原实施01证据](../../docs/quality/evidence/REPORT-FOOTER-TIPS-20261101.md)保留当时缺项，
后续覆盖本增量的客户端成功上传后再按规则DONE/completed，验收缺项独立记录。
2026-11-01设计验证：`python3 /tmp/push-kids-footer-design-20261101/render.py`生成54张PNG，
design-audit.json记录54组几何检查，0失败/0浏览器错误/0外部请求。
人工视觉读取390删除提示与320长页码两张代表图；设计证据`--allow-pending`和当前政策检查均PASS。
该结果仅证明候选HTML设计，不证明生产WXML、微信原生、真实设备或上传版本。
工作区存在并行发布和知识生成修改，已保留；本Spec仅有两份生产目标文件的批准增量。
