# Activities Page — DAY_TOUR Review 2026-06-01

## Summary
3-specialist code audit + grill + scrutinize of `/activities?category=DAY_TOUR`. 14 findings. 3 Critical, 6 Major, 5 Minor. No live browser testing — source-only. Scrutinize corrected 4 wrong claims (FQ-4 symptom, UX-2 TRANSFER, FQ-1 title, DS-1 fix path). FQ-2 severity elevated. **Branch:** `260601-fix/activities-browse-audit` — ready for implementation.

---

## Context

Page route: `pages/activities/index.js` → `FilterDayTripsPage.js`  
Branch reviewed: `main` (commit `efb59d7`)  
Category filter chain confirmed working per [[adr-experiences-nav-category-filtering]].  
DAY_TOUR default in `useDayTripFilters.js:18`.

---

## Grill — Active Contract Filter + Design System (2026-06-01)

### FQ-0 [P0] — Browse returns inactive contracts

**Root cause chain:**
- `ContractViewSet` base queryset (`operators/views.py:95`): `Contract.objects.all()` — no `is_actived` filter by default
- `is_actived` filter only when caller passes `?status=active` (`views.py:227`)
- `dayTripsApi.js:getContracts` never sends `?status=active`
- Result: `is_actived=False` contracts appear in `/activities?category=DAY_TOUR`

**Grill clarifications:**
- `confirm` — secondary. Blocks availability check (`views.py:1180`), not listing. Not browse filter.
- `stop_sale_dates` — date-level availability block only. Correct scope: availability-time, not listing. Stop sell NOT issue.
- `is_actived=True` necessary and sufficient for browse listing.

**Fix:** `store/api/dayTripsApi.js:54` — add `params.append('status', 'active')`. 1 line. No backend change.

```js
const params = new URLSearchParams();
params.append('status', 'active');  // ADD — filters is_actived=True on backend
if (serviceCategory) params.append('service_category', serviceCategory);
```

**Constraints:** no new wrapper, no new hook, no config flag. Single param append sufficient.

---

### DS-1 [P1] — Design system tokens inconsistently applied

Key gotcha: `TYPOGRAPHY_SCALE.caption` = `'text-xs'` (Tailwind string) — `.fontSize` is `undefined`. Never use in MUI `sx`. See [[design-token-caption-tailwind-gotcha]].

Scoped fix: `CategoryFilter.js:55,80` + `FilterDayTripsPage.js:142` → `TOUCH_TARGET.minHeight`. `DayTripCard.js` ×5 caption — use raw `'0.8125rem'` or add `MUI_FONT_SIZES.caption` to designSystem.js.

---

## Specialist 1 — UX / Conversion

**Focus:** Filter flow, empty/loading states, CTA clarity, search redundancy.

### Findings

**UX-1 [P0] — Two search inputs, no clear distinction**
- `FilterDayTripsPage.js:54–68` — `DayTripLocationSearch` (location autocomplete)
- `FilterDayTripsPage.js:70–88` — `TextField` (keyword search)
- Both visible simultaneously above category chips. No label hierarchy. Users confused. Standard OTA pattern: location first, keyword secondary (collapsed or below fold).
- **Fix:** Label location field "Where?" (h3 or bold label). Move keyword search below category chips or collapse behind "Search by name" link.

**UX-2 [P1] — Category chips include non-experience categories**
- `CategoryFilter.js:42` iterates ALL `SERVICE_CATEGORIES` — frontend has 9 keys: `DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION, TRANSPORTATION, OTHER`
- ~~TRANSFER~~ — REFUTED by scrutinize. `dayTripConstants.js` has no `TRANSFER` key. Exclude: `ACCOMMODATION`, `TRANSPORTATION`, `OTHER`.
- Vault canonical experience subset: `DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING` per [[homepage-experiences-section-audit]]
- **Fix:** Add `EXPERIENCE_CATEGORIES` array to `dayTripConstants.js` with 6 valid values. Replace `Object.keys(SERVICE_CATEGORIES)` in `CategoryFilter.js:42`.

**UX-3 [P1] — Empty state gives no actionable path**
- `DayTripList.js:82–91` — "No tours found. Try adjusting your filters or search for a different location."
- No "Clear filters" button. No suggested categories. User stuck.
- **Fix:** Add `clearFilters()` button (exists in `useDayTripFilters.js:54`). Wire to empty state CTA.

**UX-4 [P2] — Pagination hidden when totalPages === 1**
- `FilterDayTripsPage.js` — `totalPages` calculated but pagination renders even at 0. No guard on `totalPages > 1`.
- **Fix:** `{totalPages > 1 && <Pagination ... />}` — standard guard.

**UX-5 [P2] — "All" chip clears category entirely, defaults to DAY_TOUR on next load**
- `CategoryFilter.js:45` — `onChange(null)` sets selected to null
- `useDayTripFilters.js:18` — `category: router.query.category || SERVICE_CATEGORIES.DAY_TOUR`
- "All" → null category → API fires without `service_category` → backend returns all → but refresh has no `?category=` so hook re-defaults to DAY_TOUR. State and URL disagree.
- **Fix:** When "All" selected, set `category = 'ALL'` sentinel, send no `service_category` to API, keep `?category=ALL` in URL so state restores correctly.

---

## Specialist 2 — Visual Design + Design System

**Focus:** Design token usage, card layout, typography scale, spacing consistency.

### Findings

**VD-1 [P1] — Card image height hardcoded, not from token**
- `DayTripCard.js:94` — `sx={{ height: 180 }}`
- `helpers/designSystem.js` has no image height token. 180 is bare magic number.
- Other card patterns use `h-[200px]` (PopularRouteImageCard). Inconsistent across browse views.
- **Fix:** Add `IMAGE_HEIGHT: { card: 180, heroCard: 200 }` to designSystem.js. Reference as `COMPONENT_CONFIGS.card.imageHeight`. Or adopt 200px to match existing card standard.

**VD-2 [P1] — Card padding uses raw px values, not SPACING tokens**
- `DayTripCard.js:116` — `sx={{ px: 3, pt: 3, pb: 3 }}`
- MUI spacing unit 3 = 24px. `SPACING.md: '1.5rem'` (24px) — match coincidental, not semantic.
- **Fix:** Add comment or map to `SPACING.md` explicitly. Low priority but creates drift risk when spacing tokens change.

**VD-3 [P1] — Title line-clamp 1 on mobile**
- `DayTripCard.js:112` — `WebkitLineClamp: { xs: 1, sm: 2 }`
- Mobile clamps tour name to 1 line. Most names 40–70 chars. Single line truncates almost every title, destroying discoverability.
- **Fix:** `xs: 2, sm: 2` minimum. At 180px image + 2-line title + feature bullets + rating/price, card fits within 380px.

**VD-4 [P2] — CategoryFilter chip min-height 44px correct, but scrollbar hidden on desktop**
- `CategoryFilter.js:59–62` — `display: 'none'` on scrollbar, revealed only on hover
- Chips wrap on desktop (`md: 'wrap'`) so no scrollbar needed — correct. Mobile hides scrollbar entirely with no scroll affordance.
- **Fix:** Add fade gradient on right edge on mobile to signal more chips. CSS-only, no JS needed.

---

## Specialist 3 — Frontend Code Quality

**Focus:** React patterns, a11y, SEO, useEffect chains, skeleton mismatch.

### Findings

**FQ-1 [P0] — Skeleton anatomy shows non-existent fields (Operator, Duration, Key Features)**
- Grid column count matches — `xs=12 sm=6 md=4 lg=3 xl=3` identical in skeleton (`DayTripList.js:65`) and actual cards (`DayTripList.js:105`). ~~"4-column layout" mismatch~~ — REFUTED by scrutinize, title was wrong.
- Actual issue: skeleton card internals (`DayTripList.js:35–61`) show "Operator", "Duration", "Key Features" rows — none rendered in actual `DayTripCard`. Perception mismatch on load.
- **Fix:** Rewrite `SkeletonCard` to match actual anatomy: image rect (180px) → 2 title lines → bullet row → rating + price row. Remove operator/duration/key-features rows.

**FQ-2 [P1] — useDayTripFilters initializes from router.query before hydration; useEffect fires spurious push**
- `useDayTripFilters.js:16–21` — `useState` reads `router.query` on mount. In Next.js, `router.query` is `{}` during SSR and first CSR paint — params not available until after hydration. All filters initialize to defaults (DAY_TOUR, null, etc.) even when URL has `?category=SPA_WELLNESS`.
- `useDayTripFilters.js:25–43` — `useEffect` immediately fires `router.push` with default values → overwrites URL with defaults → URL loses actual query params on every load.
- ⚠️ **Severity elevated by scrutinize:** mounted-ref fix alone insufficient. Root: `useState` initializer runs pre-hydration. Real fix: move URL reading into `useEffect` post-hydration. Or use `useRouter` `isReady` guard before initializing state.
- CLAUDE.md rule: "useEffect chains forbidden — B depending on A → useMemo or single combined effect"
- **Fix:** Gate on `router.isReady`: `const [filters, setFilters] = useState(DEFAULT_FILTERS)` + `useEffect(() => { if (!router.isReady) return; setFilters(fromQuery(router.query)); }, [router.isReady])`. Separate push effect also check `router.isReady` before pushing.

**FQ-3 [P1] — SEO meta missing structured data (ItemList schema)**
- `pages/activities/index.js` — has `<title>`, `description`, `og:title`, `og:description`. No structured data.
- OTA category pages benefit from `ItemList` schema listing top 3–5 results. Pattern from [[trip-detail-page-review]] and [[homepage-seo-performance-deep-review-2026-05-21]].
- `og:url` hardcodes `https://smartenplus.co.th` — `NEXT_PUBLIC_SITE_URL` should be used (ISR pattern from [[og-image-ssr-fix-2026-05-23]]).
- **Fix (P1):** Replace hardcoded domain with `process.env.NEXT_PUBLIC_SITE_URL`. Add `ItemList` JSON-LD with top N contracts once SSR/ISR available.

**FQ-4 [P2] — DayTripCard: try/catch fallback to 0 shows "Price on Request" for parseable contracts**
- `DayTripCard.js:53–62` — `catch (error) { console.error(...); startingPrice = 0; }`
- ~~"From THB 0"~~ — REFUTED by scrutinize. `PricingDisplay.js:34`: `if (!price || price <= 0)` → renders **"Price on Request"**, not "From THB 0". Guard exists.
- Actual concern: valid ratecards but price parse fails → silently shows "Price on Request" instead of real price. Wrong signal, not broken UI.
- **Fix:** log warning, not error. `startingPrice = null` cosmetically identical to 0 in PricingDisplay. Real fix: validate ratecard shape earlier. Lower priority — existing UX acceptable.

**FQ-5 [P2] — Card aria-label uses `translated_name || name` but falls back to generic**
- `DayTripCard.js:89` — `aria-label={`View details for ${workingContract.translated_name || workingContract.name}`}`
- `workingContract.name` defaults to `'Tour Name Unavailable'` at line 36. Screen reader announces "View details for Tour Name Unavailable" for any contract missing both name fields.
- **Fix:** If name === 'Tour Name Unavailable', omit aria-label and rely on inner heading (`role="heading"` on `<Typography component="h3">`).

---

## Debate & Resolution

### Conflict 1 — UX-5 vs FQ-2 on URL state
UX-5: "All" chip sets `null`, causes URL/state mismatch. FQ-2: useEffect fires spurious pushes. These compound: null category → no `?category=` → push hook re-initializes to DAY_TOUR → "All" state lost immediately.
**Resolved:** Both valid. Fix FQ-2 first (prevent spurious push), then UX-5 (sentinel value). FQ-2 root, UX-5 symptom.

### Conflict 2 — VD-1 (image height) vs FQ-1 (skeleton mismatch)
VD-1 wants to formalize 180px as token or change to 200px. FQ-1 wants skeleton to match card. Must coordinate — whichever height wins, skeleton and card use same value.
**Resolved:** Fix FQ-1 first (align skeleton to 180px current). Add token VD-1 after. No height change — 200px extends card beyond current grid without layout validation.

### Conflict 3 — UX-2 (remove non-experience categories) risk
Removing `ACCOMMODATION`, `TRANSPORTATION`, `TRANSFER` means existing URLs with those category params stop showing matching chip. Backend still returns results.
**Resolved:** Safe — CategoryFilter drives UI selection only, not API. URL params still pass through correctly. On-page chip won't highlight for non-experience categories. Acceptable regression.

---

## Decision — Final Ranked Findings

### P0 — Critical (fix before ship)

| ID | File | Issue | Fix |
|----|------|-------|-----|
| FQ-0 | `dayTripsApi.js:54` | Browse returns inactive contracts — `?status=active` never sent | `params.append('status', 'active')` — 1 line |
| UX-1 | `FilterDayTripsPage.js:54–88` | Two unlabeled search inputs create UX confusion | Label "Where?" on location, move keyword below category chips |
| FQ-1 | `DayTripList.js:35–61` | Skeleton anatomy doesn't match DayTripCard — shows fields that don't exist | Rewrite SkeletonCard: image 180px → 2 title lines → bullets → rating+price |

### P1 — Major (next sprint)

| ID | File | Issue | Fix |
|----|------|-------|-----|
| UX-2 | `CategoryFilter.js:42` | All 9 categories shown including non-experiences | Filter to 6 experience categories; add `EXPERIENCE_CATEGORIES` to `dayTripConstants.js` |
| UX-3 | `DayTripList.js:82–91` | Empty state has no actionable CTA | Wire `clearFilters()` button to empty state |
| VD-3 | `DayTripCard.js:112` | Title line-clamp 1 on mobile destroys discoverability | Change `xs: 1` → `xs: 2` |
| FQ-2 | `useDayTripFilters.js:25–43` | useEffect fires spurious `router.push` on mount | Gate with query diff check or `mounted` ref |
| FQ-3 | `pages/activities/index.js` | `og:url` hardcodes domain; no structured data | Use `NEXT_PUBLIC_SITE_URL`; add `ItemList` JSON-LD |
| DS-1 | `CategoryFilter.js:55,80` + `DayTripCard.js` | Design tokens imported but not applied (minHeight, fontSize) | 2 targeted substitutions — `TOUCH_TARGET.minHeight` + `TYPOGRAPHY_SCALE.caption.fontSize` |

### P2 — Minor (backlog)

| ID | File | Issue | Fix |
|----|------|-------|-----|
| UX-4 | `FilterDayTripsPage.js` | Pagination renders on single-page results | Guard `{totalPages > 1 && <Pagination />}` |
| UX-5 | `CategoryFilter.js:45` + `useDayTripFilters.js:18` | "All" chip state lost on URL restore | Sentinel `category=ALL` value; don't default back to DAY_TOUR |
| VD-1 | `DayTripCard.js:94` | Image height `180` is magic number | Add `IMAGE_HEIGHT.card = 180` to designSystem.js |
| VD-2 | `DayTripCard.js:116` | Card padding uses raw MUI units, not SPACING tokens | Document mapping or refactor to SPACING tokens |
| VD-4 | `CategoryFilter.js:59–62` | No scroll affordance on mobile chip row | Add right-edge fade gradient via CSS |
| FQ-4 | `DayTripCard.js:53–62` | Price fallback to 0 shows "From THB 0" | Fallback to null; hide price in PricingDisplay |
| FQ-5 | `DayTripCard.js:89` | Broken aria-label when name unavailable | Guard or rely on inner h3 heading |

---

## Fix Sequence

```
0. FQ-0  — Add ?status=active (dayTripsApi.js:54) — 1 line, no backend change
1. FQ-1  — Fix skeleton anatomy (DayTripList.js:35–61)
2. UX-1  — Label search inputs, reorder (FilterDayTripsPage.js:54–88)
3. FQ-2  — Guard useDayTripFilters push (useDayTripFilters.js:25–43)
4. UX-2  — Add EXPERIENCE_CATEGORIES, filter chip list (dayTripConstants.js + CategoryFilter.js)
5. UX-3  — Wire clearFilters to empty state (DayTripList.js:82–91)
6. VD-3  — line-clamp xs:2 (DayTripCard.js:112)
7. FQ-3  — og:url + ItemList schema (pages/activities/index.js)
7b. DS-1 — CategoryFilter minHeight + DayTripCard caption fontSize (2 token substitutions)
--- P2 backlog ---
8. UX-4  — Pagination guard
9. UX-5  — "All" sentinel value
10. VD-1/VD-2 — Design token cleanup
11. VD-4  — Mobile chip fade gradient
12. FQ-4/FQ-5 — Price null + aria-label guard
```

---

## Tradeoffs

| Decision | Chosen | Skipped |
|----------|--------|---------|
| Remove non-experience categories | Yes — clean intent | Keeping all — avoids regression for existing `?category=ACCOMMODATION` deep links |
| image height token | Add to designSystem | No migration — skeleton and card already both use 180px |
| ItemList structured data | Flag as P1 — needs ISR | Skip — page currently CSR-only, JSON-LD in Head safe anyway |
| Defer full COMPONENT_CONFIGS adoption | Yes — scoped DS-1 fix only | Full token refactor — high churn, low ROI this sprint |
| `confirm` as browse filter | No — availability-time only | Filtering on `confirm` at browse level premature; no user-visible impact |

---

## Related

- [[adr-experiences-nav-category-filtering]] — URL→API chain, category enum, nav decisions
- [[homepage-experiences-section-audit]] — canonical experience category list, grill decisions
- [[trip-detail-page-review]] — 3-agent review template this follows
- [[design-system-audit-2026-05-31]] — token expansion context

## Related Atoms (Extracted 2026-06-13)
- [[contract-fk-icontains-or-fallback]] — M2M+FK icontains search with `.distinct()`; cache-clear on deploy
## Atomized Notes (Extracted 2026-06-22)

- [[activities-day-tour-stored-xss-page-crash]] — stored XSS + crash: `dangerouslySetInnerHTML` no DOMPurify + `parseISO(null)`.
- [[activities-day-tour-star-rating-aria-broken]] — star rating ARIA broken: multiple `aria-pressed=true`.
- [[activities-day-tour-wrong-router-import]] — wrong router import breaks "Write Review" CTA. `next/router` → `next/navigation`.
