# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-18 (session #130 END)

**Achieved this session (#130) — category-aware duration fix SHIPPED TO PROD (FE main). Spa "1 Day" bug killed.**
- **Bug (user-reported):** spa product showed duration "1 Day" — impossible. Root cause was category-wide: all activities components read `contract.tour_duration_days` (BE `PositiveIntegerField`, **default 1**, days) and rendered "X Day(s)" regardless of `service_category`. Public LIST serializer omits the field → cards saw `undefined` → ternary always yielded "1 Day". Same inline ternary copy-pasted in **5 sites** (3 components + 2 SEO JSON-LD builders).
- **Fix (FE-only, commit `35c524d` → develop → main):** new `helpers/formatContractDuration.js` single source of truth, returns `string|null`. Gated by existing `SERVICE_CATEGORY_CONFIG.showDuration` + new additive `durationUnit` ('days'|'time'|'nights'). Per-category: spa/dining → "2h 30m" from `duration` (colon string, parsed by reused `customFormatDuration`); event/attraction/OTHER → hidden; accommodation → "N nights"; tours → days (null if absent, no false "1 Day"). Only behavior change: `OTHER.showDuration` true→false. Replaced all 5 ternaries.
- **Verified:** ESLint clean (7 files), 36 serviceCategoryHelper tests pass, BE confirmed `duration` serializes as colon string `"2:30:00"` not ISO8601 → no parser needed.
- **PROD:** FE `main` = `develop` = `35c524d`. Pushed + shipped by user. **Side effect: FE main now also carries ISR route (66d896e) — FE half of #129 ISR-REVALIDATE-GAP is now deployed.**
- New atom: [[category-aware-duration-formatter]].

**Resume point (EXACT):**
1. **#129 ISR PROD ACTIVATION — BACKEND still pending.** FE shipped (main `35c524d` carries ISR route). BE develop `4eaaf8d` NOT yet on main/prod. On backend host: deploy develop→main + set prod `FRONTEND_URL=https://www.smartenplus.co.th` + `docker restart smartenplus-backend_celery-worker_1 smartenplus-backend_celery-beat_1`. Verify: `echo "from django.conf import settings;print(repr(settings.FRONTEND_URL))" | docker exec -i smartenplus-backend_celery-worker_1 python manage.py shell` → must print `www`.
2. **ISR smoke test:** edit a contract `tour_highlights` in admin → `docker logs -f smartenplus-backend_celery-worker_1 | grep -i revalidat` → expect `ISR revalidated slug=... status=200` → page fresh in seconds.
3. **Duration follow-up (optional):** backend Option B — add `tour_duration_days` to public `ContractSerializer` (list) so day-tour browse cards show "N Days". One-line; needs BE deploy + ISR cache clear.
4. AT-1 Airport Transfer (P0) still queued.

_(Session #129 block archived → `07-logs/session-history.md`.)_

---


**Carry-forward bugs (open, from #127):**
- **BE-IMAGE-DEDUP** tech debt (Section 2) — `process_operator_image` vs `process_review_image` dup + upload-validation copy-pasted ×5 files.
- silaphat `Operator.description` holds route notes, not real about-copy — data quality.
- `booking_count_yesterday` (`products/serializers.py:353-363`) — rolling 24h not calendar yesterday.
- Dual sort vocab: QuickSortPills PascalCase vs SortDropDown `-booked_count`.
- Prod backend git history diverged from origin (merge-noise) — pulls always merge, not FF. Cosmetic.

**Next session: starting state**
- vault: `master` @ new commit (this adds #130)
- BE: `develop` @ `4eaaf8d` — ISR revalidate + FRONTEND_URL www fix. **NOT deployed to main/prod yet.** `main` still `dbbbe97`.
- FE: `main` = `develop` @ `35c524d` — duration fix + ISR route, **SHIPPED TO PROD.**
- admin-dashboard: `main` @ `874d74d` (unchanged)
- content: `master` @ `3756e5b` (clean)
- ⚠️ #129 ISR activation: BE-only remaining — deploy BE develop→main + set prod `FRONTEND_URL=www` + restart worker.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **ISR-REVALIDATE-GAP** | Admin contract edit not reaching prod `/activities/detail` (revalidate 3600) + `/trips/detail` (revalidate 300). Backend busts Redis correctly (`operators/signals.py:33`); Next.js Pages-Router ISR HTML never told to regen + no `/api/revalidate` route → stale, forever on cold pages (persistent `next_cache` volume). Fix (4 steps, build order in plan): (1) BE `daily_counter`→`.update(F+1)` enabler stops per-view post_save, (2) FE `pages/api/revalidate.js` POSTs `{slug}` owns path map, (3) BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, (4) `REVALIDATION_SECRET` both repos incl GH Actions runtime path. Task no-ops on empty secret. | **IMPLEMENTED #129 → develop** (BE `4eaaf8d`, FE `66d896e`). All 4 steps done + verified (29 tests, manage.py check, ESLint, no-storm proof). **Prod root cause found:** `FRONTEND_URL` was apex → 301→www dropped the POST; fixed default→www (`d37dee3`). **FE SHIPPED #130** (main `35c524d` carries ISR route). **BE ACTIVATION PENDING:** deploy BE develop→main + set prod `FRONTEND_URL=www` + restart worker, then smoke-test (see Section 1 resume). | `operators/signals.py`, `operators/tasks.py`, `products/views.py:884`, `Smartenplus/settings.py:373`, FE `pages/api/revalidate.js`, `deploy-ghcr.sh` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: public LIST `ContractSerializer` doesn't expose `tour_duration_days`, so cards can't show "N Days" (detail page works, uses `__all__`). FE-only fix #130 chose omission over false "1 Day". Option B: add `tour_duration_days` to list serializer `fields`. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional follow-up, low priority. FE helper unchanged either way. | `smartenplus-backend/operators/serializers.py` (ContractSerializer), [[category-aware-duration-formatter]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate, pre-existing). Cluster 1: WebP resize/compress algorithm duplicated ~2-3× — `operators/utils.py:process_operator_image` (now parametrized #126b), `dialogue/utils.py:process_review_image` (120KB hardcoded), plus WebP/thumbnail code in `operators/admin.py`. Cluster 2: upload validation (ext whitelist + size) copy-pasted across 5 files (`stations/views.py`, `operators/utils.py`, `operators/views.py`, `pages_info/models.py`, `dialogue/utils.py`) each with own constants → drift risk. Consolidate → one `core/image_utils.py`: `process_image_to_webp(file, *, max_output_size, max_dimensions)` + `validate_upload(file, *, allowed_ext, max_size)`, migrate all callers. | OPEN #126 — dedicated refactor session. High blast radius (operators/dialogue/stations/pages_info), zero user value, all spots work. Do NOT bolt onto feature work. | `operators/utils.py`, `dialogue/utils.py` |
| **VAULT-DATE-RENAMES** | 105 files embed dates in filenames (violates "no dates in filenames" rule). Rename breaks every inbound wikilink. Needs separate planning round: `git mv` + atomic search-replace of all `[[old-name]]` → `[[new-name]]`. | OPEN #125 — next-wave vault work. | [[vault-optimization-snapshot-2026-06-16]] |
| **OPERATOR-DESC** | Operator `description` field (backend) → unblocks GEO "about operator" prose on `/operators/[slug]` (flagged in SEO/AEO/GEO audit, the one truly backend-blocked item). | **CLOSED #125** — verify-only: backend was already complete (`Operator.description = TextField()`, `OperatorDetailSerializer fields='__all__'`). Live curl confirmed populated text returned. FE wired About-{operator} section at `pages/operators/[slug].js:151` (FE `f75b411`). | done |
| **OPERATOR-TAB-COUNTS** | `by_type` aggregation (TRANSPORT-type only, computed pre-type-filter) on `OperatorContractsViewSet.list` summary → enables per-type counts in the operators page MUI tabs ("Join Tour (12)"). Frontend tabs already shipped without counts. | **CLOSED #125** — BE `0d6a3cf`, FE `f75b411`. `summary.by_type = {ALL, PRIVATE, JOIN, CHARTER}` keyed to `FILTER_TYPES`. Bug caught: `select_related` INNER JOIN was under-counting (15→3); fix = aggregate from `Contract.objects` directly. 4 invariance tests added (`operators/tests/test_operator_contracts_viewset.py`). | done |
| **MIN-RATE-BE-MERGE** | BE `fix/popular-routes-lowest-price` @ `4da0b81` — merge to develop + verify `/front-page/` Hatyai→Koh Lipe `lowest_price` matches SlideCalendar rate | **CLOSED 2026-06-16** — merged at `37387c8`, BE develop now `21fbdcf` | `smartenplus-backend/products/views.py:1197` |
| **TRIP-SEARCH-REDESIGN** | Travel Decision Engine + below-fold redesign of `/trips/[from]/[to]` | **CLOSED 2026-06-15.** R1+R2 fully shipped. FE `develop` @ `6f2ada9`. Deploy to prod pending (ops task). → `07-logs/closed-items.md` | [[trip-search-results-implementation-plan-2026-06-14]], [[trip-search-below-fold-redesign-2026-06-15]] |
| **TRUST-BADGE-BUG** | `getTrustBadges` Free-Cancellation inverted | **CLOSED 2026-06-14.** Fixed in Phase 0.5 — `refund_percentage === 0` → `=== 100`. Shipped in `feat/trip-search-redesign`, now on `develop`. | `helpers/getTrustBadges.js:19` |
| **PAYMENT-FIX** | Implement 5 HIGHs + priority MEDIUMs from payment deep review | **CLOSED 2026-06-13.** All 5 batches shipped + 8/8 E2E automated + webhook gap closed. **Both PRs MERGED:** FE merge `dae26da` (`main`), BE merge `5653b04` (`main`) — feature branches deleted. 119 tests pass. M4 retracted. | [[payment-deep-review-2026-06-12]], [[payment-auto-test-results-2026-06-12]], [[omise-webhook-tailscale-local-testing]] |
| **PAYMENT-DEADLOCK** | Recover paid-but-unfinalized order PLB0229785 from payment_pending deadlock | **CLOSED 2026-06-13.** Fix `482cfc6` "recover paid-but-unfinalized order from payment_pending deadlock" is head of BE `main`. 278 BE tests pass. | [[payment-pending-deadlock-2026-06-12]] |
| **DESIGN-SYSTEM-PHASE-1** | Token completion (audit 2026-06-13) | **CLOSED 2026-06-13.** OPACITY, Z_INDEX, TRANSITIONS, LAYOUT, SIDEBAR_CONFIG added (`helpers/designSystem.js:149-210`); token migration FE `489de5f`+`b5ce878` (18 files). Residual gaps (typography line-height/letter-spacing, 4 stray `#fff` in globals.css) trivial — untracked. | [[design-system-audit-2026-06-13]] |
| **KB-ATOMIZATION-PAYMENT** | 12 KB gaps from payment deep-review verification report | **DEFERRED.** Batch with next `/lint-vault`. M8 in `payment-backend-charge-flow.md` §5 verified accurate (email-guard ownership check present). | [[payment-deep-review-2026-06-12]] |
| **BOOKING-PAY-FIX-1** | Fix 4 verified bugs from booking-payment e2e audit | CLOSED #94. Merged `fix/checkout-stable-id-cleanup` → `develop` (`f271aef`). 53/53 tests, SM-1–SM-4 passed. | `hooks/checkout/useCartSync.js`, `components/UI/BookButton.js:41-43` |
| **BOOKING-PAY-REPRO-1** | Runtime repro C1 (formData lost on hard refresh) + C2 (transient error nukes cartId) | CLOSED #97. C1: `isCartLoaded &&` guard in clear-assignments effect (`checkout/index.js:188`). C2: `if (error?.status === 404)` in catch (`check-and-createcart.js:67`). Commit `cb817d9` on `develop`. | `pages/checkout/index.js:188`, `components/HOC/check-and-createcart.js:67` |
| **CROSS-SELL-MERGE** | Merge `feat/redesign-people-also-book-cards` → `develop` | CLOSED #97. Branch confirmed fully merged (`git merge-base --is-ancestor` → FULLY MERGED). `CheckoutRelatedTrips` mounted at `checkout/index.js:1010`. All recommendation components present. Remaining work is BD inventory only → see CROSS-SELL-BD-INVENTORY. | done |
| **SEO-SITEMAP-FIX** | Implement fixes from whole-site SEO+sitemap audit | MERGED 2026-06-12. P0+P1+P2 `1f3f7a2` merged → develop `d88f50b`, pushed. Fake reviews ×4 deleted, sitemap 128→86 URLs, noindex fixed ×5 pages, dead JSON-LD pipeline removed. Build exit 0, greps clean. **Remaining:** deploy to prod, GSC Googlebot/WAF verify (manual), nginx 301s (infra), P3 dead-code sweep. Soft-404 stays with GSC-1. | develop `d88f50b`, [[seo-sitemap-whole-site-audit-2026-06-11]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell | OPEN. BD task — no eng work. Needs: (1) return route Koh Lipe→Hat Yai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Cross-sell auto-hides until `recommendation_count > 0`. **All 4 FE surfaces already live and verified 2026-06-13. GTM `item_category` + activity-detail accuracy ALSO already shipped (`hooks/useOmisePayment.js:59`+`:144`, `RelatedExperiences.js:7`) — were wrongly listed as open eng work.** Only BD inventory blocks value. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2, not urgent). See [[cross-sell-integration-status-2026-06-13]]. | BD action |
| **BRANCH-CLEANUP-REMOTE** | 81 merged remote `origin/2606*` branches pending deletion | CLOSED #97. 42 actual branches deleted (vault count was stale). `git branch -r \| grep origin/2606 \| wc -l` → 0. `git fetch --prune` run. 45 remote branches remain (all active). | done |
| **FRONTEND-AUDIT-FIX-1** | Audit finding 3 (Formik render-prop useEffect) | CLOSED #95. PR1 `fix/audit-checkout-passengers-hooks` (e5261ab → 1e46314). New `FormikValuesSync.js` (105 lines) absorbs both effects via useFormikContext. Rules-of-hooks invariant restored. Lint clean. | `components/forms/checkout/FormikValuesSync.js`, `Passengers.js` |
| **FRONTEND-AUDIT-FIX-2** | Audit findings 1+2+4+5 (RTK Query) | CLOSED #95. PR2 `fix/audit-rtk-query-cleanup` (ecc76a9 → b6b956e). getSession pattern, activities key, cart-version extract, createCart single invalidation. New `store/cart-version.js` (12 lines). 3 sources of truth → 1. Lint clean. | `store/cart-version.js`, `store/cart-slice.js`, `store/api/*`, `store/index.js` |
| **FRONTEND-AUDIT-FIX-3** | Audit findings 6+7+8+9 (dead code + hygiene) | CLOSED #95. PR3 `chore/audit-deadcode-and-hygiene` (d69b473 → fbe9aab). 31 files, 4237 deletions, 7 insertions. Rebased onto develop post-PR1+PR2. | 5 dead-code paths, 5 .backup, 2 logs, db/ data/ *.diff *.sh, 4 archive, .gitignore |
| **FRONTEND-AUDIT-FOLLOWUP-1** | 2 exhaustive-deps warnings in FormikValuesSync.js:61:6 | CLOSED #97. Suppression comments added. Effect 1: refs + useState setter stable by definition. Effect 2: `cartitems?.cart_item` kept (not `cartitems`) — tighter RTK refetch trigger. Lint clean. Commit `7107516`. | `FormikValuesSync.js` |
| **FRONTEND-AUDIT-MANUAL-PRS** | Open 3 PRs on GitHub manually | DROPPED #97. All 3 branches confirmed merged into develop (`git branch -r --merged develop`). Merge commits `e5261ab`, `b6b956e`, `fbe9aab` in git log are the audit record. Retroactive PRs add no value. | 3 remote branches |
| **IMG-ALT-DEBUG-1** | Next.js HMR cross-module callback staleness | OPEN. Optional refactor: move mutation call INTO dialog component, drop parent `onSubmit` indirection. Atom: [[nextjs-hmr-cross-module-callback-staleness]]. Low priority. | `pages/routemanagement/operators/images/ImageEditDialog.js`, `index.js:140-178` |
| F11-FOLLOWUP | B2B corporate CTA strip | DEFERRED. BD recommended. Awaits product decision on 280px slot. | TBD |
| F11-FOLLOWUP | Shared `<Accordion>` / `<FAQAccordion>` atom | DEFERRED. UX flagged. | `components/UI/` (new file) |
| RR-1-FOLLOWUP | `submit-review/[...slug].js:77` brittle slug fallback | API returns `booking_item_slug` only. Confirm contract. Low priority. | `pages/rate-review/submit-review/[...slug].js:77` |
| GSC-1 | GSC Crawled-Not-Indexed | Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists`. | `seoConfig.js:41`, `server-sitemap.xml` |
| CMA-1 | Contract Model Ambiguity | P1/P2 partial. Remaining: data inventory. | `operators/models.py` |
| FAQ-1 | ExperienceFAQ | P0-P2 done. Admin `ageRestriction` deferred. | `admin-dashboard/DayTripDetails.js` |
| AT-1 | Airport Transfer redesign | P0. Spec: `03-knowledge/transportation-category-audit`. | `AirportTransferRouteCard.js` |
| AT-2 | Airport-transfer width mismatch | Inner margins. | `StationInformation.js` etc. |
| 15 | refetchOnMountOrArgChange | Needs justification. | `useTripData.js:16,24` |
| 1 | AdminBookingSummaryViewSet auth | Needs frontend sign-off. | `orders/views.py` |
| 2 | Delete RefundViewSet | Waiting on zero DEPRECATED_ENDPOINT_USED. | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic. | `payments/urls.py` |
| 8 | Forex endpoint naming | Naming debt. | `cards/urls.py` |
| Nav | NavigationSection empty | Restart backend + populate. | `pages_info` |
| Explore | location_type CharField | Needs `Location` model change. | `stations/models.py` |
| HD-2 | CartButton dim (70%) | Low — acceptable. | `CartButton.js:116` |
| HD-3 | xl padding gap | Low. | `main-header.js:90` |
| HD-6 | Logo size jump | P2. | `main-header.js:66,95` |
| GAP-3 | Mobile position flip | P2. | `main-header.js:45-77` |
| GAP-5 | Nav hidden while searching | P2 — accepted. | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3. | `useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden md-xl | P3. | `main-header.js:95` |

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved)
