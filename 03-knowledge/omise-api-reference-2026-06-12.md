# Omise API Reference — 2026-06-12

## Summary
Omise capabilities relevant to SmartEnPlus payment flow. Charges API (active integration). Documents API (dispute-only, not applicable). Status vocabulary mapping.

## Context
Quarterly review of payment implementation against current Omise API. Goal: ensure no missed features, clarify API scope for future work.

## Omise Charges API

### Create Charge
**Endpoint:** `POST https://api.omise.co/charges`

**Primary params:**
- `amount` (required) — smallest currency unit
- `currency` (required) — ISO 4217 code (THB, SGD, JPY, MYR, HKD)
- `source[type]` — payment method (promptpay, credit_card, mobile_banking_scb, etc.)
- `return_uri` — redirect target for redirect-based auth (card iframe, e-wallets, mobile banking)
- `capture` (optional, default true) — auto-capture behavior
- `metadata` (optional) — custom data up to 15,000 chars
- `expires_at` — expiration (PromptPay, mobile banking 10 min)
- `webhook_endpoints` (max 2 HTTPS URLs)

**Response fields (subset):**
- `status` — `pending / processing / authorized / successful / failed / expired / reversed`
- `authorized` — boolean
- `paid` — boolean
- `refundable` — boolean
- `failure_code` / `failure_message`
- `return_uri`

### QR Code Payment Flow (PromptPay)
1. Create charge with `source[type]=promptpay`
2. Response includes QR code URI
3. Customer scans QR, authorizes in banking app
4. Webhook notifies merchant of payment completion
5. `return_uri` redirects customer on completion

### Charge Expiry
**Endpoint:** `POST /charges/{id}/expire`

Proactively expires a pending charge. Returns 200 if successfully expired, 409 if charge already captured/failed/expired.

### Webhook Events
Payment completion, refunds, disputes. Specify via `webhook_endpoints` on charge creation. Requires HTTPS. Max 2 endpoints per charge.

## Omise Documents API

### Purpose
Dispute evidence upload for chargeback/refund resolution. NOT payment receipts or invoices.

### Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/disputes/{id}/documents` | Upload evidence file |
| GET | `/disputes/{id}/documents` | List all documents for dispute |
| GET | `/disputes/{id}/documents/{document_id}` | Fetch document metadata |
| DELETE | `/disputes/{id}/documents/{document_id}` | Remove document (dispute must be open) |

### File Upload Details
- **Formats:** PNG, JPG, PDF
- **Max size:** 10 MB
- **Kinds (classification):** `cardholder_details`, `details_of_purchase`, `proof_of_receipt`, `proof_of_acceptance`
- **Response:** Document object with `id`, `filename`, `kind`, `download_uri`, `created_at` (ISO 8601 UTC), `deleted` status

### Authentication
HTTP Basic. Secret API key as username, empty password.

## Status Vocabulary Mapping

| Omise Charge | SmartEnPlus GatewayCharge | Notes |
|---|---|---|
| `pending` | `pending` | Awaiting completion |
| `processing` | `processing` | Payment in flight |
| `successful` / `authorized` | `paid` | Completed successfully |
| `failed` | `failed` | Rejected |
| `expired` | `expired` | Timed out (PP/MB) |
| `reversed` | N/A | Omise-initiated reversal (not modeled) |

**Frontend polling:** Check BOTH `status === 'successful' || status === 'paid'` (domains differ).

## Integration Status

### Active (Charges API)
- PromptPay QR (Thai markets)
- Credit/debit cards
- Mobile banking (5 Thai banks)
- E-wallets (TrueMoney, Line Pay, Alipay, WeChat, KakaoPay)
- Expiry via `POST /charges/{id}/expire`
- Webhook notifications on completion

### NOT Integrated (Documents API)
- Dispute evidence upload
- Not applicable to booking receipts or invoices
- Scope: chargebacks and refund disputes only

## Related
- [[payment-integration]] — Thai payment methods, QR polling
- [[payment-status-enums]] — OmiseMethod constants, METHOD_EXPIRY
- [[payment-gateway-charge-architecture]] — charge selection rule, finalization
- [[omise-api-docs]] (external: https://docs.omise.co/)
