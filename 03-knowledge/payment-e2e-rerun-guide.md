# Payment E2E — How to Rerun Automated Tests

## Summary

One command reruns all 8 payment E2E tests locally. No staging, no manual fixtures, no test data cleanup needed.

## Prerequisites

All must be running before executing the test command:

| Requirement | How to start |
|---|---|
| FE dev server `:3000` | `cd smartenplus-frontend && npm run dev` |
| BE runserver `:8000` | `cd smartenplus-backend && venv/bin/python manage.py runserver` |
| Local Postgres | must be running (check `pg_isready`) |
| BE `.env` with `OMISE_SEC_KEY=skey_test_...` | already set — do not add quotes or trailing spaces |
| BE `venv/` with deps installed | `cd smartenplus-backend && pip install -r requirements.txt` if missing |

## Run Command

```bash
cd smartenplus-frontend
npx playwright test e2e/checkout/payment-auto-qa.spec.ts --project=chromium-desktop --workers=1
```

~1.5 min total. Workers must be 1 (tests share DB state sequentially).

## What Gets Tested

| Test | Fix | What it proves |
|---|---|---|
| H3 order reuse | BE `d7af0e9` | Second POST `/order-billing/` → `{message:"Order reused", order}` same order_id |
| H4 QR cancel expires | FE `a3c8c80` | Real sandbox QR, countdown from BE `expires_at`, cancel → charge=expired, order recovers |
| H5 self-heal pending | BE `6a481df` | GET orderdetails → `payment_pending` + paid charge → order finalizes to `paid` |
| M1 QR PendingCharge | FE `294c8fc` | Pending kakao_pay charge → QR attempt → PendingChargeNotice, no new charge |
| M2a alreadyPaid | FE `294c8fc` | Paid ikey charge → QR attempt → redirect to `/guest-order/{id}`, no Omise charge call |
| M2b amountLocked | FE `294c8fc` | `locked_amount` ≠ cart total → "Cart Changed After QR Generation" notice |
| M3 cancelState no flash | FE `294c8fc` | QR → cancel → switch to CC → no "Payment Cancelled" alert visible |
| Full smoke | all batches | Guest checkout → QR + countdown, no console errors, no 4xx/5xx |

## What Happens Automatically

- Fixture CLI (`scripts/e2e_payment_fixtures.py`) creates DB state per test (pending charges, locked amounts, paid charges + idempotency keys)
- All data tagged `qa-e2e@example.com` / `chrg_qae2e_*`
- `afterAll` runs `cleanup` — deletes all QA-tagged rows, zero residue

## If a Test Fails

**Check servers first:**
```bash
curl http://localhost:8000/admin-dashboard-orders/ -o /dev/null -w "%{http_code}"  # expect 200 or 301
curl http://localhost:3000 -o /dev/null -w "%{http_code}"                          # expect 200
```

**Check Omise key:**
```bash
grep OMISE_SEC_KEY smartenplus-backend/.env
# Must be skey_test_... with NO quotes, NO trailing \r
# If quoted: edit .env to remove quotes
```

**Run with debug output:**
```bash
npx playwright test e2e/checkout/payment-auto-qa.spec.ts --project=chromium-desktop --workers=1 --headed
```

**Manual cleanup if test crashed mid-run:**
```bash
cd smartenplus-backend
venv/bin/python scripts/e2e_payment_fixtures.py cleanup
```

## Files

| File | Purpose |
|---|---|
| `smartenplus-frontend/e2e/checkout/payment-auto-qa.spec.ts` | Playwright spec (8 tests, 425 lines) |
| `smartenplus-backend/scripts/e2e_payment_fixtures.py` | Django fixture CLI — creates/destroys DB state |

## Related

- [[payment-auto-test-results]] — test results + architecture detail
- [[omise-webhook-tailscale-local-testing]] — webhook delivery testing (separate, manual)
- [[payment-deep-review]] — source audit these tests validate

## Orphan Link-Backlog (Linked 2026-06-13)
- [[payment-checkout-e2e-testing]] — payment checkout E2E testing pattern (sibling E2E reference)
