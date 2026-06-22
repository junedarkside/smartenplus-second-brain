---
name: activities-day-tour-wrong-router-import
description: Wrong router import breaks "Write Review" CTA — using `next/router` instead of `next/navigation` (App Router incompatible). Import mismatch causes navigation failures.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: activities-day-tour-page-review
---

# Activities Day-Tour — Wrong Router Import

## Summary
Wrong router import breaks "Write Review" CTA — `next/router` instead of `next/navigation`. App Router incompatibility. Navigation failures.

## Why It Matters
"Write Review" button doesn't navigate → users can't submit reviews. Conversion blocker.

## Detail
**Bug pattern:**
```jsx
// WRONG — Pages Router import
import { useRouter } from 'next/router';
const router = useRouter();
const handleClick = () => router.push(`/activities/${slug}/review`);

// CORRECT — App Router import
import { useRouter } from 'next/navigation';
const router = useRouter();
const handleClick = () => router.push(`/activities/${slug}/review`);
```

Next.js 13+ App Router uses `next/navigation`. `next/router` is for Pages Router. Mixing imports = navigation broken.

**Why it happens:** Migration from Pages → App Router, some files missed import update.

## Constraints / Gotchas
Global search: `from 'next/router'` → replace with `from 'next/navigation'` EXCEPT in Pages Router pages (`pages/` directory).

## Related
- [[activities-day-tour-page-review]] — parent audit (P1 finding)
