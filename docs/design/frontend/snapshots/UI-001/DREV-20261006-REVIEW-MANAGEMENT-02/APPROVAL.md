# UI-001 — DREV-20261006-REVIEW-MANAGEMENT-02 Candidate Evidence

- Status: DRAFT
- UI ID: UI-001
- Design Revision: DREV-20261006-REVIEW-MANAGEMENT-02
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Task Spec path and revision: specs/active/FEAT-001-REVIEW-INVENTORY-AND-RESCHEDULING.md#SPEC-20261006-REVIEW-MANAGEMENT-02
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-02/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-02/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261006-REVIEW-MANAGEMENT-02/index.html=5afa753eaa54395baf790371300f062fe54f1b03eac5b58e3cfac95440e3e813
- Prototype generated/updated at: 2026-10-06
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING
- Superseded by: DREV-20261006-REVIEW-MANAGEMENT-03（次数筛选交互修订，待审）

## Scope

用户指定三项设计修改：删除使用danger红色；科目无“全部”并复用日期选择样式；复习次数支持精确值筛选。
本轮仅修改设计候选与待审Spec，不表示生产实现获批。01版截图为上一版历史证据，不作为02版视觉验收。

## Export manifest

NOT_RUN：要求18状态×320×568、390×844、430×932，共54张；本轮未导出。
浏览器工具明确拒绝file://本地预览访问；没有采用其他浏览器表面绕过策略，也没有自动刷新现有标签页。
本清单尚未满足完整设计批准门禁，不能声称DESIGN_EVIDENCE_VALID。

## Verification evidence

- Node JavaScript语法检查：PASS。
- Node VM交互逻辑检查：PASS。只检查源码生成的状态和事件处理，不是浏览器DOM/视觉验收。
- 覆盖：科目无全部、默认语文、数学两条、零条科学；科目复用dates样式。
- 覆盖：全部次数4条、精确0/1/2/6/8次、无匹配文案、清除筛选恢复4条。
- 覆盖：自定义输入未提交保留旧结果，负数/小数/空值/超范围值保留已应用条件并给出错误。
- 覆盖：删除菜单danger红色声明；自包含源无外部资源。
- 检查发现并修复自定义次数正则转义问题；修复后完整逻辑检查PASS。
- 浏览器截图/几何/键盘交互：NOT_RUN（上述浏览器策略限制）。
- 后端/小程序业务测试、MySQL、原生三视口、iOS/Android：NOT_RUN（本次仅设计修订）。

## Approval gate

需补齐本修订导出、hash及浏览器视觉证据后，再请求具体Spec+Design批准。
用户本次意见是修改设计的授权，不是批准实施整个功能。
