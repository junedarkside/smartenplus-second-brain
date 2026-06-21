# Architecture Guardrails

## Payment
- `finalize_payment(order)` — single source of truth. Never duplicate.
- `select_for_update()` + `payment_finalized_at` guard
- `locked_amount` — freezes charge amount after first QR
- `payment_failed` is recoverable — not terminal
- Omise sends NO webhook on PP/MB expiry
- Idempotency: SHA-256(method, amount, currency)

## DB / ORM
- Lock order: Coupon → Order → BookingItem → TimeSlot. Never invert.
- `on_delete=PROTECT` on audit-trail FKs. `db_index=True` on hot fields.
- Reverse FK ORM path: use model's `related_name` or Django default (`<model>` lowercase, no `_set`)

## Celery
- Pass IDs to tasks, not model objects.
- All tasks: `bind=True, max_retries, default_retry_delay`

## Infra
- Memory: web 512MB | celery-worker 384MB | redis 64MB = ~960MB
- `WebhookEvent.get_or_create` outside `atomic()`

## Git Branch Policy — MANDATORY (all repos)
- **NEVER commit directly to `main` or `develop`**
- Always branch from `develop`: `git checkout develop && git pull && git checkout -b <type>/<desc>`
- Branch naming: `fix/`, `feat/`, `refactor/`, `chore/`
- Merge target: `develop` only. `main` = production, deploy-only flow.
- Violation = no rollback, broken prod, lost audit trail.

## Frontend Patterns
- **Tailwind JIT:** Never interpolate into arbitrary class strings — only static strings scanned at build time
- **Currency:** `useCurrency()` → display only. API always receives THB. Pattern: `formatCurrency(value / rate, currency)`
- **Debounced inputs:** `lodash.debounce` in `useRef`, cancel on unmount. 400ms standard for filter inputs.
- **`formatCurrency(0)`:** Guard = `=== null || === undefined` not `!value`
- **PriceRangeSlider contract:** Internal values THB. Display converts via context. Never pass converted value to API.

## Header Search (2026-06-02, updated session #27)
- `HeaderSearchContext` — single source of truth. Clears only on non-shallow navigation.
- `FilterTripsPage.js` + `homepagev2.js` + `FilterDayTripsPage.js` call `setSearchBarContent()`
- `FilterDayTripsPage` passes `filters`+`updateFilter` into compact `ActivitySearch` — single state source, no dual-hook race
- `SearchDialogTrigger variant="input"` — white bg, NO left icon, `bg-fb-blue` icon-only submit, `h-10`, input `h-full`
- `PageMain` in `layout.js` — adaptive padding prevents layout gap
- `ActivitySearch` patterns: `isControlled` + `useDayTripFilters({ enabled })` + `didMountRef` + `isTypingRef`. See [[react-dual-hook-url-race]]

## Popular Routes Section (2026-05-28)
- `PopularRoutesSection.js` — NO `ContentCard` wrapper on happy path
- `Section` gets `py-6 px-4 xl:px-0`
- `ContentCard` hardcoded `bg-white` — cannot override with Tailwind

## Nav
- `NavigationSection` + `NavigationItem` — two-level hierarchy
- API cached 1hr server-side. Frontend fallback: `constants/navConfig.js`
- Migration 0010 applied locally — production needs `migrate`
