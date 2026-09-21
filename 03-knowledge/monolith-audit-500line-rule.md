# Monolith Audit — 500-Line Rule (2026-09-15)

Cross-repo scan: FE + BE + AD. Files violating 500-line threshold.

## Thresholds (CLAUDE.md)
- GREEN < 200
- YELLOW 200–400
- ORANGE 400–500 (split if fails 4-gate test)
- RED > 500 (split regardless)

---

## FRONTEND (smartenplus-frontend)

### RED (>500 lines) — 23 files
Production (non-test):
- 1256 `pages/checkout/index.js` — checkout orchestrator, DO NOT split first
- ~~917  `helpers/wordpress/api.js`~~ — **DONE 2026-09-15** → split into `queries/posts.js` (445), `queries/categories.js` (145), `queries/pages.js` (146), `queries/tags.js` (13), `queries/routes.js` (13). `api.js` = 5-line barrel re-export.
- 867  `pages/checkout/PaymentComponent.js` — payment, split UI only after e2e tests
- 724  `pages/bookings/index.js` — page, split list/filter/sort
- 672  `helpers/checkoutPersistence.js` — extract date helpers first
- ~~627  `pages/server-sitemap.xml/index.js`~~ — **DONE 2026-09-15** → split into `lib/sitemap/` (blog/help/locations/products/routes/operators/airport-transfer/ref-articles/utils). Page = 36-line orchestrator. All GREEN.
- ~~622  `components/search/SlideCalendar2.js`~~ — **DONE 2026-09-15** → extracted `helpers/calendarUtils.js` (31) + `hooks/useSlideCalendar.js` (69). Component = 487 lines ORANGE (single-responsibility dense Tab JSX; passes 4-gate). All 5 callers unchanged.
- 617  `pages/destinations/[slug].js` — page, extract sections
- 583  `hooks/useSecureValidation.js` — pure hook, extract validation domains
- ~~554  `components/trips/TripItem.js`~~ — **DONE 2026-09-15** → 258 GREEN. Extracted TripItemAccordionContent.js (90), TripItemDetails.js (85), TripItemFooter.js (75), helpers/tripButtonProps.js (9). Activated 2 orphaned stub files. All callers unchanged.
- 542  `pages/homepagev2.js` — page orchestrator
- 508  `components/itinerary/TripDetail3.js` — extract panels
- 504  `components/trips/FilterTrip.js` — extract filter groups

Test files (lower priority): 716, 644, 642, 634, 614, 568, 517, 508, 504

### ORANGE (400–500 lines) — 30 files
Top production targets:
- 478 `helpers/getBillingAndOrder.js`
- 472 `hooks/useRateLimitedQuery.js`
- 463 `pages/account/profile.js`
- 441 `helpers/authHandlers.js`
- 414 `components/autocompletesearch/SearchInput.js`

---

## BACKEND (smartenplus-backend)

### RED (>500 lines) — 42 files
Critical (non-test):
- 3332 `operators/views.py` — LARGEST; split sequentially by concern last
- 2572 `products/views.py` — extract availability service first
- 1716 `orders/views.py` — extract service layer; keep viewset for URL routing
- 1687 `products/serializers.py` (was 1632, 2026-09-21: +55 lines, `has_live_seat_check` field) — 49 top-level classes (not 101 — corrected count); split by domain (list/detail/lookup/recommendation). **Bonus finding 2026-09-21**: two classes both named `TripSerializer` (line 268 dead/shadowed, line 668 live) — delete the dead one when this splits.
- 1523 `operators/admin.py` — admin-only, safe to split by entity
- 1425 `cs/views.py` — split by concern (OTP/Supabase/conversation)
- 1364 `dialogue/views.py` — split by entity + service layer
- 1252 `operators/models.py` (was 1228, 2026-09-21: +24 lines, `has_live_seat_check` property) — 34 top-level classes, clean natural seams (Contract+relations, Operator+mappings, day-tour scheduling, small lookups). **Risk assessed 2026-09-21, split declined**: signal-receiver silent-failure risk is the real danger here, not import errors — a `models/` package split can leave a `@receiver`-decorated function unregistered if its submodule isn't imported by `models/__init__.py`, and that fails silently (no crash, feature just stops working, e.g. slug generation or cache invalidation quietly dies). Migrations are unaffected regardless (key on app_label.ModelName not file path). User declined to risk it this session; do as its own dedicated PR with per-signal manual verification, not bundled with a feature branch.
- 1136 `carts/serializers.py`
- 1057 `products/services.py`
- 969  `stations/views.py`
- 969  `cards/models.py` — Omise-tied
- 938  `carts/utils.py` — imported by 8+ modules
- 881  `bookings/admin.py` — admin-only, safe
- 853  `payments/services.py` — **DO NOT SPLIT** (money-critical)
- 824  `orders/admin.py` — admin-only, safe
- 817  `orders/serializers.py`
- 791  `carts/tasks.py` — Celery task names must stay stable
- 745  `operators/management/commands/create_all_service_tours.py` — standalone, safe
- 707  `operators/serializers.py`
- 686  `orders/utils.py`
- 680  `stations/serializers.py`
- 680  `carts/views.py`
- 631  `Smartenplus/settings.py` — **DO NOT SPLIT** (monolithic by design)
- 625  `operators/management/commands/create_day_tours.py` — standalone, safe
- 589  `payments/views.py` — **DO NOT SPLIT** (payment API)
- 511  `pages_info/views.py` — simple CRUD, safe

### ORANGE (400–500 lines) — 10 files
- 494 `bookings/views.py`
- 498 `accounts/views.py`
- 422 `stations/models.py`

---

## ADMIN DASHBOARD (admin-dashboard)

### RED (>500 lines) — 18 files
- 1248 `pages/dashboard/command-centre/index.js` — split by tab
- 922  `components/forms/contract/NewContract.js` — large form, extract sections
- 697  `pages/routemanagement/contracts/index.js`
- 688  `pages/tickets/[id].js`
- 665  `components/contracts/filters/CombinedFilterDrawer.jsx`
- 607  `components/orders/CancelBookingDialog.js`
- 592  `pages/routemanagement/places/index.js`
- 576  `pages/bookings/[slug].js`
- 566  `pages/orders/index.js`
- 549  `pages/orders/[slug].js`
- 540  `pages/routemanagement/contracts/[slug].js`
- 527  `pages/routemanagement/trips/index.js`
- 518  `components/calendar/MobileAllotmentView.js`
- 514  `components/contracts/modals/RateCardEditModal.jsx`
- 511  `components/contracts/filters/StopSalesFilterDrawer.jsx`
- 503  `components/orders/RefundTable.js`
- 502  `components/orders/Refund.js`

---

## EXECUTION ORDER (least risk first, one file per session)

### TIER 1 — Safe Now
Test files → wordpress/api.js → management commands → admin.py files → pages_info/views.py

### TIER 2 — Safe with Care
UI components → page orchestrators → serializers → utility views

### TIER 3 — Caution
Celery tasks → shared utils → models → large views

### TIER 4 — DO NOT SPLIT
`payments/services.py`, `payments/views.py`, `pages/checkout/PaymentComponent.js`,
`pages/checkout/index.js`, `Smartenplus/settings.py`
(these are payment-critical or monolithic by design)

---

## Split Protocol
1. 4-gate test (CLAUDE.md)
2. `grep -r` all callers
3. Feature branch: `refactor/<filename-split>`
4. Split + re-export via index
5. Build + tests + smoke test
6. Vault atomize → `03-knowledge/` or `07-logs/`
7. Update `master-state.md`

## Living Document Rules

- **Claude prompts user before each split** — "Ready to split `<file>`?" User decides yes/no.
- **Auto-update trigger** — whenever a session adds/modifies lines in any tracked file, re-scan that file and update this report.
- **No batch** — one file per session, always user-approved.
- Last full audit: 2026-09-15
- Last targeted update: 2026-09-21 (2 files touched by seat-check-indicator feature, line counts + risk notes refreshed, not a full re-scan)

## Related Files
- FE CLAUDE.md — monolith thresholds + 4-gate test rules
- `docs/development/CODE_PATTERNS.md`
- `docs/operations/REFACTORING_WORKFLOW.md`
