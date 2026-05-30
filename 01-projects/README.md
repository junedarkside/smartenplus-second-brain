# SmartEnPlus — Project Overview

## Summary
Thailand transportation booking platform. Buses, ferries, speedboats, trains, airport transfers. Target: English-speaking international tourists.

## Status
Active.

## Stack
- Next.js 14 + React 18 (Pages Router)
- Redux Toolkit + RTK Query
- MUI + Tailwind CSS
- NextAuth.js (Google, Facebook, LINE, Naver, Apple)
- Omise (payments)
- Formik + Yup
- Django 4.2.16 + DRF (backend)
- PostgreSQL 14 + Redis 7.2 + Celery (backend)
- AWS S3/SES (backend)

## 3-Repo Ecosystem

| Repo | Role |
|------|------|
| `smartenplus-frontend` | Customer booking platform (this project) |
| `smartenplus-backend` | Django REST API — payments, bookings, operators, orders, tours |
| `admin-dashboard` | Internal admin panel |

API changes → update frontend AND admin-dashboard.

## Key Facts
- Cart item keys: `item.id` (stable_id removed 2026-02-13)
- Checkout sorting: chronological by `traveling_date` (earliest first) on ALL steps
- Checkout SSR: disabled via `dynamic(() => Promise.resolve(Index), { ssr: false })`
- ISR cache: `revalidate: 300` on trip detail pages
- Guest mode: `isGuestMode` in checkout-slice, persisted via redux-persist
- Logout: direct CSRF + signout fetch → `/api/auth/force-logout` (302). Never use NextAuth `signOut()`
- Self-profile: `GET /api/user/` (token-based). Admin-only: `GET/PUT /api/users/{id}` since 2026-05-07
- Order status: `payment_failed` is recoverable, not terminal

## Architecture
- See [[architecture]] (frontend)
- See [[backend-architecture]] (backend)
- Payment system: [[payment-system]]
- Checkout flow: [[checkout-flow]]

## Dev Commands
- `npm run dev` — localhost:3000
- `npm run build` — production build
- `npm ci --legacy-peer-deps` — install deps

## Related
- [[nextjs-patterns]]
- [[payment-integration]]
- [[design-systems]]
- [[backend-architecture]]
