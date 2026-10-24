# DREV-20261024-TODAY-LEARNING-02 — 建议弹层重点与按钮层级

- Status: APPROVED
- Created: 2026-10-24
- Task Spec: [SPEC-20261024-SUGGESTION-SHEET-REFINEMENT-01](../../../../../specs/active/FEAT-004-SUGGESTION-SHEET-REFINEMENT.md)，已批准实施，当前VERIFYING。
- Base: [DREV01](../DREV-20261024-TODAY-LEARNING-01/FRONTEND-SPEC.md)，批准快照不修改。
- FDB / FEC: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，均APPROVED。
- Affected UI: [UI-001](../../ui/UI-001-parent-miniapp.md)；Feature: FEAT-004。
- Source: [index.html](index.html)；[批准SHA清单](../../snapshots/UI-001/DREV-20261024-TODAY-LEARNING-02/APPROVAL.md)。
- Approval: 产品负责人2026-10-24在明确列出本Spec01/DREV02及改动清单的审批问题后回复「批准，按此实现」。自此HTML、84张PNG和SHA冻结。

## 1. 设计方向和批注处理

Operate：沿用知芽暖白纸面、松绿、系统中文字体和既有圆角；具体内容先于说明，动作依强弱对齐，反馈仅用于操作状态。

批注1：删除“沿着已学内容，再试一小步”及其大段前置标题区。弹层直接以具体学习标题开头，下一行是科目、预计时间及简短“AI建议”。不重复显示“学习建议/待家长确认”，绿色确认按钮表达待审批动作。依据与实际学过后再记录的提示保留在正文。

批注2：绿色主确认按钮独占全宽；“编辑内容”“换一项”是等宽、44px高、8px间隔的浅底边框按钮；“今天先不学”全宽居中、次级文字色，与主按钮分离。焦点可见，按下有底色反馈；提交中主按钮“正在加入…”且全组及关闭禁用，审批失败保留提案、提示错误并允许重试。

## 2. 交互与实现边界

所有按钮仍调用原处理器。编辑示例保存后返回同一建议再确认，换项展示生成中，暂缓保留建议可主动查看。父级弹层协调、自动提示、服务端资格/幂等与真实记录均沿用主Spec04。可审批主态不再使用通用“学习建议”额外标题，其他生成/编辑/实际记录/删除面板不借机改版。

AI文本为普通文本，不引入HTML解析、资源、第三方库、请求或本地内容持久化。设计源只使用合成数据；设计批准本身不代表真实模型、原生或真机验收，后续本地实现见独立证据。

## 3. 精确视口和状态矩阵

320×568、390×844、430×932，1x/DPR1。保留DREV01的26态，新增`suggestion-saving`、`suggestion-approve-error`，合计28态×3=84张PNG。完整状态名由HTML `window.designStates`及[render-report.json](render-report.json)逐一列出。

| 状态集合 | 本次差异 |
|---|---|
| suggestion、suggestion-long | 具体学习标题与紧凑元信息；确认/编辑/换项/暂缓新层级 |
| suggestion-saving、suggestion-approve-error | 新增既有提交等待/失败行为的可视样本，不新增服务端状态 |
| suggestion-edit | 原型保存修改返回建议，与已有组件一致，不直接审批 |
| suggestion-stale | 沿用重新生成入口，具体标题与AI来源可见，不开放旧提案审批 |
| 其他22态 | 延续DREV01，作为邻接回归，不更改早复习和真实记录布局 |

早复习early/long/viewer仍滚动220px展示原日期/操作；其他状态顶部导出。keyboard是210px设计占位。面板最大85dvh，标题和操作固定、正文独立滚动；不靠隐藏横向溢出通过检查。

## 4. FEC与验证

正文≥14px；关闭与所有操作≥44×44，邻接操作≥8px，两列等宽误差≤1px。长标题正常换行，最小视口下正文仍有可滚动区域，按钮固定可达。Tab在面板循环，Escape关闭且等待时不能取消正在确认的请求；关闭恢复到主动查看入口。减少动态偏好生效，无装饰动效。

批准后WXML/WXSS使用原tokens和原生按钮显式宽度/边距/盒模型，不能直接复制浏览器CSS。业务测试、三视口原生节点及截图、读屏/大字体/安全区/真机验收均须绑定新源码；当前HTML导出不抵扣。既有1.5MiB包体及有界请求预算不变。

## 5. 实际结果与批准

2026-10-24执行`.venv/bin/python docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-02/render.py`。沙箱启动Chrome失败，经工具审批启动隔离Chrome后通过：84张导出，控件横向包含/44px、两列等宽/8px间距、正文可滚动空间、底部可达检查PASS；12条点击转移、Tab循环、提交禁用、Escape保护及关闭恢复焦点PASS，Runtime异常0。目视检查390主态、320长标题和430主态。详情见[本轮设计证据](../../../../quality/evidence/SUGGESTION-SHEET-DESIGN-20261024.md)。

本具体Spec01与Design02已由产品负责人2026-10-24「批准，按此实现」批准。HTML/84张PNG/SHA冻结，业务应用及验证结果另记本轮实现证据；旧DREV01只在本次变化范围由DREV02替代，其他范围继续有效。未授权改变发布状态。

2026-10-24本地应用后，[实现证据](../../../../quality/evidence/SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)记录311项前端与三视口45组原生节点/PNG通过。原生实现针对61–120字保留完整标题，在30vh标题区域滚动；这是已批准长文本可达要求的边界处理，HTML/PNG冻结源不改。系统大字体、实际键盘、读屏与真实设备仍NOT_RUN。
