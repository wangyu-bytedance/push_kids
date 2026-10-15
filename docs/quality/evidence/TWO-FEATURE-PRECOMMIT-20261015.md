# 两项功能提交前代码与文档核对

用户2026-10-15要求“当前工程有2个feature修改，提交代码，验证doc的正确定”。提交范围为已批准的学科管理与按钮/分页两项变更，以及已有已批准DOC-002治理修订；未批准的DOC-003仅保留待审范围，不将其声明为完成。

## 实现及文档对应

| 范围 | 代码与事实核对 | Spec / 生命周期 |
|---|---|---|
| 学科管理 | settings三文件及settings-state测试；整行打开面板、移出需确认、active=false保留记录、只读与canRemove限制、防重和迟到回调保护；FEAT-001、UI-001、BHV-036与实现一致 | SPEC-20261014-SUBJECT-MANAGEMENT-01，active/VERIFYING |
| 今日按钮及编辑计划分页 | today局部pill及去阴影；共享inventory专用两/三列分页及禁用透明底；未改JS、统计pager或API；FEAT-010/001、UI-001与实现一致 | SPEC-20261014-ACTION-PAGER-CONSISTENCY-02，active/VERIFYING |
| 架构及发布 | 无新模块/依赖/接口/数据库；最新开发上传仍0.1.15，本轮未上传/体验/提审/正式发布 | 本轮无需迁移；历史发布证据不作为当前测试结果 |

修正Spec索引将早期“最终变更记录”明确标为历史，补齐两项当前入口。历史243项测试是按钮实现当时结果；本轮最终联合工作区重新运行244项全部通过，不能将历史结果误认为最终diff证据。

## 本轮实际执行

- PASS：npm test，244 passed / 0 failed；npm run lint:miniapp。
- PASS：.venv/bin/python tools/validate_miniprogram.py，16页，source_bytes=1070913（源码，不是上传包）。
- PASS：.venv/bin/python tools/check_architecture.py，checked=3。
- PASS：validate_design_evidence.py --check-current-policy，及学科VALIDATION.md、按钮/分页APPROVAL.md两份manifest校验。
- PASS：git diff --check。
- 原生证据核对：学科三宽24组数字几何，按钮/分页430宽11态采样；沿用各自证据文件，本轮未重跑原生。原生截图、真机和读屏缺口保留；两Spec不能DONE或移动completed。
- 后端测试N/A：本轮仅前端及文档，无后端修改。

## 必要性与放置核对

settings三文件/测试及学科原生采样工具必要，位于既有页面/测试/工具；未创建共享抽象，旧行操作路径已删除。today及inventory三文件必要，样式局限对应控件、共享content覆盖两个消费者，无重复页面实现。两套设计源/冻结快照与各自Spec、Feature/UI/Behavior、测试和发布记录为可追溯证据所需；旧按钮修订01保留历史设计候选，不作为当前验收。治理改动按DOC-002原批准范围独立提交。DOC-003保持READY_FOR_REVIEW，不纳入功能完成结论。未发现本轮代码与对应当前文档的未披露冲突；完整视觉及真机正确性仍缺证据。
