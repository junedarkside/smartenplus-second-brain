# Second Brain — Operational Log

Chronological record of vault operations. Parseable: `grep "^## \[" log.md | tail -5`

## [2026-05-20] session-end | forex 429 fix (backend c859f3b + frontend ff1f378) + admin HeroBanner UI committed (d3194d8); all 4 repos clean + pushed

## [2026-05-20] session-end | blog perf/SEO round 2 (6b655d6) — parallel fetches, image fixes, HMR infinite loop fixed; admin HeroBanner UI still uncommitted

## [2026-05-19] session-end | blog SEO fixes + perf optimizations committed (0f38cf8); admin HeroBanner UI still uncommitted

## [2026-05-19] ingest | DAYTRIP_DOCUMENTATION_SUMMARY.md — deleted from vault root, replaced with tour-system-status.md

- Source was a 2026-03-03 meta-index pointing to 36 repo docs. Low vault value — repo already has `docs/tour-system/INDEX.md`.
- Deleted: `DAYTRIP_DOCUMENTATION_SUMMARY.md` from vault root (wrong location, stale counts, just a directory map)
- Created: `01-projects/tour-system-status.md` — Phase 2 open gaps, trust signal fields, pointer to authoritative repo docs
- Core facts still valid: Contract/TimeSlot/ContractAddon/ContractTranslation models intact. 46+ commits since doc date — test/contract counts stale.
- See [[tour-system-status]], [[operators]]

## [2026-05-19] session-end | built vault session system — init/wrap-up protocols, master-state.md, optimized CLAUDE.md + master-state.md

## [2026-05-19] system | master-state.md created — mission control / session handoff

- New file at vault root alongside `index.md` and `log.md`. Partitioned by change frequency.
- Section 1 (every session): active branches, uncommitted changes, next step, last worked on.
- Section 2 (weekly): open loose ends, in-flight features, recently closed bugs.
- Section 3 (monthly): cross-repo API contract, auth rules, data shape gotchas, payment constants.
- Section 4 (rarely): architecture guardrails — lock order, payment rules, Celery patterns, heal commands.
- Updated `index.md` (41 pages) and vault `CLAUDE.md` Special Files table.

## [2026-05-19] session-end | blog/index.js style fixes (5 gaps) + design audit (9 gaps identified, not yet fixed)
- Solves baton-pass problem: AI reads this at session start instead of re-deriving state from git log.

## [2026-05-19] feature | Hero Banner CMS — backend-controlled homepage hero

- New `HeroBanner` model in `pages_info` app. `FileField` (not `ImageField`) — Pillow 9.3.0 has no AVIF decoder, `ImageField` rejected AVIF uploads.
- Backend: `/hero-banners/` CRUD endpoint + injected into `/front-page/` response. Migrations `0008`, `0009`.
- Admin dashboard: `heroBannersApi` RTK Query slice, `HeroBannerForm` with drag-and-drop, DataGrid CRUD page at `/routemanagement/hero-banners`.
- Frontend: `homepagev2.js` — 5s auto-slideshow via `setInterval`, fallback to `bgDefault` if no banners. SSG unaffected, no SEO impact.
- Key gotcha: `display_order` empty string → DRF rejects as non-integer. Fixed in FormData submit handler.
- See [[hero-banner-cms]]

## [2026-05-19] session-end | blog detail sidebar padding — iPad mini + iPad Pro flush-right fixed

## [2026-05-19] fix | Contract_TranspotComposit admin crash — frontend sentinel id=-1

- Root cause: frontend sends `id: -1` for new unsaved rows. Backend passed it as PK into `get_or_create(id=-1)` → UniqueViolation on every save attempt.
- Fix: `operators/views.py:739-774` — branch on `id <= 0` (new) → `create()` vs positive id → `get_or_create()`. Sentinel never enters keep-list.
- Pattern captured: sentinel ids must never be PK lookup keys. See [[operators]] Contract_TranspotComposit section + [[admin-dashboard-contracts]] Payload Rules.

## [2026-05-19] refactor | Nav/Header Redesign — Minimal White Style + A11y Baseline

- Desktop: white bg (`bg-white`), `border-b border-gray-200`, tab-style active link (`border-b-2 border-brand-primary`)
- Mobile: brand blue preserved. All icons/text: `text-white md:text-gray-600` pattern (hamburger, logo, cart, profile consistent)
- Replaced pipe separators with `<nav aria-label>` + flex gap-1
- A11y: `aria-current="page"`, `focus-visible:ring`, skip-to-content link, `<IconButton>` close on drawer
- Fixed profile icon clipping: ProfileImage Box 40→44px (chevron badge `-2px` overflow clipped by AppBar `overflow:hidden`)
- Fixed huge gaps: right cluster `justify-between` → `justify-end` (was spreading items across ~900px)
- Key gotcha: MUI AppBar needs `color="inherit"` for Tailwind bg classes to take effect
- Commit `082a154` on branch `260513-refactor/payment`
- Created: `nav-header-redesign.md`. Updated: `design-systems.md`, `index.md`, `log.md`

---

## [2026-05-18] fix | StickySearchBar empty route name on fresh page load

- Root cause: `StickySearchBar` reads only Redux `state.location.from_location/to_location`. Fresh load = empty Redux = blank route name.
- Fix: `FilterTripsPage` passes `fromSearch`/`toSearch` (URL slug-derived) as props. `StickySearchBar` uses `reduxValue || propValue` fallback.
- Same pattern already existed in `SearchCover` (`fromLocationRedux || initialFromLocation`).
- 2 files changed, ~6 lines. No new abstractions, no Redux dispatch.
- Updated: CLAUDE.md (Search/UI section), vault nextjs-patterns.md (Redux Fallback Props Pattern)

---

## [2026-05-18] fix | Profile 403 Forbidden — PUT endpoint migration + UX

- Root cause: `PUT /users/${userId}/` admin-only since 2026-05-07. Frontend never migrated PUT from old endpoint.
- Backend: `UserAPIView` changed `RetrieveAPIView` → `RetrieveUpdateAPIView` (adds PUT support)
- Frontend: `pages/account/profile.js` endpoint migrated `/users/${userId}/` → `/api/user/`
- UX: `id_or_passport` + `datofbirth` made optional (OAuth providers don't supply these)
- UX: Debug error summary replaced with MUI Alert + friendly field labels (touched-only)
- Commit `a1944df` on branch `260513-refactor/payment`
- Updated: CLAUDE.md, vault accounts.md, vault api-endpoints.md

---

## [2026-05-18] fix | multi-tab payment gaps — all 7 resolved (GAP-1→7), PAY NOW lock, daytrip build fix

---

## [2026-05-18] fix | Checkout Access Broken for Auth Users — session?.email Regression

- Root cause: commit `8b3151f` changed `session?.user?.email` → `session?.email` based on wrong CLAUDE.md doc
- NextAuth does NOT set `session.email` at root level — email lives ONLY at `session.user.email`
- Effect: `email = undefined` for all auth users → `useCheckCartIdQuery` got null email → cart query returned stale/empty data → checkout redirect fired → users bounced to home
- Blast radius: 3 code files + 2 CLAUDE.md doc lines
- Investigation method: 3-agent parallel team (vault reader, checkout investigator, cart-login investigator) + independent plan reviewer (PASS) + code reviewer (PASS) + debug specialist (0 lint errors, 0 remaining hits)
- Fix: `session?.email` → `session?.user?.email` in `pages/checkout/index.js:47`, `pages/checkout/PaymentComponent.js:150`, `pages/orders/[orderid].js:113`
- Doc fix: CLAUDE.md session structure bullet + cart reprovisioning bullet corrected
- Verified: guest path (`formData?.email`, `router.query.email`) untouched. All prior payment fixes unaffected.
- Commit `5b7fa3c` on branch `260513-refactor/payment`

## [2026-05-18] fix | GAP-1 Payment Processing Banner — Dead Code Activated

- Multi-tab payment research GAP-1: `isPaymentProcessing` never dispatched, `GlobalPaymentWarning` dead code
- Worse than documented: `setPaymentProcessing` imported in `PaymentComponent.js` but never called. Component had broken `isMounted` guard — timer never started
- Fix: full lifecycle — set on charge creation, clear on paid/timeout/rehydration/error
- Backend-sourced timing: `expires_at` from charge response drives countdown. Removed hardcoded `qr_expiry_minutes: 5`. Backend `METHOD_EXPIRY` is source of truth
- Files: `useOmisePayment.js`, `GlobalPaymentWarning.js`, `paymentStatusSlice.js`, `_app.js`, `PaymentComponent.js`, order detail pages
- `GlobalPaymentWarning` moved from `_app.js` to `checkout/index.js` — under step nav, same position as guest banner
- Uses `AlertMessage` component with `warning` type (added to AlertMessage alertStyles)
- `reconcileStaleProcessing` reducer: auto-clears if `paymentInitiatedAt` >30 min on rehydration
- Branch `260513-refactor/payment`

## [2026-05-18] refactor | GAP-3 Cart Mutation Error Handling — isPaymentPendingError Utility

- Multi-tab payment research identified 6 gaps (2 HIGH, 2 MEDIUM, 2 LOW)
- Picked GAP-3: cart item DELETE silent fail on 409 — best impact-to-effort ratio
- Key discovery: research doc referenced dead code (`Itinerary.js`, zero imports). Active component: `EnhancedTripCard.js`
- Extracted `helpers/handleCartMutationError.js` — shared `isPaymentPendingError()` used by 4 components
- Fixed `EnhancedTripCard.js`: non-409 delete errors now show Alert instead of silent close
- Fixed latent bug in `BookButton.js`: bare `error?.status === 409` matched ALL 409s, not just payment_pending
- Deleted dead `components/itinerary/Itinerary.js`
- Commit `2116530` on branch `260513-refactor/payment`
- Docs: `docs/features/payment/GAP3_CART_DELETE_ERROR_FIX.md`, `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`
- Updated `payment-integration.md` in vault: "Centralized Payment Error Detection" pattern

## [2026-05-18] fix | cartId Null After Payment Redirect — Cart Reprovisioning

- Root cause: `resetCart()` nulls `cartId` in Redux on order detail pages (correct behavior — paid cart abandoned)
- No mechanism existed to provision new cart before user navigated to booking page
- `withCartValidation` HOC creates cart on demand but trip/search pages are NOT wrapped with it
- Fix: `pages/orders/[orderid].js` + `pages/guest-order/[orderId].js` — call `createCart()` fire-and-forget after `resetCart()`
- Auth flow: `session?.email` (not `session?.user?.email`). Guest flow: `decodeURIComponent(router.query.email)`
- Commit `3c89bff` on branch `260513-refactor/payment`
- Pattern added to `payment-integration.md`: "Cart Reprovisioning After Payment Reset"

## [2026-05-17] fix | PAYMENT_PENDING 409 on Step Navigation — 5 Bugs Fixed

- Root cause: `formStep === 2` guard fired `savePassengerAssignmentsToCart` in non-mixed flow (step 2 = Confirmation, not Assignment) → 409 with pending charge
- Fix 1: `index.js:805` — added `&& hasMixedPassengerCounts` guard → non-mixed flow never PATCHes cart items on step 2→3
- Fix 2: `index.js:256-261` — removed premature `isPaymentLocked` reset effect (fired on same render cycle as lock was set, nullified it)
- Fix 3: `FormCard.js:41` — added `|| isPaymentLocked` to `shouldDisableNext` → Next button disabled when payment locked
- Fix 4: `index.js:767` — added `if (isPaymentLocked) return` at top of forward nav → navbar step-click also blocked
- Fix 5: `index.js:983` — `onUnlockPayment` now calls `refetch()` to invalidate stale cart cache after cancel
- Bonus: `FormCard.js:46` — `getValidationErrorMessage` now returns correct message when `isPaymentLocked`
- 3-agent team: debug-specialist + code-reviewer for diagnosis, 3 fix agents in parallel, reviewer verified all pass

## [2026-05-17] fix | session.user.email Root Bug — 3 Files Fixed

- Root bug: `pages/checkout/index.js:46` — `session?.user?.email` always `undefined` (session has no `.user` wrapper)
- `email` variable was always `null` for all authenticated users, propagated to cart query + cancel handlers
- Fix 1: `session?.user?.email` → `session?.email` in checkout/index.js
- Fix 2: `Itineraries.js` cancel handler rewritten with auth-aware Bearer token + proper guest email fallback
- Fix 3: `savePassengerAssignmentsToCart.js` dead `session?.user?.email` URL branch removed
- Updated `payment-checkout-e2e-testing-2026-05-17.md` Bug 4 resolved + Bug 5 documented

## [2026-05-17] test | Payment Checkout E2E Attempt — Failed, Manual Guide Created

- Wrote 4 Playwright specs (3873 lines total) via 6-agent team for payment checkout E2E
- E2E failed: MSW intercepts `api.smartenplus.co.th` but Playwright `baseURL` is `localhost:3000` — MSW never intercepts
- Only 1 test passed (code inspection, no API calls needed)
- E2E specs deleted (cart-lock, cancel-state-machine, qr-polling, payment-recovery)
- Manual test guide created: `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md`
- Bug fix still valid: `savePassengerAssignmentsToCart.js` chargeId extraction (commit `38c7320`)
- data-testid attrs added to Input, Textarea, Passengers, PaymentMethodSelector (still present)
- Updated `payment-checkout-e2e-testing-2026-05-17.md` in vault

## [2026-05-17] test | Payment Checkout E2E Testing — 6-Agent Team

- Spawned 6 agents to test payment checkout flows end-to-end
- 4 E2E specs written: cart-lock (11 tests), cancel-state-machine (23 tests), qr-polling (24 scenarios), payment-recovery (16 tests)
- Audit results: Frontend 10/10, Backend 10/10, QR polling pass, Cancel spec valid
- Bug found: `savePassengerAssignmentsToCart.js` missing `chargeId` in cart 409 — 1-line fix (commit `38c7320`)
- Infrastructure issue: missing `data-testid` attrs — added to Textarea, Input, Passengers.js, PaymentMethodSelector.js
- Created `payment-checkout-e2e-testing-2026-05-17.md` in vault
- Updated index.md

## [2026-05-17] audit | Payment Checkout Architecture Audit — 20/20 Pass

- Audited smartenplus-frontend + smartenplus-backend against `PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`
- 20/20 items validated pass (10 frontend, 10 backend)
- One medium gap fixed: `getPrimaryCharge()` sort order corrected (oldest-first → latest-first)
- PromptPay intentional exclusion from one-active-lock per architecture doc
- Created `payment-checkout-architecture-audit-2026-05-17.md` in vault
- Updated MEMORY.md (SB), `project_payments_app.md` (SB)

## [2026-05-17] retro | Payment Refactor — Session Retrospective + Vault Update

- Branch `260513-refactor/payment`: 12 frontend files (+465 lines), 7 backend files (+233 lines)
- Fixed 7 frontend gaps (F1–F6 + QR expiry) and 4 backend gaps (B1–B4) vs architecture doc
- 25/28 use cases covered, 3 partial (Phase 2: WebSocket, admin reconcile UI, webhook replay)
- 5 mistakes documented: over-broad FormCard guard, positional alert text, settings.json schema, auth email param, dual cancel surface
- Key lessons: child terminal state → parent callback, sessionStorage init after persist rehydration, auth-conditional params key off token not email, dual UI surfaces sharing chargeId must be mutually exclusive
- Updated `payment-integration.md` with 8 new patterns
- Vault: log.md updated, index.md updated

## [2026-05-16] update | Repay Failure RCA — Phase 1 + Phase 2 Complete

- User couldn't repay after refresh or cart update
- Identified 8 frontend root causes → all fixed
- Phase 2 backend: idempotency key, reconciliation endpoint, CheckoutSnapshot model, expire protection
- Frontend integration: X-Idempotency-Key header, ORDER_ALREADY_PAID handling, cross-tab cart sync
- Updated: CLAUDE.md (frontend patterns), REPAY_FAILURE_RCA.md, PHASE2_BACKEND_IMPLEMENTATION.md
- Updated: payment-system.md (vault), index.md

## [2026-05-16] bootstrap | Vault Initialized

- Created vault at `~/second-brain`
- Bootstrapped full structure: 9 folders, 3 root files, 4 templates, 4 project seeds, 4 knowledge seeds
- Seeded SmartEnPlus project knowledge from existing 550 docs (synthesized, not copied)
- Git initialized with `.obsidian/` in gitignore
- Key decisions: flat folder structure, no frontmatter, wikilinks only, no raw sources folder yet

## [2026-05-16] seed | SmartEnPlus Project

- Created `01-projects/smartenplus/` with 4 pages
- README: project overview, stack, 3-repo ecosystem
- Architecture: Pages Router, Redux slices, RTK Query APIs, component tree
- Payment System: Omise, GatewayCharge, QR polling, canonical charge rule
- Checkout Flow: SSR-disabled, cart item keys, passenger assignment, guest mode

## [2026-05-16] seed | Knowledge Base

- Created 4 knowledge pages in `03-knowledge/`
- AI Workflows: LLM Wiki pattern (ingest/query/lint), three-layer architecture
- Next.js Patterns: ISR cache, dynamic imports, RTK Query, DatePicker handling
- Payment Integration: Thai methods, Omise source types, webhook reconciliation
- Design Systems: Token approach, COLORS/SPACING/BORDER_RADIUS/TYPOGRAPHY_SCALE

## [2026-05-16] update | Backend Documentation Ingest

- Created [[backend-architecture]]: Django app structure, key models, API endpoints, Celery tasks, dev commands
- Updated [[payment-system]]: added 11 backend sections (finalize_payment, locked_amount, ExpirePendingChargeView, IdempotencyKey, WebhookEvent audit, JPY handling, polling fallback, notification dedup, status machines, charge creation order, ManualAdjustment)
- Updated [[payment-integration]]: added idempotency sentinel pattern, amount locking pattern, webhook audit pattern
## [2026-05-19] fix | Breadcrumb + CategoryMenu Tech Debt + Blog Spacing Consistency
## [2026-05-20] session-end | Recommend-route review + partial implementation — hydration issue blocking
