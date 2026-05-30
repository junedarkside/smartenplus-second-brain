# Second Brain — Index

Global navigation catalog. Updated on every ingest.

---

## Meta

- [[master-state|Master State]] — Live session state: branches, loose ends, API contract, architecture guardrails

## Active Projects

- [[profile-dropdown-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** 3-specialist review. 11→6 items, 296px, pill trigger, bottom sheet mobile, 3-file split. MUI-preserve strategy. Implemented on `260528-feat/header-redesign-2026`.

- [[check-your-booking-redesign-2026-05-29]] — **COMPLETED 2026-05-29.** OTA utility card adopted. Illustration removed. 840px centered card, warm-surface bg, larger inputs, trust row with fixed copy. Eyebrow removed per judge ruling.

- [[destinations-redesign-review]] — Destinations section review: editorial grid vs carousel tradeoffs, image overlay patterns, mobile-first layout decisions.
- [[airport-transfer-redesign-2026]] — **COMPLETED 2026-05-30.** Omio-style route cards. Backend: airport_routes key in /front-page/ API. Frontend: AirportTransferRouteCard + AirportTransferSection rewrite. Style audit 8 fixes. Data shape bug fixed (StationSerializer shadow). Professional redesign spec ready (AT-1) — see [[transportation-category-audit-2026-05-30]].
- [[travel-thailand-better-section-redesign]] — **COMPLETED 2026-05-29.** `ce4d2d7` on `260528-feat/header-redesign-2026`. Replace 3 editorial sections with 1 unified "Travel Thailand Better" section. 1 featured + 2 secondary cards. AutoStoriesOutlined icon. Tailwind lib/ scan bug fixed.
- [[header-redesign-2026-spec]] — **FINAL 2026-05-28.** Adaptive Type A/B header. Type A: single-row 80px (transactional). Type B: 2-row 96px (discovery/browse). All 5 nav items kept. /blog → Type B. Dynamic layout offset. 12-file implementation plan. 4-day rollout + 2 separate PRs.
- [[header-redesign-2026-implementation]] — **Days 1–3 DONE 2026-05-28.** Branch `260528-feat/header-redesign-2026` commit `a4158b0`. 10 files. QA + AT-1 redesign pending before merge.
- [[header-redesign-2026-team-review]] — 3-specialist audit (Design+UX+Frontend) + second audit (UX Architecture+Visual Design+Frontend Eng). All blockers resolved. Key decisions locked: Type A/B split, keep Explore Thailand, /blog = Type B, dynamic offset 80/96px, HeaderRowsContext pattern.
- [[smartenplus-header-ux-v1]] — COMPLETED 2026-05-25. Desktop 2-row header: Row 1 (logo + THB + cart + profile), Row 2 (5 nav items, desktop only). Help Center added to profile dropdown. Submenus deferred.
- [[backend-n8n-resend-webhook]] — Resend Operator n8n webhook forwarding. send_booking_data moved to bookings/tasks.py. 4 commits, merged to develop. 3 bugs caught by scrutinize audit (import crash ×2, orphaned try block) + 1 env var crash on startup (N8N_WEBHOOK_URL missing default=None)
- [[fast-refresh-infinite-loop-audit-2026-05-23|Fast Refresh Infinite Loop Audit 2026-05-23]] — Root cause unconfirmed. RefreshTokenHandler diagnosis OVERTURNED (lastExpiryRef guard). Likely Next.js 14.2.x HMR + on-demand compilation cascade. 7 failed fixes documented. Next: debug instrumentation + git bisect
- [[currency-context-infinite-fetch-2026-05-23|CurrencyContext Infinite Fetch 2026-05-23]] — race condition + unstable selectCurrency ref; fix applied on branch 260523-fix/currency-context-infinite-fetch
- [[isr-429-cold-start-fix-2026-05-23|ISR 429 Cold-Start Fix + Stale Data 2026-05-23]] — cold `npm run dev` bursts `/front-page/` → 429; root: REVALIDATE_SECONDS=60 + refetchOnMountOrArgChange:300; fixes identified. + ISR stale data in Docker standalone, on-demand revalidation fix via Celery task
- [[daytrips-to-activities-rename-2026-05-23|Daytrips → Activities Rename 2026-05-23]] — COMPLETED 2026-05-23 — /daytrips → /activities rename, 7 phases + 5 scrutiny fixes, merged → develop d424d4e; deploy: clear ISR cache + resubmit GSC sitemap
- [[trip-detail-uxui-audit-2026-05-22|Trip Detail UX/UI Audit 2026-05-22]] — 3-specialist audit: 32 issues, ContentCard abstraction absent, full-bleed mobile cards, typography violations, CLS fallbacks; all P0/P1 implemented in branch 260522-fix/trip-detail-ux
- [[README|SmartEnPlus]] — Thailand transport booking platform (Next.js 14, Redux, Omise)
- [[architecture|SmartEnPlus Architecture]] — Redux slices, RTK Query, component structure
- [[payment-system|SmartEnPlus Payments]] — Omise integration, GatewayCharge, QR polling, payment internals
- [[payment-checkout-architecture-audit-2026-05-17|Payment Checkout Audit 2026-05-17]] — 20/20 pass, getPrimaryCharge fix, PromptPay exclusion
- [[multitab-payment-gaps-2026-05-18|Multi-Tab Payment Gaps 2026-05-18]] — All 7 gaps resolved, backend+frontend, 242 tests pass
- [[payment-checkout-e2e-testing-2026-05-17|Payment Checkout E2E Testing 2026-05-17]] — 6-agent test suite, data-testid fix, 23+ specs written
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
- [[payments-deep-dive|Payments Deep Dive]] — create_charge, reconcile, _to_minor_units, JPY
- [[payments-enums|Payments Enums]] — PaymentStatus, OmiseMethod, REDIRECT_METHODS, METHOD_EXPIRY
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
- [[smartenplus-wireframe-architecture|SmartEnPlus Wireframe Architecture]] — Full platform wireframe + information architecture. 15 sections: homepage, hero, journeys, destinations, search results, experiences, routes, guides, mobile strategy, design system.
- [[smartenplus-uxui-redesign-research-2026|SmartEnPlus 2026 UX/UI Redesign Research]] — Strategic direction: "premium operational transportation platform" not cinematic travel website. Compact 45-60vh hero, calm premium minimalism, efficiency-first UX. Header, search module, section redesign strategy.

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
- [[carousel-design-standard]] — Embla carousel items-per-screen breakpoints, gap values, card widths, focus ring handling
- [[admin-dashboard-contracts]] — Category registry, form flow, payload rules, helpers
- [[admin-dashboard-image-pipeline]] — Frontend image state, error reset hooks, dedup helpers
- [[admin-dashboard-component-patterns]] — Formik+Yup, RTK Query, MUI patterns, gotchas
- [[django-serializer-shadowing-pattern]] — Local class redefines imported name in same file; silently changes exposed fields. Discovered via HomeSerializer/StationSerializer in products/serializers.py.
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
- [[smartenplus-product-positioning]] — "Thailand Travel Infrastructure Platform." 5 DNA layers (transportation, experiences, route intelligence, editorial, trust). Core value: "Explore Thailand Easily."
- [[smartenplus-2026-ux-direction]] — Strategic shift: cinematic → operational. Compact 45-60vh hero, calm premium minimalism, efficiency-first. Header, search, section redesign strategy.
- [[mobile-header-scroll-behavior-change]] — Mobile header: dynamic (relative+Slide) → permanently fixed. Spacer removed, DOM paths diverged. 4 issues documented.

## Areas

- [[engineering]] — Software engineering practices and standards
- [[business]] — Validated strategy: B2B supplier (12Go+Klook 90%) + B2C direct (10%). EN customer confirmed. Vertical integration moat. "Stippl for SEA with real booking" vision.
- [[southeast_asia_transport_platform_direction]] — Product vision: SEA transport + experience infra platform. Stippl plans but can't book; 12Go books but can't plan — SmartEnPlus does both. B2B supplier → B2C direct roadmap. Core loop: destinations+dates+interests → AI plan → book.

## Decisions

- [[adr-template]] — Architecture Decision Record template
- [[atomic-note]] — Single-concept note template for extracted atoms

## Archive

- [[mobile-header-redesign-glassmorphism]] — SUPERSEDED 2026-05-28 by [[header-redesign-2026-spec]]. Dark gradient glass, sticky+blur on scroll, unified 2-row. Kept for reference.

## Systems

- [[ingestion-workflow]] — How to ingest sources into the vault
- [[atomic-notes]] — Rules for extracting single-concept notes; used by wrap-up atomize step + /lint-vault

## Templates

- [[project-readme]] — New project overview template
- [[research-summary]] — Source ingestion template
- [[bug-report]] — Bug documentation template
- [[architecture-review]] — ADR-style architecture review template

- [[content-marketing-strategy-2026-05-24|Content Marketing Strategy 2026-05-24]] — 5-agent review + full playbook rewrite. 6 contradictions fixed, keyword opportunities, tech stack integrated.

## Stats

- Created: 2026-05-16
- Pages: 72
- Last updated: 2026-05-30 (vault optimize: fixed folder structure, archived glassmorphism, updated stale statuses, added missing entries)
