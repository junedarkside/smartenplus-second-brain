# CurrencyContext Infinite Fetch Bug 2026-05-23

## Summary
Frontend hammers `/admin-dashboard-charge/forex/` + `/front-page/` + `/carts/` OPTIONS repeatedly. Hard reload fixes temporarily. Root cause **not** simple `useCallback`/`useEffect` circular dep — full trace below overturns initial diagnosis. Two separate issues. Neither fixed.

---

## Scrutiny Note (2026-05-23)

> **Initial diagnosis mechanically incorrect. Updated after full trace.**
> Initial claim: `useCallback([selectedCurrency])` + `useEffect([selectedCurrency, fetchRate])` creates infinite loop.
> **Refutation:** `useState` setter (`setSelectedCurrency`) stable. During fetch, `setLoading(true)` / `setCurrentRate(data)` do NOT change `selectedCurrency`. So `fetchRate` ref from `useCallback([selectedCurrency])` does NOT change mid-cycle. `useEffect` deps `[selectedCurrency, fetchRate]` remain stable. **Effect does NOT re-run in loop from this mechanism.**

---

## Two Actual Issues

### Issue A — Fast Refresh full reload loop (primary symptom driver)

**Symptom:** `⚠ Fast Refresh had to perform a full reload` repeating in dev console. Every full reload remounts entire app tree → 1 new `fetchForexData()` call + 1 `getStaticProps` `/front-page/` hit + 1 cart OPTIONS preflight.

**Mechanism:** `GET /_next/static/webpack/fc0ef4491715613d.webpack.hot-update.json 404`
- Browser holds stale compilation hash from before recompile
- Requests hot-update JSON for old hash → 404 (file no longer exists in memory)
- Next.js Fast Refresh falls back to full page reload
- Full reload triggers another compilation cycle if any watched file changed
- Stale hash → 404 → reload → compile → new hash → stale again → loop

**What triggers repeated recompilations in dev?** Not confirmed. Candidates:
1. Watched file written to disk during dev (e.g., log file inside `components/` or `pages/`)
2. `public/audit-screenshots/` receiving new files (Playwright audit scripts)
3. Some other process touching files in watched directory

**Evidence:** Frontend logs show `GET / 200` → `hot-update.json 404` → `Fast Refresh had to perform a full reload` → `GET / 200` repeating ~1/sec, synchronized with `/front-page/` and `/carts/` hits.

**Fix:** Identify what writes files to webpack's watched directories during dev. If `public/audit-screenshots/` culprit, add to `next.config.js` `watchOptions.ignored` or move screenshots outside project root.

---

### Issue B — CurrencyContext correctness issues (real bugs, not infinite loop)

**File:** `components/contexts/CurrencyContext.js`

**Bug B1 — No fetch cancellation / race condition on currency switch**

```js
// Current: no cleanup, no AbortController
const fetchRate = useCallback(async (currency = selectedCurrency) => {
  setLoading(true);
  const data = await fetchForexData(); // no cancellation
  setCurrentRate(selectedData);        // stale closure if currency switched mid-flight
}, [selectedCurrency]);
```

User switches currency quickly (THB → USD → EUR) → three concurrent fetches race. Last to resolve wins regardless of order. Can show wrong currency rate.

**Bug B2 — `selectCurrency` missing from `useMemo` deps**

```js
const value = useMemo(() => ({
  currentRate, loading, error,
  selectCurrency,       // ← included in object
}), [currentRate, loading, error]); // ← selectCurrency NOT in deps
```

`selectCurrency` plain function (new ref every render) included in memoized value but not in deps. Not causing loop — `selectCurrency` only calls `setSelectedCurrency` (stable) so captures correct ref. But violates React deps rules, causes lint warnings. Consumers putting `selectCurrency` in own `useCallback`/`useMemo` deps get new ref on every context recompute.

**Bug B3 — `fetchRate` exposed via `useCallback` but not in context value**

`fetchRate` created but never exposed. `useCallback` wrapper adds unnecessary complexity with no benefit. Only used inside file's own `useEffect`.

---

## Correct Fix

### Fix A — Identify and stop file writes in watched dir

```bash
# Run in dev, watch what changes:
fswatch -r /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/pages \
           /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/components \
           /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/public \
  --exclude='\.next' 2>/dev/null
```

If `public/audit-screenshots/` writing during dev, add to `next.config.js`:
```js
// next.config.js
webpack: (config, { dev }) => {
  if (dev) {
    config.watchOptions = {
      ...config.watchOptions,
      ignored: [...(config.watchOptions?.ignored || []), '**/public/audit-screenshots/**'],
    };
  }
  return config;
}
```

### Fix B — Clean up CurrencyContext (correctness, not loop prevention)

**File:** `components/contexts/CurrencyContext.js` — only this file changes.

```js
// BEFORE (current): no cancellation, unstable selectCurrency ref in memo
const fetchRate = useCallback(async (currency = selectedCurrency) => {
  setLoading(true); setError(null);
  const data = await fetchForexData();
  const selectedData = data.find((item) => item.currency === currency);
  if (selectedData) { setCurrentRate(selectedData); } else { setError('Currency not found'); }
  setLoading(false);
}, [selectedCurrency]);

useEffect(() => { fetchRate(); }, [selectedCurrency, fetchRate]);

const selectCurrency = (currency) => { setSelectedCurrency(currency); };

const value = useMemo(() => ({
  currentRate, loading, error, selectCurrency,
}), [currentRate, loading, error]);
```

```js
// AFTER: cancellation guard, stable selectCurrency, correct deps
const selectCurrency = useCallback((currency) => {
  setSelectedCurrency(currency);
}, []);

useEffect(() => {
  let cancelled = false;
  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchForexData();
      if (cancelled) return;
      const selectedData = data.find((item) => item.currency === selectedCurrency);
      setCurrentRate(selectedData ?? null);
      if (!selectedData) setError('Currency not found');
    } catch (err) {
      if (!cancelled) setError(err.message);
    } finally {
      if (!cancelled) setLoading(false);
    }
  }
  load();
  return () => { cancelled = true; };
}, [selectedCurrency]); // stable dep, no function ref

const value = useMemo(() => ({
  currentRate, loading, error, selectCurrency,
}), [currentRate, loading, error, selectCurrency]);
```

Remove `fetchRate` `useCallback` entirely.

---

## Consumers (19 files — no API change needed)

`useCurrency()` returns same shape `{ currentRate, loading, error, selectCurrency }`. No consumer changes.

Key consumers:
- `components/UI/CurrencySelector.js` — calls `selectCurrency` on user click
- `components/trips/FilterTrip.js:150` — `currentRate` in `useMemo` deps (benefits from stable ref)
- `components/itinerary/TripDetail3.js`
- `components/trips/TripItem.js`
- `pages/checkout/PaymentComponent.js`
- `pages/checkout/TotalCartSummary.js`
- (+13 more)

---

## Investigation Order

1. **First: diagnose Fast Refresh loop** — `fswatch` or add console.log to webpack `watchOptions.ignored` callback, identify which file triggers recompile. Fix first — accounts for most backend log noise.
2. **Then: apply CurrencyContext Fix B** — correctness fix, stops race condition, cleans deps.

---

## Branch

Not yet started. Create: `260523-fix/currency-context-infinite-fetch`

---

## Related

- [[hydration-infinite-refresh-fix-2026-05-20]] — prior Fast Refresh loop, different root cause (hydration mismatch)
- [[nextjs-patterns]] — useEffect dep rules, ISR dev behavior
- [[isr-429-cold-start-fix-2026-05-23]] — /front-page/ 429 (separate issue, same endpoint)