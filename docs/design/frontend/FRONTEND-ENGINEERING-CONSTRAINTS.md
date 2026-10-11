# Push Kids frontend engineering contract

## Constraint identity and approval

- Frontend engineering scope: PRESENT
- Constraint status: APPROVED
- Constraint revision: FEC-20261007-NATIVE-GEOMETRY-02
- Owner: 产品负责人（用户）
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-07
- Approval evidence: 用户在本会话针对三张原生界面错误截图要求增加同类检查及约束，随后以“修改代码 并测试”批准 `SPEC-20261007-REVIEW-GROUP-CARDS-05`，其中明确提出本修订；既有预算与规则继续有效
- Superseded revision: FEC-20260913-LOCAL-DESIGN-EVIDENCE-01（有界读取、视觉、视口、样式分层与图标条款不变）
- Related frontend design baseline: FDB-20260913-04
- Applies to: `apps/miniprogram`

## Engineering priorities and stack boundary

- Runtime is native WeChat Mini Program using WXML, WXSS, CommonJS JavaScript and platform APIs.
- Server is authoritative for identity, authorization, learning facts, job state, review state and reports.
- Client pages map gestures to API operations and render explicit states; they do not own business policy.
- Do not add a cross-platform framework, chart library, state framework or rich-text renderer without an approved Spec.

## Information architecture and action hierarchy

- Primary tabs remain 今日、日程、记录、报表、设置; onboarding, submission, confirmation, family application and approval are deep flows.
- Each page exposes one dominant action. Secondary and destructive actions are visually separated.
- Manager-only actions may be hidden for usability, but server authorization remains authoritative.

## Design tokens and component contracts

- Styles are layered and the layers are one-directional: `styles/tokens.wxss` (semantic values) -> `styles/atoms.wxss` (component classes) -> page `.wxss` (page-only geometry). `app.wxss` only imports the layers and keeps legacy class shims.
- Global semantic colors, spacing, radii, typography, elevation, motion and safe-area values live in `styles/tokens.wxss` and are the single source of truth. Pages must not redefine them.
- Pages must not create near-duplicate token scales. Reusable components require shared product semantics, not visual similarity alone.
- Radii are restricted to 8/12/16/24/32/40/999rpx; intermediate values require an approved Spec.
- Icons are generated line icons from `tools/gen_icon_styles.py` (24x24 viewBox, stroke-width 2, no fill). Emoji, text glyphs and icon fonts are forbidden as icons. The generator must stay idempotent so `styles/icons.wxss` can be regenerated in verification.
- Legacy CSS variable aliases in `styles/tokens.wxss` are a temporary compatibility layer owned by the PKDS rollout Spec and must be removed before public release.
- Touch targets are at least 44 logical pixels; body text is at least 14px; color is never the sole state indicator.

## State ownership and data flow

- Remote business state lives on the server. Page `data` owns transient view/form state.
- Local storage may contain only selected child, safe display preferences and explicitly development-only identity fixtures.
- Network access goes through `utils/api.js`; production identity is injected by the trusted platform boundary and never derived from local family IDs.
- Requests prevent stale-response overwrite, duplicate submission and late async results after cancellation.

## Forms, mutations, and destructive actions

- Forms preserve user input on recoverable errors, expose pending state and block duplicate submit.
- Server validation is authoritative; field errors are shown next to the relevant input where possible.
- Removal of a member/child/record and permission reduction require impact text and confirmation.
- Optimistic Todo feedback rolls back on failure; identity, membership and payment-like operations are never optimistic.

## Complete UI states and recovery

- Every remote surface covers loading, content, empty, error, unauthorized/forbidden, not-found and retry where applicable.
- Analysis states are 等待分析、正在分析、待确认、失败、已取消、已确认; fabricated percentages are forbidden.
- Share/application surfaces cover expired, revoked, pending, approved, rejected and duplicate request states.
- Failed AI analysis retains original evidence and offers retry or manual recording.

## Responsive layout, content, and input modes

- Required portrait viewports are 320×568, 390×844 and 430×932 logical pixels with safe-area insets.
- Layout is single column with maximum content width 480px; long CJK labels wrap and key actions remain reachable with the keyboard open.
- Ordinary pages and sheets never require horizontal dragging to find a field, date, option, or action. Seven-day, three-range, three-subject and seven-weekday controls use shrinkable tracks and remain fully visible.
- The 100-day report is the single approved horizontal gesture surface: it paginates inside its own swiper as 30/30/30/10 items, while the root page remains horizontally fixed.
- Native buttons define width/min-width, margin, padding, box sizing and line height for their role. Circular controls keep equal computed width and height and cannot shrink inside flex layouts.
- In a two- or three-column selector, the track owns its width and the native button fits that track with border-box sizing. Buttons in one row differ in rendered width by at most 1 logical pixel, with at least 8px between adjacent button edges and between rows; a partial final row retains the same column width. No selector or child may overlap or extend past the content boundary.
- A one-entry dropdown selector fills its entire content row, and its opened option list stays within that row and the viewport; each option is at least 44px high. The partial-row check applies only where a multi-column selector actually has a partial row. Verify the rendered native width: a WeChat button's default maximum can silently shrink a `width: 100%` selector, so source CSS alone is insufficient.
- An item-level ellipsis action is a fixed 44×44 logical-pixel target (±1px native-renderer tolerance), never a flex-growing sibling. Reserve its width in the adjacent title layout so long text and metadata remain readable. The anchored menu must remain inside the viewport.
- Hiding horizontal overflow is not acceptance evidence. At all three required viewports every required control must stay within its container by no more than 1px and every regular touch target remains at least 44px.
- Every changed selector/action group requires WeChat native-node rectangle evidence at 320×568, 390×844 and 430×932, including each applicable filter state, long text and an open action menu. Assert dimensions, equal columns where applicable, horizontal/vertical gaps, overlap, containment and text clearance; retain screenshots for reading and wrapping review. Static CSS assertions, HTML previews and screenshots without native node rectangles cannot pass this geometry gate.
- Landscape needs a safe return/basic-action path but no dedicated MVP composition.

## Accessibility and inclusive content

- Use native controls and semantics where possible; preserve logical reading order, visible focus, accessible names and non-color status cues.
- Toast is supplemental; critical errors remain visible in the page.
- Content avoids ranking, mastery claims, blame, coercive streaks and gender/relationship stereotypes.

## Localization, formatting, and time

- Current locale is simplified Chinese; dates/times use server canonical values and display in Asia/Shanghai unless a later Spec opens multi-timezone support.
- Preserve `occurred_at` and `created_at`. User-entered relationship labels and long knowledge names wrap safely.
- Localization is deferred, but UI must not concatenate fragments that make later translation impossible.

## Browser, device, and progressive enhancement

- Supported runtime is the current production WeChat client on representative iOS and Android devices plus WeChat DevTools.
- Optional APIs require feature detection and an actionable fallback; unavailable camera/album access must not block manual text input.
- Web, desktop and dedicated tablet layouts are outside MVP scope.

## Performance and resource budgets

- Initial tab package budget is 1.5 MiB; no chart framework in MVP.
- List pages paginate or cap rendered history; uploads use bounded count/size and show real byte progress only when available.
- Avoid request waterfalls, duplicate polling, unbounded timers, base64 media persistence and large child images in page state.
- `FEC-PERF-READ-001`: a page never downloads complete history to build an aggregate or first screen;
  it consumes a server aggregate or a hard-bounded cursor page.
- `FEC-PERF-READ-002`: cursor state is remote state keyed by family/child/filter/range/load generation;
  context changes invalidate it and stale or duplicate responses cannot append.
- `FEC-PERF-READ-003`: page data and native node count remain bounded. More rows load only after the
  approved user action; a failure retains already loaded rows and uses an existing recoverable error path.
- `FEC-PERF-READ-004`: counts, units, range and truncation metadata shown together come from one server
  contract. Partial or inconsistent aggregates degrade explicitly and are never silently presented as complete.

## Client security, privacy, and trust

- The client never authorizes a family, child, role or manager action; all checks occur at the server boundary.
- Child images, OpenID, tokens, share tokens, AppSecret and raw model payloads never enter local storage, analytics, logs or error copy.
- Untrusted text uses normal text binding, never rich HTML. Share previews expose only minimum approved family/child labels.

## Tables, charts, and data integrity

- Use text/tables for exact comparison and simple CSS bars only when visual encoding improves a named decision.
- Reports state time range, units, missing data and timezone; essential values do not depend on hover or color.
- No mastery rate, ranking, child comparison, decorative pie chart or 3D chart.

## Motion, media, and generated/AI content

- Routine feedback uses restrained 150–240ms motion and remains usable with reduced motion.
- AI text is labelled “AI 整理草稿”; only parent confirmation creates formal records or deterministic review items.
- Media remains private, shows safe thumbnails only, and provides clear upload/failure/cancel states.

## Observability and analytics

- Release/error events use safe correlation IDs and state/error codes; no child content, identity token or media path is emitted.
- Events are deduplicated across page re-render/re-entry and cannot block the primary action.
- Product analytics are deferred until a privacy-approved schema and consent/retention policy exist.

## Verification matrix and commands

| Dimension | Required evidence |
|---|---|
| unit/state/contract | `npm test` |
| static mini-program rules | `npm run lint:miniapp` |
| repository validator | `uv run python tools/validate_miniprogram.py` |
| design evidence integrity | `uv run python tools/validate_design_evidence.py --manifest <APPROVAL.md>` |
| icon asset reproducibility | `uv run python tools/gen_icon_styles.py` then confirm an empty diff |
| architecture boundaries | `uv run python tools/check_architecture.py` |
| device/visual | WeChat DevTools compile/preview plus representative iOS and Android smoke |
| viewport/state | 320×568, 390×844, 430×932 captures for changed states |
| native control geometry | three-viewport native rectangles and automated dimension/gap/overlap/containment assertions for changed selector/action groups |
| privacy/authorization | contract/integration tests plus manual bundle/log inspection |

## Design evidence, exceptions, enforcement, and review

- A visible change requires a repository-local editable SVG or self-contained HTML source, exact required
  viewport/state PNG exports, matching SHA-256 values and explicit approval of the Task Spec revision + DREV.
- Figma, external design URLs, node IDs and tool-availability waivers are not required. Historical Figma and
  waiver records remain audit evidence but do not constrain new implementation or release work.
- Repository previews do not replace WeChat native geometry, interaction, accessibility or device checks.
- Other engineering deviations still require an approved Spec with owner, risk, expiry and remediation.
  Review checks design alignment, complete states, security/privacy, budgets and evidence.

## Constraint verification checklist

- [ ] Affected state/form ownership and error recovery are tested.
- [ ] Required viewport and device evidence is retained.
- [ ] Native selector/action rectangles pass equal-width, gap, fixed-target, no-overlap and containment checks at all three viewports.
- [ ] Touch, text, semantics and non-color cues are manually checked.
- [ ] Package/resource budgets are measured for material changes.
- [ ] Logs, local storage, share payloads and analytics contain no prohibited data.
- [ ] AI output remains labelled and editable until parent confirmation.
- [ ] Deviations are approved, owned and time-bounded.
- [ ] Editable design sources and approval exports exist and their SHA-256 values match the manifest.
