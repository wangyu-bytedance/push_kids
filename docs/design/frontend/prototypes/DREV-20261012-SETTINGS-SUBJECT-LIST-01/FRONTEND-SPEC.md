# 设置页在学科目统一列表

- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-01
- Status: AWAITING_APPROVAL
- Task Spec: SPEC-20261012-SETTINGS-SUBJECT-LIST-01
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02

沿用纸芽暖白纸面、松绿线图标、16px行标题、14px状态文字和轻分隔线；科目区使用与活动、出行相同的单列结构。

1. 数学、语文、英语仍固定展示，改为图标、科目名称、在学/未加入状态、右侧加入/移出文字操作。
2. 其他已添加科目沿用相同行结构，自定义标记移到次级文字。只有现有 canRemove 为真时展示移出，不扩大删除权限。
3. 加入/移出具有至少44px有效点击区；待处理中阻止重复提交，成功刷新，失败保留状态并展示现有错误反馈。
4. 只读成员显示科目状态，隐藏写操作和添加入口。不用箭头暗示科目可进入不存在的详情页。
5. 添加其他科目继续使用现有目录半屏。课外活动、出行的页面布局和编辑行为沿用现状。
6. 长名称换行；文字列可收缩，操作列固定且不与标题重叠。基本科目排序、数据和API不变。

## 精确视口与状态

320×568、390×844、430×932，每档导出 content、unselected、readonly、pending、long-name、error。使用合成数据；首屏外内容通过纵向滚动访问。
loading、无学习档案、目录空/错误状态沿用原实现，实施时回归。

SVG与PNG由render.py生成，SHA-256见对应snapshots/UI-001目录APPROVAL.md。
候选图不代表原生验收。落地需三档原生节点矩形、长文/待处理/只读状态截图和iOS/Android检查。
