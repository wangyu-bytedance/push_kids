# 设置列表采用用户指定Hero参考效果

- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-04
- Task Spec: SPEC-20261012-SETTINGS-SUBJECT-LIST-04
- Status: AWAITING_APPROVAL
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02
- Supersedes candidate: DREV-20261012-SETTINGS-SUBJECT-LIST-03
- User reference: 2026-10-12用户附图“陪伴，从一条记录开始 / 记下今天学到的”顶部卡片（合成设计不包含儿童信息）。

以用户截图及现有pk-hero为样式权威：暖白纸面、右上角宽范围嫩绿径向晕光、细边、柔和下投影、右下年轮弧线。修订03候选未表现阴影且圆角误写40rpx，本版纠正为现有--pk-r-2xl即52rpx（设计验收矩阵准许此既有Hero token）。

复用styles/atoms.wxss的pk-hero背景、伪元素和现有--pk-e2阴影，不创造新颜色或组件。三类设置采用相同表面；单列科目、现有状态、权限、加入/移出/添加行为保留。图标保持平面底色，行标题可读，不复制参考图的教程内容或按钮结构。卡片保持列表布局，弧线在文字和控件后方且不影响点击。

320×568、390×844、430×932各导出content/unselected/readonly/pending/long-name/error，18组SVG/PNG。SVG阴影为现有原生CSS的视觉近似；三档原生矩形、视觉和iOS/Android仍须实测。图标为示意，生产保留已有活动图标映射。
