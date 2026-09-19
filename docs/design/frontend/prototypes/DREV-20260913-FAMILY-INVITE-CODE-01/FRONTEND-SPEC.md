# DREV-20260913-FAMILY-INVITE-CODE-01 — 六位家庭邀请码

- Status: `APPROVED`
- Related Task Spec: `BUG-SPEC-20260913-19`
- UI IDs: `UI-009`、`UI-010`
- Baseline: `FDB-20260913-04`
- Engineering constraints: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01`
- Editable source: `family-invite-flow.html`

## Visual direction

保持 PKDS-2.0「纸 · 芽」暖白纸面、松绿主操作和原生单列结构，只用清晰命名与数字分组修复流程，
不引入新的视觉语言或导航层级。

## Terminology and order

| Name | Created when | Used for | Visible to |
|---|---|---|---|
| 家庭邀请码 | 管理员创建邀请时 | 家人手动找到家庭并提交申请 | 管理员、申请人 |
| 微信邀请 | 管理员创建邀请时 | 通过小程序分享路径直接找到家庭 | 分享双方；长 token 不上屏 |
| 申请核验码 | 申请成功后 | 管理员与申请人核对本次申请 | 申请双方 |

“家庭邀请码”固定为 6 位数字，允许前导零；“申请核验码”也固定为 6 位数字。界面不得再把申请后
才存在的核验码写成申请前的输入条件，也不得把长 token 称为 6 位码。

## UI-009 — 管理员邀请就绪

- 点击“邀请家人”后，同一区域进入 pending；成功后显示六位家庭邀请码，视觉分组为 `482 731`。
- 提供“复制邀请码”和“微信邀请”两个操作；复制值不含空格。
- 说明文字为“家人可以输入邀请码，或直接打开微信邀请；提交后仍需你确认”。
- 邀请码只保留在当前页面内存，不进 Storage、日志、分析或错误文案。
- 页面重进后，现有有效邀请仍可撤销；若明文邀请码已不在内存，显示“重新生成邀请码”，不伪造或
  从摘要反推明文。
- 生成失败保留当前成员数据并原地重试；无管理权限时不展示创建入口。

## UI-010 — 申请人输入邀请码

- 无家庭用户点击“申请加入家庭”后进入六位数字输入。
- 输入使用数字键盘、`maxlength=6`；显示值按 `3 + 3` 分组，提交值去空格。
- 少于六位时主按钮不可用，并显示“请输入管理员发来的 6 位家庭邀请码”。
- 六位后由用户点击“查看家庭”触发预览；不在每次按键时发请求。
- 无效、过期、撤销、限流错误显示在字段附近，保留原输入并允许修改或重试。
- 从微信邀请卡进入时不显示手工输入，继续携带长 token 走原安全路径。
- 预览成功后继续选择关系并提交；申请成功显示“申请核验码”，避免与前置“家庭邀请码”混淆。

## States not shown in candidate exports

- loading：邀请码创建或预览期间按钮显示明确 pending，阻止重复提交。
- invalid/expired/revoked/rate-limited：输入保留，字段级错误 + 可重试。
- pending：显示“申请核验码”和复制入口。
- manager approval：列表与确认弹窗使用“申请核验码”。
- permission denied：非管理员不显示邀请创建入口，服务端仍最终鉴权。

## Responsive and accessibility contract

- 320×568、390×844、430×932 竖屏；内容可纵向滚动，关键操作可达。
- 常规触控目标至少 44px，正文至少 14px，数字使用 tabular nums。
- 输入框具备“6 位家庭邀请码”可访问名称；错误不只依靠颜色。
- 复制成功 Toast 只是补充反馈；关键错误持续显示在页面。

## Candidate exports

- `UI-009`: manager invite-ready at 320×568、390×844、430×932。
- `UI-010`: applicant manual-code entry at 320×568、390×844、430×932。
- HTML 查询参数：`?screen=manager`、`?screen=join`。
