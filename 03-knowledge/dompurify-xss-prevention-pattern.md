# DOMPurify XSS Prevention Pattern

## Summary
User-generated content via `dangerouslySetInnerHTML` must be sanitized server-side or with SSR-safe client library. Plain `DOMPurify` throws `window is not defined` on SSR (Next.js).

## Context
`homepage-ux-review.md`. Critical issue C1. `ReviewFirstPage.js:185` renders `reviewText` via `dangerouslySetInnerHTML` with no sanitization.

## Problem
```jsx
// ReviewFirstPage.js:185 — XSS vulnerability
dangerouslySetInnerHTML={{ __html: reviewText }}
```
`reviewText` user-generated, rendered raw. Active XSS risk.

## Decision

### Option A: Sanitize at API/Backend (Preferred)
Backend sanitizes before storing. API serves clean HTML. No client-side sanitization needed.

### Option B: SSR-safe client sanitization
```jsx
import DOMPurify from 'isomorphic-dompurify';

const sanitized = DOMPurify.sanitize(reviewText);
dangerouslySetInnerHTML={{ __html: sanitized }}
```

**Why `isomorphic-dompurify`:** Plain `DOMPurify` accesses `window` directly. Next.js SSR renders on server where `window` undefined. `isomorphic-dompurify` detects environment, falls back gracefully.

### Option C: No dangerouslySetInnerHTML
If content is plain text, render as text node:
```jsx
// Safe — no HTML rendering
<span>{reviewText}</span>
```

## Details

### isomorphic-dompurify Installation
```bash
npm install isomorphic-dompurify
```

### Usage Pattern
```jsx
import DOMPurify from 'isomorphic-dompurify';

// In component
const getSanitizedHTML = (dirty) => {
  if (!dirty) return '';
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
};

// Render
<div dangerouslySetInnerHTML={{ __html: getSanitizedHTML(reviewText) }} />
```

### Allowed Tags Configuration
Travel reviews need: `b`, `i`, `em`, `strong`, `a`, `p`, `br`, `ul`, `ol`, `li`. Strip all else (scripts, iframes, etc.).

## Tradeoffs
- Option A (backend sanitize) most robust — sanitization once at write time
- Option B adds client processing overhead — minimal for short review texts
- Option C not viable if reviews contain formatting HTML

## Consequences
- XSS vector eliminated
- `isomorphic-dompurify` adds ~15KB gzipped — acceptable for review pages
- Backend should still sanitize at API boundary regardless of frontend approach

## Additional Sites

Same pattern confirmed in `RateAndReviewForm.js` (rate review submission) and any future `dangerouslySetInnerHTML` over `contract.description` (long-form rich text from operators). Backend `sanitize_category_fields` does NOT touch description field — frontend sanitization remains the last line of defense.

## Related
- [[homepage-ux-review]] — XSS issue details (ReviewFirstPage.js:185)
- [[rate-review-uxui-audit-2026-06-06-overview]] r1-frontend — additional review-render sites
- [[dompurify-xss-prevention-pattern]] — security patterns