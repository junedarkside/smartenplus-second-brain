# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-07 (session #62)

**Achieved this session (#62):**
- **WA-2 F4 — Inter font self-host SHIPPED** — 1 commit on frontend `develop` (branch `260607-fix/wa2-f4-inter-font-self-host`):
  - `1d2d749` — **Migrate Inter from Google Fonts CDN to `next/font/google`**. Eliminates third-party request (perf + GDPR), auto-inlines `@font-face` at build, no FOUT. 4 files: `lib/fonts.js` (new — Inter weights 400/500/600/700, var `--font-inter`), `pages/_document.js` (remove 3 CDN lines), `pages/_app.js` (wrap `<Component>` with `${inter.variable} font-sans`), `tailwind.config.js` (`sans: ['var(--font-inter)', ...]`). **Build verified:** `next-font-manifest.json` shows `/_app` preloaded woff2 `e4af272ccee01ff0-s.p.woff2`; 7 woff2 files in `.next/static/media/`; 0 hits for `fonts.googleapis` / `fonts.gstatic` in source. **No component impact:** wrapper div has no styling, MUI inherits from body (unchanged), Thai fonts (`Sarabun`/`Kanit`) untouched. **Lesson:** `next/font` must be imported from `_app.js`, not `_document.js` — first attempt put className on body, build's font manifest stayed empty. Reverted to `_app.js` wrap.
- **WA-2 F5 — Carousel `align: 'start'` CLOSED (static evidence)** — investigated unmerged remotes `260521-feat/popular-routes-image-carousel` (HEAD `edccb75`) + `260602-feat/related-experiences-carousel` (HEAD `b166ad2a`); both are **ancestors of develop** — `git log origin/<branch> ^develop` returns empty. Fix already shipped via shared `CardCarouselContainer.js:17-21` (`align: 'start'` + `containScroll: 'trimSnaps'` + `loop`), consumed by `PopularRoutesCarousel` + `DestinationsCarousel` (both `lib/homepage/components/`). Plus CSS `snap-start` on each slide (line 47) + a11y attrs (`role="region"`, `aria-roledescription="carousel"`, `aria-label`). Manual iPhone SE test on `localhost:3001` blocked by backend down (carousels render empty), but config is provably correct via static. **Net code: 0 lines.** ~2 hr audit estimate was 0 because shared wrapper exists.
- **WA-2 F8 — Search form overflow SHIPPED** — 1 commit on frontend `develop` (branch `260607-fix/wa2-f8-search-form-overflow`):
  - `d1fcf47` — **`flex-wrap` + `min-w-0` on `ProductSearchForm2.js` row (MH3, High)**. 1 file, 8 insertions, 8 deletions. Root row div (line 227): added `flex-wrap` to allow intermediate 375-767px viewport wrap. All 5 input children + Date/Return wrapper (lines 228, 257, 268, 270, 291, 321, 332): added `min-w-0` to allow flex shrink below intrinsic content width. **No layout refactor** — mobile-stacked (`flex-col`) + desktop-row (`md:flex-row`) preserved. **Lint clean.** **Fast-forward merge to develop.** **WA-2 Sprint 2 CLOSED** — F4-F8 all shipped, 5/5.
- **Vault sync — divergence resolved.** Repo state ahead of vault on 2 items: RR-1/FE-22 (backend serializer returns both `slug` + `booking_item_slug`, commits `a4cb344`/`7a74394`/`f82b182`/`3d1d91a`) + Docker `libheif-dev` (`f82b182`, `Dockerfile:17`). Both unblock downstream work — RR-1 Sprint 1 (P1-3→P1-9) now unblocked, Docker only needs prod build gate.

**Resume point (EXACT):**
1. **WA-3 Sprint 3 (F9-F11)** — P2 batch. Inline style extraction, brand name, FAQPage. ~6 hrs.
2. **WA-5** — Footer secondary nav + `SearchDialogTrigger.js:33-43` touch targets. ~2 hrs.
3. **RR-1 Sprint 1** — P1-3→P1-9 (FE-22 unblocked). ~3-4 hrs.
4. **GYG-IMPL** — merge `260605-feat/review-images` (P1 thumbnails).
5. **TSTD-1 test infra** — BLOCKS RELEASE. 6 CRITICAL gaps. Schedule 4-5 day block.

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **WA-1** | **Website audit Sprint 1 (F1-F3)** | **CLOSED** (2026-06-06 #60). F1 (`40c01e2`) + F2 (`0f9df12`) + F2-followups (`1e4c549` + `fbdca15` + `e782c41`) + F3 (`9472df5`) all shipped. Atom: [[icon-button-size-decision]]. | `components/UI/ShareButton.js`, `components/layout/footer.js`, `components/search/Passenger.js`, `components/pages-info/ContactUs.js` |
| **WA-2** | **Website audit Sprint 2 (F4-F8)** | **CLOSED** (`d1fcf47` #62). F4 + F5 + F6 + F7 + F8 all shipped. | `ProductSearchForm2.js` |
| **WA-3** | **Website audit Sprint 3 (F9-F11)** | P2 batch. Inline style extraction, brand name, FAQPage. ~6 hrs. | `ProfileMenu.js`, `helpers/constants.js`, `homepagev2.js:493-495` |
| **WA-4** | **ProfileMenu UX consolidation** | DONE (`44e209d` + `40b0a36` + `f4d581f` + `314020c`). Overflow guard + 3 expandable groups. −240px default height. | `ProfileButton.js`, `ProfileMenu.js` |
| **WA-6** | **F2 refinements — 40px icon button standard** | DONE (`1e4c549` + `fbdca15` + `e782c41`). User feedback after F2 44px: too big for dense UI. Reverted swap/currency/profile to 40px (Material Design medium). Token `TOUCH_TARGET.minHeight` still 44 — defer update. Atom: [[icon-button-size-decision]]. | `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js` |
| **WA-5** | **Footer secondary nav + SearchDialogTrigger touch targets** | OPEN. Sub-44px items flagged in F2 commit body. Separate mini-batch. | footer, `SearchDialogTrigger.js:33-43` |
| RR-1 | Rate-review Release 1 shipped | P0+P1-1+P1-2 + FE-22 RESOLVED 2026-06-07 (serializer verified — both `slug` + `booking_item_slug` present, commits `a4cb344`/`7a74394`/`f82b182`/`3d1d91a`). Sprint 1 (P1-3→P1-9) unblocked. | `[reviewSlug].js`, `BookingReviewList.js`, `RateAndReviewForm.js`, `ReviewList.js` |
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
