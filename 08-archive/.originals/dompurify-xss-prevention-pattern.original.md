# DOMPurify XSS Prevention Pattern

## Summary
User-generated content rendered via `dangerouslySetInnerHTML` must be sanitized server-side or with SSR-safe client library. Plain `DOMPurify` throws `window is not defined` on SSR (Next.js).

## Context
`homepage-ux-review.md`. Critical issue C1. `ReviewFirstPage.js:185` renders `reviewText` via `dangerouslySetInnerHTML` with no sanitization.

## Problem
```jsx
// ReviewFirstPage.js:185 — XSS vulnerability
dangerouslySetInnerHTML={{ __html: reviewText }}
```
`reviewText` is user-generated content rendered raw. Active XSS risk.

## Decision

### Option A: Sanitize at API/Backend (Preferred)
Backend sanitizes before storing. API serves clean HTML. No client-side sanitization needed.

### Option B: SSR-safe client sanitization
```jsx
import DOMPurify from 'isomorphic-dompurify';

const sanitized = DOMPurify.sanitize(reviewText);
dangerouslySetInnerHTML={{ __html: sanitized }}
```

**Why `isomorphic-dompurify`:** Plain `DOMPurify` accesses `window` directly. Next.js SSR renders components on the server where `window` is undefined. `isomorphic-dompurify` detects the environment and falls back gracefully.

### Option C: No dangerouslySetInnerHTML
If content is plain text (not HTML), render as text node:
```jsx
// Safe — no HTML rendering
<span>{reviewText}</span>
```

## Details

### isomorph ic-dompurify Installation
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
Travel reviews typically need: `b`, `i`, `em`, `strong`, `a`, `p`, `br`, `ul`, `ol`, `li`. Strip everything else (scripts, iframes, etc.).

## Tradeoffs
- Option A (backend sanitize) is most robust — sanitization happens once at write time
- Option B adds client-side processing overhead — minimal for short review texts
- Option C is not viable if reviews contain formatting HTML

## Consequences
- XSS vector eliminated
- `isomorphic-dompurify` adds ~15KB gzipped — acceptable for review pages
- Backend should still validate/sanitize at API boundary regardless of frontend approach

## Related
- [[homepage-ux-review]] — XSS issue details
- [[dompurify-xss-prevention-pattern]] — security patterns
