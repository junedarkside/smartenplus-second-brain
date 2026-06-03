# Frontend Test Infrastructure Audit — 2026-06-03

## Summary
Automated test team ran full suite (Jest + Playwright). Result: **BLOCK RELEASE**. Payment path untested, mobile black box, checkout broken.

---

## Test Results

| Suite | Total | Passed | Failed | Pass Rate | Coverage |
|-------|-------|--------|--------|-----------|---------|
| Jest (unit/integration) | 719 | 502 | 217 | 69.8% | 3.92% (threshold 70%) |
| Playwright (E2E) | 260 | 27 | 233 | 10.4% | 4 pages / 10 tested |
| **Combined** | **979** | **529** | **450** | **54%** | **FAIL** |

---

## Root Cause: Test Infrastructure Broken

**~60% of unit failures = config/mock issues, not logic bugs.**

### Unit (Jest) — 217/719 failed

**CRITICAL:**
1. `jest-axe` not installed — blocks a11y suite
2. MUI emotion v4/v5 mismatch — blocks checkout test suite entirely (`react.withEmotionCache is not a function`)
3. `BookButton.js` 0% coverage — payment path untested (CLAUDE.md payment gotchas have ZERO test coverage)
4. `useRouter` mock is static object, not `jest.fn()` — Next 14 API change broke ~20 tests

**WARNING:**
5. `toHaveId` matcher doesn't exist in `@testing-library/jest-dom` v6.9.1 — test bug, not production
6. `useTripPricing` decimal format: actual `"THB 800.00"` vs expected `"THB 800"` — test expectations stale
7. localStorage `SecurityError` — 45 tests blocked
8. `Response` undefined in jsdom — needs polyfill
9. `station_name.trim` — fixture shape mismatch vs real API

### E2E (Playwright) — 233/260 failed

**CRITICAL:**
1. `chromium-mobile` 100% fail — Webkit not installed OR real mobile product issues (Thai market ~60% mobile)
2. `/checkout` 30s timeout — money flow broken end-to-end
3. Payment path completely unverified — 0% `BookButton` coverage + no E2E payment spec

**WARNING:**
4. `localStorage` SecurityError (45 occurrences) — MSW/page setup issue
5. Element not found (53 occurrences) — selector rot after checkout SSOT refactor
6. MSW handler drift — backend API ahead of mocks
7. `waitFor` timeout (18 occurrences) — timing changed after `d516b7a` checkout loading SSOT refactor

---

## Fix Priority (4-5 dev days)

**Day 1:**
- `npm i -D jest-axe --legacy-peer-deps`
- Fix MUI emotion cache render wrapper (not `styled` mock)
- Fix `localStorage` SecurityError mock

**Day 2:**
- Diagnose `chromium-mobile` 100% fail
- Investigate `/checkout` 30s timeout (`useCheckoutLoading` SSOT hook)
- Fix `useRouter` mock: `jest.fn(() => ({...}))`

**Day 3:**
- Write `BookButton` unit tests (payment path, CLAUDE.md gotchas)
- Fix `toHaveId` → `toHaveAttribute`
- Update `useTripPricing` test expectations

**Day 4:**
- Sync MSW handlers with `smartenplus-backend` API
- Audit Playwright selectors for Tailwind class churn
- Add E2E specs for untested pages (6 pages missing)

**Day 5:**
- Add E2E payment spec (Omise success/fail/timeout)
- Re-run full suite, target: Jest 90% pass / 70% coverage, Playwright 80% pass

---

## Pages Tested

| Page | Unit Coverage | E2E Status |
|------|-------------|------------|
| `/` (home) | partial | PASS |
| `/trips` | **0%** | PASS |
| `/checkout` | blocked (C3) | **TIMEOUT** |
| `/bookings` | partial | NOT TESTED |
| `/account/profile` | partial | NOT TESTED |
| `/destinations` | partial | NOT TESTED |
| `/blog` | partial | NOT TESTED |
| `/airport-transfer` | partial | NOT TESTED |
| `/orders` | partial | NOT TESTED |
| `/booking` (payment) | **0%** | **NO SPEC** |

**Money flow (checkout → payment): 0% verified**

---

## Relevant Files

- `jest.config.js` — coverage threshold 70%, not enforced in CI
- `jest.setup.js` — Phase 3A mock work good for MUI, but `useRouter` mock wrong
- `playwright.config.ts` — 4 projects (desktop/mobile/tablet/small-desktop), chromium-mobile uses iPhone 12 on chromium
- `e2e/mocks/handlers.ts` — MSW handlers may drift from backend
- `e2e/cart/cart-management.spec.ts` — trip detail tests
- `e2e/checkout/checkout-flow.spec.ts` — checkout tests (timeout)
- `components/BookButton/BookButton.js` — **0% coverage, payment path**

---

## CLAUDE.md Connections

This audit confirms:
- Payment gotchas (CLAUDE.md "Payment — BUGS IF WRONG") have **ZERO test coverage**
- `cartActions.resetCart()` location verified (only on order pages)
- `expirePendingCharge` auth `?email=` only for guests
- `isPaymentLocked` cleared only by `onUnlockPayment()`
- `payment_failed` recoverable — valid path `ordering → payment_failed → paid`

All of the above are **completely untested**.

---

## Recommendation

**Block release.** Do not ship with 0% BookButton coverage + 100% mobile E2E failure + checkout 30s timeout.

After fixes: enforce `coverageThreshold` in `jest.config.js` so PRs fail below 70%.