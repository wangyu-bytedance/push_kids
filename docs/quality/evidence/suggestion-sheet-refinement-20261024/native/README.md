# 建议弹层 — 原生合成几何与截图

2026-10-24，微信开发者工具Stable 2.01.2510290，基础库3.17.4，默认字体15、显示75%。320×568为iPhone5/DPR2，390×844为iPhone12/13Pro/DPR3，430×932为iPhone14ProMax/DPR3。使用微信原生渲染节点；PNG实际像素尺寸由截图API决定，几何断言使用逻辑像素。

对应已批准Refinement Spec01/DREV02，本地实现尚未发布。生产源码及仅副本修改清单见[source-manifest.json](source-manifest.json)；逐份JSON/PNG的SHA及采集工具版本见[verification-manifest.json](verification-manifest.json)。没有修改已批准HTML/PNG/SHA。

每视口15态，共45份节点JSON与45PNG：`design`、`design-long`、`saving`、`approve-error`、`edit`、`loading`、`error`、`stale`、`pending`、`partial`、`viewer`、`record`、`remove`、`max-title`、`max-title-scrolled`。前两态沿用DREV02合成内容；最后两态验证实际120字字段上限。三视口最终所有JSON的errors为空，截图SHA匹配。

```bash
.venv/bin/python tools/prepare_today_learning_native.py --evidence-dir docs/quality/evidence/suggestion-sheet-refinement-20261024/native
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /private/tmp/push-kids-today-learning-native-20261024 --auto-port 9488 --trust-project
# 在开发者工具选择对应设备后逐一执行，width为320/390/430。
node tools/today_learning_geometry.js <width> 9488 docs/quality/evidence/suggestion-sheet-refinement-20261024/native design,design-long,saving,approve-error,edit,loading,error,stale,pending,partial,viewer,record,remove,max-title,max-title-scrolled
```

断言覆盖精确视口、零横向位移、控件44px（测量容差1px）、文字≥14px、关闭44px且右对齐、主操作/暂缓全宽、次按钮等宽（±1px）且间隔≥8px、sheet/header/关闭/footer位于视窗内、正文≥44px且不重叠footer、viewer无写入口。最大标题在320/390实际滚动，在430无需滚动而完整容纳；元信息不被裁切。此处滚动顶部由仅合成副本的scroll-top绑定控制，正式组件只有原生可手动滚动区域。

原始source-manifest保留采集开始时的工具指纹。430最大标题初次断言仅要求scrollTop>0，实际254px内容可容纳于约280px标题视窗；最后将断言修正为“完整可见或确实滚动”并重采。最终工具指纹另记verification-manifest；业务组件源码指纹均未变化。旧未完成截图运行不算当前45组证据。

本次只取合成呈现状态；没有执行业务写入、真实模型或真实请求端到端。真实键盘、读屏、系统大字体、iOS/Android设备仍NOT_RUN，完整今日26态/复习组合也不由本目录抵扣。实现及文档闭环见[本轮报告](../../SUGGESTION-SHEET-IMPLEMENTATION-20261024.md)。
