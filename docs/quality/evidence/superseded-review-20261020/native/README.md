# 已替代词条原生数字几何（部分验收）

WeChat开发者工具Stable 2.01.2510290、基础库3.17.4，字体15。
320×568/DPR2、390×844/DPR3、430×932/DPR3，各7态×独立页/报表内嵌，共42份JSON，数字布局断言全部通过。
`SOURCE-MANIFEST.json`记录生产模板/样式与隔离副本的匹配SHA，以及采集JSON的SHA。

这是隔离合成项目：原生产WXML/WXSS、controller及组件样式原样复制；仅测试入口注入合成数据，替换业务API为拒绝请求。
内嵌宿主为最小18px边距容器，真实报表的其他区域/插件/网络流程仍需整应用验收。
后台没有读取真实家庭、孩子、学习素材或发送通知。

状态：normal、superseded、menu、viewer、long、deleted、empty。
断言覆盖状态双列等宽/间距/44px热区、过滤器/来源入口、文字横向边界、管理按钮留白、菜单不越界、只读无管理动作、已替代仅删除。
每份数据核对实际runtime宽/屏幕高、路由、状态/只读/空态，防止采到尚未应用的fixture。

截图状态全部`NOT_RUN`：官方`App.captureScreenshot`多次15秒/40秒超时。
节点矩形不能验证视觉设计和文字完整性，不能据此判定完整原生门禁通过。iOS/Android、字体放大与读屏均未验收。

复现（独立测试项目；本机localhost自动化连接需相应网络权限）：

```bash
.venv/bin/python tools/diagnostics/supersession_native_project.py /private/tmp/push-kids-supersession-native-20261020
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /private/tmp/push-kids-supersession-native-20261020 --auto-port 9441 --trust-project
# 在开发者工具分别选择iPhone5、iPhone12/13(Pro)、iPhone14ProMax，核对runtime实际尺寸。
node tools/superseded_review_geometry.js 320 docs/quality/evidence/superseded-review-20261020/native --geometry-only
node tools/superseded_review_geometry.js 390 docs/quality/evidence/superseded-review-20261020/native --geometry-only
node tools/superseded_review_geometry.js 430 docs/quality/evidence/superseded-review-20261020/native --geometry-only
# 截图通道恢复后省略--geometry-only，之后audit模式必须同时核对PNG SHA，不能接受NOT_RUN。
```

最终42份JSON用`tools/review_inventory_geometry.js`导出的audit逐份重新验证通过；截图缺失仍保留。
设计21张HTML PNG在批准DREV目录，未混入这里。
