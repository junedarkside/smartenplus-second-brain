# Homepage UX/UI Audit — SmartEnPlus

**COMPLETED 2026-05-31.** 6-phase audit by team. Scrutinized and corrected 2026-05-31.
**IMPLEMENTED 2026-05-31.** Commit `ade94ee` on `260528-feat/header-redesign-2026`.

---

## What Should Remain Unchanged

- **Search Hero (DiscoverySection)** — clean, focused, right intent placement. No changes needed.
- **Popular Routes carousel** — solid UX pattern. From→to, price, operators all present.
- **Reviews section** — appropriate social proof strip. Correct placement near other trust signals.
- **Footer** — no issues flagged.
- **Section wrapper structure** — `max-w-[1200px] mx-auto` pattern is correct. Keep.

---

## High-Priority Fixes

### 1. Destinations → Station Directory, Not Routes (Destination Section)
**Issue:** Clicking a destination card sends users to `/locations/[slug]` — a station directory. Users see A-Z station lists. The destination page has a search autocomplete in the hero (not a dead-end), but lacks a prominent labeled CTA button ("Search buses to {destination}") above the fold.

**Fix:** Add `?from=bangkok` query param to destination card links — pre-populates search on the destination page with Bangkok as origin. Also add a visible "Search buses to {destination}" shortcut button in the hero above the autocomplete.

**Files:** `lib/homepage/components/LocationsSection.js`, `pages/locations/[slug].js`

**Priority: HIGH** — destination-aware users lose context when landing on station directory.

---

### 2. MyBookingsSection Is Buried (Conversion Flow)
**Issue:** Returning users with existing bookings must scroll past 5 sections to reach "Check Your Booking." Highest-intent entry point on the page, placed last.

**Fix:** Add a persistent compact strip directly below the search hero (sticky or static). This gives immediate access for users who already have a booking without full section reorder.

**Files:** `pages/homepagev2.js`, `components/FrontPage/MyBookingsSection.js`

**Priority: HIGH** — affects returning user conversion directly.

---

### 3. Popular Routes Cards Lack Transport Type Badge (Card Differentiation)
**Issue:** PopularRouteImageCard and ExperienceCard are nearly structurally identical (same border-radius `rounded-xl`, shadow, dimensions, typography, price format). Users cannot instantly distinguish transport from activity.

**Fix:** Add transport type badge to PopularRouteImageCard — copy the category badge pattern from ExperienceCard (`text-xs text-gray-500 bg-gray-100 rounded px-2 py-0.5`). Derive label from `item.transport_type`. Also change border-radius from `rounded-xl` (12px) to `rounded-lg` (8px) to subtly differentiate.

**Files:** `components/UI/PopularRouteImageCard.js`

**Priority: HIGH** — scanability and intent clarity.

---

### 4. LocationsSection Has Double-Layer Horizontal Spacing (Layout)
**Issue:** LocationsSection uses `px-0` on Section wrapper but inner div uses `mx-2 md:mx-3 xl:mx-0` — inconsistent with all other sections which use `px-4 xl:px-0` uniformly.

**Fix:** Change Section className from `py-6 px-0` to `py-6 px-4 xl:px-0`. Remove inner div `mx-` margins. Align with other sections.

**Files:** `lib/homepage/components/LocationsSection.js` (line 58)

**Priority: HIGH** — layout inconsistency visible on desktop.

---

## Medium-Priority Fixes

### 5. Section Wrapper Gap Too Tight for Card Carousels
**Issue:** `gap-2` on Section wrapper is too tight for sections with card carousels (PopularRoutes, ExploreExperiences, Reviews). Cards feel cramped vertically.

**Fix:** Use `gap-3` for sections with card carousels. Keep `gap-2` for non-carousel sections (TravelThailandBetter, Locations).

**Files:** `components/common/Section.js` — add gap prop, override in specific section components.

---

### 6. MyBookingsSection Double-Layer Margin Conflict (Layout)
**Issue:** Same double-layer margin issue as LocationsSection — Section uses `px-4` but inner card uses `mx-2 md:mx-3 xl:mx-0`. At xl, card bleeds to edge while section constrains it.

**Fix:** Remove card `mx-` margins. Let card be full-width within Section `px-4` container.

**Files:** `components/FrontPage/MyBookingsSection.js` (line 20)

**Priority: MEDIUM** — consistency issue.

---

### 7. TravelThailandBetterSection Internal Gap Conflict (Layout)
**Issue:** Section wrapper uses `gap-2` but internal layout uses `gap-4` — conflicting vertical rhythm. Results in 16px internal gap but only 8px between grid and SectionHeader.

**Fix:** Use `gap-3` on Section wrapper for this section, or remove internal `gap-4` override.

**Files:** `lib/homepage/components/TravelThailandBetterSection.js`

**Priority: MEDIUM** — vertical rhythm issue.

---

### 8. Experiences Section Competes With Booking Intent (Conversion Flow)
**Issue:** After search hero, the next visible content is Experiences (tours/activities) — a completely different product category. Creates context switch right after primary booking action.

**Fix:** Add sub-label to ExploreExperiencesSection header — "Tours & Activities" — to visually differentiate from transport. Alternatively, ensure PopularRoutesSection is more visually prominent on mobile.

**Files:** `lib/homepage/components/ExploreExperiencesSection.js`

**Priority: MEDIUM** — category confusion for new users.

---

### 9. SectionHeader pt-2 pl-2 Feels Cramped (Layout)
**Issue:** SectionHeader internal padding (`pt-2 pl-2`) is tight.

**Fix:** Change to `pt-3 pl-2` for slightly more breathing room.

**Files:** `components/common/SectionHeader.js` (line 6)

**Priority: LOW-MEDIUM** — quick win.

---

## Low-Priority Polish

### 10. ExperienceCard Missing Duration Indicator
**Issue:** ExperienceCard has no duration hint (day tour vs multi-day). Duration is inherent to experience products.

**Fix:** Add duration text below category badge (`text-xs text-gray-500` with clock icon).

**Files:** `components/UI/ExperienceCard.js`

**Priority: LOW** — improves experience product scanability.

---

### 11. Reviews Before Guides — Design Preference (Conversion Flow)
**Issue:** Reviews appear before Travel Thailand Better (editorial). One conversion model says editorial should precede reviews (authority before trust). Another model says reviews first build immediate trust.

**Note:** This is a design preference, not a correctness issue. Both orderings are valid. No broken behavior.

**Fix:** Optional. Consider swapping for improved trust-building for new visitors. Not urgent.

**Files:** `pages/homepagev2.js`

**Priority: LOW** — design preference, not a bug.

---

## Strategic Observations (Not Actionable Fixes)

### Marketplace Orientation
SmartEnPlus mixes transport + activities + editorial content. Competitors that succeed specialize (Omio = transport only, GetYourGuide = activities only). SmartEnPlus is 5 things at once.

**Recommendation:** Do NOT add more marketplace sections. Consider moving Travel Thailand Better below Locations or to a separate `/guides` page. De-emphasize, don't expand.

---

## Items to Remove

Nothing. All current sections serve a purpose. No sections should be removed.

---

## Items to NOT Add

- Car rentals, hotels, flights sections
- More content/blog sections
- Complex search form enhancements
- Additional marketplace categories
- Destination directory pages (SEO-style lists)

---

## Summary

| Priority | Count | Key Issues |
|----------|-------|------------|
| **High** | 4 | Destinations link to station dir, MyBookings buried, card badge missing, Locations spacing |
| **Medium** | 4 | Section gap, MyBookings margin, TravelThailand gap, Experiences label |
| **Low** | 3 | SectionHeader padding, ExperienceCard duration, Reviews/Guides order |

**Total actionable fixes: 11**

**Corrections from scrutinize:**
- Finding 1 (destinations): Corrected — page has search, not a dead-end. Gap is missing labeled CTA button.
- Finding 6 (Reviews/Guides order): Demoted to LOW — design preference, not a bug.
- Finding 9 (destination page dead-end): Merged into Finding 1.
- Finding 13 (marketplace): Moved to Strategic Observations.

Report is structurally sound. Homepage main issues: (1) destination section links to wrong page type, (2) MyBookings too buried, (3) Popular Routes and Experience cards look too similar, (4) spacing inconsistencies in Locations and MyBookings.

Enough is enough. Prefer removing complexity over adding complexity.
