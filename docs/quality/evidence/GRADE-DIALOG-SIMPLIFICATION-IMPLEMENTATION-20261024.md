# 年级弹窗精简 · 本地实现与验证 · 2026-10-24

- Spec: [SPEC-20261024-GRADE-DIALOG-SIMPLIFICATION-01](../../../specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md)，VERIFYING。
- Design: [DREV02](../../design/frontend/prototypes/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/FRONTEND-SPEC.md) / [批准清单](../../design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md)。
- Approval: 本聊天在展示简化稿并明确请求Spec01＋DREV02后，用户2026-10-24回复“继续”。
- Source: 当前共享dirty工作区；本轮未提交/推送、未部署/上传。

## Actual change

只改原grade-confirmation组件WXML/WXSS、coordinator两句错误文案；原组件JS、API、App/Page接线、服务端/数据库不改。正常态只显示“孩子名的年级”、一个原生picker、并排“稍后 / 确认”。旧学年/原级/独立姓名/开学和共享说明删除；错误卡删除，仅按需显示14px短提示；保存中禁用整组，冲突只读最新，最新态无可覆盖picker。

按钮沿用批准HTML的flex1:2分配，**每个按钮另含左右12px内边距**，所以390内容列350px下外宽约121/217px；不是把外框硬改成1:2。原生审计相应扣除内边距验证，源/33张批准PNG完全不变。

测试只将旧“所选年级已保留”文案断言替换为“保存失败”，保留实际选值、单次请求及重试相同payload断言。更新既有原生工具的selector/短文案及并排按钮/内容间距审计，新输出另目录，不覆盖DREV01历史证据。

## Executed automated checks

| Check | Result | Evidence |
|---|---|---|
| `node --test tests/frontend/grade-confirmation.test.js tests/frontend/child-profiles.test.js tests/frontend/family-onboarding.test.js` | PASS / 53 | [targeted](grade-dialog-simplification-20261024/frontend-targeted.log)；确认/稍后、共享、权限、迟到/恢复、实际App/Page桥接、微任务、表单冲突和草稿 |
| `npm test` | PASS / 初轮317，最终327 | [初轮frontend](grade-dialog-simplification-20261024/frontend.log)、[最终检查摘要](grade-dialog-simplification-20261024/final-checks.json)；最终共享工作区新增其他任务用例，不能把增量10项算成本局部新测试，也不代表其他任务设备验收 |
| `npm run lint:miniapp` | PASS | [ESLint](grade-dialog-simplification-20261024/eslint.log) |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS / 17 pages | 初轮[miniapp](grade-dialog-simplification-20261024/miniapp.log)；最终源码1,219,222 bytes见检查摘要，不是官方上传包大小 |
| `.venv/bin/python tools/check_architecture.py` | PASS / 4 policies, 150 modules | [architecture](grade-dialog-simplification-20261024/architecture.log)；无边界/依赖变化 |
| `.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-015/DREV-20261024-ANNUAL-GRADE-PROMOTION-02/APPROVAL.md --check-current-policy` | PASS | [design](grade-dialog-simplification-20261024/design.log)，批准源/33张SHA一致 |
| `node --check tools/grade_confirmation_geometry.js`；prepare/render脚本Ruff/format | PASS | 语法、Ruff和2脚本格式通过；不代表原生执行 |

第一次年级19项专项为18通过/1失败，唯一失败是原断言要求已删除的长文案；修正断言后上述53/317通过。未改测试中的行为断言，也未新增镜像CSS测试。后端/数据库未变，本轮不重复后端752项或MySQL；那些结果仍属主年级任务。

## Native and device evidence

`tools/prepare_grade_confirmation_native.py`重建`/private/tmp/push-kids-grade-native-20261024`：生产模板/样式与本轮源一致，副本关闭云、移除受限插件、注入合成只读transport/布局setter；所有业务写入拒绝。只在副本App增加启动**原生产控制器**的测试入口，并在离线transport计数被拒绝的确认尝试，用于实际picker/重试/稍后验证，不替换生产组件或宿主处理器。原生采集只允许该副本，当前工具输出到`grade-dialog-simplification-20261024/native/`，禁止覆盖旧`grade-confirmation-20261024/native/`。11项生产来源SHA核对无漂移，4项关键组件/规则文件与副本逐字节相同。

原生环境：官方微信开发者工具Stable 2.01.2510290、基础库3.17.4、WebView；iPhone5（320×568，DPR2）、iPhone12/13 Pro（390×844，DPR3）、iPhone14 Pro Max（430×932，DPR3），fontSizeSetting=15。截图接口实际导出为视口2倍像素，不把截图缩放当作设备DPR。

| Native check | Result | Evidence |
|---|---|---|
| 17态×三尺寸 | PASS / 51组 | [native](grade-dialog-simplification-20261024/native/)内逐态JSON矩形/计算样式与PNG；11个显示态及6个不弹态，含长名、保存、错误、冲突、最新、导航遮挡/恢复 |
| 原生picker实际选级与重试 | PASS / 三尺寸 | `interaction-check-{320,390,430}.json/png`：CUA打开滚轮、选到四年级，实际组件→宿主→生产控制器两次确认；离线transport拒绝两次写入，所选四年级和短提示保留 |
| 稍后 | PASS / 三尺寸 | `interaction-dismissed-{320,390,430}.json/png`：实际点击稍后后弹窗消失、导航恢复，仍仅两次拒绝写入，无额外写入 |
| 目视检查 | PASS / LOCAL_SIMULATOR | 390年度态，320长名/错误/最新，430冲突及最终保存态均完整可读、无相互覆盖；错误提示现在完全容纳于短屏，无需靠隐藏或滚动掩盖 |
| 真实iOS/Android、系统大字体、读屏/焦点、双家长旧端、全原生业务端到端 | NOT_RUN | 当前仅本机原生模拟器＋离线拒绝写入交互；这些独立门禁不能由HTML、mock或历史DREV01抵扣 |

初次390请求实际仍为iPhone5/320，17组严格视口断言全部拒绝，保留于`failed-initial-viewport/`；后续增加采集前精确视口检查。截图复核发现平台默认禁用按钮样式盖过低优先级规则，文字过浅；三尺寸旧保存态保留于`failed-initial-style/`，将原有禁用规则限定到组件/操作区后，与批准设计一致。最终51组重新采集并检查实际计算颜色，所有操作文字对比度≥4.5、opacity=1，未改变冻结设计。

实际选级/重试/稍后先于最后一次**仅禁用态样式优先级**修正采集，记录其当时WXSS SHA；组件JS、控制器、事件绑定和可操作态样式相同。最终矩阵绑定修正后的WXSS，不能把两批取证冒称同一源码快照。精确SHA、时间、图片校验与阶段见[manifest](grade-dialog-simplification-20261024/manifest.json)。副本首次交互入口误用了不存在的event方法，已改为原handle并重新验证；不影响生产代码。重编译/设备切换期间发生截图超时，重开隔离项目后重采；超时和启动未就绪轮次均不计通过。普通沙箱限制了本机端口，后改用经批准的本地测试连接，没有放开业务写入。

## Documentation and lifecycle

已依据实际diff核对Feature013、Behavior BHV-042、Architecture、UI-001/015、主/局部Spec、FrontendDesign、索引、测试证据与本地发布记录。领域/权限/存储/发布事实不变；新布局替代旧弹窗呈现，不替代档案表单。旧UI-015“未采集/锁屏”摘要已按证据澄清，候选状态已换成已批准本地实现，无新增代码/文档冲突。归档区BUG-033候选仍独立待批准。[本次局部只读复核](grade-dialog-simplification-20261024/review.md)无Blocker/Major；同上下文复核，不冒充独立上下文。

Spec保留`specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md` / VERIFYING；本地实现、自动化、三尺寸呈现和局部实际交互、文档核对及同上下文只读复核已完成。完成门禁仍缺真实iOS/Android、系统大字体/读屏/焦点及主任务原生业务端到端，不能DONE、不迁completed；独立上下文复核也未由本局部复核替代。主年级Spec02继续VERIFYING。无需重新批准已实现方案，未上传部署。
