# Second Brain — Operational Log

## [2026-06-15] optimize | atomized 3 concepts from 5 oversized project files — slimmed 5 source files (481/469/433/378/391 lines from 527/492/444/437/407), extracted 3 atoms: [[contract-confidence-score-algorithm]] (formula + N+1 fix), [[route-intelligence-hero-spec]] (Phase 1 locked spec), [[core-web-vitals-budget-2026-06-06]] (site-wide perf budget). 2 candidates deleted as duplicates of existing [[sentinel-content-type-bookmark-blog]] + [[dompurify-xss-prevention-pattern]] (anti-duplication check caught both). Skipped caveman:compress (skill targets memory files, not technical vault notes — 0.7% savings on test file). Skipped full wikilink orphan sweep (49 orphans; most are "worth writing later" stubs per vault protocol). Deferred: PDF topic finalization (4 files, 36 markers), MOC creation for payment/nextjs clusters, payment-2026-06-12 burst merge. index.md updated.

Chronological record of vault operations. Parseable: `grep "^## \[" log.md | tail -5`

## [2026-06-15] fix | header-search-summary-ipad — Inline (desktop/iPad) path of `HeaderSearchSummary` truncated route to "Hatyai → K..." and "Edit Search" button wrapped to 2 lines at 768px. Fix: route gets `shrink` + `min-w-0` so it truncates last; trip-mode hidden at `md`/shown at `lg`; passenger shows icon+count at `md`, icon+text at `lg`; Edit Search uses `icon-branded` (40px blue circle) at `md`, text button at `lg`; Dots tightened to `mx-1` at `md`. No Redux/modal changes.

## [2026-06-15] research | mobile-search-bar-ux-competitor-research-2026 — Competitor analysis (Google Flights, Airbnb, VRBO, 12Go, Booking.com) for mobile sticky search bar. Redesign direction: chip pattern, brand-blue filled CTA, drop "One Way" label, 44px touch targets. Branch: `feat/mobile-search-bar-redesign`. Atom: [[mobile-search-bar-ux-competitor-research-2026]].

## [2026-06-15] fix | trip-page-currency-context — 2 outliers on `/trips/hatyai/koh-lipe` made currency-aware. `SlideCalendar2.js:977` hardcoded `฿{dayFare.toLocaleString()}` + `TripSummary.js:35` hardcoded `from THB {minPrice.toLocaleString()}` — both bypassed `CurrencyContext`. User selecting USD/EUR/JPY via `CurrencySelector` saw mixed display (calendar + Departures by Operator still in ฿, everything else converted). Fix: `useFormatPrice()` hook in both (same pattern as 5 already-correct components: `TripItem`, `FilterTrip`, `TripDetailBooking`, `RouteFAQ`, `TripItemAccordionContent`). Added `whitespace-nowrap` to calendar cell to absorb longer `"THB 1,234"` output. JSON-LD `priceCurrency: 'THB'` in `TripSummary.js:91` **intentionally unchanged** — schema describes merchant offer, not viewer display. Lint clean. Branch: `fix/trip-page-audit-2026-06-15` (sits on top of the 13 fixes from the prior session). 2 atoms: [[currency-context-price-rendering-rule]] (useFormatPrice canonical pattern + JSON-LD base-currency rule), [[slidecalendar2-farecalendar-prop-pattern]] (prop contract + caller inventory — 1 of 5 wires `fareCalendar`; `TripDetailSchedule` out of scope, pre-existing). Vault index + master-state updated.

## [2026-06-15] scope-cut | trip-search-results-plan — Grill+principles review cut P4/P5/P9/P10. P4 ConfidenceScore: no consumer after P8 cut, inline if needed. P5 RouteTimeline: JourneyTimeline exists but wrong scale, TransportItems already covers it. P9 TravelInsight: no API data, violates no-fake-metrics rule. P10 seats_available: BE complexity not justified. Remaining: P6 (scoping needed) + P11 (SEO check). Doc: [[trip-search-results-implementation-plan-2026-06-14]].

## [2026-06-15] update | trip-search-results-plan — Round 2 scope correction. Code-truth audit vs user confirmation: P2 sidebar DONE (TripsPageLayout single-column confirmed), P1 RouteIntelligenceHero CUT (SearchCover kept), P7 BookedCounter /10 CUT (booked_count default=10 seed makes real counts misleading), P8 RecommendedTripCard CUT (Top Pick badge from Round 1 sufficient). Remaining: P3/P4/P5/P6/P9/P11 unblocked, P10 BE gate. Doc updated: [[trip-search-results-implementation-plan-2026-06-14]].

## [2026-06-15] fix | round-trip-ux — 4 commits shipped to `develop` (FE @ `a3c328a`). (1) `TripProgressIndicator` collapsed into breadcrumb row — strip card chrome, save 44px vertical stack above calendar, both mobile+desktop. Mobile: icon+step-counter inline. Desktop: dots+label inline right. (2) Hero route bug fixed — `SearchCover` always received original slug props never reversed; during return step showed `Hatyai→Koh Lipe` while fetching `Koh Lipe→Hatyai`. Fix: swap `initialFromLocation`/`initialToLocation` when `isReturnJourneyActive`. Redux untouched (edit-search correct). (3) Width inconsistency fixed — aligned `mx-2 md:mx-3 xl:mx-0` to match sibling components, removed conflicting wrapper div. (4) Review label `md:hidden` fix. `SelectedOutboundSummary` card debated, reverted, open item — data path confirmed (`useCheckCartIdQuery → cart_item[0].contract.trip`). Vault plan updated. Doc: [[trip-search-results-implementation-plan-2026-06-14]].

## [2026-06-14] audit+scrutinize | trip-search-results — 3-agent code-truth audit (28/36 claims verified, 6 corrected) + outsider scrutiny (3 Phase-6 trace findings). **CRITICAL corrections:** (1) `SlideCalendar2.js` is LIVE (lines 463-1036: Redux calendar sync, URL push, return-trip validation, modal picker) NOT commented out — Phase 4 rewritten to extend not replace; (2) `getTrustBadges` Free-Cancellation inverted-bug (`refund_percentage === 0` should be `=== 100`, helpers/getTrustBadges.js:19) — flagged as TRUST-BADGE-BUG; (3) `RecommendationViewSet` exists (`products/views.py:1685`, cross-sell not search-rank) — ADR Rejected Alt B corrected; (4) `getMainPrice` needs 5 args not 1; (5) `contractsToRender` field hoisting (departureTime→departure_time map); (6) existing top-3 banner collision when recommended pulled out (copy fixed). Stamps in all 3 docs. Docs: [[trip-search-results-implementation-plan-2026-06-14]], [[trip-search-results-redesign-2026-06-14]], [[adr-trip-confidence-score-algorithm-2026-06-14]].

## [2026-06-14] plan | trip-search-results-redesign — Phase 0 complete. 3-agent analysis (backend feasibility + frontend arch + UX spec) → design doc + ADR + 7-phase impl plan. "Travel Decision Engine" vision for `/trips/hatyai/koh-lipe`: compact header, date strip, quick filter pills, recommended trip card + confidence score (formula: rating 45 / reviews 25 / popularity 20 / score-bonus 10 — raw `score` null on most contracts so reweighted from original 40%). Backend prereqs: `confidence_score` SerializerMethodField (+ `_get_review_stats` to avoid 3rd N+1), `has_direct_option`, `has_refundable_option`, `is_refundable`. Reuse targets verified: BadgeChip, UnifiedCard, TripCard, BookButton, getMainPrice, getTrustBadges, sortContractsByScore, filterData shape. "Best Value" pill deferred (no sort key). NO CODE — plan-only, FE `main` `4b65756`. Index + master-state updated.

## [2026-06-13] audit | design-system-audit-2026-06-13 — Full design system audit completed. 289-line design token system at helpers/designSystem.js, 62 shared UI components. Findings: 889 hardcoded hex colors, 386 inline style={{}} attributes, mixed styling (Tailwind + MUI + CSS Modules + inline). Token gaps: padding/margin scale, width/height tokens, opacity scale, z-index system, transitions. Typography lacks line-height/letter-spacing. globals.css has 23 hardcoded colors. 33 CSS module files (0-410 lines). 5 debate outcomes: Tailwind utilities for spacing, hybrid MUI+Tailwind styling, dark mode architectural prep later, hybrid CSS Modules+Tailwind, vault docs not Storybook. 5-phase migration roadmap: Phase 1 token completion (1-2 days), Phase 2 component cleanup (1-2 weeks), Phase 3 pattern standardization (2-3 weeks), Phase 4 documentation (1 week), Phase 5 advanced (2-4 weeks). Priority matrix + 10 quick wins identified. Report: [[design-system-audit-2026-06-13]]. index.md updated.

## [2026-06-12] doc-update | payment-deep-review — M4 retracted, M8 KB inaccuracy added, verification pass appended. Updated [[payment-deep-review-2026-06-12]]: new "Verification pass (2026-06-12) — 3-agent KB cross-check" section after Scrutinize (M4 retraction detail + M8 KB inaccuracy + 2 refinement deltas + 12 KB gap list + verdict tally + Batch 1 implementation status). Doc drift list +5th entry: `payment-backend-charge-flow.md` §5 guest email validation claim. Suggested fix order updated: M4 dropped (subsumed by M1). Doc: [[payment-deep-review-2026-06-12]]. Verification: [[payment-deep-review-verification-2026-06-12]]. Implement: [[payment-implement-plan-2026-06-12]].

## [2026-06-12] implement | Batch 1 (H3 + H4) — 2 specialist implementers (backend-architect + react-specialist) launched for cross-repo fix. Both entered plan mode internally; killed FE agent (stuck in plan loop) and did both fixes manually. BE H3 committed `d7af0e9` (wrap reuse responses + move cart fetch, 8+/9- on orders/views.py). FE H4 committed `a3c8c80` (add charge_id + charge_created_at to orderDetails, 6+/2- on useOmisePayment.js). Both on `fix/payment-deep-review-2026-06-12` from develop. No push (manual PRs pending). Lint/syntax clean. Per-batch hand-back rule enforced: classifier blocked auto-commit, user sign-off granted explicitly. Tailscale noted for Batch 2 pre-flight (dev webhook flow).

## [2026-06-12] kb-verify | payment-deep-review — 3 verifier agents cross-checked all 5 HIGHs + 18 MEDIUMs against ~1700 lines of vault payment/omise KB + read-only code spot-checks. 20 CONFIRMED · 2 REFINED (H1, M17) · 1 REFUTED (M4) · 1 KB inaccuracy (M8) · 12 KB gaps surfaced. **M4 REFUTED** — finding's `{error:'payment_pending'}` claim is wrong; canonical code is `pending_charge_exists` and FE maps it (M4 subsumed by M1, recommend retraction). M8 KB inaccuracy: [[payment-backend-charge-flow]] §5 claims email validation in `ChargeOrderView`; code shows it's only in `ExpirePendingChargeView` (`views.py:375-376`). 12 KB atomization candidates: payment-amount-validation-rule, payment-legacy-deprecation-map, IntegrityError cleanup pattern, order-creation-filter-rule, self-heal coverage matrix, payment-model-fields, payment-method-name-contract, useQRPolling 4xx branch, usePaymentInitialization lifecycle, usePaymentCouponManager state machine, refund validation rule, order-create response envelope contract. Doc: [[payment-deep-review-verification-2026-06-12]]. Implement plan: [[payment-implement-plan-2026-06-12]] (5-batch sequence). Index updated.

## [2026-06-12] kb-correction | cross-check scrutinize findings against Omise KB — 3 files updated: [[payment-gateway-charge-architecture]] corrects wrong lock order claim (Coupon→Order was false; Order locked only, Coupon implicit via F() UPDATE), [[payment-finalize-deep-dive]] side-effect order step 0 added + M6 contention note, [[payment-exception-catalog]] adds M13 silent declined-card pattern (201 + status='failed' → FE success:true → silent).

## [2026-06-12] scrutinize | 4th-pass end-to-end trace of [[payment-deep-review-2026-06-12]] — 4 corrections applied in-place: H1 fix note clarifies fee always in THB (traceable to orders/views.py:1582); H4 adds failure_code to dead-field list; M6 reclassified from "deadlock" to "contention/block" (no circular wait, ApplyCouponView never waits for Order lock); M13 full UX trace added (declined card → success:true → completely silent). All 5 HIGHs confirmed correct. Fix order unchanged. Scrutinize section appended to report.

## [2026-06-12] cleanup | delete 3 empty placeholder files — decision-slug-1.md (archive, git-tracked), decision-slug-2.md (root), docs/testing/PAYMENT_CHECKOUT_AUDIT.md. All 0 bytes, never filled. Template wikilinks in project-readme.md kept. `find . -name "*.md" -empty` → 0. Committed `508267a`.

## [2026-06-12] session-end | payment KB complete — 4 notes + 3 updates + 3 atoms + wikilink scan clean — Backend + Omise scan done. All payment patterns documented end-to-end (frontend + backend + Omise SDK + Celery). 3 atoms: [[omise-attributes-dict-extraction]], [[django-celery-beat-database-scheduler]], [[toctou-select-for-update-before-api-call]]. master-state → session #100. Vault pushed.

## [2026-06-12] deep-scan + create | backend + Omise payment scan — 4 new notes + 3 updates — 3-agent scan of payments/ models/views/services/tasks + gateway.py + orders/ManualAdjustment. Found 12 undocumented patterns. New notes: [[omise-client-integration]] (lazy module init not instance, `_attributes` dict extraction, LINE_PAY→rabbit_linepay, reversed→PENDING, PromptPay QR URI nested path at charge.source.scannable_code.image.download_uri), [[payment-backend-charge-flow]] (DB constraint unique_pending_redirect_charge_per_order, TOCTOU guard select_for_update before expire(), 5-sec reconcile throttle, C3b proactive PP expiry before PendingChargeError, AllowAny+manual ownership via user_id||email, satang conversion), [[manual-adjustment-model]] (fields, PROTECT FK, no Omise, ExtraItemAction legacy), [[celery-beat-payment-scheduling]] (DatabaseScheduler not settings.py beat_schedule, Django admin UI, retry wired-but-uncalled confirmed). Updated 3 existing: refund-flow (Omise call pattern, partial refund flow, booking_slug purpose, cards.Refund deprecation detail), payment-charge-service-layer (_attributes extraction, 5-sec throttle, TOCTOU guard), payment-status-enums (OMISE_STATUS_MAP reversed→PENDING, PAYMENT_METHOD_MAP frontend code table). index.md + log.md updated.

## [2026-06-12] deep-scan + create | frontend code scan — undocumented patterns → 7 new vault notes — 3-agent parallel scan of Redux/RTK Query/checkout/HOC/hooks. Found 30 undocumented patterns. New notes: [[redux-store-architecture]] (migrate v3→v7, cross-tab CART_VERSION_KEY, dual reset, SSR no-op storage, deprecated cart-slice, auth whitelist, 48hr TTL, stale processing reconcile), [[rtk-query-advanced-patterns]] (child/children normalization, fixedCacheKey, missing invalidatesTags, bookmark suppression, 'null' guard, forceRefetch date), [[checkout-hoc-architecture]] (withCartValidation ref dedup + 404-only clear, withCheckCartValidation, withComponent risk), [[checkout-state-persistence]] (useCartSync 6-effect ordering, ghost trip detection, dual persistence, guest→backend migration, debounce normalization), [[checkout-formdata-time-fields]] (frontend lowercase-t vs backend capital-T, HH:MM:SS format, 3 helpers), [[checkout-step-flow]] (hasMixedPassengerCounts 4vs5 steps, payment init idempotency key, CONTRACT_INACTIVE auto-redirect), [[frontend-debug-utilities]] (useRateLimitedQuery singleton+jitter, DevToolsProvider, useAuth 100ms). Updated 3 existing: checkout-formdata-persist-guard-pattern, rtk-cart-tag-invalidation-auto-refetch, redux-persist-gate-scope-gap. index.md + log.md updated.

## [2026-06-12] deep-scan + create | payment KB deep analysis — 6 new vault notes for undocumented implementation patterns. Backend: [[omise-webhook-security]] (Event.retrieve() not HMAC, double-layer dedup), [[payment-exception-catalog]] (all exceptions + HTTP codes, AmountMismatch never re-raised contract), [[payment-finalize-deep-dive]] (snapshot validation log-only, expired→success recovery, superseded charge guard, cross-order lock, CAS notification dedup, side-effect order). Frontend: [[payment-frontend-flow-mechanics]] (Card vs Source flows, canContinue 3-condition gate, NO_CONTINUE_METHODS, amountLocked UX, QR retry sequence, JPY scaling, OmiseScriptLoader linear-not-exponential bug), [[payment-qr-polling-mechanics]] (4-format response fallback chain, finalStatusCheck on expiry, guest vs auth signatures), [[payment-celery-expiry-strategy]] (PromptPay TTL, MB polls Omise, e-wallet 30min, superseded charge guard, retry uncalled bug). Updated 4 existing notes (payment-integration +3 Related links, payment-status-enums +authorized Order.status, payment-charge-service-layer +staleness reuse, payment-gateway-charge-architecture +new note links). index.md + log.md updated.

## [2026-06-12] vault-scan + gap-fill | payment knowledge base audit + repairs — 3-agent scan of 18 payment notes. Findings: 5 broken wikilinks (booking-payment-e2e-audit, payment-system, checkout-flow, orders, backend-architecture), 2 orphaned files (zero wikilinks), 3 contradictions (authorized status, getPrimaryCharge, Schedules integration status), 4 factual gaps (polling interval, double-click timeout, locked_amount rule, WeChat/Alipay active status). Fixed: 9 files updated (wikilink corrections, C1/C2 status to "FIXED cb817d9", factual enrichments), 2 files orphaned-to-linked (checkout-formdata-persist-guard-pattern, checkout-next-btn-disable-conditions). Omise integration summary corrected (Schedules/Occurrences → "Not Integrated"). All references now valid. index.md + log.md updated.

## [2026-06-12] ingest | omise-api-catalog-full-21-apis — 3-agent parallel fetch (core payment, financial/account, dispute/schedule/reference APIs). Expanded [[omise-api-reference-2026-06-12]]: 2-API stub → 21-section catalog. Core (Charges/Sources/Tokens/Refunds/Cards) active, Customers/Receipts/Search/Schedules partial, Account/Capability/Transfers/Balance/Recipients/Disputes/Forex/Documents not integrated. Status vocab mapping + integration summary. 196 lines. index.md updated.

## [2026-06-12] ingest | payment audit + Omise API gap check — 3-agent parallel (frontend code scan + backend docs + Omise API fetch). Findings: 4 confirmed bugs (2 MEDIUM cart-sync dead code, 2 LOW stable_id cleanup), 2 open candidates, Omise Documents API non-applicable (dispute-only). Vault: 2 new pages ([[payment-audit-bugs-2026-06-11]], [[omise-api-reference-2026-06-12]]), 3 updates (payment-integration +expiry paths +open issues, payment-status-enums +clean()-only clarification, payment-gateway-charge-architecture +lock order). index.md + log.md updated.

## [2026-06-11] lint | vault optimization — 21 missing index entries added (8 projects + 13 knowledge atoms), 3 stale inbox items archived, empty inbox dir removed, pdf-contract-import-research.md split into pdf-parsing-pipeline-pattern.md + pdf-import-pre-validation-rules.md (371→42 lines), index Stats updated (~237 active pages), CLAUDE.md log path clarified (root vs 07-logs)

## [2026-06-11] implementation | 3 PRs resolved 9 audit items from [[frontend-architecture-audit-2026-06-11]] — PR1 Formik render-prop extract (e5261ab → 1e46314), PR2 4 RTK Query cleanups (ecc76a9 → b6b956e), PR3 dead code + hygiene (d69b473 → fbe9aab). 1 contamination incident recovered (parallel agents in shared worktree). bug-fixer-2 went idle 3+ hours; lead took over + amended incomplete commit. Sequential pattern adopted post-incident. Lint + build clean; tests gated by harness classifier. [[frontend-audit-implementation-2026-06-11]]. master-state → session #95.

## [2026-06-11] verify+atomize | two-pass falsification audit of [[booking-payment-e2e-audit-2026-06-11]] — all claims held, doc amended (3 test files + falsification notes). 2 atoms: [[rtk-lazy-query-tuple-misuse]], [[redux-persist-gate-scope-gap]]. master-state → session #93.

## [2026-06-11] audit | booking→checkout→payment e2e audit (FE+BE) — 4 confirmed bugs (useCartSync stable_id dead paths, remnants, BookButton dead hook), 2 candidates pending repro, order-lookup ruled intentional design + hardening recs, payment layer verified clean, 4 overturned. [[booking-payment-e2e-audit-2026-06-11]]

## [2026-06-11] atomize | 3 atoms from People Also Book session: [[rtk-cart-tag-invalidation-auto-refetch]], [[recommendation-anchor-first-transport-rule]], [[django-400-vs-409-duplicate-cart-item]]. master-state updated to session #92.

## [2026-06-10] fix | people-also-book recommendations — stable anchor (first transport) + filter already-carted trips from visibleRecommendations. `d64adcf` on develop.

## [2026-06-10] fix | people-also-book duplicate toast — catch 400 + includes('already exists') in RecommendationBookingModal catch block. `a64d280` on develop.

## [2026-06-10] correction | people-also-book-checkout-audit — debug-mantra falsification overturned 3 of 4 initial bug claims. Only 1 real bug confirmed: duplicate detection toast never fires (backend 400 ≠ frontend catches 409). 1 UX gap: greyed pre-fill with no explanation. Empty ratecard, stale date, string comparison all overturned on code read. [[people-also-book-checkout-audit]] updated.

## [2026-06-10] session-end | cross-sell full redesign: horizontal cards + inline booking modal + backend serializer availability fix

## [2026-06-08] optimize | caveman-compress 3 atoms (django-partial-update-elif-metadata-drop, image-metadata-formik-state-only-save, add-flow-metadata-helper-pattern) — stripped articles, shortened sentences, kept code/headings/links exact. Result: clearer mental model, ~12% byte reduction, zero info loss.

## [2026-06-08] atomize | two-surface-parity-shared-module — extracted from this session's `components/Images/shared/` extraction. Pattern: when 2 UI surfaces need identical UX (grid, search, dialog, actions) over different data sources, extract `shared/` module of sub-pieces. Each surface becomes thin wrapper. Multiple variants stay separate components, not boolean props. Reusable for any "two pages need same UX" / "two product types share field editor" / "two list views need same toolbar" scenario.

## [2026-06-08] session-end | #87: ProductImages ↔ OperatorImages parity SHIPPED + ImageGallery metadata edit bug FIXED. 2 repos on develop. Backend: 3 nullable CharField(250) on ImageGallery (alt_text/description/caption), migration 0059 applied, serializer writable, partial_update else-branch added (c185523) — elif only wrote order, dropped all other fields on existing rows. Frontend: shared `components/Images/shared/` module (ImageMetadataDialog + ImageSearchBar + useImageSearch + DraggableImageCard with caption bar), ProductImages brings 3 fields, search/filter, click-to-edit dialog. Add-flow carries metadata via `addImageIfUnique` helper (string-coerced pickString). Edit-flow reuses contract Save (Formik state + provider useAlert snackbar, no new mutation). 3 atoms: [[django-partial-update-elif-metadata-drop]], [[image-metadata-formik-state-only-save]], [[add-flow-metadata-helper-pattern]]. IMG-PARITY-1 + IMG-META-BUG-1 closed. Resume: F11-FOLLOWUP content answers, BRANCH-CLEANUP-REMOTE, IMG-ALT-DEBUG-1 HMR refactor.

## [2026-06-08] atomize | django-soft-delete-s3-file-preserve — extracted from [[operator-image-soft-delete-cascade-gap]] "Why They Are Independent" section. Generic Django + S3 invariant: soft-delete preserves the S3 file because other models may FK-reference the same path. Hard-delete would fire `post_delete` and break those references. Reusable for any file-bearing model with cross-model FK refs. Parent note trimmed to 2-line summary + wikilink per [[atomic-notes]] rules.

## [2026-06-08] correction | operator-image-soft-delete-cascade-gap — design is intentional, not a gap. The earlier "note" entry misframed the soft-delete vs contract `ImageGallery` separation as a gap requiring a cascade fix. User clarified: `OperatorImageGallery` and `ImageGallery` are intentionally independent. Soft-deleting an operator gallery image should not affect `ImageGallery` rows attached to contracts. Existing contracts are self-managed content edited through the contract management workflow. **No cascade should be implemented.** Retracted the A+ cascade recommendation from the initial audit. The "Decision" section of [[operator-image-soft-delete-cascade-gap]] is updated to call this correct, intentional design. Only admin-UX copy change is being made (informational block in delete dialog when `active_contracts > 0`). Vault: [[operator-image-soft-delete-cascade-gap]]

## [2026-06-08] note | operator-image-soft-delete-cascade-gap — cross-repo finding ingested. `OperatorImageGallery.destroy` (operators/views.py:1858-1882) is soft-delete only and does NOT cascade to contract `ImageGallery` rows (operators/models.py:514 + :556 — no FK, only shared `image` URL string). Result: admin "deletes" a master image, contract pages (`smartenplus-frontend/components/activities/detail/DayTripDetailPage.js:118`, `browse/DayTripCard.js:43-44`) keep rendering it via `contract.image` from `imagegallery_set`. `validate-deletion` (operators/views.py:1910) computes `active_contracts_count` but gates `safe_to_delete` on bookings/carts only — contracts surface as informational warning only. `_ImageGallerySerializer` (operators/serializers.py:148, used by ContractSerializer:168) ships `[id, image, order]` — no deletion state to consumer. `signals.py:85-132` S3 cleanup only fires on hard-delete (intentional — prevents broken-image breakage). Decision: keep current behavior (correct invariant), close gap via admin confirmation dialog promoting the existing `warnings[]` line. Vault: [[operator-image-soft-delete-cascade-gap]]

> superseded by correction entry above. The framing as a "gap" was wrong — see the correction for the actual design intent.

## [2026-06-06] session-end | #56: website-audit team review COMPLETE + wrap-up. 3 specialists (perf/mobile/SEO-AI) + skeptic + leader. 15 audit issues → 12 P0-P3 items with file:line refs (~18 hrs). 5 atoms extracted (next-font, 44px-touch-target, ios-zoom-16px, brand-name-constant, embla-align-start). Vault + index + log updated. Frontend untracked: 2 new agent files. Resume: Sprint 1 P0 (F1 14px inputs, F2 44px touch targets, F3 WhatsApp wrapper).

## [2026-06-06] team-review | website-audit-full — 3 specialists (perf/mobile/SEO-AI) + skeptic + leader; 15 audit issues → 12 P0-P3 ranked items with file:line refs, sprint plan (~18 hrs), 23-file change inventory, regression test matrix. 6 audit claims reclassified as ALREADY DONE (compress: true, WebP config, GTM deferred, InArticleCTA, ProductJsonLd on Experience, BreadcrumbList on Experience). Implementation plan appended to [[website-audit-full-2026-06-06]].

## [2026-06-06] session-end | #55: website audit ingested + vault optimizer run. master-state cleaned (HEIC-1 closed, GYG-IMPL deduped). No code changes.

## [2026-06-06] ingest | website-audit-full-2026-06-06 — full external audit, SEO 75/Speed 40/A11y 85, 3 critical speed blockers, 5 high, 4 medium. Blog identity crisis + mobile touch target failures. 15 priority actions. Vault: [[website-audit-full-2026-06-06]]

## [2026-06-06] session-end | #52: rate-review 6-agent audit COMPLETE + Release 1 SHIPPED. r1-ux+r1-visual+r1-frontend+r2-skeptic+r3-leader+r4-scrutinize+r5-impl. 52 raw → 34 findings. P0-1 XSS DOMPurify fix (`[reviewSlug].js:460`), P0-2 parseISO null guard (`BookingReviewList.js:43-46,110`), P0-3 star ARIA radiogroup (`RateAndReviewForm.js`), P1-1 router import+paths (`BookingReviewList.js`), P1-2 email masking (`ReviewList.js:55`). FE-22 deferred. Sprint 1 queued. Vault: [[rate-review-uxui-audit-2026-06-06]]

## [2026-06-06] audit | rate-review UX/UI audit — 5-agent team (3 specialists + skeptic + leader). 52 raw findings, 34 unique actionable, 3 P0 confirmed. P0: stored XSS in [reviewSlug].js (dangerouslySetInnerHTML no DOMPurify), parseISO(null) page crash (BookingReviewList sort+render), star rating broken ARIA (aria-pressed vs radiogroup). P1: wrong router import (next/navigation in Pages Router), unmasked email GDPR violation, redirect produces /rate-review/undefined after submission. Design system compliance: 6.1/10 current → 9.0/10 target. Status: OPEN. Vault: [[rate-review-uxui-audit-2026-06-06]]

## [2026-06-05] session-end | #51: activities pagination orphan + dead-space fix SHIPPED to develop. 3-specialist audit (UX/Visual/Performance) → Skeptic → Leader → 2 P0 (pageSize 16→12, remove min-h) + 1 P1 (skeleton 6→12). Backend verify PASS (CustomPagination max=100). 4 LoC, 2 files, 1 commit (`2226981`). Merged develop `2bfc2bd`. Vault: [[activities-pagination-ux-audit-2026-06-05]]

## [2026-06-05] session-end | #50: activities card rating gate fix SHIPPED to develop. Drop `review_count >= 5` gate → `average_rating > 0`. Rating visible from 1 review. Color-coding rejected (GYG standard = uniform gold). 1 LoC, 1 commit (`3ce3c12`). Vault: [[gyg-card-rate-analysis-2026-06-05]]

## [2026-06-05] session-end | #49: activities /activities default category fix (3a4db81, DAY_TOUR→null) + pagination reset bug root-caused + fixed (01b3708). Root cause: React StrictMode + didMountRef persistence + setFilters side effect. Fix: no-op guard in setFilters callback + scroll:false on shallow URL push. 3 atoms extracted. develop 01b3708.

## [2026-06-05] session-end | #48: GSC-1 Phase 1+2 SHIPPED — noindex:!dataValid on empty trip pages + station-slug sitemap duplicates removed. NEXT_PUBLIC_DOMAIN leading-space bug found + user fixed in GitHub Secrets. develop 0eaf9b2. 3 files changed.

## [2026-06-05] session-end | #47: GSC 52,400 "Crawled Not Indexed" investigation. 3-team adversarial review. Primary cause: empty ISR pages (not URL pollution). notFound blanket approach overturned — 14 Koh Lipe seasonal routes at risk. Safe 3-phase plan documented. No code deployed. Vault: [[gsc-crawled-not-indexed-investigation-2026-06-05]]

## [2026-06-05] session-end | #46: blog canonical URL bug fixed (GSC "Alternate page"), WP subdomain https? regex fix, help page www prefix, develop `b0fce4f`, vault atom [[blog-canonical-url-wp-subdomain-bug]]

## [2026-06-05] session-end | #45: homepage nav labels fixed (Journeys→Routes, Explore Thailand→Destinations, H1 fix), vault organized, 3 atoms extracted, develop `aef5548`

## [2026-06-05] ingest | homepage-terminology-audit: 3-agent SEO+UX+Tech debate, production SEO phase 2, nav labels fixed (3 files), 3 atoms extracted, vault organized (root strays moved, inbox cleared)

## [2026-06-04] session-end | #43: HOTEL_PICKUP invariant (3a59a41 backend) + admin-dashboard Yup validation (c2e8e4e+5f068ef) + MeetingPointCard reviewed OK. CMA-1 nearly closed — only data inventory remains.

## [2026-06-04] session-end | #42: CMA-1 casing ADR (375e501) + CMA-2 meeting_point fix (09d6f3a backend) + get_translated_meeting_point_details deferred. Next: ContractDetailSerializer.validate() HOTEL_PICKUP invariant.

## [2026-06-04] decision | adr-info-fields-casing: info_fields casing boundary documented — 1 vault ADR + inline comments in 6 frontend files. CMA-1 casing item closed.

## [2026-06-04] session-end | CMA-1 partial: showStations deleted (ff8006e frontend) + admin PATCH guard fixed (22dc045 backend) + debate found Contract.clean() mis-scoped (rescoped to ContractDetailSerializer.validate()) + CMA-2 new gap ServiceDetail.js:35

## [2026-06-04] session-end | fix timeline stop deletion bug — 3 repos, migration 0028 applied, all merged to main. 3 atoms: django-nested-delete-sweep-pattern, django-nullable-fk-migration-pattern, react-client-key-null-id-pattern

## [2026-06-04] ingest | gyg-page-analysis — 3-specialist GYG Chiang Rai tour analysis, 11 candidates → 5 adopted (1 P0 footer meta strip, 2 P1 not-suitable-for + review thumbnails, 2 P2 sort/filter + itinerary disclaimer), 4 P3 backend debt flagged (audio guide 41 langs, private group, per-aspect rating, provider response), AI summary user-deferred. Vault: `01-projects/gyg-page-analysis-2026-06-04/`. Supersedes [[experience-detail-page-redesign-2026-06-02]] deltas. WebFetch unavailable, text dump used.

## [2026-06-03] ingest | business-development-docs — Ingested 6 business-development docs into vault. Notes created in 01-projects/: thesis (2026-2029), thailand-platform-analysis, thailand-bundle-architecture, thailand-bundling-margin, unified-travel-wellness-thesis, zeitrip-mvp. Index updated.

## [2026-06-03] decision | vault note strategy — 2-agent debate (bulk vs atomic). Team: bulk-advocate (one note per doc), atomic-advocate (per-concept extraction). User chose project notes (01-projects/ one note per source doc). Preserves document context, aligns with vault anti-overengineering rules.

## [2026-06-03] decision | airport-transfer-width-fix — 3-agent debate + judge. Option C (targeted margin reduction) chosen over Option A (full-width restructure) and Option B (status quo). Surgical: remove `px-2 md:px-3` from outer section, add `px-4 xl:px-0` to inner wrapper. LAY-1 precedent applied. 2 files, ~4 line edits. ProductCardContainer mx-2 preserved. Doc updated: [[airport-transfer-width-audit-2026-05-30]] now RESOLVED. — 1007-line source condensed to `02-areas/content-marketing-strategy-2026-06-03.md` (~190 lines). Hub-and-spoke: Travel Routes primary + 4 spokes (Cheat Codes, Tourist Mistakes, Thailand Costs, Route Intelligence). 6-platform distribution (TikTok, IG Reels, FB Groups-first, YT Shorts+Long-form, Pinterest new). Top keyword: $54.11 CPC on "hat yai airport to koh lipe". Route Demand Index identified as data moat. Plus 3 atom notes: `03-knowledge/keyword-research-routes.md` (4 CSV reference index for Bangkok-Samui / Chiang Mai / Hat Yai-Lipe en-th / Langkawi-Lipe) and 2 image reference notes (`business-development-new-site-diagram.md`, `business-development-new-site-idea.md`) linking to PNG assets. Index Areas + Knowledge Domains updated.

## [2026-06-03] ingest | business-development-thesis — SmartEnPlus strategic thesis created at `/Users/charuwatnaranong/Desktop/SmartEnPlus/business-development/business-development-thesis.md`. Condensed to vault note at `02-areas/business-development-thesis-2026.md`. Index + business.md updated. Key thesis: "Thailand's Travel Commerce Platform" — own travel connectivity not inventory. Four-phase growth model: revenue per traveler → retention → AI intelligence → journey commerce. B2B+B2C distribution.

## [2026-06-03] session-end | #38: guard contract.trip=None in AdminBookingSummarySerializer. Branch 260603-fix/booking-summary-trip-none-guard pushed to backend, needs merge.

## [2026-06-03] fix | copy-cartitem-trip-none-guard — `carts/utils.py:copy_cartitem_to_bookingitem()` crashed `contract.trip.route` when `trip=None` (DAY_TOUR etc.). Guard added. Atomic note: [[copy-cartitem-trip-none-guard]]. Also: Confirmation.js:111,115 guarded (`formData.passengers?.length ?? 0`, `|| []`).

## [2026-06-03] session-end | #37 — non-transport trip=None full flow fix complete (code done, uncommitted)

**Fixed:** 9 files across 2 repos. All crash sites on checkout→payment→order→booking path guarded. ContractSerializer extended with 10 non-transport fields (general_information, cancellation_policy, image gallery, tour_highlights, inclusions, exclusions, what_to_bring, difficulty_level, duration, instant_confirmation, mobile_ticket_enabled, meeting_point_type/details). ServiceTabbedInfo.js: `refund_hours` field fix + `?.description` guard.

**Vault:** [[contract-serializer-non-transport-fields-2026-06-03]] created. [[checkout-confirmation-payment-crash-2026-06-03]] updated with full fix table. master-state updated.

**Next:** Restart Django → test `/bookings/JOH4017133` → commit both repos → merge develop. Then back to CART-1/FAQ-1/AT-1.
## [2026-06-03] bug | checkout-confirmation-payment-crash — `formData.passengers.length` unguarded in `Confirmation.js:111,115`. Crashes for non-transport items at Confirmation step. Reproduction steps in [[checkout-confirmation-payment-crash-2026-06-03]]. Fix pending.

## [2026-06-03] session-end #36 | checkout null-contract sweep complete — 4 fixes shipped to production. Passengers.js info_fields + trip header + index.js render-root guards + FormCard button height unified h-12. Full scan vault: [[checkout-null-contract-scan-2026-06-03]].

## [2026-06-03] session-end #35 | checkout crash FIXED — `contract.trip=null` for non-transport items (DAY_TOUR/SPA/EVENT) crashed `hasPassedAdvanceHour` + `hasStopSaleDate` at render root. 3-line guard added `pages/checkout/index.js`. Commit `43b7ece`. Atomic note: [[contract-trip-null-non-transport-pattern]].

## [2026-06-02] session-end #34 | cartitems-500 FIXED — `contract.trip=None` → AttributeError in check_advance_hour(). carts/utils.py:591 null guard + call-site exception wrapper. Frontend: info alert removed + 4 console.logs cleaned. Original vault analysis corrected (Bug 1/2 false alarms). CART-1 deferred.

## [2026-06-02] bug | cartitems-500-error — 3 root causes: stale initialContract ratecard IDs, undefined contract_ratecard (pk/id mismatch), PARSING_ERROR not caught by error handler. Fix plan in [[cartitems-500-error-analysis-2026-06-02]].

## [2026-06-02] session-end #30 | Price range slider max hardcode fixed — 10,000→30,000 THB in ExperienceSidebar.js:9. Multi-agent debate (3 specialists): dynamic endpoint vs 50k vs 30k. 30k won: matches Thai market ceiling, 40% better slider precision for 500–8k density band. Uncommitted. Next: commit price fix → merge header-activities-search → AT-1.

## [2026-06-02] session-end #29 | Backend min_rate ordering fix + activities sort/filter UX redesign. Fixed: FieldError on `ordering=min_rate` without price filter (annotation hoisted). Frontend: SORT_OPTIONS shared constant, active sort chip (SortBar), mobile sort bottom-sheet, outlined buttons with state-driven emphasis. UX pattern: hierarchy via content not color (9/10 travel app standard). Committed 1c94110 (backend) + 8f05ab3 (frontend). Knowledge atomized: [[activities-sort-filter-ux]]. Next: merge header-activities-search → AT-1 airport transfer P0.

## [2026-06-02] session-end #27 | ACT-12 fully resolved — 4 commits pushed (979c45d→5eaf8e2). Fixes: dual-hook URL race (isControlled + enabled param), debounce (reused useDebounce.jsx), mid-type reset (isTypingRef + didMountRef), freeSolo Enter blank (string branch in handleChange). Knowledge atomized: [[react-dual-hook-url-race]]. Branch ready to merge. Next: merge → BW-1/2/3 blog padding → AT-1 airport transfer.
## [2026-06-01] session-end #26 | ACT-12 partial — flicker fixed (HeaderSearchContext shallow guard), Option F (routeChangeComplete) introduced 2 regressions (race condition + mid-type inputValue overwrite). 4 files modified uncommitted. Next: revert useDayTripFilters Option F, implement Option E (pass page filters+updateFilter to compact).
## [2026-06-01] scrutinize | ACT-12 root cause confirmed + original hypothesis overturned — kill chain: compact useDayTripFilters router.push(shallow) → routeChangeStart → HeaderSearchContext clears. Fix: 2-line shallow guard in HeaderSearchContext. Change 2 (readOnly) = unnecessary. Plan file + master-state updated.
## [2026-06-01] session-end #25 | ACT-10+11 done, ACT-12 open. Phase 2+3 merged develop (b552e55, f93df66, 2d5a6ee). Header activities search partial — flicker bug unresolved. Branch 260601-feat/header-activities-search (1cbec0f). Bug report + 3 next approaches in master-state Section 4 ACT-12.
## [2026-06-01] bug | header-activities-search flicker — setSearchBarContent called, search shows briefly then disappears. Hypothesis: useEffect cleanup fires on re-render loop triggered by context state update. 3 approaches for next session documented in master-state.
## [2026-06-01] session-end | Phase 1 activities marketplace shipped — 4-agent review resolved 7 blockers, backend avg_rating annotation (14b2368), frontend Phase 1 c669381 (sidebar+card+sort+wishlist), width fix b86da09. Next: QA + merge both branches.
## [2026-06-01] review | experiences-2026-marketplace-redesign — 4-agent team (UX/Frontend/Backend/Design) audit. 7 blocking issues + 9 high-priority gaps found. All resolved: sidebar 280→240px, 4-col viable, sort options trimmed to 3 for Phase 1, `-average_rating` needs ORM annotation, `booked_count` legacy documented, hover animation fix, Phase 2 pre-flight checklist added. Doc updated.
## [2026-06-01] lint | atomized 5 concepts from 3 notes — design-token-caption-tailwind-gotcha, mui-autocomplete-inputvalue-sync, django-parse-int-list-text-fallback, pdf-contract-import-adversarial-review, django-async-ai-call-pattern. Source files trimmed: day-tour-review (269→~235), location-search-bug (259→~230), pdf-contract-import (508→~370).
## [2026-06-01] plan | experiences-2026-marketplace-redesign — 4-phase plan. Phase 1: sidebar+card+sortbar (frontend only). Phase 2: backend filter params. Phase 3: mobile. Phase 4: iPad. 6 decisions documented, codebase map complete.
## [2026-06-01] session-end | unified ActivitySearch shipped — ACT-5+ACT-6 done. utils/destinations.js canonical source, ActivitySearch fetches backend locations via GET /api/v1/contract/locations/. Frontend 02f9adf + backend 0b4b44f pushed. Backend branch needs merge first, then frontend QA + merge to develop.
## [2026-06-01] session-end | activities browse fixes shipped — 11 fixes (FQ-0→DS-1 + LAY-1 + LAY-2), commit 09e0db3, pushed 260601-fix/activities-browse-audit. Layout audit doc created. Next: QA then merge to main.
## [2026-06-01] audit | layout-spacing-consistency — activities vs homepage vs trips. 3 issues: LAY-1 h-padding wrong (p-2 → px-4 xl:px-0), LAY-2 grid spacing mismatch (loaded spacing=1 → spacing=2), LAY-3 sm:py-8 intentional exception. Vault: 03-knowledge/layout-spacing-consistency-audit-2026-06-01.md
## [2026-06-01] session-end | activities page audit complete — 3-specialist + grill + scrutinize. 14 findings (3P0/6P1/5P2). P0 bug: inactive contracts in browse (status=active param missing). 4 scrutinize corrections applied. Branch 260601-fix/activities-browse-audit ready. master-state updated.
## [2026-06-01] scrutinize | activities-day-tour-page-review — 4 wrong claims corrected: FQ-4 symptom (PricingDisplay guards price≤0), UX-2 TRANSFER absent frontend, FQ-1 title (grid OK, anatomy wrong), DS-1 fix path (caption=Tailwind string not fontSize). FQ-2 elevated to router.isReady fix.
## [2026-06-01] grill | activities-day-tour-page-review — FQ-0 P0 found: inactive contracts in browse. DS-1 P1: design token gaps (minHeight, caption fontSize). Constraints: no over-engineering, reuse only, simple fixes.
## [2026-06-01] audit | activities-day-tour-page-review — 3-specialist code audit (UX+Design+FE). 12 findings: 2 Critical, 5 Major, 5 Minor. Top risks: skeleton mismatch, dual search inputs, non-experience categories in filter, spurious router.push on mount.
## [2026-06-01] research | pdf-contract-import — full grill session. Architecture locked: NotebookLM → Django (GLM/MiniMax) → ContractImportDraft → admin review → PATCH. Parked for future implementation. Vault: 03-knowledge/pdf-contract-import-research.md
## [2026-06-01] audit | timeline-update-display-bug — audit doc created. 4 suspected root causes: payload key mismatch, place shape mismatch, response race, empty place ID. Team investigation pending.
## [2026-06-01] session-end | build error fix: pages/help/index.js const index → HelpPage, react-hooks/rules-of-hooks ESLint error. efb59d7 pushed to main. Atomic note: react-hooks-rules-lowercase-component.
## [2026-05-31] session-end | seo audit: 7 fixes applied one-by-one on `260528-feat/header-redesign-2026`, CSP identified as runtime breaker, all verified OK, pushed `a2a4ff9`. Vault updated. Open: contactPoint, departureTime/arrivalTime.
## [2026-05-31] scrutinize | seo-homepage-audit-2026-05-31 — 2-agent scrutiny: P0-1 REFUTED (next-sitemap.config.js line 10 is empty array, no server-sitemap.xml reference, no active 404). P1-4 clarified: FAQPageJsonLd component exists, not wired to homepagev2. All P2/P3 confirmed correct. Fix queue verified accurate. Doc updated.
## [2026-05-31] audit+fix | css consistency: 13 commits on `260528-feat/header-redesign-2026`. All browse pages fixed: destinations, locations, trips. Card border-radius, padding, grid gaps, section padding, card bg, back/share overlay added to trips. Pushed to remote.
## [2026-05-31] session-end | blog width audit + partial fix: BlogPostDisplay 4 fixes (section padding, article width lg:w-full, engagement bar px-, duplicate breadcrumb removed). Audit doc committed 73af6e9. BW-1/BW-2/BW-3 pending. Vault updated.
## [2026-05-31] session-end | carousel 4-card desktop fix: xl:w-[284px] on PopularRouteImageCard + ExperienceCard. 4×284+4×16=1200px. b104962 pushed. PR-2 closed.
## [2026-05-30] debug | hero back/share buttons: 3 root causes found (wrong prop name, wrong containing block, dynamic loader chain breaks showActions). Buttons moved to TripDetailHero/DayTripHero outer wrapper. Glassmorphism pill style. UNVERIFIED — server in production mode. Resume: npm run dev first.
## [2026-05-30] post-mortem | FeaturedImageHeader width bug: w-[1200px] hardcoded in 0ebd755 broke mobile. Fix: w-full + max-w-[1200px]. Vault note created.
## [2026-05-30] session-end | EXP-1 implemented: PopularExperienceSerializer + ExploreExperiencesSection + ExperienceCard. 27 contracts. Backend 4ab5771, frontend f27f077. Master-state Section 1-3 updated, EXP-1 moved to closed.

## [2026-05-30] session-end | vault-only session. Experiences section feasibility: 3-agent research + scrutinize (3 wrong claims fixed) + grill (all decisions locked). EXP-1 added to loose ends. No code changes.

## [2026-05-30] grill | homepage-experiences-section-audit — all design decisions locked: skip rating (N+1), hide booked_count (default=10 misleading), card=title+category+price, image=imagegallery_set S3, serializer=standalone ModelSerializer, prefetch_related imagegallery_set.

## [2026-05-30] scrutinize | homepage-experiences-section-audit — 3 critical wrong claims fixed: featured_image missing on Contract (use ImageGallery), service_category list incomplete (TRANSPORTATION/ACCOMMODATION missed), HomeSerializer wrong copy template (use ContractSerializer). Vault doc updated.

## [2026-05-30] audit | homepage-experiences-section — 3-agent feasibility team (frontend+backend+vault). Verdict: VIABLE after AT-1. Backend ready, no new models. 5 files ~160 lines. Inventory gate required. Vault doc created.

## [2026-05-30] session-end | Airport Transfers section redesigned — Omio-style route cards with real pricing from backend. Backend airport_routes API added. Data shape bug fixed (StationSerializer shadow). Style audit 8 fixes. 1eec0aa + 3759dc2 pushed. Atom extracted: django-serializer-shadowing-pattern.

## [2026-05-30] session-end | Width consistency audit + sort dropdown fix.3-agent team (header/sections/live-verifier). Root cause: w-full + max-w-[1200px] = full viewport. Fix: explicit w-[1200px] on hero absolute div. Sort dropdown inline with title row. AirportTransferSection commented out pending AT-1. 0ebd755 committed.

## [2026-05-29] session-end | added Ask Away + Explore More to ProfileMenu (auth+guest), removed CustomerServiceSection from homepage. 7650f3c pushed.

## [2026-05-29] session-end | ProfileButton redesign complete (dac7e66) + next/image hostname fixes (help/blog). Pill trigger single-line, guest path fixed, MUI-preserve, bottom sheet mobile.

## [2026-05-29] decision | profile-dropdown-redesign — 3-specialist team (UX+UI+Frontend). 11→6 items, 296px, pill trigger, bottom sheet mobile, 3-file split, MUI-preserve. Vault doc created.

## [2026-05-29] session-end | homepage visual consistency audit + Check Your Booking UX redesign (trust badges, header position, copy)

## [2026-05-29] decision | check-your-booking v2 — reference image 2-column layout adopted. Judge: fb-blue not indigo, Order ID text link not tab, "Check" not "Manage", gap-4 not gap-6. v1 centered card rejected by user.

## [2026-05-29] decision | check-your-booking v1 — OTA utility card adopted (superseded by v2). 3-agent debate (FOR/AGAINST/JUDGE). Illustration removed, 840px card, warm-surface bg, inputs upgraded, eyebrow removed per judge, trust row copy fixed.

## [2026-05-29] session-end | homepage visual refinement: Popular Routes cards stronger, guides section renamed, reviews CTA removed, destinations grid fix reverted to 5 cards, sitewide width deferred

## [2026-05-29] create | travel-thailand-better-section-redesign — 3 editorial sections → 1 unified section. 1 featured + 2 secondary card layout. Spec ready, implementation pending.

## [2026-05-28] ingest | carousel design standard + popular routes fix: vw-based card widths, embla DOM structure, focus ring handling, items-per-screen table across 5 breakpoints

## [2026-05-28] vault-lint | 16 orphan docs analyzed. 9 hero files merged → 1 comprehensive audit. nav-header-redesign merged into existing (richer content). isr-stale-data merged into isr-429 fix doc. 5 files indexed + cross-linked (mobile-header, wireframe-architecture, uxui-research, trip-detail-deep-review, trip-detail-page-review). 11 files deleted. Index: 57→61 pages.

## [2026-05-28] vault-atomize | 5 atoms extracted from 3 source docs: hero-88px-gap-root-cause ← hero-audit, featured-image-header-usage-matrix ← hero-audit, smartenplus-product-positioning ← wireframe-architecture, smartenplus-2026-ux-direction ← uxui-research, mobile-header-scroll-behavior-change ← hero-audit. Index: 62→67 pages.

## [2026-05-28] session-end | homepage redesign 2026 implemented — commit 96bc6f9. Color tokens #1E40AF, Inter font, hero removed, DiscoverySection live, PopularRoutes polished. TrustRow + RouteChips removed per user. QA + merge next session.
## [2026-05-28] session-end | header redesign Days 1–3 complete. Branch 260528-feat/header-redesign-2026 a4158b0. Day 4 QA + merge next session. Context 48% at wrap-up.
## [2026-05-28] session-end | header redesign Days 1–3 implemented — branch 260528-feat/header-redesign-2026 commit a4158b0. Glassmorphism removed. Solid white header. 10 files. HeaderRowsContext live. Day 4 QA + merge pending.
## [2026-05-28] create | header-redesign-2026-implementation — handoff doc with full change log, architecture notes, QA checklist, remaining work
## [2026-05-28] update | header-redesign-2026 FINAL — Type A/B adaptive split locked. /blog → Type B. Keep all 5 nav items (Explore Thailand stays). Dynamic layout offset 80/96px. HeaderRowsContext for StickySearchBar. 12 files, 4-day impl + 2 separate PRs. Spec + team-review both updated.
## [2026-05-28] review | header-redesign-2026-team-review — 3-specialist audit (Design+UX+Frontend). 10 files not 5. 4 missing components (SearchDialogTrigger, CartButton, ProfileButton, NavDropdown). 2 open decisions (rows prop, mobile scroll hide). Full color map + regression matrix written.
## [2026-05-28] session-end | 2026 header redesign spec — revert merge c6d7248 (header-search-bugs), full solid-white header design brief written (HEADER_REDESIGN_2026.md + vault doc header-redesign-2026-spec.md). 5-file impl plan ready. Not yet implemented.
## [2026-05-27] create | mobile-header-redesign-glassmorphism — design spec for premium glass mobile header (solid blue → cinematic glassmorphism, always-fixed, scroll-reactive opacity, currency pill mobile variant, hero bleed pattern)
## [2026-05-27] session-end | header scroll opacity fix — root cause: CSS transition asymmetry (.glass-bg had 300ms, .glass-bg-scrolled had none) → asymmetric smooth/jarring on scroll direction change. Fix: added 200ms transition to .glass-bg-scrolled + reduced 300ms→200ms. Also removed scroll-based class toggle — desktop header always dark glass-bg-scrolled. Investigation: 1 agent (debug-specialist), 3-layer deep trace. No code pushed.
## [2026-05-25] session-end | passenger CSV export — added 6 columns (Passenger Names, Passport IDs, DOBs, Adults/Children/Infants Count). Hotfix: datifbirth→datofbirth, rate_type→attribute. Committed to feat/passenger-csv-export→develop (pushed), merged to main (user pushes manually).
## [2026-05-25] plan | premium-glassmorphism-header — team analysis (glass-auditor + hero-reviewer + scroll-specialist). Decision: Option A unified glass (both rows identical dark gradient, no divider). Remove Slide, use sticky + threshold scroll + CSS transitions. FeaturedImageHeader overlay reduction needed. Report: 01-projects/smartenplus-glassmorphism-header.md. index.md updated.
## [2026-05-25] session-end | nav redesign Phases 0-2 done + Phase 3 backend+frontend code complete. Label renames (5), Experiences dropdown, Explore Thailand dropdown + URL param, NavigationSection+NavigationItem models (0010 migrated), NavigationViewSet with cache, Django admin inline, RTK Query nav endpoint with fallback. Blocked: /pages-info/navigation/ 404 (server restart needed), NavigationSection data not populated. 3 bug fixes: api-slice path, /api/v1 prefix, React key in PopularRoutesCarousel+CardCarouselContainer. Branches: frontend 260524-feat/nav-label-changes, backend 260525-feat/nav-api-endpoint.
## [2026-05-24] plan | nav-header-redesign — 3-phase dropdown plan (UI scaffold → URL param enhancement → backend data). 3-agent audit (UX, SEO, Mobile) found: URL param links broken on /destinations, /locations, /trips (no router.query reading); mobile drawer flat list, no accordion; navLinks/menuLinks separate arrays; CategoryMenu.js wrong pattern for mobile accordion. Revised plan ready. Vault doc: nav-header-redesign-2026-05-24.md
## [2026-05-24] validate | nav-header-redesign — 6-agent validation (component-audit, pattern-specialist, implementation-critic) converged: Phase 1 dropdown over-engineered, label changes only is better Phase 0. All submenu links go to same base page (URL params don't work). Only Experiences dropdown works immediately (via /activities?category=). Mobile accordion deferred (stopPropagation a11y trap, focus management complexity, 7 extra mobile items product decision needed). Phase 0 label changes: 15 min, zero risk. Plan finalized. Vault doc updated.
## [2026-05-24] session-end | content marketing playbook rewritten — 5-agent review, 6 contradictions fixed, keyword CSV analysis, tech stack + real URLs integrated. No code changes to dev repos.
## [2026-05-24] session-end | auth pages noindex fixed — NextSeo moved outside ProtectedComponent on /bookings + /orders. 4209def pushed to main → production. All SEO wave-2 issues resolved.
## [2026-05-24] session-end | strategic direction grill complete — no code changes. Vault updated + pushed 6ba72e8. Next: auth pages noindex fix.
## [2026-05-24] ingest | strategic direction validated via grill — B2B/B2C split confirmed (90/10), EN customer confirmed (GA4+support), Malaysia Phase 2, vertical integration moat (minivan network+own tours), Stippl product vision, revenue model = markup not commission
## [2026-05-24] cleanup | deleted master-state.original.md (stale 2026-05-22 backup) + breadcrumb-dedup-plan-2026-05-20.md (work done, plan doc misleading): docker-standalone-isr-revalidate-gap, on-demand-revalidation-api-route, celery-task-over-bare-thread-django-signals, isr-csr-overlay-stale-fields, persistgate-ssr-suppresses-head-component, webpack-image-src-og-absolute-url-rule. isr-stale-data-audit (344→36L) + seo-wave2-audit (282→32L) trimmed. index.md updated. log.md appended.
## [2026-05-23] deploy | PersistGate SSR fix merged → develop df81b19 → main → production live 2026-05-23
## [2026-05-23] session-end | seo-wave2 — all 11 bugs fixed, merged to main. Auth pages noindex blocked by ProtectedComponent returning null SSR (fix deferred). Vault updated. Main merged, not pushed (user held).
## [2026-05-23] session-end | PersistGate SSR blocker fixed — all OG meta tags restored site-wide; OG image relative paths fixed in seoHelper.js + trips/index.js; NEXT_PUBLIC_SITE_URL tech debt reverted; branch 260523-fix/trips-og-image-and-site-url-env (4 commits: 61134c9, f8d9907, 4644fac, ac6f8aa) — merged → main → production
## [2026-05-23] session-end | og:image:secure_url site-wide — 24 files, homepage domain fallback, generateBlogSEO() updated, merged → main 190e2a2; verified live
## [2026-05-23] scrutinize | og-image-inferred — fix plan corrected: homepage use inline 3-tier fallback (not getSiteUrl() cross-module import); blog use generateBlogSEO() helper (not N inline copies); search page has seo object already (not blank slate); vault doc updated
## [2026-05-23] audit | og-image-inferred — site-wide Facebook og:image warning; RC1: NEXT_PUBLIC_DOMAIN undefined in prod → homepage Seo crash; RC2: missing secureUrl on blog pages; vault doc written; fix pending
## [2026-05-23] session-end | og:image Facebook "inferred" warning fixed — hardcoded 1200×630 + missing secure_url in BlogPostHeader.js; 1dd9d01 pushed to main
## [2026-05-23] audit | isr-stale-data — ISR revalidate:300 broken in Docker standalone; Django signals clear Redis but never notify Next.js; on-demand revalidation API route proposed (Option A over B/C/D); **2 blockers + 3 major findings from team scrutinize — reword before implementing: (1) revalidate.js doesn't exist, (2) network path unverified, (3) daemon thread → use Celery instead, (4) consider revalidateTag, (5) root cause conflates 2 different issues**
## [2026-05-23] audit | fast-refresh-infinite-loop — 7 fix attempts failed; RefreshTokenHandler diagnosis OVERTURNED by scrutiny (lastExpiryRef guard blocks loop); actual cause likely Next.js 14.2.x HMR + on-demand compilation cascade (self-terminating); git bisect + debug instrumentation recommended; CurrencyContext fix applied
## [2026-05-23] audit-draft | fast-refresh-infinite-loop — 7 fix attempts, RefreshTokenHandler Date.now() + state loop identified by 3 agents; CurrencyContext fix applied; vault audit doc written
## [2026-05-23] session-end | infinite fetch investigation — circular-dep theory overturned; Fast Refresh reload loop (hot-update 404) + CurrencyContext race condition identified; vault doc written; no code changes; items #16+#17 added to loose ends
## [2026-05-23] scrutinize | currency-context-infinite-fetch — initial circular-dep claim overturned; actual cause: Fast Refresh full-reload loop (hot-update 404) + CurrencyContext race condition; doc updated with correct trace + 2-step fix order
## [2026-05-23] deploy | frontend + backend pushed to main — 429 fix (67cdf66) + auth dep fix (da3c2b1) now in production
## [2026-05-23] session-end | migration audit — locked_amount chain 0038→0042 verified intact on develop; no changes made
## [2026-05-23] session-end | 429 fix + auth dep fix — 3-agent team review caught flat cache key bug; parameterized key + no DEBUG guard; Fix A merged backend 67cdf66, Fix D merged frontend da3c2b1, both pushed origin/develop
## [2026-05-23] rework | isr-429-cold-start-fix — scrutiny overturned 2 false claims: REVALIDATE_SECONDS irrelevant in dev, getStaticPaths build-time only; actual cause: DRF anon 500/hour window persists across runserver restarts; fix = backend response cache on FrontPageViewSet.list; nextjs-patterns.md corrected
## [2026-05-23] ingest | isr-429-cold-start-fix — cold start 429 on /front-page/ diagnosed: REVALIDATE_SECONDS=60 + refetchOnMountOrArgChange:300 + props-in-deps; 3 fixes identified; nextjs-patterns.md ISR+RTK rules updated
## [2026-05-23] feat | rename /daytrips → /activities complete — 7 phases, 5 scrutiny fixes (v4/v5 migration gap, duplicate [slug].js route, git rename detection, SEO title, test pathname), merged → develop d424d4e; post-deploy: clear smartenplus_next_cache + resubmit GSC sitemap
## [2026-05-23] ingest | daytrips-to-activities-rename — 3-specialist team review, unanimous `activities`, 51 files mapped, 9 critical risks documented, cart/payment flows confirmed safe; branch 260523-feat/rename-daytrips-to-activities created
## [2026-05-23] session-end | vault optimization — synopsis atom note created, 26 files caveman compressed (139KB→128KB, 7% reduction), 12 old backups + 3 empty stubs cleaned; all 3 repos unchanged
## [2026-05-23] optimize | caveman:compress — 26 files compressed (139KB→128KB, 7% byte reduction); 3 empty stubs deleted; 37 .original.md backups retained for rollback
## [2026-05-22] ingest | smartenplus-synopsis — project-wide synopsis atom note created; 12 .original.md backups cleaned
## [2026-05-22] session-end | trip detail width/gap/rounded consistency — RelatedTripsSection my-0→my-2 + rounded-md, breadcrumb padding confirmed px-2 md:px-3; merged → develop → main → production
## [2026-05-22] session-end | trips filter page gap+rounded consistency — gap-3 sidebar↔results + cards, rounded-lg unified across filter bar/sort/table; 4da9175 pushed to main
## [2026-05-22] session-end | section width unification on /trips filter+detail pages — mx-2 md:mx-3 xl:mx-0 pattern applied to calendar, filter bar, sidebar, cards, overview, summary, blog post; SlideCalendar2 className prop added; e7345ea on main (not pushed)
## [2026-05-22] session-end | blog hero-breadcrumb gap unified via BlogPageWrapper flex restructure; CategoryMenu moved to hero actionButton + styled to match back/share buttons (bg-black/25 white); all pages gap-2; 260522-fix/trip-detail-ux merged → develop
## [2026-05-22] session-end | site-wide style consistency + breadcrumb gap standardization — 8px rhythm across all pages; removed mb-6/py-2 from 35 files; ContentCard rounded-md, typography gray-900, gap-1→gap-2 filters; branch 260522-fix/trip-detail-ux uncommitted
## [2026-05-22] session-end | trip detail UX/UI audit + all P1 fixes done; branch 260522-fix/trip-detail-ux ready for PR to develop
## [2026-05-22] fix | trip-detail-uxui — 32 issues found+implemented: ContentCard wrappers, h1 text-sm, z-5→z-10, text-md phantom, pb-16, CLS fallbacks, booking bar a11y; branch 260522-fix/trip-detail-ux (3 commits)
## [2026-05-22] session-end | created trip-detail-uxui-auditor agent — 3-specialist team, 32-item checklist; deep width/margin audit confirmed Section/ContentCard absent from entire trip detail tree; calendar fix = wrap at page level; fixes pending
## [2026-05-22] session-end | homepage SEO audit all 30 findings done + AI misclassification 6 fixes; both merged to develop; next: backend #4 locked_amount + useTripSEO TouristTrip audit
## [2026-05-22] fix | ai-classification — /bookings unblocked robots.txt, BusTrip @type, Service schema, llms.txt, hasOfferCatalog on TravelAgency
## [2026-05-22] fix | homepage-seo-p1 — aggregateRating live, sameAs, lastReviewed, WebSite schema, DefaultSeo, og/twitter, logo, geo fix, preconnect, CLS, hero crossfade
## [2026-05-22] session-end | P0 SEO fixes done on branch 260522-fix/homepage-seo-p0; next: P1 fixes (aggregateRating, sameAs, DefaultSeo, Seo.js og) then merge + backend #4
## [2026-05-22] fix | homepage-seo-p0 — fake phone replaced, fake address removed (taxID added), server-sitemap.xml 404 hotfix, robots.txt policy merged
## [2026-05-22] ingest | homepage-seo-performance-deep-review — 3-specialist audit, 30 issues (3 critical, 11 major), P0: server-sitemap.xml 404 + fake phone/address in TravelAgency schema
## [2026-05-21] session-end | SEO specialist team built — agent + vault doc created; team NOT yet run; next: run review then P0 fixes + backend #4 locked_amount
## [2026-05-21] ingest | seo-homepage-specialist-team — agent created (seo-homepage-auditor.md), vault knowledge doc added, 10 pre-identified SEO gaps documented
## [2026-05-21] session-end | homepage UX/UI review doc fully cleared P0-P3; #1 trip-seo→main user handling; next: backend #4 locked_amount constraint
## [2026-05-21] session-end | homepage P1+P2+P3 fixes complete — 3 branches merged to develop, booking ID format corrected (ABC1234567 not BK prefix), P4 deferred
## [2026-05-21] session-end | homepage UX/UI review (3-agent, 11 sections) + scrutinize corrections applied — vault 52 pages, frontend on 260521-fix/trip-seo-usd-hardcode PR open
## [2026-05-21] scrutinize | homepage-ux-review — 3 corrections: IATA claim wrong (capitalizeWords preserves uppercase), DOMPurify SSR risk (use isomorphic-dompurify), help links also missing leading slash (line 46, not just forum line 83)
## [2026-05-21] ingest | homepage-ux-review — 3-agent UX/UI review, 11 sections, 4 critical (XSS, hero VP, search validation, location title) + 34 major + 15 minor; section reorder recommended
## [2026-05-21] session-end | useTripSEO USD /30 hardcode fixed (49e6f17) — PR open on 260521-fix/trip-seo-usd-hardcode
## [2026-05-21] session-end | /lint-vault first run — 6 atoms extracted; vault 51 pages, all 3 repos clean on main
## [2026-05-21] lint | /lint-vault run — 6 atoms extracted: payment-sentinel-idempotency, nextauth-session-shape, cart-reprovision-after-reset, promptpay-no-webhook-on-expiry, nextjs-isr-ratecard-empty-array-guard, nextjs-307-vs-301-product-reclassify
## [2026-05-21] session-end | atomic notes system shipped — auto-atomize in wrap-up + /lint-vault command; vault bd2fc03 pushed
## [2026-05-21] ingest | atomic-notes system — auto-atomize on wrap-up (Step 5) + /lint-vault command; atomic-note template + atomic-notes rules doc created
## [2026-05-21] session-end | Popular Routes image carousel (edccb75) — CardCarouselContainer extracted, BlogCardContainer refactored, 4-card responsive layout pushed to PR
## [2026-05-21] session-end | header/footer alignment + icon normalization merged to develop→main (e67379f). All 3 repos clean on main.
## [2026-05-21] session-end | trip detail H3 fix — fetchData 8s timeout for blocking fallback SSR (c39f83c) + H1/H2 verified already fixed — merged to develop + main
## [2026-05-21] session-end | trip detail quick-wins — 9/10 already done, 2 applied (console.log→warn, dead __dataSource branch) — b866f6c merged to develop + main
## [2026-05-21] session-end | homepage full consistency audit + design system sync — 6 fixes (footer typo, booking section brand colors, Guides double-nav, Reviews error color, hero stray class, design system hex/config) — 260520-update/frontpage merged to develop + main
## [2026-05-21] session-end | frontpage style consistency — section card rounded+margin+overflow-hidden, footer bg-fb-blue full-width, 2 commits pushed on 260520-update/frontpage
## [2026-05-20] session-end | help icon mobile fix round 2 (revert MUI sx → Tailwind div), vault updated with Emotion cache provider lesson
## [2026-05-20] fix | Help icon mobile — reverted MUI Box sx responsive breakpoints (need Emotion cache), use Tailwind div wrapper per existing pattern
## [2026-05-20] session-end | all repos merged to develop, breadcrumb dedup merged, forum table width fixed, MUI+Tailwind knowledge doc — 12 commits on frontend, vault updated

## [2026-05-20] session-end | MUI+Tailwind CSS fixes, trip detail 4 fixes, breadcrumb dedup branch — hero button sx color, help icon MUI Box breakpoint, breadcrumb SSR, redirect 308, scroll rAF, reviews fetch removed; pushed to origin

## [2026-05-20] ingest | mui-tailwind-css-specificity.md — MUI Emotion CSS overrides Tailwind className on MUI components; root cause + fix patterns (sx prop, div wrapper) + property-by-property guide; affects IconButton, Button, SvgIcon

## [2026-05-20] ingest | breadcrumb-dedup-plan-2026-05-20.md — 16 files across 3 groups; GROUP B (10 section/div), GROUP C (4 padding-only), GROUP D (2 section/py-0); 8 already correct; 5 skipped (context-dependent)

## [2026-05-20] session-end | blog index 2 fixes (1e34601) + HMR hot-update 404 fix (b56d62a) — H1 visible on mobile, Load More filled button, next.config.js Cache-Control narrowed to chunks/css only; PRs still pending

## [2026-05-20] session-end | build errors fixed + ssr:false removed + reviewer artifact deleted — calculateAge exported (96c9c10), dead getStaticProps re-export removed, DynamicReviewListByProduct ssr:false dropped (3f948bf), build clean; PRs still pending

## [2026-05-20] session-end | trip detail 16 fixes + recommend-route all committed; PRs pending — 3-agent review (24 issues) + 4-agent adversarial deep review (8 hidden); 10 quick-wins (3f35d8c) + 6 deferred fixes (0bf038d); recommend-route frontend (2434124) + backend (3e49644) committed; PRs not opened yet

## [2026-05-20] ingest | trip-detail-deep-review-2026-05-20.md — 4-agent adversarial pass; 3 original findings overturned (P2 isClient, S1 307→301, C4 typo); 8 hidden issues; top 3 risks: ratecard wipe crash, fetch timeout 500 loop, invalid ISO8601 TouristTrip schema

## [2026-05-20] ingest | trip-detail-page-review-2026-05-20.md — 3-agent review of pages/trips/detail/[...slug].js; 24 issues (8 perf, 8 SEO, 8 code quality); verified against actual code, false positives removed

## [2026-05-20] session-end | dashboard Main.js RTK Query migration (c06af90) — 3-agent review team, 12 useState→0, raw axios→RTK Query, shadowed import+memory leak+mock trends fixed, new dashboardApi.js slice, 334→170 lines; updated admin-dashboard-component-patterns.md, master-state.md

## [2026-05-20] session-end | Popular Routes admin page committed (beaf1a7) — read-only DataGrid consuming GET /admin-dashboard-routes/home/; backend+frontend recommend-route changes still uncommitted; updated recommendation-system.md, master-state.md, index.md

## [2026-05-20] session-end | hydration infinite refresh fixed — 4 files (_app.js dual-tree, PopularRoutesStructuredData Date.now, GridComponent useCallback, CurrencyContext useMemo); agent ~55% accuracy; backend+frontend still uncommitted on 260520-update/recommend-route

## [2026-05-20] session-end | forex 429 fix (backend c859f3b + frontend ff1f378) + admin HeroBanner UI committed (d3194d8); all 4 repos clean + pushed

## [2026-05-20] session-end | blog perf/SEO round 2 (6b655d6) — parallel fetches, image fixes, HMR infinite loop fixed; admin HeroBanner UI still uncommitted

## [2026-05-19] session-end | blog SEO fixes + perf optimizations committed (0f38cf8); admin HeroBanner UI still uncommitted

## [2026-05-19] ingest | DAYTRIP_DOCUMENTATION_SUMMARY.md — deleted from vault root, replaced with tour-system-status.md

- Source was a 2026-03-03 meta-index pointing to 36 repo docs. Low vault value — repo already has `docs/tour-system/INDEX.md`.
- Deleted: `DAYTRIP_DOCUMENTATION_SUMMARY.md` from vault root (wrong location, stale counts, just a directory map)
- Created: `01-projects/tour-system-status.md` — Phase 2 open gaps, trust signal fields, pointer to authoritative repo docs
- Core facts still valid: Contract/TimeSlot/ContractAddon/ContractTranslation models intact. 46+ commits since doc date — test/contract counts stale.
- See [[tour-system-status]], [[operators]]

## [2026-05-19] session-end | built vault session system — init/wrap-up protocols, master-state.md, optimized CLAUDE.md + master-state.md

## [2026-05-19] system | master-state.md created — mission control / session handoff

- New file at vault root alongside `index.md` and `log.md`. Partitioned by change frequency.
- Section 1 (every session): active branches, uncommitted changes, next step, last worked on.
- Section 2 (weekly): open loose ends, in-flight features, recently closed bugs.
- Section 3 (monthly): cross-repo API contract, auth rules, data shape gotchas, payment constants.
- Section 4 (rarely): architecture guardrails — lock order, payment rules, Celery patterns, heal commands.
- Updated `index.md` (41 pages) and vault `CLAUDE.md` Special Files table.

## [2026-05-19] session-end | blog/index.js style fixes (5 gaps) + design audit (9 gaps identified, not yet fixed)
- Solves baton-pass problem: AI reads this at session start instead of re-deriving state from git log.

## [2026-05-19] feature | Hero Banner CMS — backend-controlled homepage hero

- New `HeroBanner` model in `pages_info` app. `FileField` (not `ImageField`) — Pillow 9.3.0 has no AVIF decoder, `ImageField` rejected AVIF uploads.
- Backend: `/hero-banners/` CRUD endpoint + injected into `/front-page/` response. Migrations `0008`, `0009`.
- Admin dashboard: `heroBannersApi` RTK Query slice, `HeroBannerForm` with drag-and-drop, DataGrid CRUD page at `/routemanagement/hero-banners`.
- Frontend: `homepagev2.js` — 5s auto-slideshow via `setInterval`, fallback to `bgDefault` if no banners. SSG unaffected, no SEO impact.
- Key gotcha: `display_order` empty string → DRF rejects as non-integer. Fixed in FormData submit handler.
- See [[hero-banner-cms]]

## [2026-05-19] session-end | blog detail sidebar padding — iPad mini + iPad Pro flush-right fixed

## [2026-05-19] fix | Contract_TranspotComposit admin crash — frontend sentinel id=-1

- Root cause: frontend sends `id: -1` for new unsaved rows. Backend passed it as PK into `get_or_create(id=-1)` → UniqueViolation on every save attempt.
- Fix: `operators/views.py:739-774` — branch on `id <= 0` (new) → `create()` vs positive id → `get_or_create()`. Sentinel never enters keep-list.
- Pattern captured: sentinel ids must never be PK lookup keys. See [[operators]] Contract_TranspotComposit section + [[admin-dashboard-contracts]] Payload Rules.

## [2026-05-19] refactor | Nav/Header Redesign — Minimal White Style + A11y Baseline

- Desktop: white bg (`bg-white`), `border-b border-gray-200`, tab-style active link (`border-b-2 border-brand-primary`)
- Mobile: brand blue preserved. All icons/text: `text-white md:text-gray-600` pattern (hamburger, logo, cart, profile consistent)
- Replaced pipe separators with `<nav aria-label>` + flex gap-1
- A11y: `aria-current="page"`, `focus-visible:ring`, skip-to-content link, `<IconButton>` close on drawer
- Fixed profile icon clipping: ProfileImage Box 40→44px (chevron badge `-2px` overflow clipped by AppBar `overflow:hidden`)
- Fixed huge gaps: right cluster `justify-between` → `justify-end` (was spreading items across ~900px)
- Key gotcha: MUI AppBar needs `color="inherit"` for Tailwind bg classes to take effect
- Commit `082a154` on branch `260513-refactor/payment`
- Created: `nav-header-redesign.md`. Updated: `design-systems.md`, `index.md`, `log.md`

---

## [2026-05-18] fix | StickySearchBar empty route name on fresh page load

- Root cause: `StickySearchBar` reads only Redux `state.location.from_location/to_location`. Fresh load = empty Redux = blank route name.
- Fix: `FilterTripsPage` passes `fromSearch`/`toSearch` (URL slug-derived) as props. `StickySearchBar` uses `reduxValue || propValue` fallback.
- Same pattern already existed in `SearchCover` (`fromLocationRedux || initialFromLocation`).
- 2 files changed, ~6 lines. No new abstractions, no Redux dispatch.
- Updated: CLAUDE.md (Search/UI section), vault nextjs-patterns.md (Redux Fallback Props Pattern)

---

## [2026-05-18] fix | Profile 403 Forbidden — PUT endpoint migration + UX

- Root cause: `PUT /users/${userId}/` admin-only since 2026-05-07. Frontend never migrated PUT from old endpoint.
- Backend: `UserAPIView` changed `RetrieveAPIView` → `RetrieveUpdateAPIView` (adds PUT support)
- Frontend: `pages/account/profile.js` endpoint migrated `/users/${userId}/` → `/api/user/`
- UX: `id_or_passport` + `datofbirth` made optional (OAuth providers don't supply these)
- UX: Debug error summary replaced with MUI Alert + friendly field labels (touched-only)
- Commit `a1944df` on branch `260513-refactor/payment`
- Updated: CLAUDE.md, vault accounts.md, vault api-endpoints.md

---

## [2026-05-18] fix | multi-tab payment gaps — all 7 resolved (GAP-1→7), PAY NOW lock, daytrip build fix

---

## [2026-05-18] fix | Checkout Access Broken for Auth Users — session?.email Regression

- Root cause: commit `8b3151f` changed `session?.user?.email` → `session?.email` based on wrong CLAUDE.md doc
- NextAuth does NOT set `session.email` at root level — email lives ONLY at `session.user.email`
- Effect: `email = undefined` for all auth users → `useCheckCartIdQuery` got null email → cart query returned stale/empty data → checkout redirect fired → users bounced to home
- Blast radius: 3 code files + 2 CLAUDE.md doc lines
- Investigation method: 3-agent parallel team (vault reader, checkout investigator, cart-login investigator) + independent plan reviewer (PASS) + code reviewer (PASS) + debug specialist (0 lint errors, 0 remaining hits)
- Fix: `session?.email` → `session?.user?.email` in `pages/checkout/index.js:47`, `pages/checkout/PaymentComponent.js:150`, `pages/orders/[orderid].js:113`
- Doc fix: CLAUDE.md session structure bullet + cart reprovisioning bullet corrected
- Verified: guest path (`formData?.email`, `router.query.email`) untouched. All prior payment fixes unaffected.
- Commit `5b7fa3c` on branch `260513-refactor/payment`

## [2026-05-18] fix | GAP-1 Payment Processing Banner — Dead Code Activated

- Multi-tab payment research GAP-1: `isPaymentProcessing` never dispatched, `GlobalPaymentWarning` dead code
- Worse than documented: `setPaymentProcessing` imported in `PaymentComponent.js` but never called. Component had broken `isMounted` guard — timer never started
- Fix: full lifecycle — set on charge creation, clear on paid/timeout/rehydration/error
- Backend-sourced timing: `expires_at` from charge response drives countdown. Removed hardcoded `qr_expiry_minutes: 5`. Backend `METHOD_EXPIRY` is source of truth
- Files: `useOmisePayment.js`, `GlobalPaymentWarning.js`, `paymentStatusSlice.js`, `_app.js`, `PaymentComponent.js`, order detail pages
- `GlobalPaymentWarning` moved from `_app.js` to `checkout/index.js` — under step nav, same position as guest banner
- Uses `AlertMessage` component with `warning` type (added to AlertMessage alertStyles)
- `reconcileStaleProcessing` reducer: auto-clears if `paymentInitiatedAt` >30 min on rehydration
- Branch `260513-refactor/payment`

## [2026-05-18] refactor | GAP-3 Cart Mutation Error Handling — isPaymentPendingError Utility

- Multi-tab payment research identified 6 gaps (2 HIGH, 2 MEDIUM, 2 LOW)
- Picked GAP-3: cart item DELETE silent fail on 409 — best impact-to-effort ratio
- Key discovery: research doc referenced dead code (`Itinerary.js`, zero imports). Active component: `EnhancedTripCard.js`
- Extracted `helpers/handleCartMutationError.js` — shared `isPaymentPendingError()` used by 4 components
- Fixed `EnhancedTripCard.js`: non-409 delete errors now show Alert instead of silent close
- Fixed latent bug in `BookButton.js`: bare `error?.status === 409` matched ALL 409s, not just payment_pending
- Deleted dead `components/itinerary/Itinerary.js`
- Commit `2116530` on branch `260513-refactor/payment`
- Docs: `docs/features/payment/GAP3_CART_DELETE_ERROR_FIX.md`, `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`
- Updated `payment-integration.md` in vault: "Centralized Payment Error Detection" pattern

## [2026-05-18] fix | cartId Null After Payment Redirect — Cart Reprovisioning

- Root cause: `resetCart()` nulls `cartId` in Redux on order detail pages (correct behavior — paid cart abandoned)
- No mechanism existed to provision new cart before user navigated to booking page
- `withCartValidation` HOC creates cart on demand but trip/search pages are NOT wrapped with it
- Fix: `pages/orders/[orderid].js` + `pages/guest-order/[orderId].js` — call `createCart()` fire-and-forget after `resetCart()`
- Auth flow: `session?.email` (not `session?.user?.email`). Guest flow: `decodeURIComponent(router.query.email)`
- Commit `3c89bff` on branch `260513-refactor/payment`
- Pattern added to `payment-integration.md`: "Cart Reprovisioning After Payment Reset"

## [2026-05-17] fix | PAYMENT_PENDING 409 on Step Navigation — 5 Bugs Fixed

- Root cause: `formStep === 2` guard fired `savePassengerAssignmentsToCart` in non-mixed flow (step 2 = Confirmation, not Assignment) → 409 with pending charge
- Fix 1: `index.js:805` — added `&& hasMixedPassengerCounts` guard → non-mixed flow never PATCHes cart items on step 2→3
- Fix 2: `index.js:256-261` — removed premature `isPaymentLocked` reset effect (fired on same render cycle as lock was set, nullified it)
- Fix 3: `FormCard.js:41` — added `|| isPaymentLocked` to `shouldDisableNext` → Next button disabled when payment locked
- Fix 4: `index.js:767` — added `if (isPaymentLocked) return` at top of forward nav → navbar step-click also blocked
- Fix 5: `index.js:983` — `onUnlockPayment` now calls `refetch()` to invalidate stale cart cache after cancel
- Bonus: `FormCard.js:46` — `getValidationErrorMessage` now returns correct message when `isPaymentLocked`
- 3-agent team: debug-specialist + code-reviewer for diagnosis, 3 fix agents in parallel, reviewer verified all pass

## [2026-05-17] fix | session.user.email Root Bug — 3 Files Fixed

- Root bug: `pages/checkout/index.js:46` — `session?.user?.email` always `undefined` (session has no `.user` wrapper)
- `email` variable was always `null` for all authenticated users, propagated to cart query + cancel handlers
- Fix 1: `session?.user?.email` → `session?.email` in checkout/index.js
- Fix 2: `Itineraries.js` cancel handler rewritten with auth-aware Bearer token + proper guest email fallback
- Fix 3: `savePassengerAssignmentsToCart.js` dead `session?.user?.email` URL branch removed
- Updated `payment-checkout-e2e-testing-2026-05-17.md` Bug 4 resolved + Bug 5 documented

## [2026-05-17] test | Payment Checkout E2E Attempt — Failed, Manual Guide Created

- Wrote 4 Playwright specs (3873 lines total) via 6-agent team for payment checkout E2E
- E2E failed: MSW intercepts `api.smartenplus.co.th` but Playwright `baseURL` is `localhost:3000` — MSW never intercepts
- Only 1 test passed (code inspection, no API calls needed)
- E2E specs deleted (cart-lock, cancel-state-machine, qr-polling, payment-recovery)
- Manual test guide created: `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md`
- Bug fix still valid: `savePassengerAssignmentsToCart.js` chargeId extraction (commit `38c7320`)
- data-testid attrs added to Input, Textarea, Passengers, PaymentMethodSelector (still present)
- Updated `payment-checkout-e2e-testing-2026-05-17.md` in vault

## [2026-05-17] test | Payment Checkout E2E Testing — 6-Agent Team

- Spawned 6 agents to test payment checkout flows end-to-end
- 4 E2E specs written: cart-lock (11 tests), cancel-state-machine (23 tests), qr-polling (24 scenarios), payment-recovery (16 tests)
- Audit results: Frontend 10/10, Backend 10/10, QR polling pass, Cancel spec valid
- Bug found: `savePassengerAssignmentsToCart.js` missing `chargeId` in cart 409 — 1-line fix (commit `38c7320`)
- Infrastructure issue: missing `data-testid` attrs — added to Textarea, Input, Passengers.js, PaymentMethodSelector.js
- Created `payment-checkout-e2e-testing-2026-05-17.md` in vault
- Updated index.md

## [2026-05-17] audit | Payment Checkout Architecture Audit — 20/20 Pass

- Audited smartenplus-frontend + smartenplus-backend against `PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`
- 20/20 items validated pass (10 frontend, 10 backend)
- One medium gap fixed: `getPrimaryCharge()` sort order corrected (oldest-first → latest-first)
- PromptPay intentional exclusion from one-active-lock per architecture doc
- Created `payment-checkout-architecture-audit-2026-05-17.md` in vault
- Updated MEMORY.md (SB), `project_payments_app.md` (SB)

## [2026-05-17] retro | Payment Refactor — Session Retrospective + Vault Update

- Branch `260513-refactor/payment`: 12 frontend files (+465 lines), 7 backend files (+233 lines)
- Fixed 7 frontend gaps (F1–F6 + QR expiry) and 4 backend gaps (B1–B4) vs architecture doc
- 25/28 use cases covered, 3 partial (Phase 2: WebSocket, admin reconcile UI, webhook replay)
- 5 mistakes documented: over-broad FormCard guard, positional alert text, settings.json schema, auth email param, dual cancel surface
- Key lessons: child terminal state → parent callback, sessionStorage init after persist rehydration, auth-conditional params key off token not email, dual UI surfaces sharing chargeId must be mutually exclusive
- Updated `payment-integration.md` with 8 new patterns
- Vault: log.md updated, index.md updated

## [2026-05-16] update | Repay Failure RCA — Phase 1 + Phase 2 Complete

- User couldn't repay after refresh or cart update
- Identified 8 frontend root causes → all fixed
- Phase 2 backend: idempotency key, reconciliation endpoint, CheckoutSnapshot model, expire protection
- Frontend integration: X-Idempotency-Key header, ORDER_ALREADY_PAID handling, cross-tab cart sync
- Updated: CLAUDE.md (frontend patterns), REPAY_FAILURE_RCA.md, PHASE2_BACKEND_IMPLEMENTATION.md
- Updated: payment-system.md (vault), index.md

## [2026-05-16] bootstrap | Vault Initialized

- Created vault at `~/second-brain`
- Bootstrapped full structure: 9 folders, 3 root files, 4 templates, 4 project seeds, 4 knowledge seeds
- Seeded SmartEnPlus project knowledge from existing 550 docs (synthesized, not copied)
- Git initialized with `.obsidian/` in gitignore
- Key decisions: flat folder structure, no frontmatter, wikilinks only, no raw sources folder yet

## [2026-05-16] seed | SmartEnPlus Project

- Created `01-projects/smartenplus/` with 4 pages
- README: project overview, stack, 3-repo ecosystem
- Architecture: Pages Router, Redux slices, RTK Query APIs, component tree
- Payment System: Omise, GatewayCharge, QR polling, canonical charge rule
- Checkout Flow: SSR-disabled, cart item keys, passenger assignment, guest mode

## [2026-05-16] seed | Knowledge Base

- Created 4 knowledge pages in `03-knowledge/`
- AI Workflows: LLM Wiki pattern (ingest/query/lint), three-layer architecture
- Next.js Patterns: ISR cache, dynamic imports, RTK Query, DatePicker handling
- Payment Integration: Thai methods, Omise source types, webhook reconciliation
- Design Systems: Token approach, COLORS/SPACING/BORDER_RADIUS/TYPOGRAPHY_SCALE

## [2026-05-16] update | Backend Documentation Ingest

- Created [[backend-architecture]]: Django app structure, key models, API endpoints, Celery tasks, dev commands
- Updated [[payment-system]]: added 11 backend sections (finalize_payment, locked_amount, ExpirePendingChargeView, IdempotencyKey, WebhookEvent audit, JPY handling, polling fallback, notification dedup, status machines, charge creation order, ManualAdjustment)
- Updated [[payment-integration]]: added idempotency sentinel pattern, amount locking pattern, webhook audit pattern
## [2026-05-19] fix | Breadcrumb + CategoryMenu Tech Debt + Blog Spacing Consistency
## [2026-05-20] session-end | Recommend-route review + partial implementation — hydration issue blocking

## [2026-05-22] session-end | locked_amount db_index fix (backend #4 closed) + master-state stale item corrected

## [2026-05-22] session-end | trip SEO schema fake data fixed + dynamic sitemap phantom closed

## [2026-05-25] feat | Experiences nav category filtering — ADR written, 7 distinct categories fixed, nav 404 + empty-array fallback bug resolved
## [2026-05-25] audit | n8n webhook resend operator doc v1.1 — scrutinize audit. Findings: duplicate send on retry (major), N8N_WEBHOOK_URL required in all envs (major), payload omitted InfoFields (nit). Doc updated, implementation ready on feat/n8n-resend-webhook.
## [2026-05-25] session-end | n8n webhook deployed to production. send_booking_data moved to bookings/tasks.py, n8n webhook forwarding added, 4 commits (fa687cb+4285e70+8d88ba3+2bdf31b), 3 bugs caught pre-merge (import crash x2, orphaned try block, N8N_WEBHOOK_URL missing default). Branch→develop→main→production. Knowledge entry 04-knowledge/backend-n8n-resend-webhook.md created.
## [2026-05-27] session-end | Header search pattern review + 4 bug fixes. 3-agent team (UX/Design/Engineer) audited header. Fixed: NavDropdown WCAG contrast, HeaderSearchContext useMemo, injection effect over-firing, deleted dead StickySearchBar.js. Merged + pushed to develop (0ccf03c). Wireframe doc moved to vault.

## [2026-05-28] session-end | Header search input redesign — variant=input, white bg, fb-blue button, h-10, Plan your Thailand journey placeholder. Team debate h-9/h-11 → h-10 compromise. Search bar left-aligned in header. Header height research documented (no changes). master-state updated.

## [2026-05-28] session-end | Popular Routes no-white-bg + section/card gap fixes

## [2026-05-28] session-end | GYG split-card + all committed — 7 commits on header-redesign branch
## [2026-05-30] audit | transportation-category-audit — 3-level category system documented, Airport Transfer architecture justified, Django shell queries for inventory/booking split
## [2026-05-30] scrutinize | transportation-category-audit — 8 corrections applied: 26 not 25 station_types, TRANSFER/filter decoupled, lowest_price nullable, arrival-only gap, ZeroDivisionError guard, is_actived typo table, query_count Celery mechanism, 10% threshold is heuristic
## [2026-05-30] design | airport-transfer-redesign-spec — professional redesign spec added to audit doc: image card with IATA badge + gradient fallback, carousel mobile, serializer expansion plan, null safety requirements
## [2026-05-30] session-end | vault-only session — transport audit + scrutinize + redesign spec. master-state updated. AT-1 added as P0 next-session task. No code committed.
## [2026-05-30] optimize | vault structure fix — rogue 04-knowledge/ deleted (file moved to 03-knowledge/), homepage/ folder deleted (2 files → 01-projects/), southeast_asia doc → 02-areas/, glassmorphism → 08-archive/, 3 stale DECIDED → COMPLETED, index updated + Archive section added. Known debt: 01-projects/smartenplus/ subfolder (50+ files) violates flat schema — defer, wikilinks resolve correctly.
## [2026-05-30] session-end | #8 wrap-up — vault optimize complete. master-state updated. No code committed. Next: AT-1 airport transfer redesign (spec in 03-knowledge/transportation-category-audit-2026-05-30.md).
## [2026-05-30] audit | airport-transfer-width — 3-agent parallel audit. Root cause: inner px/mx margins (px-2 md:px-3, mx-2, mx-3) eating into max-w-[1200px] container. Fix attempt (removing all margins) broke layout — reverted. Issue unresolved. Report: [[airport-transfer-width-audit-2026-05-30]]. Next team: redesign sections as full-width with centered inner content, or accept current padding.

## [2026-05-31] session-end | #15 — header search input UI cleanup. Removed left icon, stripped 'Search' text from submit btn, fixed input height mismatch (h-full). Commits ff43d3d + aea6cf0 on 260528-feat/header-redesign-2026.

## [2026-06-01] lint | atomized 5 concepts — airport-transfer-at1-redesign-spec, nextjs-hydration-rules, payment-checkout-5-principles, nextjs-static-path-prop-divergence, designsystem-shadow-border-tokens. Source notes trimmed.

## [2026-06-01] session-end | #16 — vault atomization (5 atoms). Feature branch merged to develop + shipped to production.

## [2026-06-01] audit | activities location search — 4-team audit, 3 critical bugs confirmed. RC-1: backend text→ID type mismatch (products/views.py:446). RC-2: inputValue prop desync. RC-3: freetext not emitting. Fix sequence in [[activities-location-search-bug-2026-06-01]].
## [2026-06-01] audit | activities search merge review — true merge deferred, icon diff + side-by-side layout implemented. [[activities-search-merge-review-2026-06-01]]

## [2026-06-01] session-end | #20 — grill overturned 'backend OR-union required' claim. True merge feasible via keywords[] intent detection. Tech debt mapped: 2 POPULAR_DESTINATIONS sources incompatible. ACT-5 (consolidate) + ACT-6 (unified ActivitySearch) added to open items. master-state + vault updated.

## [2026-06-01] fix | Tailwind JIT sidebar bug — dynamic template literal `lg:grid-cols-[${var}px_1fr]` never generated by Tailwind purge. Hardcoded to static string. Sidebar now renders on desktop.
## [2026-06-01] feat | Phase 2 backend filters — products/views.py: min_price/max_price (Min annotation), duration_type, contract_type, features (Extra.item), min_rating. Fix: contract_ratecard_set → contract_ratecard ORM path. commit 508949b.
## [2026-06-01] feat | Phase 2 frontend — ExperienceSidebar 5 filter sections live. PriceRangeSlider (reusable, debounced, multi-currency). DayTripCard useCurrency(). PricingDisplay COLORS tokens. SortBar price sort. useDayTripFilters 6 new keys. commit 70c8712.
## [2026-06-01] fix | formatCurrency zero bug — `if (!value)` → `if (value === null || value === undefined)`. Slider tooltip now shows ฿0.00 at min position.
## [2026-06-01] session-end | #24 — Phase 2 complete (backend + frontend). Both repos committed + pushed. QA + merge next session. master-state updated.
## [2026-06-02] audit | BW-1/BW-2/BW-3 verified already fixed — blog padding + BlogCard radius/margins correct in code. Closed in master-state.
## [2026-06-02] atomize | 3 concepts from activities-day-tour-page-review — inactive-contracts, hydration-spurious-push, design-token-caption-gotcha
## [2026-06-02] atomize | 3 concepts from activities-location-search-bug — backend text fallback, autocomplete inputvalue sync, handleInputChange parent emit
## [2026-06-02] decision | adr-activity-card-favorite-button — grilled + scrutinized. Findings: missing unique_together migration (blocker), unused content_type param in _validate_contract_params (major), pre-existing axiosInstance infinite fetch loop (document only). ADR updated with full implementation code + handoff in master-state as FAV-1.

## [2026-06-02] session-end | FAQ fixes + activities filter + carousel shipped

**Completed:**
- FAQ architecture: buildCancellationSummary() + buildExperienceFAQItems() utilities, removed hardcoded filler/text
- Activities filter: multi-value service_category support, removed confirm=True from listing (kept on booking check)
- RelatedExperiences: carousel on mobile/iPad, grid on desktop
- Merged 3 branches to develop (frontend) and develop (backend)

**Deferred to future session:**
- FAQ-1 P1 admin-dashboard: ageRestriction field (4 files, separate repo task)
- EXP-DETAIL-1: iPad/mobile redesign (waiting on session #32 uncommitted files, status unclear)

**Vault docs updated:**
- master-state.md: Section 1 + active branches + loose ends
- log.md: this entry

## [2026-06-03] session-end | 5-agent test team: 979 tests run, BLOCK RELEASE, 4-5 dev days to fix
- Jest: 217/719 failed (30%), coverage 3.92% vs 70% threshold
- Playwright: 233/260 failed (90%), only 4/10 pages covered, mobile 100% fail
- 6 CRITICAL issues: 0% BookButton coverage, checkout timeout, mobile E2E broken, jest-axe missing, MUI emotion mismatch, payment path unverified
- Vault note: [[frontend-test-infrastructure-audit-2026-06-03]]
- Resume: merge backend branch `260603-fix/booking-summary-trip-none-guard` → develop

- Source: [[checkout-confirmation-payment-crash-2026-06-03]] (148 lines, no .original.md)
- Source: [[cartitems-500-error-analysis-2026-06-02]] (95 lines, no .original.md)
- Extracted: [[service-detail-non-transport-display]] — booking detail page field-name contract (refund_hours, general_information?.description, customFormatDuration safety)
- Extracted: [[view-utility-call-exception-wrapper]] — view-layer `try/except → ValidationError` defense-in-depth pattern
- Index: source entries updated with atom pointers. Page count: 97 → 99.
- Pre-existing atoms unchanged: [[contract-trip-null-non-transport-pattern]], [[copy-cartitem-trip-none-guard]], [[contract-serializer-non-transport-fields-2026-06-03]], [[checkout-null-contract-scan-2026-06-03]] already covered the bulk of the patterns.

## [2026-06-03] audit | contract-model-ambiguity-audit-2026-06-03 — 4-round multi-repo audit of `primary_location`/`service_areas`/`meeting_point_*`/`InfoField` casing + `Trip.route` vs `timeline_place`. 6 overlaps; 1 customer-visible (i18n unwired on `meeting_point_details`), 5 staff-side. Recommendation: document + 1 help-text fix, no model consolidation. S-1/S-2 overturned dead-code claims on `Trip.route` (25+ call sites) + `meeting_point_place` (active admin/tests/serializer). P0: fix `ContractFormFields.js:184, 227` help text contradiction (D-1, owner admin-dashboard). P1: write casing-system ADR (D-2/D-3), wire `get_translated_meeting_point_details` (B-1), add `Contract.clean()` for category/field invariants (B-7). P2: admin PATCH try/except (B-9), delete dead `showStations` flag (F-10), data inventory before any `primary_location` deletion. 5 ops questions for staff (no code jargon). Index updated.

## [2026-06-03] fix | contract-location-help-text — fa2f16a on admin-dashboard main. P0 of [[contract-model-ambiguity-audit-2026-06-03]] closed. 4 strings: help text + tooltips for Primary Location (line 179, 184) + Service Areas (line 222, 227) in `ContractFormFields.js`. `service_areas` = pickup zones + coverage areas (per user). `primary_location` = main destination or operating area. Both fields feed customer location search via OR (products/views.py:462-475, post-2026-06-01 fix). Branch: `260603-fix/contract-location-help-text` → develop → main. master-state.md Section 1 + 2 updated.

## [2026-06-11] audit | seo-sitemap-whole-site-audit-2026-06-11 — 3-agent SEO+sitemap audit (sitemap infra / on-page meta+schema / technical rendering), code + live. Live fetches 403'd by Cloudflare WAF → P0-1 verify Googlebot in GSC. 6 P0 (fake review schema ×3, sitemap private-URL pollution, broken noindex via nonexistent next-seo `robots` prop, malformed activities canonical, no origin host/HTTPS 301s), 10 P1, ~16 P2. Soft-404 recommendation from agent overruled per [[gsc-crawled-not-indexed-investigation-2026-06-05]]. Audit only — no code changed. Index updated.

## [2026-06-12] fix | seo-audit fixes implemented — branch `fix/seo-audit-2026-06-11` @ `1f3f7a2`, 26 files (+361/−756). P0+P1+P2 from [[seo-sitemap-whole-site-audit-2026-06-11]]: fake reviews ×4 deleted (4th source AirportTransferJsonLd.js found during impl), sitemap exclude → 128→86 URLs, noindex fixed/added ×5 pages, activities canonical fixed, 480-line dead JSON-LD pipeline deleted from useTripSEO, hreflang removed, xmlns http://, 3 new 301s, Promise.all+escapeXml in server-sitemap, GTM out of Head, 5 StructuredData files → www. Verified: build exit 0, 8 regression greps clean, robots.txt +5 disallows. NOT merged. Remaining: GSC/WAF verify, nginx 301s, P3 sweep.

## [2026-06-12] atomize | 3 atoms from seo-audit: next-seo-v6-robots-prop-broken (API change silent failure), canonicalization-audit-checklist (domains + per-page + parallel URL + sitemap pattern), site-url-config-pattern (baseURL vs NEXT_PUBLIC_DOMAIN const). Vault index updated with cross-links.

## [2026-06-12] audit | payment-deep-review-2026-06-12 — 3-agent team (FE reviewer / BE reviewer / cross-repo contract) + leader hand-verify of all HIGHs. 5 HIGH: H1 client-controlled charge amount, H2 unverified legacy webhook live, H3 idempotent-reuse response-shape fork breaks checkout refetch, H4 charge_id dropped → cancel-on-leave never expires, H5 paid-but-unfinalized invisible (payment_pending excluded from reconcile gate). ~15 MEDIUM, ~15 LOW, 10 test gaps, 4 PAYMENT_SYSTEM.md drifts. BE-F9 currency-confusion claim overturned by contract reviewer. Carried-over items re-checked (stable_id now comment-only, celery retry-uncalled confirmed). Report only — no code changed. Index updated.
## [2026-06-12] ingest | payment deep review test cases — 8 smoke + 7 manual + 7 E2E specs for H1-H5, M1-M3, M5, M8-M10, M17
## [2026-06-12] ingest | payment test results — BE 20/20 pass, FE 84/84 jest pass. Full coverage: paymentMethods, useOmisePayment, useQRPolling, useCancelPayment, PaymentComponent. Vault test-cases doc updated.
## [2026-06-13] audit | design-system-audit-2026-06-13 — Full design system audit: 10 token dimensions (5 missing), 889 hardcoded colors, 386 inline styles, 13 violation categories, 12 UX dimensions, 5 debate outcomes, 5-phase migration roadmap, 10 quick wins.
## [2026-06-13] lint | /lint-vault protocol: 41 new atoms extracted from 53 notes >150 lines in 01-projects/ + 03-knowledge/; 13 existing notes updated with new file:line evidence; 20 source notes received `## Related Atoms (Extracted 2026-06-13)` sections. Domains: payment (9), frontend (7), SEO (11), cross-sell (3), React (1), DRF/Django (2), Next.js (2), design system (4), misc (2). All atoms <200 lines (max 97, avg 62). Index + log updated.

## [2026-06-13] session-start | #108 — design-system token migration (18 files) + test fix; master-state updated

## [2026-06-13] audit | cross-sell-integration-status-2026-06-13 — live code verification all 4 surfaces mounted; vault stale atoms flagged (checkout debate + placement strategy + impl plan); GTM item_category quick win identified; BD inventory only gate

## [2026-06-13] session-end | #108 — cross-sell audit + vault closures: all 4 surfaces live, GTM+activity shipped (vault stale corrected), PAYMENT-FIX/DEADLOCK/design-Phase1 closed, KB atomization deferred, AT-1 next P0

## [2026-06-13] close | carried items verified complete — PAYMENT-FIX (both PRs merged: FE `dae26da`, BE `5653b04`, branches deleted), PAYMENT-DEADLOCK (`482cfc6` head of BE main), DESIGN-SYSTEM-PHASE-1 (tokens `designSystem.js:149-210`). KB-ATOMIZATION-PAYMENT deferred to next `/lint-vault` (M8 in payment-backend-charge-flow §5 verified accurate). master-state §1 resume list pruned; next: AT-1 airport transfer P0.

## [2026-06-13] correct | cross-sell note self-stale fix — re-verified live code: GTM `item_category` already shipped (`hooks/useOmisePayment.js:59`+`:144` purchase event) and activity-detail accuracy already migrated to recommendations API (`RelatedExperiences.js:7`). Both were wrongly listed as open eng work in [[cross-sell-integration-status-2026-06-13]] (note went stale day-of). Corrected: note (Already Shipped section), [[gtm-purchase-item-category-attribute]] (SHIPPED banner), master-state §1+§2. Sole open eng item now = multi-item post-booking (`bookingContext.js:33`, Sprint 2).

## [2026-06-15] audit | trip-filter-modal — 3-agent functional audit. 2 critical bugs (transport typo FilteredTripList.js ~L51, badge hardcoded defaults TripSearchFilters.js ~L16), 2 logic ambiguities (OR/AND conditions, NaN tiebreaker), 4 minor dead-code. Core wiring intact. Report → [[trip-filter-modal-audit-2026-06-15]].

## [2026-06-15] audit | trip-page-full-audit — 3-agent full-page audit /trips/hatyai/koh-lipe. 4 critical (ratecard crash, composit crash, operator null, dialog pattern), 2 XSS (BlogPost, RouteFaqs), 3 dead files (TripList, tripItemv2, RouteFaqs), 8 medium. Core wiring OK. → [[trip-page-full-audit-2026-06-15]].

## [2026-06-16] audit | trip-detail SEO/AEO/GEO — 3-specialist audit of detail page /trips/detail/[...slug] (distinct from route-listing audit). 25 raw → 18 unique, 8 HIGH. Cross-cut root cause: TripDetailSEO.js:11-15 docstring claims Breadcrumb/LocalBusiness/FAQ/TouristTrip schema it never renders (only Product) — fix = wire existing helpers. HIGH: localhost/non-www canonical, no BreadcrumbList, malformed offers, no FAQPage, generic Product not TouristTrip, facts in tooltips, og:locale th_TH hardcoded, no hreflang. Read-only, source-derived (no localhost WebFetch). → [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]].
