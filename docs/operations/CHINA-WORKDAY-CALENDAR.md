# 中国大陆工作日数据维护

Owner：活动日程维护者；年度安排含义与产品验收由产品负责人确认。
范围：全国统一法定放假与调休，不包含学校、单位或地区自定义日历；放假跳过，不顺延。

当前本地实现 `SPEC-20261105-WORKDAY-02`，离线依赖 `chinesecalendar==1.11.0`（MIT），import名`chinese_calendar`。
锁定包与来源：[PyPI 1.11.0](https://pypi.org/project/chinesecalendar/1.11.0/)，发布于2025-11-04，覆盖2004–2026整年。运行时不联网、不上传孩子或家庭数据。
wheel SHA-256：`9479ead6010e6001472efdf97317699882c16604c7858ba26862dc9d36d56d46`，`uv.lock`绑定下载物。

2026权威核对：[国务院办公厅通知，国办发明电〔2025〕7号](https://big5.www.gov.cn/gate/big5/www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm)（2025-11-04）。
独立测试列出7段放假区间与6个周末上班日，核对2026全部365天；不从依赖常量生成期望。

每年国务院发布次年安排后，在次年首个工作日之前完成：

1. 查国务院正式通知，记录文号、发布日期、原文链接及所有放假/调休日期。复核依赖新版本、MIT许可、包哈希、完整年度覆盖；不得仅因库把最大年份改大就认定数据正确。
2. 形成维护Spec并审批；更新精确依赖版本和锁文件、纯策略revision及官方独立日期期望。覆盖边界从锁定数据读取，不能手改年份掩盖缺数据。
3. 执行纯策略全年边界测试，以及日程、活动、通知、混合旧规则、覆盖缺失测试；同时检查旧年度不退化。执行本仓库完整必需检查和独立Review。
4. 按`docs/deploy/README.md`发布后端，核对服务健康、包版本和不含个人信息的覆盖状态；若有客户端变化单独走上传/体验/审核/正式发布流程。数据依赖更新不需要客户端联网。

超出覆盖范围时：`ChinaWorkdayPolicy.classify`返回`unsupported`；工作日项不投影、不冲突、不入提醒队列，既有一次/每周安排照常。日程、今日及设置读取可返回`workday_calendar_warning`（静态code与coverage_end），提醒路径只记录安全码`workday_calendar_coverage_missing`，不记录日期、名字、家庭/孩子标识或payload。不能降级为周一至周五，也不能标记为已可靠判定“没有安排”。

当前前端按已批准[备注减法Spec01 / DREV03](../../specs/completed/FEAT-001-WORKDAY-COPY-CLEANUP.md)只在真实缺覆盖的日程结果/今日活动分区显示一次短状态；设置和日程编辑不显示覆盖年份或维护后果。年份、版本及维护责任保留在本runbook。[后续年份自动获取研究](../research/china-workday/20261105-automatic-updates.md)列出定时检查依赖、结构化快照与公告解析；尚未实施或配置任何同步任务。

本地演练命令：

```bash
uv run pytest tests/unit/test_china_workday_policy.py tests/integration/test_china_workday_schedules.py tests/integration/test_china_workday_notifications.py -q
```

2026-11-05演练包含2026-12-31边界和2027-01-01/01-04未覆盖态：策略拒绝猜测、日程警告、通知零入队；不修改系统时钟、不更新真实数据。最终运行结果与版本绑定在工作日任务EVD，单测不替代云端演练。库年限扩展后必须相应更新本段与测试，不能保留过时年限。

迁移为`20261105_0026`，两张表新增false默认的workday_only。已有工作日行时禁止降级Schema或回滚到不理解该字段的旧后端；使用支持字段的forward fix。备份和恢复依既有发布手册，不在应用启动自动执行MySQL DDL。
