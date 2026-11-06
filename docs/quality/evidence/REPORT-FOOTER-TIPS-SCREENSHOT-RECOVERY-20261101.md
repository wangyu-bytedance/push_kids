# BUG-037 — 截图恢复与真机验收准备

此处保留恢复02当时结果；用户解锁后的当前[齐套03](REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101.md)
已补320，共144组原生PNG/节点，真机仍等待扫码。原02的失败/锁定记录不改写。

- Evidence revision: REPORT-FOOTER-TIPS-RECOVERY-20261101-02
- Spec: [BUG-037 Spec01](../../../specs/completed/BUG-037-REPORT-FOOTER-TIPS.md)
- Approval: 原Spec01/DREV01已批准；用户本轮要求“修复截图工具问题并补全真机验收截图”
- Production changes this turn: none；两份批准WXML/WXSS的SHA与原实施证据相同
- Current result: 390/430双宿主96组原生PNG/JSON通过；320和真机仍未完成
- Delivery: 官方开发preview成功，1,192,127字节；未upload/体验/审核/正式发布

## 截图服务恢复结果

最初保留的430节点证据没有PNG。本轮重新核对工具状态：
Computer Use辅助功能/屏幕录制权限均granted；旧进程31267与窗口39516已失效，
当前为10293，重新用官方CLI打开隔离项目后获得41287窗口。
该窗口可读真实WXML、模拟器机型菜单并产生截图；没有改macOS安全设置或工具二进制。

新会话首次`App.captureScreenshot`仍超时；先运行不截图的真实节点fixture，
再通过Computer Use刷新当前窗口观察、确认渲染内容，然后重试，官方截图恢复。
随后430/390各两宿主、每宿主24态，共96次截图连续成功，原生节点0失败。
这证明本轮恢复流程有效；不足以将所有历史超时归因于同一个软件缺陷。

使用当前工具：

```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /tmp/push-kids-footer-native-20261101 --auto-port 9612 --trust-project
NATIVE_EVIDENCE_REVISION=recovered-01 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 430 embedded
NATIVE_EVIDENCE_REVISION=recovered-01 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 430 standalone
NATIVE_EVIDENCE_REVISION=recovered-01 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 390 embedded
NATIVE_EVIDENCE_REVISION=recovered-01 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 390 standalone
```

原生模拟器仍用隔离合成只读API；真实生产WXML/WXSS/controller未替换，
两份批准实现SHA保持`c481d702…587e72` / `390bf6fa…21e11`。
数据和文本为合成示例，未发生真实删除、改期或数据写入。

## 新截图矩阵

| 真实模拟器机型 | 宿主 | 节点/PNG | 几何失败 | 图像SHA/解码 |
|---|---|---:|---:|---|
| iPhone 12/13 (Pro)，390×844 | embedded | 24 | 0 | PASS |
| iPhone 12/13 (Pro)，390×844 | standalone | 24 | 0 | PASS |
| iPhone 14 Pro Max，430×932 | embedded | 24 | 0 | PASS |
| iPhone 14 Pro Max，430×932 | standalone | 24 | 0 | PASS |
| iPhone 5，320×568 | 两宿主 | 0 | N/A | NOT_RUN，机型未成功切换 |
| 真实iOS/Android手机 | 两入口 | 0 | N/A | NOT_RUN，未连接手机/未扫码 |

每宿主24态沿用批准的时间/科目/次数分页与删除/长提示/预算/科目目录/菜单/只读/失败状态。
PNG实际尺寸为780×1688或780×1506（390），860×1864或860×1668（430）；
原生导航/Tab窗口与全屏截图范围不同，实际windowWidth和screenHeight在每份JSON里独立校验。
图像按官方返回尺寸保存，没有放大模拟不同视口。

新资产：`report-footer-tips-20261101/recovered-01/{embedded,standalone}/{390,430}/`。
96张PNG均Pillow解码通过，逐图SHA与同名JSON匹配，0缺失/0审计失败；
机器清单见[恢复manifest](report-footer-tips-20261101/recovery-manifest-02.json)。
代表删除提示已逐图视觉读取；其余状态由保留图像和节点共同供复核，
不把合成原生画面称为真机验收。

## 320与桌面锁定的真实阻断

机型菜单可读到320×568，但几次选择之后真实`wx.getSystemInfoSync()`仍390×844，
collector因viewport前置条件不符停止，未输出320通过。
专用项目close/open恢复过程中，窗口再次不可读；
`ioreg`明确返回`CGSSessionScreenIsLocked: true`、`kCGSSessionOnConsoleKey: true`，
锁定时间为2026-11-01 18:01:46（Asia/Shanghai）。
此时不盲点、不mock视口，也不重启/关闭其他并行项目。
专用auto重开未完成已停止本轮命令；原96图和首次失败保留。

OS级备用截图技能preflight发现终端屏幕录制权限未授予，与Computer Use runtime的granted分属不同进程。
未擅自修改权限，也不依赖这个备用路径；已可用的官方截图与Computer Use路径在用户解锁后继续。

## 真机预览已准备

为了让设备验收拿到实际修复，本轮从已上传0.1.17的168份冻结生产客户端复制到
`/tmp/push-kids-footer-device-preview-20261101`，仅替换本Spec批准的两个共享文件。
其余166份逐项SHA与旧冻结源一致，配置仍真实AppID、云托管环境/服务和`useCloud=true`。
没有合成API/fixture、儿童照片、密钥或并行BUG-036增量混入该真机preview。

官方CLI preview已成功，包体1,192,127字节：

```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli preview --project /tmp/push-kids-footer-device-preview-20261101 --qr-format image --qr-output /Users/bytedance/Documents/push_kids/output/BUG037-device-preview-20261101.png --info-output /Users/bytedance/Documents/push_kids/docs/quality/evidence/report-footer-tips-20261101/device-preview-info.json --lang zh
```

[预览二维码](../../../output/BUG037-device-preview-20261101.png)、
[168份源码清单](report-footer-tips-20261101/device-preview-source-manifest.json)和preview-info绑定本对象。
开发preview不是开发upload，不推进版本基准或Spec DONE。
USB查询未发现手机，`adb devices -l`为空；`idevice_id`未安装、当前xcrun没有devicectl。
没有用安装驱动或冒充设备绕过扫码。

## 恢复与验收操作

需要用户解锁Mac并保持桌面可用，再以项目开发者微信扫描本次preview二维码。
二维码过期时重新生成同一冻结对象，不能扫描旧0.1.17截图代验本次修改。
先收集手机型号、系统版本、微信版本、实际窗口尺寸及当前preview对象；
真实报表→编辑计划截图包含首页/中间/末页、科目目录和长文字，
再用隔离的合成notice在可连接的真机调试会话检查删除/长提示，以避免为图执行正式删除。
实际点击、默认/放大字体、iOS/Android与读屏按原TP-005单列结果。

截图包含真实孩子内容时原件保留附件或批准的本地私有位置，不写仓库；
仓库只保留脱敏图/数值与哈希索引。当前没有接收到真机原件，所有设备项NOT_RUN。

## 文档闭合

原实施01证据/manifest/EVD的历史NOT_RUN不改成PASS；本恢复02记录后续范围。
Spec TP-004更新为390/430已取得96组PNG/节点、320缺失；TP-005仍PARTIAL，
真正设备/大字/读屏未验。Feature/UI、设计索引、状态清单和本地发布记录同步当前证据。
Behavior BHV-033、Architecture、FEC/测试策略合同与本轮零生产diff无冲突。
Spec保持VERIFYING，位于`specs/active/`；此次preview不构成云端开发完成归档条件。
