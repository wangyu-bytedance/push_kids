# 六主题本地实现 — DESIGN-002 Spec08

批准：用户2026-11-06“好的 按照以上方案落地”，对应[Spec08 / Architecture01](../../../../specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)、DREV08设置底部入口及DREV06五主题视觉方向。当前是 **IMPLEMENTED_LOCAL / VERIFYING / NOT_UPLOADED**，没有推进体验、审核或正式发布。

## 实现与回退

- 一个`presentation/theme`域、六个稳定ID和同一套17路由业务实现；registry独占token、字体、形状、材质、插画、glyph回退和原生chrome。页面/组件显式组合生命周期，不改写全局Page/Component。
- 设置底部列表在“提醒设置”后、“关于知芽”前打开六选一面板。候选不立即应用，关闭取消，确认后同步存活/后续页面；本机`pk.theme.v1`只保存版本和ID，全孩子共享。读失败回原始，写失败本次会话仍应用并明确提示。
- 未预置科目/活动固定用书本/嫩芽/小星球/罗盘星/贝壳/芯片，不运行AI、不下载主题、不要求选图。已知活动关键词映射保持。
- 图标路径生成一次，运行时按语义tone绘制本地SVG背景；无新运行时框架或字体包。五张JPEG来自批准DREV06源，原始插画保留。图片失败仅隐藏装饰或显示文字回退。
- 回退本次前端diff即可恢复原始实现，旧客户端忽略显示偏好；无数据库/业务事实迁移，清理家庭或孩子不额外删除主题偏好。

## 同版本自动化

| 检查 | 实际结果 / 证据 |
|---|---|
| 实施前前端基线 | 359 PASS；[baseline](baseline-frontend.log) |
| 新偏好状态Red | 最小stub下4项中3项预期失败；[Red](red-theme-state.log)，不是人工制造失败 |
| 生命周期反例 | 旧根层attached被新lifetimes覆盖，新增测试实际失败；[Red](red-legacy-lifecycle.log)，修复适配器保留原生lifetimes优先级 |
| 主题专项 | 9 PASS；[Green](green-theme-contracts.log)，含恢复/非法值/读写失败、重复切换、订阅释放、Promise/this/参数、草稿/游标/忙态保留、当前页chrome、legacy生命周期、六回退与候选/取消/应用 |
| 前端全量 | 368 PASS，0FAIL/0SKIP；[最终日志](final-frontend.log) |
| ESLint | PASS；[日志](final-lint.log) |
| 主题合同/边界/资源/对比度 | PASS；[报告](contracts.json)、[日志](final-theme-check.log) |
| 小程序结构及包体 | 17pages / 1,320,423 source bytes PASS；[日志](final-miniapp.log) |
| 架构检查 | 5policies / 156modules PASS；[日志](final-architecture.log)；前端theme边界另由主题guard覆盖 |
| 当前设计政策 | PASS；[日志](final-design-policy.log)，批准快照未改 |
| DREV06/08标准manifest | PASS；[06](final-design-06.log) / [08](final-design-08.log)。原非标准APPROVAL解析失败保留在initial-design-format日志；新增CANONICAL-APPROVAL仅转换既有哈希与后续明确批准，原清单/源/导出未改。17+12个源与988+56个导出逐项SHA一致，见[完整性](design-integrity.json)。 |
| glyph与token再生 | SHA前后相同；[generation.json](generation.json) |
| 新增Python工具Ruff/format | 3文件PASS；只涉及生成/合成原生检查工具 |

本轮无API/backend/DDL变更，Python业务全suite、mypy及数据库集成为N/A；不把之前040发布检查当作本diff检查。所有命令实际执行，设备项目不因自动化通过而改标。

## 资源与可访问颜色

基线提交`e221d8d61bc164dc27b2309e62f04d3bcf4360ba`源码1,244,228字节，最终1,320,423字节，净增76,195字节（约74.4KiB）；五主题插画141,499字节，非插画净增-65,304字节。删除旧的glyph×颜色生成副本抵消资源成本，未删除原始插画。包体小于现有1,500,000硬上限，未提高预算。主题guard使用显式`--baseline=e221d8d61bc164dc27b2309e62f04d3bcf4360ba`，避免本轮中途HEAD推进使增量被低估。

[assets.json](assets.json)记录每张来源SHA和字节：garden33,619、space33,870、midnight16,501、ocean33,004、tech24,505。总量硬门禁PASS；garden/space/ocean超过单张30,000的**目标**，总量未超限，未伪称逐张达标。压缩使用系统sips JPEG quality62 / 最大780px；源设计图保持冻结。

六主题单次呈现数据3,832–4,419字节（精确值见contracts），仅ID偏好约30字节，分别低于32,000/256字节。正文、次级、弱化文字、主按钮、危险/提醒/成功文字七组语义对各≥4.5:1。共用touch角色修正为44px，避免320屏幕上88rpx/72rpx按钮触区不足；最终原生矩阵检查btn、添加和图标按钮及选择卡最小尺寸。装饰色、图表边界、图片上文字、禁用及系统控件仍需结合原生/设备审查，不能由色对计算宣称全界面可访问性通过。

保留的固定值有明确语义：原生系统危险确认色、平台地图底图上的路线色、照片遮罩/白字、原活动持久化color领域元数据。系统授权框、picker内部、微信菜单和地图底图由平台控制；不声称应用可重绘。

## 原生呈现证据与边界

`tools/prepare_theme_native.py`复制当前生产源至`/private/tmp/push-kids-themes-native-20261106`，禁用云业务写入/插件，以合成家庭/孩子数据驱动真实WXML/WXSS、theme state/adapters、图标与组件。17路由加载生命周期仅在副本中停用，每个场景重置其初始data以防上一个表单遗留；调用实际页面方法setData，不使用只改变逻辑层数据的无效夹具。生产源码SHA在各尺寸`source-sha256.json`绑定。

`tools/theme_native.js`从app.json与registry枚举17×6×3=306路由组，加8共享状态×6×3=144组，共450组。`wx.createSelectorQuery`采集真实节点尺寸/计算色、截图及SHA；校验路由/主题/精确screen viewport、页面/弹层横向边界和对应状态节点存在。相同路由内检查六主题以减少WebView反复创建；所有失败保留在报告中。

最终结果为 **PARTIAL**，见逐组[最终汇总](native-summary.json)：320×568有30组当前源码的原生节点测量，其中25组同时有匹配SHA截图，5组缺截图；这些组的已选节点尺寸、触区和状态校验未发现错误，不代表完整视觉验收。另9组因RPC超时未取得测量，111组未开始。390×844已有150组旧版本采集，但5个源文件与最终diff不符，全部不计本次验收；430×932未执行。合计450组中，25组有当前节点和截图、5组只有当前节点、9组采集失败、411组NOT_RUN。320详细报告见[矩阵](native/320/matrix.json)，390[历史报告](native/390/matrix.json)仅保留诊断，不作为当前PASS；430没有伪造报告或截图。

最终有界恢复尝试被开发者工具的服务端口关闭阻止，CLI返回246，见[工具阻塞](native-tool-blocker.md)。没有为继续测试修改安全设置。工具代码已加入连续RPC失败后停止和截图超时显式记录；最后这组恢复改动通过语法检查，未能重新执行完整原生矩阵。旧动作探针曾对六主题的候选/取消/应用、同步、草稿保留、零业务请求与本机偏好完成检查；其未绑定最终源码清单，仅作历史诊断，不计当前原生验收。当前逻辑合同由9项专项测试覆盖。

早期native-probe/native-390/attempt记录仅为历史诊断：曾有截图超时、开发者工具卡死、夹具未刷视图、状态未重置及导航选中项未随夹具更新。已修正采集工具并尝试重启隔离项目；这些历史截图不算最终矩阵。开发者工具使用Stable2.01.2510290 / 基础库3.17.4，运行时使用disable-gpu；不因此声称真实GPU性能。已检查的30组也不覆盖全部业务节点、所有可点击区域或读屏顺序。

## 文档闭环、审查与剩余门禁

已逐项核对并同步FEAT-001、BHV-046、Architecture/Constraints、UI-001/009/010/011/015/016/017/018、FDB/FEC、AGENTS六主题规则与Spec/STATUS。修订当前正文中“仅原始风格”“tokens文件唯一源”“六套图标色副本”“未知星形”等冲突；各特性原字段/权限/排期/发布阶段保留。UI-014为已取消且未实施草案，N/A。其他Feature的领域合同无变化，其页面呈现证据归对应UI文档，避免把主题误写成领域功能。

实现者自查发现的legacy生命周期已用Red/Green修复。**R2新上下文独立只读Review：NOT_RUN**，本次未以自查冒充独立审查。完整真机iOS/Android、读屏/大字/键盘/系统返回、原生全业务端到端、真实内容及点击至视觉稳定≤300ms：NOT_RUN或待补，不由合成呈现矩阵代验。物理返回取消与入口焦点恢复需设备确认；onHide关闭与候选不持久化有代码/合同依据。

Spec最终保持`VERIFYING`，路径`specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md`。尚无匹配六主题范围的官方云上传，不能DONE或移completed；原0.1.18不覆盖本增量。恢复条件为补齐上述验收/独立Review并在后续获得发布授权后执行仓库发布合同。
