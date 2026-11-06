# FEAT-007 — 出行安排

2026-10-26开发归档：已交付037后端/0.1.16客户端所覆盖的需求按用户批准规则标记开发DONE，验收缺项独立保留；后续BUG-035和旅行导入精简尚未交付，继续active。当前归档和待验入口见[Spec状态清单](../../../specs/STATUS.md)，依据为[治理Spec](../../../specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md)。本轮不改产品合同、测试结论、设计或发布阶段。

- Feature ID: `FEAT-007`
- 2026-10-13设置卡片背景接入：书包路线插画、纸面渐变，出行配置行为不变。SPEC-20261013-CARD-BACKGROUNDS-01，证据docs/quality/evidence/CARD-BACKGROUNDS-20261013.md，原生验收待补。
- Local visual update (2026-10-13): 日程页标题卡接入台历纸艺插画，出行数据与冲突行为保持原合同。Spec `SPEC-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01`；原生验收待补，证据 `docs/quality/evidence/RECORD-CALENDAR-ILLUSTRATIONS-20261013.md`。
- Status: `DEVELOPMENT_DONE / BACKEND_037_DEPLOYED / CLIENT_0.1.16_UPLOADED / NATIVE_ACCEPTANCE_PENDING`
- Current-state revision: `FEAT-STATE-20261026-04-DEVELOPMENT-DONE`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-06
- Authoritative implementation: `apps/api/src/push_kids/travel/`、`apps/api/src/push_kids/activities/conflicts.py`、`apps/miniprogram/pages/{settings,calendar}/`
- Applied Spec: `specs/completed/FEAT-007-TRAVEL-ARRANGEMENTS.md` revision `SPEC-20260906-TRAVEL-02`

> 本 Feature 对应实现已随后端037正常部署、客户端0.1.16开发上传，按用户规则开发DONE。
> 原320/390/430原生视口与iOS/Android真机验收缺项独立保留，未设体验版/审核/正式发布。

## Purpose and scope

让家长按孩子维护上学、放学、接送等每周重复时段，并只在“日程” Tab 查看这些时间占用；当同一天的
明确时段相交时，在日程中用红色与文字同时提示冲突，方便人工核对。

## Previous behavior

- 设置页可管理课外活动固定安排；固定活动同时出现在“今日”和“日程”。
- 日程页可管理单次或每周重复的日程事件。
- 日程聚合结果没有独立出行来源，也没有冲突元数据或冲突 UI。

## Current local behavior

本地视觉增量 `FEAT-VISUAL-20261021-HERO-ARC-01`：设置出行卡与日程标题卡随共享样式删除细弧线，
插画、出行与冲突合同保留。[Spec01](../../../specs/completed/BUG-030-HERO-BACKGROUND-ARC.md) /
DREV-20261021-HERO-ARC-REMOVAL-01已批准；[本轮证据](../../quality/evidence/HERO-ARC-REMOVAL-20261021.md)
记录当次验证与验收缺口；该样式已随0.1.16开发上传，未体验/审核/正式发布。

- 设置页按当前孩子新增“出行安排”卡，可新增、编辑、停用/删除每周重复时段。
- 每项包含名称、星期集合、开始时间和结束时间；上学、放学、接送是快捷名称而非封闭枚举。
- 出行只投影到“日程”，不进入“今日”、Todo、报表、AI、活动提醒或活动练习记录。
- 同一孩子、同一天的全部明确时段按半开区间 `[start, end)` 检测；相交双方均带冲突信息。
- 冲突只警告，不阻止保存；相邻端点不算冲突。
- 每个孩子的 CalendarEvent、固定 ActivitySchedule 与 TravelArrangement 在用事项合计最多 20 项；
  新增在孩子行锁内跨来源计数，删除任一来源会释放名额。既有超限数据保留且可读。

## Domain, data and permissions

- 数据 child-scoped 且 family-scoped；服务端必须校验可信家庭及孩子归属。
- 独立 `travel_arrangements` 聚合由 `travel` capability 管理；日程聚合只消费其投影合同。
- 仅 manager/editor 可写，viewer 可读；跨家庭资源按现有规则安全返回 404。
- MVP 不含地点、路线、接送人、提醒、例外日期或跨午夜出行。

## Frontend mapping and approval

- Proposed UI: `docs/design/frontend/ui/UI-017-travel-arrangements.md`.
- Candidate design: `docs/design/frontend/prototypes/DREV-20260906-TRAVEL-01/index.html`.
- Baseline/engineering: `FDB-20260906-02 / FEC-20260906-04`.
- Repository-native approval manifest: pending per UI-017；当前按 `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01` 使用可编辑 HTML、视口/状态导出与匹配 SHA-256 清单。
- `SPEC-20260906-TRAVEL-02`、`DREV-20260906-TRAVEL-01`、全部日程项冲突范围、20 项总上限已由用户于 2026-09-06 批准；开发实现已交付，完整原生/设备验收待补。

## Quality and release status

- Design governance revision: `DOC-SPEC-20261013-02-01`；[门禁同步记录](../../../specs/completed/DOC-002-MARKDOWN-STATE-RECONCILIATION.md)，仅修订设计证据政策，不改变实现/发布状态。

- Spec/Design approval: approved by the user on 2026-09-06, including all-calendar-source conflicts; historical tool waiver does not define the current design gate.
- Production code/migration: delivered in backend037 and client0.1.16 development upload. Original automation evidence retains its date and scope; native/device acceptance is still pending.
- Required visible evidence after implementation: 320×568, 390×844, 430×932 for normal/conflict/form/error/read-only states.

## Change references

- 2026-09-06 — Local implementation added independent travel CRUD/migration, Calendar-only projection, deterministic
  cross-source conflict metadata, Settings management UI and Calendar conflict UI. Full backend and frontend
  automation passed; native viewport/device evidence and every deployment state remain pending.
- 2026-09-06 — Review remediation lists every multi-conflict object and adds the approved serialized 20-item
  cross-source capacity gate without deleting existing data.
- 2026-09-06 — Planned baseline and candidate design created and subsequently approved with the scoped Figma waiver.
