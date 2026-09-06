# UI-010 — 家庭分享、申请与审批

- Status: `CURRENT_LOCAL / 390_NATIVE_CAPTURED / MATRIX_PENDING`
- Related Feature: `FEAT-002`
- Related Spec: `SPEC-20260831-10`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Design revision: `DREV-20260906-PKDS-01`（屏 A1–A4、G5；取代 `DREV-20260905-UX-03` 的视觉部分）
- Last reviewed artifact date: 2026-08-31
- Interactive artifact: `docs/design/frontend/prototypes/DREV-20260831-08/index.html`
- Snapshot manifest: `docs/design/frontend/snapshots/UI-010/DREV-20260831-08/APPROVAL.md`
- Figma file: https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj
- Figma node: `N/A` — 当前账号为 Starter/View，MCP 写入限额已触发

> BUG-010 revision 11 已获产品负责人批准并在本地实现；家庭入口层级已由390 CUA验证，未部署，双账号审批与其他视口仍待补齐。

## Core journey

```text
无孩子 → 开始记录 → 填写孩子基本信息
       ↘ 使用邀请 → 最小预览 → 申请加入 → 等待确认
manager → 邀请家人 ──────────────────────→ 确认关系与能力 → 加入家庭
```

分享入口只发起申请，不直接授权。申请人获批前不能看到学习、日程、照片或成员名单；manager
确认时选择最终关系，并在“只能查看/可以共同记录/设为家庭管理员”中选择加入后可以做什么。

## Review states

| State | Visible contract |
|---|---|
| first entry | “开始记录”和“申请加入家庭”两个主路径；描述用户目标，不把孩子表达成待添加对象 |
| share | 24 小时、管理员确认；明确最小披露和单一“微信邀请家人”操作 |
| apply | 家庭称呼、拟申请关系；说明关系不决定加入后可以做什么 |
| pending | 家庭、与孩子的关系、等待确认；允许查看最新结果和撤回 |
| approve | manager 确认最终关系与协作能力；同意/拒绝明确分层 |

## Interaction and safety contract

- 分享卡片和预览不展示学习记录、成员名单、照片或联系方式。
- 提交申请和审批均有 pending、防重复提交、可恢复错误及服务端最终授权。
- 申请人与管理员显示同一六位申请码；管理员每次授权前确认，处理时整张申请禁用。
- 一个邀请只允许批准一人；批准、撤销或到期会终结同邀请的其他待审批申请并释放申请人绑定。
- 有效邀请列表不返回或展示原始 token，原始 token 只在创建响应中用于一次微信分享。
- 批准后显示审批人和审批时间；两名 manager 并发操作只产生一个终态。
- expired、revoked、rejected、approved、duplicate、401/403、loading/error、孩子信息表单、关系编辑
  和最后 manager 保护仍须在后续 review slice 补齐后，才能批准完整实现门禁。

## Visual and responsive contract

沿用 `FDB-20260830-01` 的暖纸色、墨绿色主操作、系统中文字体与单列卡片。评审矩阵为
320×568、390×844、430×932；小屏内容允许纵向滚动，主操作不得被永久裁切。没有外部图片、
字体、图标库或儿童内容进入原型。

## Approval status

本地前后端已实现上述合同并有 SQLite 集成测试；邀请预览受可信 actor 的进程内限流保护。
当前账号线上可回滚验证完成创建201、最小预览200、撤销204和撤销后预览410，证据未保存token；
线上旧后端尚无有效邀请GET（405），本地端点必须和前端一起发布。多实例共享限流、真实微信双账号、
320/430和 iOS/Android 仍是公开发布门禁。

## Change references

- 2026-09-06 — `SPEC-20260906-PKDS-01 / DREV-20260906-PKDS-01`（屏 A1–A4、G5）：首次进入、建档、
  口令加入、等待确认和加入申请审批按 PKDS-1.0 重做。A1 提供两条并列路径卡；A2 表单有吸底 CTA
  与缺项提示；A3 展示口令错误态与隐私说明；A4 是明确的等待态，提供申请码复制与"查看最新结果"
  以及撤回二次确认，避免用户卡死。G5 从近乎空白的 WXML 重写为完整审批界面：申请卡展示申请码
  （可复制）、希望称谓与协作权限选择，同意前用 Dialog 复述"加入后可以看到什么"，处理中整张卡
  禁用，失败保留卡片并就地可重试，非管理员诚实降级。
  已知限制：`GET /families/current/requests` 只返回 pending，因此"已处理"分组用就地结果态
  2 秒后刷新替代；申请卡默认预选"可共同记录"，是否改为最小权限 viewer 待产品确认
  （Spec 的 `Q-002`）。320×568 / 430×932、真实微信双账号与真机仍为 `NOT_RUN`。
