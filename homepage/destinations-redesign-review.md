# Destinations Section Redesign Review — 2026-05-29

**Section:** "Popular Travel Destinations" → proposed "Thailand's Top Destinations"
**Branch at review:** `260528-feat/header-redesign-2026`
**Team:** UX Auditor · Design Strategist · Implementation Planner
**Status:** Research complete — implementation approved pending contrast audit
**Scrutiny pass:** 2026-05-29 — 4 major corrections applied (see Scrutiny Notes)

---

## Files Under Review

| File | Role |
|------|------|
| `lib/homepage/components/LocationsSection.js` | Section wrapper |
| `components/UI/LocationGridComponent.js` | Uniform grid renderer (to be replaced for homepage only) |
| `lib/homepage/components/LocationsStructuredData.js` | JSON-LD SEO |
| `lib/homepage/components/LocationsErrorBoundary.js` | Error boundary |
| `lib/homepage/components/LocationsSkeletonLoader.js` | Skeleton |
| `pages/homepagev2.js` line 359 | Integration point |

**Current data shape:** `{ location_name: string, route_count: number, image: string }`

---

## UX Audit (Agent 1)

### Composite Score: 22/80 (28%)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Visual Hierarchy | 2/10 | `isFirst` flag drives `loading="eager"` only — zero visual distinction. All 7 cards identical size, weight, overlay. |
| Booking Intent Support | 3/10 | Cards link to `/locations/{slug}` listing page. No price, no departure context, no direct booking affordance. Two hops from booking. |
| Emotional Framing | 2/10 | Only metadata: `(N trips)` — a supply count. Nothing communicates "beach escape" or "overnight train." |
| Information Density | 3/10 | Too sparse (no price, no travel time) AND too compressed — name + count crammed into `min-h-[64px]`. |
| Photography Quality Perception | 3/10 | Hardcoded `bg-black bg-opacity-40` on every card regardless of image luminosity. `DEFAULT_ROUTE_IMAGE` fallback can repeat across multiple cards. |
| CTA Effectiveness | 2/10 | "Explore More..." rendered as `bg-gray-100 rounded` div consuming a full grid slot — no icon, no count, reads as maintenance link. |
| Mobile Experience | 4/10 | Grid structure sound (`grid-cols-1` fallback), but `min-h-[64px]` too short for any meaningful image crop on mobile. |
| Section Title Clarity | 3/10 | Generic. Works on any travel site anywhere. Skeleton uses completely different title ("Find Perfect Locations") — no locked rationale. |

### Problem Validation

| Problem | Verdict | Evidence |
|---------|---------|----------|
| All cards identical — no hierarchy | CONFIRMED | `isFirst` only affects `loading` prop (line 29 LocationGridComponent). No class difference between card 1 and card 7. |
| Repeated dark overlays feel low quality | CONFIRMED (partial) | `bg-black bg-opacity-40` hardcoded for all cards. `DEFAULT_ROUTE_IMAGE` fallback creates visible repetition. Overlay technique not inherently bad — undifferentiation is the problem. |
| "(11 trips)" not emotionally useful | CONFIRMED | Route count is supply metadata. Baymard travel UX research: users evaluate destinations via price anchors or qualitative signals — not supply counts. |
| "Explore More..." wastes space | CONFIRMED | Occupies full grid cell. No imagery, no benefit. Booking.com/GYG place this CTA below the grid as a styled button. |
| Grid feels like sitemap | CONFIRMED (partial) | 7 equal-weight cards, minimal height, absence of ordering signal produces scan-in-reading-order behavior. Cards do have photography — problem is crops are too small to be meaningful at 64px. |
| Doesn't support booking intent | CONFIRMED | Link target is a listing page, not a pre-filtered search state. Extra navigation hop before any bookable result. |
| Title "Popular Travel Destinations" is generic | CONFIRMED | No Thailand specificity, no transport context, no value proposition. Skeleton uses different title. |

### Platform Comparison

**What leading platforms do that SmartEnPlus doesn't:**

| Platform | Key Differentiator |
|----------|-------------------|
| Airbnb (2025) | Asymmetric masonry layout. Featured destinations take 2× horizontal space. Text below image (not over it) — no overlay needed. |
| Booking.com | Carousel of 3 large cards precedes any grid. Each card shows property count as "X properties" with starting price. CTA below grid (not inside it). |
| GetYourGuide | Hero cards per section are visually larger. Gradient overlay (not flat black) adapts to image luminosity. CTA: "Explore [destination name]" — destination repeated in CTA. |
| Klook | Thumbnail 50/50 image/text split. Shows star rating + "from [price]" anchor + one-line descriptor ("Theme Parks", "Beach Hopping"). Horizontal scroll carousel on mobile. |

**Shared patterns across all four — all absent from SmartEnPlus:**
- At least one "from ฿X" price anchor per card or section
- Editorial curation signal ("popular", "trending", star rating)
- Gradient overlay (not flat black opacity)
- CTA outside grid flow
- Horizontal scroll on mobile

### Top 3 Highest-Impact Changes (by UX ROI)

1. **Surface "from price" anchor or qualitative tag** — single highest ROI. Converts browsing surface to comparison surface. If exact pricing unavailable at ISR time, use qualitative tag from editorial copy map. Baymard + Klook pattern both confirm.

2. **Hero card with asymmetric layout** — first card spans 2 columns / double height. Breaks sitemap perception, creates focal point. `isFirst` flag already exists in data model — needs to drive visual output, not just image loading.

3. **Move "Explore More..." out of grid** — styled below-grid button: "See all [N] destinations in Thailand →". Plus change card link text to "Find routes to [destination]" to explicitly connect discovery to booking.

### What to Keep

**Keep the `<article>` semantic markup with `itemScope` / `itemType="https://schema.org/TouristDestination"` and `aria-label` on each link.** Correctly formed, WCAG 2.1 AA compliant, rare in production travel codebases. `role="list"` / `role="listitem"` pairing also correct. Preserve through redesign.

---

## Design Debate (Agent 2)

### Q1: `rounded-2xl` — VERDICT: MODIFY → use `rounded-xl`

Design system token is `rounded-md` (6px) for containers. However, codebase has already drifted: `DiscoverySection.js` (highest-visibility element on homepage) uses `rounded-xl`. `AccountCard.js`, `ProfileHeader.js`, `LocationCard.js` also use `rounded-xl` / `rounded-2xl` without system tokens.

> ⚠️ **Scrutiny correction:** The original report argued that `rounded-2xl` cards nested inside a `rounded-md` ContentCard creates nesting inversion. This argument is moot — Q2 below also concludes ContentCard should be skipped entirely. The real reason to prefer `rounded-xl` is design system drift normalization: `rounded-xl` (12px) already appears in `DiscoverySection.js` (the homepage's highest-visibility element), making it the de-facto precedent. Also note: current `LocationGridComponent` article cards actually use `rounded` (4px, bare class) — not `rounded-md` (6px). The token addition fills a gap, not a replacement.

**Use `rounded-xl` (12px).** Formalize as `imageCard: 'rounded-xl'` token in `BORDER_RADIUS_CLASSES`. Do not go to `rounded-2xl` without also updating the search hero.

### Q2: Asymmetric layout vs. ContentCard — VERDICT: MODIFY → skip ContentCard

`ContentCard` contributes: `bg-white`, `flex-col`, `rounded-md`, `overflow-hidden`. For a photo-led editorial section:
- `bg-white` is irrelevant (photography fills cards)
- `overflow-hidden` should live on individual cards (to clip image at corners), not the section wrapper
- `flex-col` blocks the asymmetric CSS grid layout

**Skip ContentCard entirely.** Use `Section` + local grid div directly — the same escape hatch `PopularRoutesSection` already uses. `SectionHeader` is layout-independent and reusable as-is.

### Q3: Section title — VERDICT: MODIFY

"Popular Travel Destinations" — generic, no transport context.
"Explore Thailand by Destination" (proposed) — structural UX copy, not SEO-optimized, still no transport context.

SmartEnPlus brand voice (from `DiscoverySection.js`): "Travel Thailand your way — Book buses, ferries, trains and airport transfers." — direct, action-oriented, transport-explicit.

**Recommended title:** `"Thailand's Top Destinations"` with subtext `"Find bus, ferry & train routes."` — keeps editorial feel, anchors transport context, short enough for `text-xl` heading. Structured data (`LocationsStructuredData`) carries SEO weight; visible heading is secondary.

### Q4: 4–5 destinations max — VERDICT: MODIFY → 5–6 with `featured` flag

Risks at 4–5 slots:
- Bangkok + Phuket + Koh Samui + Krabi + Hat Yai = south-only, Chiang Mai excluded
- Adding Chiang Mai = Hat Yai dropped (loses southern land-border hub for Malaysian travelers)
- If featured card is `allLocations[0]` (database insertion order), backend reordering breaks visual hierarchy

**Use 5 minimum, 6 preferred.** Negotiate a `featured: boolean` or `sort_order` field with backend team. Until landed, treat `index === 0` as featured and document the assumption explicitly in code.

### Q5: Traveler-context strings — VERDICT: MODIFY → Option A with conditions

Backend provides `{ location_name, route_count, image }` — no editorial copy field.

Option A (hardcode frontend) is most pragmatic for SmartEnPlus 3-repo setup. Option B (backend field) is over-engineered for decorative copy. Option C (derive from route types) requires a new `route_type_breakdown` API field — equivalent complexity to Option B.

**Create `/lib/homepage/data/destinationCopy.js`** — slug-keyed map (`slugify(location_name) → { tag, context }`). Null fallback: missing slugs render no badge. Document as editorial copy file (quarterly review cadence), not code. Structure for future i18n keys.

### Q6: Mobile swipe — VERDICT: APPROVE (with architectural correction)

Complexity concern is mitigated by existing infrastructure. `CardCarouselContainer.js` already implements Embla Carousel with `useEmblaCarousel`, loop mode, `PrevButton`/`NextButton`. `PopularRoutesCarousel.js` wraps it in 30 lines.

> ⚠️ **Scrutiny correction — two issues:**
>
> **Issue 1 — Breakpoint choice unjustified:** `PopularRoutesCarousel` uses `carouselBreakpoint="lg"` (1024px). The report recommends `carouselBreakpoint="md"` (768px) for destinations without justifying the difference. The asymmetric desktop grid is complex enough that it should activate only at `lg` (1024px), matching PopularRoutes. At 768px–1023px (tablets), the asymmetric `2fr 1fr` grid may be too cramped. **Recommend `carouselBreakpoint="lg"` unless intentionally targeting tablet grid view.**
>
> **Issue 2 — Double-guard anti-pattern:** Original blueprint wraps `CardCarouselContainer` in `md:hidden` AND passes `desktopMode="carousel"`. These two mechanisms fight each other. `desktopMode="carousel"` already suppresses the static grid inside `CardCarouselContainer`. The outer `md:hidden` wrapper is then redundant. Choose one: (a) wrap in `lg:hidden` div, omit `desktopMode`, let `carouselBreakpoint="lg"` handle the switch, OR (b) no wrapper div, use `desktopMode="carousel"` + `carouselBreakpoint="lg"` and let `CardCarouselContainer` manage both cases. Option (b) matches how `PopularRoutesCarousel` is built.

**Reuse `CardCarouselContainer`** via a `PopularRoutesCarousel`-style wrapper component. Zero new carousel code, zero new dependencies.

### Design System Alignment Summary

| Element | Proposed | Existing | Recommendation |
|---------|----------|----------|----------------|
| Card radius | `rounded-2xl` (16px) | `rounded-md` token; `rounded-xl` in search form | `rounded-xl` (12px), add `imageCard` token |
| Section wrapper | ContentCard (implied) | ContentCard with `bg-white flex-col` | Skip ContentCard; use Section directly |
| Heading | "Explore Thailand by Destination" | `text-xl font-semibold` | "Thailand's Top Destinations" + subtext |
| Overlay | Softer (unspecified) | `bg-black/40` | `bg-black/25` rest, `bg-black/10` hover — verify WCAG |
| Whitespace | More (unspecified) | `gap-2 p-2` | `gap-4 md:gap-6` for destination grid only |
| Hover | Unspecified animation | `hover:scale-[1.02] hover:shadow-lg duration-200` | `hover:scale-[1.03]` — keep duration-200, no JS animation |
| Mobile | Horizontal swipe | `grid-cols-1` collapse | Swipe via CardCarouselContainer — REUSE |
| Route count | Remove visible | Shown in span | Remove from UI; keep in `aria-label` |
| CTA | "Explore all destinations →" | "Explore More..." gray div | Below-grid text link with chevron, brand primary color |

### Overall Verdict: MODIFIED BRIEF — proceed

Editorial direction is correct. Brief's instinct to move from dense utility grid to photo-led scannable layout is right for a platform competing with Klook/GYG. Implementation path is cleaner than brief suggests — carousel infrastructure already exists, ContentCard constraints point to the right architectural decision.

---

## Implementation Blueprint (Agent 3)

### File Change Map

| File | Action | What Changes |
|------|--------|-------------|
| `components/UI/LocationGridComponent.js` | PRESERVE | Used in `pages/locations/index.js` and `pages/homepagev1.js` — untouched |
| `lib/homepage/components/LocationsStructuredData.js` | PRESERVE | Receives full `allLocations` array — layout change invisible to it |
| `lib/homepage/components/LocationsErrorBoundary.js` | PRESERVE | Interface unchanged |
| `helpers/designSystem.js` | MODIFY | Add `imageCard: 'rounded-xl'` to `BORDER_RADIUS_CLASSES`; `imageCard: '12px'` to `BORDER_RADIUS` |
| `lib/homepage/data/destinationCopy.js` | CREATE | Slug-keyed editorial copy map |
| `lib/homepage/components/DestinationsEditorialGrid.js` | CREATE | Desktop asymmetric CSS grid component (lg+ only) |
| `lib/homepage/components/DestinationsCarousel.js` | CREATE | Mobile/tablet carousel wrapper — mirrors PopularRoutesCarousel pattern |
| `lib/homepage/components/LocationsSection.js` | MODIFY | Remove ContentCard + LocationGridComponent; add DestinationsEditorialGrid + DestinationsCarousel; update copy; add GTM |
| `lib/homepage/components/LocationsSkeletonLoader.js` | MODIFY | Remove ContentCard; update skeleton shape to asymmetric 5-slot; update title string |
| `pages/homepagev2.js` | MODIFY | Remove dead `LocationGridComponent` import (line 15 — confirmed unused) |

### New Component: DestinationsEditorialGrid.js

**Location:** `lib/homepage/components/DestinationsEditorialGrid.js`

**Props:**
```js
DestinationsEditorialGrid({
  items,        // allLocations.slice(0, 5) — passed by caller
  onItemClick,  // (item) => void — GTM, optional
  onItemHover,  // (item) => void — router.prefetch, optional
})
```

**Internal processing** (single `useMemo`):
- `slug` ← `slugify(item.location_name)`
- `capitalizedLocation` ← `capitalizeWords(item.location_name)`
- `imageUrl` ← `item.image || DEFAULT_ROUTE_IMAGE`
- `routeCount` ← `item?.route_count ?? 0`
- `copy` ← `DESTINATION_COPY[slug] ?? null`
- `isFeatured` ← `index === 0`
- `isEager` ← `index === 0`
- `index` ← `index` (map callback second arg — **required for GTM `destination_position` field**)

**FeaturedCard** (items[0]) — inner component, not exported:
- `<article>` with `rounded-xl overflow-hidden relative group`
- Image: `fill`, `object-cover`, `priority`, `sizes="(max-width: 768px) 100vw, 66vw"`
- Overlay: `absolute inset-0 bg-black/25 transition-opacity duration-200 group-hover:bg-black/10`
- Content pinned to bottom: `absolute bottom-0 left-0 right-0 p-4`
- Name: `text-xl font-bold text-white`
- Tag badge (conditional on `copy?.tag`): `inline-block mb-2 px-2 py-0.5 text-xs font-medium bg-white/20 text-white rounded`
- Link `aria-label`: `"View trips to ${capitalizedLocation}, ${routeCount} routes available"`

**SupportingCard** (items[1]–[4]) — same file:
- Same overlay/group pattern
- Name: `text-base font-semibold text-white`
- Same tag badge pattern

**Desktop grid** (`hidden md:grid`):
```
grid-template-columns: 2fr 1fr   [grid-template-columns:2fr_1fr]
gap-3

FeaturedCard:      row-span-2, min-h-[320px]
SupportingCard[1]: col-start-2 row-start-1, min-h-[152px]
SupportingCard[2]: col-start-2 row-start-2, min-h-[152px]
Sub-row div:       col-span-2 grid grid-cols-2 gap-3
  SupportingCard[3]: min-h-[180px]
  SupportingCard[4]: min-h-[180px]
```

**Mobile carousel** — via wrapper component `DestinationsCarousel.js` (mirrors `PopularRoutesCarousel.js`):
- `CardCarouselContainer` with `desktopMode="carousel"`, `carouselBreakpoint="lg"`
- Do NOT wrap in `lg:hidden` div — `CardCarouselContainer` handles the breakpoint internally
- `renderCard={(item) => <SupportingCard item={item} />}` — uniform cards on mobile/tablet
- Slide wrapper: `min-w-[220px] sm:min-w-[280px] h-[200px]`

> ⚠️ **Scrutiny correction:** Original blueprint used `md:hidden` wrapper + `desktopMode="carousel"` + `carouselBreakpoint="md"`. This is a double-guard anti-pattern. Corrected to single-guard via `CardCarouselContainer` alone with `carouselBreakpoint="lg"`. Matches `PopularRoutesCarousel` architecture exactly.

### destinationCopy.js

**Location:** `lib/homepage/data/destinationCopy.js` (create `lib/homepage/data/` directory)

```js
// Editorial copy keyed by slugify(location_name).
// tag: qualitative badge shown on card (max 20 chars).
// context: reserved for future tooltip/extended use.
// Missing slug = null fallback = no badge rendered.
const DESTINATION_COPY = {
  'bangkok':    { tag: 'Bus & Train Hub',    context: "Thailand's central transport interchange with routes to every region." },
  'phuket':     { tag: 'Island Gateway',     context: 'Southern hub for ferries to Koh Phi Phi, Koh Lanta, and beyond.' },
  'koh-samui':  { tag: 'Gulf Island',        context: 'Ferry connections from Surat Thani and Donsak Pier.' },
  'koh-lipe':   { tag: 'Remote Beach',       context: 'Southern Andaman island, ferry from Pak Bara or Langkawi.' },
  'hat-yai':    { tag: 'Southern Hub',       context: 'Key interchange for trains, buses, and cross-border routes.' },
  'krabi':      { tag: 'Andaman Base',       context: 'Ferry departures to Koh Lanta, Koh Phi Phi, and Phuket.' },
  'chiang-mai': { tag: 'Northern Capital',   context: 'Buses and trains to Bangkok; gateway to northern routes.' },
  'surat-thani':{ tag: 'Ferry Crossroads',   context: 'Mainland pier hub for Koh Samui, Koh Pha Ngan, and Koh Tao.' },
};
export default DESTINATION_COPY;
```

### LocationsSection.js Changes

**Remove:** `ContentCard` import + wrapper, `LocationGridComponent` import + usage, `limit={7}` / `showExploreLink` props

**Add:**
- `import DestinationsEditorialGrid from './DestinationsEditorialGrid'`
- `import { sendGTMEvent } from '@next/third-parties/google'`
- `import { isGTMEnabled } from '../../../helpers/gtmUtils'`
- `import { useCallback } from 'react'`
- `import { useRouter } from 'next/router'`

**Updated SectionHeader:**
```jsx
<SectionHeader
  icon={ExploreOutlinedIcon}
  title="Thailand's Top Destinations"
  href="/locations"
/>
<p className="px-2 text-sm text-gray-500">Find bus, ferry & train routes.</p>
```

**Render structure:**
```jsx
<Section aria-label="Thailand's top travel destinations" className="py-6 px-4 xl:px-0">
  <LocationsErrorBoundary>
    <header>
      <SectionHeader ... />
      <p ...>Find bus, ferry & train routes.</p>
    </header>
    <DestinationsEditorialGrid
      items={allLocations.slice(0, 5)}
      onItemClick={trackDestinationClick}
      onItemHover={handleDestinationHover}
    />
    <div className="flex justify-center mt-4">
      <Link
        href="/locations"
        onClick={handleSeeAllClick}
        className="inline-flex items-center gap-1 text-sm font-medium text-blue-700 hover:underline focus:underline"
      >
        See all destinations in Thailand →
      </Link>
    </div>
  </LocationsErrorBoundary>
</Section>
```

**GTM callbacks:**
```js
const trackDestinationClick = useCallback((item) => {
  if (isGTMEnabled()) {
    sendGTMEvent({
      event: 'destination_click',
      destination_name: item.capitalizedLocation,
      destination_slug: item.slug,
      destination_position: item.index,
      is_featured: item.isFeatured,
      route_count: item.routeCount,
      category: 'destinations_section',
      section_title: "Thailand's Top Destinations",
    });
  }
}, []);

const handleSeeAllClick = useCallback(() => {
  if (isGTMEnabled()) {
    sendGTMEvent({
      event: 'destinations_see_all_click',
      category: 'destinations_section',
      section_title: "Thailand's Top Destinations",
    });
  }
}, []);
```

### LocationsSkeletonLoader.js Changes

Remove `ContentCard`. Update `SectionHeader` title to `"Thailand's Top Destinations"`. Replace uniform 7-slot grid with asymmetric 5-slot skeleton:

```
Mobile: 1 tall (h-[200px]) + 2 shorter (h-[140px]) stacked
Desktop (hidden md:grid [grid-template-columns:2fr_1fr] gap-3):
  - Featured slot: row-span-2 h-[320px] rounded-xl bg-gray-200 animate-pulse
  - Slot 2: h-[152px] rounded-xl bg-gray-200 animate-pulse
  - Slot 3: h-[152px] rounded-xl bg-gray-200 animate-pulse
  - Sub-row (col-span-2 grid grid-cols-2 gap-3):
    - Slot 4: h-[180px] rounded-xl bg-gray-200 animate-pulse
    - Slot 5: h-[180px] rounded-xl bg-gray-200 animate-pulse
```

### designSystem.js Changes

```js
// BORDER_RADIUS_CLASSES — add:
imageCard: 'rounded-xl',   // 12px — editorial image cards

// BORDER_RADIUS — add:
imageCard: '12px',
```

`DestinationsEditorialGrid` imports `BORDER_RADIUS_CLASSES.imageCard` — token is the source of truth.

### Analytics Events

| Event | Trigger | Key Fields |
|-------|---------|-----------|
| `destination_click` | Card link click | `destination_name`, `destination_slug`, `destination_position`, `is_featured`, `route_count` |
| `destinations_see_all_click` | "See all" link click | `category`, `section_title` |

Pattern: mirror `PopularRoutesSection` exactly — `sendGTMEvent` + `isGTMEnabled()` guard.

### Build Sequence

- [ ] **Phase 1** — `helpers/designSystem.js`: add `imageCard` token
- [ ] **Phase 2** — Create `lib/homepage/data/destinationCopy.js`
- [ ] **Phase 3** — Create `lib/homepage/components/DestinationsEditorialGrid.js` (desktop `lg+` only, no carousel logic)
- [ ] **Phase 4** — Create `lib/homepage/components/DestinationsCarousel.js` (mirrors `PopularRoutesCarousel.js`; uses `CardCarouselContainer` with `carouselBreakpoint="lg"` + `desktopMode="carousel"`)
- [ ] **Phase 5** — Modify `lib/homepage/components/LocationsSection.js`
- [ ] **Phase 6** — Modify `lib/homepage/components/LocationsSkeletonLoader.js`
- [ ] **Phase 7** — Remove dead import from `pages/homepagev2.js` line 15
- [ ] **Phase 8** — `npm run lint` — fix any import errors
- [ ] **Phase 9** — Dev smoke test (all verification steps)
- [ ] **Phase 10** — Contrast audit before PR

---

## Risk Flags

| Risk | Severity | Mitigation |
|------|----------|-----------|
| `LocationGridComponent` still used in `pages/locations/index.js` and `pages/homepagev1.js` | HIGH | Do NOT modify it. New `DestinationsEditorialGrid` is homepage-only. |
| WCAG contrast: `bg-black/25` drops from current `bg-black/40` by 37% — white text on light beach images may fail 4.5:1 | MEDIUM | Test against actual destination images. If fail: increase to `bg-black/35`, OR add `[text-shadow:0_1px_3px_rgba(0,0,0,0.8)]` on name spans. |
| ISR: featured card (`index === 0`) stays stale for revalidation window after backend reorders | MEDIUM | Acceptable ISR behavior. Document assumption in code comment. Negotiate `featured: boolean` field with backend for permanent fix. |
| `[grid-template-columns:2fr_1fr]` arbitrary Tailwind value may be purged | LOW | Verify `tailwind.config.js` content glob covers `lib/**/*.js`. If not, add `gridTemplateColumns: { 'destinations': '2fr 1fr' }` extension. |
| `homepagev2.js` has dead `LocationGridComponent` import (line 15 — confirmed zero render-site usages via grep) | LOW-CONFIRMED | Remove unconditionally in the same PR. The comment `// Assuming this is TripRouteGridComponent after rename` is misleading — no rename evidence found. Safe to delete. |

---

## Verification Checklist

- [ ] Heading "Thailand's Top Destinations" + subtext "Find bus, ferry & train routes." visible
- [ ] 5 destination cards render — no "(N trips)" text visible anywhere
- [ ] Featured card (index 0) visually larger — spans left column, double height
- [ ] Cards 4 + 5 appear in sub-row below
- [ ] `aria-label` on each link contains route count (inspect in DevTools)
- [ ] "See all destinations in Thailand →" button below grid, not inside it
- [ ] Mobile <768px: asymmetric grid hidden, horizontal carousel visible, all 5 cards swipeable
- [ ] Skeleton shape matches asymmetric layout (1 tall + 2 medium + 2 sub-row)
- [ ] `/locations` page still renders `LocationGridComponent` with "(N trips)" counts — regression clear
- [ ] `<script type="application/ld+json">` with `ItemList` present in page source
- [ ] `destination_click` event fires in `dataLayer` on card click with correct fields
- [ ] `destinations_see_all_click` fires on "See all" click
- [ ] `npm run build` clean — no module resolution errors
- [ ] WCAG contrast audit on FeaturedCard white text over `bg-black/25` — pass 4.5:1

---

## Scrutiny Notes (Cold-Read Pass — 2026-05-29)

Verified all code claims against actual source files. Findings ordered blocker → major → nit.

### BLOCKER — none. No claim invalidates the redesign direction.

### MAJOR (4)

**M1 — rounded argument was entangled with ContentCard nesting**
Report claimed `rounded-2xl` → `rounded-xl` because nesting inversion inside ContentCard. ContentCard is being skipped — so nesting is irrelevant. Real reason: `rounded-xl` is de-facto drift standard in codebase (`DiscoverySection.js`, `AccountCard.js`, `LocationCard.js`). Also: current cards use `rounded` (4px bare), not `rounded-md` (6px token). Token addition fills a gap, not a replacement. Corrected in Q1 above.

**M2 — Mobile carousel: double-guard anti-pattern**
Blueprint specified `md:hidden` wrapper + `desktopMode="carousel"` + `carouselBreakpoint="md"` simultaneously. `CardCarouselContainer` already handles breakpoint switching internally — the outer `md:hidden` wrapper is redundant and confusing. Corrected: use `CardCarouselContainer` alone with `carouselBreakpoint="lg"` via a `DestinationsCarousel.js` wrapper (matching `PopularRoutesCarousel` architecture). File Change Map updated to include this new file.

**M3 — Carousel breakpoint choice unjustified**
Report chose `carouselBreakpoint="md"` (768px) without explaining why, when `PopularRoutesCarousel` uses `carouselBreakpoint="lg"` (1024px). The asymmetric `2fr 1fr` CSS grid on a 768px viewport produces a ~510px featured card and ~250px supporting card — likely too cramped. Corrected to `lg` (1024px) to match site-wide precedent and give the asymmetric layout room to breathe.

**M4 — GTM `destination_position` field silently undefined**
GTM callback references `item.index` but the `processedItems` useMemo spec did not include `index`. Sending `destination_position: undefined` to dataLayer. Corrected: `index` explicitly mapped in processedItems.

### NIT (1)

**N1 — Dead homepagev2.js import described as "possibly unused"**
Risk Flag R5 said "verify before PR." Grep confirms: `LocationGridComponent` appears only at line 15 (import), zero render-site usages in `homepagev2.js`. Upgraded to CONFIRMED. File Change Map updated to include this as a MODIFY action.

### Verdict: fix-then-ship

No finding invalidates the redesign direction. All 4 major issues are implementation-level corrections, not architectural rethinks. Apply corrections before coding.

---

## Team Verdict

**Proceed with modified brief.** Redesign direction validated by 3-agent review + scrutiny pass. Key modifications from original brief:

1. `rounded-xl` not `rounded-2xl` — design system drift normalization (not nesting argument — see M1)
2. Skip `ContentCard` — follow `PopularRoutesSection` escape hatch
3. Title: "Thailand's Top Destinations" + transport subtext — brand voice alignment
4. 5 destinations minimum (not 4) — avoid regional gap
5. Frontend copy map (`destinationCopy.js`) not backend field — zero cross-repo coordination
6. Reuse `CardCarouselContainer` via `DestinationsCarousel.js` wrapper — matches `PopularRoutesCarousel` pattern exactly (see M2 + M3)
7. Overlay `bg-black/25` — pending contrast audit against real images
8. `index` included in processedItems — required for GTM `destination_position` (see M4)
9. Remove dead `pages/homepagev2.js` line 15 import — confirmed unused (see N1)

**Recommended next step:** Implement in Build Sequence Phases 1–5 + `homepagev2.js` cleanup. Run contrast audit before raising PR. Tag backend team to add `featured: boolean` on Location model as a follow-up (non-blocking for this PR).
