# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-13 (session #106 — payment pending deadlock diagnosed + fixed)

**Achieved this session (#105–#106):**
- **Payment pending deadlock — diagnosed + FIXED.** Live prod bug order `PLB0229785`: charge PAID at Omise, order stuck `payment_pending` forever. Root cause: `finalize_payment` throws `PaymentAmountMismatchError` on webhook → swallowed → no recovery path (expire=400, reconcile skips non-PENDING, celery ignores PAID, retry=AlreadyPaidError without finalize).
- **3 backend fixes shipped** (`482cfc6` on BE `develop`, pushed):
  1. `ExpirePendingChargeView` — terminal charge + stuck order recovers instead of 400. PAID→verify Omise→finalize (no amount check). FAILED/REFUNDED→unlock to ordering. New `_recover_paid_stuck_order()`.
  2. `reconcile_gateway_charge` — PAID+stuck order retries `finalize_payment` on every order-detail read (auto-heals webhook-lost route).
  3. `_handle_existing_charge` — finalize before `AlreadyPaidError` on locally-PAID charge.
- **16 new tests** (test_expire_view, test_reconciliation, test_handle_existing_charge). **278 total payment tests pass.**
- **Vault atom created + updated:** [[payment-pending-deadlock-2026-06-12]] — full root cause, reproduction steps, fix docs, status=FIXED.

**Resume point (EXACT):**
1. **PAYMENT-PENDING-DEADLOCK — production recovery for PLB0229785:**
   `POST /payments/order-charge/chrg_test_67zrcauou19uk2t655l/expire/` with owner email → Fix 1 path finalizes order. Or Django shell: `finalize_payment(Order.objects.get(order_id='PLB0229785'))`.
2. **PAYMENT-FIX — open PRs via GitHub UI** (still open from prev session):
   - BE: `smartenplus-backend/fix/payment-deep-review-2026-06-12` → `develop` (head `6937f39`)
   - FE: `smartenplus-frontend/fix/payment-deep-review-2026-06-12` → `develop` (head `8430805`)
3. **KB atomization** — 12 KB gaps from verification report. Fix M8 inaccuracy in [[payment-backend-charge-flow]] §5 first.
4. **CROSS-SELL-BD-INVENTORY** — BD task. No eng work.
5. **AT-1** — Airport Transfer redesign. Awaits user direction.
6. **Item 2** (Delete RefundViewSet) — waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs.

**Next session: starting state**
- vault: `master` @ (this commit)
- BE `develop` @ `482cfc6` (clean, pushed) — deadlock fix live
- FE `develop` @ `dae26da` (clean)
- BE untracked: `.next/`, `docs/agent-policy/`, `docs/api/PUBLIC_ENDPOINTS.md`, `docs/deployment/DOCKER.md`, `docs/operations/ENV.md`, `docs/technical/` (separate work)
- admin-dashboard: `main` @ `4a6c03b` (untracked docs — separate work)
- content: `master` @ `3756e5b` (clean)

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **PAYMENT-FIX** | Implement 5 HIGHs + priority MEDIUMs from payment deep review | **ALL 5 BATCHES SHIPPED + PUSHED + 8/8 E2E AUTOMATED + WEBHOOK GAP CLOSED.** BE 7 commits `d7af0e9..6937f39` pushed. FE 8 commits `a3c8c80..8430805` all pushed. **8/8 UI E2E now automated** via `payment-auto-qa.spec.ts` + fixture CLI. **Webhook gap closed** via Tailscale. 119 tests pass. **M4 retracted.** **BONUS: deadlock fix `482cfc6` shipped directly to BE `develop`** (278 BE tests pass). Remaining: (a) open 2 PRs via GitHub UI for original deep-review branches, (b) close item after merge. KB gaps: 12 (batch with next `/lint-vault`). | [[payment-deep-review-2026-06-12]], [[payment-pending-deadlock-2026-06-12]], [[payment-auto-test-results-2026-06-12]], [[omise-webhook-tailscale-local-testing]] |
| **BOOKING-PAY-FIX-1** | Fix 4 verified bugs from booking-payment e2e audit | CLOSED #94. Merged `fix/checkout-stable-id-cleanup` → `develop` (`f271aef`). 53/53 tests, SM-1–SM-4 passed. | `hooks/checkout/useCartSync.js`, `components/UI/BookButton.js:41-43` |
| **BOOKING-PAY-REPRO-1** | Runtime repro C1 (formData lost on hard refresh) + C2 (transient error nukes cartId) | CLOSED #97. C1: `isCartLoaded &&` guard in clear-assignments effect (`checkout/index.js:188`). C2: `if (error?.status === 404)` in catch (`check-and-createcart.js:67`). Commit `cb817d9` on `develop`. | `pages/checkout/index.js:188`, `components/HOC/check-and-createcart.js:67` |
| **CROSS-SELL-MERGE** | Merge `feat/redesign-people-also-book-cards` → `develop` | CLOSED #97. Branch confirmed fully merged (`git merge-base --is-ancestor` → FULLY MERGED). `CheckoutRelatedTrips` mounted at `checkout/index.js:1010`. All recommendation components present. Remaining work is BD inventory only → see CROSS-SELL-BD-INVENTORY. | done |
| **SEO-SITEMAP-FIX** | Implement fixes from whole-site SEO+sitemap audit | MERGED 2026-06-12. P0+P1+P2 `1f3f7a2` merged → develop `d88f50b`, pushed. Fake reviews ×4 deleted, sitemap 128→86 URLs, noindex fixed ×5 pages, dead JSON-LD pipeline removed. Build exit 0, greps clean. **Remaining:** deploy to prod, GSC Googlebot/WAF verify (manual), nginx 301s (infra), P3 dead-code sweep. Soft-404 stays with GSC-1. | develop `d88f50b`, [[seo-sitemap-whole-site-audit-2026-06-11]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell | OPEN. BD task — no eng work. Needs: (1) return route Koh Lipe→Hatyai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Cross-sell auto-hides until `recommendation_count > 0`. | BD action |
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
