# 设置页柔和渐变列表

- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-02
- Status: AWAITING_APPROVAL
- Task Spec: SPEC-20261012-SETTINGS-SUBJECT-LIST-02
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02
- Supersedes candidate: DREV-20261012-SETTINGS-SUBJECT-LIST-01

用户2026-10-12认可单列方式，并要求增加美观的渐变色。三类卡片使用相同的低饱和薄荷绿到暖白渐变（#EDF5EC → #F9FBF2 → #FFFDF8），图标底座用嫩绿渐变（#D3E7D8 → #ECF0D8），“加入”操作用松绿渐变（#38826A → #1F5B45）搭配暖白文字。深墨标题与轻分隔线保留；移出保持次级文字操作。渐变不承担状态含义，无动效。

基础三科仍固定展示，显示在学/未加入及加入/移出；其他科目仅现有canRemove允许时提供移出。只读无写入口，忙状态防重复提交，失败保留数据，目录与确认行为不变。长名称换行，操作列固定，至少44px触控。

## 三档视口与状态

320×568、390×844、430×932 × content/unselected/readonly/pending/long-name/error，共18张SVG与PNG。合成数据，页面纵向滚动。加载和无档案沿用当前实现并回归。

生产落地时渐变语义值统一写入tokens.wxss，页面只引用，不新增依赖或共享组件。活动与出行仅同步卡片/图标底色，不改变其内容、几何及交互；此点纳入Spec02。
清单位于snapshots/UI-001/DREV-20261012-SETTINGS-SUBJECT-LIST-02/APPROVAL.md。设计导出不代替三档原生节点矩形及iOS/Android检查。
