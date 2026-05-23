# Second Brain — Index

Global navigation catalog. Updated on every ingest.

---

## Meta

- [[master-state|Master State]] — Live session state: branches, loose ends, API contract, architecture guardrails

## Active Projects

- [[isr-stale-data-audit-2026-05-23|ISR Stale Data Audit 2026-05-23]] — Next.js ISR revalidate:300 broken in Docker standalone. Pages never regenerate. Fix: on-demand revalidation API route. **2 blockers + 3 major findings from team audit — reword before implementing**
- [[fast-refresh-infinite-loop-audit-2026-05-23|Fast Refresh Infinite Loop Audit 2026-05-23]] — Root cause unconfirmed. RefreshTokenHandler diagnosis OVERTURNED (lastExpiryRef guard). Likely Next.js 14.2.x HMR + on-demand compilation cascade. 7 failed fixes documented. Next: debug instrumentation + git bisect
- [[currency-context-infinite-fetch-2026-05-23|CurrencyContext Infinite Fetch 2026-05-23]] — race condition + unstable selectCurrency ref; fix applied on branch 260523-fix/currency-context-infinite-fetch
- [[isr-429-cold-start-fix-2026-05-23|ISR 429 Cold-Start Fix 2026-05-23]] — cold `npm run dev` bursts `/front-page/` → 429; root: REVALIDATE_SECONDS=60 + refetchOnMountOrArgChange:300; fixes identified, not yet applied
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
- [[nav-header-redesign|Nav/Header Redesign 2026-05-19]] — minimal white desktop, brand blue mobile, a11y baseline, MUI+Tailwind coordination patterns
- [[hero-banner-cms|Hero Banner CMS 2026-05-19]] — backend-controlled homepage hero, FileField+AVIF fix, admin dashboard CRUD, 5s slideshow
- [[blog-seo-performance-2026-05-20|Blog SEO & Performance 2026-05-20]] — parallel fetches, image optimization, HMR fixes, patterns to reuse
- [[hydration-infinite-refresh-fix-2026-05-20|Hydration Infinite Refresh Fix 2026-05-20]] — all-page HMR loop from 4 hydration issues; agent accuracy ~55%; PersistGate SSR pattern
- [[trip-detail-page-review-2026-05-20|Trip Detail Page Review 2026-05-20]] — 3-agent review: 8 perf + 8 SEO + 8 code quality issues; 24 verified findings with line numbers and fix order
- [[trip-detail-deep-review-2026-05-20|Trip Detail Deep Review 2026-05-20]] — 4-agent adversarial pass: 3 findings overturned, 8 hidden issues, 4 prod failure scenarios; top risks: ratecard wipe, fetch timeout, invalid ISO8601 schema
- [[homepage-ux-review-2026-05-21|Homepage UX/UI Review 2026-05-21]] — 3-agent review, 11 sections, 4 critical + 34 major issues; XSS in reviews, section reorder, inline validation, hero value prop
- [[homepage-seo-performance-deep-review-2026-05-21|Homepage SEO & Performance Deep Review 2026-05-21]] — 3-specialist audit: structured data errors (fake phone/address, stale dates), Technical SEO gaps (server-sitemap 404, og:locale, DefaultSeo), CWV risks (CLS, preconnect); priority fix queue
- [[og-image-inferred-audit-2026-05-23|OG Image "Inferred" Audit 2026-05-23]] — Homepage + blog og:image broken. RC1: NEXT_PUBLIC_DOMAIN undefined → Seo crash. RC2: missing secureUrl on all blog pages. Fix pending branch 260523-fix/og-image-homepage-and-blog

## Knowledge Domains

- [[smartenplus-synopsis]] — Project-wide orientation: stack, repos, payment, auth, current state, open work
- [[ai-workflows]] — LLM Wiki pattern, ingestion/query/lint operations
- [[nextjs-patterns]] — ISR, dynamic SSR disable, RTK Query, date handling
- [[payment-integration]] — Thai payment methods, Omise source types, webhook flows, checkout architecture principles (28 use cases), centralized payment error detection
- [[celery-tasks|Celery Tasks]] — bind=True pattern, exponential backoff, high-risk task guards, beat schedule
- [[refund-flow|Refund Flow]] — payments.Refund model, cards.Refund (legacy), RefundViewSet deprecation
- [[journeys|Journeys]] — UserJourneyEvent analytics, event types, metadata, dedup guard pattern
- [[design-systems]] — Token-based design system approach
- [[admin-dashboard-contracts]] — Category registry, form flow, payload rules, helpers
- [[admin-dashboard-image-pipeline]] — Frontend image state, error reset hooks, dedup helpers
- [[admin-dashboard-component-patterns]] — Formik+Yup, RTK Query, MUI patterns, gotchas
- [[mui-tailwind-css-specificity]] — MUI Emotion overrides Tailwind className on MUI components; use sx prop or div wrapper; sx responsive breakpoints fail without Emotion cache provider
- [[payment-sentinel-idempotency]] — Timestamp sentinels as exactly-once guards; reusable for any side effect (email, booking, settlement)
- [[nextauth-session-shape]] — `session.user.email` not `session.email`; auth check via `session?.id`; guest email sources
- [[cart-reprovision-after-reset]] — `resetCart()` + fire-and-forget `createCart()` pattern; required on 2 order pages not wrapped in `withCartValidation`
- [[promptpay-no-webhook-on-expiry]] — PP/MB expiry has no Omise webhook; all 3 expiry paths must call `_send_payment_failed_notifications()`
- [[nextjs-isr-ratecard-empty-array-guard]] — `??` doesn't catch `[]`; use `?.length > 0` when merging CSR arrays into ISR baseline
- [[nextjs-307-vs-301-product-reclassify]] — Keep `permanent: false` on product-type redirects; 301 causes browser/CDN cache pollution on reclassification
- [[seo-homepage-specialist-team]] — SEO specialist team: 3-role sequential audit workflow, how to invoke, pre-conditions, known gaps found on first run 2026-05-21

## Areas

- [[engineering]] — Software engineering practices and standards
- [[business]] — Business operations and strategy

## Decisions

- [[adr-template]] — Architecture Decision Record template
- [[atomic-note]] — Single-concept note template for extracted atoms

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
- Pages: 55
- Last updated: 2026-05-23 (ISR stale data audit added)
