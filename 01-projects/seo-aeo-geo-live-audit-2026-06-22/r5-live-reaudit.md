---
title: "SEO/AEO/GEO Live Re-Audit 2026-06-22"
type: live-reaudit
status: complete
date: 2026-06-22
scope: live-production — HTTP fetch verification of r1+r3+r4 findings
method: WebFetch against https://www.smartenplus.co.th
specialists: SEO-Live · AEO-Live · GEO-Live
---

# Live Re-Audit: SEO/AEO/GEO — 2026-06-22

Three specialists fetched live production pages and verified findings from r1-seo, r1-aeo, r1-geo, r3-synthesis, and r4-peer-review against actual HTTP responses. Several prior findings were wrong in significant ways.

---

## Critical URL Structure Correction

**The most important finding from this re-audit:**

The entire r1-seo/r3/r4 analysis of `/ref/` URLs was **inverted**.

| Claim | Reality (live verified) |
|-------|------------------------|
| `/ref/article/{slug}` = correct live URL | **WRONG** — returns HTTP 404 |
| `/ref/{slug}` = wrong path (canonical bug) | **WRONG** — returns HTTP 200, is the correct live URL |
| `server-sitemap.xml` generates wrong `/ref/{slug}` URLs | **WRONG** — `/ref/{slug}` is correct; server-sitemap is fine |
| `CitationSection.js:32` generates broken URLs | **WRONG** — it generates `/ref/${slug}` which matches live canonical |
| `pages/ref/article/[slug].js:91` canonical is wrong | **WRONG** — canonical is `https://www.smartenplus.co.th/ref/${slug}` which is correct |

**What is actually broken:** `sitemap-0.xml` lists 41 URLs using `/ref/article/{slug}` format — these 404. Fix: regenerate sitemap using `/ref/{slug}` format.

---

## robots.txt (live)

```
User-agent: *
Content-Signal: search=yes,ai-train=no
Allow: /

User-agent: Amazonbot
Disallow: /
User-agent: Applebot-Extended
Disallow: /
User-agent: Bytespider
Disallow: /
User-agent: CCBot
Disallow: /
User-agent: ClaudeBot
Disallow: /
User-agent: CloudflareBrowserRenderingCrawler
Disallow: /
User-agent: Google-Extended
Disallow: /
User-agent: GPTBot
Disallow: /
User-agent: meta-externalagent
Disallow: /

User-agent: *
Allow: /
Disallow: /orders, /checkout, /account, /profile, /bookings, /guest-order, /dev
```

**Status: STILL BLOCKED** — all 8 AI crawlers explicitly Disallowed.

New: `Content-Signal: search=yes,ai-train=no` (Cloudflare EU DSM Article 4 opt-out). This is non-standard; no major AI crawler has adopted it. Does NOT replace explicit `Disallow` rules.

**Risk:** `next-sitemap.config.js` has `generateRobotsTxt: true`. If CF toggle is disabled without updating this config, next deploy regenerates `public/robots.txt` and loses the policy. Add explicit AI-UA allows to `next-sitemap.config.js` before or alongside the CF toggle.

---

## SEO Live Findings

### sitemap-0.xml
- Total URLs: **107**
- `/ref/article/*` present: **YES — 41 URLs** — all 404
- **Status: STILL POISONED**

### server-sitemap.xml
- Total URLs: **3,561**
- `/ref/{slug}` URLs: **YES — correct, 200 OK**
- `/operators/*`: YES — 36 URLs
- `/locations/*`: YES — 176 URLs
- **Status: CORRECT**

### /help canonical
- Live canonical: `https://smartenplus.co.th/help` (apex, no www)
- `og:url`: `https://www.smartenplus.co.th` (root — not /help)
- Title: `"Help Center | SmartEnPlus | SmartEnPlus"` — double-brand
- JSON-LD: NONE
- **Status: UNCHANGED — still broken**

### /help/faqs
- Canonical: `https://www.smartenplus.co.th/help/faqs` (www — correct)
- `og:url`: `https://www.smartenplus.co.th` (root — wrong)
- Title: `"Help & FAQs | SmartEnPlus | SmartEnPlus"` — double-brand
- JSON-LD: FAQPage (mainEntity: []), BreadcrumbList
- **FAQPage is present but EMPTY** — `mainEntity: []`

### og:locale (all pages)
- Homepage: `th_TH`
- /help: `th_TH`
- /help/faqs: `th_TH`
- /airport-transfer: `th_TH`
- /about: `th_TH`
- **Status: UNCHANGED — site-wide th_TH**

### Double-brand titles (live)
| Page | Title | Double-brand |
|------|-------|:---:|
| Homepage | `Book Bus, Ferry & Train Tickets in Thailand \| SmartEnPlus` | NO |
| About | `About Us \| SmartEnPlus` | NO |
| /help | `Help Center \| SmartEnPlus \| SmartEnPlus` | YES |
| /help/faqs | `Help & FAQs \| SmartEnPlus \| SmartEnPlus` | YES |
| /airport-transfer | `SmartEnPlus All Airport Transfers - Page 1 \| SmartEnPlus` | YES |
| 404 | `Page Not Found - SmartEnPlus \| SmartEnPlus` | YES (noindex — cosmetic only) |

### About page
- JSON-LD: NONE
- og:locale: `th_TH`
- TAT license 11/06622: in text only (not schema)
- **Status: CONFIRMED zero schema**

### /ref/{slug} pages (correct URL)
- HTTP status: **200 OK**
- Canonical: correct (`/ref/{slug}` format)
- Article schema: present (`@type: Article`, headline, datePublished, author, publisher)
- CitationSection: URLs use `/ref/${slug}` — **CORRECT**

### Airport transfer
- JSON-LD: NONE
- Station list: SSR-rendered (visible in HTML)
- Title: double-brand (prepended + appended)

---

## AEO Live Findings

### Homepage
- JSON-LD types: WebPage, TravelAgency, Service, WebSite, **ItemList (routes)**, **ItemList (destinations)**
- FAQPage: NO
- AEO score: **4/10** (up from 3/10 — ItemList schemas are new)

### /help index
- JSON-LD: NONE
- FAQPage: NO
- Q titles in SSR HTML: YES (as link text — no answers)
- AEO score: **2/10** (unchanged)

### /help/faqs — CRITICAL NEW FINDING
- FAQPage: YES — but `mainEntity: []` (zero Q/A pairs)
- Root cause: `getServerSideProps` calls `POSTS_BY_FAQ_CATEGORY` WordPress GraphQL — returns empty array in production
- Answer text: client-only (DOMPurify in `useEffect`) — even if data loads, answers not in SSR HTML
- AEO score: **1/10** (worse than r4 "working schema" claim)

### Activity detail (tested: longtail-fishing-trip-koh-lipe-for-2-pax-1352)
- JSON-LD types: Product, BreadcrumbList, Organization
- FAQPage: NO — `generateFAQSchema` exists in `dayTripSEOUtils.js` but not passed to `DayTripDetailSEO`
- FAQ section text: **visible in SSR HTML** ("What should I bring?", "Can I cancel?")
- AEO score: **5/10** (SSR FAQ text is positive; no schema)

### Route listing (/trips/bkk-phuket)
- JSON-LD: **NONE** — zero blocks in SSR HTML
- FAQPage: **NO** — `FilterTripsSEO.js` receives `faqMainEntity` prop but never renders it
- AEO score: **2/10** (corrected from r1's 8.5/10 — the single largest scoring error in all audits)

### Airport transfer
- JSON-LD: NONE
- FAQPage: NO
- Station list: SSR (in `__NEXT_DATA__`)
- AEO score: **3/10** (down from r1's 5/10)

---

## GEO Live Findings

### llms.txt (HTTP 200 — confirmed exists)
```
# SmartEnPlus
> Thailand's transport booking platform. Book bus, ferry, train, and airport transfer tickets online.

SmartEnPlus is an e-commerce booking platform for domestic transport in Thailand...

## Services
- Bus tickets: intercity coaches across Thailand
- Ferry tickets: island routes (Koh Samui, Koh Tao, Phuket, Koh Phi Phi, Koh Lanta)
- Train tickets: SRT State Railway of Thailand network
- Airport transfers: Suvarnabhumi, Don Mueang, Phuket International, Chiang Mai International

## How it works
1. Search by origin, destination, and date
2. Select a departure time and operator
3. Pay online (credit card, PromptPay QR, internet banking)
4. Receive confirmed e-ticket instantly

## Not in scope
- Travel advice or itinerary planning
- Hotel or accommodation booking
- Tour packages or guided tours
- Travel insurance
```
Missing: TAT license, VAT/taxID, founding year, route/operator stats, city-level data, press mentions.

### Homepage TravelAgency schema (live)
- `sameAs`: Facebook, Instagram, X/Twitter — 3 entries (no GBP, Wikidata, LinkedIn, Naver, LINE OA)
- `taxID`: `"0105554078213"` — **PRESENT**
- `identifier` (TAT license 11/06622): **ABSENT** — TAT number only in footer text
- `areaServed`: present in Service block (`Country: Thailand`) — absent from TravelAgency block itself
- `foundingDate`: **ABSENT**
- **Peer review claim "already present (sameAs/taxID/areaServed)" — PARTIALLY CONFIRMED.** taxID present; sameAs present but thin; areaServed in wrong block.

### About page
- JSON-LD: **NONE** (confirmed)
- TAT 11/06622, VAT 0105554078213, address, phone: all in page text — zero schema
- No named team members, no founding year in readable content

### Blog schema inconsistency
- Homepage TravelAgency: 3 `sameAs` entries
- `/blog` Organization: 1 `sameAs` entry (Facebook only)
- `BlogPostSchemaGenerator.js`: 1 `sameAs` entry (Facebook only)
- Blog post pages: duplicate schema conflict — frontend `BlogPosting` + WordPress `@graph Article` pointing to different canonical domains

### hreflang
- **ABSENT** — zero `<link rel="alternate" hreflang>` anywhere on the site

### Blog author
- `Person` schema: present — `name: "Traveler's Compass"` (pseudonym, weakens E-E-A-T)
- `sameAs`: ABSENT
- `jobTitle`: ABSENT
- `knowsAbout`: ABSENT

### GEO score
- r1-geo: 1.5/10
- r5 live re-audit: **3/10**
- Reason: taxID/sameAs/CitationSection/llms.txt/ref-pages all confirmed present; P0-A block unchanged

---

## Consolidated Change Table

| Finding | r1 audit | r4 peer-review | r5 live truth |
|---------|----------|----------------|---------------|
| AI crawler block | BLOCKED | BLOCKED | **STILL BLOCKED** |
| /ref/{slug} URLs | "wrong canonical" | "wrong" | **200 OK — CORRECT** |
| /ref/article/{slug} | "correct URL" | "correct" | **404 — WRONG URL** |
| server-sitemap /ref/ | "generates wrong /ref/{slug}" | "generates wrong URLs" | **CORRECT — /ref/{slug} is right** |
| CitationSection URLs | not checked | "generates /ref/article/ (broken)" | **CORRECT — generates /ref/${slug}** |
| sitemap-0.xml /ref/article/ | "404 — fix" | same | **CONFIRMED 404 — fix = regenerate sitemap** |
| /help canonical | apex (wrong) | apex (wrong) | **STILL APEX** |
| /help og:url | homepage root | not noted | **CONFIRMED — points to root** |
| /help/faqs FAQPage | not scored | "working schema" | **BROKEN — mainEntity:[]** |
| /help/faqs og:url | not checked | not checked | **WRONG — points to root** |
| Route listing FAQPage | "8.5/10, live in SSR" | "dropped by FilterTripsSEO" | **CONFIRMED ZERO — 2/10** |
| Activity detail FAQPage | "7/10" | "not wired" | **CONFIRMED NO FAQPage** |
| Activity FAQ text | not noted | not noted | **IN SSR HTML (positive)** |
| llms.txt | absent | exists-thin | **CONFIRMED 200 + content** |
| org sameAs/taxID | missing | already present | **CONFIRMED PRESENT** |
| org areaServed | missing | already present | **PARTIAL — in Service block, not TravelAgency** |
| org TAT identifier | not noted | not noted | **ABSENT** |
| about page schema | not noted | zero schema | **CONFIRMED ZERO** |
| /airport-transfer JSON-LD | zero | zero | **CONFIRMED ZERO** |
| homepage ItemList schemas | not noted | not noted | **PRESENT (new positive)** |
| blog sameAs inconsistency | not noted | not noted | **FOUND — 3 vs 1 entries** |
| hreflang | not noted | not noted | **ABSENT site-wide** |

---

*Live re-audit by: SEO-Live · AEO-Live · GEO-Live agents · 2026-06-22*
*Updates: r3-synthesis, r4-peer-review patched in-place. Vault atoms: see index.md.*
