# 2026-10-13 前后端发布差异与候选清单

- Status: FRONTEND_0.1.14_DEVELOPMENT_UPLOADED / COMPAT_BACKEND_029_NORMAL_PENDING_TRAFFIC / DAILY_TASK_BACKEND_NOT_DEPLOYED
- Request: 用户要求整理Git工程与当前发布版本差异，准备前后端发布。
- Release engineering commit: 898aa4b；生产源码与314150f一致。
- Frozen business candidate: `314150f`（背景/每日任务9f77774 + 已批准报表提交314150f）；后续设计脚本修复不改变生产源码。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`；服务`flask-ik19`；端口8000，PUBLIC关闭。
- 报表布局已纳入冻结前端0.1.14并完成开发上传。用户已授权后端部署及兼容过渡方案；本报告记录各阶段实际结果，数据库仍0018，兼容029已normal但流量尚未确认，每日任务新版未部署。

## 1. 基线与可信范围

| 发布物 | 可确认的基线 | 尚待确认 |
|---|---|---|
| 前端 | 历史开发版本0.1.13，源码`b2f0aa28e66ce16666fbed50944ad5918085de38`；当前0.1.14已开发上传 | 用户确认0.1.13未正式发布；0.1.14也未设置体验/审核/正式版 |
| 后端 | 历史用户确认线上028；2026-10-13 wxcloud只读version:list确认028 normal，service:list确认服务normal/PUBLIC关闭 | CLI不含源码commit及流量比例，无法证明028对应哪个Git树；需要控制台构建记录或来源manifest |
| 数据库 | 本次安全连接只读确认current为20261007_0018；本地head及每日任务新版启动要求均20261012_0019 | 生产升级尚未执行；需兼容029接管并核验后才迁移 |

后端比较使用可追溯的最终0018候选源码`8052419d37503f7597995a87f1bfa84cfb953e34`；此提交与前端0.1.13源码基线b2f0aa28的整个apps/api无差异（git diff --quiet退出0）。**这不是已证明的028→候选精确diff**；确认028源码后须重做差异核对，若不等于该API树，发布范围可能扩大。

## 2. 已提交前端差异：0.1.13 → 9f77774

21文件，343行新增、63行删除，加6张本地透明PNG；业务提交f804400和9f77774。

| 区域 | 发布后行为 | 后端依赖 |
|---|---|---|
| 设置 | 新每日任务配置、预设/自定义/编辑/删除，目标分钟；任务卡移至课外活动后，同款列表 | 新daily-tasks API，必须先发布后端和0019 |
| 今日 | 每日任务当天完成/撤销；复习/任务/学习记录/活动按完整计数默认展开或收起 | dashboard新daily_tasks、activity_remaining_count及完成事实 |
| 记录/日程 | 纸面渐变、书本/相机/台历插画及失败回退 | 无新API依赖 |
| 设置/报表 | 科目/活动/出行不同插画，报表成长记录及统一卡片背景，失败仅移除装饰 | 背景不改变既有API/权限 |
| 资源 | 六PNG共307253字节，RGBA透明通道；本地加载 | 无远程依赖 |

准确源码补丁（含二进制资源）位于忽略目录`dist/release-diff-20261013/frontend-0.1.13-to-9f77774.patch`；包含报表的最终补丁为frontend-0.1.13-to-final.patch。0.1.14实际开发上传结果见§8，下一候选0.1.15。

## 3. 后端源码差异：可追溯0018候选 → 9f77774

11文件，484新增、2删除；全部来自f804400。

- 新增`daily_tasks/{router,schemas,service,__init__}.py`，bootstrap注册路由；名称1～30字符、分钟1～180、最多20配置、家庭/孩子边界、manager/editor写入、viewer只读、幂等当天完成/撤销。
- `persistence/models.py`新增配置和完成快照模型；`data_management/worker.py`接入孩子/家庭永久删除清理。
- `reporting/service.py`为dashboard增加daily_tasks和活动剩余计数；`activities/service.py`按真实活动记录判断完成，不按结束时间推断。
- `platform/database.py`要求Schema由0018提升到0019；新增`apps/api/migrations/versions/20261012_0019_daily_tasks.py`。
- 无新增Ark/provider、身份链路、媒体owner、运行时密钥变量或Docker依赖变更。

新增接口前缀`/api/v1/children/{child_id}/daily-tasks`：GET/POST配置列表，PATCH/DELETE `/{task_id}`，GET `/today`，PUT `/{task_id}/today-completion`。完整差异见`dist/release-diff-20261013/backend-source-0018-to-9f77774.patch`。

## 4. 数据库与双版本兼容

0019仅新增daily_tasks、daily_task_completions两表，两个tenant-leading索引，完成事实唯一键family/child/task/day；不回填或修改旧行。无数据时允许降级，有任务/完成事实时拒绝丢表。

**发布顺序必须是迁移与兼容旧版核验 → 新后端灰度/业务smoke → 流量核对 → 新前端上传/体验验收。** 当前新版服务启动严格要求0019，不能在0018直接启动。旧后端是否接受0019需要按028实际代码验证，不能由“只新增表”推出可回退。若旧版严格要求0018，应先生成/验收允许0018/0019的兼容过渡包，再迁移。

用户明确要求本次不新增备份，按其指示执行，不声称存在本次恢复点。真实MySQL5.7迁移及兼容过渡服务的读写/Schema白名单验证已通过，云端验收继续进行。回滚保留新表和完成事实，不在事故中破坏性downgrade；拟用接受0018/0019的029作回退点，须先完成云端验证，不能指定未经验证的028可回退。

## 5. 未提交的额外候选

生产文件6个：review-inventory/index.js、index.wxss；records/history.wxml；reports/index.wxml、index.wxss；review-inventory/content.wxml。内容为历史/计划独立卡片展开、日期分隔列表、明确调整入口、顶部与底部收起。另有相应Spec/Design/测试/证据和文档改动。

用户本次已明确批准包含此组，已独立提交314150f并冻结上传；其提交前的源码补丁单独保存。报表证据记录三视口36态数字几何通过。其他设置候选01～05仅作为历史设计证据归档，不是额外已实现功能，不纳入生产源码。活动工作区不直接上传。

报表组已提交为314150f，6个生产文件现纳入候选；frontend-0.1.13-to-final.patch包含累计完整前端diff，backend不随报表提交变化。

## 6. 本次预检查与冻结产物

- 全套后端pytest：PASS，510 passed / 19 skipped / 62 warnings，46.50秒；跳过项包含未配置真实MySQL的测试。
- 当前工作区npm test：238/238 PASS；9f77774隔离提交内容235/235，记录见CARD-BACKGROUNDS-20261013.md。
- Mypy API：PASS，103模块；Ruff check/format API：PASS，123文件格式通过。
- 全仓Ruff及format：最终PASS，489文件已格式化。首次268项问题位于10个设计render.py；已修复导入、显式zip截断语义、局部绑定、lambda定义、格式与长字符串。长字符串拆分逐文件AST等价核验；未重新生成或改变已批准SVG/HTML/PNG及其hash。已批准核心两Design manifest与当前设计政策重验PASS。
- architecture/miniapp/current-design-policy：PASS；16pages，source_bytes1056728。核心前端样式的原生完整状态/真机验收仍待补。
- 已有工作区CLI preview：PASS，1017670字节；其中包含未提交报表改动，**不等于9f77774冻结前端包**。重新确定候选后应重编译。
- 后端最小白名单冻结目录`dist/release-candidate-20261013-9f77774`：107文件，1239519字节；逐项文件hash与9f77774 Git blob一致。
- release-manifest.json SHA256：`08593ed62ae10eb56e3f8db1acce13d07fedaa37e3576143cb39b87a6cbe1af4`。生成器拒绝环境文件/秘密及非白名单；该包只含运行应用，**数据库migration为独立发布物，不在应用目录内执行升级**。
- 真实MySQL5.7新库/升级/旧新版读写/并发、生产Schema current、容器build/nonroot/SIGTERM/ready、真实小程序新API smoke：本次NOT_RUN，待发布阶段执行。
- 本机Docker daemon未运行，且测试/生产MySQL环境变量均未配置；没有读取或输出任何凭据。不能将SQLite的510通过视为MySQL门禁通过。需由管理员提供已批准的受控运行环境，凭据留在环境/秘密存储，不进入聊天。

## 7. 当前下一步

- 用户补充确认：纳入未提交报表布局；前端0.1.13未正式发布，授权上传0.1.14而非正式发布。后端028来源与0019兼容性仍需独立核实。

1. 等待兼容029 normal，核对云端健康/业务，管理员按已批准方案确认兼容版本承载流量。
2. 使用既有受控迁移账号升级0019，核对current/check及两表；本次新增备份按用户指示跳过。
3. 从已冻结每日任务包创建新版灰度，验证每日任务和既有主流程，再确认流量；PUBLIC保持关闭。
4. 前端0.1.14已开发上传；前后端稳定后管理员选体验版并完成iOS/Android验收，再人工提审/正式发布。

## 8. 0.1.14开发上传实际结果

- 用户明确“没有发布，但不影响 你可以上传14版本”，授权开发版本阶段上传；本次先暂存前端供后端稳定后体验验收，不宣称已满足前后端联调或正式上线。
- 来源：314150f冻结源码，139个小程序文件逐字节对比Git通过；898aa4b只改设计工具和发布记录，不改生产源码。useCloud=true、真实AppID、目标env/service、urlCheck=true均核对；CLI islogin返回login=true。
- CLI upload成功，0.1.14，描述“新增每日任务和今日折叠，统一卡片插画，优化报表历史与计划布局”，TOTAL=1017762字节（993.9KB）。成功后版本工具bump至0.1.14，下次候选0.1.15。
- 前端0.1.13为历史开发上传基线、并未正式发布。0.1.14未设置体验版/审核/正式版；新每日任务尚不能宣称在线可用，需要先完成新后端0019迁移与API业务smoke。
- 本节记录上传当时状态：当时未迁移、未部署、未切流。此后用户授权后端部署并跳过新增备份，实际进展见§9和§10；不再将备份/连接准备视为当前阻塞。
- Feature/UI发布事实已同步，相关Spec保留VERIFYING于specs/active/，不是验收完成或DONE。

## 9. 用户要求部署后端后的复核

- 用户明确授权部署后端；复核源码HEAD为ca413517628dc16af69fef0fbe6cba0753f0ae52，未提交文档治理改动不进入冻结应用包。
- 实际重新执行wxcloud version:list/service:list：最新可见028为normal，服务normal，PUBLIC关闭；未创建新版本或调整流量。
- 实际重新执行Alembic heads：20261012_0019。生产current仍未读取。
- 实际检查本机：Docker daemon不可连接；MySQL连接和测试数据库环境变量均未配置（只检查存在性，未读取或输出秘密）。真实MySQL迁移/兼容与容器门禁仍NOT_RUN。
- 用户随后明确“不需要备份直接发布即可”，本次新增备份按用户指示跳过，未宣称备份存在或恢复演练通过。
- 找到既有.env中MYSQL_ADMIN_*安全配置；其地址与用户提供的目标匹配。进程内读取并只读连接生产，未回显凭据：MySQL 5.7.18-cynos-2.1.14-log，current为20261007_0018，两张daily任务表不存在。生产尚未迁移。
- 启动Docker后，冻结候选本地构建PASS；隔离本地容器UID10001、live/ready均成功、SIGTERM退出0/OOM=false。此为本地SQLite容器验证，不冒充生产链路证据。云托管dryRun打包成功，不创建云端版本。
- 隔离MySQL5.7.44首次使用默认排序规则触发历史0003迁移collation失败；清理本次测试容器并显式utf8mb4_unicode_ci重建后，base→0018→0019成功，alembic check无差异。早期未就绪连接失败亦已重试成功；没有在失败的部分Schema上继续升级生产。
- 旧源码严格要求0018，发布过渡兼容版本的额外代码修改已形成SPEC-20261013-DAILY-TASK-RELEASE-COMPAT-01（specs/active/BUG-20261013-DAILY-TASK-RELEASE-COMPATIBILITY.md）；用户2026-10-13明确批准，现为VERIFYING。备份不再是阻塞项；过渡029已创建，新版未部署，生产仍0018。
- 隔离MySQL专项pytest：11 passed / 1 warning，7.26秒（test_mysql_runtime、test_review_schedule_mysql、test_staged_mysql）。另外直接使用每日任务服务和合成家庭验证CRUD、重复完成幂等、编辑后完成快照保留、跨家庭拒绝、撤销、删除与清理PASS。没有操作生产儿童数据；证据不替代真实小程序云链路验收。

## 10. 已批准兼容过渡版本029

- 源码8052419d37503f7597995a87f1bfa84cfb953e34，仅将Database.verify_cloud_schema有限白名单改为0018/0019；活动仓库每日任务源码仍只接受0019。不含每日任务路由、新表模型或默认数据写入。
- 可重放补丁deploy/cloudbase/schema-0018-0019-compat.patch，reverse --check PASS。冻结dist/release-compat-20261013-0018-0019，103文件，manifest SHA256 bd1c3432ac200596f43f65d95cd586916d10a7b7c69bbc8ca30324decf99c9f5；逐项Git差异、manifest哈希、实际安全配置值秘密扫描PASS。
- 隔离MySQL5.7.44接受0018/0019、拒绝未知Schema，旧模型CRUD与跨家庭读取拒绝PASS；变更文件Ruff check/format PASS。
- 容器build PASS，UID10001，隔离SQLite live/ready均200，SIGTERM退出0/OOM=false；云dryRun PASS。镜像本地manifest sha256 37ae0a82de7659a79503f3738b1165316cc1b972a5eb294ea20717f31caafcdf（不是云端镜像摘要）。
- CLI确认表逐项匹配AppID/env/service/GRAY/Dockerfile/目标./8000，备注push-kids-20261013-compat01-8052419-0018-0019；确认表核对后输入yes，未使用noConfirm。detach返回部署请求成功；只读version:list确认029于2026-10-13 13:34:43创建，13:37:38达到normal，尚未宣称业务验收完成。
- 实际通过真实AppID callContainer读取当前路由live/ready均200；CLI无流量字段，此检查尚不能归因于029。服务normal、PUBLIC关闭；生产仍0018，未迁移、未确认029流量接管。
- 当前人工操作：在029发布单中将当前开发者配置为灰度测试用户，确认请求命中029，完成该版本健康与旧业务smoke后由管理员确认029接管流量。未确认前不升级生产0019；不得把normal或当前路由200当作029已承载线上流量。
