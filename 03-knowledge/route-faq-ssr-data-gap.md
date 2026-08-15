# RouteFAQ SSR Data Gap — Trip Route Page FAQ Renders Generic Filler

## Status: FIXED, merged → develop both repos (2026-08-15)
Backend: `smartenplus-backend` `develop a7eb4f1` (feature commit `a912cf3`) — `route_faq` aggregate added to `HomeViewSet.custom_route`.
Frontend: `smartenplus-frontend` `develop bd651b33` (feature commit `e2400fe4`) — wired through `getStaticProps` → `RouteFAQ.js`, added 7th question (cancellation).
`next build` verified real data renders in static HTML for `/trips/hatyai/koh-lipe` and `/trips/hatyai/penang`; zero-contract routes confirmed to skip FAQ rendering cleanly. **Remaining:** browser-verify, BE unit test for the new helpers (not written), develop→main deploy.

## Summary
`components/trips/RouteFAQ.js` on `/trips/[from]/[to]` route pages computes real FAQ answers (price, duration, operator count, first departure, direct/transfer) from a `tripsFilterSet` prop that is always empty at SSR time. Prod HTML (verified live via curl on `/trips/hatyai/koh-lipe`, 2026-08-15) serves the generic fallback string for 5 of 6 FAQ items to every crawler and non-JS client. Third occurrence of the same bug class in this codebase.

## Context
Real-data computation logic already exists in the component — `minRate`, `durationRange`, `operatorCount`/`operatorNames`, `firstDeparture`, `hasDirect` are all derived correctly from `tripsFilterSet` when populated. The component is not broken; the data wiring to it is.

## Problem
Two props feed `RouteFAQ`:
1. `contracts` — populated via `getStaticProps` (`pages/trips/[...slug].js:80`, SSR/ISR from `admin-dashboard-routes/home/<from>/<to>`). Works. This is why the "transport types available" answer partially renders real data ("Shared Ride") in prod.
2. `tripsFilterSet` — populated via `hooks/useTripData.js:20` → `useGetTripFilterSetQuery`, an RTK Query hook. Client-side only, fetched post-hydration, keyed on `activeDate` which starts unset. `FilterTripsPage.js:60` wraps `RouteFAQ` in `dynamic(() => import('./RouteFAQ'))` with no `ssr:false` — Next.js does SSR the component, but at SSR time the RTK Query fetch hasn't resolved, so `tripsFilterSet` is `undefined` server-side regardless of the `dynamic()` wrapper. The fallback branches fire and get baked into the static HTML.

Backend already computes all these fields server-side per-request in `products/views.py:1741-1938` (`FindTripViewSet.list`, behind `getTripFilterSet`) — but that endpoint is inherently date-scoped (`traveling_date` query param) and was never wired into the page's `getStaticProps`. A naive "just call it in getStaticProps" fix doesn't work as-is: ISR/SSG has no date at build time, and the endpoint's numbers (today's cheapest run, today's first departure) are meaningfully date-specific, not just missing.

## Detection
```bash
curl -s https://www.smartenplus.co.th/trips/hatyai/koh-lipe | grep -o '"mainEntity":\[[^]]*\]'
# 5 of 6 answers are generic fallback text — no price, no duration, no operator names, no departure time, no direct-route confirmation
```

## Fix (shipped, full report + 3-specialist debate in check-vault-and-http-localhost-3000-trip-linear-cook.md plan file)
Extended the already-fetched `admin-dashboard-routes/home/<from>/<to>` response with a **date-independent** aggregate block (min price + which contract/operator it came from, full operator list, has-any-direct-route flag, cancellation summary) — reuses existing `_get_display_rate` logic rather than re-deriving. Passed as a new `routeFaq` prop through `getStaticProps` → `FilterTripsPage` → `RouteFAQ`, used as the SSR-safe floor. Existing `tripsFilterSet` client fetch stays as progressive enhancement for genuinely date-specific answers (duration, first departure for the selected date) once hydrated — those two fields were deliberately excluded from the aggregate since no honest date-independent number exists for them.

A pre-merge 3-specialist debate (Next.js/Django/SEO agents, told to find holes not confirm) caught a real correctness bug before it shipped: the first draft's cancellation-summary logic picked "the first contract with structured policy data," unrelated to which contract produced the displayed cheapest price — could have shown one operator's cancellation terms while the price pointed at a different, cheaper operator. Fixed to source cancellation terms from the same contract as the cheapest price first, only falling back to another contract if the cheapest has none, and to be explicit (`is_cheapest_operator` flag) when it does fall back. Debate also caught: reuse the codebase's existing `cache.get`/`cache.set` idiom instead of proposing new infra; add `select_related`/`prefetch_related` to avoid N+1; drop a planned "how far in advance do I need to book?" question as booking-funnel content with no search intent; make the FAQPage JSON-LD dedup between `FilterTripsSEO` and `RouteFAQ` explicit instead of coincidental.

## Impact
- All `/trips/*/*` route pages (same shared component/template) — not isolated to Hatyai↔Koh Lipe. Pattern-level thin-content risk at scale: hundreds of route URLs serving near-identical generic FAQ prose to crawlers.
- `FAQPage` JSON-LD is technically emitted correctly (unlike the sibling `FilterTripsSEO.js` bug) but per [[faqpage-rich-results-deprecated-2023]] carries zero SERP rich-result benefit regardless — not the priority. The AEO/prose value of specific vs. generic text is the real stake (AI answer engines cite prose directly; generic text reads as templated/thin to both crawlers and quality raters).

## Related
[[filter-trips-seo-faq-prop-dropped]] — sibling bug, same page family, different component (`FilterTripsSEO.js`), render-drop not data-timing.
[[help-faqs-wp-graphql-broken-prod]] — same bug class (SSR-empty, client-only fill) on `/help/faqs`, first occurrence.
[[build-experience-faq-items-pure-function]] — same "derive FAQ from real structured data, never hardcode" principle, applied to experience-page FAQ.
[[faqpage-rich-results-deprecated-2023]] — why the JSON-LD correctness isn't the priority here.
