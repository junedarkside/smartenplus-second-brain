# Trip Route Page SEO/AEO/GEO Audit — 2026-06-15

## Summary
3-specialist deep audit of `/trips/hatyai/koh-lipe` post below-fold redesign. Found 3 P0 blockers: FAQPage missing from SSR HTML (client-only via RTK), wrong blog/overview content served (Khao Lak data on Hatyai route), and ItemList URLs relative not absolute. 4 P1 gaps. Page scores GEO 5.7/10, AEO 4.7/10.

## Implementation Status — 2026-06-15 ✅

All code-fixable items shipped. FE `develop` @ `45f5d7e`, BE `develop` @ `c24e73d`.

| Finding | Status | Commit |
|---|---|---|
| P0-1 FAQ not in SSR HTML | ✅ Fixed | `45f5d7e` — gate on `contracts.length` |
| P0-2 Wrong overview/blog content | ⏳ Pending | Django admin content fix required |
| P0-3 ItemList URLs relative | ✅ Fixed | `45f5d7e` — `NEXT_PUBLIC_DOMAIN` fallback |
| P1-1 H1 empty at SSR | ✅ Fixed | `45f5d7e` — `initialFromLocation` fallback |
| P1-2 LocalBusiness BusStation | ✅ Fixed | `45f5d7e` — `Place` type |
| P1-3 transport_type missing | ✅ Fixed | `45f5d7e` + `c24e73d` — real `transport_composit` data |
| P2-1 TripSummary aria-label | ✅ Fixed | `45f5d7e` |
| P2-2 S3 preconnect | ✅ Fixed | `45f5d7e` |
| Bonus: Service JSON-LD | ✅ Added | TripOverview |
| Bonus: BlogPosting schema | ✅ Added | BlogPost |
| Bonus: duplicate FAQPage | ✅ Removed | FilterTripsSEO |
| Bonus: findMinSellingRate type-aware | ✅ Fixed | helpers/utils.js |
| Bonus: ProductJsonLd Math.max→min | ✅ Fixed | seoConfig.js |
| Bonus: transportModes real data | ✅ Fixed | "van standard, speedboat standard" in meta desc |

**Remaining manual:** Django admin → `RouteByLocationInfo` hatyai→koh-lipe → fix `overview` text (currently Khao Lak content) + `blog_slug`.

## Context
Audit triggered after below-fold SEO/AEO/GEO fixes landed on `develop` branch:
- `min_display_rate` fix in RouteFAQ
- `cheapestOperator` type-split (ADULT/VEHICLE)
- `open` on first FAQ `<details>`
- Section reorder (TripSummary before BlogPost)
- BlogPosting + Service JSON-LD added
- Duplicate FAQPage schema removed from FilterTripsSEO

Prior vault: [[trip-search-below-fold-redesign-2026-06-15]], [[structured-data-schema-patterns]]

---

## Structured Data Audit

### Schema blocks found: 10

| Schema Type | Count | Status | Issues |
|---|---|---|---|
| BreadcrumbList | 1 | ✅ PASS | None |
| Organization | 1 | ✅ PASS | Correct phone +66-61-465-5695 |
| WebSite | 1 | ✅ PASS | None |
| Service (main) | 1 | ✅ PASS | @id, provider, offers present |
| Service (overview) | 1 | ❌ FAIL | `description` = Khao Lak text (wrong route) |
| FAQPage | 0 | ❌ MISSING | Schema in `<head>` but 0 `<details>` in DOM |
| ItemList | 1 | ⚠️ WARN | URLs relative (`/detail/{slug}`), not absolute |
| BlogPosting | 1 | ⚠️ WARN | Headline = "Getting from Khao lak to Krabi" (wrong route) |
| LocalBusiness (Hatyai) | 1 | ⚠️ WARN | `@type: BusStation` — debatable but defensible |
| LocalBusiness (Koh Lipe) | 1 | ❌ FAIL | `@type: BusStation` — island/pier, semantically wrong |
| Product (ProductJsonLd) | 1 | ⚠️ WARN | Seller name has "LTDeddd" typo in one offer |

### Blockers
- **FAQPage schema present in `<head>` but zero `<details>` in DOM** — Google sees schema without backing visible content. Schema will be ignored or penalised for mismatch.
- **Service `description` = Khao Lak text** — wrong destination. Content duplication signal against this URL.
- **BlogPosting `headline` = "Getting from Khao lak to Krabi"** — associated wrong blog post.
- **ItemList relative URLs** — `"url": "/detail/SeC3IaxeeW"` — Google requires absolute URLs in structured data.

---

## Technical SEO Audit

| Check | Status | Notes |
|---|---|---|
| Title tag | ✅ | `"Hatyai to Koh Lipe \| Ferry, Bus, Van Tickets \| from THB 123 \| SmartEnPlus"` (brand suffix minor issue) |
| Meta description | ✅ | ~130 chars, route-specific |
| Canonical | ⚠️ | Uses `http://localhost:3000` (dev) → will be correct on prod |
| Robots | ✅ | `index,follow` |
| OG tags | ✅ | All 7 present, populated |
| Twitter card | ✅ | `summary_large_image` |
| HTML lang | ✅ | `lang="en"` |
| **H1 content** | ❌ | H1 renders only `"→"` arrow — location names empty at SSR time |
| Heading hierarchy | ❌ | H3 nested inside H2 somewhere; missing H1 content |
| **FAQ section in DOM** | ❌ | 0 `<details>` in SSR HTML — client-side only |
| Section DOM order | ⚠️ | Overview → TripSummary → BlogPost (FAQ absent entirely from SSR) |
| `article aria-label` | ⚠️ | TripOverview ✅, BlogPost ✅ but label is "…Trip Overview" (same as TripOverview — wrong), TripSummary ❌ no label |
| Image alt | ✅ | Blog images have alt |
| Render-blocking scripts | ✅ | None |
| Resource hints | ⚠️ | S3 CDN on `dns-prefetch`, should be `preconnect` |

### Critical: H1 is empty at SSR
`SearchCover.js` H1 uses Redux state `fromLocation`/`toLocation` which are empty until client hydration. H1 reads only `"→"` in SSR HTML. Google crawls SSR = H1 = meaningless.

### Critical: FAQ not in SSR
`RouteFAQ` wraps `tripsFilterSet?.operator_list?.length > 0` — `tripsFilterSet` comes from RTK Query (client-side). No ISR data. FAQ never appears in curl output = never in Googlebot crawl.

---

## GEO / AEO Audit

### Scores

| Dimension | Score | Notes |
|---|---|---|
| GEO Entity Coverage | 6/10 | Org + Location schemas present; no @id chain Org→Service→Location |
| GEO Content Attribution | 4/10 | Service.description wrong route; BlogPosting wrong route |
| GEO Freshness | 7/10 | dateModified present; credibility hurt by wrong content |
| AEO FAQ Visibility | 2/10 | CRITICAL — FAQ not in SSR HTML at all |
| AEO Answer Quality | 7/10 | All 6 FAQ answer paths use real data (min_display_rate, operator names, times) |
| AEO Featured Snippet | 5/10 | Schema present; visible DOM text missing until JS |
| **GEO Overall** | **5.7/10** | |
| **AEO Overall** | **4.7/10** | |

### Transport Type Gap
`useRouteSeo.js:45` reads `route.transport_type` from `avaliable_routes[]`. Field does NOT exist in `AvialableContractSerializer` — always falls back to hardcoded `"ferry, bus, van, taxi"`. Vehicle type data exists via `transport_composit.vehicle_type.vehicle_type` in TripFilter view but NOT in ISR data. Meta description transport modes are always the generic fallback.

---

## Prioritized Findings

### P0 — FAQ not in SSR HTML
- **Root cause**: `RouteFAQ` gated on `tripsFilterSet?.operator_list?.length > 0` (RTK Query, client-only)
- **Impact**: FAQPage JSON-LD has no backing DOM content → Google ignores schema. Zero AEO benefit.
- **Fix options**:
  1. Pass operator list from ISR `contracts` prop to render FAQ server-side (preferred — data already available via getStaticProps)
  2. Use `contracts.length > 0` as render gate instead of `tripsFilterSet.operator_list.length`
- **Files**: `FilterTripsPage.js:287-294`, `RouteFAQ.js` (needs props from ISR data, not RTK)

### P0 — Wrong blog post / overview content on Hatyai→Koh Lipe
- **Root cause**: `data[0]?.overview` and `blogPost` from ISR are returning Khao Lak data. Either the backend `RouteByLocationInfo` record for this route has wrong `overview` text, or `getStaticProps` is fetching the wrong route record.
- **Impact**: Service.description + BlogPosting.headline both wrong route → duplicate content signal, E-E-A-T damage, GEO mismatch.
- **Fix**: Check backend admin for hatyai→koh-lipe route `overview` field content. Fix data, not code. Possibly `blog_slug` on wrong route record.

### P0 — ItemList URLs relative
- **Root cause**: `TripSummary.js:84` — `url: \`${process.env.NEXT_PUBLIC_SITE_URL || ''}/detail/${c.slug}\`` — if `NEXT_PUBLIC_SITE_URL` undefined at build time (dev), produces `/detail/slug`.
- **Impact**: Google Rich Results Test fails; schema URLs not absolute = invalid.
- **Fix**: Ensure `NEXT_PUBLIC_SITE_URL` set in `.env.local` for dev. On prod already set, so prod-only issue irrelevant. But confirm env var set.

### P1 — H1 empty at SSR
- **Root cause**: SearchCover uses Redux `fromLocation`/`toLocation` which are not populated until client hydration.
- **Impact**: Google crawls `<h1>→</h1>`. Primary heading = arrow character. Ranking signal lost.
- **Fix**: Read from URL slug (always available SSR) as fallback for H1 text, or use `routeParams.fromSearch`/`toSearch` which come from URL params.

### P1 — Service.description wrong text
- **Root cause**: `TripOverview.js` Service JSON-LD uses `overview` prop = `data[0]?.overview` = wrong for this route (data issue, not code).
- **Impact**: Service entity described as wrong location — confuses knowledge graph.
- **Fix**: Same as P0#2 — fix backend route record data.

### P1 — LocalBusiness Koh Lipe typed as BusStation
- **Root cause**: `LocalBusinessSchema.js:20` hardcodes `'@type': 'BusStation'`.
- **Impact**: Island/pier incorrectly typed. Semantic error, minor ranking signal loss.
- **Fix**: Change to `'@type': 'TouristAttraction'` for arrival locations, or `'@type': 'Place'` as safe generic.

### P1 — transport_type field missing from ISR data
- **Root cause**: `avaliable_routes[]` serializer has no `transport_type` field. `useRouteSeo.js` checks `route.transport_type` → always undefined → falls back to hardcoded "ferry, bus, van, taxi".
- **Impact**: Meta description always generic; schema `transportModes` not route-specific.
- **Fix**: Add `vehicle_type` to `AvialableContractSerializer` via `transport_composit` (already exists on TripFilter view). Or derive from `contracts[].type` using a label map (PRIVATE→"van transfer", JOIN→"shared transport").

### P2 — BlogPost aria-label duplicates TripOverview label
- **Root cause**: `BlogPost.js` `aria-label={blogPost?.title}` but when wrong blog loaded, title is "Getting from Khao lak to Krabi" — landmark label is misleading.
- **Impact**: Screen reader announces wrong destination. Accessibility issue.

### P2 — TripSummary missing aria-label on article
- **Root cause**: `TripSummary.js:111` `<article>` has no `aria-label`.
- **Fix**: Add `aria-label="Departures by Operator"`.

### P2 — S3 CDN on dns-prefetch only
- **Fix**: Add `<link rel="preconnect" href="https://smartenplus-bucket.s3.amazonaws.com" />` to seoConfig `additionalLinkTags`.

---

## What's Working Well
- Organization schema correct (phone, social links, @id)
- Service (main) schema correct — @id, provider, offers with price
- BreadcrumbList correct 4-item chain
- WebSite schema correct
- OG + Twitter meta complete
- robots: index,follow
- `RouteFAQ` answer logic quality high (7/10) — all 6 use real API data
- `min_display_rate` fix working — price 123 THB shown in title (ADULT rate)
- `cheapestOperator` type-split fix working
- Section reorder fix working (TripSummary before BlogPost in DOM)
- BlogPosting + Service JSON-LD blocks added correctly

---

## Related
- [[trip-search-below-fold-redesign-2026-06-15]]
- [[structured-data-schema-patterns]]
- [[isr-client-rtk-stats-seo-pattern]]
- [[seo-homepage-specialist-team]]
- [[gsc-crawled-not-indexed-investigation-2026-06-05]]

---

## Audit — 2026-10-07

Fresh audit of EN `/trips/hatyai/koh-lipe` + TH `/th/trips/hatyai/koh-lipe`. 10 issues, 12 passing. This session also shipped i18n station name fixes for จุดออกเดินทาง / จุดปลายทาง (FE + BE both merged to develop).

### Findings

| # | Severity | Finding | File(s) | Status |
|---|---|---|---|---|
| 1 | HIGH | FAQPage JSON-LD never emitted when contracts exist — FilterTripsPage:235 suppresses; RouteFAQ:8 says it doesn't emit; neither emits | `FilterTripsPage.js:235`, `RouteFAQ.js:8`, `useRouteSeo.js` | Open |
| 2 | HIGH | TH BreadcrumbList position 4 `item` URL missing `/th/` prefix — `router.asPath` never includes locale | `useRouteSeo.js:24` | Open |
| 3 | MEDIUM | `[TEST]` operator names in Product offers + ItemList on both pages | Backend: deactivate test trips | Open |
| 4 | MEDIUM | Meta descriptions >160 chars + internal type names (EN: 186, TH: ~185) | `seoConfig.js`, `th.js` | Open |
| 5 | MEDIUM | `og:type: article` wrong for trip results page — should be `website` | `seoConfig.js` | Open |
| 6 | LOW | `twitter:title` + `twitter:description` absent from both pages | `seoConfig.js` | Open |
| 7 | LOW | og:image:alt on TH uses `ถึง` connector — inconsistent with `ไป` standard | `seoConfig.js` (createSeo image alt) | Open |
| 8 | CONTENT-GAP | TH page may serve English overview if `translated_overview` null | Backend admin: add Thai overview for hatyai→koh-lipe | Open |
| 9 | CONTENT-GAP | Only 1 placeholder custom FAQ (test data) — no real Thai Q&A | Admin: `/securelogin/stations/routebylocationinfo/` | Open |
| 10 | VERIFY | DynamicRouteFAQ may have `ssr: false` — FAQ text absent from initial HTML | `FilterTripsPage.js:62` | Open |
| — | FIXED | Station names i18n (จุดออกเดินทาง / จุดปลายทาง) English fallback only | FE `b9317d4d`, BE `b5bb84f` + `15d4fec` | ✅ Merged |

### Passing
- Title EN (70 chars) + TH (`ไป` connector correct)
- Canonical URL (both locales correct)
- hreflang — en, th, x-default cross-referencing
- og:title, og:image (1200×630), og:locale
- Organization schema (legalName, foundingDate, availableLanguage: ["en","th"])
- WebPage schema (datePublished, dateModified, author, publisher)
- HowTo schema (4 steps, EN + TH)
- Speakable (#route-quick-answer, #route-schedule, #route-faq all confirmed in DOM)
- robots.txt — AI bots explicitly allowed (GPTBot, ClaudeBot, Google-Extended, PerplexityBot + 7 more)

### New knowledge atoms extracted
- [[th-breadcrumb-locale-prefix-bug]] — `router.asPath` drops locale prefix in Next.js i18n
- [[route-info-station-i18n-missing-context]] — DRF nested serializer silent EN fallback when outermost serializer lacks `context={'request': request}`
