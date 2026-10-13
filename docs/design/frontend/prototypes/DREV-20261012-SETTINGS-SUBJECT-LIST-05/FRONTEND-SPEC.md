# 设置卡片插画版

- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-05
- Task Spec: SPEC-20261012-SETTINGS-SUBJECT-LIST-05
- Status: AWAITING_APPROVAL
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02
- Supersedes candidate: DREV-20261012-SETTINGS-SUBJECT-LIST-04

用户要求增加图像。保留已认可的单列及Hero纸面，用三张同风格的小插画丰富每块标题区域：书本/铅笔/嫩芽、运动球/羽毛球/毛巾、书包/路线。统一低饱和松绿、暖白、少量赭黄的纸艺质感，透明背景，不含人物、文字或儿童照片。

每张插画位于标题右侧82×70px区域，标题保留左侧空间，列表从下方独立开始，不把图像铺在正文和控件后面。插画仅装饰，无点击，无状态含义；无图或加载失败不影响标题和操作。保留现有线图标及全部权限、加入/移出、目录和安排行为。

资源使用内置image_gen生成，prompt见PROMPTS.md，工作区素材位于本目录assets。实施时离线缩小压缩至适合小程序的尺寸，三张新增图片总预算≤120KiB，初始包仍≤1.5MiB，禁止远程依赖或base64进入页面data。SVG候选图引用同目录资源；原生使用本地image并标为装饰。

三档320×568、390×844、430×932，各content/unselected/readonly/pending/long-name/error，共18组候选图。SVG/PNG不代替原生几何、无图恢复、包预算或iOS/Android验收。
