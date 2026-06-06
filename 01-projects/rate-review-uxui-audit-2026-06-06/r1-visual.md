# r1-visual — Visual Design & Typography Audit
**Specialist:** Visual Design & Typography
**Date:** 2026-06-06
**Reference:** `helpers/designSystem.js`
**Scope:** `/rate-review` flow — index, detail, submit-review pages + BookingReviewList, RateAndReviewForm components

---

## Summary

The rate-review flow has moderate design-token compliance but exhibits a cluster of recurring violations: star-rating colors are hardcoded instead of using the design system's status/warning token, `gap-0` on the page container collapses intended vertical rhythm, and the native `<input type="file">` creates a jarring visual break inside an otherwise MUI-consistent form. Typography hierarchy is largely correct but the heading on the index page is absent entirely, leaving the section titleless. The detail and submit-review pages are substantially better aligned with the design system than the list page.

---

## Design Token Violations

| Finding | Location | Hardcoded Value | Should Use |
|---------|----------|-----------------|------------|
| Filled star color | `RateAndReviewForm.js:133`, `BookingReviewList.js:68` | `#FFA000` | `COLORS.status.warning` (`#F59E0B`) |
| Empty star color (form) | `RateAndReviewForm.js:141` | `#D1D5DB` | `COLORS.neutral.gray300` (`#D1D5DB`) — value matches but bypasses token |
| Empty star color (list) | `BookingReviewList.js:68` | `#E5E7EB` | `COLORS.neutral.gray200` (`#E5E7EB`) — value matches but bypasses token |
| Back button brand color | `submit-review/[...slug].js:100` | `#3b5998` | `COLORS.brand.primary` |
| Back button hover bg | `submit-review/[...slug].js:101-103` | `rgba(59, 89, 152, 0.08)` (literal) | Derived from `COLORS.brand.primary` via CSS `alpha()` or named constant |
| Photo upload file button bg | `RateAndReviewForm.js:246` | Tailwind `file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100` | `COLORS.badge.primary.bg` / `COLORS.brand.secondary` |
| Loading spinner color | `submit-review/[...slug].js:82` | No `sx` color prop → MUI default blue | `COLORS.brand.primary` (as used correctly in `[reviewSlug].js:297`) |
| Index page gap-0 wrapper | `pages/rate-review/index.js:89` | `gap-0` | `SPACING.scale.xl` (`gap-6`) or at minimum `gap-3` (`SPACING.scale.md`) |
| List header margin | `BookingReviewList.js:77` | `p-2 mb-3` (arbitrary mix) | `CARD_CONFIG.padding` (`p-4`) + `SPACING.scale.md` (`gap-3`) — use flex gap instead of margin |
| Form container radius | `RateAndReviewForm.js:101` | `rounded-md` (Tailwind class) | `BORDER_RADIUS_CLASSES.container` (`rounded-md`) — value matches but should reference the token |

---

## Findings

### [VIS-01] Hardcoded Star Color — Design Token Divergence (Priority: P1)
- **What:** Both star rating implementations hardcode `#FFA000` (amber) for filled stars. This is not a registered design token. The closest token is `COLORS.status.warning` = `#F59E0B`. The two values are visually similar but the system will drift if warning color is ever updated.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:133` and `components/review/BookingReviewList.js:68`
- **Expected (design system):** `COLORS.status.warning` (`#F59E0B`) for a star that communicates positive sentiment, or register a dedicated `COLORS.rating.filled` token.
- **Actual (code):** `color: '#FFA000'` as an inline string literal in both components independently.
- **Recommendation:** Either (a) add `COLORS.rating = { filled: '#FFA000', empty: COLORS.neutral.gray200 }` to `designSystem.js` to make the intent explicit, or (b) map to `COLORS.status.warning`. Update both files to reference the token. This is currently duplicated across two unrelated components — a future palette change will miss one of them.

---

### [VIS-02] `gap-0` Page Container Collapses Vertical Rhythm (Priority: P1)
- **What:** The `<div className="flex flex-col gap-0">` wrapper around `<BookingReviewList>` on the index page sets zero gap between the breadcrumb section and the card grid. This eliminates the breathing room between the navigation element and the content area.
- **Where:** `pages/rate-review/index.js:89`
- **Expected (design system):** The breadcrumb sits in a sibling `div` outside this wrapper, so the `gap-0` has no real gap to collapse between siblings here — but the outer `<section>` is still a `flex flex-col` with no gap. Compare to how `[reviewSlug].js` uses `gap-4` on its equivalent outer wrapper (line 321). The index page is inconsistent.
- **Actual (code):** `flex flex-col gap-0` — explicit zero gap.
- **Recommendation:** Change to `flex flex-col gap-4` to match the detail page, or remove the wrapper div entirely since it wraps only one child (`BookingReviewList`).

---

### [VIS-03] Hardcoded Brand Color on Back Button in submit-review Page (Priority: P1)
- **What:** The `IconButton` on the submit-review page hard-codes `color: '#3b5998'` instead of using `COLORS.brand.primary`. The review detail page (`[reviewSlug].js:332`) correctly uses `COLORS.brand.primary`. The two pages should be visually identical but will diverge if the brand primary changes.
- **Where:** `pages/rate-review/submit-review/[...slug].js:100`
- **Expected (design system):** `COLORS.brand.primary`
- **Actual (code):** `color: '#3b5998'`
- **Recommendation:** Replace `'#3b5998'` with `COLORS.brand.primary` import. The `[reviewSlug].js` implementation is the correct reference pattern.

---

### [VIS-04] Native File Input — Visual Mismatch with MUI Form (Priority: P1)
- **What:** The photo upload field uses a raw HTML `<input type="file">` styled with Tailwind `file:` pseudo-class utilities. The rest of the form uses MUI `TextField` with consistent outlined variant styling. The native file input renders with browser-native chrome (OS-dependent appearance), a different font size rendering, and no match to the MUI input border-radius/border-color tokens.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:236-248`
- **Expected (design system):** `INPUT_CONFIG.base`, `INPUT_CONFIG.borderRadius` (`rounded-lg` / 8px), MUI-consistent appearance.
- **Actual (code):** Native `<input type="file">` with Tailwind `file:bg-blue-50 file:text-blue-700` — the blue here is generic Tailwind, not `COLORS.brand.primary` (`#3b5998`) or `COLORS.badge.primary.bg` (`#DBEAFE`).
- **Recommendation:** Wrap the file input in a styled MUI `Button` component (variant="outlined") that triggers the hidden input via `ref`. This makes the upload trigger visually indistinguishable from the rest of the MUI form. The hidden input can retain the `accept` and `multiple` attributes. Alternatively, use MUI's `Button` component as the visible label with `component="label"`.

---

### [VIS-05] Missing Page Title / Section Heading on Index Page (Priority: P2)
- **What:** The `/rate-review` index page renders a breadcrumb and immediately the card grid — there is no `<h1>` or `<h2>` page title visible to the user. The `BookingReviewList` renders "Rate & Review" in a `Typography` inside the header row (line 78), but this is styled as `text-lg text-gray-600 font-semibold` — far below the `TYPOGRAPHY_SCALE.h1` level.
- **Where:** `pages/rate-review/index.js` (no heading at all) and `BookingReviewList.js:78`
- **Expected (design system):** `TYPOGRAPHY_SCALE.h1` = `text-2xl sm:text-3xl md:text-4xl` for primary page heading. The submit-review and detail pages both have correct `<h1>` elements.
- **Actual (code):** No `<h1>` on index page. The list header Typography is `text-lg` only.
- **Recommendation:** Add an `<h1>` with `TYPOGRAPHY_SCALE.h1` + `FONT_WEIGHTS.bold` to the index page between the breadcrumb and the section wrapper. The existing "Rate & Review" label in `BookingReviewList` should be demoted to a visual header label (not the page's semantic h1), or removed if the page-level h1 is added.

---

### [VIS-06] Star Size 44px — Too Large for Card Context (Priority: P2)
- **What:** The interactive star icons in `RateAndReviewForm` are rendered at `fontSize: 44` (44px). The MUI default large star is 35px; 44px pushes each star to the WCAG touch-target minimum size, which is appropriate for the button (`minHeight/minWidth: 44px` on the `IconButton` wrapper). However, the visual star icon itself at 44px creates a disproportionately large rating widget relative to the 16px body text fields surrounding it.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:132`, `139`
- **Expected (design system):** No explicit icon-size token. However, the card-level `renderStars` in `BookingReviewList` uses `fontSize: 16px` for display-only stars — a 2.75x size ratio between interactive and display contexts.
- **Actual (code):** `fontSize: 44` for form stars vs `fontSize: '16px'` for card summary stars.
- **Recommendation:** Reduce form star icon to `fontSize: 36` — this preserves the 44px touch-target at the `IconButton` wrapper level (via `minHeight/minWidth: 44px`) while keeping the star visually proportionate. The icon inside the button does not need to fill the entire touch target.

---

### [VIS-07] Loading Spinner Missing Brand Color on submit-review Page (Priority: P2)
- **What:** The full-page `CircularProgress` on `submit-review/[...slug].js:82` has no `sx` color override, so it renders in MUI's default primary color (typically MUI blue `#1976D2`), not in `COLORS.brand.primary` (`#3b5998`). The review detail page (`[reviewSlug].js:297`) correctly applies `sx={{ color: COLORS.brand.primary }}`.
- **Where:** `pages/rate-review/submit-review/[...slug].js:82`
- **Expected (design system):** `COLORS.brand.primary`
- **Actual (code):** `<CircularProgress />` — no color override.
- **Recommendation:** Add `sx={{ color: COLORS.brand.primary }}` to match the pattern in the detail page.

---

### [VIS-08] EmptyState variant="completed" — Semantic Mismatch (Priority: P2)
- **What:** The `completed` variant in `EmptyState` uses a `CheckCircleOutlineIcon` and default title "Nothing here yet" — conceptually appropriate for a completed/archived list. But in the review context it implies the user has completed all reviews when in fact they have zero bookings eligible for review. The icon (green checkmark) sends a false positive signal.
- **Where:** `components/review/BookingReviewList.js:54` — `<EmptyState variant="completed" title="No reviews yet" message="Complete a booking to leave your first review." />`
- **Expected (design system):** `variant="first-use"` maps to `LuggageIcon` with "Start exploring" framing — more appropriate for a user who has no reviewable bookings yet.
- **Actual (code):** `variant="completed"` with `CheckCircleOutlineIcon` (implies success state).
- **Recommendation:** Switch to `variant="first-use"` or `variant="no-results"`. The overridden `title` and `message` text are already correct — only the variant (and therefore the icon) needs to change.

---

### [VIS-09] ListSkeleton Layout Mismatch — Column vs Grid (Priority: P2)
- **What:** `ListSkeleton` renders cards in a single vertical flex column (`flexDirection: 'column'`, gap: 2). The actual `BookingReviewList` renders a 3-column responsive grid (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3`). The skeleton therefore looks like a different layout than the content it's replacing, causing a jarring shift when data loads.
- **Where:** `pages/rate-review/index.js:75-79` calls `<ListSkeleton count={3} />`, which renders from `components/UI/states/ListSkeleton.js:36`
- **Expected (design system):** Skeleton should match the loaded layout — a 3-column grid on desktop.
- **Actual (code):** `sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}` — always single column.
- **Recommendation:** Pass a `columns` prop to `ListSkeleton` or create a `gridVariant` that renders `display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))'` to approximate the loaded grid layout.

---

### [VIS-10] Action Button Hover Color — Tailwind Utility vs Design Token (Priority: P2)
- **What:** The "Write Review" primary button in `BookingReviewList` uses `hover:bg-blue-600` as its hover state (Tailwind generic blue, #2563EB). The design system defines `COLORS.brand.secondary: '#2563eb'` and `BUTTON_CONFIG.primary.hover: 'hover:bg-brand-primary-dark'`. The token value matches by coincidence but the semantic is mismatched — hover on a primary button should darken the primary brand color, not switch to the secondary.
- **Where:** `components/review/BookingReviewList.js:181`
- **Expected (design system):** `BUTTON_CONFIG.primary.hover` = `hover:bg-brand-primary-dark` (resolves to `COLORS.brand.primaryDark` = `#2d4373`)
- **Actual (code):** `hover:bg-blue-600` = `#2563EB` (Tailwind default, which coincidentally equals `COLORS.brand.secondary`, not `primaryDark`)
- **Recommendation:** Replace `hover:bg-blue-600` with `hover:bg-brand-primary-dark` to align with `BUTTON_CONFIG.primary.hover`. Alternatively, use `getButtonClasses('primary')` from the design system utility function to generate the full correct class string.

---

### [VIS-11] Dead Code — Commented-Out File is 136 Lines (Priority: P3)
- **What:** `pages/rate-review/[reviewSlug].js` contains 136 lines of commented-out legacy code (the original `ReviewDetail` implementation) before the active export. This is not a visual bug but directly impacts visual code review legibility and carries hardcoded values (`text-sm md:text-2xl lg:text-lg` inconsistency, direct `axios` + `serReview` typo) that could be mistakenly referenced.
- **Where:** `pages/rate-review/[reviewSlug].js:1-136`
- **Recommendation:** Delete lines 1–136 (entire commented block). The active implementation starting at line 138 is complete and correct.

---

### [VIS-12] Duplicated `return normalized` Statement (Priority: P3)
- **What:** `normalizeReviewForSummary()` in `[reviewSlug].js` has two consecutive `return normalized` statements — an unreachable dead statement at line 233 followed by the active one at line 235. Technically harmless but signals copy-paste debt.
- **Where:** `pages/rate-review/[reviewSlug].js:233-235`
- **Recommendation:** Remove the first `return normalized` (line 233). Keep only line 235.

---

### [VIS-13] Typography — `text-fb-blue` Class on Sort Button (Priority: P3)
- **What:** The sort toggle button in `BookingReviewList` uses `text-fb-blue` (a custom Tailwind utility class mapped to `COLORS.brand.primary`). This is the correct approach — using the design-system-aligned Tailwind alias rather than a hardcoded hex. However, it is inconsistent with how the same color is applied elsewhere in the same file via `COLORS.brand.primary` in MUI `sx` props. The pattern should be consistent: either always use the Tailwind alias in Tailwind contexts (correct), or always import from `COLORS` even for Tailwind classes (wrong, can't do that). Current usage is actually correct for Tailwind — flagging only for documentation.
- **Where:** `components/review/BookingReviewList.js:82`
- **Recommendation:** No code change needed. Document in team conventions: "Tailwind contexts use `text-fb-blue` / `bg-fb-blue`; MUI `sx` contexts use `COLORS.brand.primary`."

---

## Typography Hierarchy Assessment

| Element | Component | Current | Expected (TYPOGRAPHY_SCALE) | Status |
|---------|-----------|---------|------------------------------|--------|
| Page title | `index.js` | None | `TYPOGRAPHY_SCALE.h1` (`text-2xl sm:text-3xl md:text-4xl`) | MISSING |
| Section label "Rate & Review" | `BookingReviewList.js:78` | `text-lg font-semibold` | Acceptable as list header (h2-level visual), but not using scale token | PARTIAL |
| Page title | `submit-review/[...slug].js:111` | `text-xl sm:text-2xl md:text-3xl font-bold` | `TYPOGRAPHY_SCALE.h1` matches responsive values | COMPLIANT |
| Page title | `[reviewSlug].js:342` | `text-xl sm:text-2xl md:text-3xl font-bold` | `TYPOGRAPHY_SCALE.h1` matches responsive values | COMPLIANT |
| Sub-label (booking slug) | Both page files | `text-sm sm:text-base` | `TYPOGRAPHY_SCALE.body` = `text-sm sm:text-base` | COMPLIANT |
| Review title | `[reviewSlug].js:440` | `text-2xl font-bold` | `TYPOGRAPHY_SCALE.h2` = `text-xl sm:text-2xl` — one step too large at base | MINOR DEVIATION |
| Review body text | `[reviewSlug].js:453` | `text-base leading-relaxed` | `TYPOGRAPHY_SCALE.body` (`text-sm sm:text-base`) | CLOSE — misses `text-sm` on mobile |
| Card booking slug | `BookingReviewList.js:106` | `font-semibold text-gray-900` | No explicit size token — inherits `text-sm` from parent context | ACCEPTABLE |
| Passenger count label | `BookingReviewList.js:153` | `text-sm text-gray-600` | `TYPOGRAPHY_SCALE.small` = `text-xs sm:text-sm` | MINOR — fixed size vs responsive |
| Rating label feedback | `RateAndReviewForm.js:151` | `text-sm font-medium` (Typography body2) | `TYPOGRAPHY_SCALE.small` appropriate for caption | ACCEPTABLE |
| Photo upload caption | `RateAndReviewForm.js:262` | MUI `variant="caption"` | `TYPOGRAPHY_SCALE.caption` = `text-xs` — equivalent | COMPLIANT |

---

## Color Compliance Score

**6/10 components using design tokens correctly.**

| Component | Token Compliance | Notes |
|-----------|-----------------|-------|
| `UnifiedCard.js` | 10/10 | Fully uses `getCardClasses()` — gold standard |
| `BadgeChip.js` | 10/10 | All colors from `COLORS` tokens |
| `EmptyState.js` | 9/10 | Minor: MUI sx uses raw number spacing instead of SPACING tokens |
| `ListSkeleton.js` | 8/10 | Uses BORDER_RADIUS tokens correctly; layout mismatch vs loaded grid |
| `[reviewSlug].js` | 8/10 | Good: imports and uses COLORS; Minor: no `TYPOGRAPHY_SCALE` for review title size |
| `RateAndReviewForm.js` | 6/10 | Stars hardcoded; file input uses generic Tailwind blue; form radius uses token string |
| `BookingReviewList.js` | 5/10 | Stars hardcoded; hover color wrong token; empty stars bypass token |
| `submit-review/[...slug].js` | 5/10 | Back button color hardcoded; spinner missing brand color |
| `pages/rate-review/index.js` | 4/10 | `gap-0` bug; no page heading; SEO canonical missing `www` |
| `pages/rate-review/[reviewSlug].js` | 7/10 | Dead commented code; duplicate return; otherwise clean |

---

## Top 3 Quick Wins

1. **Register `COLORS.rating` tokens and fix star colors in both components** — Single design-system change (`helpers/designSystem.js`) + 2-line fix each in `RateAndReviewForm.js` and `BookingReviewList.js`. Eliminates the largest class of violations (token bypass) and future-proofs the amber palette across all star ratings.

2. **Fix `gap-0` to `gap-4` on index page wrapper and add `<h1>` page heading** — Two one-line changes in `pages/rate-review/index.js`. Restores vertical rhythm immediately visible on page load and adds the missing semantic heading required for accessibility and SEO.

3. **Replace native file input with MUI Button-as-label pattern in `RateAndReviewForm.js`** — Single component change (~10 lines). Eliminates the most jarring visual inconsistency in the form (OS-native file picker button vs. MUI design) and brings photo upload into line with `INPUT_CONFIG` border-radius and brand color tokens.
