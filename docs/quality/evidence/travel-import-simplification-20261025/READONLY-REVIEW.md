# 导入精简 — 单独只读复核

- Gate: PASS
- Findings: 无已验证的可执行问题。
- Scope: 获批导入精简Spec01/Architecture01/DREV02；原工作区已有BUG-035和其他改动保留，不将本增量扩大为全部dirty工作区审查。
- Baseline: HEAD `0576ac30464908154c624effed41df6dfa3110cc`＋既有BUG-035本地实现；target为source-native-manifest.json绑定的当前7份足迹源码。复核阶段只读，没有代码/配置/外部状态写入；本报告在复核结束后的交付登记阶段保存。
- Reviewer: Codex，同一代理单独只读阶段；未使用第二名代理，不将其写为独立人员签字。

| Invariant | Trace / evidence | Result |
|---|---|---|
| 直入相册、取消零写 | beginImport→choosePhotos同步chooseMedia；只有收到非空tempFiles后才调用uploadBatch→POST imports；取消/拒绝测试无写 | Matched |
| AI成员偏好不被导入覆盖 | 导入无PATCH preferences；仅saveSettings写；worker继续读取成员既有偏好；false/true动作回归及原生往返 | Matched |
| 重试/部分成功 | pendingBatchKey稳定、received_at跳过；upload-error保留pendingFiles，重试到review；真实合成1/3→3草稿 | Matched |
| 生命周期/权限 | family/member/child/generation/disposed校验、embedded.canLeave，show恢复读取；scope边界与viewer/归档服务端guard保持 | Matched |
| UI/文档/兼容 | 旧说明/checkbox/photoConsent/consentChange删除，settings既有入口；当前DREV02/旧局部替代与349/15证据分开 | Matched |

变更影响仅原footprints owner的UI/选择调用时机，无新模块、Schema、API字段或依赖，不改变过期/确认/查询预算，不删除媒体。现有后端的ImportCreate.consented=True合同继续由明确选图导入动作提交。整个工作区未来发布仍受BUG-035后端优先约束。

已运行证据：[349项前端、专项58、ESLint、小程序源预算、DAG150、设计SHA及15份原生节点/PNG](README.md)。完整图片/密钥/原始模型未进入新增证据。后端/实库无本增量变化，未重复全套测试；iPhone/Android、真实EXIF保留率/HEIC、读屏/大字/家长验收未执行，仍为产品验收缺口，不批准发布。
