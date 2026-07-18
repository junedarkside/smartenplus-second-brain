# Progressive Reveal Batch Pattern

## Summary
Large card grids: render first 24, auto-load +24 via IntersectionObserver sentinel. No virtualization library below ~2000 items.

## Context
`/trips` index renders up to 1000+ route cards. Mounting all at once = long paint, high memory on mobile, hundreds of lazy `<Image>` requests queued.

## Details

```js
const REVEAL_BATCH = 24;
const [visibleCount, setVisibleCount] = useState(REVEAL_BATCH);
const sentinelRef = useRef(null);

const visibleRoutes = filteredRoutes.slice(0, visibleCount);
const hasMore = visibleCount < filteredRoutes.length;

useEffect(() => {
  if (!hasMore || !sentinelRef.current) return;
  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) setVisibleCount((c) => c + REVEAL_BATCH);
    },
    { rootMargin: '400px' } // pre-trigger before sentinel visible — no scroll stall
  );
  observer.observe(sentinelRef.current);
  return () => observer.disconnect();
}, [hasMore]);
```

Sentinel after grid: `{hasMore && <div ref={sentinelRef} aria-hidden="true" className="h-1" />}`. Plus "Showing X of Y" text below.

**Key rule:** reset `visibleCount` to `REVEAL_BATCH` *inside* search/sort handlers — NOT in a `useEffect` watching those states. Project forbids effect chains (B-depends-on-A); handler reset is synchronous and can't loop.

## Tradeoffs
- react-window/react-virtual rejected as over-engineering below ~2000 items — batch reveal keeps DOM bounded (~visible batches only), no absolute-positioning complexity, no scroll-restoration bugs.
- SEO: only first batch in SSR HTML — acceptable because JSON-LD ItemList carries the full (capped) list; crawlers don't need 1000 rendered cards. See [[jsonld-itemlist-cap-pattern]].

## Related
[[trips-page-redesign]] · [[slim-isr-payload-pattern]] · [[jsonld-itemlist-cap-pattern]]
