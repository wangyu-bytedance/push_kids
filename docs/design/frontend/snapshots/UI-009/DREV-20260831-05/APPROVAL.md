# UI-009 / DREV-20260831-05 approval manifest

- Status: `SUPERSEDED_BY_DREV-20260831-07`
- Scope: 家庭成员列表的 manager 与普通成员 content 状态
- Baseline: `FDB-20260830-01`
- Engineering contract: `FEC-20260830-01`
- Spec: `SPEC-20260831-07`
- Prototype: `docs/design/frontend/prototypes/DREV-20260831-05/index.html`
- Figma node: unavailable；Starter/View MCP 写入限额
- Waiver: not granted

## Snapshot matrix

| State | 320×568 | 390×844 | 430×932 |
|---|---|---|---|
| manager content | `manager-members-320x568.png` | `manager-members-390x844.png` | `manager-members-430x932.png` |
| member content | `member-view-320x568.png` | `member-view-390x844.png` | `member-view-430x932.png` |

## Verification evidence

- 浏览器返回的 6 个 viewport 均与目标 `innerWidth/innerHeight` 完全一致。
- 320×568 的成员列表可纵向滚动，不再被 Flex 压缩；底部设置 Tab 保持可达。
- 390×844 和 430×932 内容无需滚动即可看到主要成员信息和角色差异。
- 浏览器 console warning/error: none。
- 未运行微信开发者工具或真机；这不是生产 UI 证据。

## Approval requested

本轮只请求批准视觉方向、信息层级、成员透明度和 manager/member 操作差异。loading、empty、
error、权限调整、移除成员、退出和最后 manager 保护状态仍需补图。
