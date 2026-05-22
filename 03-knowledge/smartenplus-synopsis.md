# SmartEnPlus Synopsis

## Summary
Thailand transport booking platform — buses, ferries, speedboats, trains, airport transfers. English-speaking international tourists. 3-repo Next.js 14 + Django ecosystem.

## Why It Matters
Orientation note for any new session. Single-page snapshot of what this project is, current production state, and open work.

## Detail
- **Stack:** Next.js 14 (Pages Router) + React 18 · Redux Toolkit + RTK Query · MUI + Tailwind · NextAuth.js · Omise (payments) · Formik + Yup · Django 4.2 + DRF · PostgreSQL 14 + Redis 7.2 + Celery
- **3 repos:** `smartenplus-frontend` (customer booking) · `smartenplus-backend` (Django API) · `admin-dashboard` (internal admin)
- **Payment:** Omise-only (Stripe dropped 2026-05-15). PromptPay QR, credit card, internet banking, e-wallets. Single `finalize_payment()` source of truth. `locked_amount` freezes charge after first QR. `payment_failed` is recoverable.
- **Auth:** NextAuth (Google, Facebook, LINE, Naver, Apple). Session shape: `{ id, accessToken, user: { email } }`. Logout: CSRF fetch → `/api/auth/force-logout` (never NextAuth `signOut()`).
- **Checkout:** SSR disabled. Guest mode via redux-persist. Cart item key: `item.id`. Chronological sort by `traveling_date`.

## Current Production State (2026-05-22)
- Frontend `main` @ `a8305ae` — trip detail width/gap/rounded fix live
- Backend `develop` @ `4140cbd` — locked_amount db_index
- Admin `main` @ `c06af90` — RTK Query Main.js refactor
- All repos clean. Uncommitted = audit artifacts + CLAUDE.md tweaks only.

## Open Work
1. `AdminBookingSummaryViewSet` unauthenticated (backend `orders/views.py`)
2. Delete `RefundViewSet` legacy (waiting prod log confirmation)
3. Remove Stripe 410 stub (waiting zero traffic)
4. Forex endpoint naming debt (public on admin path)
5. Deferred trip detail audit: CF1, CF9, VD2/VD3, VD9

## Constraints / Gotchas
- Cart item key: `item.id` (`stable_id` removed 2026-02-13)
- `payment_failed` = recoverable, not terminal
- Canonical charge = LATEST `GatewayCharge`
- ISR cache: `revalidate: 300` — deploy must clear Docker volume
- `useEffect` chains forbidden — use `useMemo` or single combined effect
- Helpers return `null` + `console.warn`, never throw
- Cross-repo: change one → check others

## Related
- [[master-state|Master State]] — live session state, branches, loose ends
- [[README|SmartEnPlus Project]] — full project overview
- [[payment-integration]] — payment patterns in depth
- [[backend-architecture]] — Django app structure
- [[nextjs-patterns]] — ISR, SSR, RTK Query patterns
