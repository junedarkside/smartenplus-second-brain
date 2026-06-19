# GetStaticProps Fetch Timeout ISR Blocking

## Summary
`getStaticProps` `fetchData()` must have an explicit timeout (e.g., 8 seconds) when `fallback: 'blocking'` is enabled. Without timeout, a slow API on the first request to a new slug = Vercel Lambda 10–30s timeout = 500 error = never caches = every subsequent visitor gets the same 500.

## Context
`fallback: 'blocking'` is the standard ISR pattern for dynamic routes (`pages/trip/[slug].js`). The first request for an unseen slug blocks while `getStaticProps` runs. If the upstream API is slow, the Lambda hits its hard timeout and returns 500 — and the failure mode is worse than a normal 500 because the page never enters the cache.

## Problem
Production incident PROD-3 in `trip-detail-deep-review`: the upstream `/api/trips/{slug}/` service had a 25-second p99 during a traffic spike. `getStaticProps` had no internal timeout, so Vercel returned 500, the page never cached, and every visitor for the next hour triggered a fresh blocking render. Cache miss storm, not a 500 storm — much harder to detect.

## Details
Wrap every upstream `fetch` in `getStaticProps` with an explicit timeout:

```js
async function fetchTrip(slug) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(`${API}/trips/${slug}/`, { signal: controller.signal });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export async function getStaticProps({ params }) {
  try {
    const data = await fetchTrip(params.slug);
    return { props: { data }, revalidate: 600 };
  } catch (err) {
    // NEVER notFound in catch — see [[never-notfound-in-catch-block]]
    return { props: { data: null, error: err.message }, revalidate: 30 };
  }
}
```

Timeout budget: 8s leaves headroom under Vercel's 10s Lambda limit (Pro) and 30s (Enterprise). Tune per-route based on upstream p99.

## Decision
Mandatory explicit timeout on every `getStaticProps` fetch. Code review rejects `fetch()` calls in `getStaticProps` without an `AbortController` timeout.

## Tradeoffs
- Pro: bounded failure mode (one slug might 500; the rest of the site is fine).
- Pro: stale props serve cleanly during API degradation (see [[never-notfound-in-catch-block]]).
- Con: timeout value is a guess — too short causes false-positive failures on slow but valid responses.
- Con: AbortController doesn't cancel server work; it just stops waiting. The API still does the work.

## Consequences
- ISR routes become resilient to upstream API degradation.
- The pattern pairs with the never-notFound rule to avoid cache destruction.
- A future observability layer should track `getStaticProps` timeout frequency as a leading indicator.

## Related
- [[isr-csr-overlay-stale-fields]] — the companion rule: stale props are better than destroyed cache.
- [[never-notfound-in-catch-block]] — the catch-block rule that this timeout pattern enables.
- [[docker-standalone-isr-revalidate-gap]] — related ISR failure mode in self-hosted deployments.
