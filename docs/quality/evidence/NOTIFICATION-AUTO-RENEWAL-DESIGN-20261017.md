# 提醒授权自动补充 — 设计期证据

- Date: 2026-10-17
- Task Spec: [SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01](../../../specs/active/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md)
- Design Revision: [DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01](../../design/frontend/prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/FRONTEND-SPEC.md)
- Feature: FEAT-011 / PLANNED；业务实现及发布不在本证据范围
- Subject: 当前候选HTML；精确SHA-256见[UI-001清单](../../design/frontend/snapshots/UI-001/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md)与[UI-011清单](../../design/frontend/snapshots/UI-011/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md)
- Subject SHA-256: `42980beb99cbbfac02da683809fdb567d2f5ed0c096d9109b97732431aa95e32`（最终index.html；变更后本证据应标stale重验）
- Code baseline: 8f3c5b04e61c96d4c19cf9eefd26514a8a095e1a；既有诊断/测试差异保留；本轮无生产业务代码修改
- Approval: 仅需求共识已确认；Spec/架构/设计批准PENDING

## Executed checks

| Command / case | Result | Actual scope |
|---|---|---|
| python3 .../render.py（系统Chrome channel） | PASS — 42 exports | 2个UI-001状态 + 12个UI-011状态，各320×568/390×844/430×932，DPR1 |
| renderer DOM assertions | PASS | 42态无pageerror、无根横向溢出、按钮至少44×44且水平包含；首次说明两个按钮完整处于视口 |
| candidate manifest validator（两个清单，--allow-pending） | PASS | DESIGN_EVIDENCE_VALID；精确尺寸/42张PNG及源SHA正确，**不是审批通过** |
| .venv/bin/python tools/validate_design_evidence.py --check-current-policy | PASS | DESIGN_EVIDENCE_VALID |
| .venv/bin/python tools/check_architecture.py | PASS | ARCHITECTURE_VALID checked=3；当前实现检查，不证明未来依赖已实施 |
| .venv/bin/ruff check / format --check（render.py） | PASS | All checks passed / 1 file already formatted |
| node inline script syntax compilation | PASS | DESIGN_JS_SYNTAX_PASS；只编译本地HTML内嵌JS |
| local Markdown references / git diff --check | PASS | 新文档和索引目标存在；无diff空白错误；新增设计文件也做空白检查 |
| rendered review | PASS（设计范围） | 查看320首次说明、320冷却、390正常、430部分类型、390登记待恢复、320错误、430无额外提示；不作为原生验收 |
| python3 /private/tmp/push-kids-renewal-design-review.py | PASS（设计范围） | 本机HTTP预览：视口/状态选择、初始焦点、循环Tab、Shift+Tab、Escape取消、按钮不伪造额度；外部请求0/pageerror0 |

导出机器记录：[render-audit.json](../../design/frontend/prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/render-audit.json)。
交互机器记录：[interaction-audit.json](../../design/frontend/prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/interaction-audit.json)。
DOM检查仅针对本地HTML，不能替代微信原生矩形、字体放大、读屏或真机授权证据。

## Environment limitations and resolved checks

- 初次启动默认Playwright失败：本机缺少它对应的chromium headless shell；没有下载/安装浏览器。
- 改为已安装系统Chrome；sandbox内启动被系统终止，批准的隔离headless本地导出随后成功。仅file本地页面，不访问微信/业务接口、不发送通知。
- `uv run ruff`未运行成功：默认uv缓存目录不可访问；使用现有`.venv/bin/ruff`复核，不读取业务凭据、不修改依赖。
- 最初脚本存在2处E501及格式问题；后续修正，最终结果以Executed checks为准。
- 预览交互初测发现iframe导航使演示消息来源失效；已改为由父预览收到演示消息后导航，最终实际交互通过。过期/未知状态标题已改为中性待确认文案，并重新导出全部候选。

## Not run / facts not claimed

业务实现、Python/JS业务测试、数据库迁移、真实MySQL5.7、原生DevTools编译/矩形、iOS/Android、字体放大/读屏、真实授权与发送均NOT_RUN，原因是当前只形成待批准方案。
无git提交/推送、小程序上传/体验/提审/正式发布、云版本/权限/流量修改。
2026-10-17的0F58成功收件属于既有通知链路，不作为FEAT-011证据。

## Documentation closure

- 已创建PLANNED Feature、active/READY_FOR_REVIEW Spec、设计说明、候选源/导出/清单和索引。
- 核对FEAT-003、FEAT-001、Behavior Catalog、Architecture、UI-001/UI-011、测试策略与发布手册：本轮没有实现新行为，现有当前正文不改成目标事实。
- UI-011旧的设计/原生缺口不被本次候选或历史收件记录追认；已有批准快照保持不变。
- Spec尚未完成，留在active；只有审批、实现、测试与验收门禁完成后才迁移completed。
