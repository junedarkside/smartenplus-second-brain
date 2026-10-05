# DRF Throttle Exemption for ISR Cache-Miss Storms

**Problem:** Default DRF `AnonRateThrottle` is `500/hour`. ISR pages with `fallback: 'blocking'` hammer the BE on cache miss + every ISR rebuild + every crawler. 500/hour quota exhausted in minutes on busy sites. After exhaustion: 429 → `getStaticProps` catches → historically `notFound:true` → ISR caches 404 → cache miss storm.

**Affected viewsets in SmartEnPlus:** ProductDetailViewSet (`/product-detail/{slug}/`), ProductSlugViewSet (`/product-slug/?limit=20` — used by `getStaticPaths`), FrontPageViewSet (`/front-page/`).

**Pattern:** Add `throttle_classes = []` to viewsets serving ISR/crawler traffic. Already-built precedent at `cards/views.py:200`.

```python
class ProductDetailViewSet(ModelViewSet):
    throttle_classes = []  # opt out of AnonRateThrottle
    ...
```

**Why safe:** Endpoints are read-only public data (contracts/slugs). Attacker value is low. Cache layer (Redis + Next.js ISR HTML) provides the actual rate protection.

**Verification:**
- Hit endpoint 600×/hour with anonymous requests → zero 429
- Compare to default settings: 500/hour hit + 1 = 429

**Related:** `getstaticprops-fetch-timeout-isr-blocking.md` (V1 catch-block pattern) — throttle + catch-block are complementary: throttle prevents quota exhaustion, catch-block prevents cache destruction on residual failures.

**Source:** Session #452, PR `fix/be-throttle-redis-guards`, commit `f95c657`.