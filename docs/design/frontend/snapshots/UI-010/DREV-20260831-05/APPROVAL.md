# UI-010 / DREV-20260831-05 approval manifest

- Status: `SUPERSEDED_BY_DREV-20260831-06`
- Scope: 首次进入、分享、申请、等待和 manager 审批的核心旅程
- Baseline: `FDB-20260830-01`
- Engineering contract: `FEC-20260830-01`
- Spec: `SPEC-20260831-07`
- Prototype: `docs/design/frontend/prototypes/DREV-20260831-05/index.html`
- Figma node: unavailable；Starter/View MCP 写入限额
- Waiver: not granted

## Snapshot matrix

| State | 320×568 | 390×844 | 430×932 |
|---|---|---|---|
| first entry | `empty-320x568.png` | `empty-390x844.png` | `empty-430x932.png` |
| share | `share-320x568.png` | `share-390x844.png` | `share-430x932.png` |
| apply | `apply-320x568.png` | `apply-390x844.png` | `apply-430x932.png` |
| pending | `pending-320x568.png` | `pending-390x844.png` | `pending-430x932.png` |
| approve | `approve-320x568.png` | `approve-390x844.png` | `approve-430x932.png` |

## Verification evidence

- 浏览器返回的 15 个 viewport 均与目标 `innerWidth/innerHeight` 完全一致。
- 320×568 的 share/apply/pending/approve 内容可纵向滚动，关键操作可达。
- 390×844 和 430×932 展示完整主要旅程；每个状态同时用文字表达，不只依赖颜色。
- 分享预览没有成员名单、学习、照片或联系方式；审批明确分离关系和权限。
- 浏览器 console warning/error: none。
- 未运行微信开发者工具或真机；这不是生产 UI 证据。

## Approval requested

本轮只请求批准核心旅程和视觉方向。登录 loading/error、创建孩子、approved/rejected/expired/
revoked/duplicate、关系编辑和最后 manager 保护仍需补图后，才能批准完整实现门禁。
