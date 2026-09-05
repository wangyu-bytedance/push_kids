# Push Kids frontend engineering contract

## Constraint identity and approval

- Frontend engineering scope: PRESENT
- Constraint status: APPROVED
- Constraint revision: FEC-20260830-01
- Owner: 产品负责人（用户）
- Approved by: 产品负责人（用户）
- Approved at: 2026-08-30
- Approval evidence: 用户批准 FEAT-001 实现并授权在既定设计基线下完成原生微信小程序
- Related frontend design baseline: FDB-20260830-01
- Applies to: `apps/miniprogram`

## Engineering priorities and stack boundary

- Runtime is native WeChat Mini Program using WXML, WXSS, CommonJS JavaScript and platform APIs.
- Server is authoritative for identity, authorization, learning facts, job state, review state and reports.
- Client pages map gestures to API operations and render explicit states; they do not own business policy.
- Do not add a cross-platform framework, chart library, state framework or rich-text renderer without an approved Spec.

## Information architecture and action hierarchy

- Primary tabs remain 今日、记录、报表、设置; onboarding, submission, confirmation, family application and approval are deep flows.
- Each page exposes one dominant action. Secondary and destructive actions are visually separated.
- Manager-only actions may be hidden for usability, but server authorization remains authoritative.

## Design tokens and component contracts

- Global semantic colors, spacing, radii, typography and safe-area values live in `app.wxss`.
- Pages must not create near-duplicate token scales. Reusable components require shared product semantics, not visual similarity alone.
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
| architecture boundaries | `uv run python tools/check_architecture.py` |
| device/visual | WeChat DevTools compile/preview plus representative iOS and Android smoke |
| viewport/state | 320×568, 390×844, 430×932 captures for changed states |
| privacy/authorization | contract/integration tests plus manual bundle/log inspection |

## Exceptions, enforcement, and review

- FEAT-001 has a scoped Figma Starter-plan evidence waiver in `ARCHITECTURE.md`; it expires before public production release and does not cover FEAT-002.
- Visible FEAT-002 work requires a new approved Figma Design Revision and snapshot unless the user explicitly approves another scoped, owned, expiring waiver.
- Exceptions require an approved Spec with owner, risk, expiry and remediation. Review checks design alignment, complete states, security/privacy, budgets and evidence.

## Constraint verification checklist

- [ ] Affected state/form ownership and error recovery are tested.
- [ ] Required viewport and device evidence is retained.
- [ ] Touch, text, semantics and non-color cues are manually checked.
- [ ] Package/resource budgets are measured for material changes.
- [ ] Logs, local storage, share payloads and analytics contain no prohibited data.
- [ ] AI output remains labelled and editable until parent confirmation.
- [ ] Deviations are approved, owned and time-bounded.
