# DREV-20260919-TODAY-SOURCE-MATERIAL-01 — Today 原始学习内容弹层

- Status: `APPROVED`
- Surface: `UI-001 / Today / TodoCard / source material sheet`
- Related Task Spec: `BUG-SPEC-20260919-REVIEW-SOURCE-01`
- Baseline: `FDB-20260913-04 / PKDS-2.0 纸 · 芽`
- Engineering contract: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Editable source: `today-source-material.html`
- Required exports: `photo + text @ 320×568 / 390×844 / 430×932`
- External design dependency: `none`

## 一句话方向

把 Today 从“解释为什么出现”改成“让家长立即想起原来学了什么”：卡片只保留具体知识、原题提示和原始内容入口，照片或原文在当前页的温和底部弹层中核对。

## 1. 信息层级

TodoCard 从上到下为：

1. 科目、复习方式、数量/分钟与建议状态；
2. 每个知识点的名称；
3. 最多两行、可空的 `原题提示：{source_summary}`；
4. 仅在 `source_submission_id` 存在时显示的 `查看原始内容`；
5. 该知识点自己的 `完成` 与更多反馈。

删除 `出现原因` 信息块和 group-level `带练提示` footer。来源日期、轮次和间隔仍是服务端兼容事实，不在本 revision 展示。

## 2. 卡片交互

- 每个知识点独立拥有来源入口；同一卡片包含多个知识点时，不允许用第一项来源代表整组。
- `完成` 可见胶囊高64rpx，文字14px；用包装层/伪元素维持至少88rpx触控热区。
- 更多反馈仍在卡内展开，文案和确定性排期后果不变。
- `source_summary` 最多两行；超长自然截断但完整内容仍可在原始材料中核对。
- 无摘要但有 source 时只显示入口；无 source 时不显示入口，也不显示不可用占位。
- `查看原始内容` 使用图片/文档线性图标和文字，不只依赖颜色表达可点。

## 3. 底部弹层

- 使用现有 `.pk-mask + .pk-sheet`，不使用 `wx.showModal`，不新增路由。
- 标题：`原始学习内容`；副标题显示来源学习日期，材料数量由复用组件加载后显示。
- 右上角关闭；点击蒙层、关闭按钮、切孩子、页面 hide 均关闭并清理内容。
- Photo：稳定 `sort_order` 缩略图；evidence image index 对应图显示 `相关图片`；点击调用微信原生全屏预览。
- Text：显示 `家长当时填写` 和可选择原文。
- Mixed：照片在前、原文在后；正文区域纵向滚动。
- 弹层内可再次显示该知识点的 `原题提示`，帮助在多图中定位；不生成答案或教学步骤。
- 隐私说明：`照片仅用于核对原始学习内容。`

## 4. 状态矩阵

| State | Display | Recovery |
|---|---|---|
| loading | 与照片/文字结构接近的骨架 | 无写操作，可关闭 |
| photo | 缩略图、相关图片标记、原题提示 | 点击全屏查看 |
| text | 家长原文、原题提示 | 原文可选择 |
| mixed | 照片、分隔、原文、提示 | 同上 |
| empty | `没有可展示的原始材料` | 关闭；Todo 仍可反馈 |
| retryable error | 页内错误条 + `重新读取` | 原地重试，保留弹层 |
| gone | 单图标记 `原图已删除或不可用` | 其他图/文字/摘要继续可读 |
| unauthorized/not-found | 清空受保护内容，显示安全错误后关闭或允许用户关闭 | 不保留上一条材料 |
| no source | 卡片不渲染入口 | N/A |

## 5. Photo candidate

卡片示例：

- Name: `根据年龄关系列加减混合算式`
- Source summary: `培优算中的年龄题，根据人物年龄差求妈妈的年龄。`
- Entry: `查看原始内容`
- Sheet: 9月7日记录、两张练习册照片、照片1为相关图片。

设计源中的题面为无身份的占位材料，只表达布局，不是生产儿童材料或测试 fixture。

## 6. Text candidate

卡片与 Photo 相同信息层级；弹层正文改为：

`今天练习了根据年龄差列加减混合算式，重点是先分清谁比谁大、相差几岁。`

它只展示“家长当时填写”，不代表模型新生成的 review。

## 7. 响应式与无障碍

- 320×568、390×844、430×932；普通页面不横向滚动。
- 320 宽允许知识名称和摘要换行；操作区不得挤出卡片。
- 弹层最高85vh，正文独立纵向滚动；底部安全区不遮挡内容。
- 触控热区至少44px；关闭、重试、缩略图、来源入口均有明确 accessible name。
- 状态使用文字、图标、位置共同表达；`相关图片` 不只靠绿色描边。
- 不新增装饰动画；沿用现有120–220ms disclosure 与 reduced-motion 规则。
- 中文正文至少14px；非关键 metadata 可使用12–13px。

## 8. 数据映射

```text
review item.knowledge_name -> 知识点标题
review item.source_summary -> 原题提示（可空）
review item.source_image_index -> 相关图片标记（可空）
review item.source_submission_id -> 是否展示入口 + 弹层读取目标
review item.source_occurred_on -> 弹层来源日期

GET history/{submission_id}.media -> 缩略图/全屏预览
GET history/{submission_id}.input_text -> 家长原文
```

字段缺失按旧服务端兼容处理，不在客户端猜测或拼造摘要。

## 9. 不采用

| Alternative | Reason |
|---|---|
| 新 AI review / practice generation | 成本与实现面过重，且不属于“回看原材料” |
| history 页面跳转 | 打断 Today 上下文且需要重新定位 |
| group-level 查看入口 | 多知识点可能来自不同 submission，来源不明确 |
| 系统 modal | 不能承载图片、长文字和恢复状态 |
| Today 首屏预下载图片 | 隐私与性能不必要；必须点击后加载 |
| 缩小真实点击区 | 违反小程序触控基线；只缩小可见胶囊 |

## 10. 实现与验证门禁

实现前需明确批准：

`BUG-SPEC-20260919-REVIEW-SOURCE-01 + DREV-20260919-TODAY-SOURCE-MATERIAL-01`

批准对象是本目录自包含 HTML、approval manifest 中六张精确视口/状态候选图及 SHA-256。仓库预览不替代实现后的原生节点几何、字体放大、iOS/Android、真实私有预览与发布人工门禁。
