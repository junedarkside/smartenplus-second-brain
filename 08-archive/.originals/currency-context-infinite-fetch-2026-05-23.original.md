# CurrencyContext Infinite Fetch Bug 2026-05-23

## Summary
Frontend hammers `/admin-dashboard-charge/forex/` + `/front-page/` + `/carts/` OPTIONS repeatedly. Hard reload fixes temporarily. Root cause is **not** a simple `useCallback`/`useEffect` circular dep — full trace below overturns initial diagnosis. Two separate issues. Neither yet fixed.

---

## Scrutiny Note (2026-05-23)

> **Initial diagnosis was mechanically incorrect. Updated after full trace.**
> Initial claim: `useCallback([selectedCurrency])` + `useEffect([selectedCurrency, fetchRate])` creates infinite loop.
> **Refutation:** `useState` setter (`setSelectedCurrency`) is stable. During a fetch, `setLoading(true)` / `setCurrentRate(data)` do NOT change `selectedCurrency`. So `fetchRate` ref from `useCallback([selectedCurrency])` does NOT change mid-cycle. `useEffect` deps `[selectedCurrency, fetchRate]` remain stable. **Effect does NOT re-run in a loop from this mechanism.**

---

## Two Actual Issues

### Issue A — Fast Refresh full reload loop (primary symptom driver)

**Symptom:** `⚠ Fast Refresh had to perform a full reload` repeating in dev console. Every full reload remounts the entire app tree → 1 new `fetchForexData()` call + 1 `getStaticProps` `/front-page/` hit + 1 cart OPTIONS preflight.

**Mechanism:** `GET /_next/static/webpack/fc0ef4491715613d.webpack.hot-update.json 404`
- Browser holds a stale compilation hash from before a recompile
- Requests hot-update JSON for old hash → 404 (file no longer exists in memory)
- Next.js Fast Refresh falls back to full page reload
- Full reload triggers another compilation cycle if any watched file has changed
- Stale hash → 404 → reload → compile → new hash → stale again → loop

**What triggers repeated recompilations in dev?** Not confirmed yet. Candidates:
1. A watched file being written to disk during dev (e.g., a log file inside `components/` or `pages/`)
2. The `public/audit-screenshots/` directory receiving new files (Playwright audit scripts)
3. Some other process touching files in the watched directory

**Evidence:** Frontend logs show `GET / 200` → `hot-update.json 404` → `Fast Refresh had to perform a full reload` → `GET / 200` repeating ~1/sec, synchronized with `/front-page/` and `/carts/` hits.

**Fix:** Identify what is writing files to webpack's watched directories during dev. If `public/audit-screenshots/` is the culprit, add it to `next.config.js` `watchOptions.ignored` or move screenshots outside project root.

---

### Issue B — CurrencyContext correctness issues (real bugs, just not an infinite loop)

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

If user switches currency quickly (THB → USD → EUR), three concurrent fetches race. Last to resolve wins regardless of order. Can show wrong currency rate.

**Bug B2 — `selectCurrency` missing from `useMemo` deps**

```js
const value = useMemo(() => ({
  currentRate, loading, error,
  selectCurrency,       // ← included in object
}), [currentRate, loading, error]); // ← selectCurrency NOT in deps
```

`selectCurrency` is a plain function (new ref every render) included in the memoized value but not in deps. When the memo recomputes (loading/error change), it captures the current `selectCurrency` ref — which happens to be correct since `selectCurrency` only calls `setSelectedCurrency` (stable). So this is not causing a loop, but it violates React deps rules and will cause lint warnings. Consumers that put `selectCurrency` in their own `useCallback`/`useMemo` deps get a new ref on every context recompute.

**Bug B3 — `fetchRate` exposed via `useCallback` but not in context value**

`fetchRate` is created but never exposed. The `useCallback` wrapper adds unnecessary complexity with no benefit. Only used inside the file's own `useEffect`.

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

If `public/audit-screenshots/` is writing during dev, add to `next.config.js`:
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
- `components/trips/FilterTrip.js:150` — `currentRate` in `useMemo` deps (will benefit from stable ref)
- `components/itinerary/TripDetail3.js`
- `components/trips/TripItem.js`
- `pages/checkout/PaymentComponent.js`
- `pages/checkout/TotalCartSummary.js`
- (+13 more)

---

## Investigation Order

1. **First: diagnose Fast Refresh loop** — `fswatch` or add console.log to webpack `watchOptions.ignored` callback, identify which file triggers recompile. Fix that first since it accounts for most backend log noise.
2. **Then: apply CurrencyContext Fix B** — correctness fix, stops race condition, cleans deps.

---

## Branch

Not yet started. Create: `260523-fix/currency-context-infinite-fetch`

---

## Related

- [[hydration-infinite-refresh-fix]] — prior Fast Refresh loop, different root cause (hydration mismatch)
- [[nextjs-patterns]] — useEffect dep rules, ISR dev behavior
- [[isr-429-cold-start-fix]] — /front-page/ 429 (separate issue, same endpoint)
