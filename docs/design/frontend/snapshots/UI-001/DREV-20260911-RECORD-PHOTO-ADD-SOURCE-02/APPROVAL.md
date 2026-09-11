# 照片统一追加入口批准快照

- Spec: `SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02`
- Design: `DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02`
- Owner/approver: 用户，2026-09-11
- Approval: “对 按照这个方案落地”
- Scope: 首张和后续添加统一为一个入口；每次均由微信原生媒体选择提供拍摄或相册；拍摄可返回后继续追加，相册可多选；共享 9 张上限；取消/失败保留表单
- Baseline/FEC: `FDB-20260906-03 / FEC-20260906-04`
- Figma: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1 （既有 FEAT-001 waiver anchor，非新增节点）
- Evidence exception: 沿用 FEAT-001 scoped Figma waiver，公开生产发布前到期；不免除 320×568、390×844、430×932 与代表性 iOS/Android 的原生媒体选择/连续拍摄验收
- Implementation evidence: 本地实现已完成；前端 135 passed，ESLint、小程序静态/架构校验通过，真实 AppID preview 573065 bytes；0/1/8/9 图近似 fixture 已生成，原生三视口与 iOS/Android 连续拍摄仍为 NOT_RUN；未上传、未部署
