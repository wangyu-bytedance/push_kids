# DREV07 — 设置页顶部切换六种界面风格

- Task: DESIGN-002-SPEC-07
- Architecture: ARCH-20261106-MINIAPP-THEMES-01
- Design: DREV-20261106-UI-CONSISTENCY-07
- Status: AWAITING_IMPLEMENTATION_APPROVAL
- 用户已确认入口位置与六主题视觉方向；新增选择器与实施机制待具体版本确认。
- 基线：FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，无预算豁免。

## 可评审内容

`source.html`是人工可编辑设计源；`build.py`将上轮五张插画和原始风格现有书本插画嵌入`index.html`，使其自包含、离线打开。没有生成新插画、修改旧图或增加外部服务。所有姓名、课程与时间均为合成示例。

原始及五种新风格的完整页面视觉仍对应DREV06和当前原生基线；本增量只批准“设置标题后、业务卡片前”的当前风格入口，以及六选一底部选择器。原始示例是保留现有气质的HTML演示，不是微信截图，也不是重做全部原始页面。

## 行为

1. 顶部入口显示“界面风格”和当前名称，含当前素材缩略图与箭头。
2. 面板使用当前主题底色/文字/按钮色，含六张预览卡，当前项有文字与勾选。六卡固定为原始、花园、星际、夜色、海洋、科技。
3. 点击候选只修改候选勾选；“使用这个风格”统一应用并关闭。当前项按钮为“正在使用”禁用。关闭、遮罩、返回均放弃候选。
4. 应用后入口名称、页头、卡片、按钮、默认图标和导航一致更新。成功提示短暂显示。HTML仅演示本页内存状态，**不持久化、不调用业务API、不证明小程序跨页已接入**。
5. `storage-error`是实际保存失败提示的设计状态：“当前风格已应用，本次未能记住，下次打开可能恢复原始风格。”生产发生条件、跨页一致与重启恢复由Spec07另验。
6. 未知自定义科目/活动复用当前主题固定图标，无生成或等待。示例“自然观察”用于表现回退；真实业务可自定义任意合法名称。
7. 面板内不展示token、图标回退等技术说明；卡片只用“纸雕花园与嫩芽”等风格描述。

## 尺寸与状态矩阵

| 主题 | ID | closed | picker | storage-error |
|---|---|---|---|---|
| 原始风格 | original | 三视口 | 三视口 | 三视口 |
| 成长花园 | garden | 三视口 | 三视口 | 三视口 |
| 星际探索 | space | 三视口 | 三视口 | 三视口 |
| 深海夜色 | midnight | 三视口 | 三视口 | 三视口 |
| 海洋风格 | ocean | 三视口 | 三视口 | 三视口 |
| 科技风格 | tech | 三视口 | 三视口 | 三视口 |

精确视口：320×568、390×844、430×932 CSS px，device scale=1；6×3×3=54张，再加一张六主题总览。单页通过URL参数`?theme=midnight&state=picker`打开；省略state为关闭态，未知theme回original。

44px交互触区，主题标题/正文使用系统字体，说明允许13px。小屏双列卡片缩略图降低高度，内部区域可滚动；关闭按钮和应用按钮不随卡片区滚出。native需保留真实safe-area与微信胶囊位置。本预览支持Escape、焦点留在面板和关闭返回入口，不能替代微信读屏/返回键/设备验证。

## 实施映射与保留业务

| 设计 | 生产目标 |
|---|---|
| 顶部theme-entry | settings在loading/empty/只读分支之外的本机偏好入口 |
| 六张choice与apply | components/theme-picker；列表由registry派生 |
| 页面/组件主题根 | presentation/theme适配器和语义样式 |
| 插画/图标 | 小型本地插画角色与共享theme-icon；不把本HTML或base64打包 |
| 保存失败notice | 有条件的真实失败结果，不能常驻防御性说明 |

本演示未重放全部设置表单、管理员权限或grade交互；实现保留全部当前字段/流程。DREV06 child-edit省略预算不构成删除批准。现有设置的工作日、逐星期时间、旅行/每日任务、清理确认、家长确认边界均不变。

## 生成与检查

```bash
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-07/build.py
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-07/verify.py
uv run python docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-07/finalize.py
```

`verify.py`只验证本地HTML的54组横向几何/触区、15项局部交互、控制台和外部请求，并与DREV06的355份apps源码SHA比对。`finalize.py`记录源和55张PNG的SHA、旧DREV完整性；批准后不重写冻结产物，任何可见改动建立新revision。

当前Playwright由系统python3环境提供；finalize按项目Python 3.11+环境执行（使用datetime.UTC）。系统3.9执行finalize会失败，不能把该失败当成完整性通过。

原生切换、持久化、设备、大字/读屏、生产对比度、资源压缩、包体增量与业务回归均为NOT_RUN。具体状态见本revision快照的RESULTS。
