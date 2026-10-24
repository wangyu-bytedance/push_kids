# FEAT-011 — 提醒授权自动补充：候选设计

- Status: APPROVED
- Task Spec: [SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01](../../../../../specs/active/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md)
- Design Revision: DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Architecture: ARCH-20261017-NOTIFICATION-AUTO-RENEWAL-01（APPROVED）
- Approval: 用户，2026-10-17，审阅本版方案与设计后回复“按照这个方案落地”。
- Baseline: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02
- UI: [UI-001](../../ui/UI-001-parent-miniapp.md)、[UI-011](../../ui/UI-011-reminder-settings.md)
- Editable source: [index.html](index.html)；不请求外部资源，不调用微信/业务接口
- Approval candidates: [UI-001](../../snapshots/UI-001/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md)、[UI-011](../../snapshots/UI-011/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md)

## Direction / primary job

Operate：家长完成复习后，不必频繁返回提醒设置。延续「纸 · 芽」暖纸背景、松绿主色、衬线标题与中文系统正文；安静地提供一次明确选择，再把状态留在提醒设置。
颜色取自现有 tokens，几何随三档视口适配；不新建品牌、字体、插画或设计系统。

## UI-001 — 今日完成与首次说明

- complete按钮、复习反馈/日期/顺序与原有成功反馈保持。HTML中其余今日内容为最小合成上下文，不是整页重设计。
- 只在首次满足资格且复习成功后显示说明。尚未准备好微信候选时先准备，不把点击后异步请求接在原手势之后伪装授权。
- 说明使用既有半屏交互：标题“以后少去一次提醒设置”，说明已开启类型、微信仍可能弹窗、普通拒绝10条后再问、一次只增一次额度、仅本人且可关闭。
- 主操作“开启自动补充”，次操作“暂不开启”；两个纵向按钮，间隔10px，分别至少48/44px，窄屏不压缩字号或触控。
- 原生微信面板不在原型模拟，记住选项不可由我们勾选。主操作先同步调用微信，再登记真实结果与显式功能选择；CAS保护另一设备后来的关闭。
- 暂不开启持久化关闭；返回/关闭语义同暂不开启，不在日常完成中反复展示。离开或切换scope不产生迟到弹层。
- 面板长文案区可纵向滚动，按钮区固定可达。读屏进入标题、正文、主次操作；关闭恢复原焦点。Escape仅为HTML预览的取消行为，原生返回/遮罩语义须同意图验收。
- 自动补充成功、失败不新增Toast。正常复习完成反馈仍按原行为保留。

## UI-011 — 提醒设置

顺序：原生返回/标题 → 通道状态 → “完成复习时自动补充”独立开关 → 三类提醒各自状态/额度 → 最近实际投递。
“想不想收”、自动补充意愿、微信授权、发送结果仍是不同事实，不用一个开关冒充全部就绪。

- 自动补充默认未开启；开关、10次进度随本人账号，跨设备有效，不替家庭成员开启。
- 开关保存中禁重复点击；失败恢复真实值。明确关闭不通过10次冷却自行重启。
- 每类显示“可发送1次”“还需完成4条复习”“微信已记住拒绝”“次数待确认”等准确文字，颜色仅辅助。
- 冷却示例是当前类型基准后6/10，剩4条；达到10之后的下一次complete点击才申请，不承诺第10次保存后异步弹面板。
- remembered reject提供“去微信调整”；普通冷却保留“手动补充次数”，手动动作不受自动等待限制，但仍受微信权限/平台限制。
- 新/换模板提示须先明确同意；历史无模板绑定不能直接推断当前模板已同意。
- 当前用户非管理员不展示家人加入申请行；有权限时标注仅管理员。
- `accept`登记未确认，显示“次数待确认”，不显示假额度；未知结果不能从getSetting猜测发送额度。
- 网络错误保留已读设置但标明过期，禁不可信写入；设置/候选未确认时自动动作跳过。
- 仅第一次说明出现自有引导；低频再询问直接交给微信，不叠加自有确认弹窗。

## Exact viewport/state matrix

每个下列状态均导出320×568、390×844、430×932（CSS viewport，DPR1），共42张PNG。
正文至少14px、主要触控至少44px、最大内容宽480px、中文自然换行；页面正常纵向滚动，不用隐藏横向溢出通过验收。

| UI | State key | 含义 |
|---|---|---|
| UI-001 | guide | 首次长文案半屏；长内容和小屏按钮可达 |
| UI-001 | today-quiet | 原完成反馈；自动补充没有额外提示 |
| UI-011 | settings-off | 首次未开启，显示可主动开启的入口 |
| UI-011 | settings-enabled | 开启且有一次额度，不申请囤积 |
| UI-011 | settings-cooldown | 普通拒绝/取消后的6/10进度，手动入口 |
| UI-011 | settings-stopped | 微信记住拒绝，停止自动申请 |
| UI-011 | settings-pending | 实际accept后服务端登记结果不确定 |
| UI-011 | settings-loading | 设置尚未读取，不展示假状态 |
| UI-011 | settings-error | 网络异常保留旧设置、可重读 |
| UI-011 | settings-unavailable | 服务不可用，不发起授权 |
| UI-011 | settings-partial | 两类型不同结果；普通成员无管理员类型 |
| UI-011 | settings-forbidden | 身份失效/不可访问；不显示家庭数据 |
| UI-011 | settings-empty | 没有满足基础条件的类型，不自动申请 |
| UI-011 | settings-saving | 偏好保存中，保留原值、禁重复操作 |

其他状态映射：授权API过低/模板ban/filter/总开关关闭复用unavailable或stopped的中性卡片，准确原因码映射准确文案，不能显示成普通拒绝。
未决回调丢失显示pending式“授权结果待确认”，区别于已知accept“登记待恢复”；quota未知不能写成0或1。
本功能无输入表单、键盘/输入校验=N/A；无图表、AI、媒体、动画依赖、横向手势、桌面专版。
字体放大、读屏、底部安全区、弱网和后台恢复须实施后原生测试，不能由此HTML证明。

## Engineering and verification

页面仅呈现状态；通知专用controller管理短期候选、wx调用、内存中的待登记结果与generation；server管理开关/计数/额度。
预备租约不授额度；候选过期时直接跳过当前点击，不能先await刷新再拉面板。跨身份回调不能写新scope。
无业务Storage，无原始payload/身份/儿童正文日志，无真实微信CI调用，无不受限轮询。
可编辑源是设计事实，不进入小程序包；render.py只做本地候选截图/DOM检查，不证明业务代码正确。

### Reproduce candidate exports

```bash
python3 docs/design/frontend/prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/render.py
uv run python tools/validate_design_evidence.py --allow-pending --manifest docs/design/frontend/snapshots/UI-001/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md
uv run python tools/validate_design_evidence.py --allow-pending --manifest docs/design/frontend/snapshots/UI-011/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md
```

**不得在清单APPROVED后重新运行导出脚本覆盖清单/PNG。**修改可见设计必须新DREV。
原生验收：三视口按钮/开关/面板的节点矩形、间距、包含/无重叠和文字净空，加完整截图；iOS/Android真实授权和记住偏好/冷却行为另验。
工程已本地实现，原生几何与缺失验收见[实现证据](../../../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)。真机、上传、体验、审核和正式发布未发生。审批只允许本Spec+DREV，不追认旧UI-011设计缺口或历史原生验证；批准HTML及42张快照保持不变。
