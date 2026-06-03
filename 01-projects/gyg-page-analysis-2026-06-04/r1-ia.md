---
name: r1-ia
description: Specialist A — Information Architect. Section-by-section diff of GYG Chiang Rai tour (22 sections) vs SmartEnPlus activity detail page. Classification: already-have / missing-candidate / skip-backend-debt / skip-off-brand / skip-deferred.
metadata:
  type: specialist-r1
  role: information-architect
  page: gyg-846675-chiang-rai
  smartenplus_route: /activities/detail/[...slug]
  source_note: WebFetch unavailable, text dump used
---

# R1 — Information Architect

**Goal:** map every GYG section to SmartEnPlus current state. No silent drops.

**Scope:** incremental gap analysis (vs 2026-06-02 redesign doc). Skip patterns already in redesign spec.

**Source:** GYG text dump (Chiang Rai tour, product 846675). 22 distinct sections in order. WebFetch unavailable this session.

---

## SmartEnPlus Current Sections (count: 14)

Recon summary from `components/activities/detail/DayTripDetailPage.js` (2-col grid `xl:grid-cols-[1fr_380px]`):

| # | Section | Component | Notes |
|---|---------|-----------|-------|
| SP-1 | Photo grid (full-bleed) | `AirbnbPhotoGrid.js` | NEW 2026-06-02 redesign |
| SP-2 | Title + breadcrumb + rating + trust badges | `ExperienceTitleArea.js` | NEW 2026-06-02 redesign |
| SP-3 | Highlights (icon cards) | `ExperienceHighlights.js` | NEW 2026-06-02 redesign |
| SP-4 | Why travelers love (5 selling cards) | `WhyTravelersLove.js` | NEW 2026-06-02 redesign |
| SP-5 | Reviews (moved up before itinerary) | `ReviewListByProduct.js` | NEW 2026-06-02 redesign |
| SP-6 | Itinerary timeline (collapsed accordion) | `TimeLineDisplay.js` | NEW 2026-06-02 redesign |
| SP-7 | Inclusions/exclusions 2-col | `IncludedExcluded.js` | NEW 2026-06-02 redesign |
| SP-8 | Meeting point card | `MeetingPointCard.js` | NEW 2026-06-02 redesign |
| SP-9 | FAQ accordion | `ExperienceFAQ.js` | NEW 2026-06-02 redesign |
| SP-10 | Related experiences (3-4 cards) | `RelatedExperiences.js` | NEW 2026-06-02 redesign |
| SP-11 | SEO JSON-LD | `DayTripDetailSEO.js` | existing |
| SP-12 | Desktop sticky right-rail booking | `PremiumBookingPanel.js` | NEW 2026-06-02 redesign |
| SP-13 | Mobile fixed bottom booking bar | `DayTripMobileBookingBar.js` | existing |
| SP-14 | Date/people/book widget | `DayTripBookingWidget.js` | existing, wrapped |

**SmartEnPlus sections GYG does NOT have** (operator-specific, invention):

- "Why travelers love" 5-card grid (SP-4) — SmartEnPlus invention, not in GYG
- Premium glassmorphism sticky booking panel (SP-12) — wraps existing widget
- "What to bring" rendered in FAQ accordion (SP-9) — SmartEnPlus chose accordion over GYG chip

---

## GYG Section Diff (22 GYG sections)

Status legend:
- `already-have` = SmartEnPlus implements (likely in 2026-06-02 redesign or earlier)
- `missing-candidate` = potential adoption this round
- `skip-backend-debt` = needs new backend field (auto-defer P3)
- `skip-off-brand` = conflicts with SmartEnPlus premium-calm feel
- `skip-deferred` = AI summary only, user-deferred

| GYG # | GYG Section | SmartEnPlus Current | Status | Notes |
|-------|-------------|--------------------|---------|-------|
| 1 | Breadcrumb (Explore Chiang Rai > Places to see > Things to do) | `StandardBreadcrumb` in `ExperienceTitleArea` (SP-2) | already-have | Standard breadcrumb pattern. Implemented. |
| 2 | Title h1 | `ExperienceTitleArea` h1 (SP-2) | already-have | `translated_name\|\|name`. Implemented. |
| 3 | "Top rated" badge | `ExperienceTitleArea` "Top Rated" badge if rating>=4.5 && reviews>=10 (SP-2) | already-have | Conditional render. Implemented. |
| 4 | 4.8 stars + 6,940 reviews + provider | `AverageRating` + `AverageReview` + operator name (SP-2) | already-have | Standard. Implemented. |
| 5 | Action row: Wishlist + Share | Wishlist in `BookmarkButton` (existing); Share — NOT IMPLEMENTED | already-have (partial) | Wishlist only. Share is separate concern. |
| 6 | Photo gallery (5 thumbs + "View all") | `AirbnbPhotoGrid` 5-up grid (SP-1) | already-have | Implemented in 2026-06-02 redesign. |
| 7 | About chips (Free cancellation / Reserve now / Duration / Live guide / Audio guide / Pickup / Private group / Popular with couples) | `ExperienceTitleArea` trust badges from `contract.extra` (SP-2) | already-have (partial) | Most chips implemented dynamically. **Missing: "Popular with couples and solo travelers" segment signal.** Audio guide 41 langs = skip-backend-debt. Private group badge = skip-backend-debt. |
| 8 | What travelers loved (5 recent 5-star) | NOT IMPLEMENTED — design choice: SmartEnPlus shows all reviews (SP-5) | skip-off-brand | GYG cherry-picks 5-star = conversion bias, not editorial integrity. Off-brand. |
| 9 | "Read more" / "See more reviews" | Implicit in `ReviewListByProduct` "See more" pattern (SP-5) | already-have | Pattern exists. |
| 10 | Itinerary timeline (with Main stop / Other stop legend + "For reference only" disclaimer) | `TimeLineDisplay` collapsed (SP-6) | already-have (partial) | Timeline exists. **Missing: stop-type legend + "For reference only" disclaimer.** |
| 11 | Highlights (5 bullets) | `ExperienceHighlights` icon cards (SP-3) | already-have | Implemented. |
| 12 | Full description (multi-paragraph) | `AboutThisExperience` inline (SP-rewrite) | already-have | Implemented. |
| 13 | Includes (bullet list) + optional add-ons (Lunch, Luggage +290 THB) | `IncludedExcluded` inclusions (SP-7) | already-have (partial) | Includes exist. **Missing: optional add-on with surcharge label** (Long Neck 300 THB, Luggage 290 THB). Backend may not surface add-on pricing. |
| 14 | Not suitable for (mobility) | NOT IMPLEMENTED | missing-candidate | NEW GYG pattern. "Not suitable for" badge. Possible via `difficulty_level` or new `restrictions` field. |
| 15 | Meeting point (human-readable + "Open in Google Maps") | `MeetingPointCard` human-readable (SP-8) | already-have (partial) | Card exists. **Missing: "Open in Google Maps" deep link** — 1-line addition. |
| 16 | Important info: What to bring / Not allowed / Know before you go | `ExperienceFAQ` accordion (SP-9) renders "What to bring" as Q. Not-allowed + know-before missing. | already-have (partial) | What-to-bring in FAQ. **Missing: explicit "Not allowed" badges + "Know before you go" disclaimers** as distinct UI. |
| 17 | Price block (strikethrough old + current + Adult x 1 + Select date) | `PremiumBookingPanel` "From THB X" header (SP-12) | already-have (partial) | "From" price + date widget. **Missing: strikethrough old price (price anchor pattern).** |
| 18 | Trust strip (Free cancellation + Reserve now & pay later) | `PremiumBookingPanel` footer trust row (SP-12) | already-have | Trust badges rendered. |
| 19 | You might also like (4 cards) | `RelatedExperiences` 3-4 cards (SP-10) | already-have | Implemented. |
| 20 | Reviews header (Overall 4.8/5 + precise 4.7598 + 6,940 reviews) | `ReviewListByProduct` overall + count (SP-5) | already-have (partial) | Overall + count rendered. **Missing: AI-precise 4.7598 display** (deferred — AI-related, out of scope this round). |
| 21 | Review summary by sub-categories (Guide 4.8 / Transport 4.7 / Value 4.7) | NOT IMPLEMENTED | missing-candidate | NEW GYG pattern. Per-aspect ratings. Backend has `average_rating` only, no per-aspect. Skip-backend-debt. |
| 22 | AI-summarized review + attribution | NOT IMPLEMENTED | skip-deferred | User-deferred P3. |
| 23 | Sort by Recommended + Filter controls | NOT IMPLEMENTED on detail page | missing-candidate | NEW GYG pattern. Review sort/filter. Reasonable UX. |
| 24 | Review cards (avatar + name + country + date + Verified booking + body + thumbnail + provider response) | `ReviewListByProduct` renders name + body (SP-5) | already-have (partial) | Standard fields exist. **Missing: review thumbnail images, "Verified booking" badge, provider response section.** |
| 25 | "Was the information on this page helpful? Yes/No" | NOT IMPLEMENTED | missing-candidate | NEW GYG pattern. Page-level feedback widget. |
| 26 | Footer meta: Product ID + provider | NOT IMPLEMENTED on page | missing-candidate | Lightweight. SEO/audit utility. |
| 27 | Newsletter signup | OUT OF SCOPE (platform-wide) | skip-off-brand | Not page-specific. |
| 28 | SEO footer blocks (Top Attractions / Experiences / Tours / Things to do — 20-item lists) | NOT IMPLEMENTED on detail page | missing-candidate | NEW GYG pattern. Internal-link SEO + keyword density. |
| 29 | Country/region/depth footer breadcrumb (Thailand > Chiang Rai (Province) > Mae Kachan Hot Spring) | `StandardBreadcrumb` (SP-2) | already-have | Already renders. |
| 30 | Language/currency selector + payment methods | OUT OF SCOPE (global header/footer) | skip-off-brand | Not page-specific. |

**GYG sections counted: 22 distinct (per spec, mapped to 30 rows in my table for granularity).** Some are sub-sections of broader patterns (e.g. #7 chips = 8 chips, #28 = 4 SEO blocks).

---

## Classification Summary

| Status | Count | Items |
|--------|-------|-------|
| already-have | 12 | Breadcrumb, Title, Top-rated, Rating, Wishlist (partial), Photo grid, Highlights, Description, Includes (partial), Trust strip, Related, Reviews header |
| already-have (partial) | 8 | Action row, About chips, Timeline legend, Meeting point maps link, Important info, Price anchor, Review cards, Breadcrumb depth |
| missing-candidate | 6 | Not-suitable-for, Review sub-categories, Review sort/filter, Page feedback, Footer meta, SEO footer blocks |
| skip-backend-debt | 3 | Audio guide 41 langs, Private group badge, Review sub-categories (Guide/Transport/Value needs new backend field) |
| skip-off-brand | 3 | Cherry-picked 5-star reviews, Newsletter signup, Language/currency selector |
| skip-deferred | 1 | AI-summarized review |

---

## Net Diff: 6 missing-candidates

1. **Not-suitable-for badges** (GYG: "Not suitable for: People with mobility impairments")
2. **Per-aspect rating breakdown** (GYG: Guide 4.8 / Transport 4.7 / Value 4.7)
3. **Review sort + filter** (GYG: "Sort by Recommended | Filter")
4. **Page feedback widget** (GYG: "Was the information on this page helpful? Yes/No")
5. **Footer meta strip** (GYG: "Product ID: 846675, Activity provider: ...")
6. **SEO footer blocks** (GYG: 4 numbered 20-item lists — Top Attractions, Experiences, Tours, Things to do)

**P3 backend debt (auto-defer):** Audio guide 41 langs, Private group badge, Per-aspect ratings (Guide/Transport/Value needs `ReviewAspect` model or annotation).

**P3 user-deferred:** AI-summarized review.

---

## SmartEnPlus Inventions (no GYG equivalent)

- `WhyTravelersLove` 5-card grid (operator-friendly, not cherry-picked)
- Premium glassmorphism sticky booking panel
- Glassmorphism back/share pill overlay
- "What to bring" rendered as FAQ accordion item

These are SmartEnPlus-specific design choices, NOT gaps. Keep.

---

## Quality Check

- All 22 GYG sections accounted for: yes
- Silent drops: none
- Already-have classified correctly: cross-referenced 2026-06-02 redesign doc
- Backend debt flagged: yes (3 items)
- Out-of-scope items called out: yes (newsletter, lang/currency selector)

**Output:** 6 missing-candidates ready for R1-UX scoring.

---

## Related

- [[experience-detail-page-redesign-2026-06-02]] — predecessor doc, 9 components already implemented
- [[business-development-thailand-platform-analysis]] — GYG competitive positioning
- [[trip-detail-page-review-2026-05-20]] — prior detail page audit
