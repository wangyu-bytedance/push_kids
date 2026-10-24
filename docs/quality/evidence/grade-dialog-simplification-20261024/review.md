# 精简弹窗局部diff只读复核

- Reviewer: Codex，同一上下文的只读复核；不声称独立上下文评审。
- Scope: 原组件WXML/WXSS、coordinator两句文案、一个既有测试断言、离线prepare/geometry工具及相应文档。
- Result: 未发现本局部diff的Blocker/Major。原生/真机门禁单列，未完成门禁不代表整体DONE。

| Contract | Read-only finding | Evidence |
|---|---|---|
| 正常态减法 | 只保留一个带孩子名标题、picker、两个操作；旧说明节点及独占样式已删 | 组件WXML/WXSS；三尺寸51组最终原生呈现 |
| 默认/实际选择 | range/index/choose绑定保持；没有在picker变更时触发confirm | 原事件绑定和53项专项 |
| 显式确认/稍后 | 按钮仅改变顺序/短标签，原confirm/later事件与coordinator提交/advance不改 | 原组件JS未修改，真实桥接测试 |
| 失败恢复 | 仅缩短error文案；previous.selected_grade和retry payload保持 | 53项中保留草稿/同payload断言 |
| 保存/冲突/最新 | 保存禁用picker及两按钮；冲突禁止改级；latest分支无picker，继续原advance | WXML分支及原submit/refreshConflict |
| 并排尺寸 | 与批准HTML同为flex1:2和各侧12px padding；原生审计比较内容宽而非错误的外宽比 | 冻结源SHA不变；geometry工具 |
| 禁用可读性 | 目视发现平台禁用样式覆盖已修正；只提高原禁用规则优先级，最终原生颜色对比度≥4.5且opacity=1 | 三尺寸最终saving JSON/PNG；旧保存态保留于failed-initial-style |
| 无新数据边界 | 没有API/数据/权限/生命周期改变，真实错误保持静态短文本 | 本次实际3个生产文件的局部修改 |
| 取证安全 | 写入拒绝、合成数据；交互夹具仅在副本App插入创建原控制器入口，不替换生产处理器 | prepare工具，来源SHA清单 |
| 历史证据 | 新目录保存DREV02；原DREV01图片/source保持，只有允许的Superseded by变更 | 两份批准manifest校验通过 |

首次专项失败来自旧长文案断言，首次原生390请求实际处于320设备，被严格视口断言拒绝；这两次失败如实记录在实施证据。错误视口图片移至`failed-initial-viewport/`，不能纳入通过矩阵。后续工具增加开始前的实际视口检查，防止错误命名/覆盖证据。

三尺寸实际picker选四年级、失败两次重试及稍后/导航恢复已另行留证；最后仅禁用态样式优先级修正后重跑全部51组呈现，对应源码阶段在manifest分开绑定。最终共享工作区npm test 327项通过，较初轮317的新增10项来自其他任务。字体放大、读屏/焦点、真实iOS/Android、双家长旧端和完整原生业务端到端仍属独立门禁。局部只读复核不抵扣它们，不能用主任务独立review的PASS替代本diff验收。
