# Second Brain — Index

Global navigation catalog. Updated on every ingest.

---

## Meta

- [[master-state|Master State]] — Live session state: branches, loose ends, API contract, architecture guardrails

## Active Projects

- [[experiences-2026-marketplace-redesign]] — **PLANNED 2026-06-01.** 4-phase redesign of `/activities` → world-class 2026 marketplace. Sidebar layout, 4-col grid, premium card, sort bar. Phase 1: frontend-only. Phase 2: backend filter params. Phase 3: mobile. Phase 4: iPad polish.

- [[profile-dropdown-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** 3-specialist review. 11→6 items, 296px, pill trigger, bottom sheet mobile, 3-file split. MUI-preserve strategy. Implemented on `260528-feat/header-redesign-2026`.

- [[check-your-booking-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** OTA utility card adopted. Illustration removed. 840px centered card, warm-surface bg, larger inputs, trust row with fixed copy. Eyebrow removed per judge ruling.

- [[destinations-redesign-review]] — Destinations section review: editorial grid vs carousel tradeoffs, image overlay patterns, mobile-first layout decisions.
- [[featured-image-header-width-bug-2026-05-30]] — **RESOLVED 2026-05-30.** `w-[1200px]` hardcoded in `0ebd755` broke mobile. Fix: revert to `w-full` + `max-w-[1200px]`. Rule: never use `w-[Npx]` on layout-spanning elements. `FeaturedImageHeader.js:121`.
- [[airport-transfer-width-audit-2026-05-30]] — **UNRESOLVED.** Post-calendar sections (StationInformation + GuidesSection) visually narrower than calendar. Root cause: inner `px-2 md:px-3` + `mx-2` margins eating into max-w-[1200px] content. Fix attempt reverted (broke layout). Next team: redesign sections as full-width with centered inner content, OR accept current padding as correct. Shared component `ProductCardContainer.js` involvement complicates fix.
- [[header-redesign-2026-spec]] — **FINAL 2026-05-28.** Adaptive Type A/B header. Type A: single-row 80px (transactional). Type B: 2-row 96px (discovery/browse). All 5 nav items kept. /blog → Type B. Dynamic layout offset. 12-file implementation plan. 4-day rollout + 2 separate PRs.
- [[hero-back-share-buttons-2row-header-fix]] — **UNVERIFIED 2026-05-30.** Back/Share pills moved from `FeaturedImageHeader` to outer wrapper of `TripDetailHero`/`DayTripHero`. Glassmorphism style. Server was in production mode — needs `npm run dev` to verify. See note for full debug trail + root causes.
- [[header-redesign-2026-implementation]] — **Days 1–3 DONE 2026-05-28.** Branch `260528-feat/header-redesign-2026` commit `a4158b0`. 10 files. QA + AT-1 redesign pending before merge.
- [[timeline-update-display-bug-2026-06-01]] — **IN PROGRESS.** Timeline page display breaks after save. Suspected payload key mismatch (`dndCharacterData` vs `timeline`) + place object vs ID. Multi-agent investigation pending.
- [[activities-day-tour-page-review-2026-06-01]] — 3-specialist code audit of `/activities?category=DAY_TOUR`. 2 Critical (skeleton mismatch, dual unlabeled search), 5 Major, 5 Minor. Fix sequence documented.
- [[activities-location-search-bug-2026-06-01]] — **IN PROGRESS.** 4-specialist team audit. Location search returns zero results. 3 critical bugs: backend text→ID type mismatch (`products/views.py:446`), `inputValue` divergence (`DayTripLocationSearch.js:20`), freetext not emitting to parent (`DayTripLocationSearch.js:26`). Fix sequence documented.
- [[activities-search-merge-review-2026-06-01]] — **UPDATED 2026-06-01.** 3-specialist review + grill. True merge "backend blocker" claim OVERTURNED — intent detection via static `keywords[]` match, no backend change needed. Blocked by tech debt: 2 incompatible `POPULAR_DESTINATIONS` sources. Next: consolidate → `utils/destinations.js` (ACT-5), then build unified `ActivitySearch` (ACT-6).
- [[header-redesign-2026-team-review]] — 3-specialist audit (Design+UX+Frontend) + second audit (UX Architecture+Visual Design+Frontend Eng). All blockers resolved. Key decisions locked: Type A/B split, keep Explore Thailand, /blog = Type B, dynamic offset 80/96px, HeaderRowsContext pattern.
- [[backend-n8n-resend-webhook]] — Resend Operator n8n webhook forwarding. send_booking_data moved to bookings/tasks.py. 4 commits, merged to develop. 3 bugs caught by scrutinize audit (import crash ×2, orphaned try block) + 1 env var crash on startup (N8N_WEBHOOK_URL missing default=None)
- [[fast-refresh-infinite-loop-audit-2026-05-23|Fast Refresh Infinite Loop Audit 2026-05-23]] — Root cause unconfirmed. RefreshTokenHandler diagnosis OVERTURNED (lastExpiryRef guard). Likely Next.js 14.2.x HMR + on-demand compilation cascade. 7 failed fixes documented. Next: debug instrumentation + git bisect
- [[currency-context-infinite-fetch-2026-05-23|CurrencyContext Infinite Fetch 2026-05-23]] — race condition + unstable selectCurrency ref; fix applied on branch 260523-fix/currency-context-infinite-fetch
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
- [[tickets|Tickets]] — Ticket model, GenericForeignKey attachable to any model, HistoricalRecords audit
- [[admin-dashboard|Admin Dashboard]] — Admin interface for SmartEnPlus platform
- [[smartenplus-glassmorphism-header|Premium Glassmorphism Header]] — dark gradient glass, sticky + blur on scroll, unified 2-row, white typography, hero integration. Supersedes header-ux-v1.
- [[adr-experiences-nav-category-filtering-2026-05-25|ADR: Experiences Nav Category Filtering]] — URL param → server-side API filter chain. Full category enum, navConfig values, contrast with client-side approach.
- [[nav-header-redesign|Nav/Header Redesign]] — Full nav evolution: Phase 0 label changes (Explore Thailand, Routes, Journeys, Experiences, Guides), Phase 1 Experiences dropdown, Phase 3 backend API + bug fixes. 6-agent validation. All submenus removed — single source of truth. A11y baseline, MUI+Tailwind coordination patterns
- [[hero-banner-cms|Hero Banner CMS 2026-05-19]] — backend-controlled homepage hero, FileField+AVIF fix, admin dashboard CRUD, 5s slideshow
- [[blog-seo-performance-2026-05-20|Blog SEO & Performance 2026-05-20]] — parallel fetches, image optimization, HMR fixes, patterns to reuse
- [[hydration-infinite-refresh-fix-2026-05-20|Hydration Infinite Refresh Fix 2026-05-20]] — all-page HMR loop from 4 hydration issues; agent accuracy ~55%; PersistGate SSR pattern
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

- [[docker-standalone-isr-revalidate-gap]] — ISR timer gap in Docker standalone, deploy volume clear workaround
- [[on-demand-revalidation-api-route]] — pages/api/revalidate.js pattern, auth, 207 Multi-Status
- [[celery-task-over-bare-thread-django-signals]] — why Celery over threads for signal side effects, slug dedup, retry
- [[isr-csr-overlay-stale-fields]] — CSR covers ratecard/dates; stale: name/description/images/JSON-LD/meta
- [[persistgate-ssr-suppresses-head-component]] — PersistGate null SSR blocks DefaultSeo/Head; hoisting fix
- [[webpack-image-src-og-absolute-url-rule]] — webpack .src relative → absolute for OG images

## Knowledge Domains

- [[smartenplus-synopsis]] — Project-wide orientation: stack, repos, payment, auth, current state, open work
- [[ai-workflows]] — LLM Wiki pattern, ingestion/query/lint operations
- [[nextjs-patterns]] — ISR, dynamic SSR disable, RTK Query, date handling
- [[payment-integration]] — Thai payment methods, Omise source types, webhook flows, checkout architecture principles (28 use cases), centralized payment error detection
- [[celery-tasks|Celery Tasks]] — bind=True pattern, exponential backoff, high-risk task guards, beat schedule
- [[refund-flow|Refund Flow]] — payments.Refund model, cards.Refund (legacy), RefundViewSet deprecation
- [[journeys|Journeys]] — UserJourneyEvent analytics, event types, metadata, dedup guard pattern
- [[design-systems]] — Token-based design system approach
- [[design-system-audit-2026-05-31]] — Design system audit: brand color (#3b5998), token gaps, hardcoded values found across components
- [[carousel-design-standard]] — Embla carousel items-per-screen breakpoints, gap values, card widths, focus ring handling
- [[admin-dashboard-contracts]] — Category registry, form flow, payload rules, helpers
- [[pdf-contract-import-research]] — Team research + decision: Django+Claude tool_use pipeline for parsing non-standard operator PDFs to update contracts. Phase 1 scope + deferred Phase 2.
- [[admin-dashboard-image-pipeline]] — Frontend image state, error reset hooks, dedup helpers
- [[admin-dashboard-component-patterns]] — Formik+Yup, RTK Query, MUI patterns, gotchas
- [[django-serializer-shadowing-pattern]] — Local class redefines imported name in same file; silently changes exposed fields. Discovered via HomeSerializer/StationSerializer in products/serializers.py.
- [[homepage-experiences-section-audit-2026-05-30]] — Feasibility audit: add "Explore Experiences" carousel to homepage. Verdict: VIABLE after AT-1 + inventory check. Backend ready (Contract model). 5 files, ~160 lines. Reuses CardCarouselContainer + PopularRoutesSection pattern.
- [[transportation-category-audit-2026-05-30]] — Full audit: 3-level category system (station_type / service_category / VehicleType), airport filter vs TRANSFER category decoupled, 26 station_types, lowest_price nullable, query_count Celery mechanism. Professional homepage section redesign spec (AT-1): image card + IATA badge + carousel mobile + serializer expansion.
- [[mui-tailwind-css-specificity]] — MUI Emotion overrides Tailwind className on MUI components; use sx prop or div wrapper; sx responsive breakpoints fail without Emotion cache provider
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
- [[pdf-contract-import-adversarial-review]] — 6 red flags for PDF import arch: async AI call required, soft-delete draft, remove LLM matching, pre-validation, no confidence auto-accept, large-delta warning. 3-screen UX. All must resolve before first commit.
- [[django-async-ai-call-pattern]] — Django sync LLM calls block WSGI workers. Pattern: return `task_id` immediately, Celery handles AI call, frontend polls status endpoint.

- [[payment-gateway-charge-architecture]] — GatewayCharge model, finalize_payment() SSOT, locked_amount freeze, webhook sole finalization
- [[payment-charge-service-layer]] — create_charge, reconcile, idempotency hash, _to_minor_units, JPY handling
- [[payment-status-enums]] — PaymentStatus machine, OmiseMethod constants, REDIRECT_METHODS, METHOD_EXPIRY TTLs
- [[multitab-payment-race-condition-fixes]] — 7 race conditions, select_for_update cart-wide lock, frontend reconciliation
- [[payment-checkout-architecture-audit]] — 20/20 audit, getPrimaryCharge fix, cancelState guards, qrState clear
- [[payment-checkout-e2e-testing]] — MSW intercept bug, 5 bugs fixed, session structure rule, manual test guide
- [[adaptive-header-route-type-pattern]] — Type A/B split (transactional/discovery), dynamic offset 80/96px, HeaderRowsContext
- [[structured-data-schema-patterns]] — TravelAgency schema accuracy, WebSite+SearchAction, server-sitemap.xml 404 crawl budget
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

## Areas

- [[engineering]] — Software engineering practices and standards
- [[business]] — Validated strategy: B2B supplier (12Go+Klook 90%) + B2C direct (10%). EN customer confirmed. Vertical integration moat. "Stippl for SEA with real booking" vision.
- [[southeast-asia-transport-platform-direction]] — Product vision: SEA transport + experience infra platform. Stippl plans but can't book; 12Go books but can't plan — SmartEnPlus does both. B2B supplier → B2C direct roadmap. Core loop: destinations+dates+interests → AI plan → book.

## Decisions

- [[adr-template]] — Architecture Decision Record template
- [[atomic-note]] — Single-concept note template for extracted atoms

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
- Pages: 96
- Last updated: 2026-06-01 (session #17: build error fix + atomic note)
