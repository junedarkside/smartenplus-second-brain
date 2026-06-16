# Omise API Reference — 2026-06-12

## Summary
Complete Omise API catalog (21 sections). Integration status per SmartEnPlus. Status vocabulary mapping.

## Context
Full Omise API review to identify active integrations, gaps, and future opportunities.

## Core Payment APIs (5)

### Charges
Create/manage payment charges (cards, wallets, sources). QR code flow for PromptPay.
**Key endpoints:** POST/GET/PATCH `/charges`, POST `/charges/{id}/capture`, `expire`, `reverse`
**SmartEnPlus:** Active — core payment processing
**Status values:** pending/processing/authorized/successful/failed/expired/reversed

### Sources
Create payment sources for non-card methods (digital wallets, QR, installments).
**Key endpoints:** POST `/sources`, GET `/sources/{id}`
**SmartEnPlus:** Active — alternative payment method support (PromptPay, TrueMoney, Alipay, etc.)
**Flow types:** redirect / offline / app_redirect

### Tokens
Tokenize credit/debit cards for single-use or recurring charges.
**Key endpoints:** POST `/tokens`, GET `/tokens/{id}`
**SmartEnPlus:** Active — card tokenization via Omise.js iframe
**Usage:** Create token in form, send to backend for charge

### Refunds
Create/manage refunds on captured charges (full or partial).
**Key endpoints:** POST `/charges/{id}/refunds`, GET `/charges/{id}/refunds`, `[refund_id]`
**SmartEnPlus:** Active — refund processing (backend-driven)
**Void support:** uncaptured charges can be voided

### Cards
Retrieve/update/delete customer cards (created from tokens).
**Key endpoints:** GET/PATCH/DELETE `/customers/{id}/cards`, `[card_id]`
**SmartEnPlus:** Partial — not fully leveraged (no saved-card checkout)
**Limits:** supports expiry_month/year, name, postal_code updates

---

## Account & Customer APIs (3)

### Customers
Create/manage customer profiles with attached cards for recurring payments.
**Key endpoints:** POST/GET/PATCH/DELETE `/customers`, GET `/customers/{id}/cards`
**SmartEnPlus:** Partial — not leveraged for recurring billing
**Auto-save:** token attached to customer auto-creates card

### Account
Retrieve/update merchant account settings, webhooks, API versions.
**Key endpoints:** GET/PATCH `/account`, PATCH `/account/api_version`
**SmartEnPlus:** Not integrated — admin-only, handled by Omise dashboard
**Config:** livemode, location, country, currency, webhook URI, transfer config

### Capability
Retrieve account capabilities (supported banks, payment methods, limits, tokenization).
**Key endpoints:** GET `/capability` (public key only)
**SmartEnPlus:** Not integrated — informational only
**Use case:** dynamic method availability per merchant

---

## Financial Operations APIs (7)

### Transfers
Create/manage transfers to bank accounts (fund withdrawals).
**Key endpoints:** POST/GET/DELETE `/transfers`, POST `mark_as_sent`, `mark_as_paid`
**SmartEnPlus:** Not integrated — payout system, backend-only
**Recipient:** optional, defaults to primary bank account

### Transfer Schedules
Schedule recurring transfers at intervals (daily/weekly/monthly).
**Key endpoints:** GET `/transfers/schedules`, filtering by from/to/order
**SmartEnPlus:** Not integrated — subscription payout infrastructure
**Dependency:** requires Transfers + Recipients APIs

### Balance
Retrieve current account balance (total, transferable, reserve).
**Key endpoints:** GET `/balance`
**SmartEnPlus:** Not integrated — accounting/reporting only
**Amounts:** in smallest currency unit

### Bank Account
Define bank account for recipients (account number, bank code, name).
**Key endpoints:** N/A — reference object used by Transfers/Recipients
**SmartEnPlus:** Not integrated — backend account setup only
**Type:** savings/checking/fixed

### Recipients
Manage recipients for transfers (individuals or corporations).
**Key endpoints:** POST/GET/PATCH/DELETE `/recipients`, PATCH `verify`
**SmartEnPlus:** Not integrated — payout network setup
**Verification:** optional, manual or automated

### Forex
Retrieve real-time exchange rates (~2-4% above mid-market).
**Key endpoints:** GET `/forex/{currency}`
**SmartEnPlus:** Not integrated — multi-currency not enabled
**Supported:** ISO 4217 codes (30+ currencies)

### Recipient Email Addresses
Recipient email used for transfer notifications.
**SmartEnPlus:** Partial — stored with recipient object

---

## Dispute & Event APIs (2)

### Disputes
Manage chargebacks (open/won/lost) with documents (evidence).
**Key endpoints:** GET/PATCH `/disputes`, POST `/charges/{id}/disputes`, PATCH `accept`, `close`
**SmartEnPlus:** Not integrated — chargeback management backend-only
**Reasons:** reason_code per card network (Visa, MC, Amex)

### Events
Retrieve account-generated events (audit trail, webhook delivery tracking).
**Key endpoints:** GET `/events`, `/events/{id}`, `/charges/{id}/events`
**SmartEnPlus:** Partial — webhooks used for payment updates, full event retrieval not exposed
**Event types:** charge, customer, refund, transfer, dispute, payout, etc.

---

## Scheduling & Search APIs (3)

### Schedules
Create recurring charges/transfers (daily/weekly/monthly).
**Key endpoints:** POST/GET/DELETE `/schedules`, GET `/customers/{id}/schedules`
**SmartEnPlus:** Not integrated — subscription billing not implemented
**Status:** active/expiring/expired/paused/suspended

### Occurrences
Retrieve scheduled charge/transfer execution details (retry dates, status).
**Key endpoints:** GET `/occurrences/{id}`, GET `/schedules/{id}/occurrences`
**SmartEnPlus:** Not integrated — dependency of Schedules API
**Status:** skipped/failed/successful

### Search
Search charges/transfers/customers/disputes with reverse-chronological order.
**Key endpoints:** GET `/search?scope={charge|transfer|customer|dispute}`
**SmartEnPlus:** Partial — backend search likely used, not frontend-exposed
**Filters:** per scope, pagination max=100

---

## Reference APIs (3)

### Receipts
Daily receipts accumulating transaction/transfer fees for reconciliation.
**Key endpoints:** GET `/receipts`, `/receipts/{id}`
**SmartEnPlus:** Not integrated — accounting/reporting, backend-only
**Fields:** charge_fee, transfer_fee, voided_fee, vat, wht, issued_on

### Documents
Dispute evidence upload (PNG/JPG/PDF, max 10MB).
**Key endpoints:** POST/GET/DELETE `/disputes/{id}/documents`, `[document_id]`
**SmartEnPlus:** Not integrated — chargeback defense only
**Kinds:** cardholder_details, details_of_purchase, proof_of_receipt, proof_of_acceptance

### Errors
Error response structure reference (4xx/5xx status codes).
**Format:** `{object: "error", location, code, message}`
**SmartEnPlus:** Active — all API error handling uses this

---

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

---

## Integration Summary

**Active:** Charges, Sources, Tokens, Refunds, Cards, Events, Errors
**Partial:** Customers, Receipts, Search
**Not Integrated:** Account, Capability, Transfers, Transfer Schedules, Balance, Bank Account, Recipients, Disputes, Schedules, Occurrences, Forex, Documents

---

## Related
- [[payment-integration]] — Thai payment methods, QR polling
- [[payment-status-enums]] — OmiseMethod constants, METHOD_EXPIRY
- [[payment-gateway-charge-architecture]] — charge selection rule, finalization
- [[payment-audit-bugs-2026-06-11]] — confirmed payment bugs
- [[omise-api-reference-2026-06-12]] (external: https://docs.omise.co/)
