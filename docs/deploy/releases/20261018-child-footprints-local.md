# 孩子照片足迹 — 本地交付状态（2026-10-18）

- Spec04 / Architecture03，本地实施获批；状态VERIFYING，见[证据](../../quality/evidence/CHILD-FOOTPRINTS-IMPLEMENTATION-20261018.md)。
- 源码：新增footprints API/五表/worker与小程序三视图；当前工作区未提交，包含另一个通知任务的原有修改，未冻结发布目录或镜像。
- 足迹迁移：`20261018_0021`，父为既有本地`20261017_0020`；这是2026-10-18历史head。当前工作区head为其他任务新增的`20261020_0022`，不得只迁移0021。SQLite增量/新库测试通过；生产MySQL未改，不把`create_all`当生产迁移。

| 阶段 | 状态 |
|---|---|
| 本地实现/确定性测试/独立代码review | 已执行，详见证据 |
| 隔离原生合成布局：24态×320/390/430 | 72份节点/PNG及SHA通过；[范围与差异](../../quality/evidence/child-footprints-20261018/native/README.md) |
| 2026-10-23入口/文案最终源码：29态×320/390/430 | 解锁后87份当前节点/PNG及SHA通过；[范围与隔离差异](../../quality/evidence/record-types-20261023/native/README.md)，非真机或完整设计验收 |
| 原生/真机、真实全球底图/供应商、MySQL5.7、设计差异验收 | 未完成 |
| 发布目录/镜像冻结、云端迁移、后端灰度/切流 | NOT_RUN |
| 小程序上传、体验、审核、正式发布 | NOT_RUN |

当前任务没有发布授权，不能从这份记录推导部署或素材外发授权。后续遵循[发布总手册](../README.md)、后端/数据库和前端playbook；0020/0021均未验证的目标环境要先审查完整迁移链，不能只验0021。回滚保留新增数据与清理兼容，非空迁移拒绝drop表。

2026-10-23后续本地增量：[标题入口Spec01](../../../specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md)与[文案精简Spec01](../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md)已获批准并实施，记录Tab内切换学习记录/旅行日记，旅行控制器复用并简化重复文案。当前自动化/隔离原生结果见[本轮证据](../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)，旧24态×3证据只作历史。未创建发布包/镜像、未上传或部署，各发布阶段保持NOT_RUN；完整真机、全球地图/供应商、MySQL等仍待验收。

## 后续运行合同

- `PUSH_KIDS_FOOTPRINT_MAP_KEY`由获批秘密配置注入，不写仓库/聊天；没有key则地图检索/反解/转换不补造值。全球覆盖/商用账号条款未验收。
- AI复用现有获批Ark运行配置和足迹专用store=false合同；没有可用服务/同意时保留人工路径，不算AI效果通过。worker跟随既有`PUSH_KIDS_RUN_WORKER`启停，readiness检查其存活/就绪。
- 私有对象/派生图需验证真实云owner、60秒预览和删除；只有元数据/派生成功才开始24h原件时钟；草稿上传成功起168h，不随重试续期。
- 运维可由当前家庭manager调用`GET /api/v1/footprints/cleanup?child_id=...`查看最多50条失败清理与total，再以当前version调用`POST /api/v1/footprints/photos/{id}/cleanup-retry?child_id=...&version=...`恢复。该接口只重排清理，不恢复已过期可读性。不得在日志记录响应中的孩子照片或位置。
- 小程序新增chooseLocation声明，公众平台实际隐私接口清单/同意声明须管理员在后续发布前核对；本轮未提交真实对外声明。
- 2026-10-18的24态三视口为历史证据；2026-10-23再次解锁后最终入口/文案29态×3共87份已验证，锁屏不再阻塞。重跑时为当前运行时使用新automation端口并校验实际尺寸。原有语音插件需在完整包恢复后复验，完整27态与真实交互仍待补；隔离副本/本地closed端口的结果不能冒充生产smoke。
