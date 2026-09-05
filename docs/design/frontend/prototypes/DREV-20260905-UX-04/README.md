# 家庭学习手册 · UX 04 评审原型

状态：设计草稿，尚未替换原生微信小程序。

- [可点击原型](index.html)
- [六页总览](board.html)
- [科目、活动与安排的二级交互](secondary-board.html)
- [二级交互总览截图](screenshots/secondary-overview.png)
- [二级交互三视口测量](screenshots/secondary-geometry.json)
- [设计合同](../../../../../specs/active/BUG-010-INTERACTION-DESIGN-V4-DRAFT.md)
- [浏览器总览截图](screenshots/overview.png)
- [历史记录示例](screenshots/history-demo-390.png)
- [家庭邀请成功态](screenshots/family-share-390.png)
- [家庭申请处理](screenshots/family-request-390.png)
- [布局测量](screenshots/geometry.json)

直接打开 index.html 即可使用；不需要安装依赖。桌面左侧可切换“当前截图状态 / 有记录示例 / 首次无配置 / 加载失败 / 加载中”。窄屏只展示应用预览。

可用 URL：`index.html?screen=record&tab=history&scenario=demo`、`index.html?screen=family&scenario=demo`。`embed=1` 为固定到浏览器视口的无评审侧栏版本。

二级交互：`index.html?embed=1&screen=settings&dialog=subject`，将 dialog 改为 activity 或 schedule 可查看活动目录与安排。

所有数据只保存在当前页面内存；刷新恢复场景初值。照片用本地 object URL 预览，不上传。模型整理与微信发送以说明层演示，不假装执行成功。示例中的人名、记录和申请码仅用于交互评审。

主要可操作路径：

- 切换五个 Tab、历史/新增、拍照/文字；输入、确认后展示演示记录。
- 切换周和日期、添加日程、字段校验、删除确认。
- 目录/自定义添加科目活动，已有项目检查，移出确认。
- 搜索与科目/来源筛选；查看示例学习详情。
- 7/30/100 天切换；100 天左右拖动或按钮翻页；点日期看详情。
- 生成邀请原位变分享、使邀请失效、申请码核对、角色单选、批准与拒绝、本人称谓编辑。

原型只覆盖代表性路径。生产已有的游标分页、原始材料签名访问、完整权限矩阵、失败恢复与重试仍应按当前 Feature/Spec 实现，不因原型简化而删除。

验证：HTML 18 个页面/视口组合无横向溢出；日历七天完整；主按钮可见；圆形无拉伸；100 天 30/30/30/10；记录确认与家庭申请代表流程通过 CUA。原生真机、数据库、模型、真实邀请没有在本设计任务中重测。
