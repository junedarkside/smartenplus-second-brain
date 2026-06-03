# Homepage UX/UI Review 2026-05-21

## Summary
3-agent review, 11 homepage sections. 4 critical, 34 major, 15 minor issues. Top: XSS in reviews, section reorder, inline search validation, hero value prop.

## Context
SmartEnPlus homepage (`pages/homepagev2.js`) — primary transport booking conversion surface. Review triggered for UX/UI quality, WCAG, design system compliance, conversion gaps pre-feature-work.

Team: UX Research Agent (Hero/Search/Routes) + UX Research Agent (Content Sections) + UI Component Engineer (Bottom Sections + Design System).

## Section Render Order (Current vs Recommended)

**Current:**
```
1. Hero + Search
2. Popular Routes
3. Guides (blog)       ← blog too early
4. Locations
5. Thailand Travel
6. Airport Transfer
7. News (blog)         ← blog fragments funnel
8. Reviews             ← trust signal buried
9. Activities (blog)   ← sandwiches Reviews
10. My Bookings CTA
11. Customer Service
```

**Recommended:**
```
1. Hero + Search
2. Popular Routes
3. Locations           ← group discovery
4. Airport Transfer    ← group discovery
5. Reviews             ← trust before editorial
6. Thailand Travel     ← features/trust
7. Guides (blog)       ← nurture/SEO
8. News + Activities   ← collapse or tab
9. My Bookings CTA
10. Customer Service
```

Reviews 8→5 = highest-leverage change. Most mobile users never scroll to position 8.

## Critical Issues

### C1 — XSS in Reviews (Security)
**File:** `components/review/ReviewFirstPage.js:185`
```jsx
dangerouslySetInnerHTML={{ __html: reviewText }}
```
User content rendered raw. No DOMPurify. Active XSS risk.
**Fix:** Sanitize backend before API serves. Client-only: `isomorphic-dompurify` — plain `DOMPurify` throws `window is not defined` on SSR (Next.js).

### C2 — Hero No Value Proposition
**File:** `pages/homepagev2.js:335`
`h1` from `seoData.title` — crawler-optimized, not user-optimized. No subheadline. First-time visitor lacks product context.
**Fix:** Add static subheadline: *"Book buses, ferries and trains across Thailand — instantly confirmed."*

### C3 — Search Validation: Toast Only, No Inline Errors
**File:** `pages/homepagev2.js:249`
Empty fields show toast only. No field highlight, no inline message. Direct abandonment risk.
**Fix:** Red border + inline error per empty required field on submit.

### C4 — Locations Title No Transport Context
**File:** `lib/homepage/components/LocationsSection.js:36`
"Find Perfect Locations" reads like hotel/real estate. SEO structured data (line 27) says "Popular Travel Destinations in Thailand" — that copy should be visible heading.

## Major Issues by Section

### Hero + Search
- Auto-rotating hero banner — no pause control, WCAG 2.2.2 violation (`homepagev2.js:180-186`)
- From/To inputs are `readOnly <input>` used as buttons — wrong semantic element (`ProductSearchForm2.js:219-256`)
- Mobile search card `min-h-[300px]` → layout shift during hydration (`homepagev2.js:340`)
- Switch label static "Round Trip" regardless of state + redundant badge (`ProductSearchForm2.js:196-213`)

### Popular Routes
- Route cards no visible CTA — hover-only underline, useless on touch (`PopularRouteImageCard.js:63-81`)
- Carousel no position indicators on mobile (`CardCarouselContainer.js:33-44`)
- Duplicate `<main>` landmark inside section — one `<main>` per page max (`PopularRoutesSection.js:101`)

### Guides Section
- Same duplicate `<main>` issue (`GuidesSection.js:136`)
- Link text "and more to discover" non-descriptive for screen readers (`GuidesSection.js:45`)

### Locations
- Error state renders skeleton loader instead of error message — unrecoverable (`LocationsSection.js:17-19`)
- Route count "(3 trips)" no transport mode context (`LocationGridComponent.js:83`)
- `sizes` attribute wrong at all breakpoints (`LocationGridComponent.js:59`): `grid-cols-1` at <640px means images full-width (should be `100vw`), `grid-cols-2` at 640px+ means ~50vw. Correct: `(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw`

### Thailand Travel (Features Carousel)
- Feature descriptions hidden on tablet — `hidden lg:block` invisible at `md` breakpoint (`ThailandTravel.js:81`)
- Carousel wrong pattern for feature/trust content — Nielsen: users miss non-first panels. Should be flat 3-col layout
- Carousel prev/next no `aria-label` — WCAG 4.1.2 violation (`CarouselArrowButtons.js:124,149`)
- Carousel no `role`, `aria-roledescription`, `aria-live` — invisible to screen readers (`ThailandTravel.js:67`)

### Airport Transfer
- No CTA on station cards — name only, no "View routes" or "Book" signal (`GridComponent4.js:9-24`)
- Error state silently swallowed — section disappears, no feedback (`AirportTransferSection.js:9`)
- IATA: `capitalizeWords` preserves all-uppercase strings (verified). Bug conditional — if backend stores `iata_code` lowercase ("bkk"), produces "Bkk". Verify backend field case; if mixed, replace `capitalizeWords(item.iata_code)` with `item.iata_code?.toUpperCase()` (`GridComponent4.js:12`)

### Reviews
- Fake rating fallback `|| '5.0'` shows fabricated rating when data missing
- No mobile swipe affordance — no dots, no peek on mobile carousel (`ReviewFirstPage.js:330`)
- No rating breakdown (5★/4★/...) — highest-converting trust signal absent
- Error state different background from normal — inconsistent

### My Bookings CTA
- Static input IDs `id="booking-id"` / `id="booking-email"` — breaks if rendered twice
- Booking ID vs Order ID toggle no helper text or format example
- Weak value prop — no description of what "manage" means

### Customer Service
- Heading reads "Helps" — grammatically wrong. Should be "Help Topics" (`CustomerServiceSection.js:40`)
- Forum link relative URL `forum/?category=...` — missing leading slash, breaks under sub-paths (`CustomerServiceSection.js:83`)
- Help links also missing leading slash: `help/${item.slug}` at line 46 — same bug, same fix
- `<article>` elements lack `aria-labelledby` (`CustomerServiceSection.js`)

### Design System
- `HOMEPAGE_SECTION` tokens in `helpers/designSystem.js` unused — all components hand-code class strings
- `text-xl md:text-xl` no-op on all h2s — design system uses `text-xl sm:text-2xl` for responsive scaling
- Multiple unnamed `<section>` landmarks — `Section.js` never passes `aria-label`

## Priority Fix Queue

**P0 — Security**
1. DOMPurify on `dangerouslySetInnerHTML` in ReviewFirstPage

**P1 — Conversion (highest ROI)**
2. Move Reviews to position 5 (reorder, ~10 min)
3. Add inline validation errors to search form (~1-2 hrs)
4. Add hero value proposition subheadline
5. Remove `|| '5.0'` fake rating fallback
6. Fix Locations section title

**P2 — Accessibility (WCAG)**
7. Remove duplicate `<main>` in PopularRoutesSection + GuidesSection
8. Add `aria-label` + ARIA roles to ThailandTravel carousel
9. Add pause control to hero banner rotation
10. Add `aria-labelledby` to Customer Service articles
11. Add `aria-label` to all `<Section>` usages

**P3 — UX Friction**
12. Replace readOnly inputs with button elements in search form
13. Add visible CTA to route cards
14. Add dot indicators to Popular Routes carousel
15. Fix ThailandTravel feature descriptions hidden on tablet
16. Add "View routes" text to airport station cards
17. Show error state (not skeleton) in LocationsSection
18. Handle error prop in AirportTransferSection
19. Fix IATA code capitalization
20. Add helper text to Booking ID toggle
21. Fix "Helps" → "Help Topics"
22. Fix relative URLs in CustomerService — forum links (`line 83`) AND help links (`line 46`) missing leading slash

**P4 — Design System**
23. Adopt `HOMEPAGE_SECTION` tokens in section components
24. Fix `text-xl md:text-xl` no-op — use `TYPOGRAPHY_SCALE.h2`
25. BookingRetrievalForm: `focus:ring-fb-blue`, button `py-3 px-6`
26. Remove unused `timeAgo` import
27. Fix `hasImage: !!item.image || true` boolean bug

## Key Files
- `pages/homepagev2.js` — section orchestration, render order
- `components/UI/FeaturedImageHeader.js` + `components/search/ProductSearchForm2.js` — hero + search
- `lib/homepage/components/PopularRoutesSection.js` + `PopularRouteImageCard.js` — popular routes
- `lib/homepage/components/LocationsSection.js` + `components/UI/LocationGridComponent.js` — locations
- `components/FrontPage/ThailandTravel.js` — features carousel
- `lib/homepage/components/AirportTransferSection.js` + `components/UI/GridComponent4.js` — airport
- `components/review/ReviewFirstPage.js` — reviews (XSS here)
- `components/FrontPage/BookingRetrievalForm.js` — booking CTA
- `components/FrontPage/CustomerServiceSection.js` — customer service
- `helpers/designSystem.js` — design tokens (unused on homepage)
- `components/common/Section.js` — section wrapper

## Related
- [[nav-header-redesign]] — header accessibility patterns from 2026-05-19 redesign
- [[design-systems]] — token-based design system approach
- [[blog-seo-performance-2026-05-20]] — blog section optimization patterns