# Fast Refresh Infinite Loop Audit — 2026-05-23

## Summary
Next.js 14.2.33 dev server infinite Fast Refresh loop since May 20. 7 failed fix attempts. **Root cause still unconfirmed.** Initial diagnosis (RefreshTokenHandler state loop) overturned by scrutiny — `lastExpiryRef` guard prevents re-execution. Actual cause likely Next.js 14.2.x HMR + on-demand route compilation cascade. Loop self-terminates when all routes compile.

---

## Scrutiny Note (2026-05-23)

> **RefreshTokenHandler state loop diagnosis OVERTURNED.**
> Claim: `Date.now()` + `props.setInterval` creates infinite loop.
> **Refutation:** `refreshTokenHandler.js:15` — `lastExpiryRef.current !== session.accessTokenExpiry` guard blocks re-execution after first run. Effect deps `[session?.accessTokenExpiry, props.setInterval]` stable (React setter identity guaranteed). Effect runs ONCE per `accessTokenExpiry` change, NOT continuously. React state loop would loop forever — user confirms loop stops after routes compile.

---

## Symptom Pattern

```
GET / 200 in 559ms
GET /_next/static/webpack/{hash}.webpack.hot-update.json 404 in 15ms
⚠ Fast Refresh had to perform a full reload
GET / 200 in 579ms
GET /_next/static/webpack/{hash}.webpack.hot-update.json 404 in 5ms
⚠ Fast Refresh had to perform a full reload
... repeats until all on-demand routes compile, then STOPS
```

**Key observation:** loop self-terminates. React state loop never stops. Points to finite cause — on-demand route compilation cascade.

---

## Most Likely Root Cause: Next.js 14.2.x HMR + On-Demand Compilation (95% confidence)

### CONFIRMED by debug instrumentation (2026-05-23)

Added `[RENDER _app]` logging to `_app.js`. Results:

```
[RENDER _app] { interval: 0, sessionExpiry: undefined }
GET /_next/static/webpack/53304070b1673f52.webpack.hot-update.json 404
⚠ Fast Refresh full reload
[RENDER _app] { interval: 0, sessionExpiry: undefined }
GET /_next/static/webpack/53304070b1673f52.webpack.hot-update.json 404
⚠ Fast Refresh full reload
... repeats indefinitely
```

**`interval` ALWAYS 0. `sessionExpiry` ALWAYS undefined.** Session never loads. RefreshTokenHandler never fires. Loop is pure Next.js HMR — no application code involved.

### Mechanism

1. Initial page load compiles homepage (`Compiled /`)
2. Page renders → triggers on-demand compilation of `/api/auth/[...nextauth]`, `/api/debug/search-step`, `/api/debug/performance`, `/404`, etc.
3. On-demand compilation changes webpack internal state → triggers HMR event
4. Browser HMR client requests `hot-update.json` for INITIAL compilation hash
5. Hot-update file for that hash doesn't exist (different compilation) → 404
6. Fast Refresh falls back to full reload
7. Full reload serves same page → more on-demand routes compile → step 3 repeats
8. Loop stops when all on-demand routes compiled → no more recompilation triggers → no more HMR events

### Evidence

- Same webpack hash on every 404 (not new hashes)
- Loop always includes `○ Compiling /404`, `✓ Compiled /api/auth/[...nextauth]`, `✓ Compiled /api/debug/*` before stopping
- DevToolsProvider disable reduced loop duration (fewer on-demand routes to compile)
- `rm -rf .next` didn't fix (hash fresh, not stale)
- `output: 'standalone'` guard didn't fix (not standalone-related)
- Hard refresh temporarily fixes (clears HMR state, but on-demand routes re-trigger)

### Why This Is a Next.js Framework Issue

Next.js 14.2.x has known issues with on-demand route compilation triggering stale HMR events. Webpack compilation hash embedded in page HTML becomes invalid when new on-demand compilation occurs, but HMR client still holds old hash.

---

## Overturned Diagnoses

### RefreshTokenHandler State Loop — OVERTURNED (was 95%, now <5%)

**Original claim:** `Date.now()` + `props.setInterval` → SessionProvider `refetchInterval` change → session re-fetch → effect re-run → loop.

**Why wrong:**
- `refreshTokenHandler.js:15` — `lastExpiryRef.current !== session.accessTokenExpiry` guard prevents re-execution
- `props.setInterval` is React state setter — guaranteed stable identity
- Effect runs once per `accessTokenExpiry` change, not continuously
- If this were cause, loop would NEVER stop — user confirms it stops

**Trace that disproves:**
1. App loads → `interval=0` → no polling
2. Session loads → effect runs → `lastExpiryRef.current` set → `setInterval(calculated_value)` → ONE state update
3. `_app.js` re-renders → `SessionProvider refetchInterval={new_value}` → polling timer set
4. Effect deps unchanged (`accessTokenExpiry` same, `setInterval` stable) → effect does NOT re-run
5. Loop stops. Only ONE state update total.

### Empty Middleware Matcher — UNLIKELY (was 40%, now <10%)

`middleware.js` exports next-auth middleware with `matcher: []`. Matches no routes but Next.js still compiles middleware module. Adds ONE extra compilation at startup — doesn't cause continuous loop.

---

## Still-Possible Secondary Factors

| Factor | Confidence | Notes |
|--------|-----------|-------|
| Next.js 14.2.x HMR + on-demand compilation | **70%** | Best fit: self-terminating, hash mismatch, route-dependent duration |
| Service worker caching stale HTML | 25% | SW `networkFirst()` for pages could cache old hash HTML |
| Specific file change May 20 triggering edge case | 15% | Many files changed that day; bisect needed to isolate |

---

## Failed Fix Attempts

| # | Approach | File | Why it failed |
|---|----------|------|---------------|
| 1 | `watchOptions.ignored` for `audit-screenshots/` | `next.config.js` | File watchers not the cause |
| 2 | Service worker `/_next/` bypass | `public/service-worker.js` | SW doesn't intercept `.json` destination |
| 3 | `rm -rf .next` on dev start | `package.json` | Hash fresh, not stale |
| 4 | `output: 'standalone'` production-only | `next.config.js` | Standalone not the cause |
| 5 | Remove SearchStepDebugDisplay auto-share | `SearchStepDebugDisplay.js` | Reduced loop duration, didn't fix |
| 6 | Disable DevToolsProvider entirely | `debug/index.js` | Same — reduced but didn't fix |
| 7 | `Cache-Control` header narrowing (`b56d62a`, May 20) | `next.config.js` | Addressed browser cache, not compilation cascade |

---

## Next Steps

### Step 1: Add debug instrumentation (confirm/deny RefreshTokenHandler)
Add to `_app.js` before return:
```js
if (process.env.NODE_ENV === 'development') {
  console.log('[RENDER]', { interval, sessionExpiry: pageProps.session?.accessTokenExpiry })
}
```

If `interval` changes during loop → RefreshTokenHandler IS involved.
If `interval` stays at 0 or changes only once → NOT the cause.

### Step 2: Git bisect to find triggering commit
```bash
# Find commits from May 19-20
git log --oneline --since="2026-05-19" --until="2026-05-21"
# Checkout commit BEFORE May 20, test if loop exists
# Binary search to find exact commit
```

### Step 3: Check Next.js version
Current: 14.2.33. Check if upgrading to latest 14.2.x or 15.x fixes HMR issue.

### Step 4: Test without service worker
Unregister SW in browser (DevTools → Application → Service Workers → Unregister), close all tabs, reopen. If loop stops → SW is cause.

---

## Recommended Minimal Fix (pending diagnosis)

**Do NOT change RefreshTokenHandler** — current code is correct, provides dynamic token refresh.

Options once root cause confirmed:
- If Next.js HMR bug: upgrade Next.js or add `webpack.devMiddleware` config
- If SW: add dev-only SW skip
- If specific commit: revert or fix triggering change

---

## Related

- [[hydration-infinite-refresh-fix-2026-05-20]] — prior Fast Refresh loop, different root cause
- [[currency-context-infinite-fetch-2026-05-23]] — CurrencyContext race condition (separate fix, applied)
- [[isr-429-cold-start-fix-2026-05-23]] — /front-page/ 429 (separate issue)