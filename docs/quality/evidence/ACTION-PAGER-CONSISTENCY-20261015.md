# 今日按钮与编辑计划分页统一验证

- Spec: `SPEC-20261014-ACTION-PAGER-CONSISTENCY-02`，`specs/active/FEAT-010-TODAY-ACTION-STYLE.md`，VERIFYING。
- Design: `DREV-20261014-ACTION-PAGER-CONSISTENCY-02`；用户2026-10-15“落地”批准；批准SVG/PNG保持不变。
- 实现：每日任务操作复用pill token、移除阴影；共享编辑计划分页使用专用三列grid，科目分页两列，显式禁用透明底和弱文字。未修改JS、API、游标、完成/撤销及权限。

## 本轮检查

- PASS：`npm test`，243 passed / 0 failed；`npm run lint:miniapp`。
- PASS：`.venv/bin/python tools/validate_miniprogram.py`，16 pages；运行时工作区包含并行设置科目改动，1070880 source bytes不是上传包大小。
- PASS：`.venv/bin/python tools/check_architecture.py`，checked=3。
- PASS：`.venv/bin/python tools/validate_design_evidence.py --check-current-policy --manifest docs/design/frontend/snapshots/UI-001/DREV-20261014-ACTION-PAGER-CONSISTENCY-02/APPROVAL.md`。
- 原生部分验证：微信开发者工具iPhone 14 Pro Max，设备宽430，内容视口430×834（不能视为已完成430×932整屏截图门禁）。合成数据仅setData，无后端写入；结束恢复数据与load方法。采集文件`action-pager-native-430.json`。
- 今日content/completed/pending/readonly/long-name五态：完成/撤销64×44px，加载约82.8×44px，均pill半径572px、box-shadow none；只读无按钮；长名与按钮未重叠。加载图标沿用原有宽度扩展，不改交互。
- 独立编辑计划first/middle/last/loading/long-page/subject六态：条目左右按钮157×44px且同排，页码居中；长页码仅中央换行。科目按钮180×44px同排；禁用computedStyle透明底，无原生白块；均无阴影。
- NOT_RUN：320/390原生，报表内嵌原生状态，完整截图矩阵、iOS/Android真机点击与加载反馈。共享content并不替代内嵌实测；不冒用历史证据。
- 第一轮采样因fixture缺loaded、迟到加载响应出现空节点，已修正fixture并重采；只有重采结果作为证据。

## 文档与范围核对

FEAT-001、FEAT-010与UI-001已同步本地视觉事实、0.1.15既有开发上传基线与本次未上传状态；Spec保持active/VERIFYING，恢复条件为补齐上述原生、截图与真机验收。Behavior Catalog、Architecture及架构约束核对：业务/数据/调用/模块边界不变，无需修改正文。发布阶段单独记录在`docs/deploy/releases/20261015-action-pager-local.md`，本轮未上传、未设体验、未提审、未正式发布。保留并行设置科目与治理文档改动，未将其归入本Spec。
