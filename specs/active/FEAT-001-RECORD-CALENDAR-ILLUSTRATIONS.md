# FEAT-001 — 记录与日程纸艺插画

- Status: VERIFYING
- Risk: R1（两个页面同一视觉修饰，无跨领域数据改动）
- Spec owner: 产品负责人（用户）
- Implementer: Codex
- Reviewer / verifier: 用户 / Codex
- Created / last updated: 2026-10-13
- Spec revision: SPEC-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01
- User confirmation: 用户2026-10-13紧接本会话两张“记录页：相机、照片与铅笔 / 日程页：台历、时钟与叶枝”效果图回复“好的 按照这个方案进行落地”。本Spec将该唯一方案版本化；批准包含前一条说明“落地时会保留现有文案、导航和操作”。
- Target release: 本地实现与验证，未授权上传/部署/发布
- Affected Feature IDs: FEAT-001、FEAT-007（仅日程呈现）
- Implementation evidence: `docs/quality/evidence/RECORD-CALENDAR-ILLUSTRATIONS-20261013.md`；本地实现已完成，原生三视口/真机验收待补，未满足DONE门禁，保留active。
- Feature current-state documents: docs/domain/features/FEAT-001-push-kids-mvp.md；docs/domain/features/FEAT-007-travel-arrangements.md
- Feature baseline revision: 当前两Feature增量事实
- Feature merge owner: Codex

## Frontend Design Impact and Repository-native Approval

- Frontend impact: yes — 记录/日程插画与Hero纸面
- Frontend engineering impact: yes — 原生WXML/WXSS、本地图片和装饰错误降级
- Affected UI IDs: UI-001、UI-017
- UI current-state documents: docs/design/frontend/ui/UI-001-parent-miniapp.md；docs/design/frontend/ui/UI-017-travel-arrangements.md
- Frontend baseline revision: FDB-20260913-04 APPROVED
- Frontend engineering constraint revision: FEC-20261007-NATIVE-GEOMETRY-02 APPROVED
- Affected frontend quality dimensions: component/state/form/responsive/a11y/browser/performance/security/privacy/motion-media/observability
- Budgets: 320×568、390×844、430×932；触控≥44px；七天可见；插画不遮挡控件；新增资源≤200KiB、主包≤1.5MiB；图片本地且无人物/文字/儿童照片
- Approved frontend engineering deviations: none
- Current Design Revisions: 记录页既有语音与输入修订、日程既有PKDS原生结构
- Proposed / Approved Design Revision: DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01
- Approved Task Spec revision: SPEC-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01
- Prototype status: APPROVED
- Design approval evidence: 同User confirmation；不额外批准效果图生成器新增的装饰性口号、虚构日期或导航高亮错误
- Editable design source: docs/design/frontend/prototypes/DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01/*.svg + render.py
- Design source SHA-256 / snapshot manifest: docs/design/frontend/snapshots/UI-001/DREV-20261013-RECORD-CALENDAR-ILLUSTRATIONS-01/APPROVAL.md
- Required exports: records empty/photos/readonly/error；calendar content/empty/error/long-name × 三档视口
- Permitted implementation deviations: 效果图按现有小程序文案、底部导航、语音与按钮状态归一；插画不新增行为。SVG阴影/字体与原生抗锯齿近似，原生几何必须实测
- UI current-state merge owner/evidence: Codex / 验证后更新
- Frontend visual/a11y/resolution verification: 三档设计+原生矩形/截图，真机如无法运行须记NOT_RUN
- Frontend engineering verification: npm test、lint、原生编译、静态/架构/设计、图标幂等与资源检查
- External design dependency: none

## 1. Problem and outcome

设置页插画方案得到方向认可后，用户批准记录页和日程页效果图。两个页面采用相同暖白松绿纸艺风格但不同主题：记录页头书本嫩芽、上传区相机照片；日程页头台历时钟。保留操作扫描效率，装饰不参与业务状态。

## 2. Scope

只修改records/index、calendar/index及三张本地图片。页头沿用原标题和孩子选择，增加右侧插画，复用pk-hero暖白径向晕光/弧线；相机图只在未选照片时显示，图片失败回退原相机图标。日程选择器及列表保持清晰独立。
设置页此前Spec仍待审批，不把本次对两张效果图的批准扩展为设置页实施。今日、报表、API、数据、权限、分析与排期均不变。
最终事实合并FEAT-001、FEAT-007、UI-001、UI-017；不改行为目录的业务合同。

## 3. Impact map

records/index.wxml → 既有addPhotos/save/语音控制器 → utils/api/cloud-media；calendar/index.wxml → 既有shiftWeek/chooseDate/chooseDay/openEvent → 现有API。
新增仅本地image错误→页面装饰flag→隐藏插画/相机回退。没有新业务路径和共享抽象。

## 4. Required design views

### Link/call graph

```text
Tab → 现有page.load → 原内容
本地插画image → binderror → 当前页装饰flag → 隐藏/图标回退
记录上传 / 周历导航 → 原handler → 原服务合同
```

### Sequence diagram

N/A：业务时序不变；本地图片失败不请求接口、不改变表单。

### State machine

```text
装饰初始可见 → image加载失败 → 隐藏（不重试、不影响正文）
记录photos=0 → 相机插画；photos>0 → 原照片网格
viewer / 无孩子 / 错误 / submitting → 原内容与权限路径
```

### Architecture diagram

N/A：页面域、层、依赖方向和扩展点均不改变。

### Trade-offs

| 选项 | 收益 | 成本 | 决策 |
|---|---|---|---|
| 本地透明纸艺插画+既有Hero | 对齐批准效果、离线可用、无新服务 | 新增约170KiB资源、页头高度增加 | selected |
| 全屏效果图作为背景 | 快速复刻 | 文字不可读、无法适配原生控件 | rejected |
| 远程图片/运行时生成 | 包体较小 | 网络依赖与隐私/恢复风险 | rejected |

## 5. Expected file changes and deletion plan

| Path | Action | Purpose |
|---|---|---|
| apps/miniprogram/pages/{records,calendar}/index.{wxml,wxss,js} | modify | 页头/上传装饰及错误降级 |
| apps/miniprogram/assets/illustrations/*.png | add | 三张本地透明插画 |
| tests/frontend相关用例 | modify | 图片失败不写业务状态，既有操作回归 |
| tools/illustration_geometry.js | add | 有意义的原生矩形审计工具，纯数字证据 |
| Feature/UI、Spec、DREV、quality evidence | add/modify | 验证事实 |

Final authoritative path: 原页面。保留既有业务代码，不复制数据控制器。

## 6. Acceptance criteria

- AC-001：两页主题不同且纸艺风格一致；记录相机只出现在空上传区，日程插画不与周历控件重叠。
- AC-002：照片/文字/语音、实际时间、只读、忙状态、提交与周历/事件编辑合同不变；无图恢复不清空数据、不发请求。
- AC-003：三档视口页头长孩子名与标题可读、插画与正文不重叠、七天在容器内、圆形控件与关键操作达到44px、页面无横向移动。
- AC-004：图像本地透明、总新增≤200KiB、主包≤1.5MiB，无人物/儿童数据、日志/存储无新隐私风险。

## 7. Required test points

| ID | AC | Test/command | Expected |
|---|---|---|---|
| TP-001 | 002 | npm test / npm run lint:miniapp | PASS |
| TP-002 | 001/003 | 24组设计SVG/PNG、SHA验证 | PASS |
| TP-003 | 001/003 | 原生320/390/430矩形及截图：记录空/照片/只读/错误/无图/长名；日程内容/空/错误/长名/无图 | 无溢出、重叠；触控尺寸达标 |
| TP-004 | 002 | 本地无图恢复和导航/时间展开/保留输入；iOS/Android smoke | 业务不变；无法真机则NOT_RUN |
| TP-005 | 004 | PNG alpha、资源尺寸/体积、编译preview包、隐私检查 | PASS |
| TP-006 | all | 小程序/架构/设计validator、图标生成幂等、diff check | PASS |

## 8. Plan

1. 保存批准效果图、本地插画和可编辑设计证据，记录既有批准。
2. 实施页面呈现与失败降级，不改业务API。
3. 自动化、原生与资源检查；更新Feature/UI及证据，评估完成状态。全量后端检查N/A（没有后端变更）。

## 9. Verification

Pending。批准时基线commit及验证见quality evidence。

## 10. Completion

批准已记录；待实现与验证。真机无法运行时明确记录，保留VERIFYING及未完成门槛，不虚称DONE。
