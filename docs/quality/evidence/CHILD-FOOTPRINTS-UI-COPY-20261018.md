# 足迹文案精简 — 候选验证记录（2026-10-18）

> 历史设计阶段证据。下文“待批准/生产未改/NOT_RUN”均指2026-10-18采集时点；Spec01与DREV02于2026-10-23获批并应用本地源码，当前代码与原生验证以[2026-10-23实现证据](RECORD-TYPES-IMPLEMENTATION-20261023.md)及UI-018为准。保留历史数值和结论，不作当前实现验收。

- Spec: [SPEC-20261018-FOOTPRINTS-UI-COPY-01](../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md)，READY_FOR_REVIEW。
- Design: DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02，AWAITING_APPROVAL / NOT_IMPLEMENTED。
- Subject: [隔离HTML](../../design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/index.html)。
- Subject SHA-256: `8c35c870ec78b8fc0da535e1f50e3d3104ada55949bee92a18e796101da5d986`。
- Source / PNG manifest: [候选清单](../../design/frontend/snapshots/UI-018/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/APPROVAL.md)。
- Raw browser audit: [render-audit.json](../../design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/render-audit.json)。

## 已执行

| 检查 | 结果 | 范围 |
|---|---|---|
| `TMPDIR=/private/tmp python3 docs/design/frontend/prototypes/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/render.py` | PASS | 最终源27态×320×568/390×844/430×932，共81张手机图+1张桌面图；页面JS/按钮及输入44px/水平边界/固定操作可达性；示例点击主流程 |
| `python3 tools/validate_design_evidence.py --allow-pending --manifest docs/design/frontend/snapshots/UI-018/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/APPROVAL.md` | PASS | 本候选源、PNG尺寸与SHA匹配；不是批准记录 |
| 相同工具严格验证旧DREV01清单 | PASS | 冻结源与PNG未改；旧源SHA仍`58982a8241094d1fbc6da97b6eb7d16a7f4bb046a7538b76c6c67eba893c896e` |
| `python3 tools/validate_design_evidence.py --check-current-policy` | PASS | 当前治理文本检查 |
| `git diff --check` | PASS | 当前工作区空白检查，不表示全部未提交修改属于本任务 |
| 候选/Feature/UI/发布记录中45个本地Markdown链接检查 | PASS | 目标均存在 |
| 按原native manifest重算14个源文件SHA | PASS | 生产足迹8文件、样式/插画与采集工具均未改变；不把旧原生结论迁移到本候选 |
| 目检320核对/授权/删除/未知态、390时间线及320回放 | PASS（设计范围） | 已删重复标题与来源行；授权目的可见；删除后果在照片前；unknown导出滚动到缺日期照片；示意标签保留 |
| 独立只读评审 | PASS（候选范围） | footprints_readonly_review确认新源、82图SHA/尺寸、81 DOM记录及27×3矩阵匹配；旧DREV01源/82图未改，13个生产前端文件未改；删除后果/unknown图可读。其余第14个采集工具亦由主执行者重算确认未改 |

执行过程中，默认沙箱无法启动Chrome；升级后曾因系统临时目录空间不足中断。最终使用`TMPDIR=/private/tmp`和最小磁盘缓存完整重跑成功；中断时或导出进行中的清单校验结果不作为最终证据。没有删除其他任务文件或既有证据。

## 文档与代码冲突核对

| 文档 | 核对及处理 |
|---|---|
| FEAT-012 | 增加文案候选，当前生产仍为原实现；不改变确认/AI/过期合同 |
| UI-018 / FRONTEND-DESIGN | Current仍DREV01，Proposed明确DREV02待批准；本轮候选不验收原设计差异 |
| Spec/索引 | 新Spec01留active/READY_FOR_REVIEW，主Spec04仍VERIFYING；没有误迁移或DONE |
| Behavior Catalog BHV-038/039/040 | 无行为改变，合同正文无需修改；授权、固定168h、家长确认与示意含义保留 |
| Architecture03 | 无边界、调用、依赖、共享抽象或扩展点变化，revision不变 |
| 发布记录 | 已登记仅设计候选，部署/上传/体验/审核/正式发布状态不变 |
| 测试策略及主实现证据 | 不更改其历史结果；本次HTML证据单列，未拿旧72份原生数据代验新稿 |

未发现本次候选与当前实现事实的冲突；原生和DREV01之间的既有差异仍开放，不由文案候选批准消除。

## 未执行及恢复条件

生产文案实施、`npm test`、小程序静态检查和本次三视口原生节点/真机均NOT_RUN：本具体Spec/DREV尚未批准且生产源码未改，须实施后重验。无后端或接口变动，不为离线文案候选重跑后端测试、数据库或云端验证。主功能的真实地图/AI/MySQL等门禁仍由Spec04跟踪。

待产品负责人批准Spec01和DREV02后实施；全部必需验收与文档闭环通过才将本Spec设DONE并迁移completed。当前没有部署、上传或发布授权。
