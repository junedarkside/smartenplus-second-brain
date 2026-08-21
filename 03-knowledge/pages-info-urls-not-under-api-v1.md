# `pages_info.urls` Is Mounted at Site Root, NOT Under `/api/v1/`

**Problem:** Most backend apps register under `/api/v1/` via the router in `apis/urls.py`. `pages_info` (hero banners, front-page, navigation, terms) is different — `Smartenplus/urls.py:39` does `path('', include('pages_info.urls'))`, mounting it at the site root. A fetch built by pattern-matching other endpoints (`${baseURL}/api/v1/hero-banners/`) 404s silently.

**Example:** Frontend `getStaticProps` fetched `${baseURL}/api/v1/hero-banners/?placement=activities` — 404. Confirmed via curl: `/api/v1/hero-banners/` → 404, `/hero-banners/?placement=activities` → 200 with correct data. Backend data (`HeroBanner` row, correct `placement`, `is_active=true`) was fine the whole time — this was purely a wrong path in one `fetch()` call, written once during planning and shipped as written without anyone curling the actual URL first.

**Why it stayed hidden:** the fetch was wrapped in `Promise.allSettled` + `console.warn`-on-failure specifically to avoid *silent* failures — but a 404 degrades gracefully to the same fallback path as "no banner configured," which looks identical from the rendered page. The failure was logged (`console.warn` fired) but nobody was watching server/build logs for it; from the browser it just looked like "the image won't change."

**Detection heuristic:** before writing any new fetch to a `pages_info`-owned endpoint (`hero-banners`, `front-page`, `navigation`, `terms`), check `pages_info/urls.py` + the `include()` line in `Smartenplus/urls.py` directly — don't infer the prefix from sibling `products`/`operators` endpoints, they're mounted differently. More generally: **curl the actual endpoint once before trusting a fetch URL you wrote from pattern-matching**, especially when wrapped in a failure-tolerant `Promise.allSettled` — that tolerance is exactly what lets a wrong URL ship silently.

**Severity:** shipped, live-reported by user as "image doesn't change" — real user-facing bug for one release cycle before caught and fixed same day.

Part of hero-banner Activities page work, #335.

## Related
- `Smartenplus/urls.py:39` — the actual mount point
- `pages_info/urls.py` — registers `hero-banners`, `front-page`, `navigation`, `terms`
- `apis/urls.py` — where `/api/v1/` IS the correct prefix (products, operators, etc.)
- `pages/activities/index.js` — the fixed call site
