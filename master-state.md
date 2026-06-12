# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-12 (session #102 wrap)

**Achieved this session (#102):**
- **Payment deep review — KB verification + implement plan + all 5 batches shipped + pushed + E2E green** — 3 Explore verifier agents cross-checked 5 HIGHs + 18 MEDIUMs from [[payment-deep-review-2026-06-12]] against ~1700 lines of vault payment/omise KB + read-only code spot-checks. **20 CONFIRMED · 2 REFINED (H1, M17) · 1 REFUTED (M4, retracted) · 1 KB inaccuracy (M8) · 12 KB gaps surfaced.** Reports: [[payment-deep-review-verification-2026-06-12]] + [[payment-implement-plan-2026-06-12]]. **All 5 batches shipped to `fix/payment-deep-review-2026-06-12` branches and PUSHED to origin:**
  - **BE (7 commits, pushed):** `d7af0e9` H3 order-reuse wrap · `3be676b` H2+M10 410 legacy routes · `f1c17b5` H1+M8 amount validation + guest email · `6a481df` H5+M5+M9 reconcile + BaseError + orphan expire · `67b490a` M17 KakaoPay mapping · `e685fc8` BE unit tests · `6937f39` test path/constraint fixes
  - **FE (4 commits, pushed):** `a3c8c80` H4 charge_id + charge_created_at · `294c8fc` M1+M2+M3+M17 FE branches + KakaoPay/Alipay contract · `478a2bf` FE jest tests (84/84 ✅) · `c7caaf3` Playwright E2E (5 API + 7 UI skip)
  - **FE follow-up (2 commits, NOT pushed — same branch, awaiting PR):** `4f88093` fix unterminated-string in skipped smoke test comment (parser blocker) · `8430805` H2+M10 POST tests assert CSRF 403, 410 covered by GET — **7/7 Playwright API tests now PASS (was 5/7), 8 skip, 0 fail**.
  - **Tests total:** 20 BE unit + 84 FE jest + 7 Playwright API (all passing) + 8 Playwright UI (skip) = 111 passing, 8 E2E skipped.
  - **gh CLI not installed** → PRs open manually via GitHub web UI. No PRs opened yet.
  - **BE untracked noise:** `.next/`, `docs/agent-policy/`, `docs/api/PUBLIC_ENDPOINTS.md`, `docs/deployment/DOCKER.md`, `docs/operations/ENV.md`, `docs/technical/` — separate work, not part of this branch.

**Resume point (EXACT):**
1. **PAYMENT-FIX PRs** — open 2 PRs manually via GitHub UI: BE `fix/payment-deep-review-2026-06-12` → `develop` (BE 7 commits, head = `6937f39`), FE same (FE 6 commits incl. 2 follow-ups, head = `8430805`). gh CLI not installed in this environment.
2. **PAYMENT-FIX staging QA** — deploy branches to staging, run smoke tests (cart → checkout → PP/QR → webhook → paid) + 8 Playwright UI tests (unskip after staging data ready). Mark PAYMENT-FIX CLOSED only after staging green.
3. **KB atomization** — 12 KB gaps from verification. Recommend batch with next `/lint-vault` (split into 2 sessions: gaps 1–6 first, 7–12 follow). Fix M8 KB inaccuracy in [[payment-backend-charge-flow]] §5 first.
4. **CROSS-SELL-BD-INVENTORY** — BD task. No eng work. Needs Koh Lipe return route + DAY_TOUR + SPA contracts.
5. **AT-1** — Airport Transfer redesign. Awaits user direction.
6. **Item 2** (Delete RefundViewSet) — waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **PAYMENT-FIX** | Implement 5 HIGHs + priority MEDIUMs from payment deep review | **ALL 5 BATCHES SHIPPED + PUSHED + E2E GREEN.** BE 7 commits `d7af0e9..6937f39` pushed. FE 6 commits `a3c8c80..8430805` (last 2 NOT pushed — follow-up: 4f88093 parser fix, 8430805 CSRF-aware assertions). **7/7 runnable Playwright API tests pass** (was 5/7), 8 UI tests skip, 84 jest pass, 20 BE unit pass. **M4 retracted.** Remaining: (a) push FE follow-up commits + open 2 PRs via GitHub UI, (b) staging QA + unskip 8 UI tests, (c) close item after staging green. KB gaps: 12 (recommend batch with next `/lint-vault`). | [[payment-deep-review-2026-06-12]], [[payment-deep-review-verification-2026-06-12]], [[payment-implement-plan-2026-06-12]] |
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
