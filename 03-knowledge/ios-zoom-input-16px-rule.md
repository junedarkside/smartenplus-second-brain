---
name: ios-zoom-input-16px-rule
description: iOS Safari auto-zooms on inputs <16px font-size. Rule: all form inputs use text-base (16px) minimum.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06-overview
---

# iOS Zoom Input 16px Rule

## Summary
iOS Safari auto-zooms the viewport when focusing an input with font-size <16px. Fix: all form inputs use `text-base` (16px) minimum. Enforce via `INPUT_CONFIG.base` in designSystem.js.

## Context
Audit MM1: search inputs in `ProductSearchForm2.js:231, 260, 283, 311, 329` and `SearchDialogTrigger.js:19` use `text-sm` (14px). 1 input at 16px (the `INPUT_CONFIG.base` token). Triggers broken mobile UX.

## Problem
iOS Safari auto-zoom on focus causes layout shift, scroll jump, and user frustration. Bug is platform-specific (iOS only) and easy to miss in Chrome/Firefox testing.

## Pattern
**Bad** (iOS zoom trigger):
```jsx
<input className="text-sm ..." />  {/* 14px */}
```

**Good** (no zoom):
```jsx
<input className="text-base ..." />  {/* 16px */}
```

**Enforcement** (`helpers/designSystem.js:188`):
```js
export const INPUT_CONFIG = {
  base: 'w-full px-4 py-3 text-base border border-gray-200',  // text-base = 16px
  // ...
};
```

## Decision
Replace `text-sm` → `text-base` in all form inputs. Update `INPUT_CONFIG.base` to enforce globally. Add to CLAUDE.md form-layout rule.

## Tradeoffs
- **Pro:** Fixes iOS auto-zoom (mobile UX critical)
- **Pro:** 1-line fix, low risk
- **Con:** Visual change is <2px (negligible)
- **Con:** Larger inputs may overflow small viewports (320px)

## Consequences
Test at iOS Safari 17+ before merge. Reference [[form-layout]] for input sizing patterns.

## Related
[[website-audit-full-2026-06-06-overview|website-audit-full-2026-06-06]] · [[r1-mobile-ux]] · [[r3-leader-synthesis]]
