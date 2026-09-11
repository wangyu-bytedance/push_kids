# 记录入口简化批准快照

- Spec: `SPEC-20260911-RECORD-SIMPLIFICATION-01`
- Design: `DREV-20260911-RECORD-SIMPLIFICATION-01`
- Owner/approver: 用户，2026-09-11
- Approval: “按照这个方案修改”（紧接本会话的 Spec 与 Design Revision 交付）
- Scope: 删除新增/历史与照片/文字两组分段选择；统一照片+文字表单；按材料自动选择现有提交路径；历史移至表单底部并默认折叠；viewer 与显式历史意图按设计自动展开
- Design artifact: `docs/design/frontend/prototypes/DREV-20260911-RECORD-SIMPLIFICATION-01/FRONTEND-SPEC.md`
- Baseline: `FDB-20260906-03`；`FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 （既有 FEAT-001 waiver anchor，非本次新增节点）
- Evidence exception: 沿用 `docs/architecture/ARCHITECTURE.md` 中 FEAT-001 scoped waiver，公开生产前到期；不覆盖 FEAT-002 新 UI，也不免除原生视口/真机验证
- Required native evidence: 320×568、390×844、430×932；空材料、纯文字、含图、历史折叠/展开、viewer、键盘、字体放大与代表性 iOS/Android；实施后执行
- Verification status: 320×568、390×844、430×932 折叠/展开近似截图已生成并走查；开发者工具模拟器重载超时，原生几何、键盘、字体放大、媒体权限拒绝及代表性 iOS/Android 仍为 NOT_RUN，且本轮未上传或部署
- Follow-up finding: 用户原生截图显示固定提交栏与自定义 TabBar/历史入口触控重叠；此修复属于已批准 AC-004/TP-006“历史入口可达”范围，未改变流程或视觉 token。记录页提交栏现避开 TabBar、中央凸起键与 safe area，页面尾部同步补足滚动占位；修复后原生点击复验仍为 NOT_RUN
