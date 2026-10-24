# BUG-031 — 足迹缩略图 MySQL5.7 回归证据

- Date: 2026-10-23；2026-10-24补齐容器与闭合验证
- Spec: [BUG-SPEC-20261023-FOOTPRINT-PREVIEW-MYSQL57-01](../../../specs/completed/BUG-031-FOOTPRINT-PREVIEW-MYSQL57.md)，用户明确批准后实施，当前DONE。
- Git baseline: `82ca52775bc948f2a963a8f4ed614322d8859de8`；完整业务工作区未提交，不能仅凭HEAD复现。
- Subject: `apps/api/src/push_kids/footprints/reads.py`；只将有界UNION的IN查询改为物化派生表JOIN，API/排序/分页/租户/状态边界不变。
- Subject SHA-256: `fe2a86300de22a12af39783e7baa34afc64bf27ddab403a5d6d057d20f101d0a`；回归文件SHA-256: `b5297c3f8eae5f1b2b2e91222b3226e0a1dd2ae456b95a0ab7b7021b916ddf22`。
- Runtime manifest: `001c2e0be2b6f0518b74248e2e2fc2dd54c8ddf100df3fc908732d3e7d67432e`，134文件/1406788字节。
- Migration manifest: `39aba303a370e8156fd61b730bb183d0367d8aba39b325bf47d12b0aa0eea31e`，157文件/1528565字节。
- Phase: 源码、数据库回归与容器门禁PASS，BUG-031已闭合；[发布记录](../../deploy/releases/20261023-fullstack-test-deployment.md)仍等待生产人工门禁，尚不代表部署成功。

## 重现与结果

所有数据均为合成。只连接本机MySQL5.7.44的随机临时库；没有生产数据写入、真实儿童照片或通知发送。

| 场景 | 旧候选 | 修复后最终冻结包 |
|---|---|---|
| 50000照片 / 1到访日 | 原预算通过 | MySQL0.3935s / peak5837733字节；SQLite0.0326s / peak5833258字节 |
| 50000照片 / 1000到访日 | 2.255s FAIL，缩略图SQL约2.106s | MySQL0.1724s / peak2510090字节；SQLite0.1040s / peak2434568字节 |
| 真实预览EXPLAIN | DEPENDENT SUBQUERY/UNION，外层child_id估算25000行 | 无DEPENDENT；每分支实际key=ix_footprint_photo_visit，type=ref或range；外层实际PRIMARY/eq_ref |

既有预算保持：首次时间线<500ms、最多5次查询、最多50到访×4预览、响应<512KiB，地图≤200簇/7查询/<256KiB，回放≤100点/5查询，内存峰值<16MiB。测试解释实际执行SQL及参数，不把possible_keys视作实际索引。

同时验证每到访精确前四张ordinal/id顺序，低ordinal的deleted或另一家庭照片不会进入预览/计数；下一页顺序无重叠，跨家庭访问被拒绝。防御夹具故意将其他家庭照片关联到可见visit，以检验读取边界，不代表业务允许创建该关联。

首次修复并行测试曾出现单到访0.543s，以及健康range访问被过窄ref断言拒绝；该次2 failed/29 passed已记录。未放宽500ms预算。后续修正执行计划断言、补齐边界用例，并从冻结包完整重跑获得上述31 passed；不把首次失败删改为通过。单次本地耗时不是生产p95承诺。

## 实际执行

- 完整后端：`pytest tests/unit tests/integration tests/contract -q` → **671 passed / 35 skipped / 86 warnings，92.98s**。普通套件未注入MySQL；下列独立门禁无skip。
- 冻结迁移包：本地MySQL5.7.44从base→0019→0022，current/check PASS，无新upgrade operations；完整迁移env.py及queue v1/v2依赖均取自冻结目录。
- 冻结生产源码执行六组MySQL专项＋`tests/performance/test_footprints_reads.py` → **31 passed**，含27项服务/并发/迁移及4项SQLite/MySQL规模分布；结束只删除本次创建的临时库。
- Ruff check、format check（628文件）、mypy（130源码）、architecture（4策略/130模块DAG）PASS。mypy仍提示既有未注解方法不检查函数体，未将此提示写成额外类型覆盖。
- 独立只读review另跑footprints integration **18 passed**及两文件Ruff/format PASS，并复核最终31项结果和291条文件SHA/当前源匹配，代码review **PASS**。修复位置/合同等价/必要性均通过；容器和人工运维门禁不在此PASS范围内。
- 新包逐文件SHA、源一致性及本机安全存储已有秘密值扫描PASS；dry-run PASS。生成ZIP移出发布目录，迁移测试生成的pycache已清理，两个包均无manifest外文件。

2026-10-24恢复执行后，原`/private/tmp/push-kids-release-20261023-*`临时日志已不存在；上述结果是2026-10-23实际执行并经独立复核后留下的摘要，不宣称原始日志仍可访问或本次重跑。原始日志回显自动审批被拒后，采用进程内白名单抽取，未绕过拒绝。

## 2026-10-24 容器闭合

重新启动本机Docker后发现最终tag已有镜像；从同一冻结目录执行标准`docker build --pull=false`成功，依赖层缓存，Dockerfile和lock未改。最终镜像ID为`sha256:ec384a3c9c4699aa1cba3b0398498ae6bee7cba82ccb5863bcce91f62b181045`，130份Python源码与manifest逐项一致。两个包291文件/当前源/已有秘密值扫描再次PASS；不带凭据的本地SQLite默认URL不归为秘密。镜像配置与history未含扫描中的真实秘密值，构建代理未持久化。

[持久化证据](fullstack-release-20261024/container.json)：网络none、文件系统只读、仅临时目录可写，使用合成SQLite和关闭的后台消费者；运行UID10001、8000端口live/ready各200、SIGTERM 0.414秒内退出0、OOM=false。本地完整真实AppID客户端同时恢复，旧031 live/ready各200。未使用生产配置或数据测试容器，未创建新云版本。

原源码/回归文件及两个manifest SHA均未变，不重复真实模型调用或把旧671/31项写成本次重跑。P01–P05已闭合，BUG Spec设DONE并迁至completed；产品和运维验收保持各自状态。

本轮归档后`git diff --check`、架构4策略/130模块DAG及当前设计证据校验再次PASS；11份闭合相关文档133个本地链接存在性通过，active旧路径已移除，completed目标存在。代码与当前Feature/Behavior/Architecture/UI/Spec/测试/发布正文逐项核对未留冲突；不更改批准设计快照。

## 文档与验收边界

FEAT-012、BHV-040、Architecture、UI-018、主Spec04和发布记录同步当前SQL/MySQL事实。模块/依赖/API/UI/Schema未变，不新增架构或设计revision。客户端来源未变，先前原生几何证据保留其原范围，不当作新数据库/真实相册/全球底图验收。

真实全球底图、照片owner/双账号、真机EXIF和AI地点效果仍开放；产品/入口/文案Spec仍VERIFYING。10-24用户指定同库升级顺序，10:55冻结0019→0022/current/check及结构/队列核验通过；035 normal后用户100%接管并删除034，11:01–11:03旧实例0、coverage=false；真实微信18项读取200、本地旅行入口加载通过。全量前定向检查未执行，见[OPS及发布记录](../../deploy/releases/20261023-fullstack-test-deployment.md)。BUG-031 DONE仅代表自身P01–P05，不代验完整产品。
