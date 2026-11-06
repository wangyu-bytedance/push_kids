# BUG-037 — 三视口原生截图齐套与真机连接准备

- Evidence revision: REPORT-FOOTER-TIPS-NATIVE-COMPLETE-20261101-03
- Requirement: [Spec01](../../../specs/completed/BUG-037-REPORT-FOOTER-TIPS.md)，TP-004/005/006
- User action: 用户本轮回复“已经解锁”，继续原“修复截图工具问题并补全真机验收截图”
- Production source changes: none；两份批准实现与controller的SHA保持原对象
- Native simulator result: PASS，两宿主×三个真实视口×24态，共144组PNG/原生节点
- Physical device result: NOT_RUN，官方无线调试码已生成，等待微信扫码连接
- Delivery: 官方preview已成功，未upload/体验/审核/正式发布；Spec VERIFYING/active

## 恢复与三视口矩阵

用户解锁后，`ioreg`没有`CGSSessionScreenIsLocked=true`，桌面可用。
重新运行专用CLI auto，HTTP服务34150、自动化9612；
新原生窗口41710可读且机型显示iPhone 5。实际`wx.getSystemInfoSync()`为320×568，
没有mock视口。此前未成功的菜单选择在新会话生效；这不是生产CSS修正。

```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /tmp/push-kids-footer-native-20261101 --auto-port 9612 --trust-project
NATIVE_EVIDENCE_REVISION=recovered-03 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 320 embedded
NATIVE_EVIDENCE_REVISION=recovered-03 node /tmp/push-kids-footer-design-20261101/native.cjs fixed 320 standalone
```

两次各24态0失败，48张PNG全部保存。和[恢复02](REPORT-FOOTER-TIPS-SCREENSHOT-RECOVERY-20261101.md)
已保留的390/430共96组组成当前完整矩阵：

| 视口 | embedded | standalone | 原生几何 | PNG解码/同名JSON的SHA |
|---|---:|---:|---|---|
| 320×568 | 24 | 24 | PASS，0失败 | PASS |
| 390×844 | 24 | 24 | PASS，0失败 | PASS |
| 430×932 | 24 | 24 | PASS，0失败 | PASS |
| 合计 | 72 | 72 | 144组PASS | 144张PASS |

各宿主24态：时间/科目/次数×首页/中间/末页/加载/长页码/菜单18态，
再加删除提示、长结果、预算、科目目录、只读与失败6态。
320保存于`report-footer-tips-20261101/recovered-03/`，
390/430保留原`recovered-01/`路径，不覆盖先前失败、几何或截图记录。
每图采集真实node rect/computedStyle和系统窗口数据，图像原始尺寸不作视口换算。

PNG经Pillow逐图解码、SHA逐项与同名JSON匹配；144组0失败。
当前来源、图像尺寸和SHA见[齐套manifest03](report-footer-tips-20261101/native-complete-manifest-03.json)，
[完整截图包](../../../output/BUG037-native-screenshots-complete-20261101.zip)包含144张原图/144份JSON与manifest。
不含真实孩子图片、账号标识或业务写入。

已视觉读取320内嵌删除提示、320独立长页码、320内嵌菜单及此前390内嵌删除提示；
提示不贴边，长页码仅中间折行，按钮仍同排；菜单自身完整可见且在Tab之上。
菜单是既有浮层，会覆盖其下方部分列表/分页，不宣称浮层展开时底层所有控件均可见。
原430尾部收起区/Tab几何与16组方法状态证据保持，真实触摸另验。

## 真机调试码已准备

保留原168份生产preview冻结包和官方preview成功1,192,127字节，
它只含旧0.1.17冻结166份及本Spec两份批准替换；无合成API、并行内容生成修改或发布。
本轮打开该preview做本地调试，语音插件provider
`wx069ba97219f66d99` / `0.3.1`报`41002, appid missing`，逻辑层URL的版本为undefined。
在独立调试副本固定libVersion3.16.2后仍有相同错误，假设未成立，不写成已修复插件。
原可用合成原生会话与生产扫码preview编译成功分别保留；不据本地插件错误断言手机编译失败。

新独立副本`/tmp/push-kids-footer-device-debug-20261101`仅DevTools配置改
`libVersion=3.16.2`与项目名，全部产品文件SHA与原preview一致；
[debug来源manifest03](report-footer-tips-20261101/device-debug-source-manifest-03.json)逐项留证。
没有移除插件或更改生产源码、AppID、云托管环境/服务。

通过已安装工具的正式自动化端口9614调用微信官方`Tool.enableRemoteDebug({auto:false})`，
获得[无线真机调试二维码](../../../output/BUG037-remote-debug-20261101.png)。
命令合同核对来自微信官方npm包`miniprogram-automator@0.13.0`的`MiniProgram.remote()`，
其使用`Tool.enableRemoteDebug`并等待`Tool.onRemoteDebugConnected`；
没有修改工具二进制或使用未声明私有调用。
当前[连接状态](report-footer-tips-20261101/remote-debug-status-03.json)为WAITING_FOR_DEVICE_SCAN，
二维码生成仅代表扫码入口准备完成，不代表手机已连接或真机验收通过。

USB/adb仍无手机；无线调试不要求USB，用户用项目开发者微信扫码即可连接。
本轮启动十分钟有界连接监听，只保存设备型号/系统/微信/库版本和数值窗口信息，
不采集家庭身份、儿童内容或执行业务写入。连接后的原始真机截图含孩子内容时保留在
批准的本地私有/临时测试位置，仓库仅纳入脱敏图、数值和哈希。
扫码是账号本人操作；不冒充“用户已经解锁”同时确认了扫码或真机成功。

## 当前验收和文档闭合

| TP | 当前结果 |
|---|---|
| TP-001 故障基线 | 保留PARTIAL：320/390基线提示padding=0复现，分页掉行未复现，430基线缺失 |
| TP-002 批准设计 | 原54张/SHA冻结，PASS，不代表真机 |
| TP-003 回归/静态 | 原349项和检查PASS，生产源未变，不重复无关全套 |
| TP-004 修复原生矩阵 | PASS：两宿主三视口144组PNG/节点/解码/SHA；合成默认字体模拟器范围 |
| TP-005 设备/触摸/可访问性 | PARTIAL：原16组方法/尾部通过；真实iOS/Android、点击、大字/读屏NOT_RUN，等待扫码 |
| TP-006 文档/政策 | PASS：Feature/UI、设计索引、Spec/状态与发布当前正文同步，批准源SHA/链接/diff检查通过 |

Behavior BHV-033、Architecture、FEC/测试策略规则与零生产diff一致，当前正文无新增冲突。
原实施01/恢复02的当时缺项保留历史结果并指向03；不覆盖旧manifest。
此任务尚未上传覆盖本源码，Spec仍VERIFYING且位于`specs/active/`，
正式验收与云交付DONE归档门槛独立，不将preview视为云开发交付。
