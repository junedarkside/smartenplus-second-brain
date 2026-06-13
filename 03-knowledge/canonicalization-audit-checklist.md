# Canonicalization audit checklist

## Domains
- [ ] Scheme (HTTP→HTTPS 301 at origin)
- [ ] Host (non-www→www OR apex→www, single-hop)
- [ ] `test.*` subdomain 301 to www

## Per-page
- [ ] `<link rel="canonical" href="..." />` present
- [ ] Uses `NEXT_PUBLIC_DOMAIN` fallback (not env-specific baseURL)
- [ ] Strips query params (`.split('?')[0]`)
- [ ] Trailing slash consistent (match site policy)

## Parallel URLs
- [ ] `/locations/{slug}` vs `/destinations/{slug}` — if same content, one canonical + 301
- [ ] `/homepagev1`, `/homepagev2` → 301 to `/`
- [ ] `/trips/detail` → 301 to `/trips`
- [ ] `/blog/[slug]` vs WP subdomain source — canonical to canonical host

## Sitemap + robots
- [ ] robots.txt Disallow matches page protection intent
- [ ] Sitemap excludes private/duplicate/noindex pages
- [ ] Only canonical URLs in sitemap

## Checks per page type
Route search `/trips/{from}/{to}`: canonical stripped of query, www.domain
Trip detail `/trips/detail/{slug}`: NEXT_PUBLIC_DOMAIN base
Activity detail `/activities/detail/{slug}`: ditto (watch baseURL.replace — breaks easy)
Blog: WP source redirect + www
Locations/destinations: separate products but distinct intent

## Known gotchas
- `baseURL.replace('/api', '')` on `https://api.smartenplus.co.th` eats the first `api` in the scheme → `https:/.smartenplus.co.th`
- Homepage query string self-canonicalize `?utm_*`, `?gclid` if not stripped
- nginx must enforce 301s at origin (Cloudflare edge may mask)
- Deploy `NEXT_PUBLIC_DOMAIN` default must include https:// and www (not bare apex)

## Related
[[seo-sitemap-whole-site-audit-2026-06-11]] (P0-5, P0-6, P1-4 findings)

## Orphan Link-Backlog (Linked 2026-06-13)
- [[next-seo-v6-robots-prop-broken]] — next-seo v6 `robots` prop silent no-op gotcha (P0-4 root cause)
