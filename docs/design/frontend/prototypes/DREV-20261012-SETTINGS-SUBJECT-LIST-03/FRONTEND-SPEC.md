# 设置卡片复用今日顶部Hero表面

- Design Revision: DREV-20261012-SETTINGS-SUBJECT-LIST-03
- Task Spec: SPEC-20261012-SETTINGS-SUBJECT-LIST-03
- Status: AWAITING_APPROVAL
- Baseline: FDB-20260913-04
- Engineering: FEC-20261007-NATIVE-GEOMETRY-02
- Supersedes candidate: DREV-20261012-SETTINGS-SUBJECT-LIST-02

用户指向其他界面最上面的card。已核对今日pages/today/index.wxml的pk-hero及styles/atoms.wxss:64-70，并查看dist/ui-preview/today-390-nav-vp.png。权威来源是现有Hero表面：

```css
background: radial-gradient(120% 130% at 100% 0%, rgba(127, 166, 92, .16), rgba(127, 166, 92, 0) 58%), linear-gradient(158deg, #FFFEFA 0%, #F7F4EA 100%);
```

三类卡片统一采用暖白纸面、右上角嫩芽径向晕光、淡绿色右下年轮弧线、既有边框和轻阴影；不是全卡绿色线性渐变。沿用Hero的40rpx圆角。科目单列结构已被用户认可，继续保留；图标底座与加入/移出回到既有平面色，避免额外渐变。

生产实施复用既有Hero样式，仅保留设置页面的列表几何，不新建渐变token、组件或依赖。伪元素置于内容后，不遮挡操作。三个区域的文字、添加、权限、API和活动/出行编辑保持现有合同。

320×568、390×844、430×932 × content/unselected/readonly/pending/long-name/error，共18组SVG/PNG。候选SVG近似表现现有CSS渐变，精确原生效果仍须节点几何、截图和iOS/Android验收。候选图使用合成数据。
