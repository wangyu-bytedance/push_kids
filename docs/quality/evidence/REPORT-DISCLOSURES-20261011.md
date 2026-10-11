# 报表折叠区本地验证 — 2026-10-11

对应 `SPEC-20261011-REPORT-DISCLOSURES-01`、`DREV-20261011-REPORT-DISCLOSURES-01`。这是本地实现证据；未上传小程序，也未进入体验、审核或生产状态。

| 测试点 | 结果 | 证据 |
|---|---|---|
| TP-001 设计和原生矩形 | PASS | 已批准的12张 SVG/PNG 与 SHA 清单校验通过；微信开发者工具 Stable 2.01.2510290、SDK 3.16.2 下，320×568、390×844、430×932 的 collapsed/history-open/review-open/both-open 共12态均通过 `tools/report_disclosure_geometry.js`。屏幕高与矩阵一致，科目→历史→编辑计划→活动顺序正确，区块无越界/覆盖；历史搜索区仅展开时挂载，编辑计划展开区高度大于标题区。两块标题点击区最小 290×61px（320视口）、354×73px（390视口）、390×80px（430视口），均超过44px。 |
| TP-002 独立状态与按需读取 | PASS | `tests/frontend/report-disclosures.test.js` 验证首次折叠、只取有界待处理计数、展开才取完整历史、两区独立、离页收起。 |
| TP-003 既有列表合同 | PASS | `npm test` 219/219；历史筛选/分页/详情及复习目录现有测试通过。同一提交产生多个正式记录时，以 `record_id` 作行键，开发者工具不再报告重复键；嵌入组件不再报告禁用的 WXSS 选择器。 |
| TP-004 意图和隔离 | PASS | 前端测试覆盖今日/科目意图、切孩子、旧请求迟到、只读/空态等已有和新增回归；开发者工具原生展开视图确认完整历史与编辑计划内容实际渲染。 |
| TP-005 工程检查 | PASS | `npm run lint:miniapp`；`npm run check:miniapp`（16 pages、724195 source bytes）；`python3 tools/check_architecture.py`（checked=3）；`python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261011-REPORT-DISCLOSURES-01/APPROVAL.md`；`python3 tools/validate_design_evidence.py --check-current-policy`；`git diff --check`。后端 API/Schema 未改，后端测试 N/A。 |
| TP-005 iOS/Android 真机 | NOT_RUN | 本轮没有连接真机；仍是完成/发布门禁。 |

原生校验只输出匿名数字矩形与布尔展开状态。真实孩子内容、图像、ID、请求体和设备截图未写入仓库。可复核脚本：`node tools/report_disclosure_geometry.js capture <state> <width> <output.json>`，在对应微信开发者工具模拟器机型下运行；再用 `audit <output.json>` 复核。
