# DREV08 — 底部设置列表入口修订

用户对顶部“界面风格”入口批注“这个放在最下面的设置里”。本轮仅修订评审设计、实施Spec和索引；没有生产代码修改。

## 实际变化

- 顶部独立卡片移除；风格入口进入业务卡片之后的页尾设置列表，位于“提醒设置”和“关于知芽”之间。
- 采用同组图标、标题/副标题、分隔线和箭头，当前主题名称保持可见。
- 六主题选项、选择/应用/取消和保存失败提示保持；失败提示随入口移到页尾。
- 增加现有家庭/删除/提醒/关于入口作为位置上下文，均来自现有原生设置页；不是新增这些设置功能。
- `section=settings`仅是评审定位参数，初次打开滚至页尾；生产设计不增加自动跳底行为。

## 验证

| 检查 | 结果 | 实际范围 |
|---|---|---|
| HTML build | PASS | self-contained index.html；既有插画，未生成新图片 |
| 六主题×三视口×三状态 | PASS / 54 | 横向几何、44px按钮、面板顶界、入口不被底部导航覆盖 |
| 局部交互 | PASS / 15 | 六主题应用/取消、未知ID回退、Escape与焦点返回、面板焦点 |
| PNG导出 | 56 | 54状态+六主题总览+915×904批注视口 |
| console / external HTTP | PASS / 0 / 0 | HTML预览环境 |
| 目视 | PASS（设计范围） | 390原始底部列表、320深色选择面板；其余见导出/总览 |
| apps源码 | PASS / 355 unchanged | 与DREV06及本轮baseline比对，不含字节码缓存 |
| 原生与设备、持久化、生产包体增量 | NOT_RUN | 本轮没有生产UI代码修改 |
| 生产测试、API/DB、发布 | NOT_RUN / N/A | 本轮仅设计位置修改 |

收尾实际检查全部PASS：

- DREV08专项`ruff check`、`ruff format --check`、`git diff --check`。
- `validate_design_evidence.py --check-current-policy`返回DESIGN_EVIDENCE_VALID；不代替原生验收。
- `uv run python .../finalize.py`验证旧DREV01–07的134/135/22/11/11/1005/67条SHA，全部不变。
- 当前12个源、56张PNG的SHA/尺寸、证据摘要、11条本地文档链接及Spec07逐字归档副本验证通过。

## 文档闭环与批准边界

- Spec07逐字保存到`specs/evidence/DESIGN-002-SPEC-07.md`；当前Spec08沿用Architecture01并修订底部位置、调用图、验收点、源SHA和证据引用。
- STATUS索引同步Spec08/DREV08；旧DREV01–07不重写。AGENTS六主题约束保持，没有本轮政策diff。
- Feature、Behavior、Architecture、UI current-state、FDB/FEC及发布正文仍对应原始生产代码；未将设计修改写成已落地。
- 当前Spec为`READY_FOR_REVIEW / specs/active/`，具体原生主题实施尚未批准或开始。设计入口位置无需再次澄清；不能将本轮位置批注追认为Architecture01实施批准。
- 没有生产diff导致的代码/当前文档冲突，无云交付，不设DONE。

浏览器同步限制：尝试绑定当前file://评审页以切换到新版时，被Browser Use URL policy阻止；现有浏览器页未改变。未绕过限制，提供新版本地预览链接及已导出的PNG供review。
