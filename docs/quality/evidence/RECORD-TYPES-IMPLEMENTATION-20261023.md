# 记录类型切换与足迹文案 — 本地实现（2026-10-23）

- Status: LOCAL_IMPLEMENTATION / VERIFYING / NOT_RELEASED。
- Approval: 用户选中“标题切换 · 推荐”后要求“完成这个功能的代码编写”，2026-10-23。对应[入口Spec01](../../../specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md) / Architecture01 / DREV-20261023-RECORD-TYPE-SWITCHER-01，以及[文案Spec01](../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md) / DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02。
- 主功能[Spec04](../../../specs/active/FEAT-012-CHILD-PHOTO-FOOTPRINTS.md)仍VERIFYING，本轮不降低其首版全球地图、照片/AI效果和真机要求。
- 工作区包含其他通知/词条替代/背景任务的未提交变更；全仓检查结果不表示这些变更属于本任务。无提交、上传、部署或发布操作。

## 实现与边界

记录Tab标题切换“学习记录 / 旅行日记”，首次学习、普通Tab返回记住类型，保留五Tab和知芽品牌栏。学习文字、照片、日期、孩子、幂等键和滚动跨切换保留；旅行孩子选择独立，归档旧草稿继续可达。明确学习recordIntent经相同离开保护切回学习，不消耗被取消的意图。

旅行Page与内嵌组件共用footprints/controller工厂、WXML和WXSS，业务继续归footprints领域；records只协调类型、学习生命周期和孩子/弹层事件。上传中阻止离开，编辑离开须确认；后台/卸载取消轮询、回放和迟到响应，清理预览。相册尚未打开时若已经卸载，不再延迟打开原生选择器。上传中的后台状态不会提前解除保护。

文案删除重复教学、处理细节和来源标签堆叠，保留家长确认、未知/失败、AI候选、同意、具体到期、删除后果和地图示意；细则集中现有设置。组件样式使用class选择器，避免微信组件不支持tag/attribute选择器造成样式丢失；授权文字允许在窄屏收缩换行。类型菜单和旅行面板打开时隐藏底部导航，关闭/卸载/离页恢复，避免实际截图暴露的遮挡。

无API、数据库、权限、AI调用范围或依赖包变更；旧足迹深链接保留。不用文案精简宣称全球底图已经完成，当前全球仍为坐标点位示意和列表。

## 实际检查

| 检查 | 结果 | 说明 |
|---|---|---|
| `npm test` | PASS，275/275 | 本轮最终源码；切换/表单保留、上传/编辑保护、意图、归档孩子、迟到响应、轮询/回放清理、TabBar恢复及原足迹业务回归 |
| `npm run lint:miniapp` | PASS | 原生源码及前端测试ESLint |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS | 17 pages，source_bytes=1163980；静态源预算，非微信上传包大小 |
| `.venv/bin/python tools/check_architecture.py` | PASS | policies=4，modules=130，runtime/lazy DAG |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | PASS | 设计证据及当前治理文本 |
| `.venv/bin/ruff check .` / `ruff format --check .` | PASS | 621 Python文件已格式化；本轮仅验证工具格式修正，无后端业务修改 |
| `.venv/bin/mypy apps/api/src` | PASS | 130 source files；既有reads.py未注解函数体提示仍存在，未把它称为全类型覆盖 |
| 足迹后端相关pytest | PASS，24 passed / 1 skipped | 下方列明5个测试文件；MySQL环境未配置而skip，12条既有告警；SQLite/元数据/迁移/有界读回归 |
| `git diff --check` | PASS | 当前工作区空白检查；收尾后复跑 |
| 独立只读代码review | PASS | footprints_readonly_review最初找到3个P1，均修复并补回归；随后目标21/21及ESLint通过，未发现新的可证实代码阻断项。最终原生/文档单独核对 |
| 独立最终证据/文档review | PASS（解锁前范围） | 独立重算38源及87对JSON/PNG共212项SHA全匹配；当时仅430的29态有效，58份中间记录排除。三份有效设计清单严格通过，19份文档154个本地链接有效，三Spec active/VERIFYING；解锁后的87份当前证据另行复核，不把旧复核范围扩大 |
| 解锁后独立最终复核 | PASS（合成布局及本轮代码/文档范围） | 独立重算212项SHA全部匹配；29态×320/390/430共87份均对应当前源码，33份隔离副本扣除声明注入后逐字节一致。320授权文字完整，菜单、三候选和照片面板未见遮挡；19份相关文档168个本地链接有效，三Spec仍active/VERIFYING。未发现可证实问题；完整设计、字体/键盘/读屏、插件包、真机和真实服务验收仍PARTIAL |
| 新入口设计导出 | PASS（设计范围） | 四态×320×568/390×844/430×932，共12 PNG及SHA；输入保留/菜单关闭点击通过。HTML不代验原生 |
| 三份有效设计清单严格校验 | PASS | 新入口APPROVAL-CORRECTED.md、足迹DREV02及DREV01分别以`--manifest`验证源/PNG/SHA/批准元数据；不是只运行政策模式 |
| 本地Markdown链接检查 | PASS | 首轮86个目标均存在；增补设计规格/更正清单后92个目标均存在；解锁后独立复核19份当前文档168个本地链接全部有效 |
| 当前原生节点/截图 | PASS（29态×3合成布局），整体验收PARTIAL | 用户解锁后最终320×568、390×844重新采集全部通过；加430×932共87份节点/PNG，全部绑定未变最终源码。审计操作区/字体/边界/间距/菜单/TabBar遮挡；目检小屏菜单、授权、候选、照片面板。详见[范围与源清单](record-types-20261023/native/README.md)，不代验完整设计/真机/真实服务 |

足迹后端命令：

```bash
.venv/bin/python -m pytest tests/unit/test_footprint_metadata.py tests/integration/test_footprints.py tests/integration/test_footprints_migration.py tests/integration/test_footprints_mysql.py tests/performance/test_footprints_reads.py -q
```

未重跑全部后端套件：本轮没有后端业务变更，执行上述受影响足迹回归及全仓静态检查。`uv run`首次受到用户cache路径沙箱权限限制，后续使用已安装的`.venv`执行，不宣称`uv run`命令成功。设计导出和本地DevTools官方CLI需升级执行权限，已通过自动审核；没有自动审核拒绝或素材外发。

新入口首次严格清单校验失败：Frontend spec path误指`specs/active/`的Task Spec，校验器要求同DREV的prototype规格。已补齐FRONTEND-SPEC.md并创建[APPROVAL-CORRECTED.md](../../design/frontend/snapshots/UI-001/DREV-20261023-RECORD-TYPE-SWITCHER-01/APPROVAL-CORRECTED.md)，旧批准清单只添加Superseded by指针。更正仅涉及元数据路径，无HTML/PNG/范围或批准变化；原错误不隐藏，最终有效清单严格通过。

## 文档与生命周期核对

| 文档 | 当前处理 |
|---|---|
| FEAT-001 / FEAT-012 / Feature索引 | 替换旧提示条/候选未实施事实，记录标题切换、文案和当前验证范围 |
| Behavior Catalog | 新增BHV-041；BHV-038/039/040的确认/过期/全球地图合同保持 |
| Architecture | 新增ARCH-20261023-RECORD-TYPE-SWITCHER-01，明确领域控制器复用、closed两项类型及无API/schema变更 |
| UI-001 / UI-018 / FRONTEND-DESIGN | 更新有效入口/文案设计；旧入口/装饰标题标为历史，明确原设计差异未验收 |
| Spec / 索引 | 入口、文案和主Spec04均active/VERIFYING；本地代码完成不等于验收DONE，无误迁移completed |
| 批准源/清单 | DREV01/02/新入口HTML和PNG冻结；旧清单只添加允许的Superseded by状态指针，历史候选描述不作当前事实 |
| 历史测试证据 | 保留历史数值/范围，加指向当前证据的说明；未用历史72原生图验收当前diff |
| TEST-STRATEGY / 权限、归档与清理Feature | 核对现行原生/回归门禁及家庭scope合同；本轮无政策/服务合同变化，不改其正文，不宣称真机或MySQL通过 |
| 发布文档 | 更新2026-10-23本地增量，迁移0021为历史足迹head、当前0022属其他任务；部署/上传/体验/审核/正式发布保持NOT_RUN |

未发现本轮已实现行为和已同步当前正文之间的未解释冲突。主Spec04既有设计差异继续列为开放验收，不以文档修订掩盖。

## 未完成验收与恢复条件

字体放大、键盘/读屏、完整语音插件包、iOS/Android真机和文案完整27态逐态核对未完成。锁屏阻断已由用户2026-10-23“已解锁，继续验证”解除，最终三尺寸87份合成原生布局已完成，不再列为阻塞。真实选图EXIF保留率、2048展示清晰度、AI地点真值/供应商隐私、全球真实底图/商用账号、MySQL5.7及云私有对象验收仍由主Spec04跟踪。无这些通过证据，不能宣称完整功能已验收或可发布。

代码编写已完成，入口Spec01、文案Spec01和主Spec04继续留在`specs/active/`，Status为VERIFYING。完成全部各自验收门禁后才设DONE并迁移`specs/completed/`。本轮没有发布授权，不创建发布包或触发人工发布流程。
