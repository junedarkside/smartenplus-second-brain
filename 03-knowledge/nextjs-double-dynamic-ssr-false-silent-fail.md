---
name: nextjs-double-dynamic-ssr-false-silent-fail
description: Wrapping a dynamic(ssr:false) component in another dynamic(ssr:false) causes the inner component to silently fail to render. No error — just blank output. Fix: import the leaf component directly with one dynamic() call.
type: knowledge-atom
date: 2026-08-04
---

# Next.js Double dynamic(ssr:false) Silent Render Failure

## Problem

```js
// StandardBreadcrumb.js — wraps NextBreadcrumbs in dynamic(ssr:false)
const DynamicNextBreadcrumbs = dynamic(() => import('./NextBreadcrumbs'), { ssr: false });

// slug.js — wraps StandardBreadcrumb in another dynamic(ssr:false)
const DynamicStandardBreadcrumb = dynamic(() => import('../../components/UI/StandardBreadcrumb'), { ssr: false });
```

Result: component renders nothing. No error in console. No hydration warning. Silently blank.

## Root Cause

Two layers of `ssr: false` dynamic imports: outer resolves on client, then triggers inner dynamic load — timing/chunk resolution conflicts in Next.js pages router. The inner `dynamic()` never fires reliably.

## Fix

Import the leaf component directly — one dynamic layer only:

```js
// slug.js — import NextBreadcrumbs directly, skip the wrapper
const DynamicStandardBreadcrumb = dynamic(() => import('../../components/UI/NextBreadcrumbs'), { ssr: false });
```

## Rule

Never nest `dynamic(ssr:false)` inside another `dynamic(ssr:false)`. If a wrapper component exists solely to add `dynamic()`, bypass it and import the underlying component directly in the caller.

## Where It Happened

`pages/airport-transfer/[slug].js` → `components/UI/StandardBreadcrumb.js` → `components/UI/NextBreadcrumbs.js`.
Fixed 2026-08-04: import `NextBreadcrumbs` directly from `slug.js`.
