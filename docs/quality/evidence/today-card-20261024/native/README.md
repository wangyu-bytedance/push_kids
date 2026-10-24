# 今日卡片原生取证

320×568、390×844、430×932均已完成：各21个card-状态＋6个DREV02弹层代表态，共81组PNG/JSON，全部errors为空。用户回复继续后完成剩余视口，先前锁屏缺口已消除。真实设备/可访问性与业务端到端不在这些合成结果内。

[source-manifest.json](source-manifest.json)绑定14份生产/工具源码及另核对的3份全局样式；[verification-manifest.json](verification-manifest.json)记录每张PNG的SHA、原生视口和剩余设备/可访问性/独立复核门禁。逐个复算81张PNG SHA、验证81份JSON和源码匹配，未改写旧DREV02取证。320首次空态因脚本误算既有44px触控分区高度而失败，[历史失败](../native-audit/initial-320-spacing.json)保留；改采实际bar/section。目视发现删除文字需按批准设计居中，完成局部CSS修正及断言后，三视口81组全部重新采集。[对齐前审计清单](../native-audit/before-quiet-alignment/source-manifest.json)保留工具旧/新SHA，最终source-manifest对应重新准备的副本。工具为官方微信开发者工具Stable 2.01.2510290、基础库3.17.4；本地自动化9488。只读合成副本拒绝业务写入，不发送真实孩子资料或调用模型。

复现：先运行`tools/prepare_today_learning_native.py --evidence-dir docs/quality/evidence/today-card-20261024/native`，用官方CLI auto启动其打印的合成项目，在GUI切到指定设备后运行`node tools/today_learning_geometry.js WIDTH 9488 docs/quality/evidence/today-card-20261024/native STATE_CSV`。不得伪改系统宽度替代实际设备切换；完成新矩阵后重新生成verification-manifest并复算源码/SHA。

代表截图：[空区隐藏](card-recent-new-390.png)、[具体建议](card-proposal-390.png)、[120字完整标题](card-proposal-long-390.png)、[只读待学](card-viewer-task-390.png)、[生成关闭但保留待学](card-task-feature-off-390.png)、[删除恢复](card-recover-after-remove-390.png)。首次局部检查发现按钮默认宽度，修正并全矩阵重采；当前文件均为修正后结果。
