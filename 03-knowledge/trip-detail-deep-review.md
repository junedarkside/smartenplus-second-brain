---
name: trip-detail-deep-review
description: 4-agent adversarial deep review of trip detail page — overturned findings, hidden issues, production failure scenarios
metadata:
  type: project
---

# Trip Detail Deep Review — 2026-05-20

> ⚠️ **SUPERSEDED 2026-06-16** — Predates the server-side SEO refactor. `useTripSEO.js` was **deleted**, replaced by `helpers/seo/tripDetailSEOUtils.js` + rewritten `TripDetailSEO.js`. The SEO findings below citing `useTripSEO.js ~line N` (H2 ISO8601, H7 USD `/30`) were resolved in the refactor — see [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]] (7/7 HIGH fixed). Findings retained as historical record; candidate for [[08-archive]].

## Summary
4-specialist second-pass team (Adversarial · Blast-Radius · Hidden Issues · Production Risk) reviewed original 24-finding report. 3 overturned, 2 downgraded conditional. 8 new hidden issues. 4 production failure scenarios.

## Context
Follows [[trip-detail-page-review]]. Branch: `260520-update/recommend-route`.

## SECTION 0 — ORIGINAL REPORT CORRECTIONS

### ❌ OVERTURNED — P2: "Remove `isClient` entirely"
**`isClient` hydration safety guard — removing breaks app.**

`TripDetailHero.js:79–82` uses `isClient` to prevent hydration mismatch. Server renders neutral placeholder, client switches to Redux value post-hydration. Without: server `0 passengers`, client `2 passengers` → hydration mismatch every page load.

**Fix:** Keep `isClient`. Combine its useEffect with calendar useEffect (one mount effect, not two).

### ❌ OVERTURNED — S1: "Change 307 → 301 redirect"
Keep `permanent: false`. Products reclassifiable — 301 causes permanent browser/CDN cache pollution. See [[nextjs-307-vs-301-product-reclassify]].

### ⚠️ DOWNGRADED — C4: "'forword' typo, just fix it"
`'forword'` in `homepagev1.js`, `useTripDetailData.js`, main detail page. Zero `'forward'` occurrences in codebase. Backend may accept `'forword'`. Blind change silently breaks all direction filtering.

**Fix:** Check backend API `direction` enum first. If backend validates `'forword'`, fix both ends simultaneously.

### ⚠️ CONDITIONAL — P4: "Remove `ssr:false` from breadcrumb"
`NextBreadcrumbs.js:31–32` reads `router.asPath` during render. SSR: `router.asPath` undefined → empty breadcrumbs server-side → hydration mismatch. `ssr:false` likely intentional.

**Fix:** Remove `ssr:false` only after adding `router.isReady` guard in `NextBreadcrumbs`, or pass path as static prop (`customBreadcrumbPath` already computed in parent).

### ⚠️ CONDITIONAL — P1: "Remove reviews useEffect"
Line 221 comment: *"Addresses static generation build regression where reviews aren't included in productData."* ISR has known build regression where `productData.reviews` empty. Removing fetch leaves reviews permanently empty.

**Fix:** Verify `getStaticProps` reliably populates `productData.reviews` first. Then remove client fetch.

## SECTION 1 — NEW HIDDEN ISSUES

### 🔴 H1 — liveProductData merge wipes valid ISR ratecard with empty array (line 89–102)
`??` doesn't catch `[]` — empty CSR ratecard wipes valid ISR data → "Pricing Unavailable" crash. Active revenue risk. See [[nextjs-isr-ratecard-empty-array-guard]].

### 🔴 H2 — TouristTrip schema invalid ISO8601 time format (`useTripSEO.js` ~line 418)
```js
departureTime: `T${productData.trip_departure_time}+07:00`
// Output: "T08:00:00+07:00" ← INVALID
// Required: "2026-05-20T08:00:00+07:00"
```
Missing date prefix. Google Search Console rejects → TouristTrip rich results disabled silently.

**Fix:** Combine with `start_date` or omit `departureTime`/`arrivalTime` if no travel date.

### 🔴 H3 — No fetch timeout in `getStaticProps` — blocking fallback SSR can 500 forever (line 450)
`fetchData()` wraps axios with zero timeout. `fallback: 'blocking'` new slugs: first visitor blocks on API. API hangs → Vercel Lambda timeout (10–30s) → 500 → page never caches → every visitor gets same 500.

**Fix:** Add 8s timeout to `fetchData` for SSG context. Existing `notFound: true` catch handles gracefully.

### 🟡 H4 — Memory leak: async reviews fetch has no AbortController (line 222–241)
No cleanup. User navigates away during fetch → `setReviews()` fires on unmounted component → React warning + state corruption.

`productData?.reviews` in dependency array (line 241) causes re-fetch on ISR review changes — circular.

**Fix:**
```js
useEffect(() => {
  const controller = new AbortController();
  const fetchReviews = async () => {
    const response = await fetch(`...`, { signal: controller.signal });
    ...
  };
  if (isClient && productData?.slug) fetchReviews();
  return () => controller.abort();
}, [productData?.slug, isClient]); // removed productData?.reviews
```

### 🟡 H5 — Calendar date calculation has no try/catch — stale Redux persist can crash (line 71–74)
```js
const dateTrip = calendarStateDate
  ? format(getStringDate(calendarStateDate), 'dd-MMM-yyyy')
  : format(new Date(), 'dd-MMM-yyyy');
```
`calendarStateDate` is serialized Redux persist object `{ serifyKey, type, value }`. Stale/malformed state → `getStringDate()` throws → crashes before early-return guards. No try/catch.

**Fix:** Wrap in try/catch, fallback to `new Date()`.

### 🟡 H6 — `router.events` hash scroll fires on ALL route changes while mounted (line 261–269)
`handleRouteChange` on `routeChangeComplete` fires on every route change app-wide while mounted. User navigates away during 100ms `setTimeout` → `scrollIntoView` on stale ref. Cleanup at unmount correct, but 100ms gap = race window.

### 🟡 H7 — FAQ schema converts THB → USD with hardcoded `/ 30` (`useTripSEO.js` ~line 321)
Exchange rate hardcoded. Current ~33–36 THB/USD. Google indexes → incorrect USD pricing in rich snippets for international users.

**Fix:** Remove USD conversion from FAQ schema, or integrate real forex data (`/forex/` endpoint already in project).

### 🟡 H8 — `TRANSPORTATION_CATEGORIES` divergence is correctness trap, not maintenance debt
`getStaticPaths` and `getStaticProps` sharing different constant copies → silent routing failure (pre-built pages redirected at runtime, no build error).
→ See [[nextjs-static-path-prop-divergence]]

## SECTION 2 — PRODUCTION FAILURE SCENARIOS

### 🔴 PROD-1 — Silent stale pricing (P1)
**Trigger:** `useCheckContractQuery` fails (5xx, timeout, network).
**Result:** `freshContract` stays `undefined` → `liveProductData` falls back to ISR cache → user books with weeks-old rates. No error indicator.
**Gap:** Zero error UI for contract fetch failure. Add error toast when RTK Query enters error state.

### 🔴 PROD-2 — Price flash → "Pricing Unavailable" crash (P1)
**Trigger:** ISR cached page has rates → operator deactivates ratecard → CSR refresh returns empty ratecard.
**Result:** ISR price in hero → CSR returns `{ ratecard: [] }` → H1 triggers → `lowestRate` = null → page unmounts to error screen.
**User sees:** "450 THB" → blank error. Booking abandonment.
**Fix:** H1 fix (ratecard guard) eliminates this. Don't recompute display price from `liveProductData` — use ISR price for display, CSR for availability.

### 🟡 PROD-3 — New slug: first visitor gets 500 if API slow (P1)
**Trigger:** Unbuilt slug, `fallback: 'blocking'`, API > Vercel Lambda limit.
**Result:** 500 → page never caches → all visitors 500.
**Fix:** H3 fix (8s timeout on `fetchData`).

### 🟡 PROD-4 — ISR revalidation failure serves stale data indefinitely (P2)
**Trigger:** API down during ISR revalidation.
**Result:** Old HTML served silently, no metric, no user-visible error.
**Mitigation:** Monitor via Vercel analytics or Datadog on `getStaticProps` errors. No code fix — expected Next.js ISR behavior.

## REVISED QUICK-WIN ORDER

**Safe now (no investigation):**

| # | Fix | Effort |
|---|-----|--------|
| 1 | C1+C2 dead imports | 30s |
| 2 | C8 hoist `TRANSPORTATION_CATEGORIES` to module level | 2 min |
| 3 | C3 `.map()→.join(' + ')` + trim space in GTM | 1 line |
| 4 | C5 remove `useMemo` on `.length` | 1 line |
| 5 | P3 move `require()` to top-level import | 3 lines |
| 6 | P8 remove `console.log` from build path | 1 line |
| 7 | S2 remove emoji from title | 1 line |
| 8 | P5 remove `refetchOnFocus/Reconnect` | 2 lines |
| 9 | H4 AbortController + fix dep array on reviews fetch | 8 lines |
| 10 | S6 fix broken `aria-labelledby` IDs | 2 lines |

**Require investigation first:**

| # | Fix | Must verify |
|---|-----|-------------|
| 11 | C4 `'forword'→'forward'` | Backend direction enum |
| 12 | P4 breadcrumb `ssr:false` | Add `router.isReady` guard in NextBreadcrumbs first |
| 13 | P1 remove reviews useEffect | Verify ISR populates reviews reliably |
| 14 | H1 ratecard merge guard | Test with empty ratecard API response |
| 15 | H2 fix ISO8601 departure time | Confirm schema.org requirement |
| 16 | PROD-2 price flash fix | Architecture decision: ISR vs CSR pricing display |

## TOP 3 HIDDEN RISKS

1. **PROD-2 + H1** — Empty CSR ratecard overwrites valid ISR price → page crashes on booking. Active revenue risk.
2. **H3** — No fetch timeout → new slugs 500 indefinitely. Silent, no alert.
3. **H2** — Invalid ISO8601 in TouristTrip schema → all rich results rejected by Google Search Console. Silent.

## Related
[[trip-detail-page-review]] · [[nextjs-patterns]] · [[hydration-infinite-refresh-fix]] · [[blog-seo-performance]]