# UI-015 — 归档操作精简候选

- Status: AWAITING_APPROVAL
- Task: [BUG-033 / Spec01](../../../../../specs/active/BUG-033-CHILD-ARCHIVE-UI.md)
- Design Revision: `DREV-20261024-CHILD-ARCHIVE-01`
- Baseline/FEC: `FDB-20260913-04` / `FEC-20261007-NATIVE-GEOMETRY-02`，沿用已批准版本。
- Source: [index.html](index.html)，自包含，无远程资源、业务调用或真实儿童数据。
- Manifest: [APPROVAL.md](../../snapshots/UI-015/DREV-20261024-CHILD-ARCHIVE-01/APPROVAL.md)。

## Visual and interaction direction

操作型表单，沿用纸色卡片与松绿主操作；归档区收为左对齐的整行操作，去除泛标题、重复说明、垃圾桶及常驻红色强调。行内标题17px，辅助文案14px，整行可点且≥44px，右箭头表示将进入确认步骤。保留原表单与保存操作层级；HTML中前三项只是只读上下文，不是字段重设计。

| State | Exact visible content / behavior |
|---|---|
| active | 标题“归档档案”；副文案“保留全部记录，随时可恢复”；右箭头，整行打开原生确认框 |
| unfinished | 同上，追加一条左对齐提醒“还有 N 条记录待处理，归档后仍可继续完成。”；数量口径不变，未知时不展示 |
| archived | 同一操作行“恢复档案”＋“重新加入孩子列表，继续记录”；调用原恢复操作 |
| working | “正在归档…”（恢复为“正在恢复…”），禁用重复点击，不显示箭头 |
| error | 保留表单和操作，服务端错误仍走既有页内错误区，可重试；示例文案不替换服务端错误协议 |
| confirm | 原生wx.showModal：标题沿用孩子名；正文“归档后从孩子列表隐藏，不能新增记录。历史记录和报表保留，随时可恢复。”；取消/归档 |
| confirm-unfinished | 上述确认正文追加“还有 N 条记录待处理，归档后仍可完成确认和复习反馈。”；提醒不阻断归档 |

归档态既有顶部说明、manager权限、未完成数量读取及归档/恢复接口、全家切换回落、年级确认均保持现有业务语义。普通说明只在操作行给一句；详细影响在动作确认处出现。归档不是删除，不使用删除图标。

## Exact viewport and engineering matrix

- 320×568、390×844、430×932 logical px，Chrome HTML候选DPR1 / font100%；7态×3视口=21张导出。
- 页面左右边距与卡片圆角、边框、阴影沿用现有tokens；局部样式不修改全局atoms。正文≥14px，标题17px，所有触控≥44px；文本可自然换行，不截断、隐藏溢出或固定说明高度。
- 原生实施后同三视口复验行/提醒/错误/进行中及确认框可读性；原生字体放大、读屏标签/焦点、iOS/Android验收按FEC记录。
- 没有新组件、请求、持久状态、日志、依赖、图片或动画；FEC-PERF-READ-001..004保持既有有界读取，不用新计数请求。
- 权限与安全由原服务端控制；CSS只改变呈现，不能授予viewer/editor归档权。
- HTML确认框仅示意文案与层级，实际wx.showModal由平台渲染，HTML键盘检查不能替代微信读屏/焦点。

## Approval and scope

需批准 `BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01 + DREV-20261024-CHILD-ARCHIVE-01`；当前不改生产页面。批准年级设计的源及57导出保持原字节，新候选仅在批准后替代档案状态卡的局部视觉。无架构边界或数据协议变更。
