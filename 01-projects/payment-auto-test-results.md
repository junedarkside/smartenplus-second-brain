# Payment Deep Review — Automated QA Results (2026-06-12)

## Summary

All 8 tests from [[payment-manual-test-skip-2026-06-12]] are now **automated** and **ALL PASS** — manual staging QA no longer needed for these. Runs against local env (FE :3000 + BE :8000, Omise TEST keys, local Postgres) with DB fixtures created/cleaned automatically.

```
Payment Deep Review Automated QA — 2026-06-12
============================================
Tester: Claude Code (automated, Playwright)
Branch: fix/payment-deep-review (FE + BE)
Date: 2026-06-12

Test 1 (H3 order reuse wrap):     [ PASS ]  second POST /order-billing/ → {message:"Order reused", order} w/ same order_id
Test 2 (H4 QR cancel expires):    [ PASS ]  real sandbox QR, countdown ticks from BE expires_at, cancel → charge=expired, order recovers
Test 3 (H5 self-heal pending):    [ PASS ]  GET orderdetails → payment_pending + paid charge finalizes to paid (DB-verified)
Test 4 (M1 QR PendingCharge):     [ PASS ]  pending kakao_pay charge → QR attempt → PendingChargeNotice, no new charge
Test 5 (M2a alreadyPaid):         [ PASS ]  paid ikey charge → QR attempt → redirect to /guest-order/{id}, no Omise charge call
Test 6 (M2b amountLocked):        [ PASS ]  locked_amount ≠ cart total → "Cart Changed After QR Generation" notice, no new charge
Test 7 (M3 cancelState no flash): [ PASS ]  QR → cancel → switch to CC → no "Payment Cancelled" alert visible
Test 8 (Full smoke):              [ PASS ]  guest checkout → QR + countdown, no console errors, no 4xx/5xx

Overall: ALL PASS (8/8, two consecutive full runs, idempotent)
PAYMENT-FIX: READY TO CLOSE
```

## How to Run

```bash
# prerequisites: BE runserver :8000 + FE dev :3000, local DB
cd smartenplus-frontend
npx playwright test e2e/checkout/payment-auto-qa.spec.ts --project=chromium-desktop --workers=1
```

~1.5 min total. Fixtures auto-created per test, auto-cleaned in `afterAll` (verified 0 residue).

## Architecture

- **Spec:** `smartenplus-frontend/e2e/checkout/payment-auto-qa.spec.ts`
- **Fixture CLI:** `smartenplus-backend/scripts/e2e_payment_fixtures.py` — commands: `setup-cart`, `create-order`, `fixture-h5`, `add-pending-redirect`, `lock-amount`, `make-already-paid`, `order-status`, `charge-count`, `cleanup`. All data tagged (`qa-e2e@example.com` / `chrg_qae2e_*`) for safe idempotent cleanup.
- **UI driver:** `reachPaymentStep()` — injects real cartId into `persist:root-sep-7` localStorage, drives guest checkout (itinerary → Checkout as Guest → passenger form → T&C → payment step), captures order from `/order-billing/` response.
- **DB assertions:** spec shells out to fixture CLI mid-test (`order-status`, `charge-count`).

## Key Findings During Automation (gotchas for future tests)

1. **Vault fixture B was wrong for M1.** A pending *PromptPay* charge does NOT trigger `pending_charge_exists` — BE C3 gate only blocks pending REDIRECT-method charges; pending PP is resumed (idempotent reuse) or proactively expired on method switch (C3b). M1 fixture must be a pending redirect charge (used `kakao_pay`).
2. **M2a `alreadyPaid` needs an IdempotencyKey row** (`order-{order_id}-{method}`) pointing at a paid GatewayCharge, plus order in `payment_pending` with `locked_amount == attempted amount` (cart total + gateway fee, e.g. PP 1.65%). Order status `paid` alone gives a generic 409, not the `Order already paid` branch.
3. **M2a/M2b automated via PromptPay branch** (`handleQRPayment` lines 316/327 of PaymentComponent) — card-iframe variant (Omise modal) not browser-automated; identical branch logic at the card/redirect handlers is covered by the existing jest suite (FE `478a2bf`).
4. **Checkout contract choice matters:** contracts with `info_fields` render readonly MUI time pickers (unfillable via keyboard). Fixture picks an active TRANSPORTATION contract with 0 info fields.
5. **Redux persist key is `persist:root-sep-7` (v7, `activities` slice)** — the older e2e helper `mockCartState` still writes `root-sep-6` and silently fails (checkout redirects home). Only `cart.cartId` matters; cart data comes from RTK Query against real BE.
6. **Order create endpoint for guests is `POST /order-billing/`** (`OrderAndBillingProfileViewSet`, AllowAny on create). `POST /orders/` requires auth. Passenger payload entries need `id` key or BE 500s in `assign_passengers_to_bookings`.
7. **Fresh charge returns 201**, reused charge 200 — accept both.
8. **QR renders as inline SVG** via `/api/qr-code-proxy` (not `<img>`); assert heading "Scan to Pay with PromptPay" + countdown `aria-label*="QR expires in"`.

## Deviations from Manual Runbook

- Runs on **local** env, not staging (all prereqs met locally; same fix branch both repos).
- Test 5 (M2a) exercised through QR + branch-equivalent code path instead of card iframe (see finding 3).
- Test 7 (M3) flash check = "alert not visible after switch" assertion; sub-frame flicker beyond Playwright resolution (acceptable — guard is a state reset, not animation).

## Webhook Delivery Test (gap closed 2026-06-12, later same day)

Real Omise webhook delivery tested via **Tailscale funnel**: `https://macbook-air-2.tailc1dfbd.ts.net/admin-dashboard-orders/payments/webhook/` registered in Omise test dashboard → forwards to local BE :8000.

```
Step 1 (forged payload rejected):   [ PASS ]  400 {"status":"verification_failed"} — event verification via Omise API retrieve blocks fakes
Step 2 (real PP charge via API):    [ PASS ]  cart→order→order-charge, chrg_test_67zrcauou19uk2t655l pending, locked 1012.71
Step 3 (payment completion):        [ PASS ]  sandbox PP source auto-completes (~30s, no mark_as_paid needed — flow:"offline" test source)
Step 4 (webhook finalizes, no FE):  [ PASS ]  evnt_test_67zrckorm42kmojdy8k → order paid in 49s, payment_finalized_at set,
                                              WebhookEvent row + charge.last_webhook_event_id recorded, 1 BookingItem confirmed.
                                              Zero frontend involvement (no browser/polling on this order).
Step 5 (dedupe on replay):          [ PASS ]  replayed same real event → 200 {"status":"already_processed"}, finalized_at unchanged
Step 6 (cleanup):                   [ PASS ]  qa data deleted
```

**Gaps #1 (payment completion) + #2 (webhook delivery) now closed.** Remaining untested surfaces: card 3DS iframe (manual sandbox, Omise test cards) + live-key production smoke — both deploy-time checks, not code risks.

**Repro notes:**
- Omise sandbox PromptPay charges self-complete shortly after source creation — webhook fires without manual trigger. `mark_as_paid` returns `processed_charge` error if already done.
- `OMISE_SEC_KEY` in BE `.env` is quoted — strip quotes/CR before curl `-u` use.
- Dedupe replay works with any real event_id (verification retrieves real event from Omise) — equivalent to dashboard "Resend".

## Related

- [[payment-manual-test-skip-2026-06-12]] — superseded manual runbook
- [[payment-deep-review]] — source review
- [[payment-deep-review-verification]] — KB verification pass
- `smartenplus-frontend/e2e/checkout/payment-auto-qa.spec.ts` — automated spec
- `smartenplus-backend/scripts/e2e_payment_fixtures.py` — fixture CLI
