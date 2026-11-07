# DREV-20261106-UI-CONSISTENCY-09 — 视觉减法

- Status: AWAITING_APPROVAL
- Task: [DESIGN-003-SPEC-01](../../../../../specs/active/DESIGN-003-THEME-VISUAL-REFINEMENT.md)
- Architecture: 保持`ARCH-20261106-MINIAPP-THEMES-01`
- Baseline: `FDB-20260913-04` / `FEC-20261007-NATIVE-GEOMETRY-02`
- Authority: 用户本轮四项反馈；六主题ID、DREV06视觉个性、DREV08设置底部入口保持。
- Editable source: source.html；build.py读取当前registry/glyph/资产，生成自包含index.html。全部文件仅供设计，不写生产源。
- Exact matrix: 320×568、390×844、430×932；六主题；reports、records、settings、nested、loading、empty、error、disabled、sheet共162导出。数据为合成示例，不是新业务要求。

固定报表标题完整单行，字号24px。记录横幅归整个页头，以自然780:304比例完整显示，菜单锚点不承担图片宽度。五新主题上传装饰用既有camera及主题色几何图形，原始相机插画保留。卡片靠surface/canvas与留白分组，嵌套反馈仅浅底，保留字段、选中/焦点、错误、上传入口与图表的有效边界。

预览选择器可切换主题和场景；卡片内业务按钮仅作布局表达，实际行为沿用当前小程序，未在HTML复制业务控制器。浏览器渲染不能证明原生widthFix、菜单层级、触区/读屏/设备兼容，最终以Spec验收点执行。
