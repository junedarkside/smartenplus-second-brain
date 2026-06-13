# Never NotFound In Catch Block

## Summary
ISR `getStaticProps` catch blocks must NEVER return `{ notFound: true }` — that destroys the ISR cache during API failures/restarts. Always return `{ props: { data: [], error: '...' }, revalidate: 30 }` and let stale props serve.

## Context
A catch block signals "the upstream API failed." The page author's instinct is to mark the page as "doesn't exist" via `notFound: true` to avoid serving bad data. But for ISR, that destroys the cached page permanently until the next successful render — and during an API outage, no successful render happens, so the URL stays out of the cache indefinitely.

## Problem
The Tier 1/2/3 model in [[tiered-empty-page-noindex-strategy]] only works if `notFound: true` is reserved for genuine Tier 1 (route doesn't exist) responses. If catch blocks also return `notFound: true`, a 5-minute API hiccup demotes every cached page to "not found," dropping them from Google's index. The "monsoon season anti-pattern" — but caused by a deployment, not by season.

## Details
The wrong pattern:

```js
export async function getStaticProps({ params }) {
  try {
    const data = await fetchTrip(params.slug);
    return { props: { data }, revalidate: 600 };
  } catch (err) {
    return { notFound: true };  // DESTROYS ISR CACHE
  }
}
```

The right pattern:

```js
export async function getStaticProps({ params }) {
  try {
    const data = await fetchTrip(params.slug);
    return { props: { data, error: null }, revalidate: 600 };
  } catch (err) {
    // Stale props serve; UI shows a "couldn't refresh" banner.
    // The page is still cached, still indexed, still 200.
    return {
      props: { data: [], error: 'Failed to refresh' },
      revalidate: 30,  // retry frequently until upstream recovers
    };
  }
}
```

Pair with the [[getstaticprops-fetch-timeout-isr-blocking]] rule: explicit timeout on the fetch means the catch block fires within 8s, not 30s. Recovery is fast.

## Decision
One-line rule: no `notFound: true` in catch blocks. Lint rule or code-review checklist item. The only valid `notFound: true` site is the explicit Tier 1 check (404 status from upstream).

## Consequences
- API outages degrade gracefully (stale data with an error banner).
- ISR cache survives upstream failures.
- Recovery is automatic: as soon as the API returns 200, the next `revalidate` cycle populates fresh data.
- Indexing status is decoupled from API health — Google sees 200s, not 404s.

## Tradeoffs
- Pro: high-blast-radius failure mode is impossible by construction.
- Pro: simple to teach, simple to lint.
- Con: page may serve stale data during outages — needs an error banner UI to be honest.
- Con: requires the fetch itself to have a timeout; otherwise catch blocks fire after 30s.

## Related
- [[isr-csr-overlay-stale-fields]] — the umbrella pattern for serving stale data cleanly.
- [[tiered-empty-page-noindex-strategy]] — defines the only valid `notFound: true` site.
- [[getstaticprops-fetch-timeout-isr-blocking]] — pairs with this rule to make catch blocks fire fast.
