# UI-011 — 提醒设置与微信授权入口

- Status: CURRENT_LOCAL / VERIFYING / NOT_RELEASED
- Current-state revision: UI-STATE-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Related Features: FEAT-003 / FEAT-011
- Approved Spec: SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Baseline: FDB-20260913-04；engineering constraints: FEC-20261007-NATIVE-GEOMETRY-02
- Approved Design Revision: DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Approval: 用户，2026-10-17，“按照这个方案落地”。
- Source/matrix: [FRONTEND-SPEC](../prototypes/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/FRONTEND-SPEC.md)
- Immutable snapshots: [manifest](../snapshots/UI-011/DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01/APPROVAL.md)
- Evidence: [实现与验收缺口](../../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)

## Information architecture

入口仍是“设置 → 提醒设置”，非Tab二级页，空档案也可进入。
顺序为通道与次数概况、自动补充独立开关、逐类提醒开关及授权状态、最近实际投递。
想不想收、是否自动补充、微信额度和真实送达分别展示，不用一个开关冒充全部就绪。

## Current states

| State | Visible contract |
|---|---|
| 次数0/新模板 | 中性“提醒需要补充次数”；逐类说明需同意当前模板，提供“手动补充次数” |
| 有次数/长期授权 | 按实际显示“可发送N次”或“长期授权有效”，不囤积额度 |
| 冷却 | “还需完成N条复习”，保留显式手动补充；自动动作仅在后续复习点击 |
| 明确停止 | 记住拒绝/总开关关闭显示原因及“去微信调整”；ban/filter显示平台原因 |
| 登记未确认 | “提醒次数待确认”及“次数待确认 · 登记待恢复”；保有真实回调时仅恢复原事件登记，隐藏该类再次申请入口 |
| 已预备尚未调用 | 显示“待微信授权”，不是已授权 |
| 开关保存中/失败 | 保留真实值并禁重复操作；失败回滚并显示错误 |
| 全部类别关闭 | “提醒尚未开启”，不自动申请 |
| 查询失败 | 状态待更新、保留旧设置、禁写；403清空家庭设置，迟到回调不覆盖新页 |
| 通道不可用/旧微信 | 如实显示原因；不调用原生授权，旧微信提供升级说明 |
| 投递读取失败 | 仅记录段降级，其余设置独立 |

## Interaction and responsive contract

候选在点击前预备，原生调用在同步点击链里、任何await之前，最多3个模板。
只有真实accept登记额度；普通reject/cancel按10条冷却，ban/filter和技术失败分别处理。
未决事件到期不自动重开，丢失结果不能由getSetting推测，手动重新授权是明确操作。
本人自动开关默认未开启；服务端跨设备保存，版本冲突需刷新，不被迟到开启覆盖。

本地视觉增量revision `UI-VISUAL-20261021-HERO-ARC-01` 已随共享样式
去掉提醒就绪/中性卡右下角细弧线，其他状态与授权行为保留。批准来源为
[Spec01](../../../../specs/active/BUG-030-HERO-BACKGROUND-ARC.md) /
[DREV-20261021-HERO-ARC-REMOVAL-01](../prototypes/DREV-20261021-HERO-ARC-REMOVAL-01/FRONTEND-SPEC.md)，
本地验证和未完成验收见[质量证据](../../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)，未上传/部署。

沿用“纸 · 芽”颜色、字体和卡片。正文/状态至少14px，操作目标至少44px，中文自然换行；
矩阵320×568、390×844、430×932。原生几何、完整截图、字体放大/读屏与真机分别验收。
不新增自动补充Toast，不改变通知受众、调度或学习/复习规则。

## Change references

2026-10-17 SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01 / BHV-037：
本页替换旧“提醒已就绪/去授权”、ban/filter统一当拒绝等本地描述。
线上发布事实见FEAT-003，本地实现不等于发布。
