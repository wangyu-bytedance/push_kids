# UI-010 — 家庭分享、申请与审批

- Status: `CURRENT_LOCAL / 390_NATIVE_CAPTURED / MATRIX_PENDING`
- Related Feature: `FEAT-002`
- Related Specs: `SPEC-20260831-10`; `BUG-SPEC-20260906-18`; `BUG-SPEC-20260913-19`
- Baseline: `FDB-20260906-02`
- Engineering contract: `FEC-20260906-04`
- Design revisions: `DREV-20260906-PKDS-01`（屏 A1–A4、G5）；`DREV-20260913-FAMILY-INVITE-CODE-01`（A3）
- Last reviewed artifact date: 2026-09-13
- Interactive artifacts: `docs/design/frontend/prototypes/DREV-20260831-08/index.html`;
  `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Current change snapshot manifest: `docs/design/frontend/snapshots/UI-010/DREV-20260913-FAMILY-INVITE-CODE-01/APPROVAL.md`
- Current change editable design source: `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Design evidence governance: `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`

> BUG-015 revision 19 与六位码输入 DREV 已获产品负责人批准并在本地实现；三视口仓库快照已通过
> manifest 校验。未部署，双账号审批、原生启动 smoke 与原生视口矩阵仍待补齐。

## Core journey

```text
未绑定家庭 → 创建家庭 → 进入家庭内空态 → 建立孩子档案
          ↘ 申请加入家庭 → 最小预览 → 申请加入 → 等待确认
manager → 邀请家人 ──────────────────────→ 确认关系与能力 → 加入家庭
```

分享入口只发起申请，不直接授权。申请人获批前不能看到学习、日程、照片或成员名单；manager
确认时选择最终关系，并在“只能查看/可以共同记录/设为家庭管理员”中选择加入后可以做什么。

## Review states

| State | Visible contract |
|---|---|
| loading | 普通启动先解析 `/me`，不提前进入今日或请求家庭业务数据 |
| unbound / first entry | “创建家庭”和“申请加入家庭”两个主路径；不把零孩子等同于未绑定家庭 |
| bootstrap error | 停留在独立错误态并允许重试，不显示未绑定家庭选择项 |
| share | manager 获得 24 小时六位家庭邀请码及微信邀请；明确最小披露和管理员确认 |
| manual code | 只接收六位数字，数字键盘，长度不足时禁用并就地提示；有效后进入同一最小预览 |
| apply | 家庭称呼、拟申请关系；说明关系不决定加入后可以做什么 |
| pending | 家庭、与孩子的关系、等待确认；允许查看最新结果和撤回 |
| bound（含零孩子） | 进入今日；零孩子由业务区既有空态承接 |
| approve | manager 确认最终关系与协作能力；同意/拒绝明确分层 |

## Interaction and safety contract

- 分享卡片和预览不展示学习记录、成员名单、照片或联系方式。
- 提交申请和审批均有 pending、防重复提交、可恢复错误及服务端最终授权。
- 申请前使用 manager 生成的六位“家庭邀请码”；申请创建后申请人与管理员显示同一六位“申请核验码”。
  两者时序和用途不同，管理员每次授权前确认核验码，处理时整张申请禁用。
- 一个邀请只允许批准一人；批准、撤销或到期会终结同邀请的其他待审批申请并释放申请人绑定。
- 有效邀请列表不返回或展示原始 token，原始 token 只在创建响应中用于一次微信分享。
- 手输家庭邀请码与微信分享 token 都进入同一服务端预览/申请授权边界；客户端不持久化凭证。
- 批准后显示审批人和审批时间；两名 manager 并发操作只产生一个终态。
- expired、revoked、rejected、approved、duplicate、401/403、loading/error、孩子信息表单、关系编辑
  和最后 manager 保护仍须在后续 review slice 补齐后，才能批准完整实现门禁。

## Visual and responsive contract

沿用 `FDB-20260830-01` 的暖纸色、墨绿色主操作、系统中文字体与单列卡片。评审矩阵为
320×568、390×844、430×932；小屏内容允许纵向滚动，主操作不得被永久裁切。没有外部图片、
字体、图标库或儿童内容进入原型。

## Approval status

本地前后端已实现上述合同并有 SQLite 集成测试；六位邀请码预览/申请受可信 actor 的更严格独立
进程内限流保护，原分享 token 继续兼容。
当前账号线上可回滚验证完成创建201、最小预览200、撤销204和撤销后预览410，证据未保存token；
线上旧后端尚无有效邀请GET（405），本地端点必须和前端一起发布。多实例共享限流、真实微信双账号、
320/430和 iOS/Android 仍是公开发布门禁。

## Change references

- 2026-09-13 — `BUG-SPEC-20260913-19 / DREV-20260913-FAMILY-INVITE-CODE-01`：A3 从长口令粘贴
  改为六位纯数字家庭邀请码输入，长度不足禁用“查看家庭”；分享 token 仍可直达相同预览。
  申请后的六位值统一改称“申请核验码”。候选 320×568、390×844、430×932 快照及 SHA-256
  manifest 已批准并通过校验；原生矩阵与真实双账号仍为 `NOT_RUN`。

- 2026-09-06 — `BUG-SPEC-20260906-18`（BUG-014）：普通启动以本页为家庭 bootstrap gate，按
  `/me` 的 unbound/pending/bound/error 状态分流；邀请分享继续直达 `family-join`，bound 且零孩子不回到
  创建家庭。修复只改变 app/page 生命周期编排与错误状态，不改变本页 WXML/WXSS。Node 生命周期及完整
  前端回归、lint、validator、架构检查、家庭 onboarding integration tests 已通过；DevTools/真机 smoke 未运行。
- 2026-09-06 — `SPEC-20260906-PKDS-01 / DREV-20260906-PKDS-01`（屏 A1–A4、G5）：首次进入、建档、
  口令加入、等待确认和加入申请审批按 PKDS-1.0 重做。A1 提供两条并列路径卡；A2 表单有吸底 CTA
  与缺项提示；A3 展示口令错误态与隐私说明；A4 是明确的等待态，提供申请码复制与"查看最新结果"
  以及撤回二次确认，避免用户卡死。G5 从近乎空白的 WXML 重写为完整审批界面：申请卡展示申请码
  （可复制）、希望称谓与协作权限选择，同意前用 Dialog 复述"加入后可以看到什么"，处理中整张卡
  禁用，失败保留卡片并就地可重试，非管理员诚实降级。
  已知限制：`GET /families/current/requests` 只返回 pending，因此"已处理"分组用就地结果态
  2 秒后刷新替代；申请卡默认预选"可共同记录"，是否改为最小权限 viewer 待产品确认
  （Spec 的 `Q-002`）。320×568 / 430×932、真实微信双账号与真机仍为 `NOT_RUN`。
