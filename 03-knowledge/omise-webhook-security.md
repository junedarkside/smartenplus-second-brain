# Omise Webhook Security

## Summary
Omise webhooks use API-based event verification (NOT HMAC signatures). Two-layer dedup prevents replay and double-processing. WebhookEvent stored outside transaction for audit safety.

## Context
Standard webhook security uses HMAC-SHA256 signature verification. Omise uses a different model: the payload contains an event ID, and the receiver queries Omise's Event API to get the authoritative data. This means no shared secret is needed for verification.

## Details

### Verification Pattern (payments/views.py:170-200)
```python
# Webhook arrives with: event_id, data.id (charge_id), key (event type)
verified_event = client.Event.retrieve(event_id)   # calls Omise API
verified_charge_id = verified_event.data.id
verified_status = verified_event.data.status

if data.get('id') != verified_charge_id:
    return Response({'error': 'verification_failed'}, status=400)
```
If `Event.retrieve()` throws → returns 400 "verification_failed".

**Security properties:**
- Replay-resistant: replayed event ID returns same Omise data (idempotent)
- Forgery-resistant: attacker can't fake a charge ID without Omise returning it
- No shared secret needed; Omise is the authority

### Double-Layer Dedup (payments/views.py:203-218)
**Layer 1: WebhookEvent creation**
```python
webhook_event, created = WebhookEvent.objects.get_or_create(event_id=event_id)
# IntegrityError (race between 2 concurrent webhooks) → 200 "already_processed"
```
Note: `get_or_create` is NOT atomic — small race window possible, hence Layer 2.

**Layer 2: Last webhook ID on charge**
```python
if charge_record.last_webhook_event_id == event_id:
    return Response({'status': 'already_processed'}, status=200)
```
Returns 200 (not 409) — tells Omise "delivered successfully" so it stops retrying.

### WebhookEvent Audit Outside Transaction
`WebhookEvent` saved **before** entering `transaction.atomic()`. Survives rollbacks. Raw event always available for manual reconciliation even if payment processing fails.

## Tradeoffs
- No HMAC secret = simpler key management, but requires outbound Omise API call per webhook (latency)
- `get_or_create` race window is acceptable because Layer 2 (last_webhook_event_id) catches it
- Returning 200 on duplicate prevents Omise retry loop (correct behavior)

## Related
- [[payment-gateway-charge-architecture]] — finalize_payment SSOT
- [[payment-finalize-deep-dive]] — what happens after webhook verification
- [[payment-exception-catalog]] — error HTTP codes
- [[promptpay-no-webhook-on-expiry]] — PromptPay/MB don't send expiry webhooks
