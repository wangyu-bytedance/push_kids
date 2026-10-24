# FEAT-013 本地实现与验证 — 2026-10-24

- State: LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED
- Approval: 用户“好的 按照这个方案落地”，批准[Spec02 / Architecture02 / DREV01](../../../specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md)。
- Baseline HEAD: `82ca52775bc948f2a963a8f4ed614322d8859de8`；共享dirty工作区，无本任务commit。其他任务在同时修改工作区，全仓结果只代表该次命令观察，不代表其他任务完成。
- Current feature: [FEAT-013](../../domain/features/FEAT-013-annual-grade-promotion.md)。
- Release scope: [本地交付记录](../../deploy/releases/20261024-annual-grade-local.md)。
- Machine evidence: [manifest](grade-confirmation-20261024/manifest.json)，记录本功能源码/日志SHA与采集时间；日志目录不含凭据或真实儿童数据。

本文件及manifest记录主Spec02/DREV01采集时源码。后续获批的[精简Spec01/DREV02实施证据](GRADE-DIALOG-SIMPLIFICATION-IMPLEMENTATION-20261024.md)拥有当前弹窗布局、短提示和317/53项前端结果；此处313项/旧原生仍是历史证据，不抵扣新布局。领域/API/Schema规则保持本主任务合同。

## Implemented and exercised

children领域新增纯序列/学年政策和共享确认用例。北京时间9月1日产生建议，第一次旧档案只核对原级；只有家长确认才原子更新正式grade/学年/revision。同学年同结果重试幂等、不同结果冲突、版本过期不可覆盖；只写children，不写学习/Review/Todo。候选服务一次有界SQL、LIMIT6异常哨兵，最多5项/8KiB，归档/清理/未知/九年级/viewer不入队。

客户端五Tab仅接宿主事件，App coordinator拥有前台会话与≤5人独立队列，当前孩子优先、不改全局孩子。稍后零共享写入；切Tab/返回/picker不重置会话，下一次前台重新核对。保存失败保留选择、双击防重、冲突只读刷新、身份/家庭变更使旧响应失效。bootstrap移除已手动确认/归档的缓存候选；新增/恢复在用孩子后在安全宿主刷新，保留当前选择和本会话稍后集合。归档/恢复/确认元数据变化使旧在途候选失效。报表筛选表单也纳入互斥。

档案页年级touched+version区分明确确认与普通名字/时长保存。人工改级冲突后保留名字、时长和年级草稿，只读获取最新正式级/version，在既有错误区域提示重新选择；未重新选择前保存只重读，不直接覆盖。读取失败不能通过重选旧值绕过刷新。新增八/九年级canonical选项，精确别名不重复，未知旧值保留。

0025接本地0024，新增两列/索引，不回填旧grade或猜测基准。本地SQLite自愈同义、重复启动不重置；有确认事实时拒绝破坏性降级。

## Actual commands and results

工具均使用现有`.venv/bin`，未安装新依赖；`uv run`缓存目录受沙箱限制，因此使用同环境可执行文件。

| Check | Actual result / evidence | Scope / limits |
|---|---|---|
| `.venv/bin/pytest tests/unit/test_grade_policy.py tests/integration/test_grade_confirmation.py tests/integration/test_grade_confirmation_migration.py tests/performance/test_grade_confirmation_reads.py -q` | **43 passed**，[targeted.log](grade-confirmation-20261024/targeted.log) | 全序列/别名、上海/UTC边界、首次/累计/终点、API、权限/家庭、CAS、人工意图/旧端、归档/冻结、回滚、迁移/重启、50k规模 |
| `.venv/bin/pytest tests/integration/test_grade_confirmation_mysql.py -q --tb=short`，显式配置隔离测试URL | **4 passed**，[mysql57.log](grade-confirmation-20261024/mysql57.log) | MySQL5.7.44真实并行事务：双家长同级重试/异级冲突、50k索引/预算、0024→0025迁移与降级保护 |
| `.venv/bin/pytest tests/unit tests/integration tests/contract -q` | **752 passed, 39 skipped**，[backend.log](grade-confirmation-20261024/backend.log) | 普通套件无MySQL等显式外部环境时skip；本功能MySQL另跑，不把skip冒充通过 |
| `npm test`（独立审查修正后） | **313 passed**，[frontend-review.log](grade-confirmation-20261024/frontend-review.log)；本功能/档案/启动定向 **53 passed**，[frontend-targeted-review.log](grade-confirmation-20261024/frontend-targeted-review.log) | 含真实App/Page桥接、五人串行、会话/权限/迟到、失败重试/冲突、原生picker事件、实际表单意图、归档恢复与在途竞态、报表筛选互斥；mock不能证明真机生命周期。293/305/311项及定向46项是历史日志；共享工作区中间3项其他任务失败和本轮定向首跑失败日志保留，随后重跑通过 |
| `.venv/bin/pytest tests/integration/test_fair_review_migration.py tests/contract/test_worker_readiness.py -q --tb=short` | **9 passed** | 首轮全仓发现历史Schema种子用了当前Child ORM默认列；改用0016冻结列清单。另一次worker readiness失败，定向重跑及最终全仓均通过；不改无关worker策略 |
| `.venv/bin/ruff check`（children、0025、新增专项测试、旧迁移fixture、prepare工具） | **PASS** | 仅本任务受影响代码 |
| `.venv/bin/ruff check .` | **PASS**，[ruff-review.log](grade-confirmation-20261024/ruff-review.log) | 早期其他任务的导入排序/长行失败保留在ruff.log |
| `.venv/bin/ruff format --check .` | **PASS / 694 files**，[format-review.log](grade-confirmation-20261024/format-review.log) | 中间其他任务新增prepare_record_entry_native.py未格式化的观察保留在format-resume.log；之后全仓重跑通过，未代为修改其他任务 |
| `.venv/bin/mypy apps/api/src` | **PASS / 150 files**，[mypy.log](grade-confirmation-20261024/mypy.log) | 保留已有untyped note，无错误 |
| `npm run lint:miniapp` | **PASS**，[eslint-review.log](grade-confirmation-20261024/eslint-review.log) | 小程序与前端测试ESLint |
| `.venv/bin/python tools/check_architecture.py` | **ARCHITECTURE_VALID policies=4 modules=150**，[architecture-review.log](grade-confirmation-20261024/architecture-review.log) | runtime/lazy依赖图无环；无新开放扩展点 |
| `.venv/bin/python tools/validate_miniprogram.py` | **MINIPROGRAM_VALID pages=17 source_bytes=1216563**，[miniapp-review.log](grade-confirmation-20261024/miniapp-review.log) | 共享工作区该次源码预算，不等同官方上传包大小 |
| `.venv/bin/python tools/validate_design_evidence.py --manifest <DREV01/APPROVAL.md> --check-current-policy`及全仓current-policy命令 | **DESIGN_EVIDENCE_VALID**（两次） | APPROVED源/57张设计导出尺寸/SHA有效，源HTML未变；不证明原生布局 |
| `node --check tools/grade_confirmation_geometry.js` | **PASS** | 原生采集执行结果另列，语法不替代布局验收 |

首次MySQL测试失败原因是任务新建数据库默认为latin1，不能存中文。仅重建本任务`grade_test`/`grade_migration`为utf8mb4_unicode_ci后上述4项通过；未连接生产。镜像为官方`public.ecr.aws/docker/library/mysql:5.7`，digest `sha256:4bc6bc963e6d8443453676cae56536f4b8156d78bae03c0145cbe47c2aad73bb`，监听仅127.0.0.1，测试使用一次性空密码容器。测试结束已删除精确命名的`push-kids-grade-mysql57-20261024`容器及其一次性库，没有操作其他容器或生产。

## Native/device gate — PARTIAL

`tools/prepare_grade_confirmation_native.py`已生成`/private/tmp/push-kids-grade-native-20261024`；只在副本关闭云、替换合成只读transport、移除受限语音插件、今日页置首及注入JSON布局fixture。生产配置、transport、AppID和插件声明不变；副本拒绝所有业务写入。`grade-source-sha256.json`记录精确生产模板/样式/规则来源。

用户回复“已解锁”后恢复官方开发者工具Stable 2.01.2510290 / WebView / 基础库3.17.4。iPhone5（320×568/DPR2）、iPhone12/13 Pro（390×844/DPR3）和iPhone14 Pro Max（430×932/DPR3），字体设置15；实际尺寸由wx节点查询同时读取，不能由图片像素倒推。三尺寸各17态共51组节点/截图，检查水平边界、≥44px目标、≥14px文本、按钮铺满内容列、10px操作间距、屏内操作及Tab隐藏/恢复；另有三尺寸档案九年级字段/保存控件节点和截图。[原始证据](grade-confirmation-20261024/native/manifest.json)保留来源SHA、时间及截图SHA。

CUA在三尺寸实际打开/取消系统picker，AX均识别小班至九年级12项；全窗口`picker-window-*.png`包含系统滚轮。官方`App.captureScreenshot`不含该平台浮层，因此不把WebView截图当作滚轮证据，也不声称获得平台滚轮每项的WXML矩形。档案页调用生产chooseGrade并核对九年级，不提交表单；320页滚动后同时显示字段和保存操作。

原生检查发现并修正：平台默认button规则将按钮缩成184px，改为组件内更明确的选择器，三尺寸现铺满内容列；组件属性/生命周期同步通知宿主造成递归setData警告，改为微任务通知并加入合同回归，五Tab初值显式为空，原生未再见该警告；档案原有保存按钮在320为40px，局部补足44px后重采。上述均为批准FEC/DREV内的一致性修正，未修改批准设计字节。

320错误态经CUA实际滚动后，保存失败提示完整可读，两枚操作仍在屏内；`error-scrolled-320.json/png`记录非零scrollTop与节点，`error-scrolled-window-320.png`保留可读性目视证据。初始错误位于滚动正文下方，与批准短屏设计一致；节点数值通过本身不等于目视/交互通过。期间重新锁屏，用户回复“继续”后恢复；原生控件RPC的Page.getElement超时不能算交互通过，最终采用实际CUA滚动并查询scrollOffset。仅为核对官方接口下载自动化SDK压缩包到/private/tmp，未修改项目依赖或安装到生产。

仍需真实iOS/Android前后台、字体放大/读屏/焦点、真实双家长和旧客户端。fixture呈现验证不抵扣生产生命周期验收。上述55份节点/59张PNG对应native manifest冻结来源；随后独立审查修正coordinator、报表互斥与档案冲突恢复，仅运行自动化回归，**未重建副本验证这些流程的原生端到端行为**。共享组件模板/样式及已测档案控件几何未因这些修正改变，原呈现证据仍只证明采集时布局。

## Ownership, compatibility and document closure

必要的新owner限children年级policy/use case与小程序session coordinator/presentation；不存在共享utils桶、泛化弹窗框架、定时任务、AI或历史表。迁移为增量，有事实拒绝删列。旧读兼容；旧writer只有同级普通保存兼容，真实改级须升级客户端。没有尝试静默维持两个写协议。

已逐项同步Feature013及005/002/001、Behavior BHV-042、Architecture模块owner/本地head、UI001/015、设计索引、Spec/索引、测试策略与本地交付记录。原设计HTML SHA仍`94e80e4b10cc27b268d3a57daca8657a8860083eaad1a78fb2c511b1631c452c`，57导出不改；设计合同内批准前叙述为历史内容，实际批准以不可变manifest审批记录为准。

本功能当前代码/文档已统一为“建议＋确认后生效”，不存在直接日期投影或初一封顶残留实现。另发现**既有文档差异**：BHV-025及FEAT-005旧段写“归档资料仍可编辑”，而实施前备份与当前update_child均要求在用（原require_active_child）。本任务沿批准Spec保持原active门禁，不把该历史文档差异扩成归档编辑行为修复，也不声称全仓历史文档零冲突；后续需在档案领域明确处理。

[独立只读评审](grade-confirmation-20261024/independent-review.md)第三轮PASS，无剩余Blocker/Major。初轮发现恢复漏核对、报表筛选互斥及人工改级冲突恢复问题；第二轮发现归档/人工确认后的在途候选竞态；四项均修复并复核关闭。当前剩余门禁为真实iOS/Android、修复后原生端到端、可访问性及双家长旧端。Spec保留`specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md`的`VERIFYING`，不满足DONE迁移条件。不重复请求已批准产品方案，不执行生产迁移/部署/上传。
