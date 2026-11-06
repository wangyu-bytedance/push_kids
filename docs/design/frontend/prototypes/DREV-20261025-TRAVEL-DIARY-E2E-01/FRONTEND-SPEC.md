# 旅行日记全链路修复 — DREV01

- Status: APPROVED / LOCAL_IMPLEMENTED / VERIFYING / NOT_UPLOADED
- Design Revision: DREV-20261025-TRAVEL-DIARY-E2E-01
- Task Spec: [BUG-035 Spec01 / Architecture01](../../../../../specs/active/BUG-035-TRAVEL-DIARY-END-TO-END.md)
- UI IDs: UI-018；UI-001嵌入只回归
- Baseline: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，沿用既有批准
- Source: [index.html](index.html)；无外部资源、网络、storage或儿童照片；仅合成插画
- Manifest: [APPROVAL.md](../../snapshots/UI-018/DREV-20261025-TRAVEL-DIARY-E2E-01/APPROVAL.md)
- Approval: 产品负责人（用户），2026-10-25，明确回复“批准 Spec01＋Architecture01＋DREV01，按此实施”；源/快照冻结
- Implementation evidence: [本轮回归与原生证据](../../../../quality/evidence/travel-diary-e2e-20261025/README.md)；最终源14态×3原生42组通过；真实云三张草稿/城市/预览及失败续接已验，真实日期/正式确认、新focus云端、实际键盘/设备/可访问性尚缺；HTML与批准快照不改

沿用暖纸色、松绿色、14px正文和既有胶囊按钮；通过照片预览、明确下一步和可恢复错误，让家长完成核对、补日期、确认与精确回看。页面是操作型界面，不新增装饰或导航层级。

## Scope and interaction

1. 导入授权保留处理/保留期/可选AI说明；未同意时主CTA禁用。选择中/上传中阻止重复操作，取消返回授权。上传分阶段，失败重试同批次剩余文件。
2. 核对保留勾选数量；缺日期时主CTA“补拍摄日期”，进入只对选中缺日期照片生效的日期面板；已知日期不被覆盖。所有必填满足后主CTA进入“确认到访”。不默认日期为今天。
3. 单张编辑显示当前照片，日期/时刻/地点仍可人工填写；保存后保留选择和最新服务端版本。批量修改失败保留输入；版本冲突明确刷新后继续，不能重复提交成功条目的旧version。
4. 图片处理失败可重试；AI失败/无候选不妨碍人工填写。未定位照片可入时间线，并提示地图未点亮；实际地图点位仍需可靠坐标。
5. 点击时间线指定缩略图从该照片打开；前后页可达。正式修改仍经过既有版本校验；删除保留原确认，不在本稿里重设计。
6. 系统相册/地点/大图与后台返回后恢复原表单/选择/轮询和有效预览；实际切scope或卸载才丢弃旧回调。遮罩内独立滚动，顶部关闭与底部CTA固定，键盘上方可达。

## Exact viewport/state matrix

320×568、390×844、430×932逻辑像素，DPR1设计导出。以下14态每态3张，共42张。原生实施后需相同视口节点几何/截图、触控目标≥44px、主CTA≥48px/16px、正文≥14px、横向/遮挡/滚动断言。

| State | Visible contract |
|---|---|
| consent | 首次同意、可选AI、未同意禁用 |
| uploading | 2/3上传中，避免重复点击 |
| review-missing | 选择数量、缺日期、补日期主CTA |
| batch-date | 仅选中且缺日期的照片补日期 |
| edit | 当前照片预览、日期/时间/地点表单 |
| review-ready | 保留选择与已补日期，确认主CTA |
| upload-error | 部分成功、继续未完成上传、查看已上传 |
| processing-error | 处理失败可重试，不伪装已完成 |
| conflict | 保留输入/选择并刷新继续 |
| confirm | 家长确认真实到访、缺地点可时间线入档 |
| saved | 入档统计/照片/时间线入口 |
| gallery-focused | 点击第三张即显示第三张，前后切换 |
| readonly | 只读无新增入口 |
| edit-keyboard | 210px键盘占位，编辑面板主CTA与关闭可达 |

loading/empty/archived/地图错误等沿用有效DREV，本轮不改变视觉合同；实施仍需回归生命周期。HTML键盘占位只是设计示意，不能替代原生真实键盘/节点/设备验收。日期picker/相册/地图由系统绘制，平台外观差异可接受，输入/取消/返回语义不可省略。

## Engineering and resources

沿用现有footprints组件，父records协调仅通过公开方法/事件；表单在photos owner，上传/勾选在imports owner，页面恢复在controller owner。数据库/API为remote state，家庭/孩子/成员隔离与过期回调保护不因“恢复”弱化。新照片焦点窗口走服务端索引有界读取，禁止循环拉完整历史。列表/图库/预览上限及7天/24h不变；真实照片/私有URL/身份/精确坐标不进仓库、日志或本地storage。

错误同时用文字和可执行动作，不依赖颜色；开关/勾选有可访问名称、禁用说明和aria状态；表单/面板键盘焦点与读屏需原生实测。性能/安全/观测和TP矩阵以Task Spec为准，不新增全局共享层或第三方依赖。

## Approval boundary

批准必须明确BUG-SPEC-20261025-TRAVEL-DIARY-E2E-01＋ARCH-20261025-TRAVEL-DIARY-E2E-01＋DREV-20261025-TRAVEL-DIARY-E2E-01。仅授权本Spec实现与测试，不包含上传代码包、部署、发布、批量数据修复或推断真实出游信息。设计导出只用于评审，不代表当前小程序已修复或通过原生/真机验收。
