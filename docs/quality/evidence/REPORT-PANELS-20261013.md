# 报表展开区本地验证 — 2026-10-13

- Spec: SPEC-20261013-REPORT-PANELS-01，VERIFYING。
- Design: DREV-20261013-REPORT-PANELS-01，用户2026-10-13批准；设计源及SHA见对应APPROVAL.md。
- 范围：报表历史/编辑计划内部布局、明确展开/收起、计划「调整」标签、首尾收起；独立条目页保留原呈现，查询及写入合同不变。
- 并行任务边界：外层卡片继续继承pk-card；未修改全局tokens或外层背景、材质、阴影、装饰。内部分组平铺与分隔属于本次批准范围。
- 发布状态：仅本地，未上传、设体验版、提交审核或发布。

## 已运行验证

| 命令/证据 | 结果 |
|---|---|
| `npm test` | PASS，236/236；包括3项几何审计校准回归 |
| `npm run lint:miniapp` | PASS |
| `.venv/bin/python tools/validate_miniprogram.py` | PASS，16页，源码920852字节 |
| `.venv/bin/python tools/check_architecture.py` | PASS，checked=3 |
| `.venv/bin/python tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261013-REPORT-PANELS-01/APPROVAL.md --check-current-policy` | PASS |
| `git diff --check` | PASS |
| HTML设计导出 | 3视口×5态；视口图、整页图、SHA；溢出检查与展开语义通过，不能替代原生验收 |

## 原生节点几何

使用微信开发者工具自动化及 `tools/report_panel_geometry.js`，分别在320×568、390×844、430×932运行capture。`report-panels-20261013/`保留36份合成数据节点矩形JSON及视口、DPR、基础库、字体缩放元数据；无真实孩子数据或服务写入。

每档12态：collapsed、history、plan、both、subject-filter、count-filter、menu、readonly、error、empty、pending、plan-empty。全部通过存在性、可见节点横向边界、标题/操作无遮挡、触控目标≥44px、调整44×44px、菜单视口内、组件/收起入口挂载检查。审计回归会拒绝缺失节点、过小目标、放大调整按钮、标题重叠及越界菜单。未测根节点scrollLeft，不将节点边界检查描述为完整滚动验收。

注入合成数组使用原生数据构造器递归复制，避免跨执行环境数组被渲染器误判；菜单在定位回调后250ms采集，320向上展开后保持视口内。最终36份结果均为修正后的采集。运行结束恢复原页面数据，模拟器恢复430视口。

320计划态经CUA人工看图，长中文标题换行及调整入口分离清晰；仅作为辅助观察，未保留原生PNG矩阵。

## 未完成及适用性

- NOT_RUN：三视口完整原生截图矩阵、字体放大、loading视觉、iOS/Android真机与完整手工操作路径。安装的自动化 `App.screenshot` / `Tool.screenshot` 返回未实现；数字矩形和HTML导出不替代这些证据。
- TP-001/004/005为PARTIAL，Spec保持VERIFYING。既有筛选/分页/保存/冲突/只读/切孩子逻辑回归通过；未改领域控制器，不声称真机全流程已验收。
- 后端pytest/ruff/mypy为N/A：本次没有Python、API、数据库或服务端策略变更。
