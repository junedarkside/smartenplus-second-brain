---
name: next-font-self-host-perf-pattern
description: Switch from render-blocking external CSS to next/font/google for self-hosted fonts. Eliminates 3rd-party DNS lookup + render-blocking CSS fetch.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06
---

# Next.js Font Self-Host Pattern

## Summary
Replace `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` in `_document.js` with `next/font/google` for FCP -0.3s to -0.5s.

## Context
Audit H2 finding: Inter font loaded via render-blocking stylesheet (`pages/_document.js:22`). Preconnect exists but no `<link rel="preload" as="font">`. Hand-rolled preload works but `next/font` is better.

## Problem
External font CSS blocks FCP. Google Fonts CSS triggers render-blocking fetch chain. 3rd-party DNS lookup adds 100-200ms.

## Pattern
**Before** (`pages/_document.js:20-22`):
```jsx
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

**After** (`pages/_app.js`):
```js
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], display: 'swap' });
// Apply: <main className={inter.className}>
```

**`tailwind.config.js`:**
```js
fontFamily: {
  sans: ['var(--font-inter)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
}
```

## Decision
Use `next/font/google` over hand-rolled preload. Auto-self-hosts, eliminates 3rd-party CSS, includes preload automatically.

## Tradeoffs
- **Pro:** FCP -0.3s, eliminates 3rd-party DNS, auto-preloads woff2
- **Pro:** No 3rd-party CSS blocking render
- **Con:** FOUT risk if `display: 'swap'` not set
- **Con:** Build time slightly longer (font subsetting)

## Consequences
Test CLS + FOUT in Lighthouse before merge. Reference [[nextjs-patterns]] for font-related gotchas.

## Related
[[website-audit-full-2026-06-06]] · [[r3-leader-synthesis]] · [[design-system-audit-2026-05-31]]
