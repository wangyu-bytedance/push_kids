# 设置统一实测记录

- Spec / Design: SPEC-20261013-SETTINGS-CONSISTENCY-01 / DREV-20261013-SETTINGS-CONSISTENCY-01
- 用户2026-10-13“样式修改的 按这个方案实施”批准。实现VERIFYING；源码5837d59，前端0.1.15开发版本已上传（1027271字节），未体验/提审/正式发布。发布记录：docs/deploy/releases/20261013-settings-consistency-frontend.md。

在学科目改为活动同款单列图标/名称/状态/操作行，基础三科及移出限制不变，失用网格与独立列表样式已删除。每日任务仍在活动下方，独立书本/时钟装饰、整行编辑、底部添加候选半屏，移除常驻预设及独立编辑按钮。表单半屏保留原校验、删除确认、只读、防重、失败输入与切换重置。
阅读20、跳绳10、练字20、户外运动20分钟是候选预填，可修改，保存才写入；自定义入口保留。API/数据库/家庭范围不变，无新增共享抽象。

| 检查 | 结果 |
|---|---|
| npm test | PASS，239项，新增候选默认分钟/无写入/只读/容量/pending/离开重置 |
| npm run lint:miniapp | PASS |
| .venv/bin/python tools/validate_miniprogram.py | PASS，16页，1066517字节源包，小于1.5MiB |
| validate_design_evidence.py --check-current-policy --manifest 本DREV/APPROVAL.md | PASS，批准元数据与30张三视口快照hash |
| .venv/bin/python tools/check_architecture.py | PASS，checked=3 |
| git diff --check | PASS |
| 新PNG | PASS，8399字节，220×188 RGBA，透明alpha，低于40KiB |
| 430×932原生几何 | PASS，content/catalog/form/error/pending/readonly/no-art/long-name八态，保存/取消存在性及44px、横向溢出 |
| 430视觉 | 在学科目实际页面已查看；完整八态截图NOT_RUN，App.screenshot返回unimplemented |
| 320×568、390×844原生 | NOT_RUN，Mac锁屏，无法切换模拟器；合成设计不替代原生 |
| iOS/Android键盘、读屏、真机写操作 | NOT_RUN，无已连接真机 |

矩形证据：settings-consistency-20261013/*-430.json。合成数据，不含真实家庭身份、学习文本或媒体。模拟器验证不提交业务写入，结束恢复真实设置。后端测试/迁移N/A：本轮不改后端。

## 已授权test档案清理

用户确认“仅删除 test 孩子档案及其数据、配置”。当前小程序身份删除接口403；使用已有受控生产管理员连接，仅为精确匹配的孩子创建幂等child清理任务并标记deleting，由现有线上DataDeletionWorker完成媒体及数据库清理。
最终state=succeeded、error_code=null；孩子不存在，22张含child_id表的对应行数全部为0。其他孩子及所属家庭保留，未清理家庭账号/配置。没有输出/保存凭据。

本Spec因两档原生、完整截图及真机缺口保留VERIFYING。旧科目候选及任务视觉稿由新批准方案取代，不再实施旧候选。
