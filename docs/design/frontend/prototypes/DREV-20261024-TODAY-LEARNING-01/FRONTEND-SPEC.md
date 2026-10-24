# DREV-20261024-TODAY-LEARNING-01 — 今日待学与提前复习

- Status: APPROVED
- Owner / designer / verifier: 产品负责人 / Codex / Codex（原生及内容由产品负责人验收）
- Created: 2026-10-24
- Task Specs: [空白日复习Spec04](../../../../../specs/active/FEAT-001-EMPTY-DAY-EARLY-REVIEW.md)；[单项建议Spec04](../../../../../specs/active/FEAT-004-INCREMENTAL-LEARNING-PATH.md)
- Approved architectures: ARCH-20261024-EMPTY-DAY-EARLY-REVIEW-02；ARCH-20261024-INCREMENTAL-LEARNING-PATH-03
- FDB / FEC: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，已批准基线不修改
- Affected current UI: [UI-001](../../ui/UI-001-parent-miniapp.md)，已同步本地待学与提前复习，验收边界独立记录
- Editable source: [index.html](index.html)，无网络依赖；[候选SHA清单](../../snapshots/UI-001/DREV-20261024-TODAY-LEARNING-01/APPROVAL.md)
- Requirement approval: 2026-10-24用户「按照这个方案 落地」批准两份Spec03及最终需求汇总
- This Design / Spec04 approval: 产品负责人2026-10-24针对明确列出两份Spec04、Architecture02/03和本Design01的审批问题回复「批准，按此实现」；HTML、78张PNG及SHA自此冻结

## 1. 方向与页面位置

Operate：沿用知芽的暖白纸面、松绿主色、系统中文字体和安静卡片，以清楚的状态与单项操作帮助家长安排、确认和记录学习。

五Tab与主品牌栏保留；正常今日hero及记录学习入口保留。新增“今日学习”建议/待学区域紧随hero，位于复习安排之前；已有“今天记录的学习”仍展示正式事实，不将待学混进已确认记录。待学只有一项，未学跨日显示，不突出欠账或连续天数。无资格时不自动弹窗；没有学习历史/年级时给出原有录入/档案入口。

复习卡增加“提前安排”与“原计划10月26日”文字。保持原学习内容入口与完成/稍后语义，目录仅增加原日期和今日安排状态；现有筛选、分页和手动改期不改。review-inventory只展示发生变化的安排信息面板，完整独立/内嵌目录沿用现行批准布局。

仅使用合成孩子、年级与学习文字，截图不包含真实家庭/儿童资料，不代表已为任何孩子生成内容。

## 2. 交互合同

1. 每孩子/自然日共享至多一次自动展示。弹层可以显示正在准备、可编辑提案或失败；关闭/“今天先不学”消费当天自动提示，主动查看与换项仍可用。模型请求与配额由服务器管理。
2. 建议面板显示AI标识、具体内容、预计时长、与已学衔接的依据及可编辑说明；主按钮“确认加入今日学习”，次操作“编辑内容”“换一项”“今天先不学”。12分钟样本特意证明新学不受复习10分钟上限约束。
3. editor/manager可批准、编辑、暂缓、换项、删除和记录；viewer只看家长已批准待学，不争抢自动提示或显示写操作。403/资源不存在/输入变化不继续提交。
4. 待学卡主操作“记录实际学习”，删除入口始终可见但视觉安静。删除前说明移除待学、已确认学习保留、将请求不同建议且仍须审批；生成失败后可以重试，不恢复旧批准。
5. “记录实际学习”显示家长可编辑的实际文字和发生时间，不要求照片；两个明确动作“完成并记录”“记录部分，继续待学”。部分只记录实际部分，同一任务继续；明确完成才结束。保存中禁双击，失败保留表单，确认成功但关联失败进入可恢复状态。
6. 暂缓次日仍符合资格且建议有效时沿用同项；有效性因新内容/年级/引用变化或7日过期而失效时，说明需要重新生成，不沿用旧批准。
7. 切孩子/家庭、权限变更或离页递增请求代次，停止轮询并丢弃迟到响应；再次进入从服务端状态恢复。已有家长确认/管理弹层期间等待，不消费自动提示；避免叠加。已学事实与复习不受建议失败影响。

## 3. 精确视口/状态矩阵

每个下列状态均导出320×568、390×844、430×932，1x/DPR1，共78张PNG。review-early/long/viewer的导出把内容区滚动220px以显示原日期和操作，其余从顶部开始；键盘态为210px占位空间，不能证明微信键盘几何。

| State | 目标与关键约束 |
|---|---|
| review-due | 自然到期，标签不伪称提前 |
| review-early | 提前标签、原日期、完成/稍后与原学习入口 |
| review-empty | 无合适候选允许为空，手工记录可用 |
| review-handled | 今天做完不再补排 |
| review-inventory | 目录原日期及今日提前安排信息，不改手动日期 |
| review-viewer | 只读提前安排，无反馈按钮，保留原学习内容查看 |
| review-source | 原始实际学习内容入口保留 |
| review-long | 长中文条目换行，日期/触控不挤压 |
| review-error | 复习读取失败，原地重试 |
| suggestion | 可编辑单项建议、依据、预计时间与确认 |
| suggestion-edit | 编辑标题/操作内容，表单保留 |
| suggestion-deferred | 今日暂缓，不自动再次打开，可主动查看 |
| suggestion-planned | 一项待学卡，家长已确认，与已学事实区分 |
| suggestion-partial | 已记录实际部分，同一待学继续 |
| suggestion-delete | 删除影响确认与替代需再批 |
| suggestion-record | 实际内容/实际时间确认，部分/完成两个明确动作 |
| suggestion-no-history | 先录入已有学习，不凭空建立课程 |
| suggestion-missing-grade | 完善现有年级，无年龄/生日表单 |
| suggestion-loading | 真实生成状态，可离开，不虚构进度 |
| suggestion-error | 无合适内容或依赖失败，重试/手工记录 |
| suggestion-viewer | 只读已批准待学，没有管理操作 |
| suggestion-stale | 输入已变化，重新生成后再确认 |
| suggestion-long | 长提案滚动、固定可达主操作 |
| suggestion-keyboard | 键盘占位下表单内滚动、保存按钮在键盘上方 |
| suggestion-saved | 实际确认成功，正式记录标识 |
| suggestion-offline | 保留既有内容和可恢复错误 |

原生验收另覆盖：复习viewer无反馈、审批冲突409、保存中/保存失败保留输入、换项限流429/取消/迟到结果、级联删除、两个家长/设备去重、自然跨日、字体放大、底部安全区。其视觉复用上表error/stale/viewer/long，不引入另一套布局；不能用HTML演示替代服务端或原生证据。

## 4. 组件、样式和数据边界

实际采用单领域组件`components/today-learning`，同目录拥有提案/待学/真实记录面板、服务调用、有界轮询和表单恢复；今日页只协调弹层/导航。没有额外独立controller或框架，责任仍限于单一业务组件。API只经utils/api.js；组件不判定两日条件、复习资格或家长权限。复习日期字段由todo-card与目录共用已有格式化层，不新建无owner通用utils。

颜色/字体/圆角/间距从tokens.wxss消费，prototype以相同语义值映射为CSS变量；生产不复制网页CSS。正文≥14px，普通触控≥44px，图标只用现有生成线图标；无框架、媒体、图表或新包。面板最大85%视口，正文独立滚动，主操作固定，普通页面不横向滚动，不靠overflow-x:hidden掩盖问题。

远端建议/任务/Job/提示状态由服务端拥有；本地仅暂存当前表单和当前请求代次，未确认正文不进Storage/日志。AI内容用普通文本绑定，不渲染HTML。无分享、埋点或儿童直接AI对话。

## 5. FEC实例化与必需验证

| Dimension | 本次约束/证据 |
|---|---|
| state/form | 显式状态、提交版本、幂等、真实记录恢复；部分/完成不能混淆；保存失败保留所有输入 |
| component/data | server为权威；当前孩子/家庭/权限/代次绑定迟到响应，GET不调用模型 |
| a11y | 原生可访问名称、状态文字、弹层背景隐藏、焦点进入/关闭恢复、逻辑顺序、读屏；HTML只验证Tab循环 |
| responsive | 三视口精确节点矩形；44px按钮/8px间隔/容器包含/长文本/键盘/安全区；不使用固定正文高裁切 |
| runtime | 微信开发者工具及代表iOS/Android客户端；相机不可用仍能文字记录 |
| performance | 主包≤1.5MiB；/current≤16KiB；关联页20/max50≤64KiB；轮询2/4/8秒至多8次，切上下文停止 |
| security/privacy | viewer拒写、双scope校验、普通文本、字段字节上限、无原始模型载荷/儿童正文日志和本地持久化 |
| motion | 无新增装饰动效，状态反馈遵循150–240ms及减少动态偏好 |
| observability | 仅安全错误码/状态/耗时；错误可见、重试不阻塞手工学习/正常复习 |

## 6. 本轮实际设计验证

执行：`.venv/bin/python docs/design/frontend/prototypes/DREV-20261024-TODAY-LEARNING-01/render.py`。隔离本机headless Chrome/155.0.8059.85，仅访问file本地HTML。首次沙箱启动失败；经自动审批允许启动隔离Chrome后成功。初版走查发现键盘遮挡操作及待学位置过低，已在未批准候选内修正后重新导出。

最终[render-report.json](render-report.json)：78份导出及HTML控件横向包含/44px尺寸/键盘保存区域检查通过；8条原型点击转移、Tab焦点循环通过，Runtime异常0。目视检查建议主态、320小屏提前复习、部分待学与键盘空间态；补齐复习只读态后重新导出最终清单。没有访问模型、后端或儿童数据。

候选manifest/hash与文档检查结果由Spec04记录。以上是批准前的设计原型验证。批准后的业务自动化、迁移/规模和原生节点实际结果见[实现证据](../../../../quality/evidence/TODAY-LEARNING-IMPLEMENTATION-20261024.md)；真机、完整读屏、内容质量与主体适用条件尚未通过，不能用原型抵扣。

## 7. 批准与后续

产品负责人2026-10-24针对两份Task Spec04（含Architecture02/03）及本DREV01明确回复「批准，按此实现」。APPROVAL.md已记录，HTML/PNG/SHA保持冻结。业务已本地实现、功能默认关闭且未部署；当前文档已按实际diff同步，完整验收继续VERIFYING。

如批准后出现可见偏离，创建新DREV并重新评审；既有manifest除Superseded by外不修改。最终验收闭合后更新当前文档，Spec才能DONE并归档。
