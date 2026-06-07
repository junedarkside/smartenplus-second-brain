# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-07 (session #79)

**Achieved this session (#79):**
- **RR-1 Submit-Review UX gap SHIPPED** — 1 commit on frontend `develop` (`de964e3`, 1 file 10+/0-). Branch `260607-fix/rate-review-submit-as-alert` created + FF-merged to develop.
- **"Submitting as X" Alert** added to `RateAndReviewForm.js` (line 110-117):
  - Authed: blue MUI Alert `Submitting as {email}`
  - Guest: blue MUI Alert `Submitting as guest. Your review will be associated with the email on your booking.`
- Reuses `Alert` (already imported at line 11) + `session` (already destructured at line 29). No new dependencies. No backend change.
- **Auth model confirmed intentional** via deep-read of `dialogue/views.py:1037-1040` (`AllowAny` on non-list actions) + `views.py:1180-1195` (user + guest_email derivation). Finding doc: `00-inbox/finding-submit-review-auth-2026-06-07.md`
- Lint clean. One file touched. Zero effect on other components.
- **RR-1 arc fully closed** (Tier 1+2 + Tier 3 + auth UX gap + P1-7 spec correction).

**Resume point (EXACT):**
1. **TSTD-1** — test infrastructure, release blocker (4-5 dev days)
2. **F11-FOLLOWUP build** — `/help/faqs` page implementation (waits for spec approval + 3 open question answers)

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md` + `01-projects/help-faqs-landing-2026-06-07/audit.md`

**Achieved this session (#78):**
- **RR Review Detail Tier 3 SHIPPED** — 1 commit on frontend `develop` (`6c09c7d`, 1 file 34+/8-). Branch `260607-fix/rr-detail-tier3-polish` created + FF-merged to develop.
- **4 polish fixes** on `pages/rate-review/[reviewSlug].js`:
  - **M6** sticky breakpoint `lg` → `md` (matches `STICKY_CONFIG` token at `helpers/designSystem.js:137`)
  - **M7** loading state: `h-screen` spinner → `FeaturedImageHeaderSkeleton` + breadcrumb + 2-col grid skeleton (no CLS)
  - **M8** hero h1: `text-2xl md:text-4xl lg:text-5xl` → `text-2xl sm:text-3xl md:text-4xl` (matches `TYPOGRAPHY_SCALE.h1` at `helpers/designSystem.js:67`, caps at 36px)
  - **N3** `useMemo(normalizeReviewForSummary, [review])` — was running 2×/render, now 1×
- Removed unused `CircularProgress` import (no longer used after M7)
- **M3 (`useReviewBySlug` hook) deferred** — re-checked: 2 pages fetch different endpoints (`/dialogue/reviews/{slug}/` vs `/dialogue/reviews/token/{token}/`) with different auth models (public vs token-gated). Forced abstraction adds more surface than it removes. Revisit if 3rd caller appears.
- Lint clean. One file touched. Zero effect on other components.

**Resume point (EXACT):**
1. **TSTD-1** — test infrastructure, release blocker
2. **F11-FOLLOWUP** — `/help/faqs` landing page (25-30 Q&As) — needs new audit doc
3. **RR-1 audit-missed follow-ups** — submit-review auth model confirm w/ backend, P1-7 spec update

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

**Achieved this session (#77):**
- **RR Review Detail Tier 1+2 SHIPPED** — 1 commit on frontend `develop` (`cc3a0dc`, 1 file 37+/150-). Branch `260607-fix/review-detail-blockers-tier1` created + FF-merged to develop.
- **2-agent parallel audit** of `/rate-review/[reviewSlug].js` (UX + Technical). Found 4 blockers + 10 major + 8 minor.
- **Blockers fixed:** B1 XSS (safe DOMPurify SSR fallback), B2 race (AbortController + state reset), B3 ProfileImage prop (email not first_name), B4 StickySidebar (added `min-h-[calc(100vh-6rem)]` on grid parent).
- **Major fixed:** M1 DOMPurify memoized in useMemo, M2 specific 404/500/network error messages, M10 back button 36→44px (WCAG 2.2).
- **Minor fixed:** N1 removed unused TYPOGRAPHY_SCALE import, N2 deleted ~150 lines of dead commented code.
- Lint clean. One file touched. No new components. Zero effect on other components.
- Plan doc: `/Users/charuwatnaranong/.claude/plans/check-vault-ot-resume-validated-wigderson.md`

**Resume point (EXACT):**
1. **TSTD-1** — test infrastructure, release blocker
2. **F11-FOLLOWUP** — `/help/faqs` landing page (25-30 Q&As) — needs new audit doc
3. **RR-1 audit-missed follow-ups** — submit-review auth model confirm w/ backend, P1-7 spec update

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

**Achieved this session (#76):**
- **RR padding aligned to blog** — 1 commit on frontend `develop` (`50eb626`, 3 files 13+/13-). Branch `260607-fix/rr-pages-match-blog-padding` created + FF-merged to develop.
- **2-agent parallel audit** compared /rate-review pages vs /blog canonical pattern: `px-2 md:px-3 xl:px-0` + `max-w-[1200px] mx-auto`
- **13 mismatches found and fixed** via className swaps:
  - `pages/rate-review/index.js`: hero action bar (`px-3` → `px-2 md:px-3 xl:px-0`), hero title, breadcrumb, content
  - `pages/rate-review/[reviewSlug].js`: error state (`px-4 md:px-6` → `px-2 md:px-3 xl:px-0`), hero action bar, hero title, breadcrumb, content grid
  - `pages/rate-review/submit-review/[...slug].js`: hero action bar, hero title, breadcrumb, content grid
- Lint clean. No new components, no new imports, no functional change. Pure visual alignment.
- Zero effect on other components.

**Achieved this session (#75):**
- **P1-4 refactor SHIPPED** — 1 commit on frontend `develop` (`95216ec`, 1 file 8+/3-). Branch `260607-refactor/rr1-p1-4-reuse-auth-hook` created + FF-merged to develop.
- **Refactor:** restored `useAuthRedirect` hook usage in `pages/rate-review/index.js` (consistent with 11+ other usages). Kept gate card UX via separate `showGate` state + 1.5s timer. Hook now handles redirect, page shows gate card.
- User feedback: "no tech debt, reusable components, no effect on other components". Original Sprint 1 P1-4 used inline `setTimeout` + `router.push` — created tech debt by removing standard hook pattern. Refactor fixes.
- Stale browser cache error (webpack factory undefined on /rate-review) was a non-issue — resolved in fresh browser. No code relation to refactor.
- Lint clean. Only `pages/rate-review/index.js` modified. Zero effect on other components.

**Achieved this session (#74):**
- **RR-1 Sprint 1 SHIPPED** — 1 commit on frontend `develop` (`8ac1029`, 7 files 85+/35-). Branch `260607-fix/rr1-sprint1-p1-3-9` (feature branch) — direct commit to develop (linear history preserved, same net result as FF-merge). Lint clean.
- **Grill skill audit** verified 5/7 claims, caught 2 spec ambiguities (P1-3 "guard" + P1-4 "interstitial" definitions), 5 audit-missed items (P1-7 understated coverage, submit-review auth model, dead code, brittle slug fallback, P1-4 definition).
- **P1-3** (`RateAndReviewForm.js`) — in-flight disable already wired (audit wrong), added success snackbar "Review submitted — thank you!" with severity="success" Alert
- **P1-4** (`pages/rate-review/index.js`) — replaced `useAuthRedirect` hard-redirect with inline "Sign in to view your reviews" gate card (LockOutlinedIcon + copy + CircularProgress, 1.5s grace), then redirect. **Refactored in #75** to use `useAuthRedirect` for redirect while keeping gate card UX.
- **P1-5** (`ReviewFirstPage.js` + `ReviewListByProduct.js`) — 6 instances of `text-gray-400` → `text-gray-500` (label uppercase, travel date, route, operator, review count)
- **P1-6** (`ReviewImageThumbnails.js`) — `<div onClick>` → `<button type="button">` with `aria-label` + `onKeyDown` (Enter/Space) + focus ring classes
- **P1-8** (`RateAndReviewForm.js`) — added "Add a title and your review to continue." helper text under disabled submit button, conditional on `!loading && (title.length === 0 || reviewText.length === 0)`
- **P1-9** (3 pages) — imported `getSiteUrl` from `utils/blog/seoHelper.js`, replaced 3 hardcoded canonicals with template literals
- Checkpoint tag `pre-rr1-sprint1-2026-06-07` for rollback
- Total time: ~2.5 hrs as estimated (optimistic scenario)

**Resume point (EXACT):**
1. **TSTD-1** — test infrastructure, release blocker
2. **F11-FOLLOWUP** — `/help/faqs` landing page (25-30 Q&As)
3. **Audit-missed follow-ups** — `submit-review/[...slug].js` no session guard (confirm with backend), P1-9 dead code cleanup at `[reviewSlug].js:43` (was deferred but kept in scope? — verify), P1-7 spec update (3 files not 2)

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

**Achieved this session (#72):**
- **F11 FAQ REWORK SHIPPED** — 1 commit on frontend `develop` (branch `260607-refactor/f11-remove-faq-add-trust-strip`):
  - `3534e21` — **Remove visible FAQ from homepage, add trust strip + footer Help link**. 3 files, 69+/31-.
  - **pages/homepagev2.js**: deleted visible FAQ Section (was 383-410), deleted FAQPageJsonLd (line 240), removed `faqsData` getStaticProps extraction (no remaining usage)
  - **lib/homepage/components/TrustStripSection.js**: NEW component. Row 1 = 6 payment logos (VISA, MC, JCB, PromptPay, Apple Pay, Google Pay — all existing assets). Row 2 = 4 trust signals (TAT Licensed, 24/7 Thai/English Support, Free Cancellation 24h, SSL Secure Payment). Uses CARD_CONFIG styling.
  - **components/layout/footer.js**: added "Help & FAQs" link in secondary nav → `/help/faqs`
  - **Lint clean**, fast-forward merge to develop
- **6-agent debate synthesis** (3 scrutinize + 3 stakeholder roleplay) confirmed: F11 placement = wrong funnel stage (PM), 280px is revenue slot not trust slot (BD), 1.86/5 design score (UX), JSON-LD silently invalid + FAQPage rich results deprecated by Google Aug 2023 (scrutinize).

**Achieved this session (#71):**
- Visual check via dev server (no code changes). All WA-5 fixes render correctly on localhost:3000.

**Resume point (EXACT):**
1. **RR-1 Sprint 1** — P1-3→P1-9, 3-4 hrs
2. **TSTD-1** — release blocker
3. **F11-FOLLOWUP** — `/help/faqs` landing page (25-30 Q&As)

Full plan: `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **WA-1** | **Website audit Sprint 1 (F1-F3)** | **CLOSED** (2026-06-06 #60). F1 (`40c01e2`) + F2 (`0f9df12`) + F2-followups (`1e4c549` + `fbdca15` + `e782c41`) + F3 (`9472df5`) all shipped. Atom: [[icon-button-size-decision]]. | `components/UI/ShareButton.js`, `components/layout/footer.js`, `components/search/Passenger.js`, `components/pages-info/ContactUs.js` |
| **WA-2** | **Website audit Sprint 2 (F4-F8)** | **CLOSED** (`d1fcf47` #62). F4 + F5 + F6 + F7 + F8 all shipped. | `ProductSearchForm2.js` |
| **WA-3** | **Website audit Sprint 3 (F9-F11)** | **CLOSED** (`0b30580` #67 + `d9d1425` #68). All 3 Sprint 3 features shipped. | `pages/homepagev2.js` |
| **WA-4** | **ProfileMenu UX consolidation** | DONE (`44e209d` + `40b0a36` + `f4d581f` + `314020c`). Overflow guard + 3 expandable groups. −240px default height. | `ProfileButton.js`, `ProfileMenu.js` |
| **WA-6** | **F2 refinements — 40px icon button standard** | DONE (`1e4c549` + `fbdca15` + `e782c41`). User feedback after F2 44px: too big for dense UI. Reverted swap/currency/profile to 40px (Material Design medium). Token `TOUCH_TARGET.minHeight` still 44 — defer update. Atom: [[icon-button-size-decision]]. | `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js` |
| **WA-5** | **Footer secondary nav + SearchDialogTrigger touch targets** | **CLOSED** (`781bf7a` #70). Expanded to 15+ clickables across 15 files. Checkpoint tag `pre-wa5-audit-2026-06-07` for rollback. 5 text-xs onClick spans + 2 role=button divs deferred (visually risky). | 15 files |
| **WA-7** | **ProductSearchForm2 mobile input height inconsistency** | **CLOSED** (`f1cbb5d` #63). From/To labels (lines 228, 257) now have `min-h-[44px]` matching Date/Return/Passenger cells. Grill review passed (no issues). | `components/search/ProductSearchForm2.js:228,257` |
| **F11** | **Homepage visible FAQ section** | **REWORKED** (`3534e21` #72). Removed visible FAQ + invalid JSON-LD from homepage. Replaced with trust strip (payment logos + trust signals) at same position. Added footer "Help & FAQs" link → /help/faqs. Reason: 1.86/5 design score, wrong funnel stage, FAQPage rich results deprecated Aug 2023, JSON-LD silently invalid (field shape mismatch). 6-agent synthesis (PM/BD/UX + 3 scrutinize). | `pages/homepagev2.js`, `lib/homepage/components/TrustStripSection.js` (NEW), `components/layout/footer.js` |
| **F11-FIX-1** | **Pre-existing `item.locationFields` undefined in /help/faqs** | **CLOSED** (`e6d1731` #72-followup). F11 footer link exposed latent bug: WordPress FAQ posts with unset `locationFields` threw `undefined.location` in useEffect. Added `?.` to 3 reads (lines 39, 45, 51). Posts without `locationFields` skip grouping, fall to `generalPosts` filter (line 74). | `pages/help/[...slug].js:39,45,51` |
| **TRUST-STRIP-1** | **Trust strip white card wrapper** | **CLOSED** (`9505117` #72-followup). 3-designer debate (minimalist+conversion=drop, design system=keep via HOMEPAGE_SECTION). HOMEPAGE_SECTION token defined but unused in codebase; neighbors are full-bleed. Dropped `bg-white rounded-md border border-gray-200 shadow-sm p-4 md:p-6`. Added `bg-gray-50 border-y border-gray-200` to Section. Visual: flat tinted section, no card chrome. | `lib/homepage/components/TrustStripSection.js` |
| F11-FOLLOWUP | `/help/faqs` landing page (25-30 Q&As) | DEFERRED. BD recommended. Current state: per-slug pages only. | `pages/help/[...slug].js` |
| F11-FOLLOWUP | B2B corporate CTA strip | DEFERRED. BD recommended. Awaits product decision on 280px slot. | TBD |
| F11-FOLLOWUP | Shared `<Accordion>` / `<FAQAccordion>` atom | DEFERRED. UX flagged. | `components/UI/` (new file) |
| RR-1 | Rate-review Release 1 shipped | P0+P1-1→P1-9 + FE-22 RESOLVED 2026-06-07. **Sprint 1 SHIPPED** (`8ac1029` #74) — P1-3,4,5,6,8,9. P1-7 already done. **Tier 1+2 SHIPPED** (`cc3a0dc` #77) — B1 XSS, B2 race, B3 ProfileImage, B4 Sticky, M1 DOMPurify memo, M2 specific errors, M10 back 44px, N1+N2 cleanup. **Tier 3 SHIPPED** (`6c09c7d` #78) — M6 sticky@md, M7 skeleton, M8 h1 cap, N3 useMemo normalize. **UX gap SHIPPED** (`de964e3` #79) — "Submitting as X" Alert in form. M3 hook extraction deferred — different endpoints/auth. Grill audit verified. Auth model confirmed intentional via `00-inbox/finding-submit-review-auth-2026-06-07.md`. | `RateAndReviewForm.js`, `pages/rate-review/index.js`, `ReviewFirstPage.js`, `ReviewListByProduct.js`, `ReviewImageThumbnails.js`, `pages/rate-review/[reviewSlug].js`, `pages/rate-review/submit-review/[...slug].js` |
| RR-1-FOLLOWUP | Submit-review no session guard | **CLOSED** (#79 — auth model confirmed intentional, finding doc `00-inbox/finding-submit-review-auth-2026-06-07.md`. UX gap "Submitting as X" shipped `de964e3`). | `pages/rate-review/submit-review/[...slug].js` |
| RR-1-FOLLOWUP | `submit-review/[...slug].js:77` brittle slug fallback | API returns `booking_item_slug` only. Confirm contract. Low priority. | `pages/rate-review/submit-review/[...slug].js:77` |
| RR-1-FOLLOWUP | `[reviewSlug].js:43` dead commented canonical | **CLOSED** (#77 N2 — 135-line dead block deleted in Tier 1+2, line 43 is now `dynamic()` import of `StandardBreadcrumb`). | `pages/rate-review/[reviewSlug].js:43` |
| **GYG-IMPL** | GYG 5-pattern | **CLOSED** (#73). All review image work already on develop via HEIC-1 (`6c10137`) + other paths. Cherry-pick of 3 review commits from stale `260605-feat/review-images` branch confirmed obsolete. `ReviewImageThumbnails` component, JSX, `BadgeChip` children pattern all verified present. | `pages/rate-review/[reviewSlug].js:161,479,414-416` |
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
