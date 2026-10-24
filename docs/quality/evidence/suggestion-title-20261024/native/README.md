# 标题约束：原生取证

- Result: PASS_NATIVE_MATRIX，2026-10-24；不是完整真机/可访问性验收。
- Approval: SPEC-20261024-SUGGESTION-TITLE-LIMIT-01 / Architecture01 / DREV-20261024-TODAY-LEARNING-04，用户明确「批准，按此实现」。
- Runtime: 微信开发者工具Stable2.01.2510290，基础库3.17.4，默认字体；320×568/DPR2、390×844/DPR3、430×932/DPR3。
- [39份节点/截图校验清单](verification-manifest.json) · [14份原生源码绑定](source-manifest.json) · [实现与测试源码绑定](../implementation-source-manifest.json) · [总证据](../../SUGGESTION-TITLE-IMPLEMENTATION-20261024.md)。

每视口13态：title-proposal、title-proposal-max、title-card-max、title-edit-default、title-edit-max、title-edit-over、title-edit-empty、title-edit-legacy、title-edit-error、title-edit-saving、title-edit-unicode、title-legacy、max-title-scrolled。39份JSON的errors均为空；PNG SHA与节点记录相符；14份源码和app.wxss/tokens/atoms与取证副本一致。时间戳保存在各JSON，不把旧卡片/弹层取证计作本轮。

官方CLI打开/连接`/private/tmp/push-kids-today-learning-native-20261024`合成副本，自动化端口9488；设备选择通过实际GUI完成，runner要求实际viewport吻合才验。副本useCloud=false/family=synthetic，API拒绝业务写入，不访问真实孩子或付费模型。测试setter调用生产setCurrent；编辑态实际调用edit/field计算计数及错误，保存中/失败为合成状态。原生geometry证据不代替HTTP/DB及真实输入提交测试。

重现命令（先在开发者工具切换对应设备，WIDTH为320/390/430）：

```bash
node tools/today_learning_geometry.js WIDTH 9488 docs/quality/evidence/suggestion-title-20261024/native title-proposal,title-proposal-max,title-card-max,title-edit-default,title-edit-max,title-edit-over,title-edit-empty,title-edit-legacy,title-edit-error,title-edit-saving,title-edit-unicode,title-legacy,max-title-scrolled
```

核对正常20字中文标题字体20px/600/1.45、两行内；14px计数与字段标签同排且至少8px间隔；错误在输入下方；21字/空值/旧120显示对应错误和完整草稿，非BMP20码点不误计40；保存等待标识；标题、元信息、正文及关闭/底部操作不重叠，44px触控与横向边界；旧120字实际滚动仍可读。已目视查看320最大新标题、390超限编辑、430旧长标题，布局符合批准设计。

未验：真实iOS/Android、系统大字体、读屏、实际软键盘（取证时关闭自动聚焦以稳定几何，不作键盘通过声明）。Spec留active/VERIFYING；本目录不表示上传、体验、审核或发布。
