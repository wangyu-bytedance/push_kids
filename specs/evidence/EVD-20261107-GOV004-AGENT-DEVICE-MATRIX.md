---
created: "2026-11-07"
updated: "2026-11-07"
type: evidence
status: verified
owner: Codex
---

# GOV-004 Agent 设备矩阵验证

- Evidence ID: `EVD-20261107-GOV004-AGENT-DEVICE-MATRIX`
- Requirement / acceptance: [GOV-004 TP-01–04](../completed/GOV-004-AGENT-DEVICE-CHECK-MATRIX.md)
- spec_revision: `GOV-004-SPEC-01`
- subject_revision: `925a8a49ea972f365e17ed1504575ac49deef65a` 加当前工作区治理增量，下列工具与测试按 SHA-256 绑定。
- result: `passed`，范围为本地治理、离线工具和兼容性验证。
- 环境：macOS，Node 22.22.0，项目 Python 3.12.11，HTML 截图使用系统 Python 3.9.6、Playwright 1.59.0 的 Chromium。

## 执行结果

| 测试点 | 命令或方法 | 实际结果 |
|---|---|---|
| TP-01 | 在临时副本运行 `node tools/preview/render.js today`；预置一个旧 `today-320.html` 后执行 `python3 tools/preview/shoot.py today`，读 PNG IHDR | 只生成两档 HTML；真实 Chromium 只输出 390 和 430 预览，2x 视口 PNG 为 780×1688、860×1864。旧 320 文件未截图。 |
| TP-02 | `uv run pytest tests/unit/test_validate_design_evidence.py -q` | Baseline 9 PASS。加用例后的预期 Red 为 2 FAIL / 11 PASS，新候选与批准清单均误报缺 320×568。Green 为 13 PASS，新矩阵两档缺任一档时分别报错，旧矩阵仍要求 320×568。 |
| TP-02 | 读取 `git show HEAD:tools/validate_design_evidence.py` 作为基线，对 84 份历史 `APPROVAL.md` 分别比较新旧 `validate_manifest` 的逐文件诊断 | 诊断逐份一致。候选模式 44 通过、40 既有缺项；严格模式 37 通过、47 既有缺项。DREV09 的 `--manifest` 单独通过。 |
| TP-02 | `uv run python tools/validate_design_evidence.py --allow-pending --manifest docs/design/frontend/snapshots/UI-001/DREV-20261107-HEADER-BLEND-01/APPROVAL.md` | 新 FDB 的实际两档候选通过，设计仍待批准。 |
| TP-03 | `node tools/theme_native.js --list-viewports`；执行 `node tools/theme_native.js 375`；在临时目录用空场景连接替身运行主题入口 | 列表仅输出 `390x844`、`430x932`。375 在建立连接前拒绝；默认报告写入 `dist/theme-native/390`。 |
| TP-03 | 模拟 `WebSocket` 对现有 time 视图节点夹具补充 `screenWidth`/`screenHeight`，通过 CLI 执行 `capture`；运行 `node tools/review_inventory_geometry.js audit docs/quality/evidence/review-inventory-redesign-20261010/review-inventory-{time,subject,count}-{320,390,430}.json` | 390×844、430×932 及显式历史 320×568 通过，430×844 在写出证据前被拒绝。9 份旧矩形证据重放通过。首次本地连接替身处理空 RPC 参数时失败，修正替身后通过。 |
| TP-04 | `npm test`、`npm run lint:miniapp` | 369 PASS；ESLint PASS。 |
| TP-04 | `uv run python tools/validate_design_evidence.py --check-current-policy`、`uv run python tools/check_architecture.py`、`uv run python tools/validate_miniprogram.py` | 设计政策通过，架构 5 policies / 156 modules，通过 17 页及 1,322,435 字节小程序静态检查。 |
| TP-04 | `node --check` 检查三个修改的 JS 工具，`uv run ruff check` / `uv run ruff format --check` 检查三个修改的 Python 文件，`git diff --check` 与本任务链接检查 | 通过，36 处本地引用验证。首轮 Ruff format 检出测试参数排版，修正后重跑通过。 |

项目虚拟环境未装 Playwright；取消隔离安装尝试后，实际截图使用本机已有 Playwright/Chromium。截图与连接替身均在临时目录执行并清理。未运行微信 DevTools 原生呈现、真机、可访问性和完整业务端到端，本任务只验证离线规则和取证入口，后续由产品任务和发布验收分别记录。后端全量业务测试、MySQL、云部署、上传、体验、提审和正式发布均不适用此治理增量。

## 只读复核与文档闭环

首轮 `CR-001` 核实主题取证默认目录可能覆盖历史 `native/390` 报告。改至 `dist/theme-native` 后复验默认目录，显式 `--output=` 继续支持归档。增量复核确认规则和代码一致，零个未关闭问题。复核为本任务的同上下文 R1 只读检查。

| 逐项范围 | 必要性与放置 |
|---|---|
| `AGENTS.md`、`REVIEW.md` | 必要，Agent 与审查的入口规则各引用当前矩阵。 |
| `FRONTEND-DESIGN.md`、`FRONTEND-ENGINEERING-CONSTRAINTS.md` | 必要，分别持有现行矩阵和原生几何证据要求，旧 DREV 保留原版本。 |
| `ARCHITECTURE-CONSTRAINTS.md`、`TEST-STRATEGY.md`、`WECHAT-MINIPROGRAM-API-BASELINE.md` | 必要，分别替换约束、测试入口和 API 平台测试中的生效旧矩阵。 |
| `docs/deploy/README.md`、`FRONTEND-RELEASE.md` | 必要，发布引用当前原生矩阵，专项真机平台能力保留。 |
| `FEAT-001`、`UI-001`、`UI-010`、`UI-015`、`UI-016`、`UI-017` | 必要，当前正文原检查要求统一引用矩阵；Feature/UI 业务事实不变。 |
| `DESIGN-002`、`DESIGN-003`、`design003-20261107/README.md` | 必要，后续通用检查切换两档，历史 DREV 与执行证据分开标识。 |
| `tools/frontend_viewports.json`、`tools/validate_design_evidence.py` | 必要，唯一机器可读版本配置与校验消费端，保留旧清单契约。 |
| `tools/preview/README.md`、`render.js`、`shoot.py` | 必要，走查说明、HTML 生成和截图共享矩阵，历史输出不会重新枚举。 |
| `tools/review_inventory_geometry.js`、`tools/theme_native.js` | 必要，原生取证消费共享配置、验证精确尺寸并保留历史重放路径。 |
| `tests/unit/test_validate_design_evidence.py` | 必要，测试新旧证据版本的兼容边界。 |
| `specs/README.md`、`specs/STATUS.md`、GOV-004 及本证据 | 必要，批准、开发归档及证据引用可追溯。 |

已核对 Behavior Catalog 和 Architecture 当前事实，生产路径、依赖方向和业务状态无变化，因此两份正文无需修订。批准快照及历史取证数据未因本任务修改。没有发现本次引入的冗余或错层。历史脚本明确指定旧宽度时仍可用于专项复现，现行默认计划只取两档。

## 工具与测试 SHA-256

```text
515dcb68b97cc3fb2d6ec3a5d97d032d1c9ce2754d7d9a33ec4f4d8759a802a0  tools/frontend_viewports.json
4f718bb7d9ef4f398b2d0e6048e6911636ca12245ccd64b519a17b490f5da04c  tools/validate_design_evidence.py
2de781bb3e8e7446a80ce27f6cf66e6a3314e6d54e7c35e1cef1be88635a592a  tools/review_inventory_geometry.js
65564e34f12f3959673b20f21def2b35d7adf1db67117134e170371c948ee1d0  tools/theme_native.js
5f7d679d31f5a7ee6341d73fb22051ac3deca49c5fb2564727427b2ee0f01e5b  tools/preview/render.js
931a18d8ec1faa8dd8c8e1fd0bcd74584e89674dd18ed1ac34449e05eab6b412  tools/preview/shoot.py
0c5ab8f422e9918a20ac015d5f9882906d79c7e0fa8c205815e7ac5c1abbb639  tests/unit/test_validate_design_evidence.py
```
