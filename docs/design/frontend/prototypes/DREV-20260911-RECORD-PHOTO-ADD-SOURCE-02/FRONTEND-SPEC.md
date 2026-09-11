# DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02 — 照片统一追加入口

- Status: APPROVED
- Related Spec: `SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02`
- Affected UI: `UI-001 / pages/records/index`
- Baseline: `FDB-20260906-03`（PKDS-2.0「纸 · 芽」）
- Engineering contract: `FEC-20260906-04`
- Figma anchor under existing FEAT-001 waiver: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1

## Interaction direction

这是 Operate 型表单。视觉方向保持“暖纸底、松绿主操作、低装饰”，采用微信用户熟悉的单一添加入口和
原生媒体来源选择；不新增自定义弹层，不改变页面其余信息层级。

## Layout and states

### 0 张

```text
学习照片                                      0 / 9
┌──────────────────────────────────────────┐
│                  [相机图标]              │
│                添加学习照片              │
│             拍摄或从相册选择             │
└──────────────────────────────────────────┘
```

点击整块入口 → 微信原生来源选择（拍摄 / 相册）。

### 1–8 张

```text
┌──────────┐ ┌──────────┐ ┌──────────┐
│  照片 1  │ │  照片 2  │ │    +     │  ← 同一 addPhotos
└──────────┘ └──────────┘ └──────────┘
```

每次返回后“+”继续存在；再次点击仍可重新选择拍摄或相册。相册可一次多选，拍摄一次返回后可以继续拍。

### 9 张

“+”隐藏；标题计数显示 `9 / 9`。删除任一照片后“+”恢复。

## Copy and accessibility

- 主标签：`添加学习照片`
- 辅助文案：`拍摄或从相册选择`
- 空态 accessible name：`添加学习照片，可拍摄或从相册选择`
- 网格“+” accessible name：`继续添加照片，可拍摄或从相册选择`
- 每个入口触控目标 ≥44px；不能仅靠“+”符号表达含义。
- 取消或权限失败不清空学习内容；上传中不允许再次选择。

## Responsive matrix

| Viewport/state | Requirement |
|---|---|
| 320×568 / 0、1、8、9 图 | 入口、缩略图和删除键不横向溢出；固定 CTA 与历史入口仍可达 |
| 390×844 / 0、1、8、9 图 | 作为主视觉对照；添加入口居中，网格间距沿用现有 token |
| 430×932 / 0、1、8、9 图 | 内容最大宽度不变，不拉伸为桌面布局 |
| representative iOS/Android | 拍摄→返回→再次拍摄、相册多选、取消、权限失败 |

## Approval boundary

产品负责人已于 2026-09-11 回复“对 按照这个方案落地”，明确批准
`SPEC-20260911-RECORD-PHOTO-ADD-SOURCE-02` 与 `DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02`。
该修订不改变照片上传/AI/确认/历史/后端合同；
若平台无法稳定提供原生来源选择，才回到新的 Spec 评审自定义 ActionSheet，不在实现中临时扩张。

批准快照：`docs/design/frontend/snapshots/UI-001/DREV-20260911-RECORD-PHOTO-ADD-SOURCE-02/APPROVAL.md`。

## Local implementation evidence

- 空态与后续“+”已统一调用 `addPhotos`，通过 `wx.chooseMedia` 同时开放 `camera` / `album`。
- 自动化覆盖连续两轮单张返回、相册多选、9 张上限、删除后恢复、取消/空返回/失败和上传中保护；
  全量前端 `135 passed`，ESLint、小程序静态与架构校验通过。
- 已生成 0/1/8/9 图 × 320/390/430 的近似预览 fixture；真实微信来源面板、三视口原生几何、
  连续拍摄与 iOS/Android 权限路径仍为 `NOT_RUN`，故本设计保持 `APPROVED`，不声明完成原生验收。
- 真实 AppID 本地 preview 编译 `573065` bytes；未上传、未部署。
