# 旅行日记导入精简 — DREV02

- Status: APPROVED / LOCAL_IMPLEMENTED / VERIFYING
- Design Revision: DREV-20261025-TRAVEL-IMPORT-02
- Task Spec: [导入精简Spec01 / Architecture01](../../../../../specs/active/FEAT-012-TRAVEL-IMPORT-SIMPLIFICATION.md)
- UI IDs: UI-018；UI-001内嵌回归
- Baseline: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，沿用已批准基线
- Source: [index.html](index.html)，自包含，无网络/storage/儿童照片
- Manifest: [APPROVAL.md](../../snapshots/UI-018/DREV-20261025-TRAVEL-IMPORT-02/APPROVAL.md)
- Approval: 产品负责人2026-10-25明确回复“批准导入精简 Spec01＋Architecture01＋DREV02，按此实施”；设计批准不代表代码已实现

操作型页面，沿用暖纸/松绿、14px正文和既有胶囊按钮。删除用户截图整块：说明、保留期提示、处理同意勾选、重复AI开关及供应商说明。点击导入直接打开系统相册；取消返回，选中后仅显示真实上传数量/进度，失败有重试。AI只使用已有更多→足迹设置入口，不复制长说明。

## Exact viewport/state matrix

320×568、390×844、430×932，DPR1，以下5态各3张，共15张。正文≥14px、普通触控≥44px、主CTA≥48px/16px；暖纸色、布局和系统相册交互习惯沿用原批准基线。

| State | Contract |
|---|---|
| entry | 导入照片按钮直入相册；原手动入口保留，无说明面板 |
| selecting | 原导入按钮忙态；宿主保持当前页面，系统相册由微信绘制 |
| uploading | 实际数量/进度，禁止重复操作；没有解释性段落 |
| upload-error | 已上传数量、具体失败与重试/核对已上传动作 |
| settings | 既有AI成员开关与保存，原值保持 |

HTML中的selecting仅展示宿主忙态，不模拟或宣称系统相册授权完成。原生系统外观属于允许差异；取消/返回语义不允许省略。原缺日期/核对/确认/编辑/画廊与地图仍沿用DREV01，不在本稿重画。

## Engineering and approval boundary

本地生产实现已完成；349项前端、当前源码15组原生节点/PNG与430实际取消/多选/失败重试通过，设置两值往返为原生方法验证，见[本轮证据](../../../../quality/evidence/travel-import-simplification-20261025/README.md)。真机/可访问性/家长验收NOT_RUN，未上传部署。批准源及15张设计图保持冻结。

离线HTML验证：5态×3视口15张导出通过，触控/字号/对话框边界与选择忙态、失败重试、设置值保存交互通过，浏览器错误0、外部请求0；详见manifest及同目录render-audit.json。320短屏按原页面正常滚动抵达导入按钮，没有隐藏溢出。该结果仅证明设计提案，不代表生产代码、原生或真机验收。

原imports/controller/WXML owner调整，删除consentChange/photoConsent和旧空面板路径；不改后端API/Schema、AI默认值或照片保留规则。取消零业务写入，AI不自动启用；错误可恢复、真实scope变化作废回调。其他FEC维度与测试点见Task Spec。

批准对象：SPEC-20261025-TRAVEL-IMPORT-SIMPLIFICATION-01＋ARCH-20261025-TRAVEL-IMPORT-SIMPLIFICATION-01＋DREV-20261025-TRAVEL-IMPORT-02。批准前只有设计证据；原生/真机验收需实施后另执行，旧截图不抵扣。本轮不含部署或代码包上传。
