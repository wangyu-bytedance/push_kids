# FEAT-007 — 出行安排

- Feature ID: `FEAT-007`
- Status: `CURRENT_LOCAL / AUTOMATION_PASSED / NATIVE_ACCEPTANCE_PENDING`
- Current-state revision: `FEAT-STATE-20260906-03-LOCAL`
- Owner: 产品负责人（用户）
- Last verified: 2026-09-06
- Authoritative implementation: `apps/api/src/push_kids/travel/`、`apps/api/src/push_kids/activities/conflicts.py`、`apps/miniprogram/pages/{settings,calendar}/`
- Active change Spec: `specs/active/FEAT-007-TRAVEL-ARRANGEMENTS.md` revision `SPEC-20260906-TRAVEL-02`

> 本 Feature 已在当前本地工作树实现并通过自动化验证；尚未上传微信小程序、部署后端或完成
> 320/390/430 原生视口与 iOS/Android 真机验收。

## Purpose and scope

让家长按孩子维护上学、放学、接送等每周重复时段，并只在“日程” Tab 查看这些时间占用；当同一天的
明确时段相交时，在日程中用红色与文字同时提示冲突，方便人工核对。

## Previous behavior

- 设置页可管理课外活动固定安排；固定活动同时出现在“今日”和“日程”。
- 日程页可管理单次或每周重复的日程事件。
- 日程聚合结果没有独立出行来源，也没有冲突元数据或冲突 UI。

## Current local behavior

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
- Figma node and approval snapshot: pending under the approved scoped waiver; Starter tool-call limit + View seat blocked the attempt.
- `SPEC-20260906-TRAVEL-02`、`DREV-20260906-TRAVEL-01`、全部日程项冲突范围、20 项总上限与 FEAT-007 scoped Figma waiver 已由用户于 2026-09-06 批准；实现与验证进行中。

## Quality and release status

- Spec/Design approval: approved by the user on 2026-09-06, including all-calendar-source conflicts and the FEAT-007-only Figma waiver.
- Production code/migration: implemented locally. Backend/frontend automation passed; local runtime deployment, cloud release and Mini Program upload were not run.
- Required visible evidence after implementation: 320×568, 390×844, 430×932 for normal/conflict/form/error/read-only states.

## Change references

- 2026-09-06 — Local implementation added independent travel CRUD/migration, Calendar-only projection, deterministic
  cross-source conflict metadata, Settings management UI and Calendar conflict UI. Full backend and frontend
  automation passed; native viewport/device evidence and every deployment state remain pending.
- 2026-09-06 — Review remediation lists every multi-conflict object and adds the approved serialized 20-item
  cross-source capacity gate without deleting existing data.
- 2026-09-06 — Planned baseline and candidate design created and subsequently approved with the scoped Figma waiver.
