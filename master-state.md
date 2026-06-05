# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-06 (session #51)

**Achieved this session (#51):**
- **HEIC review upload — IMPLEMENTATED, local deps ready** — pillow-heif 0.15.0 + libheif 1.23.0 installed locally. Backend restarted with HEIC opener registered. Code committed: backend `f82b182`, frontend `0a4e6d4`. Branch: `260606-fix/heic-review-upload`.
- **Multi-agent debate** — 2 agents evaluated base64 proxy vs pillow-heif. Chose server-side (5 lines, 33% less payload, no memory spike).

**Resume point (EXACT):**
1. **Test HEIC upload locally** — Upload HEIC file via review form, verify WebP conversion ≤120KB.
2. **Merge `260606-fix/heic-review-upload`** → main (backend) + develop (frontend).
3. **Build production Docker** with libheif-dev.
4. **Outstanding from #50:** Merge `260605-feat/review-images` → develop (frontend) + main (backend). Run migration on production.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| HEIC-1 | iPhone HEIC review upload | Implemented, deps ready. Branch `260606-fix/heic-review-upload`. Local test pending, then merge. | `dialogue/utils.py`, `RateAndReviewForm.js` |
| GYG-IMPL | GYG 5-pattern | P0-P2 done. P1 thumbnails unmerged (`260605-feat/review-images`). | Merge `260605-feat/review-images` |
| GSC-1 | GSC Crawled-Not-Indexed | Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists`. | `seoConfig.js:41`, `server-sitemap.xml` |
| CMA-1 | Contract Model Ambiguity | P1/P2 partial. Remaining: data inventory. | `operators/models.py` |
| GYG-IMPL | GYG 5-pattern | P0-P2 done. P1 thumbnails done (unmerged). | Merge `260605-feat/review-images` |
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
