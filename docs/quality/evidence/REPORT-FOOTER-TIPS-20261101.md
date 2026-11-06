# BUG-037 — 编辑计划页脚与提示实施证据

这是实施01当时记录，原失败/NOT_RUN不改写。后续[恢复02](REPORT-FOOTER-TIPS-SCREENSHOT-RECOVERY-20261101.md)
及当前[齐套03](REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)已补三视口144组PNG/节点；真机等待扫码。

- Evidence revision: REPORT-FOOTER-TIPS-20261101-01
- Task: [Spec01](../../../specs/completed/BUG-037-REPORT-FOOTER-TIPS.md)，BUG-SPEC-20261101-REPORT-FOOTER-TIPS-01
- Design: [DREV01合同](../../design/frontend/prototypes/DREV-20261101-REPORT-FOOTER-TIPS-01/FRONTEND-SPEC.md)
- Approval: 用户2026-11-01本会话“批准 Spec01 + DREV01”
- Overall acceptance: PARTIAL；本地实施完成，三视口原生/截图及设备验收未齐
- Delivery: LOCAL_ONLY；本增量不在已上传的0.1.17冻结包中

## 实际修改与来源

仅修改共享`pages/review-inventory/content.wxml`和`content.wxss`。条目分页改为Flex，
按钮等宽、最小44px、14px文字，中央64px页码与两侧8px间距；科目分页复用同一按钮。
禁用保留透明底、细描边和几何。操作结果与预算提示改为专用view/text，
水平16px、垂直12px内边距，14px/21px行高、左对齐、单行垂直居中。
删除文案、`aria-live="polite"`、只读文本、controller、API和五Tab保持原合同。

| 文件 | 基线SHA-256 | 实施SHA-256 |
|---|---|---|
| content.wxml | 3a3ecd9e51a8dedc692ae1361cbe230b4f3a2cc054f7caf939d052330563f933 | c481d7021d56095123378d2d368c022c3d77cfdaf13374d35a3ffb75c7587e72 |
| content.wxss | e64d7736ad8644ceb2f14109072a56fdd0760d9814e49ccf98960d16f3d7cfe7 | 390bf6fa08c65729639bd027bc4aa402043df9c4b39c002d8688bfe77bd21e11 |
| controller.js | 73fae9064a6544479f071c2ffd779b3ecde80ddd6c0b71a1a70f27948cd1e89e | 相同，无修改 |

完整来源与证据SHA见[来源清单](report-footer-tips-20261101/source-manifest.json)。
隔离项目使用真实生产WXML/WXSS/controller；仅配置与API替换为合成只读数据。
未执行真实删除、改期或业务数据写入，未采集家庭身份、图片、密钥或模型原文。
微信开发者工具2.01.2510290、基础库3.16.2；实际系统宽度与screenHeight逐例校验，没有mock视口或替换样式。

## Baseline分支与故障边界

提示修复的预期Red差异是旧节点水平padding=0、不满足批准的16px；
分页先保存Baseline，未重现掉行，不制造失败或将工具错误算Red。
可逆样式增量不新增逐CSS镜像单测；先保存原生几何/截图，再改权威共享文件，
改后执行已有行为回归349项。按工程模板记录的
[基线EVD](../../../specs/evidence/EVD-20261101-BUG037-BASELINE.md)与
[实施EVD](../../../specs/evidence/EVD-20261101-BUG037-FINAL.md)分别绑定改前/改后对象。

- `baseline/{embedded,standalone}/{320,390}`：每组5态，共20组JSON/PNG。
  实际`wx.getSystemInfoSync()`分别为320×568与390×844；windowHeight另受原生导航/Tab区域影响。
- 基线删除提示的computedStyle明确`paddingLeft/Right: 0px`、字号13px。
  [390报表内嵌原图](report-footer-tips-20261101/baseline/embedded/390/subject-deleted.png)
  可见文字紧贴色块左缘，与用户第二张截图一致。局部`.notice`覆盖全局padding是可证实原因。
- 时间/科目/次数的基线分页未重现掉行，禁用也为透明底。
  用户截图的故障版本、Grid或宿主兼容条件仍NEEDS_VERIFICATION；
  不把本次Flex通过追认为Grid兼容根因已确认。
- 初次不支持的`:not()`选择器探测保留于`baseline-selector-attempt01/`；
  不把该次“节点缺失”解释为产品布局故障。有效基线改用简单类选择器。
- 基线JSON里的`errors`沿用修复后审计标准；“dedicated feedback nodes absent”
  是旧结构的预期差异，旧提示padding以`.notice`原生computedStyle为准。
- 430基线截图请求超时，没有有效430基线，不补造结果。

## 必需测试点

| TP | 结果 | 当前证据与边界 |
|---|---|---|
| TP-001 原生故障基线 | PARTIAL | 两宿主320/390共20组JSON/PNG；提示padding=0已复现；分页掉行未复现；430基线缺失 |
| TP-002 批准设计 | PASS | 54张Chromium PNG/几何、源与导出SHA匹配；0运行错误/外部请求；非原生 |
| TP-003 现有回归/静态 | PASS | `npm test`349/349，ESLint及小程序校验通过；[前端日志](report-footer-tips-20261101/frontend-tests.log) |
| TP-004 修复原生矩阵 | PARTIAL | 430两个宿主各24态，共48组真实节点0失败；修复后320/390和全部原生截图NOT_RUN |
| TP-005 操作/可访问性 | PARTIAL | 430两宿主各8组原生方法/状态/尾部几何检查PASS；实际触摸、iOS/Android、大字、读屏NOT_RUN |
| TP-006 架构/设计/文档 | PASS | 架构、批准manifest/current-policy与diff检查；当前Feature/UI、Spec/索引、设计和发布记录已同步，业务/架构正文无冲突 |

已执行命令：

```bash
npm test
npm run lint:miniapp
uv run python tools/validate_miniprogram.py
uv run python tools/check_architecture.py
uv run python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261101-REPORT-FOOTER-TIPS-01/APPROVAL.md
uv run python tools/validate_design_evidence.py --check-current-policy
git diff --check
```

小程序校验17页、源码/资源1,234,665字节，低于1.5MiB；这不是上传包体。
未新增图片、请求、依赖、日志或持久状态。本次仅前端样式/结构，无后端、数据库或迁移变更，
不重跑Python业务测试或实库写入检查；不复用并行发布的云/设备证据作为本增量验收。

## 修复后原生证据

`fixed/{embedded,standalone}/430`：每宿主时间/科目/次数×
首页/中间/末页/加载/长页码/操作菜单18态，再加删除提示、长提示、预算提示、
科目目录、只读和失败6态，共24态。
48组真实`wx.createSelectorQuery`检查分页同排/等宽/居中/8px间距、≥44px高度、
≥14px字号、透明禁用、提示包含/内边距/左对齐、科目双列和菜单无横溢出。
没有用HTML或mock系统尺寸抵扣原生检查。

[430内嵌删除提示节点](report-footer-tips-20261101/fixed/embedded/430/subject-deleted.json)：
容器352×47px，左右padding16px、上下12px；文本318×21px，
左右实际留白17px、上下13px（含边框），单行居中；分页两个按钮均136×46px。
长文与长页码原生节点也在各自容器内，未压掉按钮。

[报表方法与尾部检查](report-footer-tips-20261101/native-behavior-embedded-430.json)、
[独立页检查](report-footer-tips-20261101/native-behavior-standalone-430.json)验证：
首页加载、下一页替换、加载保留并拒重入、失败保留页码/内容且不报假成功、
重试当前页、回首页、只读无管理动作，以及页脚位于可见窗口内。
报表还测量收起区≥44px、不重叠分页且在实际Tab上沿之前。
通过官方`App.callFunction`调用现有controller方法；没有模拟触摸，
不将方法调用写成WXML点击或真机操作已通过。

## 缺项与恢复条件

原生截图服务`App.captureScreenshot`在机型切换后持续超时；
Computer Use针对专用微信开发者工具窗口的截图请求只返回菜单栏，无可用窗口图像。
其后没有依据旧坐标盲点，也没有改其他并行项目或mock320/390尺寸。
官方`cli auto --help`没有机型切换选项，故当前保持PARTIAL。

恢复可读的专用开发者工具窗口后，真实切换320×568、390×844并收集每宿主24态；
补430及另外两档PNG/SHA与视觉核对，再做实际分页/重试触摸、大字、iOS/Android和读屏。
如果用户设备仍出现分页掉行，应核对该设备运行包与本证据SHA，保留原生前后数据。
原生几何已有通过项与这些缺项分别记录，未将未执行项改为PASS。

## 代码与当前文档核对

FEAT-001与UI-001原“共享三列Grid/最新分页”已明确改为历史，并加入本地Flex/提示事实。
FRONTEND-DESIGN索引接入本DREV，旧批准manifest仅添加重叠分页/提示范围的Superseded by指针；
批准HTML与PNG/SHA保持冻结。Behavior BHV-033与Architecture的服务/控制器/分页/
权限/依赖合同仍与实际diff一致，无需改正文；测试策略/FEC预算和发布门禁保持。
本Spec、状态清单与[本地交付记录](../../deploy/releases/20261101-report-footer-tips-local.md)
明确本增量未上传，Spec为VERIFYING/active，不能借0.1.17旧冻结包归档DONE。
并行BUG-036、旅行发布和其他用户修改均保留。
