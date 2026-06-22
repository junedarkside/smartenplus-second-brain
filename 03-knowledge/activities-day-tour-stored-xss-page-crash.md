---
name: activities-day-tour-stored-xss-page-crash
description: Stored XSS vulnerability in `/activities/detail/[slug]` review display + page crash from `parseISO(null)` on null date. Two Critical bugs from day-tour page audit.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: activities-day-tour-page-review
---

# Activities Day-Tour — Stored XSS + Page Crash

## Summary
Two Critical bugs: (1) stored XSS via `dangerouslySetInnerHTML` without DOMPurify on review content, (2) page crash from `parseISO(null)` when booking date is null.

## Why It Matters
**XSS:** Attacker injects malicious JS in review → executes for all viewers → account takeover, data theft. **Crash:** Entire page fails to render → zero conversions.

## Detail
**Bug 1 — Stored XSS:**
**Location:** `pages/activities/detail/[slug].js:455`
```jsx
<div dangerouslySetInnerHTML={{ __html: review.body }} />
```

No sanitization → attacker-controlled `review.body` executes JS.

**Fix:**
```bash
npm install dompurify
```
```jsx
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(review.body) }} />
```

**Bug 2 — Page crash:**
**Location:** `BookingReviewList.js:43-45`
```js
const bookingDate = parseISO(booking.created_at); // CRASH if null
```

If `booking.created_at` is `null`, `parseISO` throws → unhandled error → page crash.

**Fix:**
```js
const bookingDate = booking.created_at ? parseISO(booking.created_at) : null;
if (!bookingDate) return <span>Date unavailable</span>;
```

## Constraints / Gotchas
DOMPurify must be server-side + client-side (hydration mismatch risk). Default config safe for HTML; for rich-text from admin, allow `{ ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'] }`.

## Related
- [[activities-day-tour-page-review]] — parent audit (52 raw findings → 34 actionable)
