# DREV-20261006-SOURCE-DELETE-01

- Status: APPROVED
- Approval evidence: 产品负责人（用户），2026-10-06，本会话“落地这两个spec”，批准当前Task Spec与配套设计
- Surface: UI-001 / Today / TodoCard / submission-materials
- Related Task Spec: SPEC-20261006-SOURCE-DELETE-02
- Baseline: FDB-20260913-04 / PKDS-2.0 纸·芽
- Engineering contract: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01
- Editable source: index.html
- Required exports: menu/photo/confirm/unknown × 320×568、390×844、430×932
- External design dependency: none

Operate场景：家长快速核对当前知识点原图，并明确地移除误记知识。沿用暖白纸面、松绿、原有卡内展开菜单，删除为菜单末尾的独立操作。

## 可见合同

1. 更多菜单顺序：需要加强、只做了一部分、今天先跳过、删除记录、收起。删除与反馈用分隔线区别，次级文字“删除这个知识点及其复习安排”。点击不直接发送请求。
2. 独立确认弹层标题“删除这个知识点？”，显示知识名称，正文“将删除这个知识点的学习关联、复习安排和反馈。原始照片、原记录总结及同次上传的其他知识点会保留。此操作无法撤销。”底部“取消 / 确认删除”。最终删除使用既有danger语义色。所有操作>=44px，窄屏正文纵向滚动。
3. 成功后关闭确认层、刷新服务端列表和计数，轻提示“已删除”；失败保留卡片、弹层内错误和重试；pending显示“删除中…”，防重复。viewer无删除入口。切孩子/离页关闭并隔离迟到UI回调。
4. 原始学习内容弹层只显示目标照片；示例为第2张，标签“照片 2 · 对应照片”，不能重编号为1。照片模式不显示整次上传原文，保留当前知识点原题提示。点击仅预览该图。
5. 无可靠图索引显示“未关联具体照片”，说明“这条记录没有可靠的照片关联，可前往记录详情查看原始材料。”本次不新增自动跳转；家长可按原导航查看历史。纯文字仍可核对原文。失效图显示“原图已删除或不可用”；网络失败有重新读取；权限失效立即清空。
6. 原始材料加载保持骨架、generation隔离、按需鉴权、临时文件清理；同一submission下index变化必须重新选择。照片页loading/错误不得露出上一张内容。

## 设计范围与验证

设计源中练习题为合成排版占位，非儿童原图。菜单、单图、确认、索引未知为必备导出状态；loading/error/pending/success/viewer/text/410由上述状态合同与实现测试覆盖。无新路由、无AI生成、无图片裁剪。照片设计采用完整可读区域，原生解码比例允许自然变化。

沿用批准token；普通正文14px，metadata13px；关闭/菜单/来源入口/确认按钮触控44px以上；宽度收缩、长中文换行、弹层最高85vh且内部滚动。禁止用隐藏横向溢出替代几何证据。HTML导出仅供设计审批；原生三视口、iOS/Android、大字和真实鉴权须在实现后验证。

批准对象：SPEC-20261006-SOURCE-DELETE-02 + DREV-20261006-SOURCE-DELETE-01；hash见配套APPROVAL.md。本次只补充Spec的来源数据合同和验收点，可见设计、HTML及导出不变。获批前不得修改生产实现。
