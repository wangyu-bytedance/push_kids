# BUG-036 内容Spec03 Discovery证据

- Date: 2026-11-01。
- Scope: 当前源码、批准合同与历史安全报告的只读检查；未生产/测试实现、未调用模型、未重新获取原图、未读写生产DB。
- Request: “修复全部未通过样本”；[候选Spec03](../completed/BUG-036-SOURCE-GROUNDED-CONTENT-REPAIR.md)等待新合同批准。
- Current source: `staged-20261101-10` / `child-aware-history-agent-20261031-13`；缓存Spec02已批准并本地实现，完整内容报告仍绑定09/13。

## 静态确认

通过AST读取`StagedPipeline._call`的第6个位置参数（images，0-based索引5），及直接阅读`review_quality`、`validate_merge`、最终装配：

| 阶段 / 当前行号 | images实际参数 | 文本输入关键字段 |
|---|---|---|
| merge / 368 | `[]` | candidates |
| review / 398 | `[]` | candidates、final_items、final_omissions及可选previous_review |
| merge-correction / 446 | `[]` | candidates、previous_items、previous_omissions、review_issues |
| extract / 248 | 当前原图 | subjects、grade、parent_text、materials |
| group / 303 | 联合原图 | 上述字段及required_materials、excerpts |
| match / 593 | `[]` | 当前facts及历史options |
| reuse / 689 | `[]` | 当前facts及实际历史名 |

Review没有summary/uncertainties；直接候选evidence以`current_facts`进入历史并在最终装配复制为ModelEvidenceReference，confidence取提取最小值。validate_merge拒绝与候选不同subject；这一层没有原图重判能力。成员覆盖是编号账本，不是视觉对象完整性证明。

一次初始AST检查错误选择第7位置参数，显示deadline而非images；该检查不作为证据。随后修正为index5，结果与源码逐段阅读一致，没有通过错误工具输出断言缺口。

最新完整30安全报告解析：26产出，C1–C6通过12，含输出合同完整PASS10、FAIL15、NO_PROPOSAL3、NEEDS_PARENT_VERIFICATION1、NEEDS_MORE_MATERIAL1；原六PASS中18/25回退。case11补材料是正确拒绝，仍在30分母。

补充3份安全报告：1PASS/1FAIL/1NO_OUTPUT；词表name长度及韵母/备注教学角色反证属于待修复，原缓存机制结果不证明内容通过。

## 冻结来源SHA-256

| 当前文件 | SHA-256 |
|---|---|
| stage_contracts.py | `056cd0eb6bde33429c6eb56c9f9b11c7a96237671a6378046490ca2c18df6e6a` |
| pipeline.py | `d14bb5682a75d9bd734e039f110b5a46de0c081b6b3537c95307f5a666b3c4ac` |
| prompt.py | `61152c25593aee2665a6ae59bb489e90b9b031bc48df69a24892e82fea242823` |
| stage_provider.py | `541aa016674b35e215eee052f23bc04e00d09164995f9e169d15c65fedc125e1` |
| checkpoints.py | `45a0ce6401bc2780bf849fa7acec70a938f24fa77fde36c02afedae909e18e80` |
| worker.py | `32f8cb9f7b4a7e181ae4227bbffadfa5f2c582c4cfabf02ae8528f7172cbc2b8` |
| learning/service.py | `c0d3e595a7b9b6b947b5ad1bf38931d2988a484e985c959ad97c39b587766e27` |

本轮没有制造Red或宣称新测试通过。此前记录的各版本测试、素材评判、61表一致/并发差异、cleanup和部署状态各保留原时点。新内部证据owner、来源覆盖、局部纠正及资源变化必须先批准Spec03；单纯修复意图不追認尚未展示的新设计。

## 设计阶段检查

已执行：3份新设计/Discovery文档的本地链接全部存在；无TODO/TBD占位；call graph、sequence、state、architecture、文件变更及required点完整。7份当前生产基线SHA与上表一致，未生产修改；`git diff --check`通过。父Spec、Feature候选说明、open内容ISS和Spec索引同步；目录当前13active/109completed/13rejected，新增内容03为READY_FOR_REVIEW/active。当前事实保持10/13，未混记候选11/14或未运行的新验收结果。

未运行：本Spec03生产/测试实现、Red/Green、模型验收、真实DB读取及部署。这些结果须在具体revision批准后另建EVD；本设计检查不是内容验收、独立代码Review或云交付。
