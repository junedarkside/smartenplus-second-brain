# Core Web Vitals Budget (2026-06-06 Audit)

## Summary
Site-wide performance budget: HTML <100KB, all images WebP+AVIF, all scripts async/defer, no inline style blocks, font preload, explicit image dimensions.

## Why It Matters
Current page: 308KB HTML (3× budget), 10 sync scripts blocking FCP, 18 non-WebP images, 36/36 images missing `width`/`height` (CLS risk), no Inter font preload. Speed score 40/100.

## Detail

**Hard limits (page-level):**
- HTML size: < 100 KB (currently 308 KB)
- JS chunks: all `defer`/`async` or `next/script strategy="lazyOnload"` (currently 10/34 sync)
- Inline `<style>` blocks: 0 (currently 66 — carousel cards/sections inject CSS)
- Non-WebP images: 0 (currently 18/35 non-WebP)
- Images with explicit `width`/`height`: 100% (currently 0/36)
- Deferred stylesheet `data-href` patterns: 0 (causes FOUC)
- Third-party beacons (Cloudflare Insights etc.): 0 unless actively monitored

**Required infrastructure:**
- `<link rel="preload" as="font" href="/_next/static/media/...inter.woff2" crossorigin>` for Inter
- `<picture>` with AVIF source + WebP fallback for destination/carousel images
- CSS modules or global stylesheets — NO Tailwind arbitrary inline class chains that compile to `<style>` blocks
- `<Image>` from `next/image` always with `width` + `height` (or `fill` + sized parent)

**SEO additions:**
- `<meta name="keywords">` (Bing + Thai engines still use it)
- OG image served from CDN with cache headers (Next.js WebP may not render in FB/LINE crawlers)
- GTM preloaded if 1-2 tags (else inline)

## Constraints / Gotchas
- Tailwind arbitrary inline classes (e.g., `class="bg-[#abc123] p-[14px] w-[calc(100%-32px)]"`) compile to inline `<style>` blocks → each one is a render blocker. Use design tokens or CSS modules.
- `next/script` default is `afterInteractive` which can be a render blocker. Use `lazyOnload` for non-critical.
- Cloudflare Insights beacon adds ~50ms per page (DNS + latency) — remove if not used.
- Fragment heavy pages if single-page HTML > 100KB after compress + max SSG.

## Related
- [[website-audit-full-2026-06-06-overview]] (parent)
- [[hero-cls-precise-sizes-attribute]] (width/height requirement)
- [[mui-emotion-tailwind-injectfirst]] (66 inline styles root cause)
