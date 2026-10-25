# DREV-20261024-FOOTPRINTS-TIMELINE-01 — 旅行按钮与倒序时间线

- Status: APPROVED
- Task: [BUG-034 Spec01](../../../../../specs/active/BUG-034-FOOTPRINTS-CONTROLS-TIMELINE.md)
- UI: UI-018 / UI-001
- Baseline / engineering: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02（均已批准，本稿无例外）
- Source: [index.html](index.html)，独立自包含HTML，合成人物/日期/插画，无网络或业务写入
- Exports / SHA: [候选清单](../../snapshots/UI-018/DREV-20261024-FOOTPRINTS-TIMELINE-01/APPROVAL.md)
- Approval: 产品负责人（用户）2026-10-24在call_a4e6de3e6be5408fb860b26f20a09323回复「批准 Spec01＋Architecture01＋DREV01，按此实施」；仅覆盖本局部增量，其他旧批准范围保留

视觉方向：沿用学习页的暖纸、松绿和胶囊控件，让日期、照片和实际时刻成为时间线的主要信息。

## 可见合同

三视图使用实际学习原子`.seg.n3`的pill外框/单项；当前项纸色底、松绿字、500字重与轻阴影，不再深绿矩形填充。三项文字不换行、不截断，三等列；≥44px高与14px字。主操作使用`.btn`的松绿pill、16px/48px；次操作浅绿或文字语义、≥44px/14px。关闭/列表/照片目标保持相应角色，无全局tokens调整。

时间线日期从新到旧，卡头显示已确认当地日期、地点、真实照片数；每卡最多4缩略图，两列，图下显示HH:mm，缺时刻明确“时刻未知”。日内同组不改既有照片顺序，同日到访保留稳定服务端次序；回放仍向前。不以上传/创建时间推断未知；手动无图显示“手动到访”，不伪造缩略图。失败/加载用等尺寸占位保留可读标签；预览沿用已有详情与私有媒体路径。

## 精确矩阵

各状态均导出320×568、390×844、430×932，1x；底栏预留88px及内容安全留白，保持页面可滚动。

| state | 覆盖 |
|---|---|
| overview | 三个倒序日期、已知/未知时刻、手动无图、默认选中、导入按钮在内容之后 |
| preview_failed | 缩略图不可预览仍有时间及详情入口 |
| empty | 无数据与手动/导入入口 |
| loading | 读取中，不误报空数据 |
| error | 失败、pill重读、恢复 |
| viewer | 只读、无导入写入 |
| long | 长孩子名/地点折行，三列按钮/缩略图不溢出 |
| playback | 回放tab与播放pill，地图/回放既有结构 |
| lit | 地图tab与次操作胶囊 |
| settings | 紧凑设置、保存pill |
| saving | 保存禁用/进行中，与原保护一致 |
| photo | 预览详情及修改主操作pill |
| older_window | 后续较旧窗口，整体替换后回顶部，仍倒序 |
| standalone | 独立Page同款控件、无记录底栏 |

合计14×3＝42张。HTML中地图为合成示意；不证明真实地图、EXIF、照片上传或原生控件。设计中合成插画只是缩略图排版样例，不引入生产图片资源。

## 工程与验收边界

复用共享footprints owner及现有controller/presentation，初次/续页映射显示标签而不排序整页；原cursor/100窗口/≤4预览/并发与临时文件释放不变。时间label从确认字段派生，禁止新日志/儿童数据/存储缓存/第三方资源。前端包≤1.5MiB，样式only不扩接口，设备读屏/大字体、三视口原生节点与实际交互在批准后验证，不用这42张HTML图抵扣。

本DREV仅覆盖上述控件和时间线信息，不重画学习页、地图、上传/确认/归档流程。旧DREV按原范围保留，相应manifest仅追加本局部Superseded by指针。已按批准范围本地实施，源码/测试/原生和设备边界见[本轮证据](../../../../quality/evidence/footprints-timeline-20261024/README.md)；批准HTML与42张快照保持冻结。
