# Omise Webhook Local Testing via Tailscale

## Summary

Real Omise webhooks can be received on a local BE during development using Tailscale funnel — no ngrok, no staging deploy needed.

## Setup

**Tailscale funnel URL (dev machine):**
```
https://macbook-air-2.tailc1dfbd.ts.net/admin-dashboard-orders/payments/webhook/
```

**Registered in:** Omise test dashboard → Settings → Webhooks → this URL

**Route:** `admin-dashboard-orders/payments/webhook/` → `OmiseWebhookView` (`orders/urls.py:26`)

**Funnel liveness check:** `GET <url>` → `405 Method Not Allowed` (POST-only view alive, funnel forwarding to :8000)

## How It Works

`OmiseWebhookView` verifies every event by calling `client.Event.retrieve(event_id)` against the real Omise API. Forged curl payloads always fail with `400 {"status":"verification_failed"}` — Omise re-fetch is the security gate, not HMAC. This means:

- Only real Omise-originated events pass verification
- Forged payloads are caught at verification step (useful negative test)
- Dedupe: `WebhookEvent.get_or_create(event_id)` + `charge.last_webhook_event_id` — replaying the same real event → `200 {"status":"already_processed"}`

## Repro Steps (Full Flow)

### 1. Verify funnel alive
```bash
curl -X GET https://macbook-air-2.tailc1dfbd.ts.net/admin-dashboard-orders/payments/webhook/
# Expect: 405
```

### 2. Negative test (forged payload)
```bash
curl -X POST https://macbook-air-2.tailc1dfbd.ts.net/admin-dashboard-orders/payments/webhook/ \
  -H 'Content-Type: application/json' \
  -d '{"id":"evnt_fake","key":"charge.complete","data":{"id":"chrg_fake"}}'
# Expect: 400 {"status":"verification_failed"}
```

### 3. Create real sandbox charge (API, no browser)
```bash
cd smartenplus-backend

# Step A: create cart + order
CART=$(venv/bin/python scripts/e2e_payment_fixtures.py setup-cart | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cart_id'])")
# POST /order-billing/ with guest passenger payload → get order_id
# (see payment-auto-qa.spec.ts reachPaymentStep() for exact payload shape)

# Step B: charge order via API
# POST /payments/order-charge/ → get chrg_test_... id

# Step C: strip quotes from OMISE_SEC_KEY in .env before curl
SKEY=$(grep OMISE_SEC_KEY .env | cut -d= -f2 | tr -d '"' | tr -d $'\r')
```

### 4. Wait for sandbox PP auto-completion
Sandbox PromptPay sources auto-complete ~30s after creation (flow: "offline"). No manual `mark_as_paid` needed. Omise fires `charge.complete` → Tailscale → local BE.

> **Note:** `mark_as_paid` on a PP charge that already completed returns error `processed_charge` — this is expected. Don't use it for sandbox PP.

### 5. Verify webhook finalized order
```bash
venv/bin/python scripts/e2e_payment_fixtures.py order-status <order_id>
# Expect: {"order_status":"paid", "latest_charge_status":"paid", ...}
```

Also check DB:
- `WebhookEvent` row with real event_id exists
- `GatewayCharge.last_webhook_event_id` set
- `Order.payment_finalized_at` set

### 6. Test dedupe
Omise dashboard → Webhooks → find the event → "Resend". OR replay with real event_id:
```bash
curl -X POST <tailscale-url> \
  -H 'Content-Type: application/json' \
  -d '{"id":"evnt_test_<real_id>","key":"charge.complete","data":{"id":"chrg_test_<real_id>"}}'
# Expect: 200 {"status":"already_processed"}
# payment_finalized_at unchanged
```

### 7. Cleanup
```bash
venv/bin/python scripts/e2e_payment_fixtures.py cleanup <cart_id>
```

## Test Results (2026-06-12)

All 5 steps PASS:

| Step | Result | Notes |
|------|--------|-------|
| Forged payload | PASS | 400 `verification_failed` |
| Real PP charge | PASS | `chrg_test_67zrcauou19uk2t655l` created |
| PP auto-completion | PASS | sandbox auto-completes ~30s, no trigger needed |
| Webhook finalizes order | PASS | `evnt_test_67zrckorm42kmojdy8k` → order `AUL3348232` paid at `2026-06-12 11:01:44`, `payment_finalized_at` set, 1 BookingItem confirmed, zero FE involvement |
| Dedupe on replay | PASS | 200 `already_processed`, `payment_finalized_at` unchanged |

## Known Gotchas

- `OMISE_SEC_KEY` in BE `.env` has quotes + possible CR (`\r`) — strip before curl: `tr -d '"' | tr -d $'\r'`
- PP source auto-completes — webhook fires on its own. Don't fight the race with `mark_as_paid`
- Tailscale funnel must be running and allow unauthenticated public ingress (verified: GET → 405 reaches local BE)
- Only `charge.complete` handled by `OmiseWebhookView` — other event types return early without error

## Related

- [[omise-webhook-security]] — Event.retrieve() verification, double-layer dedupe, WebhookEvent outside atomic
- [[payment-auto-test-results-2026-06-12]] — full automated test results including webhook gap
- `smartenplus-backend/payments/views.py:176` — `OmiseWebhookView`
- `smartenplus-backend/orders/urls.py:26` — route mount
- `smartenplus-backend/scripts/e2e_payment_fixtures.py` — fixture CLI for charge creation + cleanup
