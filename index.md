# Second Brain — Index

Global navigation catalog. Updated on every ingest.

---

## Meta

- [[master-state|Master State]] — Live session state: branches, loose ends, API contract, architecture guardrails

## Knowledge — SEO/AEO

- [[trip-detail-server-side-seo-pattern]] — Pattern for moving client-side SEO hook to server-side `getStaticProps` on transport product pages. 5 pure util functions, thin renderer component, no hooks. Fixes AEO root cause (schema in SSR HTML). Key rule: JSON-LD payload functions return fields only — `CustomJsonLd` owns `@context`/`@type`.

## Knowledge — UX/Design

- [[unified-badge-system-pattern]] — Multi-badge card rows: one geometry, differentiate axes (status/category/type) by fill+icon NOT clashing hue; non-ordinal sets get one color + distinct icons; colors from tokens. Twin-component over fork/premature-primitive. From operators card fix #124.
- [[mobile-search-bar-ux-competitor-research-2026]] — Mobile sticky search bar competitor research + redesign direction. Chip pattern, brand-blue CTA, drop "One Way" label. Branch: `feat/mobile-search-bar-redesign`.

## Active Projects

- [[homepage-search-transportation-experiences-tabs-2026-06-17]] — **PLAN 2026-06-17.** File-by-file impl plan for homepage Transportation|Experiences search tabs (from [[adr-homepage-search-transportation-experiences-tabs-2026-06-17]], audited). Split 379-line ProductSearchForm2 into shared fields + 2 mode forms + segmented control (local useState). Hero → reuse FeaturedImageHeader (isCinematic). Experiences = Destination+Category → /activities?location=&category=. Key audit fix: do NOT reuse ActivitySearch (forces dayTripsApi RTK + locations API onto homepage); use AutoCompleteSearch. Tokens via helpers/designSystem.js.
- [[operator-card-badge-consistency-2026-06-16]] — **SPEC 2026-06-16.** 2-agent (design+frontend) fix for "AI slop" contract-card badges on `/operators/[slug]`. Root cause: 3 badge systems/row (3 radii, 2 heights, MUI-Chip vs raw-span) + JOIN renders success-green next to status badge. Fix: canonical Chip geometry, one neutral indigo for all contract types (icon+label differentiate, not hue), new scoped `ContractTypeBadge`, friendly `CONTRACT_TYPE_NAMES` labels. Verified: delete only `tourTypeSoft` (operators-only); KEEP `tourTypePrivate/Charter` (used by BadgeChip). No `BadgeChip` touch, no MetaBadge abstraction. Spec only.

- [[operator-detail-seo-aeo-geo-audit-2026-06-16]] — **AUDIT 2026-06-16.** 3-specialist SEO/AEO/GEO audit of `/operators/[slug]` post-redesign. Zero JSON-LD (top finding all 3 lenses), `<title>` double brand-suffix bug (hand-verified vs `_app.js:37` titleTemplate), canonical relative-URL risk (fix via `getSiteUrl()`). GEO thin until backend `description` field. Policy gate: `aggregateRating` only on bookable items (Product/TouristTrip), NEVER operator Org node — provenance confirmed first-party (`dialogue.Review is_approved` on Contract) but Google bans self-serving Org review markup. Most fixes frontend-only, reuse trip-detail SEO helpers. Read-only, leader hand-verified title bug + rating provenance.

- [[operator-detail-page-redesign-2026-06-16]] — **SPEC 2026-06-16.** 3-agent debate (UX→Design→Frontend) redesign of `/operators/[slug]`. Converged: hero-weighted header + operator-specific stat trio (rating/reviews/route count), type-filter pills→MUI tabs, dead `KeyHighlights`/`FeaturedImageHeader` imports removed, filter bar extracted (`OperatorFilterBar.js`, 200-line guideline). Tab per-type counts blocked on backend `by_type` aggregation. No code shipped — spec only.

- [[seo-sitemap-whole-site-audit-2026-06-11]] — **MERGED 2026-06-12** (`1f3f7a2` → develop `d88f50b`, pushed). 3-agent whole-site SEO+sitemap audit → P0+P1+P2 implemented: fake reviews deleted ×**4** sources (impl found 4th in AirportTransferJsonLd.js), sitemap 128→86 URLs + robots disallows, noindex fixed/added on 5 private pages, activities canonical → NEXT_PUBLIC_DOMAIN, 480-line dead JSON-LD pipeline deleted, hreflang removed, xmlns http://, 301s for homepagev1/v2 + trips/detail, Promise.all + escapeXml in server-sitemap, GTM out of Head. Build exit 0, 8 regression greps clean. Remaining: deploy to prod, P0-1 GSC/WAF verify (manual), P0-6 nginx 301s (infra), P1-3 soft-404 per [[gsc-crawled-not-indexed-investigation-2026-06-05]], P3 dead-code sweep.

- [[frontend-architecture-audit-2026-06-11]] — **OPEN 2026-06-11.** Full FE architecture audit (state/components/fetching/perf/maintainability), 3 explorers + hand-verification. No critical bugs — architecture sound. 3 confirmed LATENT bugs: useEffect inside Formik render prop ×2 (`Passengers.js:629,706` — **debug-mantra falsified: NOT critical, no crash today** since Formik calls children once/render unconditionally → constant hook count; risk is future-edit between 625–706 + misleading eslint-disable), dead auth branch reading `getState().session` (tripsApi+dayTripsApi — NextAuth session never in Redux), wrong store key `dayTrip` vs `activities` (Accept-Language stuck 'en'). `bumpCartVersion` duplicated ×2 with manual-sync comment. 5 dead-code items grep-verified (lines*/, omisecharge/, GridComponent2, cart-migration-v1, dummy-data). Hygiene: 5 .backup files + logs git-tracked. Oversized checkout files ruled refactor-on-touch only. 4 explorer findings overturned (cloneElement memo claim FALSE, context deps claim FALSE). Checkout/payment logic excluded — see [[booking-payment-e2e-audit-2026-06-11]].

- [[frontend-audit-implementation-2026-06-11]] — **COMPLETED 2026-06-11.** All 9 audit items resolved across 3 PRs: PR1 Formik extract, PR2 4 RTK Query cleanups, PR3 dead code + hygiene. 1 cross-branch contamination incident recovered; 1 unresponsive implementer replaced. Sequential pattern adopted post-incident. Lint + build clean. 3 manual PR opens pending (no `gh` CLI).

- [[payment-deep-review-2026-06-12]] — **OPEN 2026-06-12.** 3-agent payment deep review (FE / BE / cross-repo contract) + leader hand-verification, extends [[booking-payment-e2e-audit-2026-06-11]] with zero re-derivation. 5 HIGH all leader-verified: client-controlled charge amount (no server-side total check), legacy webhook live with verification commented out, idempotent order-reuse bare response shape breaks coupon/cancel refetch (+ keyless-branch NameError), FE drops `charge_id` so explicit QR cancel-on-leave never expires, paid-but-unfinalized order invisible (mismatch swallow + reconcile gate excludes `payment_pending` + FE success from charge status alone). ~15 MEDIUM (refund over-record, orphaned Omise charge race, guest charge no email proof, KakaoPay dead end-to-end, 3DS excluded from sweeps, lock-order inversion), ~15 LOW, 10 test gaps, 4 doc drifts, BE-F9 currency claim overturned. Suggested fix order in note. Report only — no code changed.

- [[payment-deep-review-verification-2026-06-12]] — **OPEN 2026-06-12.** KB verification pass on [[payment-deep-review-2026-06-12]]: 3 Explore agents cross-checked all 5 HIGHs + 18 MEDIUMs against ~1700 lines of vault payment/omise KB + read-only code spot-checks. **20 CONFIRMED · 2 REFINED (H1, M17) · 1 REFUTED (M4) · 1 KB inaccuracy (M8) · 12 KB gaps surfaced.** **M4 REFUTED** — claim that BE emits `{error:'payment_pending'}` is wrong; canonical code is `pending_charge_exists` and FE maps it (M4 subsumed by M1). M8 KB inaccuracy: [[payment-backend-charge-flow]] §5 claims email validation in `ChargeOrderView`; code shows it's only in `ExpirePendingChargeView`. 12 KB gaps (atomization candidates): payment-amount-validation-rule, payment-legacy-deprecation-map, IntegrityError cleanup pattern, order-creation-filter-rule, self-heal coverage matrix, payment-model-fields, payment-method-name-contract, useQRPolling 4xx branch, usePaymentInitialization lifecycle, usePaymentCouponManager state machine, refund validation rule, order-create response envelope contract. Implementation plan in [[payment-implement-plan-2026-06-12]].

- [[payment-implement-plan-2026-06-12]] — **OPEN 2026-06-12.** 5-batch production-safe fix sequence derived from [[payment-deep-review-2026-06-12]] + [[payment-deep-review-verification-2026-06-12]]. Batch 1: H3+H4 (~6 lines, kill 2 UX breakages). Batch 2: H2+M10 (delete legacy routes, verify zero prod traffic first). Batch 3: H1+M8 (security pair). Batch 4: H5+M5 (resilience pair). Batch 5: M1–M4, M17, LOW sweep (refunds, dead code, doc drifts, test gaps). Per-batch: file:line, exact change, verify commands, test gaps to close. NO code changes yet — implementer session picks this up.
- [[payment-deep-review-test-cases-2026-06-12]] — **OPEN 2026-06-12.** Test cases for payment deep review fixes: 8 smoke tests (curl), 7 manual UI tests (QA-run), 7 E2E unit test specs (developer-writes). Pre-flight: FE lint+build PASS, BE ruff+syntax PASS, BE unit tests SKIP (pre-existing migration error).
- [[payment-manual-test-skip-2026-06-12]] — **SUPERSEDED 2026-06-12.** Runbook for 8 Playwright tests skipped due to missing test data + dev/staging env. All 8 now automated — see [[payment-auto-test-results-2026-06-12]]. Kept as reference; SUPERSEDED notice at top of file.
- [[payment-auto-test-results-2026-06-12]] — **NEW 2026-06-12.** All 8/8 payment E2E tests automated + PASS. Spec: `payment-auto-qa.spec.ts`, fixture CLI: `e2e_payment_fixtures.py`. Architecture, key gotchas (8 items), webhook delivery via Tailscale (all 5 steps PASS). Gaps remaining: card 3DS iframe + live-key prod smoke (deploy-time only).

- [[payment-pending-deadlock-2026-06-12]] — **OPEN 2026-06-12.** Live prod bug: order `PLB0229785` stuck `payment_pending` despite charge PAID at Omise. Debug Mantra verified: `ExpirePendingChargeView` returns 400 for non-pending charges, `reconcile_gateway_charge` skips non-pending, no retry for `finalize_payment` after `PaymentAmountMismatchError`. Two backend fixes: (1) expire endpoint recovery for paid/failed charges, (2) reconcile retry for paid+unfinalized. Zero frontend changes. Related: [[payment-deep-review-2026-06-12]] H5.

- [[booking-payment-e2e-audit-2026-06-11]] — **CLOSED 2026-06-11 (#97).** Full booking→checkout→payment audit, FE+BE. 4 confirmed bugs fixed across 2 sessions. C1/C2 both fixed `cb817d9`: C1 = `isCartLoaded &&` gate stops premature clear-assignments before RTK Query resolves; C2 = `error?.status === 404` guard stops transient errors from nuking cartId. All bugs resolved.

- [[website-audit-full-2026-06-06-overview|website-audit-full-2026-06-06]] — **OPEN 2026-06-06.** External website audit: SEO 75/100, Speed 40/100, A11y 85/100. Critical: 10 blocking scripts, 66 inline styles, 18 non-WebP images, 13/18 touch targets <44px. Blog outranking booking pages (content depth gap). 15 priority actions ordered by impact. **3-specialist team review done:** 15 → 12 P0-P3 items with file:line refs + sprint plan. 6 audit items reclassified as ALREADY DONE (compress, WebP config, GTM deferred, InArticleCTA, ProductJsonLd on Experience, BreadcrumbList on Experience). ~18 hrs impl work. Working files: `r1-performance`, `r1-mobile-ux`, `r1-seo-ai`, `r2-skeptic`, `r3-leader-synthesis`.

- [[rate-review-uxui-audit-2026-06-06-overview|rate-review-uxui-audit-2026-06-06]] — **OPEN 2026-06-06.** 4-specialist UX/UI audit of `/rate-review` flow (list, detail, submit-review). 52 raw findings → 34 unique actionable (3 P0, 10 P1). P0: stored XSS (`dangerouslySetInnerHTML` no DOMPurify at `[reviewSlug].js:455`), `parseISO(null)` page crash (`BookingReviewList.js:43-45`), star rating ARIA broken (multiple simultaneous `aria-pressed`). P1: wrong router import breaks "Write Review" CTA, unmasked email GDPR violation, redirect produces `/rate-review/undefined` after submission. Implementation order in `r3-leader-synthesis.md`. Overall health: 4.5/10.

- [[gsc-crawled-not-indexed-investigation-2026-06-05]] — **IN PROGRESS 2026-06-05.** 52,400 "Crawled Not Indexed" root cause investigation. 3-team adversarial review. Primary cause: empty ISR trip pages (88% confidence), NOT URL pollution. `notFound: true` blanket approach OVERTURNED — 14 Koh Lipe seasonal routes at risk. 3-phase safe plan: sitemap filter → surgical noindex → three-tier model. Data collection required before any code change.

- [[blog-canonical-url-wp-subdomain-bug]] — **FIXED 2026-06-05.** GSC "Alternate page with proper canonical tag". `String.replace('http://...')` silently failed on HTTPS WP `opengraphUrl`. Canonical = WP subdomain. Fix: derive from slug. Also fixed help page regex + missing www. `3d30407` → develop.

- [[homepage-terminology-audit-2026-06-05]] — **COMPLETED 2026-06-05.** 3-agent SEO+UX+Tech audit of homepage nav/section terminology. Phase 2 production SEO review overturned /locations→/destinations consolidation (different products). Implemented: "Journeys"→"Routes", "Explore Thailand"→"Destinations", H1 fix on activities page. 3 atoms extracted.

- [[frontend-test-infrastructure-audit-2026-06-03]] — **BLOCK RELEASE 2026-06-03.** 5-agent team: Jest (719 tests, 30% fail) + Playwright (260 tests, 90% fail). 3.92% coverage vs 70% threshold. 6 CRITICAL issues: 0% BookButton coverage (payment path), checkout 30s timeout, mobile 100% fail, jest-axe missing, MUI emotion mismatch. 4-5 dev days to fix. Money flow (checkout → payment) completely unverified.

- [[experience-detail-page-redesign-2026-06-02]] — **PLANNED 2026-06-02.** Premium redesign of `/activities/detail/[slug]` → Airbnb-level experience detail page. Airbnb 5-up photo grid, trust badges, reviews moved up, timeline collapsed, 9 new components, 0 new API endpoints.
- [[experience-faq-architecture-review-2026-06-02]] — **DECISION 2026-06-02.** FAQ section on experience detail page audit. 5 sites mapped cross-repo: 1 customer-visible (hardcoded cancel text = legal risk for strict-policy operators), 4 staff/dormant (admin `age_restriction` missing, assumed API field doesn't exist, 2 generic fillers). Decision: document + 1 help-text fix, no model consolidation. Admin `age_restriction` edit deferred.

- [[gyg-page-analysis-2026-06-04-overview|gyg-page-analysis-2026-06-04]] — **INCREMENTAL 2026-06-04.** 3-specialist GYG Chiang Rai tour (product 846675) analysis vs SmartEnPlus activity detail page. 11 candidates → 5 adopted (P0 footer meta strip, P1 not-suitable-for badges + review thumbnails, P2 review sort/filter + itinerary disclaimer). 4 P3 backend debt flagged (audio guide, private group, per-aspect rating, provider response). AI summary user-deferred.

- [[experiences-2026-marketplace-redesign]] — **PLANNED 2026-06-01.** 4-phase redesign of `/activities` → world-class 2026 marketplace. Sidebar layout, 4-col grid, premium card, sort bar. Phase 1: frontend-only. Phase 2: backend filter params. Phase 3: mobile. Phase 4: iPad polish.

- [[profile-dropdown-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** 3-specialist review. 11→6 items, 296px, pill trigger, bottom sheet mobile, 3-file split. MUI-preserve strategy. Implemented on `260528-feat/header-redesign-2026`.

- [[check-your-booking-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** OTA utility card adopted. Illustration removed. 840px centered card, warm-surface bg, larger inputs, trust row with fixed copy. Eyebrow removed per judge ruling.

- [[destinations-redesign-review]] — Destinations section review: editorial grid vs carousel tradeoffs, image overlay patterns, mobile-first layout decisions.
- [[featured-image-header-width-bug-2026-05-30]] — **RESOLVED 2026-05-30.** `w-[1200px]` hardcoded in `0ebd755` broke mobile. Fix: revert to `w-full` + `max-w-[1200px]`. Rule: never use `w-[Npx]` on layout-spanning elements. `FeaturedImageHeader.js:121`.
- [[airport-transfer-width-audit-2026-05-30]] — **UNRESOLVED.** Post-calendar sections (StationInformation + GuidesSection) visually narrower than calendar. Root cause: inner `px-2 md:px-3` + `mx-2` margins eating into max-w-[1200px] content. Fix attempt reverted (broke layout). Next team: redesign sections as full-width with centered inner content, OR accept current padding as correct. Shared component `ProductCardContainer.js` involvement complicates fix.
- [[header-redesign-2026-spec]] — **FINAL 2026-05-28.** Adaptive Type A/B header. Type A: single-row 80px (transactional). Type B: 2-row 96px (discovery/browse). All 5 nav items kept. /blog → Type B. Dynamic layout offset. 12-file implementation plan. 4-day rollout + 2 separate PRs.
- [[hero-back-share-buttons-2row-header-fix]] — **UNVERIFIED 2026-05-30.** Back/Share pills moved from `FeaturedImageHeader` to outer wrapper of `TripDetailHero`/`DayTripHero`. Glassmorphism style. Server was in production mode — needs `npm run dev` to verify. See note for full debug trail + root causes.
- [[header-redesign-2026-implementation]] — **Days 1–3 DONE 2026-05-28.** Branch `260528-feat/header-redesign-2026` commit `a4158b0`. 10 files. QA + AT-1 redesign pending before merge.
- [[timeline-update-display-bug-2026-06-01]] — **RESOLVED 2026-06-04.** Root cause: Django `continue` skipping placeless stops from `existing_place_ids` → delete sweep wiped all stops. Fix: 5 changes across 3 repos + migration 0028. See [[django-nested-delete-sweep-pattern]].
- [[activities-day-tour-page-review-2026-06-01]] — 3-specialist code audit of `/activities?category=DAY_TOUR`. 2 Critical (skeleton mismatch, dual unlabeled search), 5 Major, 5 Minor. Fix sequence documented.
- [[activities-location-search-bug-2026-06-01]] — **IN PROGRESS.** 4-specialist team audit. Location search returns zero results. 3 critical bugs: backend text→ID type mismatch (`products/views.py:446`), `inputValue` divergence (`DayTripLocationSearch.js:20`), freetext not emitting to parent (`DayTripLocationSearch.js:26`). Fix sequence documented.
- [[activities-search-merge-review-2026-06-01]] — **UPDATED 2026-06-01.** 3-specialist review + grill. True merge "backend blocker" claim OVERTURNED — intent detection via static `keywords[]` match, no backend change needed. Blocked by tech debt: 2 incompatible `POPULAR_DESTINATIONS` sources. Next: consolidate → `utils/destinations.js` (ACT-5), then build unified `ActivitySearch` (ACT-6).
- [[header-redesign-2026-team-review]] — 3-specialist audit (Design+UX+Frontend) + second audit (UX Architecture+Visual Design+Frontend Eng). All blockers resolved. Key decisions locked: Type A/B split, keep Explore Thailand, /blog = Type B, dynamic offset 80/96px, HeaderRowsContext pattern.
- [[backend-n8n-resend-webhook]] — Resend Operator n8n webhook forwarding. send_booking_data moved to bookings/tasks.py. 4 commits, merged to develop. 3 bugs caught by scrutinize audit (import crash ×2, orphaned try block) + 1 env var crash on startup (N8N_WEBHOOK_URL missing default=None)
- [[fast-refresh-infinite-loop-audit-2026-05-23|Fast Refresh Infinite Loop Audit 2026-05-23]] — Root cause unconfirmed. RefreshTokenHandler diagnosis OVERTURNED (lastExpiryRef guard). Likely Next.js 14.2.x HMR + on-demand compilation cascade. 7 failed fixes documented. Next: debug instrumentation + git bisect
- [[currency-context-infinite-fetch-2026-05-23|CurrencyContext Infinite Fetch 2026-05-23]] — race condition + unstable selectCurrency ref; fix applied on branch 260523-fix/currency-context-infinite-fetch
- [[currency-context-price-rendering-rule]] — **NEW 2026-06-15.** `useFormatPrice()` is canonical for all user-facing price labels (7 components now: `TripItem`, `FilterTrip`, `TripDetailBooking`, `RouteFAQ`, `TripItemAccordionContent`, `SlideCalendar2`, `TripSummary`). JSON-LD `Offer.price` + `priceCurrency` stays as raw THB (merchant base, not viewer display). SSR-safe via `CurrencyContext` null→THB fallback. Audit checklist: grep `toLocaleString()` + literal `"THB"`/`"฿"` in `components/`.
- [[isr-429-cold-start-fix-2026-05-23|ISR 429 Cold-Start Fix + Stale Data 2026-05-23]] — cold `npm run dev` bursts `/front-page/` → 429; root: REVALIDATE_SECONDS=60 + refetchOnMountOrArgChange:300; fixes identified. + ISR stale data in Docker standalone, on-demand revalidation fix via Celery task
- [[README|SmartEnPlus]] — Thailand transport booking platform (Next.js 14, Redux, Omise)
- [[architecture|SmartEnPlus Architecture]] — Redux slices, RTK Query, component structure
- [[checkout-flow|SmartEnPlus Checkout]] — SSR-disabled checkout, cart, guest mode
- [[backend-architecture|SmartEnPlus Backend]] — Django apps, models, Celery, Docker
- [[operators|Operators]] — Contract, TimeSlot, ContractAddon, ContractTranslation, tour system
- [[tour-system-status|Tour System Status]] — Phase 2 gaps (time slot UI, add-ons UI), trust signal fields, authoritative doc pointers
- [[orders|Orders]] — Order, Payment, Coupon, PassengerDetail, WebhookEvent, ManualAdjustment, lock order canonical
- [[bookings|Bookings]] — BookingItem, BookingItemAddon, ExtraItem, confirmation flow
- [[cart|Cart]] — CartItem, CartItemAddon, CartItemCheckoutInfo, Phase 2 checkout persistence
- [[accounts|Accounts]] — Account (custom user), LoggedInUser, FamilyAndFriend
- [[billings|Billings]] — BillingProfile, PaymentMethod (all Thai payment types)
- [[api-endpoints|API Endpoints]] — all public/admin/payment/cart-order endpoints
- [[docker-production|Docker Production]] — docker-compose-rds.yml, memory budgets, deploy
- [[coupons|Coupons]] — Coupon model, times_used F()+1, restrictions
- [[stations|Stations]] — Station, Location, Place, Timeline, RouteByLocationInfo
- [[policies|Policies]] — CancellationPolicy, CancellationPolicies, BaggagePolicy, GeneralInformation
- [[dialogue|Dialogue]] — Review, Thread, Post, Comment, Reaction (WordPress), GenericForeignKey patterns
- [[recommendation-system|Recommendation System]] — precompute tasks, cache warming, beat schedule, Popular Routes admin analytics page
- [[cross-sell-placement-strategy]] — **NEW 2026-06-09.** Industry standard cross-sell placement: post-booking #1 (built+mounted), trip detail #2 (live), checkout sidebar = avoid. Filtering rules: same-route exclude (station→location fallback), operational_day weekday, price filter. BD gap: no DAY_TOUR/SPA at Koh Lipe blocks value.
- [[people-also-book-checkout-audit]] — **AUDIT+FIXED 2026-06-10/11.** 3-agent + debug-mantra audit. 1 real bug confirmed (3 overturned): duplicate toast caught 409 but backend returns 400 — fixed `a64d280`. Anchor stability + ghost-item filter fixed `d64adcf`. 3 atoms extracted.
- [[rtk-cart-tag-invalidation-auto-refetch]] — Cart mutations invalidate `Cart:{cartId}` tag → `checkCartId` auto-refetches. No `onSuccess` callbacks needed. `recommendationsApi` is separate slice — NOT invalidated by cart mutations.
- [[recommendation-anchor-first-transport-rule]] — Anchor = first transport (not last). Last transport causes circular recommendations when cross-sell transports added. `CheckoutRelatedTrips.js:27`.
- [[django-400-vs-409-duplicate-cart-item]] — Backend raises 400 (not 409) for duplicate cart items. Frontend must catch 400 + check `includes('already exists')`. 409 = payment_pending only.
- [[rtk-lazy-query-tuple-misuse]] — **NEW 2026-06-11.** `useLazyXQuery` returns `[trigger, result]` tuple, takes no args — passing args + object-destructuring = silent dead code, no request fired. Detection grep: `} = useLazy`. Found live in `BookButton.js:41-43`.
- [[activity-to-activity-cross-sell]] — **NEW 2026-06-11.** `find_nearby_activities()` pivots on `primary_location`/`service_areas`. Dispatch requires `arrival_station` check (not just trip+route). 3-signal scoring: location base 50 + same category +30 + quality score 0–20 + exact location +10.
- [[booking-widget-availability-error-display]] — **NEW 2026-06-11.** DayTripBookingWidget Alert must render all 6 error flags. `advanceHourPassed` + `nonOperatingDay` were missing → blank red box. `ADVANCE_HOUR_PASSED` constant added to `dayTripConstants.js`.
- [[redux-persist-gate-scope-gap]] — **NEW 2026-06-11.** PersistGate doesn't wrap `<Component>` (`_app.js:90-97`) — pages mount pre-rehydration. Restore effects need `state._persist?.rehydrated` guard; clearing effects must also wait for API data or they gut state a later restore needed (C1 chain).
- [[checkout-formdata-persist-guard-pattern]] — **NEW 2026-06-11 #97.** C1: `isCartLoaded = !!data` gates clear-assignments effect — stops premature clear before RTK Query resolves on mount. C2: `error?.status === 404` guard in HOC catch — transient 500/network errors preserve cartId. RTK Query error shapes documented (numeric HTTP status vs string FETCH_ERROR/TIMEOUT_ERROR).
- [[tickets|Tickets]] — Ticket model, GenericForeignKey attachable to any model, HistoricalRecords audit
- [[admin-dashboard|Admin Dashboard]] — Admin interface for SmartEnPlus platform
- [[smartenplus-glassmorphism-header|Premium Glassmorphism Header]] — dark gradient glass, sticky + blur on scroll, unified 2-row, white typography, hero integration. Supersedes header-ux-v1.
- [[adr-experiences-nav-category-filtering-2026-05-25|ADR: Experiences Nav Category Filtering]] — URL param → server-side API filter chain. Full category enum, navConfig values, contrast with client-side approach.
- [[adr-homepage-search-transportation-experiences-tabs-2026-06-17|ADR: Homepage Search Transportation\|Experiences Tabs]] — **PROPOSED 2026-06-17.** Add segmented control to homepage search. Hero reuses FeaturedImageHeader (isCinematic). Experiences tab = Destination+Category only → `/activities?location=&category=` (mirrors activities page real search; `/activities` reads only location+category — Date/Guests dropped, no backend = would be tech debt). Mode = local useState, no new slice. Split ProductSearchForm2 (>200 lines). Spec px/hex mapped to tokens (`#1E4ED8`→brand-primary, no 16px radius token).
- [[adr-activity-card-favorite-button|ADR: Activity Card Favorite Button]] — Extend BookmarkButton + fix BookmarkViewSet (2 ORM bugs + allow `contract` content type). No new model/migration. 3 files only.
- [[nav-header-redesign|Nav/Header Redesign]] — Full nav evolution: Phase 0 label changes (Explore Thailand, Routes, Journeys, Experiences, Guides), Phase 1 Experiences dropdown, Phase 3 backend API + bug fixes. 6-agent validation. All submenus removed — single source of truth. A11y baseline, MUI+Tailwind coordination patterns
- [[hero-banner-cms|Hero Banner CMS 2026-05-19]] — backend-controlled homepage hero, FileField+AVIF fix, admin dashboard CRUD, 5s slideshow
- [[blog-seo-performance-2026-05-20|Blog SEO & Performance 2026-05-20]] — parallel fetches, image optimization, HMR fixes, patterns to reuse
- [[hydration-infinite-refresh-fix-2026-05-20|Hydration Infinite Refresh Fix 2026-05-20]] — all-page HMR loop from 4 hydration issues; agent accuracy ~55%; PersistGate SSR pattern
- [[activities-pagination-ux-audit-2026-06-05]] — **COMPLETED 2026-06-05.** 3-specialist pagination UX audit. Load more vs infinite scroll vs numbered pages.
- [[gyg-card-rate-analysis-2026-06-05]] — **COMPLETED 2026-06-05.** GYG card rate display analysis. Display, trust badge, and pricing UX patterns.
- [[cartitems-500-error-analysis-2026-06-02]] — **RESOLVED 2026-06-02.** Cart items 500 error root cause. 3 bugs: type mismatch, exception bubbling, PARSING_ERROR display.
- [[experience-detail-ipad-mobile-redesign-2026-06-02]] — **PLANNED 2026-06-02.** iPad/mobile redesign spec for experience detail page.
- [[trip-page-full-audit-2026-06-15]] — **OPEN 2026-06-15.** 3-agent full-page audit of `/trips/hatyai/koh-lipe` (50+ files). 4 critical: ratecard crash (FilteredTripList:97), transport composit crash (FilteredTripList:53), operator null crash (TripSummary:72), dialog handler confusing pattern (FilterTripsPage:169). 2 XSS: BlogPost:46 + RouteFaqs:19 (dead). 3 dead files: TripList.js, tripItemv2.js, RouteFaqs.js. 8 medium (badge defaults, index keys, unguarded filters, OR logic, perf). Core wiring intact. **Addendum (session #116, 2026-06-15):** 2 more outliers made currency-aware — `SlideCalendar2.js:977` + `TripSummary.js:35` now use `useFormatPrice()`. See [[currency-context-price-rendering-rule]] + [[slidecalendar2-farecalendar-prop-pattern]].
- [[trip-filter-modal-audit-2026-06-15]] — **OPEN 2026-06-15.** 3-agent functional audit of filter modal on `/trips/hatyai/koh-lipe`. 2 critical bugs: typo `trasportation_com` silently breaks transport filter (FilteredTripList.js ~L51), price badge compares hardcoded [0,100] vs dynamic API defaults (TripSearchFilters.js ~L16). 2 logic ambiguities: OR vs AND for conditions/amenities, NaN tiebreaker on string IDs. 4 minor dead-code issues. Core wiring intact.
- [[trip-route-page-seo-aeo-geo-audit-2026-06-15]] — **OPEN 2026-06-15.** 3-specialist deep audit of `/trips/hatyai/koh-lipe`. GEO 5.7/10, AEO 4.7/10. 3 P0 blockers: FAQ not in SSR HTML (RTK-gated), wrong blog/overview content (data issue in backend), ItemList relative URLs. P1: H1 empty at SSR, LocalBusiness BusStation type wrong for island, transport_type field missing from ISR serializer.
- [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis|trip-detail-seo-aeo-geo-audit-2026-06-16]] — **CLOSED 2026-06-16** (`ca490ee` → develop, pushed). 3-specialist SEO/AEO/GEO audit of the **detail** page `/trips/detail/[...slug]` (transport; distinct from the route-listing audit above). 25 raw → 18 unique findings, 7 HIGH (leader scrutiny-pass downgraded malformed-offers HIGH→MED — see synthesis). Root cause flagged by all 3: `TripDetailSEO.js:11-15` docstring claims Breadcrumb/LocalBusiness/FAQ/TouristTrip schema but renders only Product+NextSeo — fix is wiring existing helpers (`JsonLd.js`, `LocalBusinessSchema.js`, `generateFAQSchema`, `generateProviderSchema`), not new code. HIGH: canonical can ship `localhost`/non-www (no `getSiteUrl()` guard), no BreadcrumbList, no FAQPage, generic Product not TouristTrip, route facts trapped in tooltips/tables, og:locale hardcoded `th_TH`, no hreflang vs Europe/USA/Asia target. Keep-as-is: `geo.region TH`, rating-gated, THB settlement, noindex on null rate. Read-only; WebFetch can't hit localhost so findings source-derived — leader hand-verified 6 load-bearing cites against source (5 held, 1 corrected); prod rich-results test still recommended. Prioritized 11-action list in synthesis. Raw: r1-seo/r1-aeo/r1-geo. **Fix plan ([[trip-detail-seo-aeo-geo-audit-2026-06-16/r3-implementation-plan|r3-implementation-plan]], grill-locked 2026-06-16):** mirror day-trip server-side pattern — new `helpers/seo/tripDetailSEOUtils.js`, SEO into `getStaticProps`, rewrite `TripDetailSEO.js` like `DayTripDetailSEO.js`. 7 HIGH only; GEO signal-only (hreflang+og:locale:alternate); ISR schema price. **Re-audit ([[trip-detail-seo-aeo-geo-audit-2026-06-16/r4-re-audit-post-impl|r4]], 2026-06-16): 7/7 HIGH PASS. 1 PARTIAL (TouristTrip schema output correct, @context/@type duplicate key code smell — MED cleanup). Implementation complete on `feat/trip-detail-seo-aeo-geo-fix`.**
- [[trip-search-below-fold-redesign-2026-06-15]] — **MERGED 2026-06-15** (`6f2ada9` → develop). RouteFAQ new (6 dynamic FAQs + FAQPage schema), RouteSummary rewrite (ISR transport chips + operator names replacing client-side stats table), TripSummary price per item (default rates only, slug-matched from avaliable_routes[]) + ItemList schema. Key bug: ExteaContractSerializer has no ratecard — use avaliable_routes[]. Atoms: [[extea-contract-serializer-no-ratecard]], [[isr-client-rtk-stats-seo-pattern]].
- [[trip-search-results-redesign-2026-06-14]] — **CLOSED 2026-06-15.** 3-agent design analysis for Travel Decision Engine redesign of `/trips/[from]/[to]`. R1+R2 fully shipped to `develop`. See [[trip-search-results-implementation-plan-2026-06-14]] + [[trip-search-below-fold-redesign-2026-06-15]].
- [[trip-search-results-implementation-plan-2026-06-14]] — **CLOSED 2026-06-15.** R1 `933b1b6` + R2 `6f2ada9` + round-trip UX `a3c328a` all merged to develop. P1-P5/P7-P10 CUT. P11 no-op. Deploy to prod pending (ops).
- [[adr-trip-confidence-score-algorithm-2026-06-14]] — **DECISION 2026-06-14.** Confidence score = backend-computed `SerializerMethodField`. Reweighted: rating 45 / reviews 25 / popularity 20 / score-bonus 10 (raw `score` is null on most contracts). Rejected Alt B corrected (RecommendationViewSet exists but is cross-sell).
- [[contract-confidence-score-algorithm]] — Atom (extracted 2026-06-15). Formula spec + cold-start handling + N+1 fix (`_get_review_stats`) + tiebreaker chain. Use when implementing confidence score sort or explaining weight choices.
- [[route-intelligence-hero-spec]] — Atom (extracted 2026-06-15). Locked Phase 1 hero spec: gradient (no photo), 180/140px, leg badge, route title with return-swap, 4-stat row, 3 screenshot refinements, CUT/BLOCKED items.
- [[core-web-vitals-budget-2026-06-06]] — Atom (extracted 2026-06-15). Site-wide performance budget: HTML <100KB, all WebP+AVIF, async scripts, no inline `<style>`, font preload, explicit image dimensions. C1-C3 + H1-H5 + M1-M4 from 2026-06-06 audit.
- [[cross-sell-integration-status-2026-06-13]] — **NEW 2026-06-13.** Live code audit: all 4 surfaces mounted (checkout `index.js:1008`, trip detail `[...slug].js:367`, activity detail `DayTripDetailPage.js:231`, post-booking `BookingDetailMain.js:161`). Vault stale atoms flagged. GTM `item_category` (`useOmisePayment.js:56`) = quick eng win. BD inventory = only gate.
- [[cross-sell-debate-review-2026-06-09]] — **COMPLETED 2026-06-09. PARTIALLY STALE** (checkout blockers resolved). 3-agent BD×ENG×PM debate. Cross-sell placement: post-booking #1, trip detail #2. Checkout IS live — see [[cross-sell-integration-status-2026-06-13]].
- [[next-priority-debate-2026-06-09]] — **COMPLETED 2026-06-09.** 3-agent next-priority debate. Decision: GTM + cross-sell mount now, journey builder gated.
- [[implementation-plan-cross-sell-2026-06-09]] — **COMPLETED 2026-06-09.** 4-agent impl plan: GTM fix → mount CheckoutRelatedTrips → wire scored API → SEO content.
- [[checkout-uxui-audit-2026-06-10]] — **OPEN 2026-06-10.** Checkout UX/UI review.

## Business Development (2026)

- [[business-development-thesis-2026-2029]] — SmartEnPlus strategic transformation: Travel Commerce Platform, "travel connectivity" vs OTA/inventory competition, 4-phase growth model
- [[business-development-thailand-platform-analysis]] — 12Go vs Klook vs GetYourGuide funnel mapping: transport aggregation, deals/bundles, premium tours. Gap: end-to-end itinerary unowned
- [[business-development-thailand-bundle-architecture]] — End-to-end bundle design: MaaS skeleton + activity decoration + wellness add-ons. Timeline UI + conflict detection. v1: 3 corridors
- [[business-development-thailand-bundling-margin]] — Margin tiers: transport (low), activities (medium), wellness/SIMs (high). Bundle Score UX. Klook content marketing model
- [[business-development-unified-travel-wellness-thesis]] — 30%+ operating margins via integrated transport+wellness. Wellness as differentiator. Gamification loops. Domestic Thai focus
- [[business-development-zeitrip-mvp]] — MVP: single itinerary timeline vs cart. 3 corridors, wizard flow, conflict detection. "Plan your Thailand trip in one timeline"
- [[trip-detail-page-review-2026-05-20|Trip Detail Page Review 2026-05-20]] — 3-agent review: 8 perf + 8 SEO + 8 code quality issues; 24 verified findings with line numbers and fix order
- [[trip-detail-deep-review-2026-05-20|Trip Detail Deep Review 2026-05-20]] — 4-agent adversarial pass: 3 findings overturned, 8 hidden issues, 4 prod failure scenarios; top risks: ratecard wipe, fetch timeout, invalid ISO8601 schema
- [[homepage-ux-review-2026-05-21|Homepage UX/UI Review 2026-05-21]] — 3-agent review, 11 sections, 4 critical + 34 major issues; XSS in reviews, section reorder, inline validation, hero value prop
- [[homepage-seo-performance-deep-review-2026-05-21|Homepage SEO & Performance Deep Review 2026-05-21]] — 3-specialist audit: structured data errors (fake phone/address, stale dates), Technical SEO gaps (server-sitemap 404, og:locale, DefaultSeo), CWV risks (CLS, preconnect); priority fix queue
- [[og-image-inferred-audit-2026-05-23|OG Image "Inferred" Audit 2026-05-23]] — Homepage + blog og:image broken. RC1: NEXT_PUBLIC_DOMAIN undefined → Seo crash (fix: inline 3-tier fallback, NOT getSiteUrl() import). RC2: missing secureUrl on blog pages (fix: update generateBlogSEO() helper + patch search page). Scrutiny corrections applied 2026-05-23.
- [[og-image-ssr-fix-2026-05-23|OG Image SSR Fix 2026-05-23]] — PersistGate SSR blocker fixed. All meta tags blank site-wide. 4 root causes: PersistGate, seoHelper relative URLs, trips relative ogImagePath, NEXT_PUBLIC_SITE_URL tech debt. 4 commits, merged → main, live 2026-05-23.
- [[seo-wave2-audit-2026-05-23|SEO Wave 2 Audit 2026-05-23]] — DONE. All 11 bugs verified + fixed + merged to main (`ceb0eac`). M5/M6: no-op. Auth pages noindex blocked by ProtectedComponent returning null SSR — fix deferred.
- [[hero-section-comprehensive-audit-2026-05-26|Hero Section Comprehensive Audit 2026-05-26]] — 9-agent synthesis: 88px header-hero gap (double-offset root cause), cross-page hero inconsistencies (Activities Browse + Trip Detail missing heroes, H1 scale mismatch, CTA inconsistency), mobile header behavior change. Priority actions defined.
- [[mobile-header-analysis-2026-05-26|Mobile Header Analysis 2026-05-26]] — Original vs current mobile header diff. Dynamic scroll→fixed position, Slide animation removed, separate DOM structures, missing spacer compensation.
- [[airport-transfer-redesign-2026]] — Homepage airport transfer section UX/UI redesign + backend API extension. AT-1 full redesign spec.
- [[smartenplus-wireframe-architecture|SmartEnPlus Wireframe Architecture]] — Full platform wireframe + information architecture. 15 sections: homepage, hero, journeys, destinations, search results, experiences, routes, guides, mobile strategy, design system.
- [[smartenplus-uxui-redesign-research-2026|SmartEnPlus 2026 UX/UI Redesign Research]] — Strategic direction: "premium operational transportation platform" not cinematic travel website. Compact 45-60vh hero, calm premium minimalism, efficiency-first UX. Header, search module, section redesign strategy.
- [[homepage-uxui-audit-2026-05-31]] — **COMPLETED 2026-05-31.** 6-phase UX/UI audit. Commit `ade94ee`. Layout, card differentiation, destination flow fixes.

- [[docker-standalone-isr-revalidate-gap]] — ISR timer gap in Docker standalone, deploy volume clear workaround. **+2026-06-17:** confirmed on `/activities/detail` (revalidate 3600, admin contract edit never reaches prod); full chain traced (save→signal→Redis bust real, ISR HTML never notified = the gap). Side finding: `daily_counter` self-save (`views.py:882`) busts backend Redis on every read.
- [[on-demand-revalidation-api-route]] — pages/api/revalidate.js pattern, auth, 207 Multi-Status. **+2026-06-17:** flagged — documented code is App Router but repo is Pages Router; use `res.revalidate(path)` not `request.revalidatePath`. Corrected snippet added.
- [[celery-task-over-bare-thread-django-signals]] — why Celery over threads for signal side effects, slug dedup, retry
- [[isr-csr-overlay-stale-fields]] — CSR covers ratecard/dates; stale: name/description/images/JSON-LD/meta
- [[persistgate-ssr-suppresses-head-component]] — PersistGate null SSR blocks DefaultSeo/Head; hoisting fix
- [[webpack-image-src-og-absolute-url-rule]] — webpack .src relative → absolute for OG images

## Knowledge Domains

- [[smartenplus-synopsis]] — Project-wide orientation: stack, repos, payment, auth, current state, open work
- [[ai-workflows]] — LLM Wiki pattern, ingestion/query/lint operations
- [[nextjs-patterns]] — ISR, dynamic SSR disable, RTK Query, date handling
- [[redux-store-architecture]] — 7-version persist migration, cross-tab cart invalidation, dual reset, SSR no-op storage, deprecated cart-slice, auth whitelist, 48hr TTL
- [[rtk-query-advanced-patterns]] — child/children normalization, fixedCacheKey dedup, intentional missing invalidatesTags, bookmark 409/404 suppression, 'null' string guard
- [[checkout-hoc-architecture]] — withCartValidation (ref dedup, 404-only clear), withCheckCartValidation, withComponent infinite-refetch risk
- [[e2e-csrf-blocks-410-legacy-post-tests]] — Django CSRF middleware returns 403 before 410 view runs in E2E. Pattern: split into GET (assert 410) + POST (assert 403 = CSRF protection). Used in [[payment-manual-test-skip-2026-06-12]].
- [[checkout-state-persistence]] — useCartSync 6-effect ordering, ghost trip detection, dual persistence strategy, guest→backend migration, debounced auto-save
- [[checkout-formdata-time-fields]] — frontend lowercase-t vs backend capital-T time field boundary, HH:MM:SS format, 3 conversion helpers
- [[checkout-step-flow]] — hasMixedPassengerCounts step branching (4 vs 5 steps), payment init idempotency key, CONTRACT_INACTIVE auto-redirect
- [[frontend-debug-utilities]] — useRateLimitedQuery global singleton (5 types, jitter), DevToolsProvider disabled by default, useAuth 100ms redirect delay
- [[payment-integration]] — Thai payment methods, Omise source types, webhook flows, checkout architecture principles (28 use cases), centralized payment error detection, expiry paths (Celery+view+mgmt), C1/C2 fixed in cb817d9
- [[payment-audit-bugs-2026-06-11]] — 4 confirmed bugs (2 MEDIUM cart-sync dead code, 2 LOW stable_id cleanup), 2 fixed candidates (formData restore, transient error nuking cartId, both cb817d9)
- [[omise-api-reference-2026-06-12]] — Full Omise API catalog (21 sections): 7 active, 3 partial, 11 not integrated; status vocabulary + authorized charge handling
- [[payment-status-enums]] — OmiseMethod constants, status machines, authorized mapping, METHOD_EXPIRY
- [[payment-charge-service-layer]] — create/reconcile operations, idempotency, locked_amount rule, getPrimaryCharge post-fix
- [[payment-gateway-charge-architecture]] — two-charge model, canonical rule, finalize_payment SSOT, ExpirePendingChargeView table
- [[checkout-formdata-persist-guard-pattern]] — C1/C2 fixes (isCartLoaded gate, 404-only cart clear), PersistGate timing issue, RTK error shapes
- [[celery-tasks|Celery Tasks]] — bind=True pattern, exponential backoff, high-risk task guards, beat schedule
- [[refund-flow|Refund Flow]] — payments.Refund model, cards.Refund (legacy), RefundViewSet deprecation
- [[journeys|Journeys]] — UserJourneyEvent analytics, event types, metadata, dedup guard pattern
- [[design-systems]] — Token-based design system approach
- [[design-system-audit-2026-05-31]] — Design system audit: brand color (#3b5998), token gaps, hardcoded values found across components
- [[design-system-audit-2026-06-13]] — Full design system audit: token coverage, component violations, UX patterns, migration roadmap. 889 hardcoded colors, 386 inline styles, 5 debate outcomes, 5-phase migration plan.
- [[carousel-design-standard]] — Embla carousel items-per-screen breakpoints, gap values, card widths, focus ring handling
- [[admin-dashboard-contracts]] — Category registry, form flow, payload rules, helpers
- [[pdf-contract-import-research]] — Team research + decision: Django+Claude tool_use pipeline for parsing non-standard operator PDFs to update contracts. Phase 1 scope + deferred Phase 2.
- [[admin-dashboard-image-pipeline]] — Frontend image state, error reset hooks, dedup helpers
- [[operator-image-alt-caption-fields]] — **NEW 2026-06-08.** `OperatorImageGallery` alt_text + caption schema, dialog 3-field UX with auto-prefill, grid alt chain. Includes DRF silent-drop gotcha: camelCase `altText` ≠ `alt_text` returns 200 OK with field not saved.
- [[nextjs-hmr-cross-module-callback-staleness]] — **NEW 2026-06-08.** Pages Router Fast Refresh edge case: child module hot-replaces, parent module's callback stays stale → new fields silently dropped. Symptom: "only old fields persist", hard refresh may or may not fix. 5-probe detection pattern + architectural fix (move mutation INTO the dialog).
- [[django-soft-delete-s3-file-preserve]] — **NEW 2026-06-08.** Soft-delete on file-bearing model rows keeps the S3 file alive because other models may FK-reference the same path. Hard-delete would fire `post_delete` and break those references. Canonical example: `operators/views.py:1860-1868` destroy docstring. Reusable for any file-bearing model with cross-model FK refs.
- [[adr-contract-soft-delete-2026-06-16]] — **NEW 2026-06-16, ACCEPTED/built #122.** Contract soft-delete via separate `is_deleted` flag (mirror ImageGallery). Hard-delete crashes on PROTECT FKs (BookingItem/CartItem). `is_deleted=True` MUST set `is_actived=False` (REQUIRED invariant — booking guard `carts/utils.py:62` checks only `is_actived`); restore does NOT auto-reactivate. Frontend ZERO changes. Audit fixed 3 defects. Admin gets Deleted chip + filter + Restore.
- [[contract-soft-delete-is-actived-invariant]] — **NEW 2026-06-16.** Load-bearing rule: `is_deleted ⇒ is_actived=False`. ~14 public/booking querysets + `carts/utils.py:62` key only on `is_actived`, so flipping it on delete is what hides a deleted contract — not the `is_deleted` filter. Lives in one method `Contract.soft_delete()`.
- [[stations-arrival-viewset-public-leak]] — **NEW 2026-06-16.** `ListProductsByArrivalStationViewSet` (public+unauth) filtered neither `is_actived` nor `is_deleted` → leaked inactive + would leak deleted. Pattern: grep ALL `Contract.objects` public paths when adding a hide flag, not just list/detail.
- [[operator-image-soft-delete-cascade-gap]] — **NEW 2026-06-08, CORRECTED 2026-06-08.** `OperatorImageGallery` soft-delete intentionally does NOT cascade to contract `ImageGallery` rows (only `image` URL string shared, no FK). This is correct design — existing contracts are self-managed content edited via the contract management workflow. No cascade is intended. Audit-only fix: explicit copy in the admin delete dialog so the operator understands the independence when `active_contracts > 0`.
- [[django-partial-update-elif-metadata-drop]] — **NEW 2026-06-08.** Backend `partial_update` with `elif field_changed` branch silently drops all other payload fields on existing rows. First save works, every subsequent metadata edit vanishes. Fix: unconditional sync of all payload fields. Reusable for any DRF partial_update with branched write logic.
- [[image-metadata-formik-state-only-save]] — **NEW 2026-06-08.** Sub-component dialog edits ride along with parent form's existing Save button via Formik `setFieldValue`. Zero new endpoints, zero new save buttons, zero new state. Reuses `useAlert` provider + parent save flow. Tradeoff: snackbar says "updated" but data not in DB until parent Save.
- [[add-flow-metadata-helper-pattern]] — **NEW 2026-06-08.** Helpers that add an item from one model surface to another (gallery → selected set) must carry ALL metadata fields, not just `id` + `image`. Pass the whole object, destructure inside the helper. Caller-side destructuring is a silent-drop trap.
- [[two-surface-parity-shared-module]] — **NEW 2026-06-08.** When 2 UI surfaces need identical UX (grid, search, dialog, actions) over different data sources, extract `shared/` module. Each surface = thin wrapper. No duplicate code, no drift. Multiple variants stay separate components, not boolean props.
- [[admin-dashboard-component-patterns]] — Formik+Yup, RTK Query, MUI patterns, gotchas
- [[django-serializer-shadowing-pattern]] — Local class redefines imported name in same file; silently changes exposed fields. Discovered via HomeSerializer/StationSerializer in products/serializers.py.
- [[checkout-confirmation-payment-crash-2026-06-03]] — **PENDING COMMIT 2026-06-03.** Full flow fixed (9 files, 2 repos). ContractSerializer extended. ServiceTabbedInfo.js refund_hours fix. Commit + merge next session. Atoms: [[service-detail-non-transport-display]], [[contract-trip-null-non-transport-pattern]], [[copy-cartitem-trip-none-guard]], [[contract-serializer-non-transport-fields-2026-06-03]], [[checkout-null-contract-scan-2026-06-03]].
- [[contract-serializer-non-transport-fields-2026-06-03]] — **NEW 2026-06-03.** ContractSerializer had minimal fields list — missing all non-transport data. Fix: 3 helper serializers + 10 new fields. Key: `refund_hours` not `cancellation_window`. `duration` DurationField → `"8:00:00"` format, safe with `customFormatDuration`.
- [[contract-model-ambiguity-audit-2026-06-03]] — **NEW 2026-06-03.** 4-round team audit of `primary_location`/`service_areas`/`meeting_point_*`/`InfoField` casing. 6 conceptual overlaps, 1 customer-visible (i18n on `meeting_point_details`), 5 staff-side or dormant. Recommendation: document + 1 help-text fix, no model consolidation. Debates 3 (D3 casing) + D1/D4/D5 with genuine agent disagreement. S-1/S-2 overturned "dead code" claims on `Trip.route` + `meeting_point_place`.
- [[copy-cartitem-trip-none-guard]] — **NEW 2026-06-03.** `carts/utils.py:copy_cartitem_to_bookingitem()` crashed `trip.route` when `trip=None`. Guard pattern + `str()` coercion for route/station CharFields. No migration.
- [[checkout-null-contract-scan-2026-06-03]] — **RESOLVED 2026-06-03.** Full scan of checkout for unguarded contract/trip access. 1 real bug found + fixed (`05fc0aa`): `Passengers.js:1097` trip header label. All other flagged sites verified safe (JSX short-circuit guards).
- [[contract-trip-null-non-transport-pattern]] — **NEW 2026-06-03.** Non-transport contracts always have `trip=None`. Guard `contract?.trip` before accessing `departure_time`/`arrival_time`/`route`. Crashes render-root computed values without guard.
- [[service-detail-non-transport-display]] — **NEW 2026-06-03.** Booking detail page field-name contract: `general_information?.description`, `refund_hours` (not `cancellation_window`), `customFormatDuration(duration)` safe with "8:00:00" DurationField format. Reusable for any contract display in booking/order/email rendering.
- [[view-utility-call-exception-wrapper]] — **NEW 2026-06-03.** View-layer `try/except → ValidationError` wrapper for untrusted utility calls. Ensures JSON 400 instead of HTML 500 when utility crashes. Defense-in-depth, not a substitute for internal null guards.
- [[activities-sort-filter-ux]] — **NEW 2026-06-02.** State-driven button emphasis pattern (both outlined, active via badge/label). Travel app standard (Klook, Booking.com). Mobile sort bottom-sheet, desktop sort chip.
- [[extea-contract-serializer-no-ratecard]] — **NEW 2026-06-15.** `ExteaContractSerializer` has no `ratecard` field. ISR price for TripSummary must come from `avaliable_routes[].ratecard[]` matched by slug. Filter: `rate_date=null` + ADULT/VEHICLE only for stable year-round baseline.
- [[isr-client-rtk-stats-seo-pattern]] — **NEW 2026-06-15.** Client-side RTK Query data in below-fold = zero crawl value. Replace with ISR-rendered `contracts[]` / `data[0].avaliable_routes[]` from getStaticProps. Applied: RouteSummary stats table → transport chips + operator names.
- [[transport-combo-card-pattern]] — **NEW 2026-06-14.** MUI icon mini-cards for transport combination filter. Icon map (type_class → MUI icon), label rule (drop vehicle class), visibility rule (hidden ≤1 combo in prod), active/inactive states. `TransportationOptionsFilter.js` `496c74a`.
- [[homepage-experiences-section-audit-2026-05-30]] — Feasibility audit: add "Explore Experiences" carousel to homepage. Verdict: VIABLE after AT-1 + inventory check. Backend ready (Contract model). 5 files, ~160 lines. Reuses CardCarouselContainer + PopularRoutesSection pattern.
- [[transportation-category-audit-2026-05-30]] — Full audit: 3-level category system (station_type / service_category / VehicleType), airport filter vs TRANSFER category decoupled, 26 station_types, lowest_price nullable, query_count Celery mechanism. Professional homepage section redesign spec (AT-1): image card + IATA badge + carousel mobile + serializer expansion.
- [[mui-tailwind-css-specificity]] — MUI Emotion overrides Tailwind className on MUI components; use sx prop or div wrapper; sx responsive breakpoints fail without Emotion cache provider
- [[popular-routes-lowest-price-farecalendar-parity]] — **NEW 2026-06-15.** `lowest_price` subquery in FrontPageRouteViewSet must use two subqueries (JOIN/ADULT + PRIVATE/CHARTER/VEHICLE) + `Least()` + sentinel to mirror FareCalendar logic. Single subquery can't do conditional type filtering.
- [[slidecalendar2-farecalendar-prop-pattern]] — **NEW 2026-06-15.** `SlideCalendar2` accepts `fareCalendar` (`{ 'YYYY-MM-DD': rate_thb_int }`) + `fareCalendarLoading` (boolean). Caller MUST fetch via `useGetFareCalendarQuery` + `skipToken` (see `TripSearchFilters.js:80-99` canonical pattern). Caller inventory (5 total): 1 wired (`TripSearchFilters`), 4 missing (incl. `TripDetailSchedule` on `/trips/detail/[...slug]` — pre-existing bug, out of scope). Cheapest-day highlight: emerald `#059669`, suppressed when all-same or single-fare.
- [[nextjs-fixed-header-per-route]] — `position: fixed` on homepage only via `router.pathname === '/'`; sticky elsewhere; `<main>` gets `pt-[88px]` on non-homepage to clear header
- [[payment-sentinel-idempotency]] — Timestamp sentinels as exactly-once guards; reusable for any side effect (email, booking, settlement)
- [[nextauth-session-shape]] — `session.user.email` not `session.email`; auth check via `session?.id`; guest email sources
- [[cart-reprovision-after-reset]] — `resetCart()` + fire-and-forget `createCart()` pattern; required on 2 order pages not wrapped in `withCartValidation`
- [[promptpay-no-webhook-on-expiry]] — PP/MB expiry has no Omise webhook; all 3 expiry paths must call `_send_payment_failed_notifications()`
- [[nextjs-isr-ratecard-empty-array-guard]] — `??` doesn't catch `[]`; use `?.length > 0` when merging CSR arrays into ISR baseline
- [[nextjs-307-vs-301-product-reclassify]] — Keep `permanent: false` on product-type redirects; 301 causes browser/CDN cache pollution on reclassification
- [[seo-homepage-specialist-team]] — SEO specialist team: 3-role sequential audit workflow, how to invoke, pre-conditions, known gaps found on first run 2026-05-21
- [[hero-88px-gap-root-cause]] — 88px white gap between header and hero on non-homepage. Double-offset: sticky reserves 88px + pt-[88px] on main. Fix: remove global pt-[88px], make spacing component-local.
- [[featured-image-header-usage-matrix]] — Cross-page FeaturedImageHeader comparison. 12 pages: 10 use component, 2 have no hero. Inconsistencies in cinematic mode, min-height, H1 size, CTA treatment.
- [[react-hooks-rules-lowercase-component]] — ESLint `next/core-web-vitals` blocks build when hooks called in lowercase-named function. PascalCase mandatory for React components, even in index.js files.
- [[smartenplus-product-positioning]] — "Thailand Travel Infrastructure Platform." 5 DNA layers (transportation, experiences, route intelligence, editorial, trust). Core value: "Explore Thailand Easily."
- [[smartenplus-2026-ux-direction]] — Strategic shift: cinematic → operational. Compact 45-60vh hero, calm premium minimalism, efficiency-first. Header, search, section redesign strategy.
- [[mobile-header-scroll-behavior-change]] — Mobile header: dynamic (relative+Slide) → permanently fixed. Spacer removed, DOM paths diverged. 4 issues documented.
- [[design-token-caption-tailwind-gotcha]] — `TYPOGRAPHY_SCALE.caption` = Tailwind string `'text-xs'` not an object. `.fontSize` = undefined. Never use in MUI `sx`. Use raw value or add parallel `MUI_FONT_SIZES` token.
- [[mui-autocomplete-inputvalue-sync]] — MUI Autocomplete `inputValue` initialized via `useState(value)` doesn't sync when controlled `value` prop changes post-mount. Fix: `useEffect(() => setInputValue(value || ''), [value])`.
- [[django-parse-int-list-text-fallback]] — `_parse_int_list` returns `[]` on text input. Caller branching to `.none()` returns zero results silently. Add text-search fallback branch.
- [[django-nested-delete-sweep-pattern]] — Exclude-based delete sweep wipes all rows when `existing_ids` set is empty. Guard: never `continue` in create branch + `if existing_ids:` before delete.
- [[django-nullable-fk-migration-pattern]] — FK `CASCADE → SET_NULL null=True` + migration. View-layer `None` without migration = `IntegrityError`. Deploy order matters.
- [[nav-label-url-slug-two-layer-strategy]] — Nav label (brand word) and URL slug (SEO word) should differ. Google indexes URLs not nav labels. Safe to change nav anytime; URL = permanent infrastructure.
- [[production-url-rename-cost-framework]] — Decision framework: refs >100 = never rename; multi-year indexed = high risk. True duplicate test before any consolidation.
- [[locations-destinations-product-split]] — /locations = routes FROM a city (departure browser). /destinations = booking TO a station (trip purchase). Different APIs, different intent. Never consolidate or cross-canonical.
- [[react-client-key-null-id-pattern]] — `id: null` sentinel for unsaved records + `_clientKey: Date.now()` for stable React key. Avoids PK collision + duplicate key warnings.
- [[react-dual-hook-url-race]] — Two hook instances owning same URL race each other. Fix: `{ enabled }` param to gate URL-sync, `isControlled` detection, `didMountRef` to skip mount-fire, MUI freeSolo string branch in `onChange`.
- [[pdf-contract-import-adversarial-review]] — 6 red flags for PDF import arch: async AI call required, soft-delete draft, remove LLM matching, pre-validation, no confidence auto-accept, large-delta warning. 3-screen UX. All must resolve before first commit.
- [[django-async-ai-call-pattern]] — Django sync LLM calls block WSGI workers. Pattern: return `task_id` immediately, Celery handles AI call, frontend polls status endpoint.
- [[react-strictmode-useref-persistence]] — **NEW 2026-06-05.** useRef state persists across StrictMode simulated remount. Mount-only `didMountRef` guards bypass on second setup, firing effects only in dev. Solution: make effects idempotent.
- [[react-state-no-op-guard-side-effect-prevention]] — **NEW 2026-06-05.** Guard `setState` callback against same-value writes: `if (prev[key] === value) return prev`. Prevents coupled side effects (page reset, URL push) from firing on no-op writes.
- [[nextjs-shallow-router-push-scroll-false]] — **NEW 2026-06-05.** `router.push({...}, undefined, { shallow: true, scroll: false })` for URL sync on filter change. Default `scroll: true` causes scroll jumps on every state change.
- [[wcag-touch-target-enforcement]] — **NEW 2026-06-06.** 3-part pattern for WCAG 2.5.5 (44×44 CSS px): (a) `TOUCH_TARGET.minHeight: '44px'` token in `designSystem.js:210`, (b) Tailwind `min-h-[44px] min-w-[44px]` OR MUI `sx={{ minWidth: 44, minHeight: 44 }}`, (c) Playwright `boundingBox` regression spec at 320/375/414 viewports. F2 batch: 5 files + 1 new spec.
- [[icon-button-size-decision]] — **NEW 2026-06-06.** 40×40px (Material medium) is default for icon buttons in dense UI. 44×44 reserved for primary CTAs. F2 of website audit shipped 44; user feedback: too big. Reverted swap/currency/profile to 40 in `fbdca15`. Apply 40 to F3 WhatsApp for consistency.
- [[mui-menu-paper-overflow-guard]] — **NEW 2026-06-06.** MUI Menu Paper has no implicit max-height. When content > viewport, rounded background ends mid-row. Fix: `MenuListProps` + `PaperProps` with `maxHeight: calc(100vh - 120px)` and `overflow: hidden/auto`. Triggered by F2 anchor re-position (ProfileImage 36→44).
- [[expandable-menu-row-mui-collapse]] — **NEW 2026-06-06.** `ExpandableMenuRow` (parent with chevron + per-row `useState` + `<Collapse>` + `aria-expanded`) + `SubMenuRow` (indented child). 3 groups in ProfileMenu save −240px default height. Use for 4+ related actions sharing a theme.
- [[rate-review-page-shell-pattern]] — Shell/skeleton pattern for rate-review pages (FeaturedImageHeader + grid + sticky sidebar).
- [[gtm-impression-dedup-sessionstorage]] — GTM impression dedup via sessionStorage guard — prevents duplicate events on re-render.
- [[django-m2m-location-join-recommendations]] — M2M location join query pattern for recommendations (`service_areas` + `primary_location`).
- [[checkout-next-btn-disable-conditions]] — Checkout Next button disable logic: all conditions that block progression.
- [[carousel-embla-align-start-mobile-snap]] — Embla carousel `align: 'start'` + mobile snap settings for consistent item alignment.
- [[touch-target-44px-enforcement]] — 44px touch target pattern (WCAG 2.5.5). Token + Tailwind + MUI + Playwright spec.
- [[ios-zoom-input-16px-rule]] — iOS auto-zoom prevention: inputs ≥16px font-size. `text-base` minimum.
- [[django-booking-creation-validation-gate]] — Validation gate at booking creation: advance_hour + stop_sale + operational_day checks.
- [[rate-review-css-audit-2026-06-06]] — CSS audit findings from rate-review pages: padding, spacing, pattern alignment with blog pages.
- [[next-font-self-host-perf-pattern]] — Next.js self-hosted font performance: `next/font` + `display: swap` + preconnect elimination.
- [[brand-name-constant-extraction]] — Extract brand name to `constants/brand.js` to prevent copy drift across SEO + UI.
- [[recommendation-type-selection-by-service-category]] — Recommendation type selection: `find_nearby_activities` for DAY_TOUR/SPA, transport-anchor for routes.
- [[star-aria-radiogroup-pattern]] — Star rating ARIA: use `role="radiogroup"` + `role="radio"` + `aria-checked`. Fixes `aria-pressed` misuse (multiple true simultaneously).
- [[pdf-parsing-pipeline-pattern]] — **NEW 2026-06-11.** Django+NotebookLM pipeline for PDF contract imports. Full flow, invariants, backend components, rate card merge strategy.
- [[pdf-import-pre-validation-rules]] — **NEW 2026-06-11.** 6 red flags + 3-screen UX for PDF import. All must resolve before first commit.

- [[payment-gateway-charge-architecture]] — GatewayCharge model, finalize_payment() SSOT, locked_amount freeze, webhook sole finalization
- [[payment-charge-service-layer]] — create_charge, reconcile, idempotency hash, _to_minor_units, JPY handling, staleness reuse, 5-sec throttle, TOCTOU guard
- [[payment-status-enums]] — PaymentStatus machine, OmiseMethod constants, REDIRECT_METHODS, METHOD_EXPIRY TTLs, authorized Order.status, OMISE_STATUS_MAP (reversed→PENDING), PAYMENT_METHOD_MAP frontend codes
- [[omise-webhook-security]] — Event.retrieve() verification (not HMAC), double-layer dedup, WebhookEvent outside atomic
- [[omise-webhook-tailscale-local-testing]] — **NEW 2026-06-12.** Tailscale funnel setup for real Omise webhook delivery to local BE :8000. Repro steps, all-5-steps PASS results, gotchas (auto-complete PP, quoted .env key). See also [[payment-auto-test-results-2026-06-12]].
- [[payment-e2e-rerun-guide]] — **NEW 2026-06-12.** How to rerun all 8 payment E2E tests locally. One command, prerequisites checklist, per-test table, failure debug steps, manual cleanup.
- [[payment-exception-catalog]] — PendingChargeError/AlreadyPaidError/LockedAmountError→409, PaymentAmountMismatchError never re-raised
- [[payment-finalize-deep-dive]] — 6 non-obvious behaviors: snapshot log-only, amount mismatch path-dependent, expired→success recovery, superseded guard, cross-order lock, CAS notification dedup
- [[payment-frontend-flow-mechanics]] — Card vs Source flows, canContinue 3-condition gate, NO_CONTINUE_METHODS, amountLocked UX, QR retry sequence, JPY scaling, OmiseScriptLoader linear-not-exponential bug
- [[payment-qr-polling-mechanics]] — 4-format response fallback chain, should_stop_polling, finalStatusCheck on expiry, guest vs auth request signatures, polling lifecycle
- [[payment-celery-expiry-strategy]] — PromptPay deterministic TTL, mobile banking polls Omise, e-wallet 30min fallback, superseded charge guard, retry wired-but-uncalled bug
- [[omise-client-integration]] — lazy init (module not instance), `_attributes` dict extraction, LINE_PAY→rabbit_linepay, reversed→PENDING, PromptPay QR URI nested path
- [[omise-attributes-dict-extraction]] — `_attributes.get()` vs direct property access; silent None bug; fields affected
- [[django-celery-beat-database-scheduler]] — DatabaseScheduler stores schedule in DB not settings.py; Django admin UI; max_retries dead without self.retry()
- [[toctou-select-for-update-before-api-call]] — lock BEFORE external API call; blocks concurrent webhook; parent record lock pattern
- [[payment-backend-charge-flow]] — DB constraint (one pending redirect/order), TOCTOU guard, 5-sec reconcile throttle, C3b proactive PP expiry, AllowAny+manual ownership, satang conversion
- [[manual-adjustment-model]] — admin-recorded manual charges, no Omise, PROTECT FK, legacy ExtraItemAction replacement
- [[celery-beat-payment-scheduling]] — DatabaseScheduler (not settings.py), Django admin UI for schedule, sync_pending_charges
- [[multitab-payment-race-condition-fixes]] — 7 race conditions, select_for_update cart-wide lock, frontend reconciliation
- [[payment-checkout-architecture-audit]] — 20/20 audit, getPrimaryCharge fix, cancelState guards, qrState clear
- [[payment-checkout-e2e-testing]] — MSW intercept bug, 5 bugs fixed, session structure rule, manual test guide
- [[adaptive-header-route-type-pattern]] — Type A/B split (transactional/discovery), dynamic offset 80/96px, HeaderRowsContext
- [[next-seo-v6-robots-prop-broken]] — robots={{}} silent no-op, correct API noindex={true}/nofollow={true}, SSR constraint false
- [[canonicalization-audit-checklist]] — domain + per-page checks, parallel URL handling, known gotchas
- [[site-url-config-pattern]] — baseURL vs NEXT_PUBLIC_DOMAIN, module const pattern, deploy default fix
- [[structured-data-schema-patterns]] — TravelAgency schema accuracy, WebSite+SearchAction, server-sitemap.xml 404 crawl budget. **+ aggregateRating-placement RULE (#124): never on Org/TravelAgency node — bookable Product/Offer only; flags a contradiction in this note's own homepage fix-list item 4.**
- [[mui-dropdown-preserve-strategy]] — ARIA test compatibility, item reduction framework (11→6), Drawer bottom-sheet pattern
- [[section-contentcard-wrapper-pattern]] — Section/ContentCard absent = full-bleed root cause; reuse across pages
- [[editorial-grid-layout-pattern]] — Asymmetric 2fr 1fr CSS grid, CardCarouselContainer, rounded-xl imageCard token
- [[section-render-order-principles]] — Trust before editorial, mobile scroll depth kills buried sections
- [[dompurify-xss-prevention-pattern]] — dangerouslySetInnerHTML + SSR-safe sanitization (not DOMPurify which needs window)
- [[api-mirroring-pattern-new-features]] — _fetch_X_data mirroring for new API features; reuse serializer; zero new endpoints
- [[design-system-tokens-expansion]] — Border/shadow tokens missing from designSystem.js; hardcoded rgba values across components
- [[designsystem-shadow-border-tokens]] — SHADOWS, BORDERS, BORDER_RADIUS_CLASSES token definitions for helpers/designSystem.js. Replaces hardcoded rgba() across card/dropdown components
- [[airport-transfer-at1-redesign-spec]] — AT-1 full redesign spec: image card + IATA badge + carousel mobile + serializer expansion (station_name, iata_code). Zero impact on other components
- [[layout-spacing-consistency-audit-2026-06-01]] — Cross-page layout audit: activities vs homepage vs trips. 3 inconsistencies: h-padding `p-2` wrong, grid gap mismatch (spacing=1 vs 2), `sm:py-8` minor. LAY-1 + LAY-2 fixes needed before merge.
- [[nextjs-hydration-rules]] — 6 rules preventing hydration mismatches + PersistGate SSR blocker pattern. Mismatch in _app.js triggers HMR infinite refresh
- [[payment-checkout-5-principles]] — 5 core checkout architecture principles: webhook SSOT, single attempt, immutable snapshot, cart lock, explicit cancel-recreate
- [[nextjs-static-path-prop-divergence]] — getStaticPaths + getStaticProps constant divergence = silent routing failure. Module-level constant mandatory
- [[content-marketing-strategy-2026-05-24]] — 5-agent review + full playbook rewrite. 6 contradictions fixed, keyword opportunities, tech stack integrated.
- [[keyword-research-routes]] — 4 CSV data assets (Bangkok-Samui, Chiang Mai, Hat Yai-Lipe en-th, Langkawi-Lipe). Reference index, files live in smartenplus-content/keyword-research/. Feeds [[content-marketing-strategy-2026-06-03]] SEO targets.
- [[business-development-new-site-diagram]] — Reference image (new site diagram.png) for [[business-development-thesis-2026]]. PNG stored outside vault, large file.
- [[business-development-new-site-idea]] — Reference image (new site idea.png) for [[business-development-thesis-2026]]. PNG stored outside vault, large file.

## Areas

- [[business-development-thesis-2026]] — **NEW 2026-06-03.** SmartEnPlus strategic thesis: Thailand Travel Commerce Platform. Four-phase growth model (revenue per traveler → retention → AI intelligence → journey commerce). Competitive position: "travel connectivity" not inventory. B2B+B2C distribution. [[business]] updated.
- [[content-marketing-strategy-2026-06-03]] — **NEW 2026-06-03.** Full Thailand travel content marketing playbook. Hub-and-spoke (Travel Routes primary + 4 spokes), 6-platform distribution, $54.11 CPC hat yai target, Route Demand Index as data moat. Supersedes [[content-marketing-strategy-2026-05-24]] (which becomes the meta-review).
- [[engineering]] — Software engineering practices and standards
- [[business]] — Validated strategy: B2B supplier (12Go+Klook 90%) + B2C direct (10%). EN customer confirmed. Vertical integration moat. "Stippl for SEA with real booking" vision.
- [[southeast-asia-transport-platform-direction]] — Product vision: SEA transport + experience infra platform. Stippl plans but can't book; 12Go books but can't plan — SmartEnPlus does both. B2B supplier → B2C direct roadmap. Core loop: destinations+dates+interests → AI plan → book.

## Decisions

- [[adr-template]] — Architecture Decision Record template
- [[atomic-note]] — Single-concept note template for extracted atoms
- [[adr-info-fields-casing]] — `info_fields` casing boundary: backend fully-lowercase keys, frontend camelCase, single conversion in `checkoutPersistence.js:normalizeTripData()`. Documents lowercase-t vs capital-T `arrivalFlightTime` split.

## Archive

- [[mobile-header-redesign-glassmorphism]] — SUPERSEDED 2026-05-28 by [[header-redesign-2026-spec]]. Dark gradient glass, sticky+blur on scroll, unified 2-row. Kept for reference.
- [[daytrips-to-activities-rename-2026-05-23]] — **COMPLETED 2026-05-23.** /daytrips → /activities rename, 7 phases + 5 scrutiny fixes, merged → develop d424d4e.
- [[css-audit-browse-pages-2026-05-31]] — **COMPLETED 2026-05-31.** 13 commits. All browse pages fixed: destinations, locations, trips.
- [[travel-thailand-better-section-redesign]] — **COMPLETED 2026-05-29.** `ce4d2d7`. Replace 3 editorial sections with 1 unified "Travel Thailand Better" section.
- [[smartenplus-header-ux-v1]] — **COMPLETED 2026-05-25.** Desktop 2-row header. Superseded by [[header-redesign-2026-spec]].
- [[og-image-inferred-audit-2026-05-23]] — **COMPLETED 2026-05-23.** Homepage + blog og:image broken. Inline 3-tier fallback fix.
- [[seo-homepage-audit-2026-05-31]] — **DONE 2026-05-31.** 17 findings → 7 resolved + 2 open + 1 skipped.
- [[trip-detail-uxui-audit-2026-05-22]] — **DONE.** 3-specialist audit: 32 issues. All P0/P1 implemented.
- [[homepage-uxui-audit-2026-05-31]] — **COMPLETED 2026-05-31.** 6-phase UX/UI audit. Commit `ade94ee`.
- [[seo-wave2-audit-2026-05-23]] — **DONE.** All 11 bugs verified + fixed + merged to main (`ceb0eac`).
- [[multitab-payment-gaps-2026-05-18]] — Original multitab payment gap analysis. Superseded by [[multitab-payment-race-condition-fixes]].
- [[payment-checkout-architecture-audit-2026-05-17]] — Original payment audit. Superseded by [[payment-checkout-architecture-audit]].
- [[payment-checkout-e2e-testing-2026-05-17]] — Original e2e testing notes. Superseded by [[payment-checkout-e2e-testing]].
- [[payment-system]] — Legacy payment system notes. Archived.
- [[payments-deep-dive]] — Legacy payment deep dive. Archived.
- [[payments-enums]] — Legacy payment enums. Superseded by [[payment-status-enums]].

## Systems

- [[ingestion-workflow]] — How to ingest sources into the vault
- [[atomic-notes]] — Rules for extracting single-concept notes; used by wrap-up atomize step + /lint-vault

## Templates

- [[project-readme]] — New project overview template
- [[research-summary]] — Source ingestion template
- [[bug-report]] — Bug documentation template
- [[architecture-review]] — ADR-style architecture review template

## Stats

- Created: 2026-05-16
- Pages: ~237 (active; 357 total including 08-archive)
- Last updated: 2026-06-12 (session #104: payment E2E automated 8/8, webhook gap closed via Tailscale, new atom omise-webhook-tailscale-local-testing)
- [[activities-browse-filter-inactive-contracts]] — FQ-0 P0: 1-line fix to send ?status=active to API
- [[usedayTripFilters-hydration-spurious-push]] — FQ-2 P1: router.query read pre-hydration → spurious push
- [[design-token-caption-tailwind-gotcha]] — DS-1 gotcha: Tailwind strings can't be used in MUI sx
- [[activities-location-search-backend-text-fallback]] — RC-1: _parse_int_list text fallback for city name search
- [[mui-autocomplete-inputvalue-sync]] — F-1: useEffect sync on value prop change to restore URL state
- [[mui-autocomplete-handlInputchange-parent-emit]] — F-2: handleInputChange must call onChange to emit to parent
- [[design-system-phase1-migration]] — Phase 1: 16 component files migrated from hardcoded hex to COLORS tokens. Exact-match only, zero visual changes.
- [[payment-amount-validation-rule]] — H1: server `(amount_thb - fee) == order.get_total_cost_after_discount()` ±1.00 THB
- [[payment-legacy-deprecation-map]] — 410-returning routes: `/api/payments/webhook-legacy/`, `/api/placeorder/`
- [[payment-orphan-charge-expire-pattern]] — M9: IntegrityError catch → `omise_charge.expire()` before re-raising
- [[payment-reconcile-gate-extension]] — H5: `finalize_payment` accepts `ordering`/`payment_failed`/`payment_pending` (guarded by `payment_finalized_at`)
- [[payment-guest-email-guard-mirror]] — M8: every charge entry point validates `order.email == data['email']` for unauth
- [[payment-cancel-state-prevmethod-guard]] — M3: `cancelState.success` reset guarded by `prevMethodRef`
- [[payment-idempotency-key-cart-total]] — H3: `X-Idempotency-Key: ${cartId}:${total}`; wrapped `{"message","order"}` shape
- [[payment-self-heal-coverage-matrix]] — M12: per-method self-heal coverage table (Card 3DS excluded)
- [[payment-cancel-vs-expire-error-mapping]] — reuse `useCancelPayment` hook + `expirePendingCharge` helper
- [[sidebar-sticky-2col-responsive-grid]] — 240px sidebar + 4-col 1440px card grid math
- [[orm-annotation-aggregate-min-rate]] — DRF `avg_rating` + `min_rate` annotation pattern
- [[wishlist-per-card-state-not-page]] — per-card `useState` for heart icon (avoid 80 re-renders/click)
- [[useeffect-cancellation-guard-pattern]] — `let cancelled=false` + check after each await
- [[useauth-axios-hook-factory]] — `useAuthAxios()` `useMemo([token])`; pass relative paths
- [[iconbutton-keydown-stoppropagation-card]] — nested IconButton needs BOTH `onClick` + `onKeyDown` `stopPropagation`
- [[lru-cache-content-type-lookup]] — `@lru_cache(maxsize=2)` for CT lookups; 12 hits/page eliminated
- [[seo-canonical-getsiteurl-pattern]] — `getSiteUrl()` → `https://www.smartenplus.co.th` (www mandatory)
- [[defaultseo-fallback-pattern]] — `<DefaultSeo>` with full OG + Twitter config in `_app.js`
- [[hero-cls-precise-sizes-attribute]] — `LocationGridComponent.js:59` `next/image` `sizes` per breakpoint
- [[getstaticprops-fetch-timeout-isr-blocking]] — 8s `fetchData()` timeout when `fallback:'blocking'` (else 500 cascade)
- [[touristtrip-schema-iso8601-departure-time]] — full ISO8601 with date prefix (prefix-less is silently invalid)
- [[og-image-1200x630-webp]] — default OG = WebP 1200×630 at `public/og-image.webp`
- [[homepage-section-render-order-conversion]] — trust-before-editorial review order
- [[tiered-empty-page-noindex-strategy]] — 3-tier: notFound:300 / noindex:3600 / fully indexed
- [[never-notfound-in-catch-block]] — ISR catch must never return `{notFound: true}`; serves stale props
- [[sitemap-filter-by-inventory-or-recency]] — pre-flight filter: `available_routes_count>0 || updated_at>365d`
- [[wordpress-faqpage-deprecation-note]] — `FAQPage` schema deprecated Aug 2023; use `<details>/<summary>` only
- [[gtm-purchase-item-category-attribute]] — `tripItems[].item_category: contract.service_category` unlocks revenue-by-category GA4
- [[multi-item-cart-anchor-last-transport]] — anchor = last transport item; rec type logic tree
- [[cross-sell-suppress-during-payment]] — DO NOT mount cross-sell during payment form interaction
- [[react-state-no-op-guard-side-effect-prevention]] — `prev===next ? return : set` guard for object refs
- [[sentinel-content-type-bookmark-blog]] — `Bookmark.objects.filter` MUST filter by `content_type=ContentType.objects.get_for_model(Bookmark)` (silent destructive bug)
- [[contract-fk-icontains-or-fallback]] — M2M+FK icontains search with `.distinct()`; cache-clear on deploy
- [[static-route-beats-catchall-priority]] — static `pages/help/faqs.js` wins over `pages/help/[...slug].js` automatically
- [[nextjs-fast-refresh-stale-hash-loop]] — N14.2.x framework gotcha; `webpack.watchOptions.ignored` is the only known fix
- [[mui-emotion-tailwind-injectfirst]] — `<StyledEngineProvider injectFirst>` + add `helpers/**/*` to tailwind content array
- [[migrate-bootstrap-palette-to-ds-tokens]] — replace Bootstrap legacy palette with `COLORS.status.*` tokens
- [[header-rows-context-dynamic-offset]] — Type A=80px / Type B=96px; StickySearchBar consumes `HeaderRowsContext`
- [[header-glass-to-solid-migration]] — glass→solid migration recipe; MUI AppBar `color="inherit"` gotcha
- [[build-experience-faq-items-pure-function]] — pure `buildExperienceFAQItems(contract)` helper; derive cancellation text from structured data (legal liability pattern)
- [[parseiso-null-guard-date-sort-pattern]] — `parseISO(null)` → Invalid Date → `compareAsc` NaN → page crash
