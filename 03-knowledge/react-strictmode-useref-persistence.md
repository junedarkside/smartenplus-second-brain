# React StrictMode + useRef Persistence

## Summary
useRef state persists across StrictMode simulated remount (setup → cleanup → setup). Mount-only guards via `didMountRef.current = true` get bypassed on the second setup, firing effects only in dev.

## Context
React 18.3.1 with `reactStrictMode: true` in `next.config.js`. Components mount in StrictMode replay every effect twice. Any effect relying on a `useRef` flag to fire exactly once WILL fire twice on mount.

## Problem
Mount-only guard pattern:
```js
const didMountRef = useRef(false);
useEffect(() => {
  if (!didMountRef.current) { didMountRef.current = true; return; }
  doExpensiveThing();
}, [dep]);
```
First setup: ref set true, return. Cleanup. **Second setup: ref already true, guard bypassed, `doExpensiveThing()` fires.** Looks correct, fires once, wrong under StrictMode.

Real consequence: `components/activities/shared/ActivitySearch.js:35-38` debounce effect second setup fired `updateFilter('search', '')`, which reset page to 1 via `setFilters({...prev, search:'', page:1})`.

## Decision
Never use `useRef` to gate "fire only on real subsequent change" effects. Make effects **idempotent** — guard at the side-effect target (e.g. no-op setState check in hook), not at the effect. `useRef` guards belong only inside the effect for cross-render state (timers, abort controllers), not as mount-once flags.

## Tradeoffs
- Pro: works identically in dev (StrictMode) and prod
- Pro: removes an entire class of subtle mount-only bugs
- Con: harder to spot in single-component review (no obvious "skip first" pattern)

## Related
- [[react-state-no-op-guard-side-effect-prevention]] — the idempotence pattern
- [[nextjs-hydration-rules]] — broader Next.js patterns
- [[react-dual-hook-url-race]] — related URL-sync + filter hook patterns
