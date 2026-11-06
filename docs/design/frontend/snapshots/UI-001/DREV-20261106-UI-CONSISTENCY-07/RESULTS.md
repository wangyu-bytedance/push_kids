# DREV07 preparation results — 2026-11-06

本轮仅实施用户明确授权的AGENTS工程规则，准备原生主题实施合同及设置顶部交互设计。**小程序换肤代码尚未实施**。

| 检查 | 实际结果 | 证据/边界 |
|---|---|---|
| self-contained build | PASS | index.html，五张既有插画+原始书本图，无新外网依赖 |
| 6主题×3视口×3状态 | PASS / 54 HTML exports | verification.json；检查横向越界、44px按钮触区、面板顶界 |
| 局部应用/取消等交互 | PASS / 15 | 六主题应用与取消12项，未知ID回退、Escape焦点返回、焦点圈闭3项 |
| console / external HTTP | PASS / 0 / 0 | 同一预览运行，不代表真实业务网络 |
| 目视 | PASS（设计稿范围） | 六主题overview，三尺寸面板及深色；不是原生验收 |
| 旧DREV01–06 SHA | PASS | 134/135/22/11/11/1005条逐项比对，未改写旧设计 |
| 当前源/PNG SHA、尺寸与文档链接 | PASS | 12个源、55张PNG、10条本地链接、Spec06逐字副本均通过 |
| apps source | PASS / 355 unchanged | 对比DREV06 production-before及本轮baseline；排除Python字节码缓存 |
| `uv run python tools/validate_miniprogram.py` | PASS | pages=17 / source_bytes=1244228，是原始生产基线，非新主题包体 |
| `uv run python tools/validate_design_evidence.py --check-current-policy` | PASS | DESIGN_EVIDENCE_VALID；不是本待批实施稿的原生验收 |
| 原生/450组/设备/读屏/大字/真实偏好恢复 | NOT_RUN | 生产实现前准备阶段 |
| 插画压缩/最终包体/300ms切换/生产对比度 | NOT_RUN | Spec07列目标和失败处理，未宣称已达成 |
| 设计脚本ruff check / format --check | PASS | DREV07目录专项；首轮长行/格式FAIL，修正后两项通过 |
| 前后端业务suite/miniapp lint/mypy | NOT_RUN | 无apps代码diff；设计脚本检查不代验生产 |
| 上传/体验/提审/正式发布 | NOT_RUN | 本轮无授权也无平台写入 |

## 测量与设计决策

- 实测原始小程序168文件、1,244,228字节；检查器上限1,500,000字节，剩余255,772字节。
- 五张设计原图8,419,871字节，不能打入生产。拟保留五种插画/材质，使用本地小图及一套共享业务和glyph路径；最终预算另验。
- 主题状态只存本机白名单ID，不增加后端配置、AI图标或课程等待；未知直接用各主题固定图标。
- 六主题测试从同一registry派生；共享业务只跑受影响流程，主题呈现仍逐主题检查。Spec07全局首次矩阵450组；后续局部UI无需无条件重跑全产品。

## 本轮实际diff与文档闭环

| 层 | 处理 |
|---|---|
| AGENTS | 新增用户明确要求的六主题适配、集中token/资源、默认图标、动态枚举和预算/证据约束 |
| Spec | 原Spec06逐字保留到evidence；当前Spec07/Architecture01 READY_FOR_REVIEW，仍active |
| Design | 新增DREV07源、55张PNG、交互/几何报告、SHA与批准记录；DREV01–06不变 |
| STATUS | 将设计06扩展阶段更新为六主题实施准备07，明确NOT_STARTED和待具体批准 |
| Feature / Behavior / Architecture / UI / FDB / FEC | 与未改动的apps代码核对后保留当前生产正文；不把待实施提案冒充CURRENT；实施后按Spec07逐项合并 |
| 代码与设计差异 | child-edit原生有预算字段，DREV06曾省略；本Spec明确保留，不能随主题删除；其他设置字段/权限仍按真实业务 |
| 测试与发布 | 未做生产测试或发布，不覆盖旧证据，不以本轮HTML代验原生/设备 |

无生产diff导致的当前事实冲突。待确认Spec07（含Architecture01）+DREV07后才启动原生代码；本地设计完成不满足云交付DONE规则。

工具环境：build/Playwright verify用系统python3；finalize首次误用系统Python3.9导致datetime.UTC ImportError（FAIL），按项目要求改为`uv run python`的3.11+环境执行。该失败保留，不影响已导出图像；完整性是否通过以实际后续命令为准。

后续`uv run python .../finalize.py`已实际PASS；收尾源/PNG维度与SHA、本地链接和`git diff --check`也已实际通过。与旧DREV06的355份apps源码一致；没有运行时换肤实现或新云交付。
