# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-06 (session #58)

**Achieved this session (#58):**
- **Sprint 1 P0 — F1 + F2 SHIPPED** (website audit). 4 commits on frontend `develop`:
  - `40c01e2` **F1** — Search input font 14→16px (iOS zoom fix). 6 inputs across `ProductSearchForm2.js` + `SearchDialogTrigger.js`.
  - `0f9df12` **F2** — 44×44px touch targets (WCAG 2.5.5). 5 component files: `CurrencySelector.js`, `ProfileImage.js`, `CartButton.js`, `ProductSearchForm2.js` (3 buttons), `CarouselArrowButtons.js`. New regression spec `e2e/a11y/touch-targets.spec.ts` (8 assertions × 4 viewport projects).
- **ProfileMenu UX consolidation** (3 commits):
  - `44e209d` — Post-F2 regression fix: desktop `<Menu>` Paper had no `maxHeight`/`overflowY`; F2's `ProfileImage` 36→44 height pushed the anchored menu 8px past viewport edge. Added `MenuListProps` + `PaperProps` with `maxHeight: calc(100vh - 120px)`, `overflowY: auto`.
  - `40b0a36` — Combine Ask Away + Explore More into expandable `<ExpandableMenuRow>` parent + 2 `<SubMenuRow>` children (both → `/forum`).
  - `f4d581f` — Group Edit Profile + Family & Friends + Change Password into "Account" expandable. Newly surfaces `/account/editPassword` route.
  - `314020c` — Group My Bookings + My Orders + Rate & Reviews into "My Activity" expandable.
  - **Cumulative menu height savings: −240px** (default collapsed). Desktop menu now fits fully on 1280×720 with all 3 expandables open.
- **3 atoms extracted to `03-knowledge/`** — `mui-menu-paper-overflow-guard`, `expandable-menu-row-mui-collapse`, `wcag-touch-target-enforcement`.

**Resume point (EXACT):**
1. **F3 — WhatsApp 20×20 → 44×44 wrapper** (Sprint 1 P0 last item). 4 files: `components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`. ~1 hr, low risk. Reuse `min-h-[44px] min-w-[44px]` pattern + extend `e2e/a11y/touch-targets.spec.ts`. Commit: `fix(audit-F3): WhatsApp 44×44 wrapper batch (WCAG 2.5.5)`.
2. **Sprint 2 P1** (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. **Verify FE-22 API shape** — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response: `slug` or `booking_item_slug`? Fix `[...slug].js:71-72` accordingly.
4. **Build production Docker** with `libheif-dev` (backend HEIC dependency).
5. **WA-5** (new) — Footer secondary nav + SearchDialogTrigger mobile button touch targets (deferred from F2; separate mini-batch).

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **WA-1** | **Website audit Sprint 1 (F1-F3)** | F1 + F2 DONE (`40c01e2` + `0f9df12`). F3 (WhatsApp wrapper) OPEN. ~1 hr. | `components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js` |
| **WA-2** | **Website audit Sprint 2 (F4-F8)** | P1 batch. Inter font self-host, carousel scroll-snap, nav dedupe, OG image, search form overflow. ~7 hrs. | `_document.js`, `*Carousel.js`, `navConfig.js`, `og-image.webp` |
| **WA-3** | **Website audit Sprint 3 (F9-F11)** | P2 batch. Inline style extraction, brand name, FAQPage. ~6 hrs. | `ProfileMenu.js`, `helpers/constants.js`, `homepagev2.js:493-495` |
| **WA-4** | **ProfileMenu UX consolidation** | DONE (`44e209d` + `40b0a36` + `f4d581f` + `314020c`). Overflow guard + 3 expandable groups. −240px default height. | `ProfileButton.js`, `ProfileMenu.js` |
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
