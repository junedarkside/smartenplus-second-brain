# Closed Items

Archived from master-state.md Section 2. Audit trail only.

## Closed — 2026-07-11 (session #236)

| Item | Closed | What shipped |
|------|--------|-------------|
| **COMMAND-CENTRE-BADGE** | session #236 | Pending-count pill on sidemenu "Command Centre" icon + "Direct Requests" tab label. Spec reviewed (2-agent), vault docs updated, 2 edits in admin-dashboard: `SideList.js` (badge key added to `badgeCounts`), `command-centre/index.js` (`<Badge>` wrapping tab label). Pill-clip fix (`pr:1.5, right:-6, top:6`). Merged `feat/command-centre-pending-badge` → develop `8653679`. Zero backend change. |

## Closed — 2026-07-07 (session #225)

| Item | Closed | What shipped |
|------|--------|-------------|
| **CHAT-SUPABASE-OFFLOAD** | session #225 | Full realtime unread badge system verified working. AD CS inbox: sidebar icon badge + conv row pill + tab title all update via Supabase payload (client-authoritative, no Django round-trip). Fixes across 8 branches: `fix/cs-unread-badge-realtime`, `fix/cs-sidebar-badge-realtime`, `fix/cs-unread-badge-markread`, `fix/cs-inbox-realtime-preview`, `fix/cs-unread-client-authoritative`, `fix/cs-auto-select-markread`. Admin-dashboard `develop` → `9316997`. |

## Closed — 2026-07-07 (session #223)

| Item | Closed | What shipped |
|------|--------|-------------|
| **CHAT-409-DIAGNOSIS** | session #223 | RC: `SupabaseTokenView` STAFF tier matched staff/superuser test account first and skipped `upsert_cs_conversation` — conversation row never mirrored to Supabase → FK 23503 on every send. H5 (PostgREST silent no-op) refuted; real customers never affected. Fix: staff tier gated behind `scope='staff'` body param (BE `5071926`), admin-dashboard hooks send it (`4a766af`), FE DEBUG-409 logs reverted (`91485ac6`). Verified live: `upsert_cs_conversation id=3 status=201`, row landed; customer + staff claims correct. Duplicate open conv 5 closed. Merged develop: BE `da88aed` · FE `dd1df3da` · admin `509927e`. Full trail: [[chat-409-diagnosis-handoff-2026-07-07]]. |

## Closed — 2026-07-03 (session #216)

| Item | Closed | What shipped |
|------|--------|-------------|
| **CS-CENTRALIZATION-DEPLOY** | session #216 | All manual tests done (#203). BE `6cb2328` · FE `5617b137` · admin `0e5727b`. Tests A1/A1b/A2/A3/B/C/D/F/A9 ALL PASS. Deployed develop→main all 3 repos. BE migrations `0005`–`0009` applied. |
| **OTA-FLOW-BUGS** | session #216 | 3 commits shipped to develop (`c96b1724` COLORS crash+image guard · `09e3f955` polling anti-pattern · `0657c6fb` TDZ crash). Included in prod deploy → main all 3 repos `2026-07-03`. |
| **OTA-RESEND-EMAIL** | session #216 | BE `OtaResendMagicLinkView` now calls `send_html_email()` + `magic_link_last_sent_at` tracking. Migration `0009`. Admin shows `trip_link` inline after send (`517a62c`). All deployed → main `2026-07-03`. |

## Closed — 2026-06-28 (session #184)

| Item | Closed | What shipped |
|------|--------|-------------|
| **SEO-R6-R9-DEPLOY** | session #184 (subsumed) | Originally USER-OWNED deploy handoff 2026-06-26 tracking SEO r6-r9 commits. Subsumed by **FULL-DEPLOY 2026-06-26** which shipped all 3 repos develop→main (FE `43299da` · BE `ebbb044` · admin `3d5a3a4`) including G8/P3a/P3b/CS chat Steps 5-7/CS-CHAT-PERF + r12 SEO. SEO commits r6 `87e3c15`, r7 `3fa482f`, r8 `961c645`, r9 `b5867c7`, faqpage-fix `bc538ef`, r7-coverage `1fafa5f` all included in full deploy. |

## Closed — 2026-06-25 (session #169)

| Item | Closed | What shipped |
|------|--------|-------------|
| **G8-OTA-CONSENT** | session #169 | PDPA consent gate on `/my-trip` before any trip data shown. Once per token (localStorage key `ota_consent_<first8>`). `OtaPdpaGate.js` (Thai PDPA compliant: controller, purpose, retention, rights, withdraw). `otaConsent.js` helper (SSR-safe). `consentChecked` flag prevents flash-of-gate on return visits. FE `feat/g8-ota-pdpa-gate` `d0d2069` — pending merge → develop. |
| **P3b-OTA-TICKETS** | session #168 | BE `OtaTripView` returns `tickets[]` array (all tickets newest-first). FE `/my-trip` renders all `OtaRequestCard`s stacked; form shown only when no tickets. RTK `invalidatesTags: ['OtaTrip']` on submit. Admin-dashboard ticket components OTA-guarded. BE `fix/ota-trip-tickets-list` `f8e1f4b` + FE `fix/my-trip-tickets-list` `d18941e` — merged to develop. |
| **G2-OTA-COPY-LINK** | session #167 | Admin-dashboard command-centre OTA Bookings tab + Copy Link button. BE `cs/views.py` OTA trip token endpoint. Admin `f7cc7ee` — merged to develop. |

## Closed — 2026-06-24 (session #159)

| Item | Closed | What shipped |
|------|--------|-------------|
| **P1e-REQUEST-STATUS** | session #159 | BE `ListModelMixin` + `booking_id` filter on `CustomerTicketViewSet` (`tickets/views.py`). FE `getCustomerRequests` RTK query + `ChangeRequestsSection.js` (white cards, human-language status labels, MUI icons, 60s poll). Header buttons labeled "Get Ticket"/"Request Change". Mobile responsive `flex-wrap` header. Merged FE develop `90392ba`, BE develop `6b10123`. |

## Closed — 2026-06-23 (deploy-blocking verified shipped)

| Item | Closed | What shipped |
|------|--------|-------------|
| **SEO-P0-DEPLOY** | #p0-seo-geo-2026-06-22 | P0 SEO fixes: sitemap poison, /help canonical, AI crawler unblock, robots.txt bot rules (GPTBot, ClaudeBot, Google-Extended, Perplexity, etc). FE main `6390887`. OAI-SearchBot gap = follow-up, not blocker. |
| **SEARCH-DIALOG-UI-TEST** | #138 | Unified search dialog tabs (Transportation + Experiences) in all 3 hosts (StickySearchBar/HeaderSearchSummary/SearchCover). Extracted `TabbedSearchPanel`. FE main `ceaa003`. |
| **REC-CHECKOUT-ZONES** | #133 | Checkout "Complete your trip" rec engine: ESSENTIAL/POPULAR/SIMILAR zones, hybrid fix, price/anchor fix, GTM `add_cart`, mobile cap, seed command. FE `0877d23` + BE `ae31f1f` both on main. Prod seed cleanup pending (low, BD). |
| **ISR-REVALIDATE-GAP** (deploy portion) | #129/#130 | On-demand ISR: FE `pages/api/revalidate.js` + BE `revalidate_frontend_isr` Celery task + `FRONTEND_URL` www fix. FE main `35c524d`, BE main `4eaaf8d`. Prod env var activation (REVALIDATION_SECRET + worker restart) = MONITOR item, not deploy-blocking. |
| **BE-HOMEPAGE-PRICE** (homepage portion) | #136 | `get_min_price` ADULT+fallback + `route_lowest_price_annotation` helper for experiences + airport routes. BE main `cff26b3`. REC-engine price bug (`services.py:74`, `serializers.py:~1105`, 6 finder annotations) still open. |

---

| # | Issue | Resolved |
|---|-------|----------|
| **REC-PRECOMPUTE-CACHEKEY** | precompute cache key 4-part vs runtime 5-part (`:none` suffix) → zero cache hits → prod CPU-credit drain on 1-vCPU EC2. Was mislabeled "low" #132; was actually the incident root cause. | **CLOSED #139** (2026-06-20). Fixed `7b6a9f8` (`:none` align + cache list not dict), `a59b9b8` (skip-if-fresh), `2c2c799` (every-6h, drop nightly), `bf633ac` (bound sync_pending_charges). Merged develop `e983c3e`, deployed, admin DatabaseScheduler updated. [[precompute-popular-contracts-fix-plan]] |
| **VAULT-DATE-RENAMES** (#125) | All 62 active dated filenames stripped of `-YYYY-MM-DD`; ~795 wikilinks rewritten via sed. 2 collision pairs resolved semantically (design-system-audit; content-marketing-strategy vs -review). 0 dated filenames outside `08-archive/`, 0 broken wikilinks. | **CLOSED #137** (2026-06-19). Vault commit `d235870`. [[vault-optimization-snapshot]] |
| **SOFT-DELETE-SHIP** | Push `feat/contract-soft-delete` (BE+admin) + verify | **CLOSED #123.** Pushed + merged `--no-ff` → develop both repos, branch pruned local+remote. BE develop `0e52782`, admin develop `f75d721`. Also fixed in-flight: global summary counts, `is_deleted` list-payload omission (badge/restore root fix), status-aware Restore, id-only deleted badge. [[adr-contract-soft-delete]] |
| WA-1 | Website audit Sprint 1 (F1-F3) | 2026-06-06 #60. F1 (`40c01e2`) + F2 (`0f9df12`) + F2-followups (`1e4c549` + `fbdca15` + `e782c41`) + F3 (`9472df5`) all shipped. Atom: [[icon-button-size-decision]]. |
| DOMAIN-1 | NEXT_PUBLIC_DOMAIN leading space | 2026-06-05. GitHub Secret + deploy confirmed. |
| TL-1 | Timeline stop deletion bug | 2026-06-04. Migration 0028. 3 atoms. |
| CMA-2 | ServiceDetail.js zero i18n fallback | #42. `09d6f3a`. |
| ACT-DEFAULT-CAT | /activities defaulted to DAY_TOUR | 2026-06-05 #49. `3a4db81`. |
| ACT-PAGINATION-RESET | Pagination chip jumped to page 1 | 2026-06-05 #49. `01b3708`. |
| ACT-7 | Phase 1 QA + merge | Done |
| ACT-8 | Backend merge | `2d5a6ee` → develop |
| ACT-9 | Phase 2 pre-flight (backend) | `508949b` |
| ACT-10 | Phase 2 QA + merge | `b552e55` → develop |
| ACT-11 | Phase 3 mobile layout | `f93df66` → develop |
| ACT-12 | Header search | `5eaf8e2` — ready to merge |
| BW-1 | Blog index hero px-4 padding | Already fixed |
| BW-2 | Blog index featured px-2 md:px-4 | Already fixed |
| BW-3 | BlogCard rounded-lg + no mx- | Already fixed |
| EXP-DETAIL-1 | Experience Detail Page redesign | #33 — shipped |
| HEIC-1 | iPhone HEIC review upload | 2026-06-06 #54. Client-side preview via heic2any. `6c10137`. |
| RR-REVIEW-DETAIL-T1+2 | Review detail page Tier 1+2 | 2026-06-07 #77. `cc3a0dc`. B1 XSS, B2 race, B3 ProfileImage, B4 Sticky, M1 DOMPurify memo, M2 specific errors, M10 back 44px, N1+N2 cleanup. |
| RR-REVIEW-DETAIL-T3 | Review detail page Tier 3 polish | 2026-06-07 #78. `6c09c7d`. M6 sticky@md, M7 skeleton, M8 h1 cap, N3 useMemo normalize. M3 hook deferred. |
| RR-1-FOLLOWUP-1 | Submit-review auth model confirm | 2026-06-07 #79. Finding doc `00-inbox/finding-submit-review-auth-2026-06-07.md`. Auth model confirmed intentional (backend `AllowAny` on create + user/guest_email derivation). UX gap "Submitting as X" shipped `de964e3`. |
| F11-FOLLOWUP-LANDING | /help/faqs landing page | 2026-06-07 #80. `43ed62a`. 2 files 139+ (pages/help/faqs.js NEW + api.js +POSTS_BY_FAQ_CATEGORY). Replaces broken catch-all stub. 4-agent team debate (IA/UX/SEO + code-review) refined plan. Content questions pending. |
| CHECKOUT-BTN-1 | Checkout Next btn enabled on advance-booking/auth-loading | 2026-06-10 #90. `92bf653` dropped `isAdvanceBookingError` from `shouldDisableNext`. Fix `FormCard.js` `f7d2956` + backend `aed70f6` (advance_hr + stop_sale enforced at booking creation). |
| CROSS-SELL-1 | BD inventory gate — cross-sell returns 0 | 2026-06-10 #91. Inline booking modal shipped, ContractRecommendationSerializer fixed. Superseded by CROSS-SELL-MERGE. |
| WP-IMAGE-1 | WP Media Library tab + image URL pipeline | 2026-06-10 #88. `99e45b2` (admin) + `b3b8ee0`/`f7010d2` (backend). Root cause: is_deleted=True row leaking through unfiltered imagegallery_set. |
| IMG-PARITY-1 | ProductImages ↔ OperatorImages parity | #87. `c425ff6` + `e777816`. Migration 0059, shared components in `components/Images/shared/`. 3 atoms. |
| IMG-ALT-1 | Operator image alt_text + caption editing | #86. `71c2352` + `08b6593`. Migration 0058, 3-field dialog + auto-prefill. Atom [[operator-image-alt-caption-fields]]. |
| IMG-META-BUG-1 | ImageGallery metadata dropped on existing-row edit | #87. `operators/views.py:720-722` elif only wrote order. Fix `c185523`. Atom [[django-partial-update-elif-metadata-drop]]. |
| FAV-1 | Favorite heart | 2026-06-08 #83. `951bd9c` FE + `3c0d1b6` BE. RDS migration 0026 DROPPED per user — runbook in `01-projects/favorite-heart-analysis-2026-06-08/migration-0026-runbook.md`. |
| BRANCH-INCIDENT-1 | develop branch accidentally deleted in bulk cleanup | #84. `git branch -d develop` succeeded (merged into itself), main checked out. Self-restored from `origin/develop`. Lesson: `git for-each-ref --format='%(refname:short)' refs/heads/` for scripts. |
| IMG-IND-1 | Operator/contract image independence audit | #85. Intentional separation confirmed (no cascade). Informational Alert in delete dialog. Atom [[django-soft-delete-s3-file-preserve]]. |
| CART-1 | PARSING_ERROR catch | #82. Branch in `DayTripBookingWidget.js` before generic else surfaces RTK PARSING_ERROR (HTML 500). |
| HD-1 | CurrencySelector small tablet | #82. Audit claim stale — `min-h-[40px] min-w-[40px]` already present per WA-6 standard. Actual path `components/UI/CurrencySelector.js:55`. |
| IDX-1..4 | index.md lint (unindexed pages, dup-basename wikilinks) | #82. 3 files renamed `-overview`, 17 wikilinks + 9 YAML parents updated. |
| WA-2 | Website audit Sprint 2 (F4-F8) | `d1fcf47` #62. |
| WA-3 | Website audit Sprint 3 (F9-F11) | `0b30580` #67 + `d9d1425` #68. |
| WA-4 | ProfileMenu UX consolidation | `44e209d` + `40b0a36` + `f4d581f` + `314020c`. |
| WA-5 | Footer secondary nav + SearchDialogTrigger touch targets | `781bf7a` #70. 15 files. |
| WA-6 | F2 refinements — 40px icon button standard | `1e4c549` + `fbdca15` + `e782c41`. |
| WA-7 | ProductSearchForm2 mobile input height | `f1cbb5d` #63. |
| F11 | Homepage visible FAQ section | REWORKED `3534e21` #72. TrustStripSection.js NEW. |
| F11-FIX-1 | item.locationFields undefined in /help/faqs | `e6d1731` #72-followup. |
| TRUST-STRIP-1 | Trust strip white card wrapper | `9505117` #72-followup. |
| GYG-IMPL | GYG 5-pattern | #73. `pages/rate-review/[reviewSlug].js:161,479,414-416`. |
| RR-1 | Rate-review Release 1 | Shipped #74-#79 (`8ac1029`, `cc3a0dc`, `6c09c7d`, `de964e3`). All tiers + UX gap. M3 hook extraction deferred (different endpoints/auth). Auth model confirmed intentional. |
| RR-1-FOLLOWUP | Submit-review no session guard | #79. |
| RR-1-FOLLOWUP | [reviewSlug].js:43 dead commented canonical | #77 N2. |
| **TRIP-SEARCH-REDESIGN (R1)** | Travel Decision Engine redesign `/trips/[from]/[to]` | **CLOSED 2026-06-14/15.** Phases 3-7 shipped `933b1b6`. Confidence score, sidebar removal, header, calendar, skeleton, filter, sort, trust badges, getTrustBadges bug fix. BE `develop` @ `64a2fce`. | [[trip-search-results-implementation-plan-2026-06-14]], [[trip-search-results-redesign-2026-06-14]], [[adr-trip-confidence-score-algorithm]] |
| **TRIP-SEARCH-REDESIGN-R2** | Round 2 + below-fold | **CLOSED 2026-06-15.** Hero, transport combo filter, RecommendedTripCard (P6), round-trip UX, below-fold (RouteFAQ new, RouteSummary ISR rewrite, TripSummary price+schema). FE develop @ `6f2ada9`. P1-P5/P7-P10 CUT. P11 no-op. Deploy to prod pending (ops). | [[trip-search-below-fold-redesign-2026-06-15]] |

## 2026-06-18 — purged from master-state Section 2 (vault optimization)

| **OPERATOR-DESC** | Operator `description` field (backend) → unblocks GEO "about operator" prose on `/operators/[slug]` (flagged in SEO/AEO/GEO audit, the one truly backend-blocked item). | **CLOSED #125** — verify-only: backend was already complete (`Operator.description = TextField()`, `OperatorDetailSerializer fields='__all__'`). Live curl confirmed populated text returned. FE wired About-{operator} section at `pages/operators/[slug].js:151` (FE `f75b411`). | done |
| **OPERATOR-TAB-COUNTS** | `by_type` aggregation (TRANSPORT-type only, computed pre-type-filter) on `OperatorContractsViewSet.list` summary → enables per-type counts in the operators page MUI tabs ("Join Tour (12)"). Frontend tabs already shipped without counts. | **CLOSED #125** — BE `0d6a3cf`, FE `f75b411`. `summary.by_type = {ALL, PRIVATE, JOIN, CHARTER}` keyed to `FILTER_TYPES`. Bug caught: `select_related` INNER JOIN was under-counting (15→3); fix = aggregate from `Contract.objects` directly. 4 invariance tests added (`operators/tests/test_operator_contracts_viewset.py`). | done |
| **MIN-RATE-BE-MERGE** | BE `fix/popular-routes-lowest-price` @ `4da0b81` — merge to develop + verify `/front-page/` Hatyai→Koh Lipe `lowest_price` matches SlideCalendar rate | **CLOSED 2026-06-16** — merged at `37387c8`, BE develop now `21fbdcf` | `smartenplus-backend/products/views.py:1197` |
| **TRUST-BADGE-BUG** | `getTrustBadges` Free-Cancellation inverted | **CLOSED 2026-06-14.** Fixed in Phase 0.5 — `refund_percentage === 0` → `=== 100`. Shipped in `feat/trip-search-redesign`, now on `develop`. | `helpers/getTrustBadges.js:19` |
| **PAYMENT-FIX** | Implement 5 HIGHs + priority MEDIUMs from payment deep review | **CLOSED 2026-06-13.** All 5 batches shipped + 8/8 E2E automated + webhook gap closed. **Both PRs MERGED:** FE merge `dae26da` (`main`), BE merge `5653b04` (`main`) — feature branches deleted. 119 tests pass. M4 retracted. | [[payment-deep-review]], [[payment-auto-test-results]], [[omise-webhook-tailscale-local-testing]] |
| **PAYMENT-DEADLOCK** | Recover paid-but-unfinalized order PLB0229785 from payment_pending deadlock | **CLOSED 2026-06-13.** Fix `482cfc6` "recover paid-but-unfinalized order from payment_pending deadlock" is head of BE `main`. 278 BE tests pass. | [[payment-pending-deadlock]] |
| **DESIGN-SYSTEM-PHASE-1** | Token completion (audit 2026-06-13) | **CLOSED 2026-06-13.** OPACITY, Z_INDEX, TRANSITIONS, LAYOUT, SIDEBAR_CONFIG added (`helpers/designSystem.js:149-210`); token migration FE `489de5f`+`b5ce878` (18 files). Residual gaps (typography line-height/letter-spacing, 4 stray `#fff` in globals.css) trivial — untracked. | [[design-system-audit]] |
| **KB-ATOMIZATION-PAYMENT** | 12 KB gaps from payment deep-review verification report | **DEFERRED.** Batch with next `/lint-vault`. M8 in `payment-backend-charge-flow.md` §5 verified accurate (email-guard ownership check present). | [[payment-deep-review]] |
| **BOOKING-PAY-FIX-1** | Fix 4 verified bugs from booking-payment e2e audit | CLOSED #94. Merged `fix/checkout-stable-id-cleanup` → `develop` (`f271aef`). 53/53 tests, SM-1–SM-4 passed. | `hooks/checkout/useCartSync.js`, `components/UI/BookButton.js:41-43` |
| **BOOKING-PAY-REPRO-1** | Runtime repro C1 (formData lost on hard refresh) + C2 (transient error nukes cartId) | CLOSED #97. C1: `isCartLoaded &&` guard in clear-assignments effect (`checkout/index.js:188`). C2: `if (error?.status === 404)` in catch (`check-and-createcart.js:67`). Commit `cb817d9` on `develop`. | `pages/checkout/index.js:188`, `components/HOC/check-and-createcart.js:67` |
| **CROSS-SELL-MERGE** | Merge `feat/redesign-people-also-book-cards` → `develop` | CLOSED #97. Branch confirmed fully merged (`git merge-base --is-ancestor` → FULLY MERGED). `CheckoutRelatedTrips` mounted at `checkout/index.js:1010`. All recommendation components present. Remaining work is BD inventory only → see CROSS-SELL-BD-INVENTORY. | done |
| **BRANCH-CLEANUP-REMOTE** | 81 merged remote `origin/2606*` branches pending deletion | CLOSED #97. 42 actual branches deleted (vault count was stale). `git branch -r \| grep origin/2606 \| wc -l` → 0. `git fetch --prune` run. 45 remote branches remain (all active). | done |
| **FRONTEND-AUDIT-FIX-1** | Audit finding 3 (Formik render-prop useEffect) | CLOSED #95. PR1 `fix/audit-checkout-passengers-hooks` (e5261ab → 1e46314). New `FormikValuesSync.js` (105 lines) absorbs both effects via useFormikContext. Rules-of-hooks invariant restored. Lint clean. | `components/forms/checkout/FormikValuesSync.js`, `Passengers.js` |
| **FRONTEND-AUDIT-FIX-2** | Audit findings 1+2+4+5 (RTK Query) | CLOSED #95. PR2 `fix/audit-rtk-query-cleanup` (ecc76a9 → b6b956e). getSession pattern, activities key, cart-version extract, createCart single invalidation. New `store/cart-version.js` (12 lines). 3 sources of truth → 1. Lint clean. | `store/cart-version.js`, `store/cart-slice.js`, `store/api/*`, `store/index.js` |
| **FRONTEND-AUDIT-FIX-3** | Audit findings 6+7+8+9 (dead code + hygiene) | CLOSED #95. PR3 `chore/audit-deadcode-and-hygiene` (d69b473 → fbe9aab). 31 files, 4237 deletions, 7 insertions. Rebased onto develop post-PR1+PR2. | 5 dead-code paths, 5 .backup, 2 logs, db/ data/ *.diff *.sh, 4 archive, .gitignore |
| **FRONTEND-AUDIT-FOLLOWUP-1** | 2 exhaustive-deps warnings in FormikValuesSync.js:61:6 | CLOSED #97. Suppression comments added. Effect 1: refs + useState setter stable by definition. Effect 2: `cartitems?.cart_item` kept (not `cartitems`) — tighter RTK refetch trigger. Lint clean. Commit `7107516`. | `FormikValuesSync.js` |
| **FRONTEND-AUDIT-MANUAL-PRS** | Open 3 PRs on GitHub manually | DROPPED #97. All 3 branches confirmed merged into develop (`git branch -r --merged develop`). Merge commits `e5261ab`, `b6b956e`, `fbe9aab` in git log are the audit record. Retroactive PRs add no value. | 3 remote branches |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short when cart item overlaps backend rec (FE excludes cart ids AFTER backend per-zone caps; multi-item cart scales waste, 2-transport cart empties zone) | CLOSED #249 — **DO NOTHING per 4-agent audit** [[rec-engine-report-audit]]. Severity overturned: near-zero incidence (collision inventory doesn't exist — Koh Lipe returns/island tours absent), empty zone arguably correct UX (user already has transport), `checkout_recommendation_empty` GTM measures it. Option A `exclude_ids` rejected unanimously (unbounded cache-key space on 1-vCPU box, RTK cache churn per cart mutation, only fixes cart-overlap drain not `filterValidRecommendations` drain). If ever revisited: 1-line finder over-fetch `[:limit*2]` in `find_transport_at_location`, NOT exclude_ids. Monitor GTM ~30 days. | `products/services.py` get_recommendations · [[recommendation-engine-completion-roadmap]] |
