# 今日学习卡片显隐与风格统一 — 实现与验收

- Date: 2026-10-24
- State: LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED
- Approval: 用户在call_ac391833df284fc7b0afcb71c55abec7明确回复「批准，按此实现」，批准[Spec01](../../../specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md)与[DREV03](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-03/FRONTEND-SPEC.md)。批准记录先于生产修改。
- Baseline: main / `82ca52775bc948f2a963a8f4ed614322d8859de8`，共享未提交工作区。只归属本次today-learning组件、专项回归、合成取证工具及相应文档；未覆盖其他会话修改。

原组件保持挂载。唯一快照写入方法setCurrent投影显示状态，权限observer重新投影；不计算服务端两日资格，不增加请求。无实际内容的无资格/未知/eligible纯空快照整块隐藏；自动提示和轮询仍执行。有实际可操作提案则显示标题、科目、可选时长及AI标识；已批准Task优先，含viewer、部分记录和生成开关关闭。生成、失败、失效及删除后恢复保留简短状态和原操作；请求失败保留内容与重新加载。

复用sec/sec-bar/s-t/sec-rule/pk-card/btn：17px衬线分区标题、16px/600无衬线实际标题、14px正文、胶囊按钮。删除空原因文案和两句口号。局部样式限定卡片/状态区，不改变DREV02弹层。首次原生发现微信按钮默认宽度覆盖全局样式，补充组件内全宽约束；续验收目视发现删除文字继承全局左对齐，按批准设计限定卡片内居中并增加textAlign/justifyContent原生断言。最终81组已全部重采，对应修正后源码；[对齐前记录](today-card-20261024/native-audit/before-quiet-alignment/verification-manifest.json)保留，不冒充最终结果。

## 实际检查

| 检查 | 结果与范围 |
|---|---|
| `node --test tests/frontend/today-learning.test.js` | PASS，13项；新增4项覆盖空状态、任务优先/角色切换、生成恢复及零写入、隐藏仍自动提示/网络失败保留/重置 |
| `npm test` | PASS，最终327项，0失败/跳过；首次实现时317项，续验收期间共享工作区增加了其他任务测试，不能全部归属本改动。最终对齐修正后全量重跑退出0，日志位于/private/tmp/push-kids-today-card-final-frontend.log |
| `npm run lint:miniapp` | PASS，退出0 |
| `validate_miniprogram.py` | PASS，最终修正后17页，共享工作区源码预算1,219,145字节，低于1.5MiB；此前1,217,535字节为上轮时点，非上传包体。本卡片无新增资源/依赖 |
| `check_architecture.py` | PASS，4政策/150模块 runtime/lazy DAG |
| DREV03批准源/SHA/当前政策 | PASS，`validate_design_evidence.py --manifest …DREV03/APPROVAL.md --check-current-policy`，无allow-pending |
| 准备脚本Ruff、原生runner语法 | PASS；最终收尾检查另记 |
| 原生320×568、390×844、430×932 | PASS，每视口21卡片态＋6个原弹层代表态，合计81组节点/PNG（63卡片＋18弹层）。用户回复继续后桌面可操作，锁屏缺口已消除；三视口均用最终同版runner采集，全部errors为空，基础库3.17.4。见[原生目录](today-card-20261024/native/) |
| 真实iOS/Android、系统大字体、读屏/键盘 | NOT_RUN，本机合成模拟器不能替代 |
| 独立只读复核 | NOT_RUN，尚无独立复核结论 |

收尾实际执行：DREV01、DREV02批准源/清单分别校验PASS；准备脚本与DREV03 renderer的Ruff format --check通过，准备脚本Ruff check与runner node --check通过；git diff --check通过。逐个复算81张原生PNG SHA与JSON错误、14份源码hash全部匹配，另核对全局app.wxss/tokens/atoms与副本一致；见[verification-manifest](today-card-20261024/native/verification-manifest.json)。工具更正的旧/新SHA见[对齐前审计清单](today-card-20261024/native-audit/before-quiet-alignment/source-manifest.json)，最终清单对应重新准备的副本。14份相关文档本地链接0缺失；Spec仍active/VERIFYING，completed无副本。Architecture/ADR依赖与所有权、Feature/UI/Behavior、Spec、测试和发布事实逐项无冲突；旧自动化数字已明确为历史范围，不冒充本次结果。

320首次运行10个空态因取证脚本假设sec-bar始终80rpx而失败；实际原生交互分区具有既有44px触控下限，文本居中产生的间隔不同。改为同时采集原生reviewSection.marginTop、reviewBar矩形计算邻接间隔，[初始失败](today-card-20261024/native-audit/initial-320-spacing.json)保留；该脚本修正未改变生产间距。随后只按批准设计修正卡片删除文字居中，三个视口各27态全部重跑。期间两次App.captureScreenshot超时的命令退出1，未计通过；官方CLI auto重连后实际81组全部退出0并有匹配PNG/JSON，未以预览或旧记录代验。

原生使用官方DevTools自动化接口，只操作`/private/tmp/push-kids-today-learning-native-20261024`只读合成副本。副本拒绝业务写入，useCloud=false/family=synthetic双重校验；测试setter调用生产setCurrent，未手动强制card标志。新增原生断言核对隐藏区域零节点与Hero到复习分区仅保留原生section margin、分区字体家族/字阶/字重/行高/字距一致、16px具体标题/卡片包含、40rpx圆角、胶囊全宽与≥44px、viewer无写入口、删除操作居中、错误保留及横向边界。长标题为120字完整换行并滚动到分区取证。已目视核对390主态/空态、320空态/最长标题、430主态与最终居中待学；不把无横向溢出代替真实设备可用性。

21态：recent-new、warming-up、no-history、missing-grade、no-subject、disabled、inactive、eligible-empty、viewer-empty、unknown-empty、proposal、proposal-long、task、partial、viewer-task、task-feature-off、generating、generation-error、stale、recover-after-remove、network-error。原生文件名前缀card-；额外modal：design、saving、approve-error、edit、max-title、max-title-scrolled。

## 文档与生命周期

Feature004、UI001、Frontend Design、Behavior Catalog BHV-045、测试策略、主Spec/卡片Spec、发布记录和索引按本地事实同步；Architecture/ADR逐项核对，无模块/所有权/依赖方向/API/Schema/扩展点变化，N/A。DREV01只新增卡片范围的Superseded by指针；DREV02仍为弹层基线，旧源/快照/SHA不变。设计阶段记录为历史取证，不冒充当前实现结果。

卡片Spec保留`specs/active/FEAT-004-TODAY-CARD-VISIBILITY.md`、VERIFYING；三视口原生已完成，尚缺真实设备/可访问性及独立复核，不能DONE或迁入completed。恢复条件为补齐这些验收结论；当前没有新的设计/实现批准需求。没有提交、推送、上传、部署、改变默认开关或写入真实学习数据。
