# Daytrips → Activities Rename

## Summary
Rename `/daytrips` section to `/activities` across the entire frontend codebase.

## Context
`/daytrips` covers 6 product categories: DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, ATTRACTION_TICKET, FOOD_DINING, EVENT_TICKET. The name "day trips" misrepresents spa, dining, and event products — hurts SEO relevance and user mental model. 3-specialist team review (SEO + UX + Code) unanimous: rename to `activities`.

## Decision
**`activities` wins** — matches tourist search intent ("activities in Thailand/Phuket"), creates clean cognitive split from `/trips` (transportation = how you get there vs activities = what you do when you arrive), industry standard (Viator, GetYourGuide). 301 redirects preserve SEO equity.

Rejected: `experiences` (vague for non-native English), `tours` (collides with `/trips`), `explore` (verb — bad Redux slice name).

## Scope

**51 files affected total.**

| Category | Count |
|----------|-------|
| Pages | 3 |
| Components (`/components/daytrips/`) | 18 |
| Components outside daytrips dir | 3 |
| Hooks | 4 |
| Store (Redux + RTK Query) | 3 |
| Constants | 2 |
| Helpers/utils | 3 |
| Tests | 6 |
| Debug files | 5 |

## Critical Risks

### 1. Redux Persist Migration (BLOCKER)
- Persist version: **6**, key: `root-sep-6`, whitelist includes `'dayTrip'`
- Rename slice key without migration = all active user sessions lose `selectedDate`, `selectedAddons`, `selectedTimeSlot`, `recentSearches`, `selectedLanguage` on deploy
- **Fix:** increment version 6→7, add migration `state.dayTrip → state.activities`, update whitelist in `/store/index.js`
- Must test on staging with existing session before deploy

### 2. ISR Cache Window
- Detail pages: ISR revalidate = **3600s (1 hour)**
- Must clear `smartenplus_next_cache` Docker volume on deploy
- Add 301 redirects in `next.config.js` BEFORE renaming pages folder to avoid 404 window

### 3. Dual SEO URL Generation
- Breadcrumb URLs hardcoded in TWO places: `helpers/seo/dayTripSEOUtils.js` (lines 288, 297) AND `hooks/useDayTripSEO.js` (lines 111, 120)
- Both must be updated — missing one = mismatched JSON-LD breadcrumbs

### 4. `getTripDetailPath()` — App-Wide Routing Helper
- `/helpers/serviceCategoryHelper.js:385` returns `/daytrips/detail/{slug}` for non-transport
- Used in 5 places outside daytrips: EnhancedTripCard, ServiceCategoryDetail, RecommendationCard, ReviewFirstPage, ReviewsSection
- Single fix propagates everywhere — do NOT update individual call sites

### 5. Trips Detail 308 Redirect Chain
- `/pages/trips/detail/[...slug].js:456` permanent 308 redirect → `/daytrips/detail/{slug}`
- If not updated: `/trips/detail/{activity-slug}` → `/daytrips/` → 404 chain broken

## Cart / Checkout / Payment — SAFE

All payment flows unaffected:
- Booking widget → cart payload has no URL, redirects to generic `/checkout`
- Payment success → `/orders/{id}` or `/guest-order/{id}` (no daytrips URL)
- `EnhancedTripCard` in checkout uses `getTripDetailPath()` — auto-fixed by helper update
- `TotalCartSummary` checks `service_category` enum values (backend constants, not URL segments)

## Implementation Phases

| Phase | Action | Blocking? |
|-------|--------|-----------|
| 0 | Redux persist migration (v6→v7, migrate `dayTrip→activities`) | YES — do first |
| 1 | Add 301 redirects to `next.config.js` | YES — before page rename |
| 2 | Rename constants + helpers (central, unblocks all dependents) | — |
| 3 | Rename hooks | — |
| 4 | Rename + update pages | — |
| 5 | Rename components dir + all 18 DayTrip* files + update imports | — |
| 6 | Update tests + debug files | — |
| 7 | Add "Activities" to main nav in `main-header.js` | — |

## Hardcoded URLs To Fix

| File | Line | String |
|------|------|--------|
| `helpers/seo/dayTripSEOUtils.js` | 288, 297 | `/daytrips`, `/daytrips?category=` |
| `hooks/useDayTripSEO.js` | 111, 120 | `/daytrips`, `/daytrips?category=` |
| `pages/server-sitemap.xml/index.js` | 245, 297 | `/daytrips`, `/daytrips/detail/` |
| `pages/daytrips/detail/[...slug].js` | 129 | `/daytrips/detail/` (canonical URL) |
| `pages/daytrips/detail/[slug].js` | 89 | `/daytrips/detail/` (canonical URL) |
| `pages/daytrips/index.js` | 36 | `https://smartenplus.co.th/daytrips` (og:url) |
| `pages/trips/detail/[...slug].js` | 456 | `/daytrips/detail/` (308 redirect destination) |
| `helpers/serviceCategoryHelper.js` | 385 | `/daytrips/detail/` |
| `components/daytrips/browse/DayTripCard.js` | 78 | `/daytrips/detail/` |
| `components/daytrips/detail/DayTripDetailHeader.js` | 101 | `/daytrips?category=` |

## What Is NOT Changing

- Backend API endpoints (`/product-detail/`, `/contract/`, `/product-slug/`) — already generic
- Django model names, DB tables
- RTK Query cache keys (tag values `DayTrip:${slug}` are internal, not URL-based)
- `robots.txt` — no daytrips reference
- `middleware.js` — empty matcher
- No hreflang, no GTM hardcoded paths, no `<Link prefetch>` to daytrips

## SEO Post-Launch
- Submit updated sitemap to Google Search Console
- Monitor GSC Coverage for 301→200 transition over 7–14 days
- Update CMS blog post internal links from `/daytrips` → `/activities`
- After 90 days: confirm `/daytrips` dropped from GSC Index

## Status — COMPLETED 2026-05-23

- [x] Phase 0 — Redux persist v6→v7 migration (dayTrip → activities key; v4/v5 branches patched)
- [x] Phase 1 — next.config.js 301 redirects (/daytrips, /daytrips/detail/:slug*, /daytrips/:path*)
- [x] Phase 2 — Constants + helpers (serviceCategoryHelper.js:385, dayTripSEOUtils.js:288,297)
- [x] Phase 3 — Hooks (useDayTripSEO.js:111,120)
- [x] Phase 4 — Pages (renamed pages/daytrips/ → pages/activities/, URL strings updated)
- [x] Phase 5 — Components (renamed components/daytrips/ → components/activities/, URL strings updated)
- [x] Phase 6 — Tests + debug (store key, component imports, persist key, route pathnames)
- [x] Phase 7 — Nav (desktop navLinks + mobile menuLinks in layout.js)
- [ ] Deploy + ISR cache clear (smartenplus_next_cache Docker volume)
- [ ] GSC sitemap submission (resubmit https://www.smartenplus.co.th/sitemap.xml after deploy)

## Scrutiny Fixes Applied (2026-05-23)
- **BLOCKER fixed:** v4/v5 migration branches now also rename dayTrip → activities (custom migrate fn doesn't chain)
- **MAJOR fixed:** Deleted duplicate pages/activities/detail/[slug].js — [slug].js shadowed [...slug].js, bypassing ISR pre-warming
- **MAJOR fixed:** Used git add + git rm --cached to record as renames (R) not delete+add (D) — history preserved
- **MEDIUM fixed:** SEO title "Day Trips in X" → "Activities in X" at /activities
- **MEDIUM fixed:** Integration test pathname '/daytrips/detail/[slug]' → '/activities/detail/[...slug]'

## Commits
- `dab579e` feat: rename /daytrips → /activities across frontend
- `0a8081d` fix(activities): update SEO page title and description to Activities branding
- Merged → develop `d424d4e`

## Sitemap Notes
- `public/sitemap-0.xml` regenerates on `npm run build` — will emit /activities post-deploy
- `pages/server-sitemap.xml/index.js` already updated — emits /activities at runtime
- No changes needed to next-sitemap.config.js or robots.txt

## Branch
`260523-feat/rename-daytrips-to-activities` (merged → develop)

## Related
[[master-state]] [[architecture]] [[nextjs-patterns]] [[seo-homepage-specialist-team]]
