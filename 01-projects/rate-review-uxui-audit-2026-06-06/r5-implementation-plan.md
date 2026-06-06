# r5-implementation-plan — Release 1 Fix Spec
**Date:** 2026-06-06
**Branch:** `260606-fix/rate-review-p0`
**Source:** r3-leader-synthesis + r4-scrutinize corrections

---

## Release 1 — P0 Batch (ship together)

### Fix 1 — Stored XSS (P0-1) · `[reviewSlug].js`
**File:** `pages/rate-review/[reviewSlug].js`
**Pattern source:** `components/review/ReviewList.js:3,5,95`

Add after all imports at top of file:
```js
let DOMPurify = null;
if (typeof window !== 'undefined') {
  DOMPurify = require('dompurify');
}
```

Change line ~455:
```js
// Before:
dangerouslySetInnerHTML={{ __html: formattedText }}

// After:
dangerouslySetInnerHTML={{ __html: DOMPurify ? DOMPurify.sanitize(formattedText) : formattedText }}
```

---

### Fix 2 — parseISO(null) crash (P0-2) · `BookingReviewList.js`
**File:** `components/review/BookingReviewList.js`

Replace sort comparator (lines ~43-46):
```js
// Before:
return sortOrder === 'asc'
    ? compareAsc(parseISO(a.traveling_date), parseISO(b.traveling_date))
    : compareDesc(parseISO(a.traveling_date), parseISO(b.traveling_date));

// After:
const dateA = a.traveling_date ? parseISO(a.traveling_date) : new Date(0);
const dateB = b.traveling_date ? parseISO(b.traveling_date) : new Date(0);
return sortOrder === 'asc' ? compareAsc(dateA, dateB) : compareDesc(dateA, dateB);
```

Replace date render (line ~110):
```js
// Before:
{format(parseISO(booking.traveling_date), 'dd MMM yy')}

// After:
{booking.traveling_date ? format(parseISO(booking.traveling_date), 'dd MMM yy') : '—'}
```

---

### Fix 3 — Star rating ARIA (P0-3) · `RateAndReviewForm.js`
**File:** `components/RateAndReview/RateAndReviewForm.js:111-158`

Add `id="rating-label"` to the "Rating" Typography:
```jsx
// Before:
<Typography className="text-base font-semibold" style={{ color: COLORS.neutral.gray700 }}>
    Rating
</Typography>

// After:
<Typography id="rating-label" className="text-base font-semibold" style={{ color: COLORS.neutral.gray700 }}>
    Rating
</Typography>
```

Replace the star buttons container:
```jsx
// Before:
<div className="flex items-center gap-1">
    {[1, 2, 3, 4, 5].map((value) => (
        <IconButton
            key={value}
            onClick={() => setRating(value)}
            onMouseEnter={() => setHoverRating(value)}
            onMouseLeave={() => setHoverRating(0)}
            disabled={loading}
            aria-label={`Rate ${value} star${value !== 1 ? 's' : ''} - ${ratingLabels[value]}`}
            aria-pressed={value <= rating}
            sx={{ ... }}
        >

// After:
<div role="radiogroup" aria-labelledby="rating-label" className="flex items-center gap-1">
    {[1, 2, 3, 4, 5].map((value) => (
        <IconButton
            key={value}
            role="radio"
            aria-checked={value === rating}
            aria-label={`${value} star${value !== 1 ? 's' : ''} — ${ratingLabels[value]}`}
            onClick={() => setRating(value)}
            onMouseEnter={() => setHoverRating(value)}
            onMouseLeave={() => setHoverRating(0)}
            disabled={loading}
            sx={{ ... }}
        >
```

---

### Fix 4 — Router import + relative paths (P1-1) · `BookingReviewList.js`
**File:** `components/review/BookingReviewList.js`

Line 2:
```js
// Before:
import { useRouter } from 'next/navigation';

// After:
import { useRouter } from 'next/router';
```

Lines ~185-186:
```js
// Before:
router.push(isReviewed ? `rate-review/${booking.slug}/` : `rate-review/submit-review/${booking.token}`)

// After:
router.push(isReviewed ? `/rate-review/${booking.slug}` : `/rate-review/submit-review/${booking.token}`)
```

---

### Fix 5 — Email masking GDPR (P1-2) · `ReviewList.js`
**File:** `components/review/ReviewList.js:55`

```js
// Before:
{review.user_info.email}

// After:
{maskEmail(review.user_info.email)}
```

---

## Fix 6 — DEFERRED: Redirect guard mismatch (P1-3/FE-22)
**File:** `pages/rate-review/submit-review/[...slug].js:71-72`

**Must verify first:** Check `smartenplus-backend/dialogue/serializers.py` ReviewSerializer — does POST response return `slug` or `booking_item_slug`?

- If response has `slug` → change line 72: `router.push(\`/rate-review/${review.data.slug}\`)`
- If response has `booking_item_slug` → change line 71: `if (review?.data?.booking_item_slug)`

Do NOT implement until API shape confirmed.

---

## Sprint 1 Backlog (next session, after Release 1 ships)

See `r3-leader-synthesis.md` for full spec. Priority order:
1. P1-3 — post-submit guard + success banner (after FE-22 API verified)
2. P1-4 — guest redirect interstitial + session loading guard (`index.js`)
3. P1-5 — caption contrast `text-gray-400` → `text-gray-500` (2 files)
4. P1-6 — thumbnail keyboard access (`ReviewImageThumbnails.js`)
5. P1-7 — back button `aria-label` (2 page files)
6. P1-8 — submit button disabled feedback (`RateAndReviewForm.js`)
7. P1-9 — canonical URLs fix with `getSiteUrl()` (3 page files); `reviewSlug` confirmed in scope at `[reviewSlug].js:243`

---

## Test Checklist for Release 1

- [ ] `/rate-review` loads — booking list renders, sort toggle works
- [ ] "Write Review" button navigates to correct URL (no double-path `/rate-review/rate-review/...`)
- [ ] "View Review" button navigates to correct URL
- [ ] Star rating: keyboard Tab/Enter/Space selects stars; screen reader announces radiogroup
- [ ] Review detail page: view a review with `<script>` or `<img onerror>` in text — not executed
- [ ] Sort with a booking that has null `traveling_date` — list renders, doesn't crash
- [ ] `ReviewList` component: user email shows masked (e.g., `j***@example.com`)
- [ ] `npm run lint` passes on 4 changed files
