# SmartEnPlus — Project Overview

## Summary
Thailand transportation booking platform. Buses, ferries, speedboats, trains, airport transfers. Target: English-speaking international tourists.

## Status
Active.

## Stack
- Next.js 14 + React 18 (Pages Router)
- Redux Toolkit + RTK Query
- MUI + Tailwind CSS
- NextAuth.js (Google, Facebook, LINE, Naver, Apple)
- Omise (payments)
- Formik + Yup
- Django 4.2.16 + DRF (backend)
- PostgreSQL 14 + Redis 7.2 + Celery (backend)
- AWS S3/SES (backend)

## 3-Repo Ecosystem

| Repo | Role |
|------|------|
| `smartenplus-frontend` | Customer booking platform (this project) |
| `smartenplus-backend` | Django REST API — payments, bookings, operators, orders, tours |
| `admin-dashboard` | Internal admin panel |

API changes → update frontend AND admin-dashboard.

## Key Facts
- Cart item keys: `item.id` (stable_id removed 2026-02-13)
- Checkout sorting: chronological by `traveling_date` (earliest first) on ALL steps
- Checkout SSR: disabled via `dynamic(() => Promise.resolve(Index), { ssr: false })`
- ISR cache: `revalidate: 300` on trip detail pages
- Guest mode: `isGuestMode` in checkout-slice, persisted via redux-persist
- Logout: direct CSRF + signout fetch → `/api/auth/force-logout` (302). Never use NextAuth `signOut()`
- Self-profile: `GET /api/user/` (token-based). Admin-only: `GET/PUT /api/users/{id}` since 2026-05-07
- Order status: `payment_failed` is recoverable, not terminal

## Architecture
- See [[architecture]] (frontend)
- See [[backend-architecture]] (backend)
- Payment system: [[payment-system]]
- Checkout flow: [[checkout-flow]]

## Dev Commands
- `npm run dev` — localhost:3000
- `npm run build` — production build
- `npm ci --legacy-peer-deps` — install deps

## Related
- [[nextjs-patterns]]
- [[payment-integration]]
- [[design-systems]]
- [[backend-architecture]]

---

# 01-projects — MOC

## Project Index

### By domain

#### Architecture / Platform
- [[architecture]] — system architecture overview
- [[backend-architecture]] — backend overview
- [[frontend-architecture-audit-2026-06-11]] — frontend audit
- [[frontend-audit-implementation-2026-06-11]] — frontend impl
- [[admin-dashboard]] — admin dashboard
- [[docker-production]] — Docker prod setup
- [[smartenplus-wireframe-architecture]] — wireframes
- [[smartenplus-uxui-redesign-research-2026]] — redesign research

#### API / Data
- [[api-endpoints]] — endpoint catalog
- [[accounts]] — accounts domain
- [[bookings]] — bookings domain
- [[cart]] — cart domain
- [[cartitems-500-error-analysis-2026-06-02]] — cart 500
- [[coupons]] — coupons
- [[dialogue]] — dialogue
- [[operators]] — operators
- [[orders]] — orders
- [[policies]] — policies
- [[stations]] — stations
- [[tickets]] — tickets
- [[tour-system-status]] — tour system
- [[billings]] — billings
- [[recommendation-system]] — recommendations

#### Payment
- [[payment-auto-test-results-2026-06-12]] — auto test
- [[payment-deep-review-2026-06-12]] — deep review
- [[payment-deep-review-test-cases-2026-06-12]] — test cases
- [[payment-deep-review-verification-2026-06-12]] — verification
- [[payment-implement-plan-2026-06-12]] — impl plan
- [[payment-manual-test-skip-2026-06-12]] — manual skip
- [[booking-payment-e2e-audit-2026-06-11]] — booking e2e
- [[checkout-flow]] — checkout flow
- [[checkout-confirmation-payment-crash-2026-06-03]] — checkout crash
- [[checkout-null-contract-scan-2026-06-03]] — null contract
- [[checkout-uxui-audit-2026-06-10]] — checkout audit
- [[cross-sell-integration-status-2026-06-13]] — cross-sell status
- [[cross-sell-debate-review-2026-06-09]] — cross-sell debate
- [[implementation-plan-cross-sell-2026-06-09]] — cross-sell plan

#### Header / Navigation
- [[header-redesign-2026-spec]] — header spec
- [[header-redesign-2026-implementation]] — header impl
- [[header-redesign-2026-team-review]] — team review
- [[nav-header-redesign]] — nav header
- [[mobile-header-analysis-2026-05-26]] — mobile analysis
- [[smartenplus-glassmorphism-header]] — glass header

#### Homepage
- [[homepage-ux-review-2026-05-21]] — UX review
- [[homepage-seo-performance-deep-review-2026-05-21]] — SEO perf
- [[homepage-terminology-audit-2026-06-05]] — terminology
- [[hero-banner-cms]] — hero CMS
- [[hero-section-comprehensive-audit-2026-05-26]] — hero audit

#### Activities / Trips
- [[activities-day-tour-page-review-2026-06-01]] — day tour
- [[activities-location-search-bug-2026-06-01]] — location bug
- [[activities-search-merge-review-2026-06-01]] — search merge
- [[destinations-redesign-review]] — destinations
- [[airport-transfer-redesign-2026]] — airport transfer
- [[experience-detail-page-redesign-2026-06-02]] — experience detail
- [[experience-detail-ipad-mobile-redesign-2026-06-02]] — iPad/mobile
- [[experience-faq-architecture-review-2026-06-02]] — FAQ arch
- [[operator-card-badge-consistency-2026-06-16]] — operator badge
- [[operator-detail-page-redesign-2026-06-16]] — operator detail
- [[operator-detail-seo-aeo-geo-audit-2026-06-16]] — operator SEO
- [[trip-search-results-redesign-2026-06-14]] — trip search
- [[trip-search-results-implementation-plan-2026-06-14]] — trip search impl
- [[trip-search-below-fold-redesign-2026-06-15]] — below-fold
- [[trip-page-full-audit-2026-06-15]] — trip full audit
- [[trip-filter-modal-audit-2026-06-15]] — trip filter
- [[trip-route-page-seo-aeo-geo-audit-2026-06-15]] — trip route SEO
- [[profile-dropdown-redesign-2026-05-29]] — profile dropdown
- [[timeline-update-display-bug-2026-06-01]] — timeline bug

#### Rate Review
- [[rate-review-uxui-audit-2026-06-06-overview]] — overview

#### SEO / Performance
- [[blog-seo-performance-2026-05-20]] — blog SEO
- [[seo-sitemap-whole-site-audit-2026-06-11]] — sitemap audit
- [[gsc-crawled-not-indexed-investigation-2026-06-05]] — GSC investigation
- [[og-image-ssr-fix-2026-05-23]] — og SSR fix
- [[isr-429-cold-start-fix-2026-05-23]] — ISR 429
- [[fast-refresh-infinite-loop-audit-2026-05-23]] — fast-refresh loop
- [[currency-context-infinite-fetch-2026-05-23]] — currency fetch
- [[hydration-infinite-refresh-fix-2026-05-20]] — hydration loop

#### Testing
- [[frontend-test-infrastructure-audit-2026-06-03]] — test infra
- [[filter-functionality-audit-2026-06-15]] — filter functionality audit

#### Strategy / BD
- [[business-development-thesis-2026-2029]] — 3-year thesis
- [[business-development-thailand-platform-analysis]] — Thailand platform
- [[business-development-thailand-bundle-architecture]] — Thailand bundle
- [[business-development-zeitrip-mvp]] — Zeitrip MVP
- [[next-priority-debate-2026-06-09]] — next priority

### Subfolders (schema deviation: nested = audit family with r1/r2/r3)
Each subfolder has its own README enumerating the family.

- [[activities-pagination-ux-audit-2026-06-05/README]] — 5 rounds
- [[favorite-heart-analysis-2026-06-08/README]] — 7 rounds
- [[gyg-card-rate-analysis-2026-06-05/README]] — 3 rounds
- [[gyg-page-analysis-2026-06-04/README]] — 5 rounds
- [[help-faqs-landing-2026-06-07/README]] — 1 round
- [[rate-review-uxui-audit-2026-06-06/README]] — 7 rounds
- [[trip-detail-seo-aeo-geo-audit-2026-06-16/README]] — 6 rounds
- [[website-audit-full-2026-06-06/README]] — 5 rounds

## Conventions for this folder
- One project = one scope, end date, decision
- 88 root notes + 8 subfolders; subfolders house multi-round audit families
- Subfolder README enumerates child rounds; do not move children
- When project closes: move superseded files to [[08-archive/README]]; current stays
