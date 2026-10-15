# 学科管理统一 — 2026-10-15本地验证

- Spec: [SPEC-20261014-SUBJECT-MANAGEMENT-01](../../../specs/active/FEAT-001-SUBJECT-MANAGEMENT-CONSISTENCY.md)，VERIFYING。
- Design: DREV-20261014-SUBJECT-MANAGEMENT-01；用户本聊天2026-10-15“落地和实现”批准。
- Base HEAD: 111ce1b；本次为未提交工作区diff。工作区存在其他任务修改，均保留，不计作本任务交付。
- Scope: settings/index.js、index.wxml、index.wxss；学科整行进入面板，面板底部移出并二次确认。active=false保持学习记录，服务端合同/权限/数据模型不变。

| 检查 | 结果 | 证据与限制 |
|---|---|---|
| npm test | PASS，244项 | 学科专项新增5项；基础/自定义确认、取消、加入/恢复、限制、重复操作、失败和跨孩子迟到响应 |
| npm run lint:miniapp | PASS | settings及前端测试 |
| python3 tools/validate_miniprogram.py | PASS | 16页，当前source_bytes=1070913；这是源码静态预算，不是上传包体 |
| python3 tools/check_architecture.py | PASS | checked=3；未改变模块边界与依赖方向 |
| python3 tools/validate_design_evidence.py --check-current-policy | PASS | 当前政策检查 |
| python3 tools/validate_design_evidence.py --manifest docs/design/frontend/snapshots/UI-001/DREV-20261014-SUBJECT-MANAGEMENT-01/VALIDATION.md | PASS | 27张PNG，三档九态，与原批准SVG哈希一致；原APPROVAL与SVG不重写 |
| git diff --check | PASS | 保留其他工作区修改 |
| 三档原生数字几何 | PASS，24组 | tools/subject_management_geometry.js；subject-management-20261015/*.json；320/390/430宽对应iPhone5、12/13、14 Pro Max，窗口高度扣除平台栏；行/关闭/操作触控≥44px、无横向溢出、操作处于视口内 |
| 原生确认弹窗、完整视觉截图 | NOT_RUN | 自动化几何只覆盖list/panel/unselected/readonly/restricted/pending/error/long-name，未覆盖原生modal几何及截图；设计PNG只为合成候选 |
| iOS/Android、读屏 | NOT_RUN | 未连接真机，不能声明通过 |
| 后端测试、MySQL、迁移 | N/A | 本次无服务端或数据库修改，复用原PATCH/POST；不复用历史后端测试作本轮PASS |
| 上传/体验/审核/正式发布 | NOT_RUN | 本次仅本地实现，无发布授权 |

原生脚本只设置合成示例页面数据，结束恢复原视图，不调用业务写API。首轮因沙箱端口拒绝连接，获本地自动化执行许可后连接；首轮缺少示例children导致节点缺失，补齐fixture后上述24组通过。CLI启动会话不用于认证或绕过平台门禁。

uv命令未成功：默认缓存权限拒绝，切换到/private/tmp可写缓存后uv在macOS system-configuration出现NULL对象panic。系统Python执行相同三个纯脚本均通过，未将uv失败写成PASS。

## 文档与冲突核对

- Feature FEAT-001：合并本地学科面板、统一移出确认、范围及发布状态。
- UI-001：合并入口/面板及状态，替换“只有自定义项可移出”的冲突正文为基础三科可切换、其他项受canRemove限制。
- Behavior Catalog：BHV-036记录面板确认、记录保留、只读/防重/迟到合同。
- Architecture及constraints：无新增模块/共享抽象/依赖/API，无需事实修订；check_architecture通过。
- 旧设计APPROVAL及SVG批准后保持冻结；补充PNG与完整清单不改变设计内容。
- 发布README/FRONTEND-RELEASE核对：未上传、未产生新版本，不修改历史上传记录。
- Spec保留active/VERIFYING，完整原生视觉/确认与真机验收通过后才迁移completed，代码完成不等于验收完成。

本轮移除了toggleBaseLearning/removeLearning两个旧行操作路径及subject-action样式。风险主要为尚未完成的视觉、原生确认弹窗及真机/读屏验收；当前自动回归和三档原生数字几何未发现缺陷。
