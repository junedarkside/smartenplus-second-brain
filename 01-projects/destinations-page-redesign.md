# /destinations Page Redesign — 2026-07-18

## Summary
Full visual redesign of `/destinations` index page via 3-agent team (design-review auditor → designer w/ platform research → react-specialist implementer). Image-forward cards, intent-driven H1, full a11y pass. Branch `feat/destinations-page-redesign` commit `943deb7d` — pending user approval to merge → develop.

## Context
Page = station browser ("go TO a station, book trip" — see [[locations-destinations-product-split]], never merge with /locations). Pre-redesign: letter-avatar text cards, `location.image` API field (33/54 locations) unused, token drift, 2 a11y P0s.

## Audit Scores (before)
Visual Hierarchy 6 · Booking Intent 4 · Info Density 7 · **Imagery 2** · CTA 5 · Mobile 7 · A11y 5 · **Token Compliance 4**. Grid audited from code — local dev backend returned 0 locations (empty ISR page), hero/filters/empty-state audited live via Playwright.

Key findings: P0 search input unlabeled; P0 expand toggle no `aria-expanded` + `focus:outline-none` killed focus ring; P1 H1 "Thailand All Destinations" no booking intent; P1 EmptyState rendered `Your search for ""` on empty data; P1 `location.image` unused; P1 back button 36px < 44px; P1 `console.log` in handler; P2 invalid `text-md` class on CTA, StatsDisplay dots 3.98:1 contrast fail, SearchBar bypassed `getInputClasses()`.

## Platform Research (designer)
12Go: image top + price anchor + booking CTA. Booking.com: bottom linear-gradient for text-over-any-image. GYG: full-bleed image, name overlaid on gradient. Klook: 50/50 + descriptor. Omio station index: hierarchical text list (utility). Direct fetches mostly 403 (bot-blocked) — verified via 12Go mirror + extractions + [[destinations-redesign-review]] 2026-05 priors.
**Synthesis:** hybrid = GYG/Booking image-overlay card (identity) + Omio text station list (utility) + explicit booking CTA. No carousel — browse-all index, not teaser.

## Decisions
- **H1:** `Where in Thailand Do You Want to Go?` + sub-line "Find your station and book your trip" — go-TO intent, differentiates from /locations. SEO title untouched (useStructuredData independent of H1 — verified).
- **Card:** `<article>` + `h-40` image region (`location.image || DEFAULT_ROUTE_IMAGE`, blur placeholder) + name/province overlaid on `bg-gradient-to-t from-black/60 via-black/25 to-transparent` (bottom gradient, NOT flat `bg-black/25` — flat fails 4.5:1 on light images). Hover scales image only inside `overflow-hidden` (no layout wobble). Count moved to overlay caption + `aria-label`. Dropped MUI Card, letter-avatar, GroupOutlinedIcon.
- **Tokens:** CTA via `getButtonClasses('primary')`, input via `getInputClasses()`, `rounded-xl` = imageCard token, 44px = TOUCH_TARGET. Flagged missing tokens kept as commented one-offs (single consumer, YAGNI): overlay gradient, `h-40` media height, `text-white/90`.
- **DEFAULT_ROUTE_IMAGE:** local const in LocationCard (3rd duplicate w/ LocationGridComponent + BookYourTripWidget — consolidation deferred, 3 lines < premature helper).
- **EmptyState:** branch on `searchTerm.trim()` — no-match (w/ Clear button) vs no-data "Destinations Temporarily Unavailable" (no button).

## File Map
`pages/destinations/index.js` (H1, back button 44px, console.log) · `components/destinations/{LocationCard,SearchBar,StatsDisplay,FilterControls,EmptyState}.js`. All <200 lines, no new deps, no useEffect additions. **NOT touched:** `LocationGridComponent.js` (pattern source, used by /locations + homepage), `FeaturedImageHeader`, hooks, helpers.

## Verification
`npm run build` clean · lint clean on 6 files · live HTML checks pass (new H1, sub-line, no-data empty state, JSON-LD present, sr-only label, old H1 gone) · S3 image host confirmed in next.config remotePatterns · SEO title decoupling confirmed. **Gap:** grid/card interactions (search, filter, expand, CTA route) untested live — local backend had 0 locations; test post-deploy or with backend up.

## Tradeoffs
- Fixed `h-40` image region = uniform rows, simple; loses asymmetric editorial hierarchy of homepage grid (fine — this is utility browse, not teaser).
- 21/54 locations use shared fallback image — repeated imagery until backend fills `image`.
- Empty-quote copy fixed frontend-side; root cause of empty local data = dev backend down, unrelated.

## Follow-up: CTA Alignment Fix (2026-07-18)
User screenshot showed Book CTA floating mid-card on short station lists (grid rows stretch equal-height, button sat after list). Fix commit `6d89c875`: `<article>` → `flex flex-col h-full`, body → `flex flex-col flex-1`, CTA → `mt-auto`. Buttons now share baseline per row.

## Mobile Design Debate (2026-07-18) — Verdict: YES-WITH-FIXES
Adversarial 2-agent debate (design-review `mobile-critic` w/ Playwright at 390/360/768 vs `design-advocate` w/ code verification), orchestrator judged. Question: is redesign best mobile design yet?

**Critic (NO):** ~21k px scroll at prod 54 cards with no sticky search/wayfinding (search gone after 600px scroll); 71% cards repeat default-route.webp; 407px chrome above first card (48% of 390×844 viewport); StatsDisplay overflows 200px mobile hero by ~40px; `alt=""` on real photos; 54 identical CTAs; tablet 248px dead whitespace; MUI selects 96% width saturation at 360px.

**Advocate rebuttals that held (judge-accepted):**
- 71% fallback = dev-DB skew (5/7 dev); prod = 39% (21/54). Content-ops gap (upload photos), not design flaw. `image || DEFAULT` correct pattern.
- `alt=""` CORRECT per W3C adjacent-text pattern — name announced via overlay `<h3>` + article `aria-label`; non-empty alt would double-announce.
- "No alternative affordance" false — every StationItem is real Link (3-5 nav targets/card).
- FilterControls full-height containment claim contradicted by code (normal-flow div) — DevTools artifact.
- Tablet equal-height + pinned CTA = deliberate pattern user explicitly requested (CTA alignment fix same day). Keep.
- Long scroll platform-normal (Booking/GYG mobile lists); missing piece = persistent tool access, not pagination.

**Concessions — IMPLEMENTED `24c92257`:**
1. **P0 — sticky FilterControls:** `sticky top-0 md:top-20 z-20` (mobile AppBar is relative+Slide → top-0; desktop fixed header → top-20 per STICKY_CONFIG). Filter/sort/search persist mid-scroll.
2. **P1 — mobile SearchBar moved hero → sticky bar** via new `children` slot on FilterControls (`w-full sm:hidden` instance); hero search now `hidden sm:block`; SearchBar got `id` prop (default `destinations-search`) to avoid duplicate DOM ids.
3. **P1 — responsive MUI select widths:** `minWidth: {xs:120, sm:160}` / `{xs:132, sm:180}` (was 160+180+paddings = 388px > 360px viewport).
4. **Judge simplification:** planned `customMinHeight` hero fix DROPPED — removing search from mobile hero shrinks content (~136px) below the 200px hero boundary, resolving StatsDisplay overflow without touching FeaturedImageHeader.

**Deferred:** fallback image variety (content-ops ticket — upload 21 location photos), multi-expand accordion Set (measure viewport shift first), ShareButton popover overlap (re-check after hero fix), router.back() on SEO entry (site-wide pattern).

**Judge rationale:** core design (GYG/Booking overlay card + Omio station list + booking CTA) survives; genuine failures narrow — ~4 class/prop-level diffs across 2 files, inside no-overengineering regime.

## Follow-up: Sitewide Touch-Target Fix (2026-07-18)
Commit `1e4f2f46` — hero pill buttons 36px→44px across 16 non-destinations files (ShareButton, DayTripHero, AirportTransferHeader, BlogPageWrapper, SearchCover, TripDetailHero, FeaturedImageHeaderSkeleton + 9 pages: airport-transfer, forum, help, locations×2, operators, rate-review×2, trips). Generalizes the P1 back-button finding (44px = TOUCH_TARGET token) sitewide. +1/-1 per file, no behavior change. Shipped on same branch — merged to develop with redesign.

## Related
[[destinations-redesign-review]] · [[locations-destinations-product-split]] · [[design-system-audit]]
