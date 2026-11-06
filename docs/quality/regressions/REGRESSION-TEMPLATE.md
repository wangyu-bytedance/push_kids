---
id: "REG-[TODO: stable-id]"
type: regression
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: draft
kind: behavior
owner: NEEDS_VERIFICATION
issue: NEEDS_VERIFICATION
bad_revision: NEEDS_VERIFICATION
fixed_revision: NEEDS_VERIFICATION
test_path: NEEDS_VERIFICATION
command: NEEDS_VERIFICATION
red_evidence: NEEDS_VERIFICATION
green_evidence: NEEDS_VERIFICATION
reviewer_fixture: NEEDS_VERIFICATION
reviewer_evidence: NEEDS_VERIFICATION
quarantine_reason: N/A
quarantine_until: N/A
retirement_reason: N/A
---

# Replayable Regression Case

路径为仓库相对路径；主路径填元数据，其他证据在正文补充。
本模板不计覆盖，实例active条件见[README](README.md)。

## Contract and behavior regression

- Feature/module/failure class/severity / 原问题及根因：
- 合成夹具、安全隔离环境、前提及清理：
- 操作步骤、可观察期望、禁止副作用、相邻合法/非法/边界：

| 阶段 | 精确命令/环境 | 被测版本 | 预期/实际 | EVD |
|---|---|---|---|---|
| Red复现 | NEEDS_VERIFICATION | bad_revision | 目标行为失败 | NEEDS_VERIFICATION |
| Green及相邻行为 | NEEDS_VERIFICATION | fixed_revision | 通过 | NEEDS_VERIFICATION |

## Reviewer evaluation

- 不可变base/target或脱敏快照清单；正例或干净/误报负例：
- 已确认期望根因、位置、严重性/明确无发现及禁止有害修复：
- 模型、提示、REVIEW、工具/配置版本；人工标签及评估者：
- 精确重放方法/命令、预算、评分准则、观测结果、轮数/时间/费用：

reviewer_evidence的passed表示满足识别标准，subject_revision绑定bad_revision，
不表示坏版本产品正确。behavior-only本节可N/A并说明；reviewer-only的行为字段
可N/A。不同运行追加新证据，不追改旧版本。

## Lifecycle decisions

- 隔离原因、缺失覆盖、Owner和到期日：
- 退役理由、批准及替代案例：
- 重放历史和EVD链接（保留失败）：
