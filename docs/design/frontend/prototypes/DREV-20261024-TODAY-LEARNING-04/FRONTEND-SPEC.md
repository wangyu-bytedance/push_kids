# DREV-20261024-TODAY-LEARNING-04 — 学习建议标题约束

- Status: APPROVED
- Date: 2026-10-24
- Task Spec: [SPEC-20261024-SUGGESTION-TITLE-LIMIT-01](../../../../../specs/active/FEAT-004-SUGGESTION-TITLE-LIMIT.md)，APPROVED，含Architecture01。
- FDB / FEC: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，均APPROVED，沿用文案减法附加条款。
- UI / Feature: UI-001 / FEAT-004；[当前UI](../../ui/UI-001-parent-miniapp.md)。
- Source: [self-contained HTML](index.html)；[SHA清单](../../snapshots/UI-001/DREV-20261024-TODAY-LEARNING-04/APPROVAL.md)。
- Approval: 用户，2026-10-24，call_39aaa3dd3cdf4a52b2bfc9c4d862ee58「批准，按此实现」。HTML/33张PNG及SHA自此冻结；批准时尚未修改生产组件/provider/API，实施和验证另记。

Operate方向：延续DREV02的暖白纸面、松绿操作及20px标题，DREV03的今日页字阶与卡片；把内容预算放在生成/编辑入口，不以缩小标题字体或省略正文解决问题。

新生成/重新编辑标题trim后1–20个Unicode码点，详细步骤使用已有具体内容字段；标题不含内部换行。示例「用积木表示两组数相加」；20字边界「用积木表示加法并说说两组数量合起来的变化」。正常字体下三视口均最多两行；这是本矩阵的几何断言，系统大字体需独立原生验证，不承诺固定两行裁切。

编辑表单仅增加：学习标题右侧14px的`当前字数/20`，字段无效时的短错误及输入边框。超限「标题最多20字，请精简。」、空值「请填写学习标题。」、内部换行「标题请写成一行。」。无效保存定位字段、零请求、保留原输入；不在20字处自动裁剪。原input120防护上限保留，实际有效保存上限20；计数采用Array.from(trimmed).length，与服务端码点口径一致。保存成功回建议弹层，网络失败保留草稿，等待禁用表单和关闭。

旧21–120字提案/待学保持原文与既有审批/实际记录能力；超过60字仍完整显示在30vh标题滚动区。本设计不是批量缩写或强制旧提案审批前编辑。旧提案进入编辑完整带入120字，显示120/20并要求精简后才能重新保存。未知/失败/资格、角色、家长确认、记录真实学习和所有其他弹层操作沿用已批准合同。

精确设计矩阵：320×568、390×844、430×932，DPR1，各11态，共33张。状态为proposal、proposal-max、card-max、edit、edit-max、edit-over、edit-empty、edit-legacy、edit-error、edit-saving、legacy。截图保留固定操作和垂直滚动内容边界；不隐藏横向溢出，不通过标题截断降低高度。编辑输入的原生单行文字光标滚动是输入控件行为，不等于页面横向拖动。

原型按生产组件布局关系表达标题/编辑部分，使用合成数据和本地命令记录验证，不连接业务或模型；真实编辑键盘、WeChat原生节点、设备/读屏/系统大字体均NOT_RUN。其他命令按钮仅作原有操作层级上下文，不由本原型声明端到端业务验证。设计导出与21条交互见[设计证据](../../../../quality/evidence/SUGGESTION-TITLE-DESIGN-20261024.md)。

没有新增资源、依赖、动画、富文本、内容日志或网络请求。默认开关、正式学习/知识输入上限及冻结DREV02/03源不改。批准后只在原组件增加字段反馈，在原合同处执行上限；代码/原生证据独立记录。
