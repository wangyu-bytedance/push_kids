# UI-001 — DREV-20261006-SOURCE-DELETE-01 Approval Snapshot

- Status: APPROVED
- UI ID: UI-001
- Design Revision: DREV-20261006-SOURCE-DELETE-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Task Spec path and revision: specs/active/FEAT-001-PRECISE-SOURCE-AND-KNOWLEDGE-DELETION.md#SPEC-20261006-SOURCE-DELETE-02
- Frontend spec path: docs/design/frontend/prototypes/DREV-20261006-SOURCE-DELETE-01/FRONTEND-SPEC.md
- Editable design source path(s): docs/design/frontend/prototypes/DREV-20261006-SOURCE-DELETE-01/index.html
- Editable source SHA-256: docs/design/frontend/prototypes/DREV-20261006-SOURCE-DELETE-01/index.html=107a6d94ce16a47bb6bf0d9f10473c2ead2209f14b43317979cb6f4df9946956
- Prototype generated/updated at: 2026-10-06
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-06
- Approval evidence: 本会话用户“落地这两个spec”，批准SPEC-20261006-SOURCE-DELETE-02与DREV-20261006-SOURCE-DELETE-01
- Superseded by: N/A

## Approval identity

已批准 SPEC-20261006-SOURCE-DELETE-02 + DREV-20261006-SOURCE-DELETE-01。本清单自2026-10-06批准后冻结。
2026-10-06：待审批期间将Spec引用更新为02，补充来源定位合同；可见设计源、导出和哈希未变。已有截图与预览证据不代表AC-007/008等业务验收通过。

## Candidate scope

四状态各三档视口：menu 更多菜单、photo 对应照片、confirm 删除确认、unknown 无可靠索引。
小屏菜单允许正常纵向滚动，“收起”在首屏下方；禁止隐藏横向溢出伪造合格。
其他加载、错误、取消、pending、权限和文字状态按 FRONTEND-SPEC.md 实现验证。
合成题面只表达布局，不含真实儿童照片；无远程资源。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
| confirm-320.png | confirm | 320×568 | 1x | 4cf0d586a0deb35a9aa0c98a24516f7e4c288882c79e39bb0fb8fe7bd1943a02 | 合成设计预览 |
| confirm-390.png | confirm | 390×844 | 1x | 86cc17385bd36cc01af199d1746e7892d8da96a24c783ee0fac963e2a9320766 | 合成设计预览 |
| confirm-430.png | confirm | 430×932 | 1x | 5cfdc45a9e5ae80df6769bd7dc7c7c34b9a47ad066115c1b3bb918424fa60c68 | 合成设计预览 |
| menu-320.png | menu | 320×568 | 1x | 42697f59e50fa0812cb24560736c1a3d4f8fc27633351c9f01eb81d05e6fa017 | 合成设计预览 |
| menu-390.png | menu | 390×844 | 1x | a4746b62b8132e3e591369664c0c39d01ad50c1c14cd6d5fc35bb97c36e1a774 | 合成设计预览 |
| menu-430.png | menu | 430×932 | 1x | 991a890dbeee9b765ea4d12a14bcb9aae6f984f0e854336df844d0a1dd7611ca | 合成设计预览 |
| photo-320.png | photo | 320×568 | 1x | bf3ea1ddd168ce73fb748e6e8e4768716234282dca08658609712fa10f745f83 | 合成设计预览 |
| photo-390.png | photo | 390×844 | 1x | 8be31f1da28dc00832e050690c5254066c77aad0d882c7bee551b106e71bd2d4 | 合成设计预览 |
| photo-430.png | photo | 430×932 | 1x | c9999ae60494c38682515e0c70ac30434c0ae9c12e2115a32e9c300f497494dd | 合成设计预览 |
| unknown-320.png | unknown | 320×568 | 1x | a6a9c24c6ef9124eb843aeadb50d284d6890d46abbdf29e7a3f41aadf1118b74 | 合成设计预览 |
| unknown-390.png | unknown | 390×844 | 1x | 0919c38a8a22c14558e98bf500e221d2ada983393a24e838d1f2da23fce26134 | 合成设计预览 |
| unknown-430.png | unknown | 430×932 | 1x | 6a03986d5a03dce2bb178c59ec0f53cf8f15288eee0352c95469923b9578e7b3 | 合成设计预览 |

## Verification evidence

- 2026-10-06：独立临时 Chrome 154.0.8037.93、Playwright、DPR=1，12张PNG导出成功。
- 12/12 HTML状态无横向滚动，渲染按钮高度均>=44px；不是原生节点几何证据。
- 设计预览：来源打开/关闭、删除取消保留卡片、确认删除演示成功；pageerror=0。
- 人工视觉检查：menu-320、photo-390、confirm-320；小屏菜单可纵向滚动，确认按钮可达。
- 默认Playwright浏览器版本未安装，沙箱Chrome启动失败；改用已安装Chrome独立临时实例后导出成功，未安装依赖、未读取个人浏览器资料。
- 业务自动化、原生三视口、iOS/Android、大字、私有原图实际鉴权：NOT_RUN（尚未批准/实现）。
- 本清单完整性校验：`python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261006-SOURCE-DELETE-01/APPROVAL.md --allow-pending --check-current-policy` → `DESIGN_EVIDENCE_VALID`；不是生产功能测试。

## Integrity checklist

- [x] 本地可编辑源、PNG和哈希已记录。
- [x] 所需三视口和四种状态都有导出。
- [x] 用户明确批准具体Spec + DREV。
- [ ] 实现后的原生与业务验证通过。
