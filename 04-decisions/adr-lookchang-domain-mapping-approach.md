# ADR: lookchang.com Domain-Mapping Approach — 3-Lens Review Verdict

## Status
proposed — 3-lens review (Business Dev/SWE/Architecture, 3 parallel background agents) run 2026-09-25 against the `lookchang.com` domain-mapping plan recorded in [[multi-market-i18n-analytics-migration]]. Findings below are a recommendation, not yet an accepted implementation decision — no nginx/middleware code built from this review.

## Context
`smartenplus.co.th/th` is live (one real page, `/th/about`). A separate `lookchang.com` domain, carrying a distinct "LookChang" brand for the Thai market, has been proposed since the original external consultant report but was never validated against this codebase, never given an owner, and never scheduled — tracked in the vault as an explicitly unvalidated block ("no business commitment on timing," "re-audit each individually when actually reached").

On 2026-09-25 the project owner accepted accountability for this specific sub-item, gated on `smartenplus.co.th/th` "working properly" first (see [[multi-market-i18n-analytics-migration]] OWNERSHIP DECIDED note). Before committing engineering time, a 3-lens review was run to sanity-check the domain-mapping *approach itself* — not just whether to do it, but whether the mechanism already sketched in the vault (`next.config.js` hostname rewrites) is actually sound.

## Review Method
3 independent background agents, each given the same confirmed facts (current `/th` architecture, chosen-but-unbuilt mechanism, nginx/Cloudflare state) and told to ground findings in real-world practice, not restate the vault's own framing:
- **Business Dev / GTM** (`business-analyst-expert`)
- **Software Engineer** (`backend-architect`, infra/mechanism lens)
- **Architecture** (`backend-architect`, system-design lens)

Full findings published as artifacts this session (screenshots/diagrams, session-scoped, not persisted as vault files): EN status report, Thai translation, 3-lens synthesis (EN + Thai), plain-language summary.

## Findings

### Business Dev
Dark-subpath-first with no exit date diverges from how comparable OTAs (Agoda, Klook, Booking) actually sequence market entry — they launch indexed and branded from day one; dark-subpath is normal only as a short (4-8 week) technical QA gate, not an open-ended default. "Inherited from a consultant report, no business commitment on timing" is a textbook zombie-backlog signature — no one's OKRs depend on it shipping. Real cost, not free optionality: every quarter without indexed Thai content is a quarter not compounding toward search authority.

### Software Engineer
The sketched mechanism — `next.config.js` hostname-conditional `rewrites()` — is likely the wrong layer for a Docker+nginx deployment (that pattern fits Vercel's edge-as-router model, not a reverse-proxy-fronted app). Better fit: nginx `server_name`-level host dispatch (two blocks, same upstream) + the already-present but inert `middleware.js` (currently just re-exports NextAuth, `matcher: []`) carrying a brand-context signal downstream. The nginx Host-header-forwarding unknown is real but trivial (`proxy_set_header Host $host;`, one line) — `server_name` needs `lookchang.com` added regardless, the actual first blocker. Unaddressed risks named: auth cookie domain-scoping (won't carry over to a new domain by default), CORS/CSRF backend allow-list (silent 403 if unadded), CSP (`frame-ancestors` silently blocks new host), canonical-tag duplicate-content risk across two live domains serving identical `/th` content.

### Architecture
The earlier 3-axis→1-axis simplification (dropping `market`, keeping `language`) was correct — avoided duplicating the Django backend's own i18n system. But `BRANDS` (`helpers/siteContext.js`) got accidentally coupled to the language axis in the same motion — keyed by the identical string as `SUPPORTED_LANGUAGES`, meaning brand and language are currently the same variable under two names. Breaks the moment they need to vary independently (e.g. an English-language LookChang page for tourists). Correct model was 2-axis (language × brand), not 1. **Sharpest finding across all three lenses**: `getCurrentLanguage()`'s SSR fallback silently returns English with no error when it can't detect language server-side — a live landmine for the next SSR page built without an explicit `lang` arg, not a hypothetical (fixed same-day, see Consequences below). Brand-consolidation debt (60+ hardcoded "SmartEnPlus" files) compounds non-linearly per additional market, not linearly — each new brand turns dead-weight literals into live customer-visible bugs.

## Decision
Not yet made — this ADR records the review verdict, not an implementation commitment. The gate set 2026-09-25 (work starts once `/th` is "working properly") stands. This review defines what "working properly" should include before that gate is considered satisfied:
1. The SSR-default-to-English landmine must be fixed (loud, not silent) — **done same day**, see Consequences.
2. Remaining English UI chrome on `/th/about` (nav/footer/`ContactUs`) should be addressed — **`ContactUs` done same day**; nav/footer remain, larger scope, not started.
3. Before any `lookchang.com` engineering starts: get a real nginx+middleware host-dispatch prototype working on staging (not `next.config.js` rewrites), and attach a real time/cost estimate to the whole domain-mapping phase — converts it from an unowned line item into a schedulable decision.

## Consequences
- `helpers/siteContext.js`'s `getCurrentLanguage()` now `console.warn`s on server-side calls instead of silently defaulting — shipped 2026-09-25, branch `fix/th-about-ssr-default-and-chrome`, not yet merged to `develop`.
- `components/pages-info/ContactUs.js` now branches static strings by language via `useSite()` — shipped same branch, same day. Pattern documented at [[sitecontext-language-branch-pattern]].
- Nav bar / footer translation remains unscoped — larger surface than the "cheap fix" bar this session targeted.
- The `BRANDS`/language-axis coupling flagged by Architecture is **not yet fixed** — real risk, deliberately deferred, not silently dropped. Should be addressed before any `lookchang.com` engineering begins, per the mechanism this ADR reviews.
- No nginx/middleware prototype work has started. No time/cost estimate exists yet.

## Related
- [[multi-market-i18n-analytics-migration]] — parent project; OWNERSHIP DECIDED note this ADR's review was commissioned to inform
- [[nextjs-page-router-no-fallback-routing]] — separate but related finding from the same day (why `/th` itself 404s)
- [[nextjs-builtin-i18n-vs-page-cloning]] — the routing-model alternative that would also close the SSR-default-language gap as a side effect
- [[sitecontext-language-branch-pattern]] — the pattern used for the same-day `ContactUs.js` fix
