# r1-aeo — Answer Engine Optimization Lens (Live Prod)

> Audit 2026-06-22 · [[r3-synthesis]] for merged priorities. AEO = optimizing content/structure so answer engines (Google AI Overviews/SGE, featured snippets, Bing Copilot) can extract and cite answers.

## Summary

AEO is **bimodal**: trip-detail and route-listing pages are **excellent** (FAQPage schema live in SSR HTML, answer-target headings, structured facts), but the **two highest-intent Q&A surfaces — `/help` and the homepage — have zero FAQ markup**, and a JS-gated help center hides the actual answer text from crawlers. Compounding all of it: the site-wide **robots.txt AI-crawler block** (see [[r1-geo]]) means even the good content never reaches answer engines. AEO fixes are frontend-only; the block is the gating issue.

## Method

SSR HTML inspection (what an answer-engine crawler sees without executing JS) + source trace of FAQ generators. Answer-target = does the page contain a self-contained Question→Answer block reachable in the static HTML?

## Per-template AEO assessment

### Homepage — **AEO score 5/10**
- ❌ **No FAQPage**. 167 JSON-LD nodes (TravelAgency/Offer/BusTrip/ItemList/Review) but no Q&A entity. A homepage for "book Thailand bus/ferry/train tickets" should answer: *How do I book? What payment methods? Can I cancel? Are tickets instant?* — high-volume informational queries.
- ❌ No `definedTerm`/definition block. First-time visitor intent ("what is SmartEnPlus", "is it legit") answered only in footer fine-print (TAT license, business reg) — not structured.
- ✅ "Thailand: All Options, One Search" / "Easy E-Tickets & Secure Payments" / "24/7 Expert Support" are answer-target-shaped copy blocks but live as marketing cards, not Q&A.
- Fix: add a homepage FAQPage (6–8 Q/A) via `components/SEO/JsonLd.js` or `generateFAQSchema`-style helper (reuse [[build-experience-faq-items-pure-function]]). Keep Q/A in SSR HTML (NOT RTK-gated — see [[isr-client-rtk-stats-seo-pattern]]).

### Trip detail — **AEO score 8/10**
- ✅ **FAQPage live in SSR HTML** (4 Question / 4 Answer, schema-valid). This is the [[trip-detail-seo-aeo-geo-audit-2026-06-16]] fix, working in production.
- ✅ TouristTrip + Product carry itinerary facts (departure, meeting point, duration) — extractable for "how to get from X to Y" answers.
- ⚠️ Description meta is messy raw content (`Meeting Point&nbsp;\n\tBARAMEE…`) — strip HTML entities for a clean answer snippet.
- Minor: schema `Question` count (4) is thin; route listings have 6. Expand to 6–8 covering price, duration, luggage, refund.

### Route listing — **AEO score 8.5/10**
- ✅ **FAQPage 6Q/6A** + BlogPosting cross-link (routes → related blog answer) + 132 schema nodes. Best-in-class AEO on the site.
- ✅ Multiple Product/Offer nodes = answer engine can cite "operators on Phuket→Koh Phi Phi start from THB 700".
- This template is the **model** the homepage/help/activity should follow.

### Activity / day-trip detail — **AEO score 4/10**
- ❌ **No FAQPage**, only 12 schema nodes (Product/Offer/Breadcrumb). A day-tour ("Chiang Mai→Chiang Rai sightseeing") has obvious Q&A: itinerary, pickup, duration, inclusions, language. None structured.
- ❌ Title is 131 chars (detail-heavy) but the page has no answer-target Q/A section to match snippet intent.
- Fix: reuse `helpers/seo/dayTripSEOUtils.js` + `DayTripDetailSEO.js` FAQ path (it exists for day-trips — verify wiring on this template; the sampled URL may be an activities-detail page distinct from day-trip detail).

### Blog index — **AEO score 7/10**
- ✅ 10 BlogPosting nodes + CollectionPage + ItemList. Blog content is the natural AEO asset (long-form answers).
- ⚠️ Title `Blogs | SmartEnPlus` (19 chars) is under-optimized — no keyword/topic signal for "Thailand travel tips/guides".
- Blog lives partly on `blog.smartenplus.co.th` (WP) — see [[r1-geo]] for the subdomain split; AEO is fragmented across two origins.

### Help / FAQ — **AEO score 2/10** ⚠️ highest-leverage gap
- ❌❌ **Zero JSON-LD** (0 nodes). No Organization, no FAQPage, no BreadcrumbList. This is the site's dedicated Q&A hub and it has the **least** answer-engine signal.
- ❌ The actual Q&A content (Booking Process, Check-in/Tickets, Delays & Cancellations, etc.) is rendered via `POSTS_AND_CHILD_CATEGORIES_BY_PARENT_CATEGORY` WP fetch (`help/index.js:9`) + dynamic breadcrumb (`ssr: false`). **Breadcrumbs are client-only (`DynamicStandardBreadcrumb`, ssr:false)** → answer engines see the category labels only after JS runs.
- ❌ Category titles ("Booking Process", "Delays & Cancellations") are **answer-target headings** but the underlying Q/A text is loaded client-side from WP — not in SSR HTML.
- Description meta = `Support Customers ` (truncated, no value).
- Fix: SSR-render the help category list + top FAQ Q/A; emit a **FAQPage** schema from the real questions; fix canonical/og (see [[r1-seo]] SEO-2). Reuse [[build-experience-faq-items-pure-function]] shape. This single page is the biggest AEO ROI.

### Airport transfer — **AEO score 4/10**
- ❌ Zero JSON-LD. A hub listing of airports (BKK, HKT, PEN…) should carry an **ItemList** of transfer services + a small FAQ ("how to book airport transfer", "meet and greet").
- ✅ Station cards exist in DOM but are JS-rendered (`useState`/`useEffect`, `StationCard`). Listing is crawlable via internal links but not structured.
- Fix: emit ItemList + FAQPage; SSR the station list.

### `/ref/article/*` (404) — n/a
- 404 for 41 sitemap URLs (see [[r1-seo]] SEO-1). When working, these were strong AEO assets (ArticleJsonLd + BreadcrumbJsonLd + CitationSection — designed as factual reference). Their disappearance removes authoritative answer content the site was banking on. **Restore WP articles or remove from sitemap.**

## Cross-cutting AEO issues

### AEO-1 · Answer content must be in SSR HTML (not RTK/WP-gated) — **P1 pattern**
- Recurring root cause across templates: question/answer text loaded client-side (RTK Query, `ssr:false` dynamic imports, WP fetch in `useEffect`). Answer engines (and Google's crawler for AI Overviews) increasingly read **server-rendered HTML**.
- Rule (already in vault): data in below-fold/answers → ISR `getStaticProps`, not client fetch. See [[isr-client-rtk-stats-seo-pattern]], [[trip-detail-server-side-seo-pattern]], [[nextseo-v6-jsonld-silent-drop]] (why `jsonLd` prop on `<NextSeo>` is silently dropped → use raw `<script type="application/ld+json">`).
- Trip detail + route listing already follow this. Homepage/help/activity do not.

### AEO-2 · No `definedTerm`/entity definitions — **P2**
- Site has authoritative entity context (TAT License, routes, operators, piers) but no `DefinedTerm`/`Glossary` markup. `/ref` (terminology section) is the natural home — when its articles 404 (AEO-1 above), that entity layer is gone.
- Fix: restore `/ref` terminology articles OR add a glossary FAQ to the homepage.

### AEO-3 · Review answer-snippet bait is thin — **P2**
- Homepage AggregateRating shows "10+ reviews" — too thin for "is SmartEnPlus legit" answer citations. The 3 Review nodes are 5★ but few. More review volume → more citation trust (also a GEO lever).

## AEO scoring summary

| Template | Score | Blocker |
|----------|------:|---------|
| Route listing | 8.5/10 | — (model page) |
| Trip detail | 8/10 | thin Q count, messy desc |
| Blog index | 7/10 | title, subdomain split |
| Homepage | 5/10 | no FAQPage |
| Activity detail | 4/10 | no FAQ, thin schema |
| Airport transfer | 4/10 | no schema, JS-gated list |
| **Help/FAQ** | **2/10** | zero schema + client-only content |
| `/ref/article` | n/a | 404 (SEO-1) |

**Note:** every score above is **capped by the robots AI-crawler block** ([[r1-geo]] GEO-1). No answer engine can reach any of this until that block is lifted. The scores reflect *latent* AEO quality, not current answer-engine visibility.

## Related
- [[r1-seo]] · [[r1-geo]] · [[r3-synthesis]]
- [[build-experience-faq-items-pure-function]] · [[trip-detail-server-side-seo-pattern]]
- [[isr-client-rtk-stats-seo-pattern]] · [[nextseo-v6-jsonld-silent-drop]] · [[wordpress-faqpage-deprecation-note]]
- [[trip-detail-seo-aeo-geo-audit-2026-06-16]] · [[trip-route-page-seo-aeo-geo-audit]]
