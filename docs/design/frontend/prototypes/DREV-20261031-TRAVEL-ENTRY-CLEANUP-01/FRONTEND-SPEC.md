# 旅行日记入口精简 — DREV01

- Status: APPROVED / LOCAL_IMPLEMENTED / NATIVE_NOT_RUN
- Design Revision: DREV-20261031-TRAVEL-ENTRY-CLEANUP-01
- Task Spec: [入口精简 Spec01 / Architecture01](../../../../../specs/active/FEAT-012-TRAVEL-ENTRY-CLEANUP.md)
- UI IDs: UI-018；UI-001 内嵌旅行回归
- Baseline: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02（既有 APPROVED 基线）
- Source: [index.html](index.html)与同目录22个场景SVG；HTML内联相同SVG，全部自包含，仅合成状态和仓库已有插画，无外部资源/Storage/真实儿童信息
- Manifest: [APPROVAL.md](../../snapshots/UI-018/DREV-20261031-TRAVEL-ENTRY-CLEANUP-01/APPROVAL.md)
- Approval: 用户于2026-10-31在本对话回复“批准”，批准 SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01 / ARCH-20261031-TRAVEL-ENTRY-CLEANUP-01 / DREV-20261031-TRAVEL-ENTRY-CLEANUP-01；记录见 Task Spec 的 Approval record

## 可见合同

删除零草稿时三视图下方“查看待整理照片”和空时间线下“手动记录”。删除真实节点及占位，不迁入更多菜单，不新增帮助/解释。保持原插画和“还没有足迹”，下方唯一“导入照片”主操作跟随页面滚动，空态自然收高。

有真实草稿时“X 张待核对”继续显示并进入既有核对流程。历史无图到访使用原文字展示，纠正/删除继续可达。学习手动输入、照片日期/地点人工纠正保持原流程。主按钮、三视图、孩子chip、更多、标题、导航及色彩/字阶均继承有效 DREV。

本 DREV 只接管上述入口区域。DREV-20261025-TRAVEL-IMPORT-02 的直接相册、忙态、上传/失败/设置仍有效；其余旅行 DREV 的核对/编辑/地图/画廊和领域合同不重画。批准前不修改任何旧批准源或 manifest。

## 精确视口与状态

320×568、390×844、430×932 逻辑像素，portrait，DPR1。每态三个主图PNG，共21张；另有320错误顶部辅助1张，总22张。暖纸/松绿、正文≥14px、普通触控≥44px、主CTA≥48px；保留安全区和导航下方空间。必要时SVG表示滚动至主操作的位置，不宣称全内容同屏；320错误顶部另单列。设计没有增加隐藏横向溢出的样式。

| State | Contract |
|---|---|
| empty | 0正式/0草稿；两处按钮消失，原插画/标题＋导入 |
| drafts | 0正式/3草稿；实际“3 张待核对”保留，可恢复处理 |
| legacy | 历史无图到访以文本和真实0照片数显示，没有新建手动入口 |
| loading | 保留加载状态；不出现零草稿兜底或手动创建按钮 |
| error | 原错误/重新读取保留；空态与导入不增加替代说明 |
| viewer | 原只读短标签；两入口和导入均不出现 |
| archived | 已归档短标签；不出现新增导入/手动创建入口 |

示例孩子与到访均为合成内容。插画仅使用仓库已有 record-camera.png 的内联副本；没有复制用户截图。HTML是内联SVG状态浏览器，导入/核对只作设计图形，不调用微信相册、API或更改家庭数据。正文采用Heiti SC、标题Songti SC系统字体；原生产token与微信实际字体不修改。

## State ↔ component mapping

| Design region | Existing owner | Change |
|---|---|---|
| 三视图后的草稿区 | footprints/index.wxml / openDrafts | 删除零草稿else；实际数量分支保留 |
| 时间线空态 | footprints/index.wxml / fp-empty | 删除 manualEntry 按钮；插画/标题与原padding保留 |
| 新建无图状态 | controller/photos.js | 删除无消费者创建路径；不影响历史 is_manual 展示 |
| 导入/核对/历史详情 | imports/photos/controller | 存活状态/事务合同保留，既有回归重跑 |
| 两种旅行宿主 | embedded 与 Page | 使用同一模板/控制器，不新增复制页面 |

## 工程与验证边界

按 Task Spec TP01..TP06 分开记录：22张SVG导出保留原尺寸/摘要与声明几何证据，本轮批准清单及current-policy校验通过；本机浏览器启动失败，HTML渲染/DOM/交互NOT_RUN。本地原WXML/controller/photos已删除入口及创建路径，349项前端回归、ESLint、源码预算和DAG151通过。官方CLI open初始化被沙箱以EPERM拒绝，因此最终源原生三视口几何/实际点击和用户功能测试仍NOT_RUN，没有原生编译或真机通过结论。resvg-py仅在/private/tmp作为验证依赖；无生产依赖/持久化状态/日志变化，客户端不再调用manual创建API；服务端兼容API及family/child授权保留。

审批对象：SPEC-20261031-TRAVEL-ENTRY-CLEANUP-01＋ARCH-20261031-TRAVEL-ENTRY-CLEANUP-01＋DREV-20261031-TRAVEL-ENTRY-CLEANUP-01。批准后在原领域实施并本地重编译，不含代码包上传。
