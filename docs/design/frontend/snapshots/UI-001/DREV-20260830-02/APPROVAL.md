# UI-001 — DREV-20260830-02 Approval Snapshot

- UI ID: UI-001
- Design Revision: DREV-20260830-02
- Task Spec path and revision: `specs/completed/BUG-002-SETTINGS-CONFIG-AND-COPY.md` / `BUG-SPEC-20260830-02`
- Figma node URL(s): https://www.figma.com/design/FAyfmjNrA3btWztwyxI6Zj?node-id=0-1
- Approved by: 产品负责人（用户）
- Approved at: 2026-08-30
- Approval evidence: 用户提供设置页反馈并批准删除开发地址与修正文案；使用历史 FEAT-001 限时 Figma waiver
- Frontend baseline: FDB-20260830-01
- Engineering contract: FEC-20260830-01
- Waiver: `node-id=0-1` 只是文件根节点定位；本局部修订以设置页 DevTools 截图为批准证据，公开生产前必须补齐 Figma

## Approved scope

设置页删除开发服务地址表单；创建/保存孩子的用户文案替换为学习档案语义。

## Export manifest

| File | Viewport/state | Runtime | SHA-256 |
|---|---|---|---|
| `settings-devtools.jpg` | iPhone 12/13 Pro / Settings | WeChat DevTools 2.01.2510290 | `2cd9d0187dd64e96153413b1e509ba65e6d18704727e29563215237ae1070c74` |

## Integrity checklist

- [x] SHA-256 corresponds to retained export.
- [x] Screenshot contains no secret or real child data.
- [x] Waiver scope and expiry are explicit.
- [ ] Editable Figma node exists; required before public release.
