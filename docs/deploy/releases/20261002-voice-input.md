# 2026-10-02 — 语音录入提交与发布准备

## Scope and authorization

- 用户在明确得知待提交内容为语音录入后回复“提交然后部署”，授权提交及前端部署。
- Spec: `SPEC-20261001-VOICE-INPUT-03`；Design: `DREV-20261001-RECORD-VOICE-INLINE-03`。
- 范围：WechatSI 语音输入、记录页集成、测试、图标及设计/规格证据。前两个已废弃设计版本保留历史标记。
- 本记录随语音实现一同提交；基线 commit 为 `d749c8d`，精确源提交可由本文件首次提交的 Git 历史定位。
- `output/imagegen/review-source-modal-concept.png` 是另一个设计产物，不属于本次提交或发布包。
- 每日复习 30 分钟已经通过孩子配置生效；本次前端发布不修改复习策略或数据库。

## Target and unchanged services

- AppID: `wx5d2e0014690bf285`；项目目录：`apps/miniprogram`。
- 云环境：`prod-d2g14rwoycac6b45d`；服务：`flask-ik19`；`useCloud=true`、`urlCheck=true`。
- 后端：本次无代码部署或流量调整；既有灰度状态见 `20260926-024.md`。
- Schema before/after: `20260913_0014` / `20260913_0014`，本次无 migration。
- 当前已上传基线：`0.1.12`；后续上传前重新计算版本，本次未占用或推进版本号。
- 回退目标：保持 `0.1.12` 及当前后端；没有新上传版本或数据库迁移需要撤回。

## Fresh verification

| Check | Result | Evidence |
|---|---|---|
| `npm test` | PASS | 184 passed |
| `uv run pytest tests/unit tests/integration tests/contract -q` | PASS | 389 passed, 5 skipped；29.41s |
| `npm run lint:miniapp` | PASS | zero findings |
| Ruff check / format | PASS | 361 files formatted |
| Mypy | PASS | 86 source files |
| architecture checker | PASS | checked=3 |
| current design policy | PASS | `DESIGN_EVIDENCE_VALID` |
| Mini Program validator | PASS | 15 pages / 685412 source bytes |
| `git diff --check` | PASS | no whitespace errors |
| DevTools CLI `islogin` | PASS | `login: true` |
| isolated MySQL runtime | SKIPPED | five cases require unconfigured `PUSH_KIDS_TEST_MYSQL_URL`；no backend/SQL changes |
| native preview/audio/device matrix | NOT_RUN in this release attempt | prior preview was 650045 bytes / 634.8 KB；does not prove microphone authorization |
| current cloud live/ready and two-account smoke | NOT_RUN in this release attempt | recheck when resuming upload; no backend rollout in this task |

## Actual release state and next gate

**代码进入 Git 提交阶段；开发版本未上传、未设置体验版、未提审、未发布正式版。**

当前语音 Spec §13 要求上传前完成隐私配置及原生验证。最近一次目标 AppID 麦克风授权
返回 `errno 112`：`api scope is not declared in the privacy agreement`。管理员补充麦克风信息
并清理缓存后复测仍失败；本轮尚未取得隐私指引生效或真机授权成功的新证据。

管理员需在 [微信公众平台](https://mp.weixin.qq.com/) → 设置 → 服务内容声明 → 用户隐私保护指引
确认麦克风/语音转文字的真实用途及第三方处理说明审核通过并生效；在设置 → 第三方设置 → 插件管理
核验 WechatSI 当前条款。随后复测授权、按住/松开转写、取消及原生设备矩阵。

通过后继续 §13 和前端发布手册：核对后端健康及业务 smoke，真实 AppID preview，计算下一版本，
上传成功后才推进版本文件；再由管理员选择体验版并验收。独立审查和剩余原生验收未完成，
Spec 保留在 `specs/active/` 的 VERIFYING 状态。
