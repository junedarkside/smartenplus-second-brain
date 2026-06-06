# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-06 (session #59)

**Achieved this session (#59):**
- **3 touch-target bug fixes** on frontend `develop`. 3 commits:
  - `1e4c549` — **Swap button re-center** after F2 44px bump. `ProductSearchForm2.js:249` `left: -17px` → `-23px` (re-center 46px wrapping div on From/To boundary).
  - `fbdca15` — **Swap/currency/profile 44→40 revert** (user feedback: 44 too big for dense UI). 4 files: `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js`, `e2e/a11y/touch-targets.spec.ts` (3 test thresholds). Swap wrapper `left: -23px` → `-21px` to match 4px shrink.
  - `e782c41` — **Mobile drawer English/currency center** fix. `components/layout/layout.js:204-206` 3 className edits: parent `items-start` → `items-center`, both cells `text-center` → `flex justify-center items-center`, English cell `py-2` for 40px pill visual parity.
- **1 atom extracted** to `03-knowledge/` — `icon-button-size-decision` (40px default for icon buttons in dense UI, 44px reserved for primary CTAs).

**Resume point (EXACT):**
1. **F3 — WhatsApp 20×20 → 44×44 wrapper** (Sprint 1 P0 last item, NOT yet touched). 4 files: `components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`. ~1 hr, low risk. Commit: `fix(audit-F3): WhatsApp 44×44 wrapper batch (WCAG 2.5.5)`. **Note:** new atom says 40px is preferred for icon buttons in dense UI — apply 40px to F3 (WhatsApp) for visual consistency with swap/currency.
2. **Sprint 2 P1** (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. **Verify FE-22 API shape** — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response: `slug` or `booking_item_slug`? Fix `[...slug].js:71-72` accordingly.
4. **Build production Docker** with `libheif-dev` (backend HEIC dependency).
5. **WA-5** — Footer secondary nav + SearchDialogTrigger mobile button touch targets (deferred from F2; separate mini-batch).

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **WA-1** | **Website audit Sprint 1 (F1-F3)** | F1 + F2 DONE (`40c01e2` + `0f9df12`). F2-followups DONE (`1e4c549` + `fbdca15` + `e782c41` — 40px preferred for icon buttons in dense UI). F3 (WhatsApp wrapper) OPEN. ~1 hr. Apply 40px to F3 for visual consistency. | `components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js` |
| **WA-2** | **Website audit Sprint 2 (F4-F8)** | P1 batch. Inter font self-host, carousel scroll-snap, nav dedupe, OG image, search form overflow. ~7 hrs. | `_document.js`, `*Carousel.js`, `navConfig.js`, `og-image.webp` |
| **WA-3** | **Website audit Sprint 3 (F9-F11)** | P2 batch. Inline style extraction, brand name, FAQPage. ~6 hrs. | `ProfileMenu.js`, `helpers/constants.js`, `homepagev2.js:493-495` |
| **WA-4** | **ProfileMenu UX consolidation** | DONE (`44e209d` + `40b0a36` + `f4d581f` + `314020c`). Overflow guard + 3 expandable groups. −240px default height. | `ProfileButton.js`, `ProfileMenu.js` |
| **WA-6** | **F2 refinements — 40px icon button standard** | DONE (`1e4c549` + `fbdca15` + `e782c41`). User feedback after F2 44px: too big for dense UI. Reverted swap/currency/profile to 40px (Material Design medium). Token `TOUCH_TARGET.minHeight` still 44 — defer update. Atom: [[icon-button-size-decision]]. | `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js` |
| **WA-5** | **Footer secondary nav + SearchDialogTrigger touch targets** | OPEN. Sub-44px items flagged in F2 commit body. Separate mini-batch. | footer, `SearchDialogTrigger.js:33-43` |
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
