# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-19 (session #134 END)

**Achieved this session (#134) — Diagnosed local Celery `unregistered task` error, filed operational atom. No code change.**

- **Diagnosed** local worker error `Received unregistered task 'operators.tasks.revalidate_frontend_isr'` / `KeyError`. Root cause: worker process booted **before** #129 (`0f2d108`) added the task; `autodiscover_tasks()` runs once at boot, so the registry is stale. Web reload ≠ worker reload. Unregistered messages are **discarded, not retried**.
- **Confirmed benign in dev** (triple-guard): (1) stale worker discards, (2) local `.env` has empty `REVALIDATION_SECRET` → task no-ops at `tasks.py:70`, (3) frontend routinely down during admin-dashboard testing → POST would fail anyway. Error = log spam; fix = restart worker.
- **Prod exposure clarified:** container worker (`docker-compose-deploy.yml:34`) → `docker compose up -d --build` auto-recreates = safe; at-risk only on partial `restart web`. Reinforces the #129 deploy checklist (restart worker + non-empty `REVALIDATION_SECRET`).
- **Filed atom** [[celery-unregistered-task-stale-worker]] (symptom signature, why, silent-loss, local/prod, not-confused-with, side hardening), cross-linked from [[celery-task-over-bare-thread-django-signals]]; updated `index.md` + `log.md`.
- **Side item flagged:** `celery-worker` + `celery-beat` lack `restart: always` in `docker-compose-deploy.yml` — crash won't auto-recover.
- **Pruned** admin-dashboard `feat/contract-not-suitable-for` (local `a70630b` + remote) — merged to develop `bdf85ff`, verified fully-merged before delete.

**Resume point (EXACT):**
1. **Deploy BE develop→main** → recommendation engine (zones, P0, image/price/logo_url) reaches prod. Run prod seed cleanup (detach dummy trips) / `seed_demo_destination` if testing on prod data.
2. **Deploy FE develop→main** → zone UI + anchor/recType fixes to prod.
3. **#129 ISR PROD ACTIVATION** (folds into step 1): BE develop→main + prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (this session's lesson — else `unregistered task`, see [[celery-unregistered-task-stale-worker]]). Then smoke-test: edit a contract, confirm worker log shows `ISR revalidated slug=... status=200`.
4. **Vault hygiene:** mark anchor-flip + price-floor DONE in roadmap note; retire stale [[recommendation-anchor-first-transport-rule]] (now contradicts shipped code).
5. **Next eng (deferred, tracked):** slot-waste `exclude_ids` API (ESSENTIAL renders short when a cart item overlaps a rec), `recommendation_purchase` GTM (then measure zone conversion), UPGRADE zone (`upgrade_of` FK), multi-destination 2-anchor, weekly trending.

_(Session #133 block archived → `07-logs/session-history.md`. Note: BE `main` is now `bb5c199`, FE `main` `4c9354b` — both repos moved since #133; recommendation-engine deploy state should be re-verified against current `main` before step 1.)_

---


**Carry-forward bugs (open, from #127):**
- **BE-IMAGE-DEDUP** tech debt (Section 2) — `process_operator_image` vs `process_review_image` dup + upload-validation copy-pasted ×5 files.
- silaphat `Operator.description` holds route notes, not real about-copy — data quality.
- `booking_count_yesterday` (`products/serializers.py:353-363`) — rolling 24h not calendar yesterday.
- Dual sort vocab: QuickSortPills PascalCase vs SortDropDown `-booked_count`.
- Prod backend git history diverged from origin (merge-noise) — pulls always merge, not FF. Cosmetic.

**Next session: starting state** (live git 2026-06-19, all clean)
- vault: `master` @ new commit (this adds #134)
- BE: `main` @ `bb5c199` (clean) — `feat(operators): add not_suitable_for field to Contract`. ⚠️ moved since #133's `ae31f1f` — re-verify recommendation-engine deploy state against current `main`.
- FE: `main` @ `4c9354b` (clean) — `fix(activities): make category chip visibly clickable`.
- admin-dashboard: `main` @ `bdf85ff` (Not Suitable For multi-select merged; `feat/contract-not-suitable-for` pruned local+remote)
- content: `master` @ `3756e5b` (clean)
- ⚠️ #129 ISR activation: prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (else `unregistered task` — [[celery-unregistered-task-stale-worker]]).

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **REC-CHECKOUT-ZONES** | Checkout "Complete your trip" recommendation engine: P0 hybrid fix + zones (ESSENTIAL/POPULAR/SIMILAR) + matrix + transport finder + per-zone caps + price-bug + experience-first anchor + recType-follows-anchor + card-count tuning + add_cart GTM + mobile cap + seed command. **MERGED to develop #133** (BE `ae31f1f`, FE `0877d23`), branches pruned. | **MERGED, NEEDS DEPLOY** develop→main both repos. Then prod seed cleanup. | `products/services.py`, `components/recommendations/*`, [[recommendation-engine-completion-roadmap]] |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when a cart item overlaps a backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. Medium. | OPEN #133 — deferred, tracked. | `smartenplus-backend/products/services.py` get_recommendations, [[recommendation-engine-completion-roadmap]] |
| **REC-PRECOMPUTE-CACHEKEY** | Low. `products/tasks.py:67` precompute builds cache key `recommendations:{id}:{type}:{limit}` (4-part) but `get_recommendations:667` runtime key is 5-part (`:{rate_date or 'none'}`). Precompute writes never hit at runtime → wasted warm. Pre-existing, found in #132 verify. | OPEN #132 — out of scope of P0 fix. | `smartenplus-backend/products/tasks.py:67` |
| **ISR-REVALIDATE-GAP** | Admin contract edit not reaching prod `/activities/detail` (revalidate 3600) + `/trips/detail` (revalidate 300). Backend busts Redis correctly (`operators/signals.py:33`); Next.js Pages-Router ISR HTML never told to regen + no `/api/revalidate` route → stale, forever on cold pages (persistent `next_cache` volume). Fix (4 steps, build order in plan): (1) BE `daily_counter`→`.update(F+1)` enabler stops per-view post_save, (2) FE `pages/api/revalidate.js` POSTs `{slug}` owns path map, (3) BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, (4) `REVALIDATION_SECRET` both repos incl GH Actions runtime path. Task no-ops on empty secret. | **IMPLEMENTED #129 → develop** (BE `4eaaf8d`, FE `66d896e`). All 4 steps done + verified (29 tests, manage.py check, ESLint, no-storm proof). **Prod root cause found:** `FRONTEND_URL` was apex → 301→www dropped the POST; fixed default→www (`d37dee3`). **FE SHIPPED #130** (main `35c524d` carries ISR route). **BE ACTIVATION PENDING:** deploy BE develop→main + set prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (#134: stale worker = `unregistered task`, msgs discarded — [[celery-unregistered-task-stale-worker]]), then smoke-test (see Section 1 resume). | `operators/signals.py`, `operators/tasks.py`, `products/views.py:884`, `Smartenplus/settings.py:373`, FE `pages/api/revalidate.js`, `deploy-ghcr.sh` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: public LIST `ContractSerializer` doesn't expose `tour_duration_days`, so cards can't show "N Days" (detail page works, uses `__all__`). FE-only fix #130 chose omission over false "1 Day". Option B: add `tour_duration_days` to list serializer `fields`. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional follow-up, low priority. FE helper unchanged either way. | `smartenplus-backend/operators/serializers.py` (ContractSerializer), [[category-aware-duration-formatter]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate, pre-existing). Cluster 1: WebP resize/compress algorithm duplicated ~2-3× — `operators/utils.py:process_operator_image` (now parametrized #126b), `dialogue/utils.py:process_review_image` (120KB hardcoded), plus WebP/thumbnail code in `operators/admin.py`. Cluster 2: upload validation (ext whitelist + size) copy-pasted across 5 files (`stations/views.py`, `operators/utils.py`, `operators/views.py`, `pages_info/models.py`, `dialogue/utils.py`) each with own constants → drift risk. Consolidate → one `core/image_utils.py`: `process_image_to_webp(file, *, max_output_size, max_dimensions)` + `validate_upload(file, *, allowed_ext, max_size)`, migrate all callers. | OPEN #126 — dedicated refactor session. High blast radius (operators/dialogue/stations/pages_info), zero user value, all spots work. Do NOT bolt onto feature work. | `operators/utils.py`, `dialogue/utils.py` |
| **VAULT-DATE-RENAMES** | 105 files embed dates in filenames (violates "no dates in filenames" rule). Rename breaks every inbound wikilink. Needs separate planning round: `git mv` + atomic search-replace of all `[[old-name]]` → `[[new-name]]`. | OPEN #125 — next-wave vault work. | [[vault-optimization-snapshot-2026-06-16]] |
| **SEO-SITEMAP-FIX** | Implement fixes from whole-site SEO+sitemap audit | MERGED 2026-06-12. P0+P1+P2 `1f3f7a2` merged → develop `d88f50b`, pushed. Fake reviews ×4 deleted, sitemap 128→86 URLs, noindex fixed ×5 pages, dead JSON-LD pipeline removed. Build exit 0, greps clean. **Remaining:** deploy to prod, GSC Googlebot/WAF verify (manual), nginx 301s (infra), P3 dead-code sweep. Soft-404 stays with GSC-1. | develop `d88f50b`, [[seo-sitemap-whole-site-audit-2026-06-11]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell | OPEN. BD task — no eng work. Needs: (1) return route Koh Lipe→Hat Yai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Cross-sell auto-hides until `recommendation_count > 0`. **All 4 FE surfaces already live and verified 2026-06-13. GTM `item_category` + activity-detail accuracy ALSO already shipped (`hooks/useOmisePayment.js:59`+`:144`, `RelatedExperiences.js:7`) — were wrongly listed as open eng work.** Only BD inventory blocks value. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2, not urgent). See [[cross-sell-integration-status-2026-06-13]]. | BD action |
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
