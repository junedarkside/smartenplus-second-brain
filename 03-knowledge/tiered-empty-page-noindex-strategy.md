# Tiered Empty Page Noindex Strategy

## Summary
For ISR pages with potentially-empty inventory, use a three-tier model: Tier 1 (route not in DB) → `notFound: true` + `revalidate: 300`; Tier 2 (route exists, zero active schedules) → `200` + `noindex: true` + `revalidate: 3600`; Tier 3 (active inventory) → fully indexed. Backend must distinguish: 404 for nonexistent, 200 `{routes: [], route_exists: true}` for empty.

## Context
Transport routes are seasonal. A Phuket→Krabi route that has zero active schedules during monsoon season is still a real, valid route in the database. Returning `notFound: true` for it destroys the ISR cache, drops the URL from Google's index, and means a search for "Phuket to Krabi transport" returns nothing during the very months travelers are searching.

## Problem
The "monsoon season anti-pattern" — blanket `notFound: true` for any route with empty inventory — was the most-cited SEO incident in the vault. The blanket approach destroyed seasonal route rankings, then required multi-month reindexing when the route came back online. Blanket noindex (Tier 1 for all empty) is the opposite mistake: it leaves thousands of thin URLs indexed.

## Details
Backend must expose the distinction:

```python
# /api/routes/{slug}/
# 404 if route slug doesn't exist in DB at all
# 200 with body if route exists, regardless of schedule count
def get_route(slug):
    route = Route.objects.filter(slug=slug).first()
    if not route:
        return JsonResponse({}, status=404)
    return JsonResponse({
        'route': route.data,
        'schedules': route.active_schedules(),
        'route_exists': True,  # explicit signal
    })
```

Frontend `getStaticProps` implements the three tiers:

```js
const res = await fetch(`/api/routes/${slug}/`);
if (res.status === 404) {
  return { notFound: true, revalidate: 300 };
}
const data = await res.json();
if (data.schedules.length === 0) {
  return {
    props: { data, isEmpty: true },
    revalidate: 3600,
  };
}
return { props: { data, isEmpty: false }, revalidate: 600 };
```

Tier 2 pages render a "no trips available, check back soon" empty state with `<meta name="robots" content="noindex, follow" />` injected via `<NextSeo>`. They stay in the ISR cache, serve fast, and don't compete in SERPs.

## Decision
Mandate the three-tier model. Reject blanket `notFound` or blanket `noindex` for any route/inventory page. Backend API contract must include `route_exists` (or equivalent) so the frontend can distinguish Tier 1 from Tier 2.

## Tradeoffs
- Pro: seasonal routes keep their rankings through empty windows.
- Pro: nonexistent routes are properly 404, not 200-with-empty (which Google penalizes).
- Pro: cache TTLs differ — Tier 2 changes less often, so longer revalidate is safe.
- Con: backend contract change requires frontend coordination; both repos need to ship.
- Con: three code paths in `getStaticProps` — needs good tests covering each tier.

## Consequences
- Search Console "Crawled - currently not indexed" count drops to near-zero for route pages.
- Reindexing pressure is gone — empty pages return to active state without re-crawl delay.
- The pattern extends to any inventory-driven page (tours, activities, hotels) with the same caveats.

## Related
- [[isr-csr-overlay-stale-fields]] — companion rule: stale data is better than cache destruction.
- [[docker-standalone-isr-revalidate-gap]] — relevant for self-hosted deployments where `revalidate` semantics differ.
- [[never-notfound-in-catch-block]] — the catch-block rule that protects Tier 2/3 from being demoted to Tier 1 on API errors.
