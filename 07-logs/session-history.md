# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #71 (2026-06-07) — Visual check session (no code)
- Verified WA-5 fixes render correctly via dev server (localhost:3000).
- All 15 file changes from `781bf7a` intact.
- No new commits. Checkpoint tag `pre-wa5-audit-2026-06-07` still available.

**Resume point:** RR-1 → GYG-IMPL → TSTD-1

## Session #70 (2026-06-07) — WA-5 EXPANDED (comprehensive touch-target audit)
- **Scrutinize #69** found F2 was partial; recommended comprehensive audit
- **WA-5** `781bf7a` — Floor 15+ clickables at 40px (WCAG 2.5.5). 15 files, 52+/30-.
- SearchDialogTrigger (3 variants): mobile 26→40, desktop 32→40, input h-10→h-11
- Footer nav: 9 links → `inline-flex items-center min-h-40`
- 10 IconButton `size=small` → `size=medium`
- 8 single-file fixes (SingleComment, SearchBar, SearchResultsList, PaymentComponent, ReactionTrigger, Coupon, LocationTree)
- e2e test +2 assertions (search trigger mobile, footer privacy)
- Checkpoint tag `pre-wa5-audit-2026-06-07` for rollback
- Lint clean (5 pre-existing warnings unrelated)
- **Deferred:** 5 text-xs onClick spans (TripItem, tripItemv2, TripItemFooter, TripDetailsAttribute, TripDetailInfo) + TripDetailBooking/TripDetail3 role=button — visually risky, need product decision

**Resume point:** RR-1 → GYG-IMPL → TSTD-1

## Session #68 (2026-06-07) — WA-3 F11 SHIPPED (spec mismatch corrected)
- **F11** `d9d1425` — Add visible FAQ section to homepage. 1 file, 18+. `pages/homepagev2.js` insert `<Section id="faq-section">` between TravelThailandBetterSection and LocationsSection. 5 native `<details>/<summary>` from existing `faqsData`. No JS state, no new component. Lint clean. Fast-forward to develop.
- **Spec mismatch noted.** F11 spec said "Add FAQPage schema"; reality: `FAQPageJsonLd` already wired at line 240 (pre-existing). Pre-check: `helpSubcategories` is subcategory metadata, not Q&A. Real Q&A source = `faqsPosts` (line 454, pre-existing). New work = visible content only.
- **WA-3 Sprint 3 CLOSED.** F9 + F10 + F10-followup + F11 all shipped.

**Resume point:** WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #67 (2026-06-07) — WA-3 F9 SHIPPED (spec mismatch corrected)
- **F9** `0b30580` — Add `ELEVATION_TOKENS` (`none/sm/md/lg/xl`) to `helpers/designSystem.js`. Extract 2 real boxShadows: `ProfileButton.js:20` → `ELEVATION_TOKENS.lg`; `NavDropdown.js:72` → `ELEVATION_TOKENS.md`. 3 files, 15+/2-. Lint clean. Fast-forward to develop.
- **Spec mismatch noted.** F9 spec listed 5 files for extraction; audit found only 2 boxShadows in entire codebase, in 2 different files. Spec-listed files have only dynamic/ternary styles that correctly stay inline per F9 rule. User accepted "extract the 2 real ones" — no fabrication.

**Resume point:** WA-3 F11 → WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #66 (2026-06-07) — WA-3 F10-followup Part 3 SHIPPED
- **F10 Part 3** `324d449` — Replace 5 hardcoded `'SmartEnPlus'` NextSeo `siteName` sites with `siteName` import from `helpers/constants.js`. 5 files, 10+/5-: `components/FrontPage/Seo.js`, `pages/privacy/index.js`, `pages/ref/index.js`, `pages/ref/[type].js`, `pages/blog/index.js`. Fast-forward to develop. Lint clean.
- **F10 + F10-followup fully CLOSED.** No more hardcoded brand name in OG siteName. No `BRAND_NAME`. No typo refs. `siteName` = single source of truth.

**Resume point:** WA-3 F9 → F11 → WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #65 (2026-06-07) — WA-3 F10-followup closed (clean state)
- **F10 revert** `cf71511` — Drop `BRAND_NAME`, keep `siteName` (user callout: duplication). 5 files, 9+/14-: `helpers/constants.js` (-1 export), `pages/_app.js` (-1 import + 4 sites), 3 structured data files (-1 import + 5 sites). Fast-forward to develop.
- **F10 typo imports fix** `a2c6d27` — Update 9 imports + 1 URL to renamed `smartenplus-transportation-booking-online.webp`. 10 files, 10+/10-. F10 (#64) renamed file but only updated 1 import; build was broken at 9 import sites. Fast-forward to develop.
- **F10 closed cleanly.** No `BRAND_NAME` in code. No `smartenpus-` typo refs. `siteName` = single source of truth (9 use sites). Typo file rename fully consistent.
- Lint clean both branches.

**Resume point:** WA-3 F10-followup Part 3 (5 hardcoded 'SmartEnPlus' sites in pages/ → siteName import) → WA-3 F9 → WA-3 F11 → WA-5 → TSTD-1

## Session #64 (2026-06-07) — WA-3 F10 closed (spec scope)
- **WA-3 F10** `e3194dc` — Brand name consistency: `BRAND_NAME = 'SmartEnPlus'` constant added to `helpers/constants.js`, 8 hardcoded sites replaced in 4 files (DefaultSeo + 3 structured data components), 1 typo file renamed
- 7 files changed, +15/-10, fast-forward merge to develop
- **Spec under-scoped:** audit found 39 total `'SmartEnPlus'` occurrences; spec listed 9. Shipped spec-faithful 8 sites; 30+ deferred to **F10-followup**
- Lint clean

**Resume point:** WA-3 F10-followup → F9 → F11 → WA-5 → TSTD-1

## Session #63 (2026-06-07) — WA-7 closed
- **WA-7** `f1cbb5d` — Mobile input height parity: `min-h-[44px]` added to From/To labels (lines 228, 257) in `ProductSearchForm2.js` to match Date/Return/Passenger cell pattern
- 1 file, +2/-2, fast-forward merge to develop
- Grill review: passed — no High/Medium issues, F8's `min-w-0` and WA-7's `min-h-[44px]` are independent CSS axes
- All 5 input cells now have `min-h-[44px]` (Date/Return/Passenger + From/To)

**Resume point:** WA-3 → WA-5 → RR-1 Sprint 1 → GYG-IMPL → TSTD-1

## Session #62 (2026-06-07) — WA-2 Sprint 2 CLOSED (F4-F8)
- **F4** `1d2d749` — Inter font self-host via `next/font/google` (no FOUT, GDPR clean)
- **F5** (static) — Carousel `align: 'start'` already in `CardCarouselContainer.js:17-21`; 2 unmerged remotes are ancestors of develop
- **F6** `041f51a` — Nav dedupe: `/locations` label "Routes" → "Locations" in `navConfig.js`
- **F7** `7895695` — OG image 1200×630 WebP (new asset + 4-line `pages/_app.js` edit)
- **F8** `d1fcf47` — `flex-wrap` + `min-w-0` on `ProductSearchForm2.js` row (MH3, High)
- All 5 branches fast-forwarded to develop, pushed
- Code review (grill) on F8 found false positive: desktop 2-line wrap is design intent (search button CTA below 5 inputs)
- WA-7 noted: mobile input height inconsistency between From/To (no min-h) and Date/Return/Passenger (min-h-[44px])

**Resume point:** WA-3 → WA-7 → WA-5 → RR-1 Sprint 1 → GYG-IMPL → TSTD-1

## Session #60 (2026-06-06)
- **F3 — Social icon 40×40 wrapper batch** (Sprint 1 P0 closeout). 1 commit on frontend `develop`:
  - `9472df5` — Wrap isolated social icons in `inline-flex items-center justify-center min-w-[40px] min-h-[40px]` per `icon-button-size-decision` atom. 4 files: `components/UI/ShareButton.js` (WhatsApp `<span>`), `components/layout/footer.js` (4 social `<Link>`s), `components/search/Passenger.js` (3 social `<Link>`s), `components/pages-info/ContactUs.js` (4 social `<Link>`s). Added missing `aria-label`s. **Row-wide consistency rule applied:** when WhatsApp wrapped, all sibling icons in the same row wrapped too (same a11y gap, visual consistency).
- **WA-1 Sprint 1 P0 CLOSED.** F1 (search 16px) + F2 (44→40px dense UI) + F3 (40px wrapper) all shipped.

**Resume point:**
1. WA-2 Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
2. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets. ~2 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. TSTD-1 test infra — BLOCKS RELEASE. 6 CRITICAL gaps. Schedule 4-5 day block.

---

## Session #59 (2026-06-06)
- **3 touch-target bug fixes** on frontend `develop`. 3 commits:
  - `1e4c549` — **Swap button re-center** after F2 44px bump. `ProductSearchForm2.js:249` `left: -17px` → `-23px` (re-center 46px wrapping div on From/To boundary).
  - `fbdca15` — **Swap/currency/profile 44→40 revert** (user feedback: 44 too big for dense UI). 4 files: `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js`, `e2e/a11y/touch-targets.spec.ts` (3 test thresholds). Swap wrapper `left: -23px` → `-21px` to match 4px shrink.
  - `e782c41` — **Mobile drawer English/currency center** fix. `components/layout/layout.js:204-206` 3 className edits: parent `items-start` → `items-center`, both cells `text-center` → `flex justify-center items-center`, English cell `py-2` for 40px pill visual parity.
- **1 atom extracted** to `03-knowledge/` — `icon-button-size-decision` (40px default for icon buttons in dense UI, 44px reserved for primary CTAs).

**Resume point:**
1. F3 — WhatsApp 20×20 → 44×44 wrapper (`components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`) ~1 hr.
2. Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets.

---

## Session #58 (2026-06-06)
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

**Resume point:**
1. F3 — WhatsApp 20×20 → 44×44 wrapper (`components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`) ~1 hr.
2. Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets.

---

## Session #54 (2026-06-06)
- **HEIC-1 CLOSED** — Client-side HEIC preview fixed. `heic2any` added (`^0.0.4`). `RateAndReviewForm.js` `onChange` async-converts HEIC/HEIF → JPEG via dynamic import. Committed `6c10137` on `develop`.

**Resume point:** Verify FE-22 API shape → Sprint 1 (P1-3→P1-9) → Docker libheif-dev build.

---

## Session #52 (2026-06-06)
- **Rate-review UX/UI audit COMPLETE** — 6-agent team (r1-ux, r1-visual, r1-frontend, r2-skeptic, r3-leader-synthesis, r4-scrutinize). 52 raw findings → 34 unique. 3 P0 confirmed.
- **Scrutiny pass** — 4 corrections applied to r3. r5-implementation-plan written.
- **Release 1 SHIPPED** — 5 fixes: XSS DOMPurify, parseISO null guard, star ARIA radiogroup, router import + leading slashes, email masking. Branch: `260606-fix/heic-review-upload`.

**Resume point:**
1. Verify FE-22 API shape — check backend ReviewSerializer POST response (`slug` vs `booking_item_slug`).
2. Lint + test Release 1. Merge `260606-fix/heic-review-upload` → develop.

---

## Session #51 (2026-06-06)
- **HEIC review upload — IMPLEMENTATED, local deps ready** — pillow-heif 0.15.0 + libheif 1.23.0 installed locally. Backend restarted with HEIC opener registered. Code committed: backend `f82b182`, frontend `0a4e6d4`. Branch: `260606-fix/heic-review-upload`.
- **Multi-agent debate** — 2 agents evaluated base64 proxy vs pillow-heif. Chose server-side (5 lines, 33% less payload, no memory spike).
- **Test deferred** — User to test HEIC upload later, then merge to production.

**Resume point:**
1. **Test HEIC upload locally** — Upload HEIC file via review form, verify WebP conversion ≤120KB.
2. **Merge `260606-fix/heic-review-upload`** → main (backend) + develop (frontend).
3. **Build production Docker** with libheif-dev.

---

## Session #50 (2026-06-05)
- **DOMAIN-1 closed** — deploy + cache clear confirmed. `NEXT_PUBLIC_DOMAIN` propagated.
- **GYG-THUMB Review Images — DONE (unmerged)** — Full image support across 2 repos: ReviewImage model + WebP ≤120KB conversion + lightbox thumbnails + file upload form + profile menu + review detail page + CSR refetch. 7 bugs found+fixed. Backend `3d1d91a`, frontend `e73fc23`, both pushed.
- **Vault optimized** — extracted dead weight to `vault-protocol.md`, `vault-guardrails.md`, `session-history.md`, `closed-items.md`. 78% reduction in master-state.md size. Report: [[vault-wrapup-optimization-report]].

**Resume point:**
1. Merge `260605-feat/review-images` → develop (frontend) + main (backend). Run migration on production.
2. GYG-THUMB follow-up: Review edit mode (RateAndReviewForm dual-mode). Backend `partial_update`.

---

## Session #49 (2026-06-05)
- **Activities /activities default category — FIXED + SHIPPED** — `hooks/useDayTripFilters.js` `DEFAULT_FILTERS.category`: DAY_TOUR → null. `filtersFromQuery` `|| null` fallback. Commit `3a4db81` → frontend develop → pushed.
- **Activities pagination reset bug — ROOT CAUSE FOUND + FIXED + SHIPPED** — StrictMode + didMountRef. No-op guard in `useDayTripFilters.js:67-75`. `scroll: false` on `router.push`. Commit `01b3708` → frontend develop → pushed.
- 3 atoms: [[react-strictmode-useref-persistence]], [[react-state-no-op-guard-side-effect-prevention]], [[nextjs-shallow-router-push-scroll-false]]

## Session #48 (2026-06-05)
- **GSC-1 Phase 1 + Phase 2 — SHIPPED** — `seoConfig.js:41` noindex fix + station-sitemap removal. Branch `effdc49` → develop `0eaf9b2`.
- **NEXT_PUBLIC_DOMAIN leading-space bug — FOUND + USER FIXED**
- Multi-agent review: SEO + frontend + /scrutinize + /debug-mantra.

## Session #47 (2026-06-05)
- **GSC 52,400 "Crawled Not Indexed" — RESEARCH COMPLETE, NO CODE** — 3-team review. Primary cause: empty ISR trip pages. Three-tier plan designed.

## Session #46 (2026-06-04)
- **Blog canonical URL bug — FIXED + SHIPPED** — WP subdomain rewrite fix. Commits `3d30407` + `b0fce4f` → develop.

## Session #45 (2026-06-04)
- **Homepage terminology audit — DONE** — Nav labels fixed. Branch `36e2786` → develop `aef5548`.
- **Production SEO phase 2 — DONE** — /locations + /destinations confirmed different products.
- 3 atoms extracted.

## Session #44 (2026-06-04)
- **GYG P1 not-suitable badges — DONE** — `IncludedExcluded.js` + `DayTripDetailPage.js`. Branch `3f12f52` → develop.
- **GYG P2 review filter — DONE** — `ReviewListByProduct.js` filter chips. Branch `d5d7482` → develop.

## Session #43 (2026-06-03)
- **CMA-1 HOTEL_PICKUP invariant — DONE** — `ContractDetailSerializer.validate()`. Commit `3a59a41` → backend main.
- **Admin-dashboard HOTEL_PICKUP validation — DONE** — Yup schema. Commits `c2e8e4e` + `5f068ef` → admin main.

## Session #42 (2026-06-03)
- **CMA-1 casing ADR — DONE** — 6 inline comments. Frontend `375e501` → develop.
- **CMA-2 meeting_point_details — FIXED** — 2 lines in `AdminBookingSummarySerializer`. Commit `09d6f3a` → backend main.

## Session #41 (2026-06-03)
- **CMA-1 partial — 2 of 6 shipped** — `showStations` deleted `ff8006e`. Admin PATCH guard `22dc045`.

## Session #40 (2026-06-03)
- **Timeline stop deletion bug — FIXED + SHIPPED** — 5 changes across 3 repos. Migration 0028.

## Session #39 (2026-06-03)
- **Contract model ambiguity audit** — 4-round debate. 6 overlaps confirmed. Vault: [[contract-model-ambiguity-audit-2026-06-03]]
- **Contract location help text fix (P0)** — admin form 4 strings. Commit `fa2f16a` → main.

## Session #38 (2026-06-03)
- **booking-summary 500 fix** — trip=None guard. Commit `4bec691` → backend main.
- **Frontend test infrastructure audit** — 54% pass rate, 6 CRITICAL. Vault: [[frontend-test-infrastructure-audit-2026-06-03]]
