# UI-018 — 足迹文案精简

- Status: APPROVED / LOCAL_IMPLEMENTATION_VERIFYING
- Design Revision: DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02
- Task Spec: [SPEC-20261018-FOOTPRINTS-UI-COPY-01](../../../../../specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md)
- Baseline: FDB-20260913-04；Engineering: FEC-20261007-NATIVE-GEOMETRY-02，均已批准。
- Editable source: [index.html](index.html)；[导出工具](render.py)。无外部资源或业务请求。
- Evidence: [候选清单](../../snapshots/UI-018/DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02/APPROVAL.md)、[浏览器走查](render-audit.json)。
- Scope: 只精简FEAT-012的可见文案，不改变接口、状态迁移、字段必填、权限或存储规则。
- Approval: 产品负责人（用户），2026-10-23，选择标题切换后要求“完成这个功能的代码编写”，批准文案Spec01与本DREV02。当前源码验证见[实现证据](../../../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)，主Spec04仍VERIFYING。

## 界面约定

沿用DREV01的纸面、绿色、照片卡片与三视图结构。删除首页英文装饰语、每张卡片重复的“已确认”、操作教学和统计重算说明。标题与按钮直接表达对象和动作，如“核对照片”“手动记录”“修改照片信息”。不增加新的教程、折叠帮助或提示弹窗。

日常浏览只呈现照片、日期、地点、数量和可执行操作。未知日期/地点以字段状态表达；AI候选保留明确标记，不假装是已核实信息。草稿保留具体到期日期，批量编辑保留“留空项不修改”。删除保留“删除后无法恢复，其他照片保留”，放在照片之前以便小屏首屏可读。确认仍要求家长核对实际到访；原有可选AI与照片处理同意没有默认勾选或弱化。

导入时保留信息处理范围、浏览版相册、7天未确认清理及可选AI第三方处理目的。此设计曾将24小时清理/不延期等细则放在设置；该部分已由2026-10-24获批[DREV-20261024-FOOTPRINTS-MINIMAL-01](../DREV-20261024-FOOTPRINTS-MINIMAL-01/FRONTEND-SPEC.md)覆盖，设置仅开关与保存，规则仍在领域执行。回放“顺序示意”及地图位置示意合同继续有效；本源/导出冻结，不据删字宣称真实地图完成。

## 精确视口与状态

320×568、390×844、430×932，DPR=1；以下27态均导出，合计81张手机PNG，另附1600×1040桌面工作台。

`records / timeline / empty / import / consent / importing / review / batch / confirm / saved / playback / paused / lit / world / place / failed / unknown / denied / viewer / map-error / ai-settings / archived / photo-edit / photo-delete / expired / draft-delete / photo`

通过`index.html?capture=1&state=<state>`重现。`capture`只隐藏桌面评审栏，不隐藏手机内溢出。详细生产文案目标见[变更清单](COPY-CHANGES.md)。原生实现既有的清空日期/时刻、同日排序、全球总览和批准设计之间的差异仍由主Spec04跟踪，本次文案批准不代替这些设计及技术验收。

## 验证与限制

导出脚本检查页面JS错误、水平边界、44px操作区、固定操作栏可达性，并用实际点击走通导入、同意、核对、确认、回放、全球、逐张修改/删除、AI开关、归档草稿和到期边界。仅为离线HTML原型，不接真实相册、身份、EXIF、AI、后端或地图服务。

照片、孩子、日期和地点均为虚构示例，插画标签保留。刷新继续仅用本机虚构数据演示。HTML导出不能代替微信原生节点、真机和当前生产实现的验收。批准前不修改小程序生产文件；批准后须针对本次代码重新验证，不复用旧72份原生证据作为通过结论。

## 生命周期

DREV01/02源、PNG及批准清单保持冻结。DREV02已获批准并应用本地源码，仅接管本文案范围；记录入口由配套DREV-20261023-RECORD-TYPE-SWITCHER-01接管，旧设计其余约定继续适用。完整验收未闭环，未上传或上线。
