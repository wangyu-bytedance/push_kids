# UI-001 — DREV-20261006-REVIEW-MANAGEMENT-03 Candidate Evidence

- Status: DRAFT
- UI ID: UI-001
- Design Revision: DREV-20261006-REVIEW-MANAGEMENT-03
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Task Spec path and revision: specs/active/FEAT-001-REVIEW-INVENTORY-AND-RESCHEDULING.md#SPEC-20261006-REVIEW-MANAGEMENT-03
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-03/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-03/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-03/index.html=ec597735143ddda77e6430c6054a5edd6abfd95a5814fc4254708d90ac712933
- Prototype generated/updated at: 2026-10-06
- Approved by: 产品负责人（用户）；批准设计方向及本地实施，不代表导出证据已齐备
- Approved at: 2026-10-06
- Approval evidence: 本会话“落地并实现”，对应SPEC-20261006-REVIEW-MANAGEMENT-03；Status仍为DRAFT以标示缺少导出
- Superseded by: N/A

## Scope

修正用户截图指出的次数筛选交互：直接点选次数，指定次数用弹层确定，取消不改变结果；移除重复排序文案和假交互外观。保留02版红色删除和单科样式。
03设计评审后用户已批准实施，原生源码本地实现；01版截图仍为历史证据，不作为03版视觉验收。

## Export manifest

NOT_RUN：要求18状态×320×568、390×844、430×932，共54张；本轮未导出。
浏览器工具明确拒绝file://本地预览访问；没有采用其他浏览器表面绕过策略，也没有自动刷新现有标签页。
本清单尚未满足完整设计批准门禁，不能声称DESIGN_EVIDENCE_VALID。

## Verification evidence

- Node VM源码解析与状态/事件处理检查：PASS；执行 node /private/tmp/check-review-management-03.cjs。
- 科目无全部、默认语文/数学/空科目；红色删除样式保留：PASS。
- 次数筛选移除select；直接点击0/1/2/3次；全部时只有一次固定排序说明，具体次数没有排序说明：PASS。
- 指定次数弹层：未确定保留旧结果、取消不应用、确定6/8次精确匹配和空态：PASS。
- 非法负数/小数/空值/越界保留弹层与旧结果；自定义输入3选中3次快捷项：PASS。
- 本轮只读用户附图和本地源码，不再次请求被策略禁止的浏览器访问。
- 浏览器渲染/节点几何/PNG导出、原生三视口/iOS/Android、生产业务测试：NOT_RUN。
- 本检查是设计交互逻辑验证，不是完整DOM、视觉或原生验收。

## Approval gate

具体Spec+Design的实施批准已记录；仍需补齐本修订导出、hash和原生视觉证据才能关闭验收门禁。
2026-10-06原生检查尝试的DevTools自动化启动失败；随后自动审批明确拒绝界面检查并视为绕过此前访问限制，
已停止该路径。此文件尚非完整冻结视觉manifest；未修改03版可编辑HTML及其hash。

