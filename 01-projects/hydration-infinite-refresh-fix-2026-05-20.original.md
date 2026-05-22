# Hydration Infinite Refresh Fix — 2026-05-20

## Summary
Fixed infinite page refresh affecting ALL pages in SmartEnPlus frontend. Root cause: hydration mismatch in shared modules imported by `_app.js` → Next.js HMR enters error state → reloads every page.

## Context
Branch `260520-update/recommend-route`. Popular routes feature added new components (`PopularRoutesStructuredData`, `GridComponent` changes). After these changes, dev server showed infinite refresh on all pages — not just homepage. Diagnosed via 3-agent parallel investigation team + leader verification.

## Problem
Next.js HMR behavior: when any module imported (directly or transitively) by `_app.js` causes a hydration mismatch, HMR enters an error reload loop affecting ALL pages — not just the page rendering the mismatched component.

Four separate issues compounded:

### Issue 1 — Date.now() in render (P0)
**File:** `lib/homepage/components/PopularRoutesStructuredData.js`
`Date.now()` called during render → server timestamp ≠ client timestamp → hydration mismatch.

### Issue 2 — render-prop function not memoized (P1)
**File:** `components/UI/GridComponent.js`
`renderTripItem` defined inside component body → new function ref every render → `memo()` on `BaseGridComponent` bypassed → cascading re-renders.

### Issue 3 — Dual JSX tree via isClient (P1, all-page)
**File:** `pages/_app.js`
`isClient ? <PersistGate>...</PersistGate> : <...without PersistGate...>` → two different component trees → hydration mismatch on every single page.

### Issue 4 — Context value not memoized (P2)
**File:** `components/contexts/CurrencyContext.js`
`const value = { currentRate, loading, error, selectCurrency }` → new object ref on every render → all `useCurrency()` consumers re-render unnecessarily.

## Decision

Fixed all 4. Minimal changes — no new abstractions.

| File | Change |
|------|--------|
| `PopularRoutesStructuredData.js` | `Date.now()` → module-level `PRICE_VALID_UNTIL` constant |
| `GridComponent.js` | `renderTripItem` wrapped in `useCallback([locationImg])` |
| `pages/_app.js` | Removed `isClient` state + dual tree → single `PersistGate loading={null}` tree |
| `CurrencyContext.js` | `value` wrapped in `useMemo([currentRate, loading, error])` |

## Agent Investigation — What Was Real vs Hallucinated

3-agent team deployed in parallel. Leader verified each claim against actual code before accepting.

| Agent Claim | Verdict |
|-------------|---------|
| `Date.now()` in render = hydration mismatch | ✅ REAL |
| `renderTripItem` not memoized = memo bypass | ✅ REAL |
| `_app.js` isClient dual tree = all-page mismatch | ✅ REAL (pre-existing but now surfaced) |
| CurrencyContext value not memoized | ✅ REAL (pre-existing) |
| `router` from `useRouter()` = new object each render | ❌ WRONG — stable ref |
| `refetchOnMountOrArgChange: 300` = 300ms | ❌ WRONG — 300 seconds |
| CurrencyContext fetchRate = infinite loop | ❌ WRONG — loop stops after fetch |
| Math.random in error boundaries = render mismatch | ❌ WRONG — only fires on thrown error |
| `withComponent` HOC = infinite redirect loop | ⚠️ REAL BUG but HOC unused (all commented out) |

**Agent accuracy: ~55% true positive rate.** Leader verification step is mandatory — do not ship agent findings directly.

## Tradeoffs

**`PersistGate loading={null}` without isClient guard:**
- SSR-safe: PersistGate renders `null` during SSR, then children after client rehydration. Server HTML (no persisted state) = initial client render (also no persisted state) = no mismatch.
- Slight flash: on cold load, page renders without persisted Redux state for ~1 frame. `loading={null}` means that frame renders nothing (blank), then full page. Acceptable — same behavior as before but without mismatch.

## Consequences
- Hydration error eliminated → HMR stable
- All-page infinite refresh fixed
- CurrencyProvider no longer causes consumer re-renders on unrelated state changes
- `memo()` on BaseGridComponent now works as intended

## Related
- [[nextjs-patterns]] — Hydration Error Prevention rules derived from this investigation
- [[blog-seo-performance-2026-05-20]] — same session, prior fix (Blog HMR loop)
- [[recommendation-system]] — feature this branch is building
