# FEAT-011 — 本地交付状态（不是发布记录）

- Date: 2026-10-17
- Spec: SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01，active / VERIFYING
- Architecture: ARCH-20261017-NOTIFICATION-AUTO-RENEWAL-01
- Design: DREV-20261017-NOTIFICATION-AUTO-RENEWAL-01，用户“按照这个方案落地”批准
- Implementation: LOCAL_IMPLEMENTED
- Verification: AUTOMATED_PASS / DEVICE_AND_INDEPENDENT_REVIEW_PENDING
- Release: NOT_STARTED
- Evidence: [实现与验收缺口](../../quality/evidence/NOTIFICATION-AUTO-RENEWAL-IMPLEMENTATION-20261017.md)

本轮仅本地代码、自动化和隔离验收。没有git提交/推送、生产Schema迁移、云端新版本或流量调整，
没有小程序上传、体验版、提审或正式发布；未调用真实微信授权或发送通知。
历史031及0F58单条收件不作为本功能发布/验收证据。

## Future release constraints

未来授权发布后按[发布手册](../README.md)执行：生产备份、扩展Schema至0020、兼容后端灰度，
再上传新客户端并完成体验及真机，最后经过平台人工发布门禁。旧客户端subscriptions合同保留；
新客户端依赖新增API，不能先于兼容后端发布。

默认unseen，不自动为既有成员开启，不补算历史完成，不补发旧通知。
回退客户端/后端保留新增表和实际授权事实；新表有数据时迁移拒绝破坏性downgrade。
任何重复+1、越权或授权阻断复习都阻断发布，不能以HTML/模拟回调或历史通知成功代验。
