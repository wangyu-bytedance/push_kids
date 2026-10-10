# 设置页课外活动排序验证

- Date: 2026-10-10
- Spec revision: SPEC-20261010-ACTIVITY-WEEKDAY-ORDER-02
- Design revision: DREV-20261010-ACTIVITY-WEEKDAY-ORDER-01
- Approval: 用户“按照这个方案实现”；原UI不变，只排序。
- Subject: apps/miniprogram/pages/settings/index.js 的 activityOrderKey 及 addedActivities 派生路径。

## Verified

| Check | Result |
|---|---|
| node --test tests/frontend/activity-weekday-order.test.js | 6 passed |
| npm test | 213 passed，0 failed，0 skipped |
| npm run lint:miniapp | passed |
| .venv/bin/python tools/check_architecture.py | ARCHITECTURE_VALID checked=3 |
| .venv/bin/python tools/validate_miniprogram.py | MINIPROGRAM_VALID pages=16 source_bytes=713379 |
| .venv/bin/python tools/validate_design_evidence.py --check-current-policy | DESIGN_EVIDENCE_VALID |
| git diff --check | passed |
| settings/index.wxml及index.wxss diff | 空；布局、文案、图标及行结构未改 |

专项用例覆盖完整星期顺序、周三围棋09:00先于钢琴19:00、首时段优先、同键稳定、
缺失安排/时段/非法星期、缺失/非法时间、秒级时间、不修改输入、排序后点击正确对象、
安排刷新重排、加载错误保留列表、空态、学习列表不受影响、迟到响应不覆盖新孩子。
只在已有返回的活动列表上进行O(n log n)排序，每活动常数工作；无新增请求、依赖或持久化。
自查确认0是合法周一，时间缺失只影响同星期内部位置，不挤到下一星期或无星期组之后。

## Not run / release

- TP-004原生320×568、390×844、430×932截图及节点矩形：NOT_RUN。
  本机未发现默认微信自动化端口9420监听，连接尝试不可用；未拿HTML/SVG替代原生证据。
  只修改行顺序，但原生行读取、点击及长文本三视口验收仍待补充。
- 后端测试：NOT_RUN，本次无后端、API、排期、数据模型或数据库变更。
- 未上传或发布小程序；实施已完成，本Spec保持VERIFYING直到原生验收通过。
