# System One Spec06 — 本地验证边界

- Spec：`BUG-SPEC-20261105-SYSTEM-ONE-06 / ARCH-20261105-SYSTEM-ONE-06`，已批准本地实施与真实同源测试。当前VERIFYING/active；被替代的05未交付实验CANCELLED/rejected，历史FAIL保留。
- 当前：原Pro生成后事务外执行Lite辅助验收；错误/疑点不丢产物，仍需家长确认。没有部署、上传、生产DDL/业务写入、Git提交或推送。
- `PUSH_KIDS_SYSTEM_ONE_ENABLED`本地默认true且仅代表辅助验收，关闭使用同一Pro生成。未修改云开关、Ark配置或其他运行凭据；旧部署配置中的同名开关必须在未来发布时核对语义。
- 本轮无新迁移。历史0027的`ix_knowledge_recent_subject`和0026链保留，但最近40运行查询已清退。应用Schema guard预期0027不是云Schema观测，也不授权生产迁移。
- 当前真实同期生成/43旧产物保持/检查器意见及家长内容review见[Spec06 EVD](../../../specs/evidence/EVD-20261105-BUG036-SYSTEMONE06.md)。Spec05的36/40、关系召回85%、37/45对43/45及命名FAIL仍为[旧证据](../../../specs/evidence/EVD-20261105-BUG036-SYSTEMONE05.md)，不能覆盖为当前通过。
- 当前90次结果：验收开启43/45＝95.6%，同期关闭42/45＝93.3%，43有效产物0丢弃；58既有产物/回归验收事实全保留。988 Python/56条件skip、MySQL12、前端359、静态及独立代码/文档Review通过；已知命名定位0/3漏检、人工内容PENDING、原生/真机NOT_RUN及既有SDK测试deadline首败保留。小样本回放不是线上成功率，也不直接放行发布。
- 旧server-owned覆盖判定/Review版本字段仅兼容已有草稿，无新生产者。评估家庭只读0份不证明全库清零；Owner为agent_processing/learning维护者，2026-11-12复查，全租户旧草稿清零并经兼容回归才可删除。旧MySQL13PASS只绑定Spec05；本轮实际MySQL/全库Schema漂移检查结果在新EVD单列，不借历史验证关闭索引漂移ISS。
- 恢复发布条件：绑定最终冻结源码，补齐质量/性能门禁、独立Review、全库Schema drift及发布手册其余要求，再取得具体版本的部署授权。没有请求本次用户操作平台，也没有到达人工发布门禁。
- 后续按[发布手册](../README.md)区分云部署、小程序开发上传、体验、审核和正式发布。原039/0.1.17不覆盖本增量。
