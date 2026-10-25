# 最新后端发布验证 — 2026-10-24

源码26714b9，运行/迁移冻结SHA见`push-kids-latest-freeze.json`。全量后端780 passed/40条件MySQL skip、前端332 passed及静态/规模/容器结果见[发布记录](../../../deploy/releases/20261024-latest-backend-test-deployment.md)。

MySQL一次性本地5.7.44：首次runner1049与attempt02的31 passed/1历史夹具失败保留；已批准测试隔离修订后attempt03永久替代13 passed、年级4 passed、base→head/current/check通过。合并未改的其他专项，全部32个MySQL用例有通过证据。SQLite年级/永久替代迁移4 passed，23 warnings，2.44s。Ruff/format、DAG150、git diff --check通过。

独立冻结迁移包0022→0025守恒、结构、9触发器及10k/50k新查询真实计划/预算通过，见`mysql-frozen-migration-and-scale.json`。后续CRUD修复仅改变启动权限检查，冻结02源码/两包manifest见`push-kids-latest-freeze-02.json`及source.patch；测试不进入运行包，不改生产保护，失败证据保留。

生产备份按用户确认，未独立恢复。`production-upgrade.json`记录0025迁移/admin结构与投影PASS；`cloud-036.json`与`runtime-account-schema-attempt02.json`保留036失败和实际CRUD可见trigger0、旧检查RuntimeError。首次内网不可达单列保留。修复后`runtime-account-schema-fixed-02.json`记录同实际CRUD默认校验PASS；`production-verify-fixed-02.json`记录admin9trigger严格工具PASS，无重复DDL。

CRUD Spec01/Architecture01已批准并实施。后端780 passed/46条件MySQL skip；attempt04今日立即claim失败保留，真实DATETIME round探针及批准T03相关测试最多2秒轮询后，attempt05全部26项通过（权限6/年级4/今日1/永久13/计划2）。Ruff/format740、mypy150、DAG150、冻结02源码/秘密、容器UID10001/live/ready200/SIGTERM4.808s/exit0及CLI dry-run通过；前端未改，先前332通过未冒充复跑。

`cloud-037.json`记录修复版本normal/100%/1、配置18项相等/PUBLIC关闭；用户人工接管后`cloud-smoke-037.json`记录真实本地客户端20项GET全部200（60–227ms），含最新年级/建议接口。`local-client.json`仅记录打开/配置，不单独当业务smoke。全量前定向smoke未运行，用户真实写入/设备/内容验收NOT_RUN。

`handoff-observation-037.json`记录239.699秒控制面观察跨度和末次live/ready再200（2735/108ms），旧035 0%/1、036失败0%/1未删除。`post-handoff-jobs-037.json`记录Schema0025、各主要待运行任务0及停用coverage queued23保留。均为离散只读采样，不声称完整监控窗口无瞬时错误。最终DAG150、diff空白检查及20份Markdown/261个本地链接检查通过。

历史测试Spec在completed/DONE；OPS与CRUD修复Spec在active/VERIFYING等待用户业务反馈，自动化与读取部署门禁已通过。Feature/Behavior/Architecture/UI/发布/Spec按实际diff同步，领域/API/UI合同不变，启动权限合同与双账号发布门禁已更新正文。未知云日志持久化探针被自动审批拒绝、未执行；安全只读固定字段/Schema探针获准完成，无额外日志授权需求。
