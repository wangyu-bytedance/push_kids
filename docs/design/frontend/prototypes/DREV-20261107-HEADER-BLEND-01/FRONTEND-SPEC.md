# DREV-20261107-HEADER-BLEND-01 — 六主题页头统一

- Status: AWAITING_APPROVAL
- Task: [DESIGN-004-SPEC-01](../../../../../specs/completed/DESIGN-004-HEADER-BLEND.md)
- Baseline: `FDB-20261107-05` / `FEC-20261107-AGENT-DEVICE-MATRIX-03`
- Editable preview: [index.html](index.html)。`source.html` 为易编辑模板，`render.py` 从现有主题 registry 和本地资源生成自包含 HTML 与验证截图。
- Matrix: 390×844、430×932，六主题，18 个宿主/状态，216 张导出。

页头与页面用同一底色，取消页头外框，插画按自然比例覆盖页头的可用宽度。左右短渐变、上缘短渐变和底部较长渐变都用当前画布色。五个主页面的标题叠在插画上，使用主题页头前景色。详情、表单等子页的标题在素底上自然换行，插画接在标题下方。缺图也使用页面语义前景色。原始风格为素底，保留报表、日程等原有局部小插画。文案、孩子选择及记录菜单保持原有位置关系，菜单作为前景显示。

今日和报表是首次打开的对照，下面是当前形态的近似参考。页面和视口选择可查看独立场景，`?single&theme=garden&scene=reports&width=390` 可打开单屏。合成内容用于说明布局。HTML 导出供设计批准，原生图片层、节点、菜单动作和设备单独验收。
