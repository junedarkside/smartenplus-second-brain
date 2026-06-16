# useEffect Cancellation Guard Pattern

## Summary
Async effect with potential races needs `let cancelled = false; ...; return () => { cancelled = true; };` cleanup, then check `if (cancelled) return;` after each await. Apply to any effect that calls setState after fetch.

## Context
On 2026-05-23 a `CurrencyContext` fetch effect appeared to cause an "infinite loop" in dev — every state change re-triggered the effect, which set state, which re-triggered it. Initial diagnosis blamed a missing dependency. Re-scrutiny (the 2nd pass by the skeptic reviewer) found the real bug: a stale-closure race between two overlapping fetches. The "loop" was actually a race where an older fetch's resolution overwrote newer state, retriggering downstream effects.

## Problem
The `useEffect` ESLint exhaustive-deps rule is necessary but not sufficient. It does not catch:
1. **Stale closure** — the effect captures `currency` from the first render; the second render's effect starts before the first resolves.
2. **Late setState after unmount** — React will warn but the state has already drifted.
3. **Re-entry race** — fast successive calls (currency change, language change) produce out-of-order responses.

## Details
The pattern that fixes all three:

```jsx
useEffect(() => {
  let cancelled = false;

  async function load() {
    setLoading(true);
    const rates = await fetchRates(currency);
    if (cancelled) return;          // first guard
    setRates(rates);
    setLoading(false);
  }

  load();

  return () => { cancelled = true; };
}, [currency]);
```

The `cancelled` flag is closure-captured per effect invocation. Each new effect run gets its own flag; the previous run's flag flips to `true` on cleanup, so its post-await `setState` calls are no-ops.

For multiple awaits, add a check after each one — anything that could trigger cleanup must be guarded.

## Decision
Standard pattern for all async effects in the codebase. ESLint rule `react-hooks/exhaustive-deps` remains mandatory; the cancellation guard is layered on top.

## Tradeoffs
- `AbortController` is more powerful (cancels the network request itself) but overkill for cheap fetches and harder to retrofit. Use `AbortController` only when the request is expensive.
- The flag is a manual discipline — easy to forget the post-await check. A custom `useAsyncEffect` hook (returning `{ data, error, loading }` and handling the guard internally) is a future refactor candidate.
- Strict Mode double-invocation in dev intentionally surfaces missing cleanups — if you see double-fetch warnings, you forgot the guard.

## Consequences
Reusable for: currency, locale, user-pref, theme, auth-context, feature-flag context. The cost of NOT using the pattern is intermittent state corruption that's nearly impossible to reproduce locally. The cost of using it is ~3 extra lines per effect. Net win.

## Related
- [[react-state-no-op-guard-side-effect-prevention]] — same family of state-hygiene patterns; pairs with the cancellation guard.
- `useAuthRedirect` patterns elsewhere — `useAuthRedirect` is one of the largest consumers of this pattern; the auth context is the canonical example.
