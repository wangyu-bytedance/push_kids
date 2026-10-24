# 足迹界面减法 — 设计阶段证据（历史）

- Date: 2026-10-24
- Status: DESIGN_APPROVED / HISTORICAL_DESIGN_PHASE
- Spec: [SPEC-20261024-FOOTPRINTS-MINIMAL-UI-01](../../../specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md)，当前active/VERIFYING。
- Design: [DREV-20261024-FOOTPRINTS-MINIMAL-01](../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)。
- Approved rules: [UI-COPY-REQUIREMENTS.md](../../design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/UI-COPY-REQUIREMENTS.md)；用户回复“批准 Spec01 + DREV01，按此实施并合并 UI 规范”后已合并到FRONTEND-DESIGN及FEC正文。

以下保留批准前纯设计阶段的检查和未实施边界；批准后的生产改动、327项前端与原生验证另见[实施证据](footprints-minimal-20261024/README.md)。不将历史NOT_RUN读成当前代码未改。

## 本轮实际改动

仅新建Spec、可编辑HTML、工程UI文案条款稿、导出工具与24张候选PNG/SHA；更新Spec索引及两份工程规范的候选登记。Feature/UI当前已实现正文保持原样，仅登记待批增量。没有修改生产前后端、API、数据、测试合同或发布阶段；无需运行后端及全量业务测试来证明纯设计文件。批准后仍须修改原权威实现并重新验证，不能用本轮HTML代替原生验收。

## 检查

| 检查 | 本轮结果 |
|---|---|
| `python3 docs/design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/render.py` | PASS，8态×3视口=24张1x PNG；三个视口交互通过；页面无JS错误且无业务网络请求 |
| 主界面/设置目视 | PASS：390×844主界面无重复身份标题及常驻次要入口；320×568设置只剩开关和保存，按内容收高 |
| `validate_design_evidence.py --manifest …/DREV-20261024-FOOTPRINTS-MINIMAL-01/APPROVAL.md --allow-pending --check-current-policy` | PASS，候选源和24张PNG的SHA、视口、路径匹配 |
| 新 `render.py` 的 `ruff check` / `ruff format --check` | PASS |
| 当前相关文档链接 / `git diff --check` | PASS，8份文档111个本地引用无缺失；批准旧设计源SHA未变 |
| npm / lint:miniapp / native / devices | NOT_RUN，本轮尚未改生产源；批准后的状态/权限/菜单和原生节点必须另验 |
| 独立review及产品最终验收 | NOT_RUN，设计/实施尚未闭环 |

更多菜单和归档列表在HTML中模拟微信原生可见效果；不能由DOM点击推断真机原生事件、地图层叠或读屏通过。日期、AI同意/确认、7天/24小时和归档写入限制不改变；内部细则留在Feature/Spec，不另添帮助长文。

内置浏览器尝试打开新本地设计文件被URL协议策略拦截；没有换协议、代理、其他浏览器或原始调试接口绕过。已用先前启动的本地设计导出流程生成PNG，后续通过本地文件链接和图片提供审阅，不声称已在用户当前浏览器自动打开。

## 既有缺陷和闭合边界

设计阶段CR-001仍开放：时间线满100条的下一组响应可清理新照片面板预览。后续在BUG-032已批准TP04/TP10范围实施修复并补两种预览时序回归，详见新实施证据；原313项/51组结果不证明该竞态通过。

设计阶段以READY_FOR_REVIEW交付，随后用户明确批准Spec01+DREV01；当前本地实现后仍active/VERIFYING，未齐门禁不转DONE。无提交、推送、上传、部署或数据库操作。
