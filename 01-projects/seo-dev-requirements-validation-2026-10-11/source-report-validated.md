# Dev Requirements — SmartenPlus Public-Site SEO Fixes (VALIDATED)

**Document:** SEO-REQ-2026-10-11-v1
**Owner:** SEO/Product (June)
**Audit reference:** `01-projects/seo-audit/reports/2026/10/2026-10-11-public-site-seo-audit.md`
**Scope:** Read-only audit was performed on 2026-10-11. These are the backend / frontend code changes the dev team needs to ship to resolve the 4 critical issues + the prioritized quality fixes.
**Out of scope:** API contract changes, business logic changes, design changes unrelated to SEO.

---


> **VALIDATED 2026-10-11** against live production (curl) and `smartenplus-frontend` code. Original report kept unchanged at `2026-10-11-dev-requirements-seo-fixes.md`. This copy adds a validation status per REQ and **corrects the implementation guidance**. Where a REQ body below conflicts with the "Validation addendum", **the addendum wins**.

# Validation addendum (read this first)

## Stack corrections (apply to every REQ)
- Frontend is **Next.js Pages Router at repo root** — `pages/`, `components/`, `helpers/`, `lib/`, `hooks/`. There is **no `src/`** and **no App Router** (`app/`). Ignore `notFound()` from `next/navigation`, `src/lib/seo*`, `src/components/SEO.tsx`.
- In Pages Router ISR (`getStaticProps`) the 404 is `return { notFound: true, revalidate: N }`. Never return `notFound` from a `catch` block for transient errors (CLAUDE vault rule: it caches a 404 and destroys the ISR slot).
- Sitemap is **hand-built** in `lib/sitemap/*.js` and served by `pages/server-sitemap.xml/index.js`. `next-sitemap.config.js` only covers the 80 static pages. Ignore `lastmod` resolver advice for `next-sitemap`.
- `:from(lower)` in `next.config.js` redirects **is not valid Next.js**. Do the case redirect in `getStaticProps`.
- Branch policy: work on `fix/<desc>` branched from `develop`. Repo is currently on `main`.

## Status table

| REQ | Report claim | Live result (2026-10-11) | Status |
|---|---|---|---|
| 001 `/trips/<a>/<b>` soft-404 | `/trips/zzzz/yyyy` → 200 full meta | 200, canonical self, **robots already `noindex,follow`**, Service + HowTo JSON-LD, ~34 words body | **CONFIRMED** (status 200 is the bug; robots part overstated) |
| 002 `/trips/detail/<slug>` soft-404 | fake slug → 200, "full meta" | 200 but body "Trip Not Available", title "Trip Not Available", **robots `noindex, nofollow` already present** | **PARTLY CONFIRMED** — status 200 wrong, meta claim wrong |
| 003 `/ref/<slug>` broken | 4 of 5 sample URLs broken; 42 in sitemap, 1 works | **41 of 42 sitemap URLs return 200 "Reference Type Not Found"**, homepage `<title>`, robots `index,follow`. Only `/ref/route` works. `/ref/train`, `/bus`, `/ferry`, `/payment` same. | **CONFIRMED — and worse** (sitemap URLs are real WP article slugs, not dead) |
| 004 mixed-case duplicate | `/trips/Phuket/Koh-Phi-Phi` 200 dup, 352,156 B | 200, canonical self, **352,431 B identical** to lowercase | **CONFIRMED** |
| 005 help canonical | all 54 `/help/<slug>` canonical `/help` | Category pages (1-segment, 9 of 54; 8 of 9 sampled canonical `/help` ❌, `/help/faqs` self ✅). **45 post pages (`/help/<cat>/<post>`) already self-canonical ✅.** `/help/cancel-booking` is **404**, not 200. | **PARTLY CONFIRMED** — scope is 9 category pages, not 54 |
| 006 sitemap lastmod | 2,184 of 4,471 same ms | **2,182 of 4,475** share same minute | **CONFIRMED** |
| 007 hreflang mismatch | trip pages `en-US/th-TH` | Home `en/th`; **hub `/trips/<a>/<b>` `en-US/th-TH`**; **trip detail `en/th`** (not mismatched) | **CONFIRMED** for hub pages only |
| 008 pagination canonical | `/trips?page=N`, `/blog?page=N` canonical page 1 | `/trips` and `/blog` have **no server pagination** (infinite scroll / cursor). Canonicals correct. `/activities?page=2` canonical `/activities` (needs check whether `?page` changes content). | **INVALID** for trips/blog; re-scope to activities only |
| 009 clean `/ref` from sitemap | 41 dead URLs | All 42 return 200 (placeholder). They are real articles that are **mis-routed**. Removing them throws away content. | **REFRAMED** — fix routing (REQ-003), do not delete URLs |
| 010 detail cannibalization | 1,735 detail URLs | 1,739 detail URLs in sitemap | **CONFIRMED** (count), strategy is a business decision |
| 011 title/meta template | casing + length | not re-measured | **UNVERIFIED** |
| 012 FAQPage JSON-LD | visible FAQ, no schema | `/trips/phuket/koh-phi-phi` has "Frequently Asked" heading, **0 `FAQPage` JSON-LD** (only Product ×21, Service, HowTo) | **CONFIRMED** |
| 013 `dateModified` stale | 2026-01-26 | `"dateModified":"2026-01-26T10:49:41"` | **CONFIRMED** |

Sitemap actuals: **4,475** `<loc>`; **2,443** hub (includes `/th/` mirrors); **1,739** detail; **42** `/ref`; **54** `/help`.

## Corrected diagnosis + fix per REQ

### REQ-001 — correct file: `pages/trips/[...slug].js` (`getStaticProps`)
- Today: when API returns `routes: []` it logs `No route data found… Rendering page with contracts only` and returns **200 props**. The API-error `catch` also returns 200.
- Fix: if the route API responds 404, or `routes` is empty **and** `contracts` is empty → `return { notFound: true, revalidate: 3600 }`. Keep the `catch` soft path (5xx / timeout) so transient errors don't cache a 404.
- Already fixed (do not redo): single-segment `/trips/<x>` → `helpers/i18n/resolveNonRouteSlug.js`. Note it **302-redirects to `/locations/<x>` when the location exists** (report said 404) — report's matrix row for `/trips/foo` is correct only when location doesn't exist.
- Watch: `noindex` already comes from `components/SEO/seoConfig.js` (`noindex: !dataValid`). Don't duplicate.

### REQ-002 — `pages/trips/detail/[...slug].js`
- Already returns `notFound: true` when API returns empty. The soft-200 is the `catch` branch: backend 404 throws in axios → renders "Trip Not Available" with 200.
- Fix: in `catch`, `if (error.response?.status === 404) return { notFound: true, revalidate: 3600 }`; keep soft path otherwise.
- Meta already `noindex, nofollow` — AC "includes noindex" already met on the soft page.

### REQ-003 — root cause found (not what the report assumed)
- `next.config.js` has `rewrites()`: `/ref/:slug((?!route|pier|location|terminology).*)` → `/ref/article/:slug`. In production the **dynamic page `pages/ref/[type].js` wins** over that rewrite, so every `/ref/<article-slug>` renders `[type].js`, which has no matching section → "Reference Type Not Found", 200, `index,follow`, homepage title.
- Direct `/ref/article/<slug>` returns **404** in prod too, so check whether the article page's WP lookup works (`pages/ref/article/[slug].js` `getStaticProps` `notFound` branches).
- Fix order: (1) make `/ref/<slug>` resolve to the article page (move rewrite to `beforeFiles`, or merge logic into one dynamic page that checks "is type" else "is article"); (2) verify article slugs exist in WP; (3) `[type].js`: return `notFound` when `section` undefined / zero articles; (4) never ship `robots: index,follow` on a not-found body.
- Decision gate in original REQ-003 (410 vs "coming back") **no longer applies** — these are real articles.

### REQ-004 — `pages/trips/[...slug].js`
- Do in `getStaticProps`: `const canon = params.slug.map(slugify)`; if any segment differs from the raw param → `return { redirect: { destination: prefix + '/trips/' + canon.join('/'), permanent: true } }`. Mirror locale prefix handling in `resolveNonRouteSlug.js`.
- Also check `/th/trips/...` mirror.
- Regression test: 5 mixed-case inputs in the original AC.
- Remove invalid `:from(lower)` snippet.

### REQ-005 — `pages/help/[...slug].js`
- `defaultSEO.canonical = '/help'` (line ~82) is used for **category pages and any post without `seoPost`**. Posts with SEO data already self-canonical (line ~100).
- Fix: default canonical = `https://www.smartenplus.co.th${router.asPath.split('?')[0]}` for category pages.
- AC3 (404 on missing slug) **already done** (`notFound` in `getServerSideProps`).
- Affected: 9 category URLs, not 54.

### REQ-006 — `lib/sitemap/*.js`
- Sources using `new Date()`: base entries (home, `/trips`, `/activities`, `/locations`, `/destinations`, `/help`, `/ref`, `/blog`, operators) and fallbacks `x.updated_at || x.created_at || currentDate` in `locations.js`, `products.js`, `blog.js`, plus **all `/ref/<type>` category entries** and operators.
- Routes sitemap already omits `<lastmod>` when `updated_at` missing — correct pattern; apply the same to every fallback (omit tag instead of faking).
- Check which API endpoints lack `updated_at` (locations, stations, operators) — needs BE field.

### REQ-007 — `components/SEO/seoConfig.js:65-66`
- Change `en-US`/`th-TH` → `en`/`th` (matches `Seo.js`, `tripDetailSEOUtils.js`, sitemap). Also check `<html lang>` in `pages/_document.js` (`lang={this.props.language}`).

### REQ-008 — withdraw for `/trips` and `/blog`
- No paginated URLs exist. Only audit `/activities?page=N`, `/forum`.

### REQ-009 — merged into REQ-003
- Keep sitemap URLs; fix routing. Add CI check "every sitemap `<loc>` returns 200 **and** has non-placeholder title" to catch exactly this bug.

### REQ-012 — new components needed
- `components/trips/RouteFAQ.js` / `routeFAQBuilder.js` emit FAQPage only in some data conditions; live hub `phuket/koh-phi-phi` emits none. Find why (`customFaqs`/`routeFaq` empty vs suppressed by `FilterTripsPage.js` comment ~line 228).

### REQ-013
- `lastModified` in `hooks/useRouteSeo.js:184,201` = WordPress blog post `modified`. Use route/API `updated_at` when available; omit field otherwise rather than send stale date.

## Corrections to report text
- Appendix B row 1: "REQ-005 trailing-slash redirect" — REQ-005 is canonical, not trailing slash. No trailing-slash redirect is in scope.
- REQ-004 AC4: same mislabel.
- Appendix A matrix: `/help/cancel-booking` → 404 (not 200); `/trips/foo` → 302 `/locations/foo` if location exists else 404.
- Appendix A: `/ref/train` placeholder is real; so are 40 other `/ref/<slug>`.

## Revised sequencing
- **Week 1:** REQ-003 (highest — 41 real articles invisible), REQ-001, REQ-002, REQ-004, REQ-005, REQ-007
- **Week 2:** REQ-006 (needs BE `updated_at`), REQ-012, REQ-013, REQ-011
- **Later:** REQ-010 (business decision)
- **Dropped:** REQ-008 (trips/blog), REQ-009 (merged into 003)

---


# Standards review (CLAUDE.md, CODING_STANDARDS, ISR/SEO rules) — corrections to the fixes above

Two reviewers checked the addendum fixes against project rules. **Where this section conflicts with the addendum above, this section wins.** Caveat: the SEO reviewer could not open `docs/operations/SEO.md`; its canonical/`/th` points come from code + vault notes — re-check against that file before implementing.

## Rules that apply to every fix
- **Never `notFound` from a `catch` for transient errors.** Only for a *confirmed 404*. 5xx/timeout keep the soft path. (Reword addendum line "never return notFound from a catch".)
- **`notFound` revalidate = 300**, not 3600. With `fallback:'blocking'`, 3600 hides a route/article created in the last hour. (`pages/trips/[...slug].js:198` already uses 300; `/ref/article` uses 86400 for a missing article — cut it.)
- **Deploy must clear the `smartenplus_next_cache` Docker volume** or stale 404/redirect ISR results persist. Add as acceptance step to REQ-001..005.
- **`/th/` mirrors need the same fix** for REQ-001, -004, -005 (and `/th/ref/<slug>` — rewrite has `locale:false`, so no rule matches it today).
- Canonicals: `https://www.smartenplus.co.th` + locale prefix, no query. Use `getSiteUrl()` (`utils/blog/seoHelper.js`).
- Sitemap must not list URLs that 404 or redirect.
- Branch from `develop`: `fix/<desc>`. Run build + `npm test` + `wc -l` on changed files.

## Per-REQ corrections
| REQ | Verdict | Required change |
|---|---|---|
| 001 | PASS w/ edits | `[...slug].js:138-140` throws on any `!res.ok`, so a 404 lands in the soft `catch` (:200) — the addendum's "if API 404" cannot fire as written. Read `res.status` **before** the throw; 404 → `{ notFound: true, revalidate: 300 }`. Condition for empty page: API ok **and** `routes` empty **and** `contracts` empty. Contracts-only (:146-152) stays 200. File 222 lines — fine. |
| 002 | PASS, needs split note | `trips/detail/[...slug].js` is **517 lines (red, >500)**. 3-line fix, but CLAUDE.md says split regardless → extract SEO/JSON-LD block first, or record explicit waiver + linked issue. Verify `fetchData` (:469) exposes `error.response`; use `error.response?.status ?? error.status`. Use `revalidate: 300`. 404-only. |
| 003 | **REWRITE** | (a) Move rewrite to `rewrites(){ return { beforeFiles:[ref rewrite], afterFiles:[/graphql] } }` (`next.config.js:114-126`). **Do not** merge into one dynamic page — `[type].js` 377 + `article/[slug].js` 370 lines would blow the size budget. (b) **Regex bug:** `(?!route\|pier\|location\|terminology).*` is a prefix lookahead — blocks any article slug starting with those words. (c) **Second bug:** `sectionMap` (`ref/[type].js`) has **11 types** (route, pier, location, terminology, access, seasonal, safety, administrative, destination, crossborder, infrastructure); rewrite excludes only 4, so once moved to `beforeFiles` the other 7 type pages would be hijacked and 404. Exclude all 11 with end anchor: `(?!(?:route\|pier\|location\|terminology\|access\|seasonal\|safety\|administrative\|destination\|crossborder\|infrastructure)$).*` — better: generate it from `Object.keys(sectionMap)`. (d) `[type].js`: `getStaticProps` (:333) → `if(!sectionMap[type]) return { notFound:true, revalidate:300 }`; optional-chain `json.data.referenceArticles` in `getStaticPaths` (:310, throw risk); add `noindex` to placeholder. (e) `article/[slug].js`: catch (:364-369) returns `notFound` → violates ISR rule, change to soft/short revalidate; "Article Not Found" render path (:45, :332-354) must be real `notFound`; missing-article revalidate 86400 → 300. (f) Canonical already self `/ref/${slug}` (`article/[slug].js:91`) — do not add another; `/ref/article/<slug>` stays a second URL → redirect it to `/ref/<slug>`. (g) Test with a real WP slug. |
| 004 | PASS w/ edits | 308 (`permanent:true` in gSP = 308; fine for Google, write "308"). Reuse `slugify`; **extract** locale-prefix logic from `resolveNonRouteSlug.js:19-20` into a shared helper (not a copy). Redirect **before** API call. Compare per segment; redirect only if `slugify(seg) !== seg` (loop guard — check diacritics/underscore handling). Apply to hub, `/trips/detail`, `/locations`, `/activities` as in scope. Acceptance: loop-curl the redirect (vault flags "redirect revalidate not confirmed honoured"). |
| 005 | PASS, locale fix | Extract `const canonical` reuse the :100 expression. `router.asPath` has no locale prefix → `/th/help/x` would canonicalize to English URL. Use `getSiteUrl()` + locale prefix, or confirm `/th/help` is not served. File 358 lines (yellow) — change does not grow it. |
| 006 | **INCOMPLETE** | More `new Date()` sites: `help.js:9,52`, `operators.js`, `airport-transfer.js:7`, `blog.js:8`, `utils.js:8`, `ref-articles.js:22`. Add one shared `lastmodTag(date)` in `lib/sitemap/utils.js` returning `''` for missing/invalid date (+ `console.warn`, never throw), reuse the `routes.js:44` pattern. Do not hand-edit 9 files. |
| 007 | PASS w/ edits | Lines are `seoConfig.js:65` (`en-US`) and the next line (`th-TH`) — range "65-66" ~right. Only caller `useRouteSeo.js:6`, blast radius = hub pages. hreflang hrefs must equal canonical (:53 sets canonical = `thUrl` for `th`) and match sitemap `/th/` mirrors; emit `thUrl` only if page exists; `en` and `x-default` share one href (next-seo dedupe) — check. |
| 012 | REWORD | Diagnosis first (why `routeFaq`/`customFaqs` empty or suppressed — `FilterTripsPage.js` ~228), then fix. Put any builder in `routeFAQBuilder.js`, **not** `useRouteSeo.js` (256 lines, yellow). Emit FAQPage only when FAQ text is visible on page. Drop "new components needed". |
| 013 | PASS w/ edits | `lastModified` is set in `trips/[...slug].js:179` getStaticProps → fix there (hook already omits falsy). Hook lines are 184/201 (192/206 are dep arrays). Needs BE `updated_at` for routes. |

## Report text corrections added by review
- Addendum "Vault rule: never notFound in catch" → "only for confirmed 404".
- REQ-003 "move rewrite to beforeFiles" is necessary but **not sufficient** (regex + 7 hijacked type pages).
- REQ-012 "new components needed" contradicts its own diagnosis step.


---

## How to use this document

- Each requirement is **independently shippable** and **independently verifiable**.
- Requirements are grouped by priority and effort. Items P0–P1 should ship within the current sprint. P2–P3 in the following sprint.
- Every requirement has:
  - **Why** (root cause)
  - **Acceptance criteria** (testable)
  - **Verification** (exact curl/check command the dev can run after deploy)
  - **Rollback** (how to revert if it breaks)

---

# P0 — Critical (ship this week)

## REQ-001 — Server-side validation for `/trips/<from>/<to>`

**Why:** Any 2-segment URL matching `/trips/<a>/<b>` (e.g. `/trips/zzzz/yyyy`) currently returns HTTP 200 with full SEO meta + canonical + hreflang + auto-generated JSON-LD. Spammers can invent unlimited fake URLs and have Google index them. Verified live on 2026-10-11:

```
GET /trips/zzzz/yyyy → 200, 162 words, full meta, full JSON-LD
GET /trips/phuket/koh-phi-phi → 200, real content (correct)
```

**Acceptance criteria:**
1. `GET /trips/<valid-route-slug>/` → 200 with real content (unchanged behavior).
2. `GET /trips/<invalid-route-slug>/` where the `<from>` or `<to>` slug does not match a route in the data layer → **HTTP 404** (not 200, not 302).
3. The 404 response body must include `<meta name="robots" content="noindex,nofollow">` in the HTML head (already done in your `/404` page — verify it's reused, not duplicated).
4. Trailing-slash behavior preserved: `/trips/<a>/<b>/` → 308 to `/trips/<a>/<b>` (existing behavior, do not break).
5. JSON-LD on the 404 page must NOT be generated (no Product/Service/HowTo schemas).
6. `<link rel="canonical">` on the 404 response must point to itself or be absent (not to a real route).

**Implementation guidance:**
- Next.js: change the route handler at `pages/trips/[from]/[to]/` (or `app/trips/[from]/[to]/page.tsx` if using App Router) to call `notFound()` after a DB lookup that returns 0 rows for the `(from, to)` pair.
- The lookup should use the same data source as the route-discovery API. If the API uses `GET /api/v1/routes?from=<slug>&to=<slug>`, mirror the call server-side — do not introduce a new DB query.

**Verification:**
```bash
# 1. fake URL returns 404
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/zzzz/yyyy" | head -1
# Expected: HTTP/2 404

# 2. real URL still 200
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/phuket/koh-phi-phi" | head -1
# Expected: HTTP/2 200

# 3. 404 page has noindex,nofollow
curl -s -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/zzzz/yyyy" | grep -i 'meta name="robots"'
# Expected: <meta name="robots" content="noindex,nofollow">
```

**Rollback:** Git revert. No data migration needed.

**Estimated effort:** S (1–2 dev hours)

---

## REQ-002 — Server-side validation for `/trips/detail/<slug>`

**Why:** Same soft-404 surface as REQ-001 but for the auto-generated detail pages. These currently have **1,735 URLs in `server-sitemap.xml`** — among the highest-volume indexed surfaces on the site. Verified live:

```
GET /trips/detail/krabi-to-koh-lanta-105 → 200, real content (correct)
GET /trips/detail/zzz-yyyy-9999999 → 200, auto-generated thin page + full meta (vulnerable)
```

**Acceptance criteria:**
1. `GET /trips/detail/<valid-slug>/` → 200 with real content (unchanged).
2. `GET /trips/detail/<invalid-slug>/` → **HTTP 404** with `noindex,nofollow`.
3. The fix must NOT change behavior for the 1,735 valid slugs already in `server-sitemap.xml`.
4. Trailing-slash handling preserved.

**Implementation guidance:**
- Same pattern as REQ-001 — server-side lookup before render, `notFound()` on miss.
- Data source: same endpoint already powering the detail pages (likely an API call like `GET /api/v1/trips/detail/<slug>` or a direct DB query for the route record).

**Verification:**
```bash
# 1. valid slug returns 200
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/detail/krabi-to-koh-lanta-105" | head -1
# Expected: HTTP/2 200

# 2. fake slug returns 404
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/detail/spam-9999999-zzz" | head -1
# Expected: HTTP/2 404

# 3. sitemap count unchanged for valid detail URLs
curl -s "https://www.smartenplus.co.th/server-sitemap.xml" | grep -c 'trips/detail/'
# Expected: ~1,735 (or whatever the current valid count is — verify before/after)
```

**Rollback:** Git revert.

**Estimated effort:** S

---

## REQ-003 — Server-side validation for `/ref/<slug>`

**Why:** The `/ref/` template is broken: 4 of 5 sample URLs return a 129-word "Reference Type Not Found" fallback that still ships the homepage's `<title>` and `<meta description>`. These URLs are in `server-sitemap.xml`. Verified live:

```
GET /ref/route → 200, real 712-word article (only working slug)
GET /ref/train → 200, 129-word placeholder, homepage <title> (broken)
GET /ref/bus → 200, same placeholder (broken)
```

**Acceptance criteria:**
1. `GET /ref/<valid-content-slug>/` → 200 with real content (only `/ref/route` currently passes).
2. `GET /ref/<slug-without-content>/` → **HTTP 410 Gone** (preferred) OR **HTTP 404** (acceptable). 410 is preferred because it explicitly tells Google "this content was intentionally retired."
3. Pages returning 410/404 must have `<meta name="robots" content="noindex,nofollow">`.
4. The 42 broken `/ref/<slug>` URLs currently in `server-sitemap.xml` must be **removed from the sitemap** in the same deploy. See REQ-009.
5. While REQ-009 ships separately, dev should manually verify the sitemap regen logic excludes 410/404-returning slugs. (Add a unit test if the sitemap is generated from app code.)

**Implementation guidance:**
- Decide first: are these 42 slugs coming back, or are they permanently gone? If permanently gone → 410 + remove from sitemap. If coming back → mark the route as "not yet implemented" and render a 200 page with `noindex` + canonical to `/ref` until content ships.
- Whichever choice is made, the validation must be server-side (route handler check), not client-side.

**Verification:**
```bash
# 1. working slug still 200
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/ref/route" | head -1
# Expected: HTTP/2 200

# 2. broken slug now 404 or 410
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/ref/train" | head -1
# Expected: HTTP/2 404 or HTTP/2 410

# 3. 404 has noindex
curl -s -A "Mozilla/5.0" "https://www.smartenplus.co.th/ref/train" | grep -i 'meta name="robots"'
# Expected: <meta name="robots" content="noindex,nofollow">
```

**Rollback:** Git revert.

**Estimated effort:** S–M (depends on whether content is being authored or URLs are being retired)

---

## REQ-004 — Lowercase normalization + canonical on `/trips/*`

**Why:** `/trips/Phuket/Koh-Phi-Phi` and `/trips/phuket/koh-phi-phi` return **byte-identical HTML** (352,156 bytes each), and each URL self-canonicals to itself. Google sees two URLs with the same content competing for the same keyword on the most-crawled template on the site. Verified live on 2026-10-11:

```
GET /trips/Phuket/Koh-Phi-Phi  → 200, canonical=https://www.smartenplus.co.th/trips/Phuket/Koh-Phi-Phi
GET /trips/phuket/koh-phi-phi  → 200, canonical=https://www.smartenplus.co.th/trips/phuket/koh-phi-phi
# Both 352,156 bytes, byte-identical
```

**Acceptance criteria:**
1. `GET /trips/<mixed-case>` → **HTTP 301** to `/trips/<all-lowercase>`.
2. `GET /trips/<all-lowercase>` → 200, **canonical=self** (already correct).
3. The 301 redirect must preserve query string and fragment.
4. The 301 must NOT preserve trailing slash if REQ-005 ships; if REQ-005 ships in same release, the two redirects chain (lowercase first, then trailing slash, or vice versa).
5. Internally generated links (in `<a href>`, JSON-LD `url`, sitemap `<loc>`) must use lowercase. Add a code-review checklist item: "all `/trips/*` links are lowercase."
6. A regression test must cover at least 5 mixed-case inputs: `Koh-Phi-Phi`, `koh-phi-Phi`, `KOH-PHI-PHI`, `koH-Phi-phi`, `KOHPHIPHI`.

**Implementation guidance:**
- Next.js (Pages Router): in `next.config.js`, add a `redirects()` entry:
  ```js
  {
    source: '/trips/:from/:to',
    destination: '/trips/:from(lower)/:to(lower)',
    permanent: true,
  }
  ```
- Next.js (App Router): same in `next.config.js`. The `:from(lower)` syntax is supported.
- If using a reverse proxy (Nginx/Cloudflare Worker), set up the redirect at the edge.
- Cloudflare Workers: `request.url` → match `/trips/...` → `Response.redirect()` with HTTP 301.

**Verification:**
```bash
# 1. mixed-case redirects to lowercase
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/Phuket/Koh-Phi-Phi" | head -5
# Expected: HTTP/2 301  →  location: /trips/phuket/koh-phi-phi

# 2. lowercase still 200
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/phuket/koh-phi-phi" | head -1
# Expected: HTTP/2 200

# 3. follow the redirect, ensure no redirect loop
curl -sIL -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/Phuket/Koh-Phi-Phi" 2>&1 | grep -E '^HTTP|^location'
# Expected: 301 → 200, no further redirects
```

**Rollback:** Git revert. Note: search engines will re-index within 1–4 weeks after revert because they had already de-duped the signal. Monitor Search Console for crawl spikes after revert.

**Estimated effort:** M (need to audit all internal link generators: blog posts, sitemap, JSON-LD, footer nav, mid-article links, breadcrumbs)

---

## REQ-005 — Help-article self-canonical

**Why:** All 54 `/help/<slug>` URLs (including `/help/booking-process`, `/help/cancel-booking`, `/help/faqs`) ship with `<link rel="canonical" href="https://www.smartenplus.co.th/help">`. Every help article is being told to Google "I'm just a duplicate of `/help`" → none of the 54 can rank. Verified live:

```
GET /help/booking-process → 200, canonical=https://www.smartenplus.co.th/help  ← wrong
GET /help/cancel-booking  → 200, canonical=https://www.smartenplus.co.th/help  ← wrong
GET /help/faqs             → 200, canonical=https://www.smartenplus.co.th/help  ← wrong
GET /help                  → 200, canonical=https://www.smartenplus.co.th/help  ← OK (self)
```

**Acceptance criteria:**
1. `GET /help/<any-slug>/` → 200 with `<link rel="canonical" href="https://www.smartenplus.co.th/help/<slug>">` (self-reference).
2. `GET /help` (listing page) → 200 with `<link rel="canonical" href="https://www.smartenplus.co.th/help">` (unchanged).
3. Behavior for non-existent help slugs: same as REQ-001 (404 + noindex) — apply the same `notFound()` pattern.
4. Hreflang tags on `/help/<slug>/` must reference the correct Thai equivalent if one exists.

**Implementation guidance:**
- The bug is almost certainly one line in the help route handler — `head`/`<Head>` is hardcoding the canonical to `'/help'` instead of using the request URL.
- Find it by grep: `rg 'canonical.*help' --type ts --type tsx -A 1`

**Verification:**
```bash
# 1. help article now self-canonicals
curl -s -A "Mozilla/5.0" "https://www.smartenplus.co.th/help/booking-process" | grep -i 'canonical'
# Expected: <link rel="canonical" href="https://www.smartenplus.co.th/help/booking-process">

# 2. /help listing still canonicals to itself
curl -s -A "Mozilla/5.0" "https://www.smartenplus.co.th/help" | grep -i 'canonical'
# Expected: <link rel="canonical" href="https://www.smartenplus.co.th/help">
```

**Rollback:** Git revert.

**Estimated effort:** XS (likely 1 line in a config file)

---

# P1 — Action Required (ship this sprint if possible)

## REQ-006 — Sitemap `lastmod` from real content date

**Why:** 2,184 of 4,471 URLs in `server-sitemap.xml` (49%) carry `lastmod=2026-10-11T04:39:21.xxxZ` — within 1ms of each other. They match the sitemap-fetch timestamp, not the actual content-modified date. Google's sitemap trust degrades when so many URLs claim identical-millisecond freshness. Verified live by curl-fetching `server-sitemap.xml`:

```
<url><loc>https://www.smartenplus.co.th</loc><lastmod>2026-10-11T04:39:21.850Z</lastmod>...
<url><loc>https://www.smartenplus.co.th/about</loc><lastmod>2026-10-11T04:39:21.851Z</lastmod>...
<url><loc>https://www.smartenplus.co.th/activities</loc><lastmod>2026-10-11T04:39:21.851Z</lastmod>...
... (continues for 2,184 URLs)
```

**Acceptance criteria:**
1. Each `<lastmod>` value must come from the underlying content entity's `dateModified` field, NOT from `Date.now()` at render time.
2. For pages where content rarely changes (e.g. `/about`, `/privacy`), `lastmod` should be the date that page content was last edited — usually weeks or months ago, not today.
3. For dynamic content (trip pages with live schedules), `lastmod` should be the schedule's last update.
4. After deploy, the distribution of `lastmod` values should span weeks/months (not cluster on the same minute). Verify with:
   ```bash
   curl -s "https://www.smartenplus.co.th/server-sitemap.xml" | grep -oE '<lastmod>[^<]+' | sort -u | head -20
   ```
   Expected: spread across at least 30+ unique days.

**Implementation guidance:**
- Likely cause: `next-sitemap` or `@nuxtjs/sitemap` is using build-time as `lastModified`. Pass a custom `lastmod` resolver in `next-sitemap.config.js`:
  ```js
  module.exports = {
    sitemap: {
      lastmod: async (url) => {
        // Look up the entity in DB by URL pattern
        // Return its dateModified, fallback to the page's actual CMS modified date
      },
    },
  };
  ```
- For static pages, the resolver can return the file's git-blame last-modified date (already on disk).

**Verification:**
```bash
# Distribution check
curl -s "https://www.smartenplus.co.th/server-sitemap.xml" \
  | grep -oE '<lastmod>[^<]+' \
  | sort -u \
  | head -20
# Expected: distinct dates spanning weeks/months, not all the same minute

# No single date dominates
curl -s "https://www.smartenplus.co.th/server-sitemap.xml" \
  | grep -oE '<lastmod>[^<]+' \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -5
# Expected: no single date has >100 occurrences
```

**Rollback:** Revert to `Date.now()` behavior — same code path, will degrade signal again.

**Estimated effort:** M (need to wire up per-URL `lastmod` lookup)

---

## REQ-007 — Standardize hreflang codes

**Why:** Mixed hreflang codes across templates confuse Google's language clustering:
- Homepage uses `en` / `th` / `x-default` ✅
- Trip pages use `en-US` / `th-TH` / `x-default` ⚠️
Google treats `en` and `en-US` as different language signals, splits the signal.

**Acceptance criteria:**
1. All pages on the site use the SAME hreflang codes: either `en` / `th` / `x-default` everywhere OR `en-US` / `th-TH` / `x-default` everywhere.
2. Pick one and stick to it. Recommended choice: bare codes `en` / `th` because the site targets English-language tourists globally (not specifically US English).
3. `<html lang="...">` attribute must match the hreflang code (commonly a separate bug but check it).

**Implementation guidance:**
- Find the hreflang generator (likely a component or config in `src/lib/seo/` or `src/components/SEO.tsx`).
- Currently parameterized per template — change the parameter to a single constant.

**Verification:**
```bash
# 1. home uses bare
curl -s "https://www.smartenplus.co.th/" | grep -oE 'hreflang="[^"]+"'
# Expected: hreflang="en", hreflang="th", hreflang="x-default"

# 2. trip page uses bare too
curl -s "https://www.smartenplus.co.th/trips/phuket/koh-phi-phi" | grep -oE 'hreflang="[^"]+"'
# Expected: hreflang="en", hreflang="th", hreflang="x-default"
# (After fix — currently shows en-US, th-TH, x-default)
```

**Rollback:** Git revert. Hreflang changes only affect which page Google shows for which language query — no content impact.

**Estimated effort:** XS

---

## REQ-008 — Pagination canonical fix (deep-page indexing)

**Why:** `/trips?page=N` and `/blog?page=N` canonicalize all to page 1, even though each page contains unique long-tail content. Deep pages like `/trips?page=14` are never indexed. Verified live:
```
GET /trips → 200, canonical=https://www.smartenplus.co.th/trips
GET /trips?page=2 → 200, canonical=https://www.smartenplus.co.th/trips  ← wrong
```

**Acceptance criteria:**
1. `GET /trips?page=1` → 200, canonical = `https://www.smartenplus.co.th/trips?page=1` (or clean `/trips` — accept either as long as it's self).
2. `GET /trips?page=2` → 200, canonical = `https://www.smartenplus.co.th/trips?page=2` (self-reference).
3. `GET /trips?page=99` (out of range) → 404 with noindex.
4. Same behavior for `/blog`, `/activities`, `/destinations`, `/locations`, `/operators`.
5. Do NOT add `rel="next"` or `rel="prev"` — Google deprecated these signals in 2019.

**Implementation guidance:**
- Read the page number from the query string in `getServerSideProps` (or the App Router equivalent) and emit `<link rel="canonical" href={`${baseUrl}${currentPage > 1 ? `?page=${currentPage}` : ''}`} />`.

**Verification:**
```bash
curl -s "https://www.smartenplus.co.th/trips?page=2" | grep -i 'canonical'
# Expected: <link rel="canonical" href="https://www.smartenplus.co.th/trips?page=2">
```

**Rollback:** Git revert.

**Estimated effort:** XS

---

# P2 — Quality fixes (next sprint)

## REQ-009 — Clean `/ref/<slug>` entries from sitemap

**Why:** Currently 42 `/ref/<slug>` URLs are in `server-sitemap.xml`, of which only 1 (`/ref/route`) has real content. The other 41 are dead or unused. They waste crawl budget and signal Google to revisit dead URLs.

**Acceptance criteria:**
1. After REQ-003 ships, verify that the sitemap generator's URL list excludes any `/ref/<slug>` that returns 404/410.
2. Add a CI test: when sitemap generation runs, every `<loc>` should return 200 from a sample HEAD check.
3. Document the policy: **only routes returning 200 enter the sitemap.** 404/410/3xx-redirect are excluded.
4. Until REQ-003 ships, manually remove the 41 dead `/ref/` entries from `server-sitemap.xml`.

**Verification:**
```bash
# All URLs in server-sitemap.xml should return 200
curl -s "https://www.smartenplus.co.th/server-sitemap.xml" \
  | grep -oE '<loc>[^<]+' \
  | sed 's|<loc>||' \
  | xargs -I{} curl -sI -A "Mozilla/5.0" "{}" \
  | grep -E 'HTTP/' \
  | awk '{print $2}' \
  | sort -u
# Expected: only "200" (or empty if filters to non-2xx)
```

**Rollback:** Re-add manually — not a code rollback; this is a data fix.

**Estimated effort:** S (when combined with REQ-003, the fix is automatic)

---

## REQ-010 — De-cannibalize `/trips/detail/<slug>` from parent `/trips/<a>/<b>/`

**Why:** `/trips/phuket/koh-phi-phi` (hub) and its ~5 detail variants (`/trips/detail/<slug>`) compete for the same keyword. 1,735 detail URLs in sitemap × ~351 hub pages = ~5 detail pages per hub, all ranking for the same query. Compounded by thin detail content (534–1,054 words, generic boilerplate meta) and meta-description leakage (operational notes like `"Operation time 06:00- 17:00"` leaking into search snippets).

**Acceptance criteria:**
1. Pick ONE strategy and ship it:
   - **Option A (recommended for now):** Add `<link rel="canonical" href="{parent_hub_url}">` on every `/trips/detail/<slug>/` page. Hub pages absorb the link equity, 1,735 detail pages de-indexed.
   - **Option B:** Add `<meta name="robots" content="noindex,follow">` on detail pages — they pass link juice without ranking.
2. Whichever option, detail pages still link correctly to the booking flow (don't break user functionality).
3. After deploy, verify Search Console "Pages" report shows de-indexed URLs within 4–6 weeks.
4. Rewrite `/trips/detail/<slug>` meta descriptions to unique ad copy (110–155 chars, no backend leakage). At minimum, eliminate the leakage strings identified in the audit:
   - `"Operation time 06:00- 17:00"` (currently in koh-mook-any-hotel-trang-airport-1821)
   - `"The service area for drop off in area from White Sand Beach to Bang Bao only"` (currently in bangkok-to-koh-chang-1582)
   - `"Check in 30 minutes before departure time at Bundhaya Counter"` (likely on multiple)

**Implementation guidance:**
- Option A: detail page looks up its parent route via the `route_id` field (likely already in the data model), generates canonical = `https://www.smartenplus.co.th/trips/<from_slug>/<to_slug>`.
- Option B: simpler — set meta robots tag in the detail layout. Less risk but doesn't consolidate link equity as cleanly.
- Whichever option, the meta-description rewrite needs a new field in the data model (`meta_description_override`) or a function that interpolates operator name + arrival city into a templated string. Discuss with content team.

**Verification:**
```bash
# 1. detail page now has canonical to parent (Option A)
curl -s "https://www.smartenplus.co.th/trips/detail/krabi-to-koh-lanta-105" | grep -i 'canonical'
# Expected: <link rel="canonical" href="https://www.smartenplus.co.th/trips/krabi/koh-lanta">

# 2. meta description is no longer leaked
curl -s "https://www.smartenplus.co.th/trips/detail/koh-mook-any-hotel-trang-airport-1821" \
  | grep -i 'meta name="description"'
# Expected: NEW unique copy, NOT containing "Operation time 06:00-"

# 3. detail page still user-navigable (no 404, no broken booking flow)
curl -sI -A "Mozilla/5.0" "https://www.smartenplus.co.th/trips/detail/krabi-to-koh-lanta-105" | head -1
# Expected: HTTP/2 200
```

**Rollback:** Git revert. Note: de-indexed URLs take 4–6 weeks to be re-indexed after rollback.

**Estimated effort:** L (Option A: data-model change for canonical resolution. Option B: smaller.)

---

## REQ-011 — Title case consistency + meta-description template

**Why:** `/trips/detail/<slug>` titles show inconsistent casing (`"Koh Lipe Pattaya Beach"` vs `"boonsiri counter koh tao"`). Title length 43–76 chars — 70+ truncates on mobile SERP. Brand-consistent Title Case + 50–60 char titles improve mobile CTR.

**Acceptance criteria:**
1. All `/trips/detail/<slug>` titles must be Title Case (each word capitalized: `Boonsiri Counter Koh Tao to Khao Sok Van Stop`)
2. All `/trips/detail/<slug>` titles ≤ 60 chars (truncate with ellipsis where needed).
3. All `/trips/detail/<slug>` meta descriptions are 110–155 chars, unique per page (not a single string repeated across 1,735 pages).
4. Hub `/trips/<a>/<b>/` titles and descriptions already meet standards (no fix needed there).

**Implementation guidance:**
- Helper function in `src/lib/seo.ts` (or equivalent):
  ```ts
  export function titleCase(slug: string): string {
    return slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }
  export function truncate(s: string, max: number): string {
    return s.length <= max ? s : s.slice(0, max - 1) + '…';
  }
  ```
- Title = `${titleCase(route)} | SmartenPlus`, truncated to 60.
- Description = unique-generated from operator name + route summary.

**Verification:**
```bash
# 1. title is title-case, ≤ 60 chars
curl -s "https://www.smartenplus.co.th/trips/detail/boonsiri-counter-koh-tao-to-khaosok-van-stop-1743" \
  | grep -oE '<title>[^<]+</title>'
# Expected: title starts with capital, contains " | SmartenPlus", length ≤ 60 chars

# 2. description is unique, 110-155 chars
curl -s "https://www.smartenplus.co.th/trips/detail/boonsiri-counter-koh-tao-to-khaosok-van-stop-1743" \
  | grep -oE 'meta name="description" content="[^"]+"'
# Expected: 110-155 chars, not the generic "Book reliable bus, ferry..."
```

**Rollback:** Git revert.

**Estimated effort:** M (per-page template function)

---

# P3 — Nice-to-have

## REQ-012 — Add `FAQPage` JSON-LD schema on trip pages (already have visible FAQ content)

**Why:** Trip pages already have visible FAQ sections (`<h2>Frequently Asked Questions</h2>` with Q&A pairs) but no `FAQPage` structured data. Adding it is an easy win for AI-search snippet eligibility (Perplexity, ChatGPT, Google AI Overview).

**Acceptance criteria:**
1. `/trips/<a>/<b>/` pages emit a `<script type="application/ld+json">` block with `@type: FAQPage` and a `mainEntity[]` array of `Question`/`Answer` pairs.
2. The schema content matches the visible FAQ HTML on the same page (Google penalizes mismatches).
3. Validate with Google's Rich Results Test: https://search.google.com/test/rich-results

**Verification:**
```bash
curl -s "https://www.smartenplus.co.th/trips/phuket/koh-phi-phi" \
  | grep -oE '<script type="application/ld\+json">[^<]+FAQPage[^<]+</script>' \
  | head -1
# Expected: a JSON-LD block with @type: FAQPage
```

**Rollback:** Git revert (low risk).

**Estimated effort:** S

---

## REQ-013 — Fix `dateModified` in `Service` schema

**Why:** Trip page `Service` JSON-LD shows `dateModified: "2026-01-26"` — 9 months stale at audit time. This is a stale-content signal to Google.

**Acceptance criteria:**
1. `dateModified` in `Service` (and `Product`, if present) JSON-LD must reflect the actual entity update timestamp.
2. For pages without explicit updates, set `dateModified` to the same value as `datePublished`.

**Verification:**
```bash
curl -s "https://www.smartenplus.co.th/trips/phuket/koh-phi-phi" \
  | python3 -c "import sys, re, json; [print(json.dumps(json.loads(m), indent=2)[:300]) for m in re.findall(r'<script[^>]+ld\+json[^>]*>(.+?)</script>', sys.stdin.read(), re.S) if 'Service' in m or 'Product' in m]"
# Expected: dateModified within last 30 days
```

**Rollback:** Git revert.

**Estimated effort:** XS

---

# Appendix A — Reference data (live observations from 2026-10-11 audit)

## URL pattern behavior matrix

| Pattern | Current | Required |
|---|---|---|
| `/trips/phuket/koh-phi-phi` (valid pair) | 200, real | 200, real (unchanged) |
| `/trips/zzzz/yyyy` (invalid pair) | **200, soft-404** | **404** (REQ-001) |
| `/trips/foo` (1 segment) | 404 | 404 (unchanged) |
| `/trips/a/b/c` (3 segments) | 404 | 404 (unchanged) |
| `/trips/detail/krabi-to-koh-lanta-105` (valid slug) | 200, real | 200, real (unchanged) |
| `/trips/detail/spam-9999-zzz` (invalid) | **200, soft-404** | **404** (REQ-002) |
| `/ref/route` (valid) | 200, real | 200, real (unchanged) |
| `/ref/train` (no content) | **200, placeholder** | **404 or 410** (REQ-003) |
| `/trips/Phuket/Koh-Phi-Phi` (mixed case) | **200, dup** | **301 → lowercase** (REQ-004) |
| `/help/booking-process` | 200, canonical=/help | 200, canonical=self (REQ-005) |
| `/help` (listing) | 200, canonical=/help | 200, canonical=/help (unchanged) |
| `/trips?page=2` | 200, canonical=/trips | 200, canonical=self?page=2 (REQ-008) |

## Sitemap statistics

- `sitemap-0.xml`: 80 hand-curated URLs
- `server-sitemap.xml`: 4,471 URLs
  - 2,088 `/trips/<a>/<b>` (hub) URLs
  - 1,735 `/trips/detail/<slug>` URLs
  - 42 `/ref/<slug>` URLs (1 with content, 41 dead)
  - 54 `/help/<slug>` URLs
  - 80 hand-curated SEO pages
  - Remainder: blog posts + activity + destination pages
- **2,184 URLs (49%) have `lastmod=2026-10-11T04:39:21.xxx` — within 1ms of each other** (REQ-006)

## Known soft-404 sample URLs (use these as test inputs)

```
/trips/zzzz/yyyy
/trips/abc/def/ghi
/trips/detail/spam-9999999-zzz
/trips/detail/zzz-yyyy-xxxxx
/ref/train
/ref/bus
/ref/ferry
/ref/payment
```

## Reference articles already in good shape (do not regress)

- `/help` listing (RE: REQ-005 — keep its current canonical=/help)
- `/blog/*` URLs — 404 handling correct, no soft-404 surface
- 404 page itself — returns real 404 + `noindex,nofollow` ✅

## 9-dimension audit reference

For background on each finding, see the full audit at:
`01-projects/seo-audit/reports/2026/10/2026-10-11-public-site-seo-audit.md`

The audit walks through:
1. Sitemap architecture (drift)
2. Soft-404 surface (3 templates)
3. Case + URL normalization
4. Canonical + hreflang consistency
5. Meta quality (title/desc/H1)
6. JSON-LD correctness
7. Pagination
8. Internal-link hygiene
9. Image + asset hygiene

---

# Appendix B — Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| REQ-004 redirect chain loops with REQ-005 trailing-slash redirect | M | M | Test all combinations in CI before deploy. Chain order: lowercase first, then trailing slash. |
| Sitemap regen ships 410s before REQ-003 in production | L | M | Ship REQ-003 + REQ-009 in same release, or hold REQ-009 until after. |
| Help-article self-canonical floods Search Console with "newly indexable" warnings | L | L | Informative noise, not a real issue. Monitor for 1 week post-deploy. |
| FAQPage schema fails Rich Results Test | M | L | Validate before deploy using local schema validator + Google's Rich Results Test on staging. |
| Meta-description template interpolation produces duplicate descriptions | M | M | Add a uniqueness check in CI: run a build that detects duplicate descriptions across all detail pages. |
| `/trips/[A-Z]` → `/trips/[a-z]` redirect breaks existing inbound links to mixed-case URLs | L | L | 301 preserves link equity. Track Search Console "Page with redirect" report after deploy to confirm. |

---

# Appendix C — Sequencing recommendation

**Week 1 (current sprint):** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-007

**Week 2:** REQ-006, REQ-008, REQ-009, REQ-011

**Week 3 (after data-model discussion with content team):** REQ-010

**Whenever / low priority:** REQ-012, REQ-013

The REQs are designed to be independently shippable — none block another. If only one or two can ship this sprint, prioritize in the order listed. Items 1–5 are likely to produce measurable organic-traffic lift within 2–4 weeks of deploying (Google's typical re-crawl window). Items 6–13 compound over months.

---

# Appendix D — Definition of done (per requirement)

A requirement is "done" when:
1. All acceptance criteria pass.
2. The verification command(s) return expected output in production.
3. No regression: previously-passing URLs still pass.
4. The change is logged in the deployment changelog with date + responsible dev.
5. After 7 days in production, Google Search Console shows no new "Page with redirect" or "Excluded by noindex" entries that suggest the fix went wrong.

**End of document. REQ count: 13. Total estimated effort: ~3–5 dev-weeks spread across 2–3 sprints.**
