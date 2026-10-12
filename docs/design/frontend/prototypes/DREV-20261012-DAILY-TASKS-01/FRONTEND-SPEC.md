# 每日任务增量设计合同

- Design Revision: DREV-20261012-DAILY-TASKS-01
- Task Spec: SPEC-20261012-DAILY-TASKS-01
- Status: APPROVED（产品负责人2026-10-12消息「好的按照这个方案实现前后端代码。」）
- Baseline / engineering: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02

复用纸·芽色彩、中文字体、卡片、原生导航及安全区，不改变既有 Hero 和其他设置卡片。
设置提供阅读、跳绳、练字、户外运动的快捷添加、自定义、目标分钟、编辑/删除及取消。
今日复习安排下方展示每日任务；未完成在前，完成文字及撤销在后；空/全部完成默认收起。
手动展开空态提供设置入口。学习记录非空展开；其他区块依据未完成计数。

可编辑源 design.html；三视口320×568、390×844、430×932的五状态PNG及SHA-256见APPROVAL.md。
settings与form-error为长页，可滚动到表单与错误提示。iOS/Android键盘调整、只读、pending、失败保留输入、长名称、跨孩子晚响应遵循Task Spec。
HTML设计导出不是原生验收；原生节点矩形、文字放大、真机、弱网证据在实施记录中独立报告。
