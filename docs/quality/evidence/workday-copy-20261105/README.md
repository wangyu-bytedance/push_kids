# 工作日备注减法验证 · 2026-11-05

对象：[SPEC-20261105-WORKDAY-COPY-01](../../../../specs/completed/FEAT-001-WORKDAY-COPY-CLEANUP.md) / [批准DREV03](../../../design/frontend/snapshots/UI-001/DREV-20261105-WORKDAY-03/APPROVAL.md)。用户批准后才改生产代码及通用规范。局部可逆呈现变更R1，采用Baseline，未制造Red；源码绑定见`before/manifest.json`、`implementation.patch`和`source-sha256.json`。当前工作区含并行任务，不用Git总diff冒充本任务范围。

## 实际检查

| 检查 | 当前结果 | 日志/说明 |
|---|---|---|
| 改前`node --test tests/frontend/workday-schedules.test.js` | 10 PASS | `logs/workday-copy-baseline-20261105.log`；保存改前10文件及SHA |
| 改后同一专项 | 10 PASS | `logs/workday-copy-focused-20261105.log`；保留模式、回填、逐日草稿、只读/失败、缺覆盖及cache语义测试 |
| `npm test` | 359 PASS / 0 skip | `logs/workday-copy-frontend-20261105.log`；本轮真实执行，非父Spec历史计数 |
| `npm run lint:miniapp` | PASS | `logs/workday-copy-eslint-20261105.log` |
| `uv run python tools/validate_miniprogram.py` | PASS | `logs/miniprogram.log`；pages17 / source_bytes1,244,228，低于1.5MiB源预算 |
| `uv run python tools/validate_design_evidence.py --check-current-policy` | PASS | `logs/design.log`；批准源与24张导出另做SHA核对 |
| `uv run python tools/check_architecture.py` | PASS | `logs/architecture.log`；无本任务模块边界或依赖变更 |
| 验收工具Ruff check/format、Node语法 | PASS | `logs/tool-checks.log`；未新增项目依赖 |
| 三尺寸原生节点 | 24组 PASS | `native/*.json`；390×844、320×568、430×932各8态，实际window/screen尺寸写入JSON |
| 原生PNG | PARTIAL | 390八张已观察；320/430 `App.captureScreenshot`超时，非HTML替代 |
| iOS/Android真机、读屏、独立Review | NOT_RUN | 本地作者自查不计独立Review |
| 后端全量/迁移/云部署/上传 | NOT_RUN | 本增量无后端/Schema变化，未执行发布；父Spec旧919/48结果不纳入 |

`final-audit.json`记录批准设计SHA、生产与原生WXML/WXSS一致性、24节点/8截图清单及文档引用核对；`artifact-sha256.json`绑定本轮日志/工件。仅合成家庭、孩子和活动；离线副本拒绝业务写入，没有真家庭请求或通知。

## 原生方法与失败留存

微信开发者工具Stable2.01.2510290 / 基础库3.17.4，任务副本`/private/tmp/push-kids-workday-copy-native-20261105`，端口9632。由`tools/prepare_workday_native.py --output <副本>`复制原生源，WXML/WXSS逐字一致；仅副本增加fixture hook和离线API。`tools/workday_geometry.js <width> 9632 --copy-cleanup --screenshots`调用`wx.createSelectorQuery`测量，不把Page JS数据或HTML当原生布局。原生源SHA保存在`native-source-sha256.json`。

8态为settings-workday/coverage、calendar-create/edit/coverage/partial-coverage、today-coverage/partial-coverage。检查删除备注与空容器、结果短状态唯一、未知无确定空态、已知游泳卡保留、模式/picker/保存44px、短状态14px及水平边界。编辑长表单允许纵向滚动，初始滚动位置可能只露出部分时间字段，底部保存仍完整可见；未以隐藏水平溢出通过。

最终`native/`24份JSON均errors=[]；390八张PNG逐张观察表单、唯一状态与部分缺数据结果，未发现本增量可见偏差。320/430没有可用原生PNG，故完整三视口视觉与TP005为PARTIAL，不能称原生验收全部通过。

失败保留：`attempt-01-old-project/`为误连旧9631项目；`attempt-02-cross-realm-fixture/`中跨realm setData显示数据但数组未渲染，改为在真实Page内JSON.parse；`attempt-03-font-container/`误检Calendar容器继承13px，实际叶子14px，改查叶子。中间重连/冷启动失败日志亦保留。以上不是生产Red，最终成功对象另存。`capture-retry-430/`仍截图超时；`capture-retry-320/`实际仍为430视口，明确wrong viewport/overflow，不能记为320通过或生产回归。宿主模拟器图像曾滞后/裁切，不用于弥补截图缺项。

## 工程与文档闭合

- Component/form/state：沿用原Page与三模式、草稿/回填/保存合同；删除无消费者映射、规则样式和卡片。未建立共享文案工具或新组件。
- A11y：状态保留`aria-live=polite`，新增短状态14px，原按钮44px检查通过；屏幕阅读器实际播报未执行。
- Performance/resource：无新请求、依赖、图片、缓存或业务查询；保留原API metadata，源预算见小程序检查。
- Security/privacy/observability：无身份、存储、日志或提醒合同变化；实际缺覆盖仍可见。后端静态日志码保持，不新增遥测。
- Feature001、Behavior BHV009a、UI001已用COPY03正文替换旧呈现描述，通用FDB正文/FEC引用同步；父Spec加后续修订指针。旧DREV02只加Superseded by，冻结源/导出不改。
- Architecture/constraints、测试策略按真实任务diff核对，无边界/API/Schema、测试门槛变更，正文N/A；原后端政策与父Spec剩余缺项保留。
- 子Spec/EVD、Spec README/STATUS、年度运维及本地发布记录同步。数据自动化仅研究，未配置任务。
- 未发现本任务未记录的代码与当前文档冲突。无对应云交付，子Spec VERIFYING/active；后续补完整原生PNG、真机/读屏和独立Review，发布仍执行既有手册门禁。
