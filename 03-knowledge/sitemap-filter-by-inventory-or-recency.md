# Sitemap Filter By Inventory Or Recency

## Summary
Sitemap generation should filter routes by `available_routes_count > 0 || updated_at > 365 days ago` to stop feeding Googlebot new thin URLs without deindexing already-cached pages. Fully reversible. Deploy first (lowest risk) before any noindex changes.

## Context
When a transport platform has thousands of origin-destination pairs and only a fraction have active inventory, the sitemap becomes a thin-content factory. Every new (slug × schedule) combination creates a new URL, gets crawled, gets indexed, then sits empty for months. Search Console flags it as "Crawled - currently not indexed" or "Discovered - currently not indexed" and the cumulative signal drags down site quality.

## Problem
The blast-radius question for any sitemap change: "what if I'm wrong and a filtered URL was actually ranking?" The safe answer is to stop feeding the crawler new thin URLs (sitemap filter) without telling Google to deindex URLs it has already cached (noindex). Deindexing is irreversible in the short term; sitemap filtering is fully reversible in minutes.

## Details
Pre-flight Phase 1 filter, applied at sitemap generation:

```python
# In sitemap generator
def should_include(route):
    if route.available_routes_count > 0:
        return True
    if (now() - route.updated_at).days <= 365:
        return True  # recently updated, might have new schedules soon
    return False
```

The filter only affects what Googlebot discovers. Already-indexed URLs stay indexed until Google re-evaluates them (which is slow but safe). The OR with recency keeps "stale but maybe-coming-back" routes in the crawl queue.

Deploy order:
1. **Phase 1 (this rule):** filter the sitemap. Monitor Search Console for 7 days. No ranking risk.
2. **Phase 2:** add `<meta name="robots" content="noindex, follow" />` to Tier 2 pages. Monitor for 14 days.
3. **Phase 3:** consider canonical consolidation or 410 for persistently thin URLs.

## Decision
Sitemap filtering is always Phase 1. Never skip to noindex without first removing the URL from the sitemap. Never blanket-noindex before filter.

## Tradeoffs
- Pro: low-risk first move; reversible in minutes by reverting the filter.
- Pro: keeps "seasonal" routes in the crawl queue (recency clause).
- Pro: reduces crawl budget waste on thin pages.
- Con: doesn't fix already-indexed thin URLs — Phase 2 still needed eventually.
- Con: filter logic needs maintenance as business rules change (e.g., "what counts as active inventory").

## Consequences
- Search Console "Discovered - currently not indexed" count drops within a crawl cycle.
- Crawl budget goes to URLs that produce conversions, not empty pages.
- The phased approach becomes a template for any future content-quality intervention.

## Related
- [[isr-csr-overlay-stale-fields]] — the ISR-side analog: stale data is fine, destroyed cache is not.
- [[tiered-empty-page-noindex-strategy]] — Phase 2 of the same playbook.
- [[never-notfound-in-catch-block]] — protects the ISR cache during the rollout.
