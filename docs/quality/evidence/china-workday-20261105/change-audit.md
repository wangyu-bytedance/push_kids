# 本任务变更与文档闭合核对

作者自查，非新上下文独立R2。精确对象SHA见`source-sha256.json`；工作区其他BUG、档案、发布与治理修改保留，本任务没有删除生产路径、提交或发布。

| 对象（仓库相对路径） | 必要性/位置 | 合同与文档核对 |
|---|---|---|
| `pyproject.toml` / `uv.lock` | 必要；精确离线依赖，锁下载物 | 官方来源/许可/年度维护记录与实际1.11.0一致；无运行时API |
| `activities/workday.py` | 必要；activities拥有纯日期政策 | 年限从数据得到；不覆盖则unsupported，不能Mon–Fri回退 |
| `activities/schemas.py` | 必要；传输层输入合同 | 两类显式boolean及null/混合规则，PATCH最终合并目标再校验 |
| `activities/service.py` | 必要；既有用例owner | 日期/时段复用、old fingerprint、原子转换和容量；warning同可见科目作用域，保持bounded |
| `activities/router.py` | 必要；投影字段与warning | 不在router写日期政策；家庭/孩子boundary保持 |
| `persistence/models.py` | 必要；既有两表字段 | 默认false；不新增通用repeat框架 |
| `migrations/versions/20261105_0026_china_workday_schedules.py` | 必要；加法迁移 | 接0025，不改旧版本；true行禁止丢失模式降级 |
| `platform/database.py` | 必要；本地旧SQLite与云readiness | 本地旧表补字段、周slots回填排除工作日；云预期0026，未自动迁移MySQL |
| `reporting/service.py` | 必要；Today覆盖状态 | 读取ActivitiesService，不复制纯规则 |
| `notifications/planner.py`（未改） | 无需改；已消费公开occurrence | 实际队列测试验证假期/调休/去重，保留渠道/授权/发送边界 |
| `pages/settings/index.js` | 必要；表单状态和API映射 | 模式/草稿/统一时间、确认及generation防迟到，原星期逻辑保持 |
| `pages/settings/index.wxml` / `index.wxss` | 必要；批准DREV02呈现 | 原位三选项、真实picker/disabled/notice，最小44px/14px；不改全局tokens |
| `pages/calendar/index.js` | 必要；系列编辑与来源路由 | 原始event_date回填、workday payload、来源活动定位、warning缓存一致 |
| `pages/calendar/index.wxml` / `index.wxss` | 必要；批准DREV02呈现 | 三模式、起始日期/系列后果、错误与覆盖态；保留一次/每周 |
| `pages/today/index.js` / `index.wxml` | 必要；批准覆盖态 | 现有notice与activity区展开，不把未知标空；学习引导语义独立 |
| `tests/unit/test_china_workday_policy.py` | 必要；独立期望 | 从正式通知人工列出日期，测试不从库常量生成期望 |
| `tests/integration/test_china_workday_schedules.py` | 必要；真实API与消费路径 | 模式、隔离/冲突/旧PATCH/旧fingerprint/可见性、window与警告 |
| `tests/integration/test_china_workday_migration.py` | 必要；数据与启动 | 旧0025种子、false/true、保护降级和重复启动 |
| `tests/integration/test_china_workday_notifications.py` | 必要；真实planner而非同helper断言 | 合成授权/队列实际0/1/0，重复tick不多发；无微信发送 |
| `tests/integration/test_schema_readiness_mysql.py` | 必要；跟随中央expected head | 只将测试收尾恢复值改为Database.expected_cloud_revision，隔离MySQL未配置而跳过 |
| `tests/frontend/workday-schedules.test.js` | 必要；实际Page方法 | 10项双入口、草稿/转换、无权限/提交中、失败与缺覆盖态 |
| `tools/check_architecture.py` | 必要；现有纯政策门禁 | 新策略受纯import约束，不改变依赖规则方向 |
| `tools/prepare_workday_native.py` / `tools/workday_geometry.js` | 必要；只测隔离合成副本 | WXML/WXSS SHA一致、拒绝写入，真实原生节点而非HTML替代；首败保留 |
| DREV02源/导出/manifest | 必要；实现前设计门禁 | 60张HTML只作设计；批准后source/导出未改，不追认原生验收 |
| Feature001/003及索引、BHV009a、Architecture、UI001 | 必要；当前事实 | 已实施/已批准正文与实际diff一致；local0026和cloud0025区分，旧038/0.1.16当前说法更正为引用已记录039/0.1.17 |
| Spec/STATUS/README、Test strategy、runbook、release/EVD/ISS | 必要；事实/生命周期 | VERIFYING/active；全库Schema既有失败及截图/设备/Review缺项不写PASS，不因本地代码完成移completed |

删除/抽象检查：无可安全删除的本次生产路径；保留旧字段、星期slots、manual输入与既有日程/出行用途。未新增generic common/utils、反向域依赖、动态扩展点或运行时网络。查询保留既有20项时段容量、family/child范围与投影路径，新增warning读有SQL侧limit1。MySQL执行计划和并发实库验证尚未执行，不能以结构自查代替。

前端安全/性能/可访问性：客户端不携带日历数据集、不新增图片/库/日志，继续复用api身份注入；源体积1245796字节不是上传包大小。新控件声明button role/label、选中态与disabled，颜色以外有文字；原生44px/规则字号与横向边界已测，焦点/读屏/大字及真实设备仍待验。全局grade-confirmation旧selector警告仍在DevTools，不是本次工作日样式新增，未据此越界修改。
