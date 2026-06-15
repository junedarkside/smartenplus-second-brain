# r3-leader-synthesis — Final Audit Synthesis
**Lead:** Architecture & UX
**Date:** 2026-06-06
**Source:** r1-ux + r1-visual + r1-frontend + r2-skeptic

---

## Executive Summary

The `/rate-review` flow covers three pages (`/rate-review`, `/rate-review/[reviewSlug]`, `/rate-review/submit-review/[token]`) and provides a token-gated review submission system backed by the `dialogue` app. A 4-specialist audit (UX, Visual, Frontend, Skeptic) produced 52 raw findings; after skeptic deduplication and triage, 34 unique actionable findings remain across 4 priority tiers. The most critical risk is a stored XSS vulnerability in the review detail page — `dangerouslySetInnerHTML` is used without DOMPurify on user-submitted text, despite the fix pattern already existing in three sibling components. A secondary P0 crash (`parseISO(null)`) can blank the entire Rate & Review page for any authenticated user when the API returns a booking with a null `traveling_date`. The flow's guest experience is effectively invisible — no interstitial, no loading guard — and the core "Write Review" navigation button uses the wrong Next.js router import, making it undefined behavior. Overall health score: **4.5/10** (functional under happy path, but fragile under error conditions and inaccessible to screen reader users).

---

## Auth State Assessment

### Logged-in user experience

The authenticated flow has a structurally complete happy path: booking list renders with Reviewed/Pending badges, the form loads booking context via `BookingSummaryCard`, and the detail page has a correct sticky sidebar layout. However, multiple friction points erode trust at key moments:

- **Core CTA may navigate incorrectly** (FE-14/UX-15 merged): `useRouter` imported from `next/navigation` (App Router) in a Pages Router component, plus relative push paths — broken navigation on the primary user action.
- **Post-submission crash**: guard checks `review?.data?.slug` but redirects via `review.data.booking_item_slug` — produces `/rate-review/undefined` after successful submission (FE-22, UX-05).
- **Entire page crashes on one bad API record**: no null guard on `traveling_date` in sort/render (FE-03).
- **Email privacy leak**: `review.user_info.email` rendered unmasked in `ReviewList.js` despite `maskEmail()` being defined in the same file (UX-10).
- **No post-submit confirmation**: user is redirected immediately with no success feedback.
- **Submit button silently disabled** with no inline validation explaining why (UX-04).
- **Cancel button routes to homepage** instead of `/rate-review` (UX-14).

### Guest / unauthenticated experience

The guest flow is nearly invisible with no affordance or guidance:

- **Silent cold redirect**: `useAuthRedirect.js` immediately pushes to `/api/auth/signin` with no interstitial explaining why login is required. The `callbackUrl` is preserved (correct), but there is zero contextual messaging at the redirect target (UX-01, downgraded to P1).
- **Blank flash during session resolution**: `loading` initialized to `false` — page renders the full empty layout before NextAuth confirms unauthenticated state (UX-02/FE-14 guard gap).
- **Token-based guest review path exists but is invisible**: `/rate-review/submit-review/[token]` does not check `session` — it is intended for email-invited reviewers with valid tokens. This path is undocumented and provides no UI hint that the reviewer is submitting unauthenticated. The `Authorization: Bearer ` empty-string header behavior depends on backend policy that is not documented in the frontend.
- **All three pages missing `noindex`** on auth-gated and token-gated URLs — crawl budget waste and potential token URL exposure (FE-08, P2 for index + submit-review only; detail page should be indexed).

---

## P0 — Must Fix Before Next Release

### P0-1 — Stored XSS in review detail page
→ See [[dompurify-xss-prevention-pattern]] (SSR-safe pattern, 3 options, why `isomorphic-dompurify` over raw `dompurify`). File: `pages/rate-review/[reviewSlug].js:455`. Effort: XS. Pattern copy from 3 sibling files.

---

### P0-2 — `parseISO(null)` crashes entire Rate & Review page
- **Finding:** FE-03 (confirmed P0 by skeptic)
- **File:** `components/review/BookingReviewList.js:43-45` (sort comparator), `BookingReviewList.js:110` (render)
- **Fix:**
  ```js
  // sort comparator
  const dateA = a.traveling_date ? parseISO(a.traveling_date) : new Date(0);
  const dateB = b.traveling_date ? parseISO(b.traveling_date) : new Date(0);
  return sortOrder === 'asc' ? compareAsc(dateA, dateB) : compareDesc(dateA, dateB);

  // render
  {booking.traveling_date ? format(parseISO(booking.traveling_date), 'dd MMM yy') : '—'}
  ```
- **Effort:** XS (2 lines)

---

### P0-3 — Star rating ARIA pattern breaks screen reader accessibility
- **Finding:** FE-02 (confirmed P0 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:111-147`
- **Fix:** Replace `aria-pressed={value <= rating}` pattern with `radiogroup`/`radio`/`aria-checked` pattern:
  ```jsx
  <div role="radiogroup" aria-labelledby="rating-label">
    {[1,2,3,4,5].map((value) => (
      <IconButton
        key={value}
        role="radio"
        aria-checked={value === rating}
        aria-label={`${value} star${value !== 1 ? 's' : ''} — ${ratingLabels[value]}`}
        onClick={() => setRating(value)}
      />
    ))}
  </div>
  ```
- **Effort:** S (~20 lines, self-contained refactor of existing markup)

---

## P1 — Fix This Sprint

### P1-1 — Wrong router import + relative push paths break "Write Review" / "View Review"
- **Finding:** FE-14 (upgraded from P2 by skeptic); absorbs UX-15
- **File:** `components/review/BookingReviewList.js:2, 185-186`
- **Fix:**
  ```js
  // line 2: change import
  import { useRouter } from 'next/router'; // was next/navigation

  // lines 185-186: add leading slashes
  router.push(`/rate-review/${booking.slug}`)
  router.push(`/rate-review/submit-review/${booking.token}`)
  ```
- **Effort:** XS (2 lines)

---

### P1-2 — Unmasked email in ReviewList — GDPR/PDPA violation
- **Finding:** UX-10 (confirmed P1 by skeptic)
- **File:** `components/review/ReviewList.js:53-56`
- **Fix:** Replace `review.user_info.email` with `maskEmail(review.user_info.email)`. The `maskEmail` helper is already defined in the same file and applied to `guest_email`.
- **Effort:** XS (1 line)

---

### P1-3 — Post-submission redirect guard mismatch — produces `/rate-review/undefined`
- **Finding:** FE-22 (upgraded from P2 by skeptic); related to UX-05
- **File:** `pages/rate-review/submit-review/[...slug].js:71-76`
- **Fix:**
  ```js
  // Guard on the field actually used in the redirect
  if (review?.data?.booking_item_slug) {
    router.push(`/rate-review/${review.data.booking_item_slug}`);
  }
  ```
  Additionally, show a success banner before redirect (UX-05 companion):
  add `<NotificationSnackbar severity="success" message="Review submitted successfully!" />` visible for 2 seconds before `router.push`.
- **Effort:** S (guard = 1 line; success banner = ~5 lines)

---

### P1-4 — Auth redirect without interstitial — no context for guest users
- **Finding:** UX-01 (downgraded from P0 to P1 by skeptic)
- **File:** `components/utils/useAuthRedirect.js:11-14`, `pages/rate-review/index.js:24-27`
- **Fix:** Before calling `router.push('/api/auth/signin?callbackUrl=...')`, render a brief interstitial card: "Log in to see and write reviews for your recent bookings" with a "Log In" button preserving `callbackUrl`. Alternatively gate rendering on `status !== 'loading'` and show `<ListSkeleton count={3} />` during the loading phase (covers UX-02 simultaneously).
- **Effort:** S (~15 lines in index.js)

---

### P1-5 — Caption text `text-gray-400` fails WCAG AA contrast
- **Finding:** FE-04 (confirmed P1 by skeptic)
- **Files:** `components/RateAndReview/RateAndReviewForm.js:262`, `components/review/BookingReviewList.js:109`
- **Fix:** Replace `text-gray-400` with `text-gray-500` (`#6B7280`, contrast ratio ~4.6:1 on white — passes AA). `COLORS.neutral.gray500` is already defined in the design system.
- **Effort:** XS (2-line find-replace)

---

### P1-6 — Image thumbnails not keyboard accessible
- **Finding:** FE-05 (confirmed P1 by skeptic)
- **File:** `components/review/ReviewImageThumbnails.js:23-34`
- **Fix:**
  ```jsx
  <div
    role="button"
    tabIndex={0}
    aria-label={img.caption || `View review photo ${idx + 1}`}
    onClick={() => { setLightboxIndex(idx); setLightboxOpen(true); }}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); setLightboxIndex(idx); setLightboxOpen(true);
      }
    }}
  >
  ```
- **Effort:** S (~8 lines per thumbnail div)

---

### P1-7 — Back IconButton has no accessible label
- **Finding:** FE-06 (confirmed P1 by skeptic)
- **Files:** `pages/rate-review/[reviewSlug].js:248`, `pages/rate-review/index.js:94`, `pages/rate-review/submit-review/[...slug].js:102` (3 files, not 2 — audit missed `index.js` back button)
- **Fix:** Add `aria-label="Back to reviews"` (or "Go back" on `index.js`) directly on all `IconButton` elements. MUI Tooltip does not propagate `aria-label` to the button in MUI v5.
- **Effort:** XS (1 line each, 3 files)

---

### P1-8 — Submit button disabled with no explanation
- **Finding:** UX-04 (confirmed P1 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:291` (disabled condition), `:175, :212` (TextFields)
- **Fix:** Add `helperText` or inline `<FormHelperText>` on blur when title or reviewText is empty. At minimum: add MUI `Tooltip` to the disabled button: "Please add a title and review text to continue." Also update the disabled condition to include `rating === 0` once UX-03 (P2) is implemented.
- **Effort:** S (~10 lines)

---

### P1-9 — Canonical URL missing `www.` on all three pages
- **Finding:** FE-09 / UX-17 merged (confirmed P1 by skeptic; UX-17 identified the additional detail-page-specific canonical problem)
- **Files:** `pages/rate-review/index.js:56`, `pages/rate-review/[reviewSlug].js:247-250`, `pages/rate-review/submit-review/[...slug].js:24`
- **Fix:**
  ```js
  import { getSiteUrl } from '../../utils/blog/seoHelper';
  // index.js
  canonical: `${getSiteUrl()}/rate-review`
  // [reviewSlug].js — dynamic per page
  canonical: `${getSiteUrl()}/rate-review/${reviewSlug}`
  // submit-review — noindex (see P2-5), canonical secondary
  canonical: `${getSiteUrl()}/rate-review/submit-review`
  ```
  Note: UX-17 confirmed all review detail pages currently share the same static canonical — the list page URL. The per-page dynamic canonical for `[reviewSlug].js` is the more impactful fix.
- **Effort:** S (3 files, import + one-line fix each)

---

### P1-10 — `aria-required` on MUI TextField wrapper, not inner input
- **Finding:** FE-16 (confirmed P2 by skeptic, but re-evaluated: real WCAG gap affecting form usability)
- **File:** `components/RateAndReview/RateAndReviewForm.js:175, 212`
- **Fix:** Use MUI's `inputProps` to pass ARIA to the inner `<input>`:
  ```jsx
  inputProps={{ 'aria-required': true }}
  ```
  Or use MUI's `required` prop which correctly sets both the asterisk and the native `required` attribute.
- **Effort:** XS (2-line change)

---

## P2 — Fix Next Sprint

### P2-1 — Default star rating of 5 — inflate risk
- **Finding:** UX-03 (downgraded from P1 to P2 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:22`
- **Fix:** Initialize `rating` to `0`. Require non-zero rating in submit disabled condition (alongside P1-8). Add "Tap to rate" helper label when `rating === 0`.
- **Effort:** S (~5 lines)

---

### P2-2 — Error state uses raw API error string / silent failure on undefined
- **Finding:** UX-06 + FE-13 merged (confirmed P2 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:90`
- **Fix:**
  ```js
  setError(
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    'Failed to submit review. Please try again.'
  );
  ```
  Also map known messages: "review with this booking id already exists" → "You've already reviewed this booking."
- **Effort:** XS (1 multi-line change)

---

### P2-3 — No feedback when >5 photos selected
- **Finding:** UX-07 (downgraded from P1 to P2 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:241`
- **Fix:** After `slice(0, 5)`, check `e.target.files.length > 5` and show a warning: "Only the first 5 photos were selected. Maximum is 5."
- **Effort:** XS (~3 lines)

---

### P2-4 — Native file input visual mismatch with MUI form
- **Finding:** VIS-04 (downgraded from P1 to P2 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:236-248`
- **Fix:** Replace native `<input type="file">` with a hidden input triggered by a visible MUI `Button` via `component="label"`:
  ```jsx
  <Button variant="outlined" component="label">
    Upload Photos
    <input type="file" hidden accept="image/*,.heic,.heif" multiple onChange={handleFileChange} />
  </Button>
  ```
- **Effort:** M (~15 lines refactor)

---

### P2-5 — Missing `noindex` on auth-gated and token-gated pages
- **Finding:** FE-08 (downgraded from P1 to P2 by skeptic; detail page should NOT be noindexed)
- **Files:** `pages/rate-review/index.js`, `pages/rate-review/submit-review/[...slug].js`
- **Fix:**
  ```js
  // index.js and submit-review/[...slug].js only
  noindex: true,
  nofollow: true,
  ```
  Do NOT add `noindex` to `[reviewSlug].js` — review detail pages with content are desirable SEO targets.
- **Effort:** XS (2 files, 1-line each)

---

### P2-6 — Cancel button routes to homepage instead of `/rate-review`
- **Finding:** UX-14 (confirmed P2 by skeptic)
- **File:** `pages/rate-review/submit-review/[...slug].js:143`
- **Fix:** Change `onClose={() => router.push('/')}` to `onClose={() => router.push('/rate-review')}`.
- **Effort:** XS (1 line)

---

### P2-7 — Network fetch error shows EmptyState as if no bookings
- **Finding:** FE-21 (confirmed P2 by skeptic)
- **File:** `pages/rate-review/index.js:39-41`
- **Fix:**
  ```js
  const [fetchError, setFetchError] = useState(null);
  // in catch: setFetchError('Unable to load your bookings. Please try again.');
  // in render: {fetchError && <div role="alert" className="text-red-600 p-4">{fetchError}</div>}
  ```
- **Effort:** S (~8 lines)

---

### P2-8 — Empty state has no CTA and uses wrong variant icon
- **Finding:** UX-16 (confirmed P2) + VIS-08 (confirmed P2) — combined fix
- **File:** `components/review/BookingReviewList.js:52-58`
- **Fix:** Change `variant="completed"` to `variant="first-use"` (removes false-positive green checkmark). Add `ctaText="Explore Trips"` and `ctaHref="/trips"` to give users a path forward.
- **Effort:** XS (2-line change)

---

### P2-9 — Empty star color `#D1D5DB` fails WCAG 1.4.11 Non-text Contrast
- **Finding:** FE-19 (upgraded from P3 to P2 by skeptic)
- **File:** `components/RateAndReview/RateAndReviewForm.js:141`
- **Fix:** Replace `#D1D5DB` (ratio ~1.62:1) with `#6B7280` (`COLORS.neutral.gray500`, ratio ~4.6:1) for the unselected star color. Also add `COLORS.review = { starFilled: '#FFA000', starEmpty: '#6B7280' }` to `helpers/designSystem.js` to register these as tokens.
- **Effort:** S (designSystem.js + 1 component = 2 files, ~5 lines total)

---

### P2-10 — Sort button has no `aria-pressed` toggle state announcement
- **Finding:** FE-07 (downgraded from P1 to P2 by skeptic); related to UX-09 (confirmed P2)
- **File:** `components/review/BookingReviewList.js:81-87`
- **Fix:**
  ```jsx
  <button
    onClick={toggleSortOrder}
    aria-pressed={sortOrder === 'desc'}
    aria-label={`Sort by date, currently ${sortOrder === 'asc' ? 'ascending' : 'descending'}. Click to toggle.`}
    className="text-fb-blue text-sm hover:underline"
  >
  ```
  Separately, replace `hover:underline` styling with a proper `<Button>` or icon-button to distinguish it visually from navigation links (UX-09).
- **Effort:** S (~5 lines)

---

### P2-11 — Loading state blank flash (no session-loading guard)
- **Finding:** UX-02 (downgraded from P1 to P2 by skeptic)
- **File:** `pages/rate-review/index.js:73-80`
- **Fix:** Add top-level guard: if `status === 'loading'`, return `<ListSkeleton count={3} />`. Also remove `router` from the `useEffect` dependency array (FE-11 companion — `router` is unused inside the effect body, only `session` matters).
  ```js
  // UX-02 fix
  if (status === 'loading') return <ListSkeleton count={3} />;
  // FE-11 fix
  }, [session, status]);  // remove router
  ```
- **Effort:** XS (2 lines)

---

### P2-12 — Missing page-level H1 on reviews list index page
- **Finding:** UX-18 / VIS-05 merged (confirmed P2 by skeptic)
- **Files:** `pages/rate-review/index.js` (no H1), `components/review/BookingReviewList.js:78` (Typography not h1)
- **Fix:** Add `<h1 className="sr-only">Rate & Review</h1>` to `index.js`, or change `BookingReviewList.js:78` Typography to `component="h1"` with `TYPOGRAPHY_SCALE.h1` classes.
- **Effort:** XS (1-2 lines)

---

### P2-13 — `gap-0` on index page wrapper collapses vertical rhythm
- **Finding:** VIS-02 (downgraded from P1 to P3 by skeptic — but reconsidered: with H1 added in P2-12, this becomes a real gap issue)
- **File:** `pages/rate-review/index.js:89`
- **Fix:** Change `gap-0` to `gap-4` to match detail page pattern (`[reviewSlug].js` uses `gap-4` at equivalent wrapper).
- **Effort:** XS (1 word change)

---

## P3 — Backlog

- **Dead code cleanup**: Remove 136-line commented-out block at `pages/rate-review/[reviewSlug].js:1-136` (UX-11, VIS-11, confirmed by all 3 specialists).
- **Duplicate `return normalized`**: Remove second `return normalized` at `[reviewSlug].js:233` (UX-12/FE-12/VIS-12 — all agree).
- **Dead import `ReviewList`**: Remove unused `import ReviewList` from `pages/rate-review/index.js:6` (FE-10).
- **`onClose` null guard**: Add default noop `onClose = () => {}` in `RateAndReviewForm.js` props destructuring (FE-15).
- **Photo alt text**: Use filename instead of generic `"Preview 1"` in `RateAndReviewForm.js:254` (FE-17).
- **Individual photo removal**: Add `×` button on each preview thumbnail to allow removing a single file without clearing all (UX-08).
- **Booking slug as heading**: Replace `Booking: {slug}` subtitle with human-readable trip context — `booking.contract_name` or station pair (UX-13).
- **Star filled color token**: Add `COLORS.review.starFilled: '#FFA000'` to `helpers/designSystem.js` and update `BookingReviewList.js:68` and `RateAndReviewForm.js:133` to reference it (VIS-01 — visual token only, no user impact).
- **Back button hardcoded color**: Replace `color: '#3b5998'` with `COLORS.brand.primary` in `submit-review/[...slug].js:100` (VIS-03/FE-18 — same hex value, developer hygiene only).
- **Loading spinner brand color**: Add `sx={{ color: COLORS.brand.primary }}` to `CircularProgress` in `submit-review/[...slug].js:82` (VIS-07).
- **ListSkeleton column vs grid**: Pass `columns` prop to `ListSkeleton` so skeleton matches the 3-column loaded grid (VIS-09).
- **Error boundary**: Wrap `<BookingReviewList>` in an `<ErrorBoundary>` as belt-and-suspenders defense after FE-03 is fixed (FE-20).

---

## Deferred / Dropped

The following findings were **dropped** by the skeptic and should not be implemented:

- **VIS-06 — Star size 44px "too large"**: The 44px is the WCAG-minimum touch target on the `IconButton` wrapper. The recommendation to reduce to 36px is a product preference, not a defect. Dropped.
- **VIS-10 — Action button hover wrong token**: `hover:bg-blue-600` = `#2563EB` which is identical to `COLORS.brand.secondary`. No visual difference exists today. Pure token-labeling concern. Dropped.
- **VIS-13 — `text-fb-blue` vs `COLORS` import inconsistency**: The Visual specialist themselves said "No code change needed." Using `text-fb-blue` in Tailwind contexts is the correct pattern. Dropped — not a finding.

The following were **merged** (duplicate findings, less complete version dropped):

- **UX-15** (relative path bug): Absorbed into FE-14, which also catches the wrong router import.
- **UX-17** (canonical on detail page): Absorbed into FE-09, with UX-17's additional scope (dynamic per-page canonical) carried forward into the P1-9 fix.
- **UX-18** (missing H1): Merged with VIS-05. Single fix in P2-12.
- **UX-06** (raw error string): Merged with FE-13. Single fix in P2-2.
- **FE-18** (hardcoded `#3b5998`): Merged with VIS-03. P3 backlog.
- **FE-12** / **UX-12** (duplicate `return normalized`): Merged with VIS-12. P3 backlog.

---

## Implementation Order

Fix in this sequence to minimize risk and maximize dependency resolution:

1. **P0-1 — XSS fix** (`[reviewSlug].js:455`) — isolated, 1 file, no dependencies. Ship immediately.
2. **P0-2 — `parseISO(null)` null guard** (`BookingReviewList.js:43-45, 110`) — isolated, 1 file. Ship immediately.
3. **P1-1 — Router import + paths** (`BookingReviewList.js:2, 185-186`) — fixes the core navigation CTA. Ship immediately. Required before any other BookingReviewList changes.
4. **P1-2 — Email masking** (`ReviewList.js:53-56`) — isolated 1-line fix. Ship with #1-3 in same commit.
5. **P1-9 — Canonical URLs** (3 page files) — isolated SEO fix, no UI dependencies. Ship with initial batch.
6. **P0-3 — Star ARIA radiogroup** (`RateAndReviewForm.js:111-147`) — form-only, no page dependencies. Next.
7. **P1-5 — Caption contrast** (`RateAndReviewForm.js:262`, `BookingReviewList.js:109`) — ship with P0-3 (same files open).
8. **P1-7 + P1-10 — Back button aria-label + aria-required fix** (3 page files + form file) — accessibility sweep, batch together.
9. **P1-3 — Post-submission guard + success banner** (`[...slug].js:71-76`) — depends on understanding redirect field; verify `booking_item_slug` === `slug` with backend before shipping.
10. **P1-4 — Guest interstitial / loading guard** (`index.js`) — also covers P2-11 (session loading flash) + FE-11 (router dep). Batch together.
11. **P1-6 — Thumbnail keyboard access** (`ReviewImageThumbnails.js`) — isolated component.
12. **P1-8 — Submit button disabled feedback** (`RateAndReviewForm.js`) — can bundle with P2-1 (star default change) and P2-2 (error fallback) since same file.
13. **P2-1 through P2-5** — next sprint, grouped by file proximity.
14. **P3 items** — dead code cleanup, token registration, minor a11y improvements. Can be done in any order.

---

## Design System Compliance Score

| Component | Current | Target |
|-----------|---------|--------|
| `UnifiedCard.js` | 10/10 | 10/10 (baseline) |
| `BadgeChip.js` | 10/10 | 10/10 |
| `EmptyState.js` | 9/10 | 10/10 |
| `[reviewSlug].js` | 8/10 | 9/10 (after canonical + dead code) |
| `ListSkeleton.js` | 8/10 | 9/10 (after grid variant) |
| `RateAndReviewForm.js` | 6/10 | 9/10 (after star tokens, ARIA, file input, error handling) |
| `[...slug].js` | 5/10 | 8/10 (after color token, spinner, canonical, noindex) |
| `BookingReviewList.js` | 5/10 | 9/10 (after router fix, null guard, contrast, sort ARIA) |
| `pages/rate-review/index.js` | 4/10 | 8/10 (after H1, gap fix, canonical, noindex, loading guard) |

**Current overall design system compliance: 6.1/10**
**Target after P0+P1+P2 fixes: 9.0/10**

## Sibling Sub-Files (Linked 2026-06-13)
- [[../rate-review-uxui-audit-2026-06-06-overview]] — umbrella overview
- [[r1-frontend]] — Phase 1 frontend & a11y audit (22 findings)
- [[r4-scrutinize]] — outsider verification pass (4 corrections)
- [[r5-implementation-plan]] — Release 1 fix spec + Sprint 1 backlog
