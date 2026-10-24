# 足迹界面减法

- Status: APPROVED / LOCAL_IMPLEMENTATION / VERIFYING
- Approval: 产品负责人（用户），2026-10-24，“批准 Spec01 + DREV01，按此实施并合并 UI 规范”（call_3e246df48da4467983d023b06a443aeb）。
- Design Revision: DREV-20261024-FOOTPRINTS-MINIMAL-01
- Task: [SPEC-20261024-FOOTPRINTS-MINIMAL-UI-01](../../../../../specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md)。
- UI IDs: UI-001、UI-018；owner 产品负责人（用户）。
- Baselines: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，均已批准；工程文案附加条款随本次 Spec01 / DREV01 获批。
- Source: [index.html](index.html)，自包含、合成数据、无网络/业务写入。
- Manifest: [24张三视口候选及SHA](../../snapshots/UI-018/DREV-20261024-FOOTPRINTS-MINIMAL-01/APPROVAL.md)。
- Approved engineering rules addendum: [UI-COPY-REQUIREMENTS.md](UI-COPY-REQUIREMENTS.md)，已合并。

Operate 型界面，沿用纸面/松绿、既有字号与线性图标；用照片、真实统计和动作承载内容，减少重复文字，不新增插画、装饰或教程。

## 改动

1. 删除重复的“孩子的足迹”标题。
2. 两行次要入口改为统计右侧44px更多按钮。原生操作菜单保留可用功能，空归档时不出现该项，viewer 不提供设置。仅一项直接执行，没有操作则隐藏。
3. 选择已归档孩子后，使用原生归档选择列表；取消保持原孩子，仍通过现有离开保护。
4. 设置仅保留“AI 地点候选”开关、关闭和保存。正文按内容收高，删除供应商及存储/清理流程解释。

日期筛选删除、顶部类型/孩子控件、三视图、原下方48px导入按钮均延续既有批准；原上传授权流程不在本次重画范围。示例中的“8 个地点”等是设计合成数据；没有业务数据写入。

## 视口与状态

320×568、390×844、430×932；各 overview / empty / actions / settings / archived / viewer / long / standalone，1x，共24张。设置和原生操作单显示时关闭底部交互；其余状态保留原导航。更多/关闭至少44px，设置行/动作行至少48px，主按钮48px，文字至少14px。

HTML 的原生操作菜单模拟只表达目标可见效果；不能代替微信原生弹出、图层、取消/选择、读屏、真机和节点验收。standalone 仅验证保留原深链接和其孩子选择器；不新增第二套业务实现。

## 交互和验证

更多 → 原生操作菜单 → 足迹设置 / 归档选择；点击外部或取消关闭。设置保存后回原视图，开关值保留；归档选择更新孩子并显示归档标签，隐藏导入。HTML Escape 关闭当前层并将焦点还给触发器；页面 Tab 导航不穿透打开的模态层。

候选导出命令：`python3 docs/design/frontend/prototypes/DREV-20261024-FOOTPRINTS-MINIMAL-01/render.py`。结果记录于 `render-audit.json`，执行后如实填写，不引用旧设计/原生结果。

- Candidate render / interactions: PASS，24张三视口导出、三个视口的设置开关/保存、焦点恢复/循环、取消不切换、归档选择及viewer入口检查；无页面JS错误或业务网络请求。见[render-audit.json](render-audit.json)。已目视390×844主界面和320×568紧凑设置，后者不再保留原52vh空正文。
- Candidate SHA / lint / references: 见[本轮设计证据](../../../../quality/evidence/FOOTPRINTS-MINIMAL-DESIGN-20261024.md)；仅记录实际运行结果。
- Current production implementation: 已获批并在原模板/控制器/样式实施，最终331项前端及lint/结构/设计检查通过；三尺寸27态原生及430实际菜单取消/设置/归档选择通过，文案条款已合并。
- Native / devices / review: 以[当前实施证据](../../../../quality/evidence/footprints-minimal-20261024/README.md)为准，不能用HTML验收替代。
- Approved sources changed: none；旧 DREV 与批准截图保持不可变。
