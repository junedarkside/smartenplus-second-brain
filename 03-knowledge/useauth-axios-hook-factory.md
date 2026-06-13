# useAuthAxios Hook Factory

## Summary
Replace inline `axios.create({baseURL, headers: {Authorization: 'Bearer ${token}'}})` (created every render) with `useAuthAxios()` hook — uses `useMemo([token])` for stable instance reference. Pass relative paths (not absolute) to instance methods.

## Context
During the 2026-06-08 favorite-heart analysis, a hydrate-time check (`/api/check/`) was firing 12× per card per render. Root cause: an inline `axios.create` inside the card component created a fresh instance on every render, each with the auth header re-resolved, and the useEffect dependency included the instance (or the token), so the fetch refired on every render. A 405 Method Not Allowed also surfaced because the same component was hitting an absolute URL `https://api.smartenplus.com/check/` instead of the relative path that respects the Next.js baseURL rewrite.

## Problem
Three compounding issues:
1. **Inline `axios.create` is recreated every render** — the useEffect can't stabilize on the instance.
2. **Instanced axios + absolute URL** — defeats the baseURL config and causes 405s on edge routes that don't allow CORS preflights on the absolute host.
3. **N+1 hydration storm** — 12 cards × N renders = N+1 `/check/` calls during hydration.

## Details
The hook factory:

```jsx
// hooks/useAuthAxios.js
import { useMemo } from 'react';
import axios from 'axios';
import { useSession } from 'next-auth/react';

export function useAuthAxios() {
  const { data: session } = useSession();

  return useMemo(() => {
    const instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
      headers: session?.accessToken
        ? { Authorization: `Bearer ${session.accessToken}` }
        : {},
    });
    return instance;
  }, [session?.accessToken]);
}
```

Usage in a card:

```jsx
const api = useAuthAxios();
useEffect(() => {
  api.get('/check/').then(...);   // RELATIVE path
}, [api, item.id]);
```

Key rules:
- Always pass **relative** paths to instance methods. The instance `baseURL` resolves them.
- The instance is stable until `accessToken` changes — re-fetches are intentional only on auth change.
- For guest paths, do NOT add the auth header at all (omit it conditionally).

## Decision
All auth-aware fetches go through `useAuthAxios()`. Inline `axios.create` in components is a code-review red flag. Skeptic Finding 7 from the favorite-heart analysis documented the relative-vs-absolute path gotcha.

## Tradeoffs
- A shared instance means request interceptors (e.g., for 401 refresh) attach globally — that's a feature, not a bug, but worth noting for tests that mock axios.
- `useMemo` with `[session?.accessToken]` is intentionally narrow: re-creating on session object identity churns would be worse than the original bug.
- The hook is React-only; SSR fetches in `getServerSideProps` need a separate server-side factory.

## Consequences
Reusable for any auth-aware fetch: profile, wishlist, cart, booking-history. The pattern eliminates an entire class of N+1 hydration storms and 405s. Audit script: `grep -rn "axios.create" components/ pages/ —exclude-dir=hooks` should return zero results.

## Related
- [[rtk-cart-tag-invalidation-auto-refetch]] — eventually we move to RTK Query; the auth instance becomes a `baseQuery` wrapper. Same hook boundary.
