# 合成原生页面证据

当前结果：390×844，基础库3.17.4，12态全部原生节点几何检查通过；每态有PNG、节点JSON及截图SHA-256。状态为empty、proposal、edit、long、loading、error、stale、pending、partial、viewer、record、remove。`source-manifest.json`记录本轮源码及采集脚本SHA；批准的设计HTML/78PNG/SHA未修改。

重现：运行`.venv/bin/python tools/prepare_today_learning_native.py`，用官方开发者工具CLI打开`/private/tmp/push-kids-today-learning-native-20261024`并启用自动化9465，再运行`node tools/today_learning_geometry.js 390 9465`。只能操作该合成副本；运行前校验family=synthetic、useCloud=false，API拒绝全部业务写入。

已检查：实际视口、横向包含、正文≥14px、操作有效尺寸≥44px、关闭位置、底部操作可达、正文/操作不重叠、主按钮全宽及三次操作的间距、viewer无写按钮。目视复核proposal截图；早期默认按钮184px导致的窄主按钮/关闭偏移已修正，当前同名产物均为复验结果。

未验证：320×568与430×932因Mac再次锁屏无法切换设备；复习专属状态、真实键盘焦点/读屏、字体放大、安全区/真实iOS与Android、完整26态批准设计对照尚未完成。此12态不冒充26态×3，也不证明真实AI内容适合。详情见[实现证据](../../TODAY-LEARNING-IMPLEMENTATION-20261024.md)。
