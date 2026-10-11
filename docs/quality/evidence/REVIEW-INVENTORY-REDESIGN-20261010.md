# 复习条目清单式改版 — 本地验证记录

- Spec: `SPEC-20261010-REVIEW-INVENTORY-REDESIGN-01`
- Design: `DREV-20261010-REVIEW-INVENTORY-02`
- Date: 2026-10-10
- State: local implementation, native simulator geometry passed; iOS/Android physical-device acceptance not run; no new front-end upload or release

## Implemented behavior

- 删除内容区重复标题及泛化说明；时间、科目、次数三种视图各只有一层筛选。
- 明天/后天为同排两段选择；科目/次数为显示当前值的单入口下拉，选项在小程序原生节点内展开，指定次数仅确认后应用。
- 时间/次数继续按当前有界页的科目独立折叠；单科直接显示有分隔线的清单。条目显示完整标题、真实复习次数、最近反馈、日期及今日安排状态；44×44“…”菜单保留原排期/删除调用。
- 翻科目页不再暗中改变已选科目。选择、翻页、旧响应、只读及失败状态仍由现有页面流程处理；服务端策略和API未改。

## Verification

| Gate | Result | Evidence |
|---|---|---|
| Frontend focused | PASS | `node --test tests/frontend/review-inventory.test.js tests/frontend/review-inventory-geometry.test.js` — 18/18 |
| Frontend suite | PASS | `npm test` — 216/216 |
| Lint/static | PASS | `npm run lint:miniapp`; `npm run check:miniapp` — 16 pages, 718445 source bytes |
| Design manifest | PASS | `python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261010-REVIEW-INVENTORY-02/APPROVAL.md`; `--check-current-policy` |
| Architecture | PASS | `python3 tools/check_architecture.py` — checked=3. `uv run` entry first failed because sandbox could not read the global uv cache; direct Python command then passed. |
| Native geometry | PASS | WeChat DevTools Stable 2.01.2510290, 320×568 / 390×844 / 430×932; numeric captures in `docs/quality/evidence/review-inventory-redesign-20261010/`, ten JSON files. `node tools/review_inventory_geometry.js audit .../*.json` — 10/10. Time views include opened “…” menu and a visible second-row upward-menu case at 320px; subject/count views include opened selector. |
| Native visual | PARTIAL | DevTools screenshots manually inspected at 390 time and 320 count expanded. No screenshots with child content stored in repository. |
| iOS / Android physical device | NOT_RUN | Requires separate device acceptance; simulator rectangles do not prove platform-font and gesture behavior. |
| Backend tests / cloud release | NOT_RUN | No backend code, schema, or API change; no upload/deployment in this task. |

During native verification, the first time selector rendered at 38px despite `min-height:44px`; it was corrected with an explicit 52px track and 44px segment height. The first subject trigger rendered at WeChat's 184px default width despite `width:100%`; it was corrected with a full-width WXML `view` carrying button semantics. Both issues are now checked by numeric renderer bounds instead of inferred from WXSS.

The capture JSON is limited to viewport and node rectangles; it contains no child names, knowledge titles, IDs, credentials, or image data. The approved design manifest remains unchanged after approval. The Spec stays in `VERIFYING` until risk-state exports and physical-device acceptance are complete.
