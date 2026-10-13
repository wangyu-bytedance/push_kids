# 2026-10-13 前后端发布差异与候选清单

- Status: PREPARING / FRONTEND_UPLOAD_AUTHORIZED / NOT_DEPLOYED
- Request: 用户要求整理Git工程与当前发布版本差异，准备前后端发布。
- Frozen business candidate: `314150f`（背景/每日任务9f77774 + 已批准报表提交314150f）；后续设计脚本修复不改变生产源码。
- Target: AppID `wx5d2e0014690bf285`；环境`prod-d2g14rwoycac6b45d`；服务`flask-ik19`；端口8000，PUBLIC关闭。
- 本报告不修改业务代码、不迁移生产、不部署、不上传前端；未提交报表改动尚未纳入冻结候选。

## 1. 基线与可信范围

| 发布物 | 可确认的基线 | 尚待确认 |
|---|---|---|
| 前端 | 开发版本0.1.13，源码`b2f0aa28e66ce16666fbed50944ad5918085de38`，上传门禁4268f4f之间小程序源码不变；记录见20261011-report-disclosures-frontend.md | 当前正式线上版本是否0.1.13；不能将“已上传”当作“正式发布” |
| 后端 | 历史用户确认线上028；2026-10-13 wxcloud只读version:list确认028 normal，service:list确认服务normal/PUBLIC关闭 | CLI不含源码commit及流量比例，无法证明028对应哪个Git树；需要控制台构建记录或来源manifest |
| 数据库 | 最近迁移记录20261007_0018；本地head及启动要求均20261012_0019 | 本次生产current尚未读取，不能把历史0018视为当前读取结果 |

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

准确源码补丁（含二进制资源）位于忽略目录`dist/release-diff-20261013/frontend-0.1.13-to-9f77774.patch`。前端下一上传候选号0.1.14；实际上传前需核对平台没有被其他任务占用该号。当前尚未上传。

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

BACKEND-RELEASE §4.2允许纯增量且真实MySQL新旧读写/回退验证完成后免本次新增备份；当前MySQL兼容证据不足，不满足豁免条件，不能直接迁移。回滚保留新表和完成事实，不在事故中破坏性downgrade；需要旧前端0.1.13和经验证接受0019的后端作为回退点，不能直接指定未经验证的028可回退。

## 5. 未提交的额外候选

生产文件6个：review-inventory/index.js、index.wxss；records/history.wxml；reports/index.wxml、index.wxss；review-inventory/content.wxml。内容为历史/计划独立卡片展开、日期分隔列表、明确调整入口、顶部与底部收起。另有相应Spec/Design/测试/证据和文档改动。

用户本次已明确批准包含此组，正在独立提交并重新冻结候选；其提交前的源码补丁单独保存。既有报告称236测试及三视口36态数字几何通过。其他设置候选01～05仅作为历史设计证据归档，不是额外已实现功能，不纳入生产源码。活动工作区仍不直接上传。

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

## 7. 下一步

- 用户补充确认：纳入未提交报表布局；前端0.1.13未正式发布，授权上传0.1.14而非正式发布。后端028来源与0019兼容性仍需独立核实。

1. 核对平台前端正式版本、028源码来源与流量、生产Schema；确认是否纳入未提交报表组。
2. 修复全仓Ruff门禁（设计生成器格式与静态问题，保留已批准SVG/HTML/export哈希），重跑；完成MySQL与旧版本兼容/回退验证。
3. 按纯增量条件判定备份；不满足则管理员确认备份及受控迁移runner，再发布兼容过渡服务和0019迁移。
4. 从冻结白名单候选构建新后端不可变灰度，确认normal及真实业务smoke，再经管理员确认流量；平台PUBLIC保持关闭。
5. 后端稳定后上传0.1.14候选开发版本，管理员选体验版并完成iOS/Android验收，再人工提审/正式发布。

当前实际状态：diff已整理、后端候选冻结；没有生产迁移、后端部署、前端上传或流量变化。
