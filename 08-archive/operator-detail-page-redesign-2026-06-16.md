# Operator Detail Page Redesign — `/operators/[slug]`

> **SHIPPED TO PROD 2026-06-16 (#124).** Implemented + merged → FE develop `6fff946` (this work `8853cb2`), deployed live.

## Summary
3-agent debate (UX → Design → Frontend) redesign spec for `pages/operators/[slug].js` (e.g. `/operators/silaphat`). Converged: hero-weighted header with operator-specific stat trio, type-filter pills promoted to MUI tabs, `KeyHighlights` (dead/generic) removed, filter bar extracted into its own component. No code shipped yet — spec only.

## Context
Page already went through a token-consistency fix this session (typography/colors/border-radius/width via `helpers/designSystem.js`, branch `fix/operators-design-tokens`). This redesign is a separate, bigger pass on structure/UX, not a continuation of the token fix.

Current page (before this spec): flat single column — gradient header (small 64-80px logo, name, tiny conditional rating) → breadcrumb → filter bar (search + sort + flat type pills) → vertical contract-card list → pagination. `KeyHighlights` (site-wide 4-stat trust bar) and `FeaturedImageHeader` are both imported but **never rendered** — dead imports, confirmed by grep.

Untapped data: `pagination.count` (total routes, scoped to current filter) and `summaryData.average_rating`/`review_count` exist but are barely surfaced.

## Debate trail

**UX (round 1):** User's job-to-be-done is trust-check operator, then route-pick — both underserved today. Proposed: hero-weighted header with stat trio (rating + review count + "X routes available"), promote flat type-filter pills to primary tabs w/ counts, demote breadcrumb, get the contract list higher in viewport, **remove `KeyHighlights`** (generic site-wide stats dilute/create attribution ambiguity on an operator-specific page — is "4.8" the operator's or the site's?). Mobile: tabs scroll horizontally (primary axis stays visible), search/sort can collapse.

**Design (round 2, reacting to UX):** Rejected `FeaturedImageHeader` for the hero — that component is built for wide high-res photography with dominant-color extraction; a small square operator logo would float awkwardly in it. Instead: keep the current contained gradient header, just upscale the logo (`w-16/20` → `w-20/28`). Stat trio as inline text row (icon + bold value + gray label, `•` separators) — not cards, not badges, reuses `TYPOGRAPHY_SCALE`. Tabs: MUI underline style, not pill buttons (pills = filter affordance, underline = "this changes the whole view"). Agreed with cutting `KeyHighlights` — bonus catch: its icon colors (`text-blue-500` etc.) aren't even in the `COLORS` token set, already stylistically disconnected from the token-compliant rest of the page.

**Frontend (round 3, feasibility):** Verified MUI `Tabs`/`Tab` already used elsewhere (`components/airport-transfer/TripListingSection.js` has a directly reusable `TabPanel`/`a11yProps` pattern). Confirmed `pagination.count` is a true cross-page total — but scoped to the **current filter** (search/type), not an unfiltered operator-wide number, so it'll fluctuate live as the user filters; documented as intended, not a bug. Confirmed contract `type` values (`PRIVATE`/`JOIN`/`CHARTER`) exactly match backend `CONTRACT_TYPE` and the existing `COLORS.badge.tourTypeSoft` keys — no invented categories. **Found a real blocker**: per-type tab counts ("Join Tours (12)") aren't cheaply available — the customer-facing endpoint returns one count for the active filter only, no per-type breakdown; that aggregation exists only in a separate admin-only endpoint. Confirmed `KeyHighlights` removal is a true one-line import deletion (zero JSX, zero prop cleanup — it was never rendered). Flagged page is already 450 lines (over the repo's 200-line/component guideline) — adding tabs without extraction would make it worse.

## Decision (converged spec)

### Section structure (top to bottom)
1. **Header** (existing gradient block, unchanged structurally) — logo `w-16 h-16 md:w-20 md:h-20` → `w-20 h-20 md:w-28 md:h-28`, keep existing `rounded-2xl`/`rounded-xl` wrapper sizing as-is, header `py-8 md:py-12` → `py-10 md:py-14`.
2. **Stat trio** — inline row under H1: `★ 4.8 · 128 reviews · 12 routes available`, `TYPOGRAPHY_SCALE.body`/`small`, `text-gray-500` labels, `•` dividers, existing `StarIcon` import. Sourced from `summaryData.average_rating`, `summaryData.review_count`, `pagination.count` — all already wired into the page. **Note: scoped to current filter, updates live** — not a static operator-wide number.
3. **Breadcrumb** — demoted to thin utility line (`text-xs text-gray-500 mb-2`), same `DynamicStandardBreadcrumb` component, no logic change.
4. **Type tabs** — full-width borderless row, own `mb-3`, MUI `Tabs`/`Tab` (pattern: `components/airport-transfer/TripListingSection.js`). Labels: All / Private / Join / Charter — 1:1 with backend `CONTRACT_TYPE`, same `handleFilterChange({ type })` handler as today's pills. **No counts in labels at launch** (see Data Requirements — blocked on backend). Active: `COLORS.brand.secondary` underline+text; inactive: `text-gray-600`. Mobile: `variant="scrollable" scrollButtons="auto"` (native MUI, no custom code).
   - **Grilled 2026-06-16 — real gap found and fixed**: confirmed operators CAN have mixed `service_category` contracts (transport + day tours + spa etc — `ServiceCategoryBadge` already renders per-card alongside `type`, lines 281-294), but `type` (PRIVATE/JOIN/CHARTER) is transport-specific; non-transport contracts likely carry a null/meaningless `type`. Converting `type` to PRIMARY tab nav risked silently hiding non-transport contracts whenever a specific type tab (not "All") is selected. **Fix**: "All" must be a true unfiltered catch-all (no `type` param sent to backend at all, not "type=ALL"), guaranteeing every contract — transport or not — is visible by default. Specific type tabs (Private/Join/Charter) will only ever show transport contracts, by design; document this as expected, not a bug. Backend confirmed: `OperatorContractsViewSet.get_queryset()` (`smartenplus-backend/operators/views.py:2930-2932`) already only filters by `type` when the query param is present — so this requires no backend change, just ensuring the frontend's "All" tab omits the param entirely (matches current pill behavior already, per `handleFilterChange({ type: filterType === 'ALL' ? '' : filterType })` in the existing code).
5. **Search + sort row** — separate white card below tabs, same 2 controls (search input + sort `<select>`), same markup/behavior, just no longer sharing a grid with the type pills.
6. **Contract list** — unchanged card logic (`getTypeColor`, `ServiceCategoryBadge`, `getTripDetailPath`). One tweak: "Valid until" row `text-gray-500` → `text-gray-400`, drop the `border-t border-gray-100` divider above it (rely on existing `gap-3` flex spacing instead) — quiets a row that doesn't need equal visual weight to the route/badge row above it.
7. **Pagination** — unchanged.
8. **`KeyHighlights`** — removed (delete the import; confirmed dead, never rendered, zero side effects).
9. **"About operator"** — not built. Reserve a placeholder comment under the header; render only if/when backend adds an operator description field. No frontend skeleton until then.

### Components/tokens to reuse
- `Tabs`, `Tab` from `@mui/material` — already a dependency, pattern precedent in `components/airport-transfer/TripListingSection.js`
- `COLORS.brand.secondary`, `COLORS.badge.tourTypeSoft`, `BORDER_RADIUS_CLASSES`, `TYPOGRAPHY_SCALE`, `FONT_WEIGHTS`, `LAYOUT.pageContentClasses` — all `helpers/designSystem.js`
- `StarIcon` (`@mui/icons-material/Star`, already imported), `ServiceCategoryBadge` (`components/UI/ServiceCategoryBadge.js`), `DynamicStandardBreadcrumb` (`components/UI/StandardBreadcrumb.js`) — unchanged usage

### Net-new
- `components/operators/OperatorFilterBar.js` (~80-100 lines) — tabs + search + sort extracted out of the page file. **Grilled 2026-06-16**: original rationale ("page is 450 lines, over the 200-line guideline") doesn't hold — checked sibling pages, `destinations/[slug].js` is 584 lines and `blog/[slug].js` is 364 lines, neither extracted, no codebase precedent for splitting page files on line count alone. Real justification: tabs+search+sort is a self-contained, testable, reusable unit (clean prop-down/event-up: `type`/`search`/`sort` in, `onFilterChange`/`onSearchSubmit` out) — extract for that reason, not file length.
- No new stat-trio component — three `<span>`s with `•` separators fit inline in the page without complexity concerns. **Grilled 2026-06-16**: confirmed via codebase search this pattern has zero precedent anywhere else (not on `destinations/[slug].js`, `blog/[slug].js`, or any other detail page) — it's a new pattern, not an existing-convention reuse. Flagged as worth documenting in `docs/design/` once built, so other detail pages can adopt it later for consistency rather than it staying an operators-only one-off.

### Data requirements
- Stat trio (no counts caveat aside), tabs (no per-type counts), search, sort, contract list, pagination: **100% frontend-only**, all fields already returned by the existing contracts endpoint.
- **Blocked on backend**: per-type tab counts — needs a `by_type` aggregation added to `OperatorContractsViewSet.list`'s summary (same pattern as the admin-only `ContractViewSet.list` in `smartenplus-backend/operators/views.py`, computed pre-type-filter so counts don't collapse when a tab is active).
- **Blocked on backend**: "About operator" section — no description/bio field currently flows through `operatorData`.

## Consequences
Unlocks: clearer operator credibility signal above the fold, faster path to the route list, primary navigation (type) visually distinct from secondary refinement (search/sort), removes a stylistically disconnected dead component, "All" tab guaranteed to surface every contract regardless of service category (post-grill fix). Doesn't solve: tab counts (ships without them, real number deferred to backend follow-up — and that follow-up must count transport-type contracts only, not all categories), "About operator" enrichment (no data source yet). Specific type tabs (Private/Join/Charter) will only ever surface transport contracts by design — operators with non-transport offerings (spa, day tours, etc.) will only see those under "All," never under a type tab; this is intentional, documented behavior, not a future bug to fix.

## Grill audit notes (2026-06-16)
Audited against live code (verified, see inline **Grilled** notes above) and `helpers/designSystem.js`. Could NOT cross-check against `docs/design/DESIGN_SYSTEM.md`/`DESIGN_SYSTEM_QUICK_START.md` — both permission-blocked (settings.json deny rule on `docs/`, confirmed via two separate read attempts). User confirmed proceeding without this check rather than pasting contents manually. If those docs later turn out to contradict this spec's tabs/hero/stat-trio choices, re-grill against them then.

## Open questions
1. **RESOLVED 2026-06-16**: ship tabs without counts now (frontend-only, faster); file backend `by_type` aggregation as separate follow-up. Note from grill: that future backend work is slightly more nuanced than originally scoped — the aggregation should count transport-type contracts only (consistent with the category-gap fix above), not all contracts regardless of category, or counts will overstate what each type tab actually shows.
2. **RESOLVED 2026-06-16**: keep "X routes available" filtered/live (updates as user searches/picks a tab), not an unfiltered operator-wide total. Zero backend work, confirms original spec.

## Related
- This session's token-consistency fix on the same page: branch `fix/operators-design-tokens` (typography, badge colors, border-radius, `LAYOUT.pageContentClasses` width fix).
- Closest precedent in this vault: [[experience-detail-page-redesign]] — same shape (detail-page premium redesign spec, component-reuse-first, no code yet).
- Token source: `helpers/designSystem.js` (`LAYOUT.pageContentClasses` added this session, `COLORS.badge.tourTypeSoft` also added this session).

## Files referenced
`pages/operators/[slug].js` (450 lines, to be reduced via extraction), new `components/operators/OperatorFilterBar.js`, `components/airport-transfer/TripListingSection.js` (tab pattern precedent), `helpers/designSystem.js`. Backend (if pursuing tab counts): `smartenplus-backend/operators/views.py` `OperatorContractsViewSet.list`.
