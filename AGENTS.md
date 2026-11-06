# Push Kids repository contract

## Product and stack

- Product: 家长管理小学生已学内容、复习计划和课外活动记录的微信小程序。
- Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite（本地）/ 原生微信小程序。
- Source of truth:
  - AI Native profile: `.ai-native/project.json`
  - Current architecture: `docs/architecture/ARCHITECTURE.md`
  - Enforced architecture: `docs/architecture/ARCHITECTURE-CONSTRAINTS.md`
  - Current feature state: `docs/domain/features/`
  - Current behavior: `docs/domain/BEHAVIOR-CATALOG.md`
  - Approved frontend baseline and repository-native design evidence index: `docs/design/frontend/FRONTEND-DESIGN.md`
  - Enforced frontend engineering rules and budgets: `docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md`
  - Current frontend UI state: `docs/design/frontend/ui/`
  - Test policy: `docs/quality/TEST-STRATEGY.md`
  - Development and coding: `docs/ai/DEVELOPMENT-PROTOCOL.md`, `docs/ai/CODING-CONSTRAINTS.md`
  - Review policy: `REVIEW.md`; issue learning: `docs/quality/issues/`; replay contracts: `docs/quality/regressions/`
  - Release workflow and human-operation gates: `docs/deploy/`
  - Task intent and acceptance: `specs/`

## Commands

```bash
uv sync --all-groups
npm install
uv run pytest tests/unit tests/integration tests/contract -q
uv run ruff check . && uv run ruff format --check .
uv run mypy apps/api/src
npm test
uv run python tools/check_architecture.py
uv run python tools/validate_design_evidence.py --check-current-policy
uv run python tools/validate_miniprogram.py
uv run uvicorn push_kids.bootstrap.app:create_app --factory --app-dir apps/api/src --reload
```

Never claim a check passed unless it ran. Record skipped checks and the reason.

Read the development protocol and coding constraints before implementation, and `REVIEW.md` before review.
Use the protocol's honest Red/Baseline branches and versioned evidence; a passing test alone does not prove
correct design, necessary changes, proper placement, or documentation consistency. Preserve project-specific
frontend and release gates. Maintenance follows `docs/ai/MAINTENANCE-PLAYBOOK.md`.

## Release workflow

- Every frontend, backend, database, or combined release must follow `docs/deploy/README.md` and its linked
  playbooks. Preserve the distinction between uploaded, experience, review, and production states.
- When a release reaches a required manual action, stop before that gate and output the standardized
  `【需要人工操作】` block from `docs/deploy/README.md`, including the direct console link, navigation path,
  required values or decision criteria, success signal, and exact reply requested from the operator.
- Never ask the operator to paste credentials, OpenID, database URLs, Ark keys, HMAC keys, or COS credentials
  into chat. Secrets remain in the platform runtime configuration or an approved secret store.

## Non-negotiable product rules

- AI output is an editable proposal. Only a parent confirmation creates formal learning records and review items.
- AI never grades answers or declares mastery. Extraction only describes learned facts. Approved FEAT-004 permits one editable incremental suggestion based on existing grade and confirmed learning; it never prescribes a required next lesson. Parent approval creates only a StudyTask; actual learning confirmation alone creates formal records and deterministic reviews.
- Review dates are produced by deterministic planning policy, never by the model.
- Every query and write is family-scoped at the server boundary. MVP uses `X-Family-ID`; public release must replace it with verified WeChat identity.
- Never store secrets, tokens, raw model payloads, or child images in logs or the repository.
- Manual learning input and manual Todo feedback must remain first-class paths.
- Preserve both `occurred_at` and `created_at`; historical backfill schedules a current check and does not create past Todo debt.

## Architecture rules

- Organize production code by coherent purpose/business domain, then by layer; keep file responsibilities narrow.
- Extract common code only when consumers share stable semantics, owner, contract, and change axis; never create an unowned dumping ground.
- The module/package dependency graph must remain acyclic, including indirect and test-only edges.
- Extensibility is explicit and bounded as `open`, `closed`, or `deferred`; every open point needs compatibility, isolation, security, observability, and contract-test rules.
- `planning/domain.py` is pure policy and must not import FastAPI, SQLAlchemy, settings, or provider clients.
- Routers validate transport and delegate. Services own use cases and transaction boundaries.
- `agent_processing/providers` implement the provider contract; domain modules never call Ark directly.
- Cross-domain access goes through services/contracts. Avoid generic `utils`, `common`, or direct cross-module table writes.
- External inputs and model outputs are untrusted and validated.
- Collection and embedded-list reads must be bounded end to end: stable cursor pagination or a documented
  domain cap, database-side aggregates, O(1) page query count, tenant-leading indexes, response budgets and
  scale/query-plan tests. A router `limit` does not excuse an unbounded service query.
- Background jobs are idempotent and have explicit terminal states, retries, cancellation, and observable errors.
- Use `apply_patch` for handwritten file edits. Preserve unrelated user changes.

## Feature workflow

Visible or behavioral changes require an approved Spec revision and relevant current-state update. FEAT-001 is approved for implementation by the user on 2026-08-30. Repository-native design evidence replaces the former Figma requirement under `GOV-SPEC-LOCAL-DESIGN-EVIDENCE-20260913-01`.

## 3. Requirement workflow

For every request that changes behavior, APIs, data, architecture, tests, or documentation facts:

1. Resolve affected Feature IDs and read their current state under `docs/domain/features/`.
2. Create or update the matching template from `specs/_templates/`; include link/call graph, sequence diagram, state machine, architecture diagram, trade-offs, expected file changes, and required test points, or mark a view `N/A` with a reason.
3. Wait for explicit user confirmation of the specific Spec revision before production implementation. A user instruction to build, implement, fix, or proceed **according to a named Spec** is approval of that Spec's current revision: record it in the approval block (approver, date, message reference) and set the Spec `Status` to `APPROVED` before coding. A bare "可以/继续/OK" counts only when it maps unambiguously to one Spec revision.
4. Implement only approved scope, run every required test point, and record pass/fail/not-run evidence.
5. Merge verified final facts into Feature/UI current-state documents and check architecture cleanliness before completion.
6. On finishing, evaluate the Spec's lifecycle status and relocate it — do not leave finished work in `specs/active/`. Under the user-approved 2026-10-26 rule, verified cloud delivery of the corresponding implemented scope establishes development completion: set `Status: DONE` and move it to `specs/completed/`. Record incomplete acceptance separately with its actual result and follow-up conditions. If cancelled or rejected, record the reason and move it to `specs/rejected/`. A Spec stays in `active/` only while its development is genuinely unfinished or its scope has not been delivered.

### Development completion and acceptance

- 用户于2026-10-26明确要求：“如果已经发布到云端就认为需求已经开发完成，你来更新”。`DONE`表示需求开发完成，验收状态与发布阶段独立记录。
- 云端交付证据须覆盖该Spec实际实现的范围和版本：后端正常部署或微信小程序开发版本成功上传均可作为对应端的交付证据；涉及两端时分别核对。仅本地实现、构建、preview、dry-run或部署失败不满足。旧包不覆盖的后续增量继续留active。
- 已交付Spec的真机、业务、内容、可访问性或评审缺项保留真实PASS/PARTIAL/NOT_RUN/FAIL及后续条件，不再阻止开发DONE归档；这不把未验收项改成通过，不追认缺失的设计/实施批准。
- 未来发布仍执行既有必需检查和人工门禁；已上传、体验版、审核与正式发布继续严格区分。依据见`specs/completed/GOV-002-CLOUD-DELIVERY-DEVELOPMENT-COMPLETION.md`。

### Mandatory documentation closure after every code change

- 每次完成代码修改，必须按实际 diff 核对受影响的 Feature、Behavior Catalog、Architecture、UI current-state、Spec、测试证据与发布文档。逐项检查代码和当前文档是否冲突；不能只追加新说明而保留相互矛盾的当前正文。
- 更新已验证事实对应的正文、状态、revision、变更引用和证据；明确区分本地实现、自动化通过、原生/真机验收、上传、体验、审核和正式发布。未执行检查不得写成通过，历史证据不得冒充当前 diff 的验证。
- 每次收尾都必须检查 Spec 状态和存放位置：按上述云端交付规则确认开发完成后设为 DONE 并迁移到 specs/completed/，未完成验收独立保留；取消/拒绝应记录理由并迁移到 specs/rejected/；未交付的开发任务留在 specs/active/，记录缺失交付、验收和恢复条件。开发完成本身不等于验收完成。
- 迁移文档后同步修复索引和引用，检查目标路径存在；已批准设计快照保持不可变，只按既有规则添加 Superseded by 指针。
- 完成回复必须说明已同步的文档、Spec 最终状态/位置、代码与文档冲突核对结果，以及尚未验证或需要批准的事项。发现超出已批准范围的事实修订时先形成明确 Spec revision，不得静默扩展实现或用文档掩盖代码偏差。

Before initial production coding, or before changing module boundaries, shared abstractions, dependency direction, or extension points, present the recommended design, alternatives, and trade-offs and obtain confirmation of the architecture/Spec revision.

### Frontend repository-native design gate

User-visible frontend work requires an approved baseline covering style consistency, user interaction conventions, and an exact resolution/viewport matrix; affected UI current state; a repository-local editable SVG or self-contained HTML design source; required viewport/state exports with matching SHA-256 manifest; and explicit approval of the Task Spec revision + Design Revision. Figma, external design URLs, node IDs, and tool-availability waivers are not required. Frontend engineering impact independently requires the approved FEC revision and affected component/state/form, accessibility, browser/device, performance/resource, security/privacy, and observability evidence.

Native Mini Program viewport acceptance follows `docs/design/frontend/FRONTEND-ENGINEERING-CONSTRAINTS.md` and `docs/quality/TEST-STRATEGY.md`; repository previews, hidden overflow, or HTML rendering cannot replace native node geometry and three-viewport evidence. Approved manifests are immutable except for a `Superseded by` pointer; visible divergence requires a new Design Revision and approval.

### Multi-theme UI contract

- 用户于2026-11-06明确要求六种风格：原始风格、成长花园、星际探索、深海夜色、海洋风格、科技风格。修改任何 UI（页面、复用组件、导航、表单、图表、空态、加载、错误、禁用、只读、弹层）均须检查全部六种风格，不能只适配默认或浅色风格。该约束是本次明确授权的工程规则，不表示六主题运行时已经实现；实施与验收状态见 `specs/active/DESIGN-002-GLOBAL-UI-CONSISTENCY.md` 及其后续归档位置。
- 主题颜色、材质、字体角色、共享圆角、插画引用、图标语义和未知科目的默认图标由有明确 owner 的主题配置统一管理。页面和组件消费语义 token/资源角色；禁止新增散落的品牌色、固定浅色背景、逐页主题判断或六套业务页面。业务枚举、平台要求的固定值和必要的页面几何不因“减少硬编码”被无差别抽象。
- 未预置的科目/活动直接使用当前主题的固定默认图标：原始书本、花园嫩芽、星际小星球、夜色罗盘星、海洋贝壳、科技芯片。不得增加逐科目 AI 生成、联网等待或强制选图流程。
- 主题清单及适配检查必须从同一权威注册表派生；新增风格必须同步完整 token/资源角色、回退规则和检查矩阵，删除/改名必须兼容已保存的主题 ID。禁止全局改写 `Page`/`Component` 或复制业务控制器来接入主题。
- 每次 UI diff 提交六主题适配记录：共用业务逻辑只验证受影响流程；每个主题仍需验证受影响页面/组件的三视口（320×568、390×844、430×932）及相关状态，保留原生节点几何与截图证据。共享组件变更还须覆盖实际宿主、深色对比度、长文案、弹层及导航；HTML 预览不能代替原生或真机验收。未运行项如实记为 NOT_RUN，不能用默认主题结果代替。
- 继续执行现有包体与性能预算；主题不得引入新的运行时 UI/图标框架，不得把评审 HTML、原始大插画或图片 base64 全量放入页面 data/本地存储。变更后记录资源字节、源码总量、切换同步与偏好恢复结果。新主题机制的具体批准版本与交付证据仍遵守上方 Spec / Design / FEC 门禁。
