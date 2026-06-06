# r1-frontend — Frontend & Accessibility Audit
**Specialist:** Frontend Engineering & Accessibility
**Date:** 2026-06-06

## Summary

The `/rate-review` flow is functional but carries several significant accessibility violations: the star rating widget uses `aria-pressed` on independent `IconButton` elements instead of a `radiogroup`/`radio` pattern, which causes screen readers to misread the component's purpose entirely. There are two security concerns — `dangerouslySetInnerHTML` in `[reviewSlug].js` renders user-submitted review text without DOMPurify sanitization (XSS vector), and unguarded `parseISO()` calls in `BookingReviewList.js` will throw and crash the entire list if any booking has a null `traveling_date`. The canonical URL across all three pages uses the non-www domain (`smartenplus.co.th`) in violation of the project's own CLAUDE.md SEO rule.

---

## WCAG Violations

| Finding | WCAG Criterion | Severity | Location |
|---------|---------------|----------|----------|
| Star rating uses `aria-pressed` on independent buttons, not `radiogroup`/`radio` | 1.3.1 Info and Relationships (A) | **High** | `RateAndReviewForm.js:112-147` |
| `aria-required="true"` on MUI `TextField` wrapper div, not on the inner `<input>` | 1.3.5 Identify Input Purpose (AA) | Medium | `RateAndReviewForm.js:175, 212` |
| `text-gray-400` caption text (`#9CA3AF` on white) — contrast ratio ~2.85:1, fails AA | 1.4.3 Contrast Minimum (AA) | **High** | `RateAndReviewForm.js:262` (caption), `BookingReviewList.js:109` |
| Thumbnail `div` in `ReviewImageThumbnails` is click-only, no `role`, no keyboard access | 2.1.1 Keyboard (A) | **High** | `ReviewImageThumbnails.js:23-34` |
| Sort button in `BookingReviewList` has no `aria-label` describing current state | 4.1.2 Name, Role, Value (A) | Medium | `BookingReviewList.js:81-87` |
| Back `IconButton` in `[reviewSlug].js` and `[...slug].js` has no accessible label (tooltip only) | 4.1.2 Name, Role, Value (A) | Medium | `[reviewSlug].js:327-339`, `[...slug].js:95-109` |
| Photo preview images `alt="Preview 1"` — generic, not meaningful | 1.1.1 Non-text Content (A) | Low | `RateAndReviewForm.js:254` |
| No `noindex` on auth-required pages — indexed by search engines | 3.1 (SEO/privacy) | Medium | All three pages |
| No focus management after form submit — screen reader stays on Submit button | 2.4.3 Focus Order (A) | Medium | `RateAndReviewForm.js:53-94` |

---

## Findings

### [FE-01] XSS via unsanitized `dangerouslySetInnerHTML` (Priority: P0)
- **What:** `[reviewSlug].js` renders `review_text` via `dangerouslySetInnerHTML={{ __html: formattedText }}` where `formattedText` is produced by a simple `.replace(/\r?\n/g, '<br />')` with no HTML sanitization. A user who submitted a review with `<script>` tags or `<img onerror=...>` payload would have that executed in any viewer's browser.
- **Where:** `pages/rate-review/[reviewSlug].js:455`
- **WCAG:** Not a WCAG issue — this is a security issue (XSS)
- **Impact:** Stored XSS. All users viewing a review detail page can have arbitrary JavaScript executed in their session.
- **Recommendation:** Import and apply DOMPurify identically to how `ReviewList.js`, `ReviewDetailModal.js`, and `ReviewFirstPage.js` already do it:
  ```js
  // At top of file (SSR-safe pattern already established in codebase)
  let DOMPurify = null;
  if (typeof window !== 'undefined') {
    DOMPurify = require('dompurify');
  }
  // At render
  dangerouslySetInnerHTML={{ __html: DOMPurify ? DOMPurify.sanitize(formattedText) : formattedText }}
  ```

---

### [FE-02] Star rating ARIA pattern incorrect — `aria-pressed` vs `radiogroup` (Priority: P0)
- **What:** Five `IconButton` elements each have `aria-pressed={value <= rating}`. This tells screen readers each button is an independent toggle switch, not a mutually exclusive 1–5 star selection. A user navigating with NVDA/VoiceOver will hear "Rate 1 star — Poor, pressed. Rate 2 stars — Fair, pressed. Rate 3 stars — Good, pressed." for a 3-star selection — three "pressed" buttons simultaneously, which is semantically wrong and confusing.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:111-147`
- **WCAG:** 1.3.1 Info and Relationships (A)
- **Impact:** Screen reader users cannot understand or operate the rating control correctly.
- **Recommendation:** Replace with a `radiogroup` pattern. Wrap the five buttons in a `<div role="radiogroup" aria-labelledby="rating-label">` and change each `IconButton` to `role="radio"` with `aria-checked={value === rating}` (not `aria-pressed`, not `value <= rating`):
  ```jsx
  <div role="radiogroup" aria-labelledby="rating-label">
    {[1,2,3,4,5].map((value) => (
      <IconButton
        key={value}
        role="radio"
        aria-checked={value === rating}
        aria-label={`${value} star${value !== 1 ? 's' : ''} — ${ratingLabels[value]}`}
        onClick={() => setRating(value)}
        ...
      />
    ))}
  </div>
  ```

---

### [FE-03] `parseISO(null)` crash — unguarded date parsing (Priority: P0)
- **What:** `BookingReviewList.js` calls `parseISO(a.traveling_date)` and `parseISO(b.traveling_date)` in `.sort()` and `format(parseISO(booking.traveling_date), ...)` in the render. If any booking has `traveling_date: null` or `traveling_date: undefined`, `parseISO(null)` returns an `Invalid Date`, `compareAsc` returns `NaN`, and `format(Invalid Date, ...)` throws a `RangeError`, crashing the entire list render with no error boundary.
- **Where:** `components/review/BookingReviewList.js:43-45, 110`
- **WCAG:** N/A
- **Impact:** One bad record from the API kills the entire Rate & Review page for the authenticated user.
- **Recommendation:**
  ```js
  // Guard in sort comparator
  const dateA = a.traveling_date ? parseISO(a.traveling_date) : new Date(0);
  const dateB = b.traveling_date ? parseISO(b.traveling_date) : new Date(0);
  return sortOrder === 'asc' ? compareAsc(dateA, dateB) : compareDesc(dateA, dateB);

  // Guard in render
  {booking.traveling_date ? format(parseISO(booking.traveling_date), 'dd MMM yy') : '—'}
  ```

---

### [FE-04] Caption text `text-gray-400` fails WCAG AA contrast (Priority: P1)
- **What:** `text-gray-400` maps to `#9CA3AF` (per Tailwind defaults). On a white (`#FFFFFF`) background the contrast ratio is approximately 2.85:1 — far below the WCAG AA requirement of 4.5:1 for normal text. This affects the "Up to 5 photos, 10MB max each" caption and the date text in booking cards.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:262`, `components/review/BookingReviewList.js:109`
- **WCAG:** 1.4.3 Contrast Minimum (AA)
- **Impact:** Users with low vision cannot read supplemental instructions and date information.
- **Recommendation:** Use `text-gray-500` (`#6B7280`, ratio ~4.6:1 on white — passes AA) instead of `text-gray-400` for all caption/secondary text. The design system already defines `COLORS.neutral.gray500 = '#6B7280'`.

---

### [FE-05] Image thumbnails not keyboard accessible (Priority: P1)
- **What:** In `ReviewImageThumbnails.js`, each thumbnail is a plain `<div>` with an `onClick` handler. There is no `role`, no `tabIndex`, no `onKeyDown`/`onKeyUp`, and no `aria-label`. Keyboard users and screen reader users cannot access or activate the lightbox.
- **Where:** `components/review/ReviewImageThumbnails.js:23-34`
- **WCAG:** 2.1.1 Keyboard (A), 4.1.2 Name Role Value (A)
- **Impact:** Users who cannot use a mouse cannot view full-size review photos.
- **Recommendation:**
  ```jsx
  <div
    key={img.id}
    role="button"
    tabIndex={0}
    aria-label={img.caption || `View review photo ${idx + 1}`}
    className="w-16 h-16 relative rounded overflow-hidden cursor-pointer"
    onClick={() => { setLightboxIndex(idx); setLightboxOpen(true); }}
    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setLightboxIndex(idx); setLightboxOpen(true); } }}
  >
  ```
  Also increase thumbnail size from `w-16 h-16` (64px) to at minimum `w-11 h-11` (44px) — they are already 64px so this is fine, but confirm touch target with padding included.

---

### [FE-06] Back `IconButton` has no accessible label (Priority: P1)
- **What:** Both `[reviewSlug].js` and `[...slug].js` render an `IconButton` containing only `<ArrowBackIosOutlinedIcon />`. The `Tooltip` title provides a visual hover label but `Tooltip` does not propagate `aria-label` to the button in MUI v5. Screen readers announce "button" with no name.
- **Where:** `pages/rate-review/[reviewSlug].js:327-339`, `pages/rate-review/submit-review/[...slug].js:95-109`
- **WCAG:** 4.1.2 Name, Role, Value (A)
- **Impact:** Screen reader users hear an anonymous button with no purpose.
- **Recommendation:** Add `aria-label="Back to reviews"` directly on the `IconButton`:
  ```jsx
  <IconButton aria-label="Back to reviews" onClick={() => router.push('/rate-review')} ...>
  ```

---

### [FE-07] Sort button has no `aria-label` for current state (Priority: P1)
- **What:** The sort button in `BookingReviewList` renders as a plain `<button>` with text "Sort by Date (Ascending)". While text content is present, there is no `aria-pressed`, `aria-sort`, or `aria-label` indicating that clicking it will *toggle* the order. The current state is embedded in the button text, which is acceptable but the toggle action is implied, not announced.
- **Where:** `components/review/BookingReviewList.js:81-87`
- **WCAG:** 4.1.2 Name, Role, Value (A)
- **Impact:** Screen reader users understand the current state but not that the button is a toggle.
- **Recommendation:** Add `aria-pressed`:
  ```jsx
  <button
    onClick={toggleSortOrder}
    aria-pressed={sortOrder === 'desc'}
    aria-label={`Sort by date, currently ${sortOrder === 'asc' ? 'ascending' : 'descending'}. Click to toggle.`}
    className="text-fb-blue text-sm hover:underline"
  >
    Sort by Date ({sortOrder === 'asc' ? 'Ascending' : 'Descending'})
  </button>
  ```

---

### [FE-08] All three pages missing `noindex` — auth-required content indexed (Priority: P1)
- **What:** `/rate-review`, `/rate-review/[reviewSlug]`, and `/rate-review/submit-review/[...slug]` all use `NextSeo` without `noindex: true`. The index page is auth-gated but crawlers can still request it (they won't be redirected). The review detail page is fully public — any user's review is publicly readable and indexable. The submit-review page is token-gated but the URL pattern `submit-review/[token]` will still be crawled. None of the pages set `robots: { noindex: true }`.
- **Where:** All three page files, `seo` config objects
- **WCAG:** N/A (SEO/privacy concern)
- **Impact:** User-specific review submission URLs with opaque tokens can appear in search results. The authenticated list page returns 200 with empty content for crawlers, wasting crawl budget.
- **Recommendation:**
  ```js
  // index.js and submit-review/[...slug].js — hard noindex
  noindex: true,
  nofollow: true,

  // [reviewSlug].js — allow index only if review data loaded, otherwise noindex
  noindex: !review,
  ```

---

### [FE-09] Canonical URL missing `www.` on all three pages (Priority: P1)
- **What:** All three pages set `canonical: 'https://smartenplus.co.th/rate-review'`. Per CLAUDE.md: "all canonicals must use `https://www.smartenplus.co.th`. Never `https://smartenplus.co.th` (no www)."
- **Where:** `pages/rate-review/index.js:56`, `pages/rate-review/[reviewSlug].js:249`, `pages/rate-review/submit-review/[...slug].js:24`
- **WCAG:** N/A (SEO)
- **Impact:** Google may treat the www and non-www versions as separate URLs, splitting link equity and causing duplicate content.
- **Recommendation:** Use `getSiteUrl()` from `utils/blog/seoHelper.js` instead of hardcoding:
  ```js
  import { getSiteUrl } from '../../utils/blog/seoHelper';
  canonical: `${getSiteUrl()}/rate-review`,
  ```
  For `[reviewSlug].js` the canonical should also be dynamic: `${getSiteUrl()}/rate-review/${reviewSlug}`.

---

### [FE-10] Dead import `ReviewList` in `index.js` (Priority: P2)
- **What:** `pages/rate-review/index.js` imports `ReviewList` from `../../components/review/ReviewList` (line 6) but it is never rendered anywhere in the component. `BookingReviewList` is used instead.
- **Where:** `pages/rate-review/index.js:6`
- **WCAG:** N/A
- **Impact:** Increases bundle size marginally; adds confusion about which component is authoritative.
- **Recommendation:** Remove the unused import.

---

### [FE-11] `router` as `useEffect` dependency in `index.js` — stale/infinite risk (Priority: P2)
- **What:** `useEffect` in `index.js` lists `[session, router]` as dependencies. In Next.js, `useRouter()` returns a stable object reference but this is an implementation detail that can change. More critically, `router` is not used inside the effect body at all — only `session` matters. Including `router` is a lint violation (unused dep) and may cause subtle re-fetches on any router state change (query params, hash changes during navigation).
- **Where:** `pages/rate-review/index.js:48`
- **WCAG:** N/A
- **Impact:** Potential redundant API calls on query string changes; eslint-plugin-react-hooks will flag this.
- **Recommendation:** Remove `router` from the dependency array: `}, [session, status]);`

---

### [FE-12] Duplicate `return normalized` statement (unreachable code) (Priority: P2)
- **What:** `normalizeReviewForSummary()` in `[reviewSlug].js` has two consecutive `return normalized` statements at lines 231 and 233. The second is dead code.
- **Where:** `pages/rate-review/[reviewSlug].js:231-233`
- **WCAG:** N/A
- **Impact:** No runtime impact, but indicates copy-paste error and will trigger lint warnings.
- **Recommendation:** Remove the duplicate `return normalized` at line 233.

---

### [FE-13] `setError(error?.response?.data?.detail)` may set `undefined` (Priority: P2)
- **What:** In `RateAndReviewForm.js`, the catch block calls `setError(error?.response?.data?.detail)`. If `detail` is absent from the error response (e.g., a network timeout or a 500 with a non-standard body), `detail` is `undefined`, so `setError(undefined)`. The Snackbar condition is `{error && ...}` so it won't render, but the user sees no feedback about the failure at all.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:90`
- **WCAG:** N/A
- **Impact:** Silent failure on network errors or unexpected API shapes — user clicks Submit, spinner disappears, nothing happens.
- **Recommendation:**
  ```js
  setError(error?.response?.data?.detail || error?.response?.data?.message || 'Failed to submit review. Please try again.');
  ```

---

### [FE-14] `router.push` paths missing leading slash in `BookingReviewList` (Priority: P2)
- **What:** `BookingReviewList.js` pushes `rate-review/${booking.slug}/` and `rate-review/submit-review/${booking.token}` (no leading `/`). The `useRouter` from `next/navigation` (App Router) resolves relative paths against the current URL, while `next/router` (Pages Router) treats them as absolute. `BookingReviewList` imports from `next/navigation` but runs under Pages Router — relative push paths are undefined behavior and may resolve incorrectly depending on the current path depth.
- **Where:** `components/review/BookingReviewList.js:2, 185-186`
- **WCAG:** N/A
- **Impact:** Navigation may fail or route to wrong URLs on certain page depths.
- **Recommendation:** Add leading slashes and fix the router import:
  ```js
  import { useRouter } from 'next/router'; // Pages Router, not next/navigation
  // ...
  router.push(`/rate-review/${booking.slug}`)
  router.push(`/rate-review/submit-review/${booking.token}`)
  ```

---

### [FE-15] `RateAndReviewForm` `onClose` called without guard — crashes if undefined (Priority: P2)
- **What:** The Cancel button calls `onClick={onClose}` directly. If `onClose` is not provided by a parent, clicking Cancel throws `TypeError: onClose is not a function`. In `[...slug].js`, it's provided as `() => router.push('/')` which is fine, but the component has no prop-types or default value to guard against future misuse.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:270`
- **WCAG:** N/A
- **Impact:** Runtime crash if component is used without `onClose`.
- **Recommendation:** Add a default noop: `const ReviewForm = ({ ..., onClose = () => {} }) => {` or add `PropTypes.func` validation.

---

### [FE-16] `aria-required` on MUI `TextField` wrapper div, not inner `<input>` (Priority: P2)
- **What:** `aria-required="true"` is passed as a prop to MUI `TextField`. MUI v5 does not forward unknown props to the underlying `<input>` element by default — it applies them to the wrapper `<div>`. Screen readers look for `aria-required` on the `<input>` element, not its container. The attribute effectively has no effect.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:175, 212`
- **WCAG:** 1.3.5 (AA)
- **Impact:** Screen readers do not announce these fields as required.
- **Recommendation:** Use MUI's `inputProps` to pass ARIA attributes to the inner input:
  ```jsx
  inputProps={{ 'aria-required': true, 'aria-label': 'Review title' }}
  ```
  Or use MUI's `required` prop which correctly sets both the label asterisk and the input's `required` attribute.

---

### [FE-17] Photo preview alt text generic and not meaningful (Priority: P3)
- **What:** Preview images use `alt={`Preview ${idx + 1}`}`. While this meets the basic non-empty alt requirement, it provides no meaningful description for screen reader users who may be reviewing their uploads.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:254`
- **WCAG:** 1.1.1 Non-text Content (A)
- **Impact:** Minimal — the user just selected the file and knows what they uploaded.
- **Recommendation:** Use the file name: `alt={`Preview of ${files[idx]?.name || `photo ${idx + 1}`}`}`. Also add a remove button per thumbnail to allow deselection without clearing all files.

---

### [FE-18] Hardcoded color `'#3b5998'` in `[...slug].js` bypasses design token (Priority: P3)
- **What:** `submit-review/[...slug].js:100` hardcodes `color: '#3b5998'` for the back button, instead of using `COLORS.brand.primary` from the design system. `[reviewSlug].js` correctly uses `COLORS.brand.primary`. Inconsistency means a brand color change would require hunting down raw hex values.
- **Where:** `pages/rate-review/submit-review/[...slug].js:100`
- **WCAG:** N/A
- **Impact:** Design system drift.
- **Recommendation:** Import `COLORS` and use `COLORS.brand.primary`.

---

### [FE-19] Star icons in form hardcode `#FFA000` and `#D1D5DB` outside design system (Priority: P3)
- **What:** `RateAndReviewForm.js:133, 141` hardcodes gold (`#FFA000`) and unselected gray (`#D1D5DB`) for star icons. These values exist nowhere in the design system (`designSystem.js`) — meaning if the brand palette is updated, these will drift silently.
- **Where:** `components/RateAndReview/RateAndReviewForm.js:133, 141`
- **WCAG:** N/A
- **Impact:** Design system drift; contrast for the gray star against white is 1.6:1 (UI component, needs 3:1 per WCAG 1.4.11 for non-text contrast). `#D1D5DB` on white is only ~1.62:1, which fails WCAG 1.4.11 Non-text Contrast.
- **Recommendation:** Add tokens to designSystem.js (`COLORS.review.starFilled: '#FFA000'`, `COLORS.review.starEmpty: '#9CA3AF'`) and use `#9CA3AF` instead of `#D1D5DB` for the empty star (ratio ~2.85:1 — still borderline, but better). Best option is `#6B7280` (~4.6:1, passes).

---

### [FE-20] No error boundary on `BookingReviewList` (Priority: P2)
- **What:** If `parseISO` throws (see FE-03) or any `booking` property access causes an error in the map, the entire page crashes to a blank screen. There is no error boundary wrapping the list or the page.
- **Where:** `pages/rate-review/index.js`, `components/review/BookingReviewList.js`
- **WCAG:** N/A
- **Impact:** Complete page failure for the user with no recovery path.
- **Recommendation:** Wrap `<BookingReviewList>` in an `<ErrorBoundary>` component that shows a user-friendly fallback. Fix FE-03 (null date guard) as the immediate tactical fix.

---

### [FE-21] Network error on fetch shows no user-facing state on `index.js` (Priority: P2)
- **What:** The catch block in `index.js` only calls `console.error(error)`. If the `/booking-reviews/` API call fails (network error, 500, 401), `reviews` stays as `[]`, the loading spinner clears, and `EmptyState` renders as if the user genuinely has no reviews. The user has no way to distinguish "no bookings" from "request failed."
- **Where:** `pages/rate-review/index.js:39-41`
- **WCAG:** N/A
- **Impact:** Users with failed fetches see "No reviews yet" and may think they have no booking history.
- **Recommendation:** Add an error state:
  ```js
  const [fetchError, setFetchError] = useState(null);
  // in catch:
  setFetchError('Unable to load your bookings. Please try again.');
  // in render:
  {fetchError && <div role="alert" className="text-red-600 p-4">{fetchError}</div>}
  ```

---

### [FE-22] `handleReviewCreated` uses `review?.data?.slug` check but redirects on `booking_item_slug` (Priority: P2)
- **What:** In `[...slug].js:71-76`, the success guard is `if (review?.data?.slug)` but the redirect uses `review.data.booking_item_slug`. If `booking_item_slug` is null/undefined but `slug` exists, the push creates `/rate-review/undefined`.
- **Where:** `pages/rate-review/submit-review/[...slug].js:71-76`
- **WCAG:** N/A
- **Impact:** User is redirected to a broken URL after successful submission.
- **Recommendation:** Guard on the field actually used:
  ```js
  if (review?.data?.booking_item_slug) {
    router.push(`/rate-review/${review.data.booking_item_slug}`);
  }
  ```

---

## Auth State Analysis

### Authenticated flow
- `useEffect` in `index.js` checks `!session?.accessToken && status !== 'loading'` before calling `handleUnauthenticated()`. This is correct — it avoids redirect during NextAuth's loading phase.
- However, there is a brief flash: `loading` is initialized to `false` (not `true`), so on first render with `status === 'loading'`, the page renders the full layout (breadcrumb, empty section) before the effect fires. Fix: initialize `loading` to `true` or check `status === 'loading'` before rendering.
- The `useEffect` dependency array includes `router` (unused inside the effect — see FE-11).

### Guest flow
- `useAuthRedirect.js` redirects to `/api/auth/signin?callbackUrl=<encoded-path>`. This is the NextAuth sign-in page, which is correct.
- The `callbackUrl` uses `router.asPath` — this correctly preserves the full path including query strings.
- **Loading flash exists**: `loading` starts as `false`. On mount, React renders the empty page layout before the effect fires and calls `handleUnauthenticated()`. Users on slow connections briefly see the breadcrumb and empty container before being redirected. Mitigation: set `const [loading, setLoading] = useState(status === 'loading' || !session)` to show skeleton immediately.
- **Guest on `/rate-review/submit-review/[token]`**: The submit-review page does NOT call `useAuthRedirect` and does NOT check `session`. It fetches booking data via token only (no auth header). `ReviewForm` sends `Authorization: Bearer ${session?.accessToken || ''}` — if `session` is null, the header is `Authorization: Bearer ` (empty string). Whether the backend accepts this depends on backend token-review policy. This is ambiguous — if token-based reviews are meant to be accessible to unauthenticated users (email-invited reviewers), the backend must accept empty bearer tokens, but the form never informs the guest that they are submitting unauthenticated.

---

## Code Quality Issues

| Issue | Location | Type |
|-------|----------|------|
| Dead import `ReviewList` | `index.js:6` | Dead code |
| `router` in `useEffect` deps — unused | `index.js:48` | Lint violation |
| Duplicate `return normalized` statement | `[reviewSlug].js:231-233` | Dead code / copy-paste error |
| Entire `[reviewSlug].js` has 137-line commented-out block at top | `[reviewSlug].js:1-136` | Dead code |
| `useRouter` from `next/navigation` (App Router) in Pages Router component | `BookingReviewList.js:2` | Wrong router API |
| `#3b5998` hardcoded color bypasses design system | `[...slug].js:100` | Design system drift |
| `#FFA000`, `#D1D5DB` hardcoded star colors | `RateAndReviewForm.js:133,141` | Design system drift |
| `setError(error?.response?.data?.detail)` can set `undefined` | `RateAndReviewForm.js:90` | Silent failure bug |
| `onClose` called without null guard | `RateAndReviewForm.js:270` | Defensive programming gap |
| `slug === 1` check is fragile — `slug.length === 1` discards multi-segment paths silently with no user message explaining why | `[...slug].js:45-64` | UX gap |
| Loading spinner in `[...slug].js` uses unstyled `<CircularProgress />` (no `COLORS.brand.primary` sx) | `[...slug].js:80-85` | Design inconsistency |

---

## Top 3 Quick Wins

1. **Fix XSS in `[reviewSlug].js`** (FE-01) — one-line fix, copy the DOMPurify pattern already used in `ReviewList.js`. Highest severity item, zero architectural change required.

2. **Fix `parseISO(null)` crash guard** (FE-03) — add null checks in `BookingReviewList.js` sort comparator and render. Prevents entire Rate & Review page from going blank on any bad API record. Two-line fix.

3. **Fix missing leading slashes in `router.push` + wrong router import** (FE-14) — change `next/navigation` to `next/router` and prepend `/` to both push paths. Prevents broken navigation on the core user action (clicking "Write Review" or "View Review" buttons).

---
*Audit completed 2026-06-06 · Branch: 260606-fix/heic-review-upload*
