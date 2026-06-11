# Frontend Debug Utilities

## Summary
3 non-obvious utility patterns: useRateLimitedQuery global singleton, DevToolsProvider disabled by default, useAuth 100ms redirect delay.

## Context
Utility hooks and dev infrastructure. Non-obvious because they appear simple but have singleton state, disabled code paths, or timing assumptions.

## useRateLimitedQuery — Global Singleton (hooks/useRateLimitedQuery.js)

Single `rateLimitManager` class instance shared across ALL hook calls (lines 182-183):
```js
// Module-level singleton — not per-component, not per-user
const rateLimitManager = new RateLimitManager()
```

### Rate Limits per Type
```js
SEARCH:   30 req/min  // Trip search
FILTER:   60 req/min  // Browse page filters
LOCATION: 20 req/min  // Location autocomplete
BOOKING:  10 req/min  // Booking creation
```

### Retry with Jitter (line 125)
Adds randomized delay to prevent thundering herd when multiple tabs simultaneously hit limits:
```js
const delay = baseDelay * Math.pow(2, retryCount) + Math.random() * 1000
```

### Cleanup Interval
```js
setInterval(() => rateLimitManager.cleanup(), 5 * 60 * 1000)  // every 5 min
```
Cleans old request history. No per-window or per-user isolation — cross-tab interference possible if both tabs use same hook type simultaneously.

## DevToolsProvider — Disabled by Default (components/debug/index.js:67-87)

```js
export function DevToolsProvider({ children }) {
  if (!isDev) return children  // line 70: early return in prod
  // ...
}
```

Dev mode renders 3 floating panels + 1 full-page dashboard:
- Cart state panel
- Redux state inspector
- API request logger
- Full debug dashboard at `/debug`

All panels: `dynamic(import(...), { ssr: false })` — no hydration issues.

**Activation:** set `NODE_ENV=development` or `NEXT_PUBLIC_DEV_TOOLS=true`. Never active in prod.

## useAuth — 100ms Redirect Delay (hooks/useAuth.js:5-33)

```js
// Uses session === null check (not status === 'unauthenticated')
const { data: session } = useSession()

useEffect(() => {
  if (session === null) {
    // 100ms delay prevents race with session loading
    const timer = setTimeout(() => router.push('/login'), 100)
    return () => clearTimeout(timer)
  }
}, [session])
```

**Why `session === null` not `status`:
- `status === 'loading'` = session not yet determined
- `session === null` = determined, user is unauthenticated
- `status === 'unauthenticated'` would also work but this predates that API

**Why 100ms delay:**
- NextAuth fires session update asynchronously
- Without delay: brief null state during token refresh triggers redirect
- 100ms is arbitrary; could fail if API latency > 100ms on slow connections

**Risk:** logout detection (session → null transition) and "loading" phase look the same to this hook. May cause brief redirect flash then redirect back.

## Related
- [[nextauth-session-shape]] — session structure used by useAuth
- [[redux-store-architecture]] — store-level debug patterns
- [[rtk-query-advanced-patterns]] — rate limiting context (BOOKING type)
