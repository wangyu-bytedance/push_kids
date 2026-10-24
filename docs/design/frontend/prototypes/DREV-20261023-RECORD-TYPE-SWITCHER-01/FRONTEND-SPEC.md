# UI-001 / UI-018 — 记录标题类型切换

- Status: APPROVED / LOCAL_IMPLEMENTATION_VERIFYING。
- Design Revision: DREV-20261023-RECORD-TYPE-SWITCHER-01。
- Task / architecture: [入口Spec01](../../../../../specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md) / ARCH-20261023-RECORD-TYPE-SWITCHER-01。
- Approval: 产品负责人（用户），2026-10-23，选中“标题切换 · 推荐”后要求“完成这个功能的代码编写”。
- Baselines: FDB-20260913-04 / FEC-20261007-NATIVE-GEOMETRY-02，APPROVED。
- Source: [自包含HTML](index.html)，源及导出保持冻结；[有效批准清单](../../snapshots/UI-001/DREV-20261023-RECORD-TYPE-SWITCHER-01/APPROVAL-CORRECTED.md)。

保留知芽品牌栏，内容首行使用“学习记录 / 旅行日记”标题按钮，右侧为当前类型的孩子。点击标题打开底部两项菜单，当前项有勾选，遮罩/关闭可取消，不展示未实现类型。替代旧装饰标题卡和“孩子足迹”提示条，五个底部Tab保持；面板打开时隐藏导航防遮挡，关闭恢复。暖纸/松绿/原有图标、正文≥14px和操作≥44px，安全区留白沿用基线。

学习未提交内容跨类型保留，旅行孩子独立；上传中阻止离开，旅行未保存编辑须确认。第一次学习，普通Tab返回记住类型，明确学习意图通过同样保护切回。旅行三视图业务及精简文案见DREV-20261018-CHILD-PHOTO-FOOTPRINTS-02，旧独立足迹页保留。

精确设计矩阵：320×568、390×844、430×932，DPR1；learning、travel、picker、long四态共12张PNG。render-audit记录输入保留和Escape关闭菜单的交互结果。HTML不能替代原生节点、截图和真机；当前验证与未完成门禁见[本轮证据](../../../../quality/evidence/RECORD-TYPES-IMPLEMENTATION-20261023.md)。

批准清单首次把Frontend spec path误写为Task Spec路径，严格校验指出路径须位于本DREV的prototype目录。此次只补齐本设计规格及更正元数据清单，不改批准源、导出、DREV、范围或批准事实；旧清单保留不可变并用Superseded by指向更正清单。
