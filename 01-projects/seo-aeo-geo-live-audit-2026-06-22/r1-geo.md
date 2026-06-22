# r1-geo — Generative Engine Optimization Lens (Live Prod)

> Audit 2026-06-22 · [[r3-synthesis]] for merged priorities. GEO = visibility in generative engines (ChatGPT/OpenAI, Claude/Anthropic, Gemini/Google, Perplexity, Meta AI, Copilot). The decisive lever is **crawl permission** — everything else is moot if AI crawlers are blocked.

## Summary

**GEO score today: ~1.5/10 — and ~all of it is one defect.** The live `robots.txt` (Cloudflare-managed) **blocks every major AI crawler** with `Disallow: /` (GPTBot, ClaudeBot, Google-Extended, CCBot, meta-externalagent, Bytespider, Applebot-Extended, Amazonbot). Result: SmartEnPlus **cannot appear** in ChatGPT answers, Claude responses, Gemini grounding, Perplexity, or Meta AI — regardless of content/schema quality. Lifting the block is a Cloudflare dashboard toggle (frontend robots cannot override it). Secondary GEO gaps: thin `sameAs`/entity signals, review volume too low for citation, blog siloed on a separate subdomain, no `llms.txt`.

## The robots.txt block — full evidence

Live `https://www.smartenplus.co.th/robots.txt` (fetched 2026-06-22, Cloudflare edge):

```
# BEGIN Cloudflare Managed content
User-agent: *
Content-Signal: search=yes,ai-train=no

User-agent: Amazonbot
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot            # Perplexity
Disallow: /

User-agent: ClaudeBot        # Anthropic / Claude
Disallow: /

User-agent: CloudflareBrowserRenderingCrawler
Disallow: /

User-agent: Google-Extended  # Gemini grounding
Disallow: /

User-agent: GPTBot            # OpenAI / ChatGPT
Disallow: /

User-agent: meta-externalagent  # Meta AI
Disallow: /
# END Cloudflare Managed Content
```

**Diagnosis:**
- The block is auto-injected by **Cloudflare** ("BEGIN/END Cloudflare Managed content"). It is **NOT** in `smartenplus-frontend/next-sitemap.config.js` (which only sets `User-agent: *` allow + private-path disallows). CF prepends its managed block at the edge and **overrides** frontend robots.
- `Content-Signal: search=yes, ai-train=no` — explicit reservation against training (fine to keep), but **no `ai-input` signal** is set. Per the file's own preamble, a missing signal "neither grants nor restricts" — but the `Disallow: /` per-UA rules take precedence and hard-block the crawlers regardless.
- Affected engines: ChatGPT (GPTBot), Claude (ClaudeBot), Gemini AI Overviews/grounding (Google-Extended), Perplexity (CCBot), Meta AI (meta-externalagent), ByteDance/Doubao (Bytespider), Apple Intelligence (Applebot-Extended), Amazon Q/Rufus (Amazonbot).
- **Not blocked**: `PerplexityBot` (Perplexity's newer crawler) is not listed — but CCBot (its primary indexer) is, so Perplexity is effectively dark.

## Fix spec — allowlist (draft, not applied)

### Step 1 — Cloudflare (REQUIRED, decisive)
The frontend cannot override CF's managed robots. Action in Cloudflare dashboard:
- **Zone → Security → Bots → "AI Scrapers and Crawlers" toggle → DISABLE (Allow).**
- Or, if keeping training protection: use **AI Audit** "allow list" / WAF custom rule to permit specific AI UAs while keeping `ai-train=no` Content-Signal.
- After toggling: the `# BEGIN Cloudflare Managed content` block is removed/neutralized; the frontend `next-sitemap.config.js` policy becomes authoritative.

### Step 2 — Frontend explicit allowlist (`next-sitemap.config.js`)
Add explicit allow rules so intent is unambiguous and survives any CF policy drift. Draft (mirrors current `siteUrl`/`robotsTxtOptions`):

```js
robotsTxtOptions: {
  policies: [
    // Default: crawl for search + AI grounding/answers, block training
    { userAgent: '*', allow: '/', disallow: ['/orders','/checkout','/account','/profile','/bookings','/guest-order','/dev'] },

    // --- AI answer/grounding crawlers: ALLOW (GEO) ---
    { userAgent: 'GPTBot',          allow: '/' },
    { userAgent: 'OAI-SearchBot',   allow: '/' },   // ChatGPT search
    { userAgent: 'ClaudeBot',       allow: '/' },
    { userAgent: 'anthropic-ai',    allow: '/' },
    { userAgent: 'Google-Extended', allow: '/' },   // Gemini
    { userAgent: 'CCBot',           allow: '/' },   // Perplexity
    { userAgent: 'PerplexityBot',   allow: '/' },
    { userAgent: 'meta-externalagent', allow: '/' },// Meta AI
    { userAgent: 'Bytespider',      allow: '/' },   // optional — BYD market
    { userAgent: 'Applebot-Extended', allow: '/' }, // Apple Intelligence

    // --- Training: keep blocked (Content-Signal ai-train=no handles this) ---
  ],
  additionalSitemaps: ['https://www.smartenplus.co.th/server-sitemap.xml'],
},
```

Keep `Content-Signal: search=yes, ai-train=no` (CF-managed) to **protect training** while permitting grounding/answers. This is the recommended posture: let AI engines *read and cite* you, but not *train* on you.

**Verification after change:** `curl https://www.smartenplus.co.th/robots.txt` — confirm no `Disallow: /` under AI UAs. Then check GSC + each engine's crawl reports over 1–2 weeks.

### Decision input: allow training too?
- **Allow grounding/answers only (recommended)** — preserves brand control, blocks competitors training on your content/route data. Matches current `ai-train=no`.
- Allow training — maximizes long-tail mention probability (models that trained on you cite you more), but gives away route/price/operator data. Not recommended for a booking platform with proprietary inventory.

## Secondary GEO findings

### GEO-2 · Weak `sameAs` / entity signals — **P1**
- Footer carries strong offline entity proof: **TAT License 11/06622**, **VAT TH 0105554078213**, **Business Reg 0105554078213**, NAP, registered in Bangkok. But these are **not surfaced as schema `identifier`/`sameAs`/`taxID`** on the Organization/TravelAgency node.
- No `sameAs` links to authoritative external entities (Wikidata, Wikipedia, Google Business Profile, official tourism registry, social profiles). Generative engines ground brand mentions via `sameAs` — its absence weakens "is this a real/legit business" confidence.
- Fix: extend the Organization/TravelAgency schema (likely in `components/SEO/LocalBusinessSchema.js` or homepage `_app`/SEO config) with `sameAs: [GBP url, Facebook, Naver blog, …]`, `taxID`, `areaServed: TH`, `identifier` for TAT license.

### GEO-3 · Review/citation volume too thin — **P1**
- Homepage AggregateRating = "10+ reviews", 3 Review nodes. Generative engines cite volume + recency. "10+" is below the threshold where engines confidently cite "travelers rate SmartEnPlus X/10".
- Tied to [[trip-detail-server-side-seo-pattern]] review pipeline. More reviews → higher citation probability (also AEO-3).

### GEO-4 · Blog siloed on subdomain — **P2**
- `blog.smartenplus.co.th` (WordPress) is a separate origin. Its robots presumably inherits the same CF AI block (verify). Long-form guides (the strongest GEO content — "how to get from X to Y", "drone rules Thailand") are split from the booking domain, diluting entity authority.
- Options: (a) reverse-proxy blog under `/blog` on main domain (canonical consolidation), (b) keep subdomain but ensure AI-crawler allow applies there too, (c) cross-link aggressively. See prior [[blog-canonical-url-wp-subdomain-bug]].

### GEO-5 · No `llms.txt` — **P2**
- No `/llms.txt` (emerging convention to point AI crawlers at canonical content/descriptions). Low effort, emerging standard. Optional but cheap GEO signal.

### GEO-6 · Authoritative reference content is dark — **P1**
- The `/ref` terminology/route articles (designed as factual, citation-worthy reference with `CitationSection`) are **404ing** ([[r1-seo]] SEO-1). This was the site's GEO backbone — the kind of factual, well-structured content generative engines prefer to cite. Restoring it (or replacing with a live equivalent) is high GEO ROI.

## GEO scoring

| Lever | State | Score |
|-------|-------|------:|
| AI-crawler permission (robots) | **All blocked (CF)** | 0/10 |
| `Content-Signal` ai-input | not set (neutralized by Disallow) | 1/10 |
| Structured data quality (product pages) | Strong | 7/10 |
| Entity `sameAs`/taxID/areaServed | Absent | 2/10 |
| Review citation volume | Thin (10+) | 3/10 |
| Factual reference content (/ref) | 404 | 0/10 |
| Blog authority consolidation | Subdomain silo | 3/10 |
| `llms.txt` | Absent | 0/10 |

**Composite GEO: ~1.5/10** — gated almost entirely by the robots block. Lift the block + restore `/ref` + add `sameAs` → realistic path to 6–7/10.

## What "good GEO" looks like for SmartEnPlus
1. AI crawlers allowed (grounding/answers), training blocked.
2. Every bookable + route + reference page has clean SSR FAQ + Product schema.
3. Organization node with `sameAs` (GBP, social, Wikidata if notable) + `taxID`/`identifier` (TAT).
4. `/ref` terminology/route articles live and cited-able.
5. Reviews in the hundreds, recent, with distribution.
6. Blog consolidated or at least AI-crawlable on its subdomain.

## Related
- [[r1-seo]] · [[r1-aeo]] · [[r3-synthesis]]
- [[canonicalization-audit-checklist]] · [[blog-canonical-url-wp-subdomain-bug]]
- [[trip-detail-seo-aeo-geo-audit-2026-06-16]] · [[operator-detail-seo-aeo-geo-audit]]
