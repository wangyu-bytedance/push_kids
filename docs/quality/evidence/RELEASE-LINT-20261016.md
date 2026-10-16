# 历史设计生成脚本 lint 清理证据

- Date: 2026-10-16
- Approved Spec: [`SPEC-20261016-RELEASE-LINT-01`](../../../specs/completed/CHORE-20261016-RELEASE-LINT.md)，用户异步明确批准。
- Baseline: `8b933dae762f6dbdb1bb9c2286155106b0a5fdc6`；5个脚本在清理前与该HEAD逐字节相同，68处lint为既有问题。
- Scope: 仅5个离线设计生成脚本等价整理；不更改可见设计、批准快照或运行应用。

## 验证

| 检查 | 实际结果 |
|---|---|
| `.venv/bin/ruff check .` | PASS |
| `.venv/bin/ruff format --check .` | PASS，519 files already formatted |
| 新旧脚本输出一致 | PASS，在两个独立临时仓库镜像复制脚本及既有SVG，依次运行4个render及export，真实调用rsvg-convert；168个非Python输出SHA-256全相同（82 SVG、81 PNG、5 manifest） |
| 批准设计证据不可变 | PASS，git差异中无SVG/PNG/HTML/APPROVAL.md/VALIDATION.md；生成器只在临时镜像运行 |
| `.venv/bin/python tools/validate_design_evidence.py --check-current-policy` | PASS，DESIGN_EVIDENCE_VALID |
| 发布包边界 | PASS，最小白名单107文件/1239653字节，仅4个根配置与API Python源码；5个脚本及全部docs/tests/tools/小程序均排除 |

预提交manifest SHA-256为 `a752ba7bd8a1849a6f58d116aff89006a3cd14175fb0db7dcc3d06b75f8d0476`；正式冻结记录跟随BUG-029发布报告。临时比较文件未写入批准快照目录。

## R1 Diff Review

2026-10-16，Codex实现者逐文件复核；不宣称为独立人员审查。

| 文件（均位于docs/design/frontend/prototypes/） | 必要性、位置与语义核对 |
|---|---|
| DREV-20261013-SETTINGS-CONSISTENCY-01/render.py | 原地格式/拆行；绘图helper绑定当前循环的p/state/w，仍在该循环立即调用；摘要lambda改def。SVG字符串AST等价，输出一致 |
| DREV-20261014-ACTION-PAGER-CONSISTENCY-02/render.py | 原地格式/拆分分号；text绑定当前p，摘要def；分支/绘制顺序不变，输出一致 |
| DREV-20261014-SUBJECT-MANAGEMENT-01/render.py | 原地格式/字符串拆行；text/box绑定当前p，输出一致 |
| DREV-20261014-SUBJECT-MANAGEMENT-01/export.py | 原地字符串与格式整理；批准源读取、不可覆盖保护和导出行为保持，输出一致 |
| DREV-20261014-TODAY-ACTION-STYLE-01/render.py | 原地格式/字符串拆行及摘要def；输出一致 |
| 本证据、Spec、Spec索引 | 记录明确批准、实际检查、范围与生命周期；不修改现有批准manifest，不制造新设计revision |

不存在新增模块/共享抽象、依赖方向或发布内容变化；无遗留发现。Feature FEAT-001/010、Behavior Catalog、Architecture与UI当前事实逐项核对，无需为等价工具整理修改正文。Spec已DONE并迁入completed；BUG-029部署状态另记。
