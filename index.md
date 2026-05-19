# Second Brain — Index

Global navigation catalog. Updated on every ingest.

---

## Meta

- [[master-state|Master State]] — Live session state: branches, loose ends, API contract, architecture guardrails

## Active Projects

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
- [[recommendation-system|Recommendation System]] — precompute tasks, cache warming, beat schedule
- [[tickets|Tickets]] — Ticket model, GenericForeignKey attachable to any model, HistoricalRecords audit
- [[admin-dashboard|Admin Dashboard]] — Admin interface for SmartEnPlus platform
- [[nav-header-redesign|Nav/Header Redesign 2026-05-19]] — minimal white desktop, brand blue mobile, a11y baseline, MUI+Tailwind coordination patterns
- [[hero-banner-cms|Hero Banner CMS 2026-05-19]] — backend-controlled homepage hero, FileField+AVIF fix, admin dashboard CRUD, 5s slideshow
- [[blog-seo-performance-2026-05-20|Blog SEO & Performance 2026-05-20]] — parallel fetches, image optimization, HMR fixes, patterns to reuse

## Knowledge Domains

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

## Areas

- [[engineering]] — Software engineering practices and standards
- [[business]] — Business operations and strategy

## Decisions

- [[adr-template]] — Architecture Decision Record template

## Systems

- [[ingestion-workflow]] — How to ingest sources into the vault

## Templates

- [[project-readme]] — New project overview template
- [[research-summary]] — Source ingestion template
- [[bug-report]] — Bug documentation template
- [[architecture-review]] — ADR-style architecture review template

## Stats

- Created: 2026-05-16
- Pages: 42
- Last updated: 2026-05-19 (tour-system-status.md created — Phase 2 gaps, trust signals, doc pointers)
