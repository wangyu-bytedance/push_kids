# 孩子足迹原生布局证据 — 2026-10-18

Status: **合成布局子集 PASS / TP09 PARTIAL / NOT_RELEASED**。本证据没有通过整个功能、27态设计一致性或真实设备验收。用户回复“已解锁，可以继续原生验证”后恢复采集。

## 环境与结果

微信开发者工具 Stable 2.01.2510290，基础库3.17.4，字体设置15，模拟器显示比例75%。以下尺寸由运行时 `wx.getSystemInfoSync()` 返回，脚本在采集前校验；屏幕高度包含微信原生导航，节点与截图对应内容窗口。

| 模拟设备 | 屏幕 | 内容窗口 | 设备DPR | 官方截图像素 | 状态数 |
|---|---|---|---|---|---|
| iPhone 5 | 320×568 | 320×504 | 2 | 640×1008 | 24 |
| iPhone 12/13 (Pro) | 390×844 | 390×753 | 3 | 780×1506 | 24 |
| iPhone 14 Pro Max | 430×932 | 430×834 | 3 | 860×1668 | 24 |

共72份原生节点JSON和72张PNG。每份JSON含采集时间、实际视口、选择器矩形、字号、状态断言、截图尺寸与SHA-256；[manifest.json](manifest.json)包含完整文件及源码哈希。官方 `App.captureScreenshot` 在本环境按内容窗口2倍采样，与设备DPR不是同一个值。所有图片为本地相机插画，无真实儿童照片；所有姓名、地点、日期为合成数据。

24态：timeline、empty、consent、importing、review、batch、confirm、playback、paused、lit、world、place、failed、unknown、viewer、map-error、ai-settings、archived、photo-edit、photo、loading、error、long-content、candidates。

断言覆盖所列节点的水平边界、字号≥14px、所列交互目标≥44px（1px采集容差）、三视图/三地图范围按钮、双字段等宽及间距、底部操作数量/宽度/可见性、标题与关闭按钮间距、44px选择/48px关闭按钮、长姓名与有图草稿布局。地点候选额外滚动至可视区域，验证三条候选完整位于原生滚动容器内；目检320候选长名换行。没有用隐藏水平溢出替代矩形验证。

## 本轮实际修正

微信原生 `button:not([size=mini])` 默认规则优先于单一角色类，曾使关闭/选择按钮宽184px、底部按钮不能铺满。生产WXSS增加页面/面板作用域，关闭48×48、选择44×44、底部按钮铺满可用宽度，三视图及范围按钮等宽、间距8px。修正后矩形检查通过。未改变业务语义或模块边界。

## 隔离副本与复现

390采集副本：`/private/tmp/push-kids-footprints-native-20261018`；320/430副本：`/private/tmp/push-kids-footprints-native-r2-20261018`。它们没有写入生产配置或使用真实家庭服务。以下差异均仅存在于临时副本：

- `config.js`关闭云调用，指向未启动的 `http://127.0.0.1:18769/api/v1`。
- `app.json`将足迹调为首页面；原语音插件报41002，副本清空plugins，生产插件保留。
- `index.js`在onLoad替换load为空操作，并加入 `applyGeometryFixture(serialized) { this.setData(JSON.parse(serialized)); }`。JSON在页面运行域解析，避免跨运行域数组长度失真；工具也停止轮询、播放和预览请求。
- `index.wxml`仅为 `.fp-sheet-body` 增加 `scroll-top="{{geometryScrollTop}}"` 测试绑定。候选态先测量相对位置，再设置原生scroll-top；该绑定不在生产WXML中，不证明真实用户滚动手势通过。
- r2固定基础库3.17.4并关闭lazyloadPlaceholderEnable；r1项目配置与生产文件一致，基础库由工具选择。生产WXSS与两个副本逐字一致，SHA见manifest；其他足迹模块、WXML去测试绑定后与生产逐字一致。

在开发者工具选择对应设备，再为当前运行时启动新的本机automation端口。切换设备复用旧端口可能仍返回旧运行时；脚本遇尺寸不符直接失败，不写该组证据。

```bash
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project <isolated-copy> --auto-port <new-local-port> --trust-project
MINIPROGRAM_AUTOMATION_WS=ws://127.0.0.1:<new-local-port> node tools/footprints_geometry.js <320|390|430> docs/quality/evidence/child-footprints-20261018/native
node tools/footprints_geometry.js audit docs/quality/evidence/child-footprints-20261018/native/*-320.json docs/quality/evidence/child-footprints-20261018/native/*-390.json docs/quality/evidence/child-footprints-20261018/native/*-430.json
```

最终390/320/430端口分别9434/9436/9438，仅供本次运行记录，不保证重启后有效。截图偶发15s超时的单态已按相同夹具重新采集；最终清单无NOT_RUN截图、无错误断言，SHA/PNG尺寸复核通过。失败截图不计PASS，旧对应PNG会清除。

独立只读Reviewer `footprints_readonly_review`复核72份节点audit及各JSON内的PNG SHA，目检三个视口候选，并核对副本差异：**PASS，CR009 CLOSED**。人工把候选移出body的内存变异能被断言拒绝。外部manifest生成后又经独立复核：144个节点/PNG文件哈希、14个源码哈希、两副本12个文件哈希均匹配，冻结设计源不变，README范围说明一致。该PASS仅适用于本证据声明的合成布局子集。

## 尚未覆盖的门禁

批准设计27态中的records、import、saved、denied、photo-delete、expired、draft-delete尚无本轮三视口原生导出；本次额外4态不能抵扣它们。原生删除系统确认框、相册/地图授权、拒绝、键盘弹出、字体放大、屏幕阅读、前后台与真实播放拖动仍待验。只读/归档/处理中等状态来自合成数据，截图不是业务操作成功证据。

本次移除插件、绕开load的副本不能代表完整生产包编译、启动与记录页入口通过。iOS/Android真机、真实私有图清晰度、地图账号/海外覆盖/坐标与底图、AI效果/费用、MySQL5.7均未由本证据验证。全球图仍是坐标示意；与冻结DREV01的控件、图标、圆角及全球呈现差异需另行设计评审，未经批准不降低原合同。Spec继续VERIFYING，未上传或发布。
