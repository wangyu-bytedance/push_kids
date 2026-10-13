# 记录 / 日程插画方案

- Design Revision: DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01
- Task Spec: SPEC-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01
- Status: APPROVED
- Approved by: 用户
- Approved at: 2026-10-13
- Evidence: 本会话两张效果图后用户“好的 按照这个方案进行落地”
- Baseline / FEC: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02

Operate页面，暖白纸面、松绿正文强调、纸艺插画、柔和阴影，动作保持简洁。记录页头书本嫩芽、空照片区相机照片；日程页头台历时钟。插画独立留白，不能铺在日期、时间线、文本输入或操作后。
保留原品牌导航、标题、孩子选择、语音入口、待处理提示、上传/提交/只读状态、七天选择与日程动作。AI生成概念稿中的额外宣传文案与日期/导航错误不成为产品合同。

页头复用pk-hero样式；内布局左文案/孩子选择、右透明插画。320档图像缩到约90px宽，390/430约120/130px；标题允许换行，孩子名称截断且点击可访问原完整选择流程。上传区插画约140px宽，下方标题和说明，已选照片恢复原网格。

images为装饰（aria-hidden），加载失败隐藏；上传图失败显示原相机线图标。页面仅保存装饰失败bool，不记录儿童内容、不发新请求。
生产图片为本地PNG，3张总共173638 bytes；原始生成文件不进包。主包预算1.5MiB，新增图预算200KiB。

## Repository evidence

批准概念图位于concept-records.png、concept-calendar.png；editable源为三档状态SVG，render.py可以重新生成批准前导出；APPROVAL.md记录SHA-256。原生审核后批准清单不可更改。
records：empty/photos/readonly/error；calendar：content/empty/error/long-name；320×568、390×844、430×932，共24组。

## Asset generation

Built-in image_gen：从批准记录概念图提取相机/照片/铅笔/叶枝，透明背景，保持纸艺质感、色彩、形状，去除UI、文字；从日程概念图提取台历/时钟/叠书/叶枝，台历留白、透明背景，保持原造型。record-books复用上一候选已生成书本嫩芽。全部通过sips缩到最大320px（书本220px），保留alpha。
