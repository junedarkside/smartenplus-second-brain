# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-06 (session #56)

**Achieved this session (#56):**
- **Website audit team review COMPLETE** — 3 specialists (Performance/CWV, Mobile UX/A11y, SEO+AI Recognition) + Skeptic + Leader. 15 audit issues → **12 P0-P3 items** with file:line refs, ~18 hrs impl work. 5 audit claims reclassified as ALREADY DONE (compress, WebP config, GTM deferred, InArticleCTA, DayTripDetailSEO).
- **Created orchestrator agent** — `smartenplus-frontend/.claude/agents/website-audit-team-orchestrator.md` (mirrors gyg/seo-homepage pattern, ready for future audits).
- **5 working files** in `01-projects/website-audit-full-2026-06-06/`: r1-performance, r1-mobile-ux, r1-seo-ai, r2-skeptic, r3-leader-synthesis.
- **Extended main doc** — `01-projects/website-audit-full-2026-06-06.md` 258→432 lines, added `# Team Review & Implementation Plan` section.
- **Vault index + log updated.**

**Resume point (EXACT):**
1. **Sprint 1 P0 (Website Audit)** — frontend branch `develop`. Start with F1 (lowest risk):
   - F1: 14px → 16px search inputs — `components/search/ProductSearchForm2.js:231, 260, 283, 311, 329` + `SearchDialogTrigger.js:19` (30 min)
   - F2: 44×44px touch targets (WCAG 2.5.5) — CurrencySelector, ProfileButton, CartButton, swap/date/passenger buttons (1-2 hrs)
   - F3: WhatsApp 20×20 → 44×44 wrapper — ShareButton, footer, Passenger, ContactUs (1 hr)
   - Test at 320px (iPhone SE) before F2 merge
2. **Verify FE-22 API shape** — check `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response: `slug` or `booking_item_slug`? Fix `[...slug].js:71-72` accordingly.
3. **Build production Docker** with `libheif-dev` (backend HEIC dependency).

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **WA-1** | **Website audit Sprint 1 (F1-F3)** | P0 batch. 14px→16px inputs, 44×44 touch targets, WhatsApp wrapper. ~3 hrs. | `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileButton.js`, etc. |
| **WA-2** | **Website audit Sprint 2 (F4-F8)** | P1 batch. Inter font self-host, carousel scroll-snap, nav dedupe, OG image, search form overflow. ~7 hrs. | `_document.js`, `*Carousel.js`, `navConfig.js`, `og-image.webp` |
| **WA-3** | **Website audit Sprint 3 (F9-F11)** | P2 batch. Inline style extraction, brand name, FAQPage. ~6 hrs. | `ProfileMenu.js`, `helpers/constants.js`, `homepagev2.js:493-495` |
| RR-1 | Rate-review Release 1 shipped | P0+P1-1+P1-2 DONE. FE-22 deferred (API unverified). Sprint 1 (P1-3→P1-9) pending. | `[reviewSlug].js`, `BookingReviewList.js`, `RateAndReviewForm.js`, `ReviewList.js` |
| GYG-IMPL | GYG 5-pattern | P0-P2 done. P1 thumbnails done (unmerged). | Merge `260605-feat/review-images` |
| GSC-1 | GSC Crawled-Not-Indexed | Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists`. | `seoConfig.js:41`, `server-sitemap.xml` |
| CMA-1 | Contract Model Ambiguity | P1/P2 partial. Remaining: data inventory. | `operators/models.py` |
| CART-1 | PARSING_ERROR catch | Deferred from #34. | `DayTripBookingWidget.js:338` |
| FAQ-1 | ExperienceFAQ | P0-P2 done. Admin `ageRestriction` deferred. | `admin-dashboard/DayTripDetails.js` |
| FAV-1 | Favorite heart | ADR ready. 4 files. | `dialogue/views.py`, `BookmarkButton.js` |
| AT-1 | Airport Transfer redesign | P0. Spec: `03-knowledge/transportation-category-audit`. | `AirportTransferRouteCard.js` |
| AT-2 | Airport-transfer width mismatch | Inner margins. | `StationInformation.js` etc. |
| TSTD-1 | Test infrastructure | BLOCK RELEASE. 6 CRITICAL. 4-5 dev days. | `jest.setup.js`, `e2e/` |
| 15 | refetchOnMountOrArgChange | Needs justification. | `useTripData.js:16,24` |
| 1 | AdminBookingSummaryViewSet auth | Needs frontend sign-off. | `orders/views.py` |
| 2 | Delete RefundViewSet | Waiting on zero DEPRECATED_ENDPOINT_USED. | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic. | `payments/urls.py` |
| 8 | Forex endpoint naming | Naming debt. | `cards/urls.py` |
| Nav | NavigationSection empty | Restart backend + populate. | `pages_info` |
| Explore | location_type CharField | Needs `Location` model change. | `stations/models.py` |
| HD-1 | CurrencySelector small tablet | Low. | `CurrencySelector.js:55` |
| HD-2 | CartButton dim (70%) | Low — acceptable. | `CartButton.js:116` |
| HD-3 | xl padding gap | Low. | `main-header.js:90` |
| HD-6 | Logo size jump | P2. | `main-header.js:66,95` |
| GAP-3 | Mobile position flip | P2. | `main-header.js:45-77` |
| GAP-5 | Nav hidden while searching | P2 — accepted. | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3. | `useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden md-xl | P3. | `main-header.js:95` |
| IDX-1 | Unindexed experience-detail | Add to index.md. | `01-projects/` |
| IDX-2 | Unindexed experience-faq | Add to index.md. | `01-projects/` |
| IDX-3 | Missing content-marketing-strategy | Verify intent. | `03-knowledge/` |
| IDX-4 | Duplicate-basename wikilinks | 3 conflicts. Rename with suffix. | Various |

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38-#49) · [[closed-items]] (resolved)
