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
---

## Update 2026-08-25 (session #352)

**Option B (`isomorphic-dompurify`) does NOT work in Next.js Pages Router SSR.** Transitive deps include `jsdom → html-encoding-sniffer → @exodus/bytes/encoding-lite.js` (ESM-only). Pages Router SSR runs as CJS → `require()` of the ESM module throws `ERR_REQUIRE_ESM` → 500.

**Working pattern (Pages Router SSR):** use `dompurify` + manual JSDOM window:
```js
import DOMPurify from 'dompurify';

let serverPurify = null;
const getPurifier = () => {
  if (typeof window !== 'undefined') return DOMPurify;
  if (serverPurify) return serverPurify;
  const { JSDOM } = require('jsdom');
  const jsdomWindow = new JSDOM('').window;          // ← do NOT name this `window`
  serverPurify = DOMPurify(jsdomWindow);
  return serverPurify;
};
```

Two traps:
1. **ESM/CJS interop** — `isomorphic-dompurify` cannot be required in Pages Router SSR context (see above).
2. **Webpack-hoisted TDZ** — naming the local var `window` (shadowing the global) gets hoisted to module scope by webpack, putting the `const window` BEFORE the `typeof window` check and triggering `ReferenceError: Cannot access 'window' before initialization`. See [[webpack-hoisted-const-tdz-shadowing-globals]].

Verified live on `/locations/hatyai` after fix: 200, 141 KB, all 5 JSON-LD blocks (WebPage, BreadcrumbList, ItemList, TouristDestination, FAQPage) present in SSR HTML. Commits `e7bbfabe` + `24109412`.
