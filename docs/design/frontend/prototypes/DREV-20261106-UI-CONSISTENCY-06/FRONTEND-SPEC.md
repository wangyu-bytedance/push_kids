# DREV06 — 五主题全界面评审

- Task Spec: DESIGN-002-SPEC-06
- Design Revision: DREV-20261106-UI-CONSISTENCY-06
- Status: READY_FOR_REVIEW / PRODUCTION_NOT_STARTED
- Authorization: 用户要求“按照以上方案生成6套的全部界面，其中原始的不需要生成了”。
- Scope: 成长花园、星际探索、深海夜色、海洋、科技共五套；原始风格不重绘。
- Matrix: 65个页面/关键状态 × 5主题 × 320×568、390×844、430×932，DPR=1。
- Entry: [交互预览](index.html)；[Spec06](../../../../../specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md)。

## 视觉与内容合同

页面以家长完成记录、核对和安排为主；五种视觉方向继承DREV05，采用清晰中文无衬线、相同操作顺序和可滚动内容。主页面用完整插画页头，表单用较小页头；浮层遮罩下的内容不可操作。

| 主题 | 材质与图像 | 固定回退图标 |
|---|---|---|
| 成长花园 | 纸雕、嫩芽角色、奶油纸面、叶片局部细节 | 嫩芽 |
| 星际探索 | 星空观测站、机器人和望远镜、浅色舷窗内容面 | 带环小星球 |
| 深海夜色 | 深蓝绿海底、香槟细线、低调光线与轮廓 | 罗盘星 |
| 海洋风格 | 阳光浅海、读书鲸鱼、柔和波浪与贝壳 | 贝壳 |
| 科技风格 | 银白实验室、学习机器人、电路和模块边角 | 芯片 |

“思维拓展”代表未预置科目，直接使用本主题一个固定图标。没有运行时AI生成、逐课程补图或新增图标选择流程。五张静态插画来自内置image_gen，原图逐字节保存；[完整提示词](PROMPTS.md)和[来源/SHA](assets.json)可追溯。SVG功能图标为本地确定性图形。

所有姓名、日期、数字、照片和地图均为合成示例。学习草稿由家长确认；手动路径保留；AI不评分、不宣布掌握；复习日期遵循既有确定性规则。报表示例反馈2/4/0/3/5/1/3条与合计18条一致，图表显示日期、单位和可访问文本。

## 路由覆盖

以下是现有17条路由对应的设计场景；新增主题选择只是设置页设计提案，未新增生产路由。

| 当前路由 | 主要场景ID |
|---|---|
| pages/family-onboarding/index | family-onboarding, family-create |
| pages/today/index | today, review-feedback, empty, loading, notification-renew |
| pages/calendar/index | calendar, activity-schedule, travel-plan |
| pages/records/index | records, record-type, manual-input, voice-recording, processing, processing-failed |
| pages/footprints/index | travel, travel-map, travel-playback, travel-review, travel-upload, travel-upload-error, travel-edit, travel-confirm, travel-settings, travel-detail |
| pages/reports/index | reports, record-history |
| pages/review-inventory/index | review-inventory, review-plan, review-superseded |
| pages/settings/index | settings, settings-routines, subject-picker, subject-edit, daily-presets, daily-form, child-switch, theme-picker, saved, error, permission, unsaved |
| pages/submission/confirm | confirm, manual-confirm, confirm-error |
| pages/record-detail/index | record-detail, photo-preview |
| pages/activity/edit | activity |
| pages/child-edit/index | child, grade, child-archive, archive-list |
| pages/family-join/index | family-join, family-preview, join-pending |
| pages/family-members/index | family-members, family-role |
| pages/family-requests/index | family-requests |
| pages/delete-settings/index | delete-settings, delete-confirm, family-delete |
| pages/notifications/index | notifications, notifications-unavailable, channel-unavailable |

关键状态覆盖不等于全部角色×数据×网络×操作的排列组合。原生系统相册、权限弹窗和微信设置属于平台界面，不伪造为本产品设计。所有65场景与实际导出记录见[覆盖清单](../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06/coverage.json)。

## 相对旧底稿的内容校正

DREV02被冻结并作为组件底稿复用；本轮独立替换其记录页入口、复习目录、档案预算和旅行核对样例，使之对应当前UI合同。记录通过标题切换类型，照片保持单一入口；历史从报表进入；复习目录区分参与/已替代；孩子档案不出现可编辑复习预算；旅行保留导入、日期地点核对、家长确认。清理孩子与清空家庭分别核对不同名称。

这不把DREV02或DREV05追认为生产批准稿，也不把DREV06写成当前产品。

## 源、预览与重建

- `themes.css`：共享尺寸与五套主题规则。
- `screens.js`：五主题元数据、固定图标、65场景以及局部演示。
- `gallery.js`：主题/页面/尺寸导航和总览。
- `build.py`：从冻结的DREV02组件与本轮源码组装 `index.html`。
- `assets/`：五张原始插画，不加入小程序包。
- `export.py` / `verify.py`：浏览器导出、几何与交互检查。

`index.html`的页面预览、主题素材、图标与交互自包含；“全部页面总览”链接读取仓库中导出的PNG。离线评审资产大小不是生产包体，也没有实现主题资源下载或缓存服务。

```bash
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-06/build.py
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-06/export.py
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-06/verify.py
python3 docs/design/frontend/prototypes/DREV-20261106-UI-CONSISTENCY-06/finalize.py
```

## 验证与批准边界

检查范围包括三尺寸HTML节点横向边界、至少44px的控件范围、插画解码、页内滚动、主题切换、表单保留、键盘焦点、危险动作禁用及零外部请求。实际通过数及发现/修正记录见[RESULTS](../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06/RESULTS.md)，源/PNG摘要见[manifest](../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06/manifest.json)。

原生三视口节点、微信实际交互、真机、大字/完整读屏、完整色彩对比、真实照片权限、生产包体和缓存均NOT_RUN。当前只申请用户review视觉稿；没有生产代码、接口或发布动作。FDB/FEC/Feature/UI current-state与发布事实保持原权威。
