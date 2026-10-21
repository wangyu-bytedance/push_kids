# 背景细弧线统一清理 — 2026-10-21

- Status: LOCAL_IMPLEMENTED / AUTOMATION_PASS / NATIVE_PARTIAL / DEVICE_PENDING / NOT_RELEASED
- Task Spec: [BUG-SPEC-20261021-HERO-ARC-01](../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md)，VERIFYING，保留active。
- Approved design: [DREV-20261021-HERO-ARC-REMOVAL-01](../../design/frontend/prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/FRONTEND-SPEC.md)
- Source: 验证时基于HEAD `8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a` 的当前工作树；下列结果的范围为该工作树。
- Changed production file: `apps/miniprogram/styles/atoms.wxss`
- Changed source SHA-256: `1c569b76f2cecb5331371b1378092be3388544bceaa9bd3e6ff1365993a9e17f`
- Scope: 仅共享装饰；不改变API、数据、权限、排期、事件或扩展点。并行工作树改动保留。

## 全面排查与处理

已检索全部小程序WXML/WXSS的背景、伪元素、圆描边与负偏移装饰，并目视检查7张本地插画
（书本、台历、成长记录、活动、每日任务、出行、相机）。同类孤立细弧线来自唯一共享
`.pk-hero::after`：1rpx低透明圆描边被卡片裁切。未在这些插画中发现同类孤立发丝瑕疵，未重绘PNG。

本次直接删除权威绘制规则，修正对应注释。全部7个页面、11处WXML引用一起生效：

| 页面 | 生效位置 |
|---|---|
| 今日 | 正常安排卡、首次引导卡（二选一） |
| 日程 | 带台历插画的标题卡 |
| 记录 | 带书本插画的标题卡 |
| 报表 | 带成长插画的标题卡 |
| 设置 | 在学科目、课外活动、每日任务、出行安排四张卡 |
| 家庭与成员 | 邀请卡 |
| 提醒设置 | 就绪/中性状态卡 |

纸面渐变、插画、卡片边框/阴影、布局和原事件保持原状。实际diff为一条规则删除和一处注释修订。

## 批准与冻结设计

助手已向用户展示Spec01/DREV01和前后对比并请求具体确认，用户随后要求
“还有很多其他的背景 有类似的问题 一起修复掉”。此前Spec01/DREV01已明确覆盖全部共享卡片，
全面排查未发现第二种需另立方案的弧线，因此记录为对本轮唯一具体方案的继续实施批准。
先记录APPROVED及三个UI清单的批准，再删除生产规则。

三个新DREV清单均已按批准状态验证；获批HTML与30张设计PNG不变。
旧背景、邀请和提醒清单仅添加局部Superseded by指针，原源文件/PNG/哈希不改。

## 本次实际检查

| 检查/命令 | 结果 | 范围与证据 |
|---|---|---|
| `npm test` | PASS | 265 tests / 265 pass / 0 fail / 0 skip；本轮运行，原始本地日志 `/private/tmp/push-kids-hero-arc-frontend-tests.log`。 |
| `npm run lint:miniapp` | PASS | 现有小程序JS与前端测试；本轮运行。 |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS | 17页，source_bytes=1155936，低于1.5 MiB预算。 |
| `.venv/bin/python tools/check_architecture.py` | PASS | 4项策略、130模块，runtime/lazy DAG。 |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | PASS | 本轮当前政策检查。 |
| `tools/validate_design_evidence.py --manifest <UI-001/UI-009/UI-011的本DREV清单>` | PASS | 三份清单逐一按APPROVED验证，包括源/PNG哈希和尺寸。 |
| 额外复核被局部替代的三份历史清单 | PARTIAL / 1 pre-existing FAIL | 旧CARD-BACKGROUNDS与旧NOTIFICATION-AUTO-RENEWAL清单通过；旧UI-009家庭邀请源哈希不一致，详情见下文。此项未伪装为PASS。 |
| `node docs/quality/evidence/hero-arc-removal-20261021/verify.cjs` | PASS | 实际首次运行入口为 `/private/tmp/push-kids-hero-arc-verify.cjs`；同一验证源码已保留为[verify.cjs](hero-arc-removal-20261021/verify.cjs)。27组受影响状态/视口当前渲染在只规范化注释与CSS空行后与冻结批准HTML一致；[对照JSON](hero-arc-removal-20261021/approved-parity.json)。75份现有25个fixture×三视口渲染中均无该弧线规则。 |
| 原生合成页面编译/采集 | PARTIAL | 微信开发者工具Stable 2.01.2510290，基础库3.17.4，三视口实际信息和数值几何见下表。截图/导航API存在超时，不能算完整通过。 |
| 原生字体放大、完整长内容/状态与iOS/Android实机 | NOT_RUN | 本轮未完成，需要后续验收；不是自动化PASS。 |
| 后端pytest/Ruff/Mypy/MySQL/Ark | NOT_APPLICABLE | 仅WXSS纯装饰删除，无Python/API/SQL/模型行为变化；未运行，未声明通过。 |
| 上传/体验/审核/正式发布 | NOT_RUN | 本任务止于本地修复，未执行这些平台操作，不改变既有版本记录。 |

候选设计期27组hero前后几何一致、伪元素none、图片解码/运行错误/远程请求为0的记录位于DREV
`render-audit.json`；这些仍是设计证据，不代替下述原生验收。

## 原生证据与明确缺口

副本：`/private/tmp/push-kids-hero-arc-native-20261021`。
副本关闭云服务，业务API固定拒绝，页面控制器替换为合成展示fixtures；生产WXML/WXSS和图片不改。
为避免无关WechatSI插件的`41002 appid missing`启动错误，仅在临时副本去掉插件声明。
这只能证明隔离展示编译与被采集几何，不能证明完整生产插件包或真实交互链路通过。
[源文件哈希对照](hero-arc-removal-20261021/native-source-hashes.json)覆盖app.wxss、atoms.wxss和7页WXML/WXSS。
采集源码保留为[capture-native.cjs](hero-arc-removal-20261021/capture-native.cjs)，连接仅本机9443端口。

| 原生逻辑视口 | 设备/DPR/字体设置 | 已采集状态几何 | 已留存截图 | 未完成 |
|---|---|---|---|---|
| 320×568 | iPhone5 / DPR2 / fontScale15 | 6组：今日、引导、记录、日程、报表、设置 | 3张：今日、引导、记录 | 日程/报表/设置及设置下部截图API超时；家庭/提醒导航失败，未采集。 |
| 390×844 | iPhone12/13Pro / DPR3 / fontScale15 | 全部9组，包括家庭与提醒正常/中性 | 10张，含设置下部 | 当前字体与合成fixture范围；非实机验收。 |
| 430×932 | iPhone14ProMax / DPR3 / fontScale15 | 5组：今日、引导、记录、日程、报表 | 4张：引导、记录、日程、报表 | 今日截图API超时；设置导航App.callFunction超时，后续未执行。 |

合计20组状态/视口数值证据、17张原生截图；[原生目录](hero-arc-removal-20261021/native/)中的JSON逐项记录
截图文件/哈希或NOT_RUN。截图导出的实际像素与运行时DPR分别记录，不能混同；清单见
[native-manifest.json](hero-arc-removal-20261021/native-manifest.json)。
已采集卡片均存在，宽高为正、位于视口横向边界内，根页面无横向滚动；这只覆盖卡片级检查，
未宣称全部触控目标、长文本、读屏或错误状态的完整FEC矩阵通过。已目视核对390设置原生截图，弧线消失。

原生自动化首次启动受沙箱本地端口限制，授权后正常启动；之后截图/导航错误已单列保留。
没有通过更改生产插件配置、隐藏溢出或HTML截图补记原生PASS。

## 收尾发现的既有历史证据问题

额外验证旧 `UI-009/DREV-20260913-FAMILY-INVITE-CODE-01/APPROVAL.md` 时，校验器报告
`family-invite-flow.html` 的 editable source hash mismatch：

- 清单期望：`de5e54eb908f2a938a070467a86930d91b92f9629dd26826cc32d49e958f8d59`
- 当前文件实际：`be5357bd54d01b21befb6c2513f42050e376443a9404bfa6a778d54a993dd349`
- `git show HEAD:<source>`计算结果与当前文件相同，证明源文件不是本次改动产生的偏差。
- 本次只在旧清单添加允许的局部Superseded by指针，没有改写旧源、旧PNG或历史哈希。

本次DREV的UI-009新清单与自包含源/三视口PNG均校验通过；旧证据问题单独留存，不能宣称旧清单
已经恢复有效。若要修复历史源与清单，需要另行明确修复范围和批准，不能用当前文件哈希覆盖历史证据。

## 文档闭环与最终状态

- 提交边界：用户随后要求“提交代码”，本次提交只收录共享WXSS修复、本DREV/证据和既有文档的对应增量。
  工作树中的FEAT-011正文与其旧通知DREV清单属于另一项尚未提交的任务，本轮加入的视觉说明/替代指针随其保留，
  不将整份并行任务纳入本次提交。相同提醒背景事实已独立写入本次提交的FEAT-003、UI-011和新DREV清单。
  六份Feature及三份旧清单的下述同步数量描述工作树；本次提交包含五份既有Feature和两份既有清单增量。
  原生/设计对照使用验证时工作树的合成展示，不能推广为排除并行功能后的完整提交树验收。
- 六份Feature当前正文加入 `FEAT-VISUAL-20261021-HERO-ARC-01`，三份UI正文加入
  `UI-VISUAL-20261021-HERO-ARC-01`；前端设计正文、Spec、索引与批准清单同步本次局部事实。
- Behavior Catalog：无交互/业务改变，原条款继续有效，无需新增行为ID或改写当前业务事实。
- Architecture：没有模块/依赖/扩展点改变，原正文继续有效；本轮架构DAG检查通过。
- TEST-STRATEGY/FEC：政策不变；实际执行与未执行项在本证据逐项记录，不把部分原生结果写成全量通过。
- 发布文档：无上传/部署事实变化，既有线上记录保持原状；未为本轮制造发布版本。
- 在本次diff范围内未发现代码与已同步正文冲突；上述既有旧邀请设计证据不一致已独立列出，未掩盖或重写。
  这也不代表并行工作树其他任务已完成验收。

生产修复与自动化已完成，但完整原生截图、字体放大/长内容、iOS/Android与用户视觉验收尚未齐全，
因此Spec为VERIFYING、保留 `specs/active/BUG-030-HERO-BACKGROUND-ARC.md`，不设DONE、不移completed。
后续从上述缺失矩阵恢复；满足全部验收后再闭环归档。回滚仅恢复原伪元素和对应注释，无数据迁移。
