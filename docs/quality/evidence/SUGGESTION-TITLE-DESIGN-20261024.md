# 学习建议标题约束 — 2026-10-24 设计阶段证据

- Subject: SPEC-20261024-SUGGESTION-TITLE-LIMIT-01 / Architecture01 / DREV-20261024-TODAY-LEARNING-04。
- State at capture: READY_FOR_REVIEW / AWAITING_APPROVAL；以下保留批准前设计阶段事实，不是当前实现状态。随后用户在call_39aaa3dd3cdf4a52b2bfc9c4d862ee58明确批准Spec01/Architecture01/DREV04；当前本地实现、原生结果与缺口见[实现证据](SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)。
- Source SHA-256: `6ebbac1c69481fc5d5d09376f6bde689e6be2a5e678b0e61a0a9dfcf3008a754`。
- [Spec](../../../specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md) · [设计说明](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/FRONTEND-SPEC.md) · [33张SHA清单](../../design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-04/APPROVAL.md) · [机器报告](../../design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/render-report.json)。

## 实际检查

| 检查 | 结果 | 范围/限制 |
|---|---|---|
| `.venv/bin/python docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-04/render.py` | PASS | 隔离无头Chrome155.0.8059.85，本地合成HTML；33导出、21交互，Runtime异常0 |
| 三视口320×568/390×844/430×932，每视口11态 | PASS | proposal/proposal-max/card-max/edit/edit-max/edit-over/edit-empty/edit-legacy/edit-error/edit-saving/legacy |
| 标题与操作节点布局 | PASS | 正常字体20字CJK标题≤2行，常规页面无横向溢出；关闭/操作≥44px且包含，头部/正文/操作不重叠 |
| 每视口7条输入交互，共21条 | PASS | 20可保存；21保留输入/零写入/定位字段；空值零写入；旧120完整编辑并主动精简；非BMP计数与内部换行拒绝；保存失败保留；pending禁用关闭/提交 |
| 现有DREV01、DREV02、DREV03分别运行validate_design_evidence.py --manifest | PASS | 78+84+63既有冻结导出和源SHA均保持有效，未修改批准源/清单 |
| DREV04 validate_design_evidence.py --manifest ... --allow-pending --check-current-policy | PASS | 源/33张SHA、PNG精确尺寸与仓库当前政策，未将pending冒充批准 |
| 本轮render.py Ruff check / format --check | PASS | 初次发现长行/循环闭包绑定/格式问题，已修正；修正后重跑渲染，33张SHA及21条交互仍通过 |
| 本轮15个文档本地链接、7个生产源基线SHA、git diff --check | PASS | 链接存在，生产源未变；current-state仅登记候选，无120/20当前事实冲突 |
| 原生小程序/真实API与模型/iOS和Android/实际键盘/大字体/读屏/独立实现复核 | NOT_RUN | 本阶段尚未获本Spec+DREV批准；设计不能作为生产行为或原生验收 |

第一次在默认沙箱运行渲染器因Chrome不能启动而失败（headless_chrome_exited），随后经工具执行权限检查后运行隔离无头Chrome并通过；没有操作共享桌面/微信开发者工具，没有使用业务数据，也没有额外模型请求。

人工查看了proposal-max-320×568和edit-over-390×844导出：活动标题完整分两行，具体内容有独立滚动空间；字数/错误紧邻标题输入，原主次操作层级保留。正常字体两行只适用于本矩阵，不是限制系统大字体时的行数。

## 设计取证时的生产源码基线（历史，未实施本修订）

以下文件在设计阶段仅只读检查，仍为120字合同。SHA供批准后实现/证据版本对照，不能冒充20字代码通过：

| File | SHA-256 |
|---|---|
| apps/api/src/push_kids/agent_processing/suggestion_contracts.py | 4fb9dca4bfa3b023fe9af9d2ae249fa496803c1c2dd135f570d3e88f526c6c04 |
| apps/api/src/push_kids/agent_processing/suggestion_provider.py | 04e75a724f58ff1225c778015dbe5144ecb71af2bc0c7e700c053f2a3a31b9bb |
| apps/api/src/push_kids/learning_suggestions/schemas.py | 3e179e10cd950e95b8aaae2ff1b52096dc5f77bc78afed04a4ad0fb0a4b0cec6 |
| apps/api/src/push_kids/learning_suggestions/generation.py | 9fe72036c2d4ab0a26b4bbeb4a6ff6fc40b91a490a7e56cc1586080e4a0563e6 |
| apps/miniprogram/components/today-learning/index.js | 1c4e2013d9401e7c2cd22cb7597c0d043b5bf71a1f659064078001d36782d291 |
| apps/miniprogram/components/today-learning/index.wxml | 6b1f24365dfcc498d85742d4bc677068f967da8aca06dbfa88040f148a1e817b |
| apps/miniprogram/components/today-learning/index.wxss | 0ecd9353655ed3699dac1b0e4cb621040abad3cbdb7ff98bc67403778cf80458 |

## 文档闭合与剩余门禁

Feature、UI current-state、前端设计与Spec索引只登记待批准候选；既有120字生产事实、Architecture/BHV045/测试和发布记录未改为20字。当前没有代码与新事实冲突，也没有把前一轮327项前端/81组原生作为本修订通过。

Spec保留`specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md`，状态READY_FOR_REVIEW；等待具体Spec01（含Architecture01）与DREV04批准。批准后再完成生产回归、三视口原生和设备/可访问性、独立复核及事实合并；不满足全部门禁不标DONE。未提交、上传、部署、迁移、批量改写或改变功能开关。
