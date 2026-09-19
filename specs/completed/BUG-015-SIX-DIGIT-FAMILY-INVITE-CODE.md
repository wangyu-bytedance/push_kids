# BUG-015 — 六位家庭邀请码在申请前不可获得

- Status: DONE
- Severity: `P1 — 新用户无法按六位码入口完成家庭加入`
- Risk: R3
- Owner: 产品负责人（用户）
- Implementer: Codex
- Reviewer/Verifier: Codex + 产品负责人双账号验收
- First observed: `2026-09-13 / 当前小程序家庭加入流程`
- Related incident/ticket: `本对话：用户报告“申请加入家庭需要先输入6位申请码，但是这个时候还没有”`
- Spec revision: `BUG-SPEC-20260913-19`
- User confirmation: `APPROVED — 产品负责人（用户），2026-09-13，本对话“按照方案生成代码”明确对应上一轮 BUG-SPEC-20260913-19 + DREV-20260913-FAMILY-INVITE-CODE-01`
- Affected Feature IDs: `FEAT-002`
- Feature current-state documents: `docs/domain/features/FEAT-002-family-collaboration.md`
- Feature baseline revision: `FEAT-STATE-20260906-BUG014-STAGING-EVIDENCE`
- Feature merge owner: Codex

## Frontend Design Impact and Repository-native Approval

- Frontend impact: `yes — 邀请就绪态显示六位家庭邀请码，申请入口接收该邀请码，并区分申请后的核验码`
- Frontend impact reason: `修复用户进入家庭加入流程所需的前置凭证与可见文案`
- Frontend engineering impact: `yes — 表单输入模式、校验、状态和 API 字段发生变化`
- Frontend engineering impact reason: `UI-009 创建响应展示；UI-010 手工输入、预览、失败恢复和申请后核验码命名`
- Affected UI IDs: `UI-009、UI-010`
- UI current-state documents: `docs/design/frontend/ui/UI-009-family-members.md；docs/design/frontend/ui/UI-010-family-access.md`
- Frontend baseline revision: `FDB-20260913-04（APPROVED）`
- Frontend engineering constraint revision: `FEC-20260913-LOCAL-DESIGN-EVIDENCE-01（APPROVED）`
- Affected frontend quality dimensions: `state/form/responsive/a11y/browser-device/security/privacy/observability`
- Frontend quality budgets/requirements: `三视口；触控>=44px；正文>=14px；数字键盘与字段级错误；凭证不进Storage/日志/分析；服务端最终鉴权`
- Frontend quality verification plan: `邀请码创建/复制/分享/手输/预览/申请；不足6位、无效、过期、撤销、限流、重复、权限；三视口原生几何、iOS/Android双账号`
- Approved frontend engineering deviations: `none`
- Current Design Revision(s): `DREV-20260906-PKDS-03（视觉基线）；本修复 candidate DREV-20260913-FAMILY-INVITE-CODE-01`
- Editable design source path(s): `docs/design/frontend/prototypes/DREV-20260913-FAMILY-INVITE-CODE-01/family-invite-flow.html`
- Design source SHA-256: `de5e54eb908f2a938a070467a86930d91b92f9629dd26826cc32d49e958f8d59`
- Proposed Design Revision: `DREV-20260913-FAMILY-INVITE-CODE-01`
- Required viewport/state exports: `UI-009 invite-ready + UI-010 manual-code-entry × 320×568、390×844、430×932；其他错误/等待/审批态实现后原生验证`
- Prototype status: `APPROVED`
- Approved Task Spec revision: `BUG-SPEC-20260913-19`
- Approved Design Revision: `DREV-20260913-FAMILY-INVITE-CODE-01`
- Design approval evidence: `产品负责人（用户）/ 2026-09-13 / 本对话“按照方案生成代码”`
- Snapshot manifest path: `docs/design/frontend/snapshots/UI-009/DREV-20260913-FAMILY-INVITE-CODE-01/APPROVAL.md；docs/design/frontend/snapshots/UI-010/DREV-20260913-FAMILY-INVITE-CODE-01/APPROVAL.md`
- Permitted implementation deviations: `原生字体 fallback 与内容自然换行；不得改变字段名称、操作顺序或数字长度`
- UI current-state merge owner: Codex
- UI current-state merge evidence: `UI-009/UI-010 Change References + FEAT-STATE-20260913-BUG015-SIX-DIGIT-INVITE`
- Frontend visual/a11y/resolution verification: `两组已批准设计图覆盖三视口并通过 manifest 完整性校验；实现 HTML 的 320/390/430 Chrome 走查完成；原生证据须发布前补充`
- Frontend engineering verification evidence: `167 个前端测试、Mini Program lint/validator、11 个家庭入口定向测试通过；原生 DevTools/真机未运行`
- External design dependency: `none`

## 1. Symptom and impact

- Who/what is affected: 无家庭、尝试手动加入现有家庭的微信用户。
- Frequency: 只要入口要求六位码即为必现。
- User-visible symptom: 页面把“六位申请码”作为创建申请的前置输入，但该码只在申请创建后生成。
- Business/data/security impact: 手工加入流程无法完成；无数据损坏或越权写入。
- First known good version: 未知；当前后端从 FEAT-002 首次实现起即使用长 token，设计稿同时保留六位输入。
- First known bad version: `0.1.7` 对应源码仍存在合同分裂。
- Workaround: 管理员使用“微信邀请”分享卡，或复制长口令；不满足六位码手工加入预期。

## 2. Reproduction

### Preconditions

- Environment/version: 当前仓库及小程序 `0.1.7` 对应前端源码。
- Actor/permissions/tenant: A 为家庭 manager，B 为 unbound trusted WeChat actor。
- Data/fixture: A 已有 active family。
- Feature flags/config: 云环境或测试环境家庭身份链路可用。
- External dependencies: 无。

### Steps

1. A 打开“家庭与成员”，点击“邀请家人”。
2. A 的页面不显示六位家庭邀请码，只把 43 位 token 留在内存供复制/分享。
3. B 打开“申请加入家庭”；若按设计输入六位申请码，则此时还没有任何申请，也没有申请码。

### Actual result

管理员没有可告知的六位码；后端 `request_code` 只有 `POST /family-requests` 成功后才返回。

### Expected result

管理员创建邀请时得到并看到六位“家庭邀请码”；申请人可以用它预览家庭并创建申请。申请创建后生成的
六位值明确命名为“申请核验码”，不再作为前置凭证。

### Reproduction evidence

- Test/script: 现有 `tests/integration/test_family_onboarding.py` 和前端源码静态检查。
- Request/trace/log ID: N/A；根因可由确定性调用链复现，未读取敏感生产日志。
- Screenshot/data query: candidate DREV；未查询生产家庭数据。
- Reproduction rate: 100%。

## 3. Triage

### Confirmed facts

| Fact | Evidence |
|---|---|
| 创建邀请返回长 token，不返回六位邀请码 | `families/service.py::_invite_token/create_invite` |
| 手工加入当前实际接收 32..120 位 token | `families/schemas.py::InviteTokenRequest/JoinRequestCreate` |
| 六位 request_code 在申请存在后由 request id 派生 | `families/service.py::_request_code/_request_view/apply` |
| 当前 request_code 可包含 A-F，并非纯数字 | `_request_code` 取 UUID 十六进制前六位 |
| 设计稿曾要求 A3 输入六位后预览 | `DREV-20260906-PKDS-01/FRONTEND-SPEC.md` A3 |
| 当前 WXML 却要求粘贴长邀请口令 | `pages/family-onboarding/index.wxml` |

### Hypotheses

| Hypothesis | Supports | Contradicts | Experiment | Result |
|---|---|---|---|---|
| 后端偶发没有生成 request_code | 用户看到无六位码 | request view 始终派生 code | focused integration tests | rejected；现有 6 tests pass |
| 前后端把邀请码与申请核验码合并成一个概念 | 设计与实现命名/时序冲突 | 无 | 调用链 + DREV 对照 | confirmed |

### Blast radius

- Entry points: 家庭成员邀请、首次 onboarding 手工加入、分享直达、加入申请审批。
- Callers/consumers: Mini Program UI；families invite/preview/apply services；通知中的申请码。
- Data already affected: 无损坏；既有 active invite 只有 token_hash，不具备六位码摘要。
- Security/tenant boundary: 六位码只允许可信 actor 查询最小预览；加入仍需 manager 审批。
- Related behaviors: `BHV-017` 单次邀请、撤销/到期级联、原 token 不进列表/日志。
- Other code with the same pattern: onboarding pending、family-join applied、family-requests、通知文案。

### Link/call graph

```text
manager create invite → POST /families/current/invites → long token only
applicant manual join → six-digit UI expectation ─X→ no pre-application code
applicant apply → POST /family-requests → request_code generated too late
```

## 4. Root cause

### Fault mechanism

初始 FEAT-002 用高熵 token 作为邀请凭证；后续 A3 交互把前置凭证设计成六位输入，但生产 API/数据模型
没有同步增加独立家庭邀请码。与此同时，申请后的人际核验码仍被称为“申请码”，造成前后两个不同阶段的
凭证被当成同一个字段，形成循环依赖。

### Why existing controls missed it

- Missing/incorrect test: 没有“manager 创建可见六位码 → applicant 手输 → preview/apply”的端到端测试。
- Review/spec gap: DREV 的六位输入与 FEAT-002 的 256-bit token 安全合同没有在同一验收矩阵对齐。
- Monitoring gap: 只覆盖 API 成功和分享路径，没有手工加入漏斗状态。
- Architecture/process contributor: API 字段 `token` 同时承担分享凭证和手工输入语义，UI 文案缺少术语表。

### Root-cause evidence

- Code location: `families/{schemas,service,repository}.py`；`pages/family-{members,onboarding,join,requests}`。
- Failing test: 待新增 `TP-001`，在当前实现应因无 `invite_code` 失败。
- Runtime evidence: 用户当前体验报告；本轮不执行生产写入复现。

## 5. Fix contract

### Required behavior

- 创建邀请同时返回 6 位纯数字 `invite_code` 和既有高熵 token/share_path。
- 管理员页面立即显示并可复制 `invite_code`；复制值为六位、无空格。
- 申请人手工入口只接收六位 `invite_code`；微信分享路径继续使用高熵 token。
- preview/apply 后端兼容两种凭证，统一解析到同一 invite，并继续执行 active/expiry/family 状态检查。
- 申请后的 `request_code` 改为六位纯数字并在界面称为“申请核验码”。
- 任何凭证都不进 URL 查询（分享 path 除既有 Mini Program 页面参数）、日志、Storage 或分析。

### Must not change

- 邀请只创建申请、不直接授权；manager 明确审批后才创建 active membership。
- 单次批准、撤销/到期级联、幂等、family scope、角色和最后管理员保护保持不变。
- 既有微信分享链接和长 token 在兼容窗口内继续可用。
- 邀请列表仍不返回长 token；不得用客户端状态授权。

### Feature current-state impact

- Current Feature sections affected: Current user/system behavior、contracts、quality/operations、limitations。
- Incorrect/obsolete statement to correct: “有效邀请列表不返回 token，申请双方通过六位申请码核对”需要区分邀请码与核验码。
- Final facts to merge after verification: 双凭证兼容、六位数字生成、限流与双账号证据。
- Change Reference to add: `BUG-SPEC-20260913-19`。

### Non-goals

- 不改变成员角色、按孩子授权、家庭切换、通知订阅或公开发布状态。
- 不把六位码当作授权凭证；不取消 manager 审批。
- 不部署、不上传体验版、不切生产流量。

### State/data repair

- Does the fix prevent new corruption only? 是；现有数据没有损坏。
- Is existing data repair required? 不回填明文；迁移后旧 active invite 继续仅支持原分享 token，管理员可重新生成六位码邀请。
- How is affected data identified? `active_code_hash IS NULL` 的兼容邀请。
- Is repair idempotent/reversible/audited? additive migration；新邀请继续写 `invite.created`，不记录明文。

## 6. Fix design

### Selected change

- Existing path to modify: 既有 FamilyInvite/FamilyService/API/四个家庭页面。
- Logic to delete/replace: 删除“六位申请码是前置邀请码”的文案；保留申请后核验用途。
- Why no parallel path is needed: preview/apply 仍走同一 service，只在凭证解析边界识别六位 code 或长 token。
- Error/transaction/concurrency implications: additive nullable code hash + 唯一索引；碰撞时有限重试；事务失败不产生半邀请。

六位码由现有高熵 token、服务端 secret 与有限 nonce 经 HMAC 确定性派生，结果允许前导零且对客户端不可
预测。数据库仅保存另一个用途隔离的 HMAC 摘要和 nonce；为避免同时 active 邀请码碰撞，新增 nullable
unique `active_code_hash`。邀请进入 exhausted/revoked/expired 时清空该字段，释放码空间。该实现不保存
可逆明文，同时让同一幂等创建请求在网络重试时稳定返回同一码；页面成功后仍清除幂等键，刷新不会从邀请
列表重新显示凭证。这是批准方案在实现期的安全/幂等细化，不改变用户操作顺序或授权边界。

手工六位码的最小预览仍受 trusted actor 限流；受控阶段维持现有每 actor 20/min 上限，新增 6 位路径的
更严格 5 attempts/15min。多实例共享限流仍为公开发布阻断项，不以本 bugfix 宣称关闭。

### Trade-offs and alternatives rejected

| Alternative | Why rejected |
|---|---|
| 继续要求复制 43 位 token，只改文案 | 无法满足明确的六位手工加入需求，且用户难以跨设备输入 |
| 把申请后 request_code 提前生成并直接用于 lookup | 混淆 invite 与 request 生命周期；申请不存在时没有 request owner |
| 用六位码替换分享 token | 把低熵人工凭证放进所有分享路径，降低现有安全性且破坏兼容 |
| 数据库存储六位明文以便刷新后重显 | 扩大凭证泄漏面；本轮选择一次展示，丢失时重新生成 |
| 客户端从长 token 截取六位 | 碰撞不可控、客户端拥有业务规则、服务端无法稳定鉴权 |

### Sequence diagram

```mermaid
sequenceDiagram
  participant M as Manager Mini Program
  participant A as Applicant Mini Program
  participant S as FamilyService
  participant DB as MySQL
  M->>S: POST /families/current/invites
  S->>DB: token_hash + active_code_hash + expiry
  S-->>M: invite_code + share_path
  alt manual code
    A->>S: POST /family-invites/preview {token:"482731"}
  else WeChat share
    A->>S: POST /family-invites/preview {token:"<high entropy>"}
  end
  S->>DB: resolve active invite + expiry check
  S-->>A: minimal family preview
  A->>S: POST /family-requests {credential, relationship}
  S->>DB: create pending request
  S-->>A: six-digit request verification code
  M->>S: approve request after out-of-band verification
  S->>DB: activate member; exhaust invite; clear active_code_hash
```

### State machine

```text
invite active(code+token) → exhausted / revoked / expired
                         ↘ terminal transition clears active_code_hash
request absent → pending(request verification code) → approved / rejected / cancelled / expired
```

### Architecture diagram

```text
UI-009 manager ─┐
UI-010 applicant├─> families router → FamilyService credential resolver → FamilyRepository → FamilyInvite
share path ─────┘                         │
                                         └─ trusted actor rate limiter
```

### Expected file changes

| File/path | Action | Expected change | Why required |
|---|---|---|---|
| `apps/api/migrations/versions/20260913_0014_family_invite_codes.py` | add | nullable unique active code digest | 六位码服务端 lookup |
| `persistence/models.py` | modify | FamilyInvite active_code_hash | ORM 对齐迁移 |
| `families/{schemas,repository,service,router,rate_limit}.py` | modify | 双凭证、生成/释放、字段和限流 | 权威后端修复 |
| `pages/family-members/*` | modify | 显示/复制家庭邀请码 | manager 获得前置凭证 |
| `pages/family-onboarding/*`、`pages/family-join/*` | modify | 六位输入、校验、错误恢复 | applicant 完成手工加入 |
| `pages/family-requests/*` | modify | “申请核验码”命名 | 避免术语再次混淆 |
| `tests/integration/test_family_onboarding.py` | modify | 双凭证、碰撞、过期、数字与隔离 | 后端回归 |
| `tests/frontend/family-onboarding.test.js` | modify | 入口和状态回归 | 前端回归 |
| Feature/UI/behavior docs | modify | 合并最终事实 | current-state 同步 |

### Compatibility and rollout

- Deployment order: additive migration → 兼容旧 token 的后端 → 新前端；不得先发只接受六位码的前端。
- Feature flag: 无；后端兼容使滚动发布安全。
- Migration/backfill: 不回填旧邀请码明文；旧 token 继续有效至自然终态。
- Rollback/restore: 前端可回滚到 token 流；后端旧版本忽略 nullable 新列；事故中不做 destructive downgrade。
- Success/abort metrics: 只记录无凭证内容的 create/preview/apply outcome；跨家庭、429、5xx 异常升高即停止发布。

## 7. Regression verification

### Required regression test

- Test point ID: `TP-001`
- Acceptance/expected behavior: manager 创建得到 `^\d{6}$` invite_code，applicant 用它 preview/apply 成功。
- Test level: backend integration + Mini Program state test。
- Pre-fix failure evidence: 当前响应没有 invite_code，schema 拒绝六位输入。
- Post-fix success evidence: `tests/integration/test_family_onboarding.py` 8 passed；创建响应含六位码，
  手输 preview/apply、旧 token、碰撞重试、幂等重放、数字核验码和摘要释放均通过。
- Why this test proves the bug: 直接覆盖用户无法获得并使用前置六位码的断点。

### Adjacent cases

| Case | Expected |
|---|---|
| Original reproduction | 六位码创建、显示、复制、输入、预览、申请成功 |
| Prior valid path | 微信 share_path/长 token 继续成功 |
| Invalid/unauthorized | 非 manager 不能创建；无效码不泄露家庭数据 |
| Boundary/empty/null | 000000 合法；少于/多于六位拒绝；非数字拒绝 |
| Duplicate/concurrent | idempotent create 不双建；active code 不冲突；单邀请只批准一人 |
| Dependency failure | 保留输入/成员旧数据，显示可恢复错误 |
| Expired/revoked/exhausted | 长 token preview/apply 410；已释放摘要的六位码返回通用 404/不可用，不保留终态映射 |
| Privacy/logging | 日志、Storage、错误文本无 code/token |

### Verification commands

| Test point | Command/case | Environment | Result | Evidence |
|---|---|---|---|---|
| `TP-001..API` | `uv run pytest tests/integration/test_family_onboarding.py -q` | SQLite | PASS | 8 passed |
| `TP-UI` | `node --test tests/frontend/family-onboarding.test.js` | Node | PASS | 11 passed |
| `TP-FULL-BE` | `uv run pytest tests/unit tests/integration tests/contract -q` | SQLite | PASS | 335 passed、4 skipped（MySQL 环境型） |
| `TP-FULL-FE` | `npm test && npm run lint:miniapp` | Node | PASS | 167 passed；eslint exit 0 |
| `TP-STATIC` | `uv run ruff check . && uv run ruff format --check . && uv run mypy apps/api/src` | local | PASS | 330 files formatted；85 source files typed |
| `TP-ARCH` | `uv run python tools/check_architecture.py && uv run python tools/validate_miniprogram.py` | local | PASS | `ARCHITECTURE_VALID checked=3`；`MINIPROGRAM_VALID pages=15` |
| `TP-MIGRATION` | unique head + fresh SQLite base-to-head/current + local legacy auto-upgrade | SQLite | PASS | `20260913_0014 (head)`；新增列/唯一索引存在 |
| `TP-DESIGN` | 两个 DREV manifest 校验 + 实现三视口 HTML/Chrome 走查 | local | PASS（非原生） | 两次 `DESIGN_EVIDENCE_VALID`；320/390/430 走查完成 |
| `TP-MYSQL57` | affected family suite with `PUSH_KIDS_TEST_MYSQL_URL` | real MySQL 5.7 | NOT_RUN | 本机未配置该环境；阻断后端云发布，不阻断本地代码完成 |
| `TP-NATIVE` | DevTools + 320/390/430 + iOS/Android two-account | real AppID | NOT_RUN | 阻断体验版/发布验收，不阻断本地代码完成 |

## 8. Review checklist

- [x] Observable symptom and expected contract are clear.
- [x] Root cause is evidence-backed, not only plausible.
- [x] Same pattern was searched elsewhere.
- [x] The fix modifies the authoritative path.
- [x] Obsolete workaround/branch is identified for removal.
- [x] Required design views are complete or marked with implementation gates.
- [x] Expected changed, added, moved, and deleted files were reviewed.
- [x] Required regression is executable and directly reads the absent baseline `invite_code`; pre-fix source/API contract evidence is preserved（未在脏工作区另行 checkout 旧实现）。
- [x] Every required test point ran or has an explicit skipped-check risk.
- [x] Historical behavior tests pass.
- [x] Data repair, compatibility and rollback are addressed.
- [x] Monitoring detects recurrence without logging credentials.
- [x] No unrelated refactor is mixed in.

## 9. Closure and prevention

- Changed behavior: manager 现在创建并展示六位家庭邀请码；申请人可手输预览/申请；微信分享继续兼容；
  申请后的六位值统一为申请核验码。
- Deleted workaround/logic: 删除前端长口令手输和“申请码既是前置邀请码”的混合文案；长 token 只保留微信分享兼容。
- Data repaired: N/A。
- Monitoring added: 本地实现未新增持久指标；保留不含凭证的 HTTP outcome/429 观测合同，发布时按 safe outcome counters 检查；共享多实例限流仍为发布风险。
- Behavior catalog update: `BHV-017` 已区分家庭邀请码、分享 token 与申请核验码。
- Feature current-state document update and Change Reference: `FEAT-STATE-20260913-BUG015-SIX-DIGIT-INVITE`、UI-009/UI-010 已同步。
- Architecture/test/process change preventing recurrence: dual-credential contract test + terminology table。
- Independent Review: Codex 完成最终 diff、迁移、隐私、兼容和门禁复核；产品负责人双账号原生验收待发布阶段执行。
- Residual risk: 六位码低熵；真实 MySQL 5.7、共享多实例限流和双账号真机必须在发布前单独验证。
- Follow-up owner/date: 发布负责人 / 发起后端或小程序发布前。
