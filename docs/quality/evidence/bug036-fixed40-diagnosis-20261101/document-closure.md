# 固定40诊断与Spec04设计闭合

- 范围：诊断及待批准方案；没有生产/测试代码修改，没有Spec04实现或云交付。
- EVD：[诊断证据](../../../../specs/evidence/EVD-20261101-BUG036-FIXED40-DIAGNOSIS.md)；[Spec04](../../../../specs/completed/BUG-036-FIXED40-SUCCESS-REPAIR.md)READY_FOR_REVIEW/active。
- 原10/13的34/40与新12/15的33/40分别绑定其来源，原30+3内容FAIL保持；原40fixture/评分和所有失败分母不变。

| 核对对象 | 处理与当前事实 |
|---|---|
| FEAT-001 | 更新诊断结果及待批准入口；现有12/15产品合同保持，未把Spec04写成已实现 |
| Behavior Catalog / BHV-003 / BHV-032 | 核对原非空提案、最多三attempts、来源/缓存规则仍是当前代码；无新行为实现，不改正文 |
| Architecture | 核对原DTO/Provider/历史/缓存依赖保持；Architecture04只在待批准Spec，不改当前Architecture03 |
| UI-001 / FEC / DREV | 无前端代码、字段、布局、状态或资源改变；原设备/原生缺项保持，不新增通过结论 |
| Test Strategy | 更新独立新40 FAIL；原固定40阈值/评分/重试、旧34/40发布候选保持，待实施验证点只列于Spec04 |
| Spec / 索引 / 生命周期 | Spec04 READY_FOR_REVIEW/active；109completed/15active/13rejected，合计137；原父/缓存/内容VERIFYING，OPS BLOCKED |
| 内容ISS | 添加新诊断/失败及待批准修复入口；ISS仍open，不能由科目检查证明真实内容正确 |
| 发布Spec / 发布记录 | 添加后续独立诊断，不更改10/13 manifest、原34/40停止证据或039云状态；无新GRAY |
| EVD / manifest | 保留原六条诊断、完整新40安全阶段、原评分输出、153文件源码指纹；不含原SDK响应、儿童图或凭据 |

源码冻结时Feature正文为CONTENT-10，闭合时原任务已更新CONTENT-11；本任务保留其他会话正文，153份源码/fixture/工具逐项SHA与冻结值相同，变更0。
Spec04修改技能/来源/终态合同，必须批准后才写代码。静态设计自查完成范围/替代方案/预算/必要文件/验收/回滚，无占位字段；没有冒称独立代码Review。

实际闭合检查只核对本任务文档链接、目录数量、源SHA、证据SHA和`git diff --check`；没有本轮新实现，未重跑后端/Ruff/原生/云套件。记录于[closure-checks.json](closure-checks.json)。
